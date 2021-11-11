import plotly.graph_objects as go
from plotly.subplots import make_subplots


class Mining:

    def __init__(self, total_reserve, init_cost, cost_open_mine, maintain_cost,
                 productivity, mine_life, price):
        self.total_reserve = total_reserve
        self.init_cost = init_cost
        self.cost_open_mine = cost_open_mine
        self.maintain_cost = maintain_cost
        self.productivity = productivity
        self.mine_life = mine_life
        self.price = price

    def calculate(self):
        mines = []
        # first mine will be created in order to make sustainable
        mine = self.open_mine()
        total_profit = (self.cost_open_mine + self.init_cost) * -1
        mines.append(mine)
        year = 0
        chart = Chart([], [])
        total_year_cost = 0
        while self.total_reserve > 0:
            year += 1
            chart.collect_year_data(year)
            if year == 1:
                total_year_cost += self.init_cost + self.cost_open_mine
            else:
                total_year_cost += 0
            # condition to create a new mine
            # maximum profit
            # if self.count_available_mines(mines) == 0:
            # minimum time
            if self.count_available_mines(mines) == 0 or total_profit >= self.cost_open_mine:
                new_mine, total_profit = self.create_new_mine(total_profit, self.total_reserve)
                if new_mine is not None:
                    mines.append(new_mine)
                    total_year_cost += self.cost_open_mine
                    print("create a new mine")
            # digging mineral for profit
            for mine in mines:
                if mine.is_active():
                    profit, self.total_reserve, current_year_cost_per_mine = mine.digging(self.total_reserve, 0)
                    total_profit += profit
                    total_year_cost += current_year_cost_per_mine
            chart.collect_mine_data(mines)
            chart.collect_profit_data(total_profit)
            chart.collect_cost_and_net_profit(total_year_cost)
            print(
                "Year: %s, profit: %s, total mines: %s, active mines: %s, remain mineral: %s, current_year_cost %s" % (
                    year, total_profit, len(mines), self.count_available_mines(mines), self.total_reserve,
                    total_year_cost))
            # check the infinite loop
            if self.total_reserve > 0 and self.count_available_mines(
                    mines) == 0 and self.cost_open_mine > total_profit:
                print("not enough money to mining the rest mineral, year: %s, profit: %s, mineral left: %s" % (
                    year, total_profit, self.total_reserve))
                break
        chart.draw_year_profit_line_chart()
        chart.drew_cost_net_profit_line_chart()
        return year

    def create_new_mine(self, profit, reserve):
        if profit >= self.cost_open_mine:
            profit -= self.cost_open_mine
            if reserve < (self.productivity * self.mine_life):
                return Mine(self.cost_open_mine, self.productivity, self.maintain_cost, self.mine_life,
                            reserve), profit
            else:
                return Mine(self.cost_open_mine, self.productivity, self.maintain_cost, self.mine_life), profit
        else:
            return None, profit

    def open_mine(self):
        return Mine(self.cost_open_mine, self.productivity, self.maintain_cost, self.mine_life)

    @staticmethod
    def count_available_mines(mines):
        available_num = 0
        for mine in mines:
            if mine.is_active():
                available_num += 1
        return available_num


class Mine:
    def __init__(self, cost, productivity, maintain_cost, life, mine_capacity=None):
        self.cost = cost
        self.productivity = productivity
        if mine_capacity is None:
            self.mine_capacity = productivity * life
        else:
            self.mine_capacity = mine_capacity
        self.maintain_cost = maintain_cost
        self.life = life

    def is_active(self):
        return self.life > 0 and self.mine_capacity != 0

    def operation(self):
        self.life = self.life - 1
        pass

    def digging(self, reserve, current_cost):

        # check total reserve has enough mineral for this mine
        if reserve >= self.mine_capacity:

            if self.mine_capacity >= self.productivity:
                profit = PRICE * self.productivity - self.maintain_cost
                self.mine_capacity = self.mine_capacity - self.productivity
                reserve -= self.productivity
            else:
                profit = PRICE * self.mine_capacity - self.maintain_cost
                reserve = reserve - self.mine_capacity
                self.mine_capacity = 0
        else:
            # not enough reserve mineral left, update current mine capacity
            self.mine_capacity = reserve
            return self.digging(self.mine_capacity, current_cost)
        self.operation()
        current_cost += self.maintain_cost
        return profit, reserve, current_cost


class Chart:
    def __init__(self, year_list=None, profit_list=None):
        self.cost_list = []
        self.net_profit_list = []
        self.year_list = year_list
        self.profit_list = profit_list
        self.total_mines = []
        self.active_mines = []
        self.fig = make_subplots(specs=[[{"secondary_y": True}]])

    def collect_year_data(self, year):
        self.year_list.append(year)

    def collect_profit_data(self, profit):
        self.profit_list.append(profit)

    def draw_year_profit_line_chart(self):
        self.fig.add_trace(go.Bar(x=self.year_list, y=self.active_mines, name="active mines"), secondary_y=True)
        self.fig.add_trace(go.Scatter(x=self.year_list, y=self.profit_list, name="$profit"), secondary_y=False)
        self.fig.update_layout(
            title_text="Profit and Active Mines over the Year"
        )
        # Set x-axis title
        self.fig.update_xaxes(title_text="Years")

        # Set y-axes titles
        self.fig.update_yaxes(title_text="<b>Profit</b> Per Year", secondary_y=False)
        self.fig.update_yaxes(title_text="<b>Active Mine</b> Number", secondary_y=True)


    def collect_mine_data(self, mines):
        self.total_mines.append(len(mines))
        self.active_mines.append(Mining.count_available_mines(mines))

    def collect_cost_and_net_profit(self, cost):
        # self.net_profit_list.append(profit)
        self.cost_list.append(cost)

    def drew_cost_net_profit_line_chart(self):
        rate = []
        for i in range(len(self.cost_list)):
            rate.append(self.cost_list[i] / self.profit_list[i])
        self.fig.add_trace(go.Scatter(x=self.year_list, y=rate, name="Rate"))
        self.fig.update_xaxes(title_text="Year")
        self.fig.update_yaxes(title_text="Total Cost/Net Profit")
        self.fig.update_layout(title='Total Cost/Net Profit Rate')
        self.fig.show()


# total reserved mineral(t)
TOTAL_RESERVE = 600
# initial cost to start this mining project
INIT_COST = 300
# cost on opening a new mine
COST_OPEN_MINE = 50
# cost of operation a mine
MAINTAIN_COST = 30
# amount of mineral in ton per year
PRODUCTIVITY = 15
# mineral sale price per ton
PRICE = 5
# time for each mine to operation(year)
LIFE = 10

mining = Mining(TOTAL_RESERVE, INIT_COST, COST_OPEN_MINE, MAINTAIN_COST, PRODUCTIVITY,
                LIFE, PRICE)
info = """
# total reserved mineral(t)
TOTAL_RESERVE = 600
# initial cost to start this mining project
INIT_COST = 300
# cost on opening a new mine
COST_OPEN_MINE = 50
# cost of operation a mine
MAINTAIN_COST = 30
# amount of mineral in ton per year
PRODUCTIVITY = 15
# mineral sale price per ton
PRICE = 5
# time for each mine to operation(year)
LIFE = 10
"""
print(info)
mining.calculate()
