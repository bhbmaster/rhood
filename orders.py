import dateutil.parser

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
            self.datetime = dateutil.parser.parse(date_string)
        except:
            raise ValueError('provided date must be a parseable date - preferablly of the type "%y-%m-%dT%H:%M:%S.%f%z" or "%y-%m-%d %H:%M:%S.%f %z"')

    def date_nice(self):
        return self.datetime.strftime("%Y-%m-%d %H:%M:%S %z")

    # def __str__(self):
    #     return f"{self.date_nice()} buy"

    def __repr__(self):
        return f'order("{self.date_nice()}","{self.type_string}",{self.price_float},{self.amount_float})'

# define type
Orders = list[order]

class stock_orders:

    def __init__(self,symbol_name: str,orders: Orders = []):
        self.symbol_name = symbol_name
        self.orders = order
    
    def clear_orders(self):
        self.orders = []

    def add_order(order: order):
        self.orders.append(order)

    def len(self):
        return len(self.order)

    def sort_by_time_increasing():
        pass

    def sort_by_time_decreasing():
        pass

    def profit(self):
        pass