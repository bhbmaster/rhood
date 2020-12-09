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
        self.price_float = price_float
        self.amount_float = amount_float

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

    def len(self):
        return len(self.orders)

    def sort_by_time_increasing(self):
        pass

    def sort_by_time_decreasing(self):
        pass

    def profit(self):
        pass

# EOF
