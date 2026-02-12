import sys

# ANSI escape codes
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
WHITE = "\033[37m"
BRIGHT_RED = "\033[91m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_WHITE = "\033[97m"

_enabled = False

def init(mode="auto"):
    global _enabled
    if mode == "always":
        _enabled = True
    elif mode == "never":
        _enabled = False
    else:  # auto
        _enabled = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

def _wrap(codes, text):
    if _enabled:
        return f"{codes}{text}{RESET}"
    return str(text)

# basic styles
def bold(text):
    return _wrap(BOLD, text)

def dim(text):
    return _wrap(DIM, text)

def red(text):
    return _wrap(RED, text)

def green(text):
    return _wrap(GREEN, text)

def yellow(text):
    return _wrap(YELLOW, text)

def cyan(text):
    return _wrap(CYAN, text)

# compound styles
def bold_cyan(text):
    return _wrap(BOLD + CYAN, text)

def bold_red(text):
    return _wrap(BOLD + RED, text)

def bold_green(text):
    return _wrap(BOLD + GREEN, text)

def bold_yellow(text):
    return _wrap(BOLD + YELLOW, text)

def bold_white(text):
    return _wrap(BOLD + WHITE, text)

def bright_green(text):
    return _wrap(BRIGHT_GREEN, text)

def bright_red(text):
    return _wrap(BRIGHT_RED, text)

# semantic helpers
def section(text):
    return bold_cyan(text)

def header(text):
    return bold_white(text)

def note(text):
    return yellow(text)

def warn(text):
    return bold_yellow(text)

def error(text):
    return bold_red(text)

def status(text):
    return dim(text)

def buy_sell(side):
    s = str(side)
    if s.lower() == "buy":
        return red(s)
    elif s.lower() == "sell":
        return green(s)
    return s

def profit(value):
    s = f"{float(value):.2f}"
    v = float(value)
    if v > 0:
        return _wrap(BRIGHT_GREEN, f"${s}")
    elif v < 0:
        return _wrap(BRIGHT_RED, f"${s}")
    return f"${s}"

def open_marker(text=" ** currently open **"):
    return _wrap(BOLD + BRIGHT_YELLOW, text)

def symbol(text):
    return bold(text)

# EOF
