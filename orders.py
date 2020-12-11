import dateutil.parser

# a single order (symbol name not included)
class order:

    def __init__(self, date_string: str, type_string: str, price_float: float, amount_float: float):

        if type_string.lower() !="sell" and type_string.lower() != "buy":
            raise ValueError("type must be 'sell' or 'buy' (any casing)")

        if price_float < 0:
            raise ValueError("price must be over 0$")

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
            raise ValueError('provided date must be a parseable date - preferablly of the type "%y-%m-%dT%H:%M:%S.%f%z" or "%y-%m-%d %H:%M:%S.%f %z"')

    def date_nice(self):
        return self.date_dt.strftime("%Y-%m-%d %H:%M:%S %z")

    # def __str__(self):
    #     return f"{self.date_nice()} buy"

    def __repr__(self):
        return f'order("{self.date_nice()}","{self.type_string}",{self.price_float},{self.amount_float})'

# define type
Orders = list[order]

# multiple multiple orders (symbol name included) - used to be called stock_orders but it works for crypto + options as well
class multi_orders:

    def __init__(self, symbol_name: str, orders: Orders = []):
        self.symbol_name = symbol_name
        self.orders = orders

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

    def sort_by_time_increasing(self): # this is the best sort order (we need to guarantee it although it pretty much is already)
        self.orders.sort(key=lambda x: x.date_epoch, reverse=False)

    def sort_by_time_decreasing(self):
        self.orders.sort(key=lambda x: x.date_epoch, reverse=True)

    def time_vs_change_and_total_ATTR(self, attribute_name: str): # TODO: specify output type & rethink!!
        # possible attribute_name so far 'value_float' or 'share_float'
        # output is list of these tuples (datetime, change in attribute, cumulative atttributes so far)
        result = []
        cumulative = 0 
        for o in self.orders:
            if o.type_string == "buy":
                sign = -1  # used to be +1
            else:           # if "sell"
                sign = 1   # used to be -1
            attribute_value = getattr(o,attribute_name)
            change_in_attribute_value = sign * attribute_value
            cumulative += change_in_attribute_value
            result.append( (o.date_dt, change_in_attribute_value, cumulative) )
        return result

    def time_vs_amount(self): # TODO: specify output type
        # output (date, change in share, cumulative shares so far)
        return self.time_vs_change_and_total_ATTR("amount_float")

    def time_vs_value(self): # TODO: specify output type
        # output (date, change in value, cumulative value so far)
        return self.time_vs_change_and_total_ATTR("value_float")

    def latest_profit(self) -> float: # shows final cumulative value
        tvv = self.time_vs_value()
        last_i = len(tvv)-1
        return tvv[last_i][2]

    def latest_amount(self) -> float: # shows final cumulative amount of shares
        tva = self.time_vs_amount()
        last_i = len(tva)-1
        return tva[last_i][2]

# EOF
