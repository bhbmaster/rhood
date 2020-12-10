# maybe? implement unsync for fast?

# to figure out stock profit make a class called stock-orders
# stockname: string
# orders: dictionary list of all the orders { date: datetime, type: string buy or sell, price: float, amount: float }
# or orders can be a list of all order instanstance class (then we would need to create an order class)

# then have a list of all of the stocks
# stocks = [ stock-orders from APPL, stock-orders from TSLA, etc...]

# order class:
# input: date string (in class can convert to datetime), type: string buy or sell, price: float, amount: float

# UPDATE: 2020-12-07
# I think best way to store stock orders
# have a dictionary { str: stock-order-class}
# { "APPL" : stock-order-class("APPL")}

# UPDATE: 2020-12-08
# implemented above. it works great.
# sidenote: should test, find very first order from text output in multi_order's order.
# changed name from stock_orders to multi_orders as it handles cryp + opt as well
# next:
# need to implement sort (although its already sorted)
# then implement profit
# TODO: show my calculations of profit for stock, crypto, options + total
# instead of PRINT_X_ORDERS make a PRINT_ORDERS_DICTIONARY -> because we do symbol look up which is expensive in both

# UPDATE: 2020-12-09
# implemented sort and PRINT_ORDERS_DICT
# TODO: show my calculations of profit for stock, crypto, options + total
# TODO: implement profit from start calculation
# TODO: implement value x (date),y (value) per stock
# TODO: implement total value x (date),y (vlue)
# implement pickle save + load for testing (
# remove creds comments and put into README.md 

# UPDATE: same day
# implement pickle load or use API (dont save pkl if we load pkl + only save if we use save argument)
# TODO: show my calculations of profit for stock, crypto, options + total
# TODO: implement profit from start calculation
# TODO: implement value x (date),y (value) per stock
# TODO: implement total value x (date),y (vlue)
# if creds file missing error

# Save and load implemented; it will be quicker once we stop using PRINT_X_ORDERS because that has ORDER number of api calls to find symbol. Need to run tests to make sure PRINT_ORDERS_DICTIONARY provides enough information. <-- implemented this, but should test to make sure we are not missing anything with PRINT_ORDERS_DICTIONARY (in the end this is the way regardless)