import dateutil.parser
import datetime

# a single order (symbol name not included)
class order:

    def __init__(self, date_string: str, type_string: str, price_float: float, amount_float: float):

        if type_string.lower() !="sell" and type_string.lower() != "buy":
            raise ValueError("type must be 'sell' or 'buy' (any casing)")

        if price_float < 0:
            raise ValueError("price must be over $0")

        if amount_float < 0:
            raise ValueError("amount must be over 0")

        self.date_string = date_string
        self.type_string = type_string.lower()
        self.price_float = price_float    # prices a single share sold / buy at
        self.amount_float = amount_float  # number of shares
        self.value_float = self.amount_float * self.price_float  # total val

        try:
            self.date_dt = dateutil.parser.parse(date_string)
            self.date_epoch = self.date_dt.timestamp()
        except:
            raise ValueError('provided date must be a parseable date - preferably of the type "%y-%m-%dT%H:%M:%S.%f%z" or "%y-%m-%d %H:%M:%S.%f %z"')

    def date_nice(self):
        return self.date_dt.strftime("%Y-%m-%d %H:%M:%S %z")

    def __repr__(self):
        return f'order("{self.date_nice()}","{self.type_string}",{self.price_float},{self.amount_float})'

# define type
Orders = list[order]

# symbol class holds symbol name, all of its orders, and current value (open positions)
class multi_orders:

    def __init__(self, symbol_name: str, orders: Orders = None, current_amount: float = 0, current_avgprice: float = 0):
        self.symbol_name = symbol_name
        # all orders
        self.orders = orders if orders is not None else []
        # current open
        self.current_amount = current_amount
        self.current_avgprice = current_avgprice
        self.current_value = self.current_amount * self.current_avgprice

    def update_current(self,current_amount: float, current_avgprice: float):
        self.current_amount = current_amount
        self.current_avgprice = current_avgprice
        self.current_value = self.current_amount * self.current_avgprice

    def clear_orders(self):
        self.orders = []

    def add_order(self, order: order):
        self.orders.append(order)

    def print_all_orders(self):
        print(f"* {self.symbol_name} has {self.len()} orders:")
        for i, val in enumerate(self.orders):
            print(f"- {i}: {val}")
        # print(self.total_profit())

    def len(self):
        return len(self.orders)

    def sort_by_time_increasing(self):
        # this is the best sort order (we need to guarantee it although it pretty much is already)
        self.orders.sort(key=lambda x: x.date_epoch, reverse=False)

    def sort_by_time_decreasing(self):
        self.orders.sort(key=lambda x: x.date_epoch, reverse=True)

    def time_vs_change_and_total_ATTR(self, attribute_name: str) -> list:
        # possible attribute_name so far 'value_float' or 'share_float'
        # output is list of these tuples (datetime, change in attribute, cumulative atttributes so far)
        result = []
        cumulative = 0 
        for o in self.orders:
            if o.type_string == "buy":
                sign = -1
            else: # if "sell"
                sign = 1
            # note: with negative buys and positive sells, we just add out open position values and get our profit. however, we get negative amounts which don't make sense so just multiply them by -1 to make sense. however, calculating amounts/quantity this way is not advised as stock splits mess the numbers up. instead use current open positions for current value. historical stock quantity doesn't really matter, its the value that matters.
            attribute_value = getattr(o,attribute_name)
            change_in_attribute_value = sign * attribute_value
            cumulative += change_in_attribute_value
            result.append( (o.date_dt, change_in_attribute_value, cumulative) )
        return result

    def time_vs_amount(self) -> list:
        # if splits happen this will not make sense and thats okay
        # output (date, change in share, cumulative shares so far)
        return self.time_vs_change_and_total_ATTR("amount_float")

    def time_vs_value(self) -> list:
        # output (date, change in value, cumulative value so far)
        return self.time_vs_change_and_total_ATTR("value_float")

    def latest_value(self) -> float:
        # this part of the profit formula
        # profit = sells - buys + opens
        # this reports the sells - buys
        # shows final cumulative value
        tvv = self.time_vs_value()
        last_i = len(tvv)-1
        return tvv[last_i][2]

    def latest_profit(self) -> float:
        # latest profit is cumulative value plus what we have open
        # profit = sells - buys + opens
        return self.latest_value() + self.current_value

    def latest_amount(self) -> float:
        # shows final cumulative amount of shares (this is not going to make much sense if there are splits that happened)
        tva = self.time_vs_amount()
        last_i = len(tva)-1
        return tva[last_i][2]

    # def total_buys_value(self) -> float:
    #     # sum of all of the buys
    #     sum = 0
    #     for o in self.orders:
    #         if o.type_string == "buy":
    #             sum += o.value_float
    #     return sum

    # def total_sells_value(self) -> float:
    #     # sum of all of the sells
    #     sum = 0
    #     for o in self.orders:
    #         if o.type_string == "sell":
    #             sum += o.value_float
    #     return sum

    # def ratio_profit_buys(self) -> float:
    #     # profits / total buys -> i believe this would be % growth of the stock after you multiple by 100
    #     if self.total_buys_value() == 0:
    #         return None
    #     return self.latest_profit() / self.total_buys_value() 

    # def ratio_profit_sells(self) -> float:
    #     # profits / total sells -> not sure what this is - maybe need to get rid of this function
    #     if self.total_sells_value() == 0:
    #         return None
    #     return self.latest_profit() / self.total_sells_value() 

    # def print_some_values(self) -> tuple:
    #     # test info
    #     a = self.symbol_name
    #     b = self.total_sells_value()
    #     c = self.total_buys_value()
    #     d = self.latest_profit()
    #     e = self.ratio_profit_buys()
    #     es = f"{e*100:.5f}" if e is not None else "NA"
    #     f = self.ratio_profit_sells()
    #     fs = f"{e*100:.5f}" if f is not None else "NA"
    #     print(f"{a}, sells: ${b:.2f}, buys: ${c:.2f}, profit: ${d:.2f}, profit per buys: %{es}, profit per sells: %{fs}")
    #     return (a,b,c,d,e,f) # symbol, sells, buys, profit, ratio profit buys, ratio profit sells

# added dividend class
class dividend:

    def __init__(self, symbol_name: str, payed_amount: float, pay_date_string: str, state: str, run_date_dt: datetime):
        # run_date is the current run_date, if we get a pay_date_string is None, then we assume date is now
        self.symbol_name = symbol_name
        self.payed_amount = payed_amount
        self.pay_date_string = pay_date_string
        self.state = state  # state "paid" seems the best one
        if pay_date_string is None: 
            # NOTE: might need to change this behavior. if the pay_date_string is None, most likely state is pending, so lets just give it current date for fun. For current date we better provide the run_date, which is global var in another file, so we will need to feed it in thru an argument.
            self.date_dt = run_date_dt
            self.date_epoch = run_date_dt.timestamp()
        else:
            try:
                self.date_dt = dateutil.parser.parse(pay_date_string)
                self.date_epoch = self.date_dt.timestamp()
            except:
                raise ValueError('provided date must be a parseable date - preferably of the type "%y-%m-%dT%H:%M:%S.%f%z" or "%y-%m-%d %H:%M:%S.%f %z"')

    def date_nice(self):
        return self.date_dt.strftime("%Y-%m-%d %H:%M:%S %z")

# EOF