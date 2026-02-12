# CLAUDE.md - AI Assistant Guide for rhood

## Project Overview

**rhood** is a Python CLI tool that analyzes Robinhood trading accounts via the `robin_stocks` API. It aggregates profile data, trading history (stocks, crypto, options), open positions, net profits, dividends, and total profit into text output, with optional CSV export and data caching via pickle files.

**Version:** 0.3.0
**Python:** 3.9+ (tested on 3.9, 3.10, 3.11)

## Repository Structure

```
rhood/
├── rhood.py               # Main application (entry point, ~1050 lines)
├── orders.py              # Data model classes: order, multi_orders, dividend
├── requirements.txt       # Pinned Python dependencies
├── run.sh                 # Scheduled execution wrapper (cron/task scheduler)
├── TestSuite.sh           # Bash test harness (22 test combinations)
├── README.md              # User-facing documentation
├── .python-version        # Python version spec (3.9.0, for pyenv/asdf)
├── .gitignore             # Excludes creds*, dat*pkl, output*, csv/*, etc.
├── archive/
│   ├── parse-outputs.sh   # Parses archived output files for profit trends
│   └── rotate.sh          # Compresses archived output/dat files (xz)
└── csv/
    └── rotate.sh          # Compresses CSV output directories (tar.xz)
```

## Key Files

- **`rhood.py`** - All application logic: login, API calls, order parsing, profit calculation, CSV export, pickle save/load, argparse CLI. Uses procedural style with global state and UPPERCASE function names for major operations.
- **`orders.py`** - Three data classes:
  - `order` - Single buy/sell transaction (date, type, price, quantity, value)
  - `multi_orders` - All orders for a symbol with profit calculation methods
  - `dividend` - Dividend payment record (symbol, amount, date, state)
- **`run.sh`** - Wrapper that runs `rhood.py --all-info --extra --save --csv --profile-csv`, saves output to `archive/output/` and pickle to `archive/dat/` with dated filenames.
- **`TestSuite.sh`** - Runs 22 argument combinations against a live Robinhood account. Not a unit test framework; requires valid credentials.

## Dependencies

From `requirements.txt`:
```
pyotp==2.9.0                  # TOTP for 2FA login
robin-stocks==3.0.6           # Robinhood API wrapper
python-dateutil==2.9.0.post0  # Date parsing
```

Install: `pip install -r requirements.txt`

## How to Run

```bash
# Basic usage (requires creds-encoded file, see README.md)
python rhood.py --all-info

# With CSV export and data saving
python rhood.py --all-info --save --csv --profile-csv

# Load from cached pickle (avoids API calls)
python rhood.py --all-info --load

# Profile info only
python rhood.py --profile-info

# Financial info only
python rhood.py --finance-info
```

Key CLI flags: `--all-info`, `--profile-info`, `--finance-info`, `--save`, `--load`, `--extra`, `--csv`, `--profile-csv`, `--sort-by-name`, `--insecure`, `--username`, `--password`, `--authkey`, `--creds-file`, `--finance-file`, `--csv-dir`.

## Testing

```bash
# Run full test suite (requires valid Robinhood credentials in creds-encoded)
./TestSuite.sh > test-output.txt 2>&1 &
```

There is no unit test framework (no pytest/unittest). `TestSuite.sh` is a bash script that runs 22 combinations of CLI arguments and logs timestamped results. Tests cover: `--all-info`, `--finance-info`, `--profile-info` with combinations of `--extra`, `--save`, `--load`, `--csv`, `--profile-csv`, `--sort-by-name`. CLI login and insecure login modes require manual testing.

## Code Conventions

### Naming
- **UPPERCASE functions** for major operations: `LOGIN()`, `LOAD_STOCK_ORDERS()`, `PARSE_STOCK_ORDERS()`, `PRINT_ALL_PROFILE_AND_ORDERS()`
- **lowercase functions** for utilities: `errmsg()`, `errext()`, `save_data()`, `load_data()`
- **UPPERCASE constants**: `CREDENTIALSFILE`, `FILENAME`, `Version`
- **lowercase classes**: `order`, `multi_orders`, `dividend`

### Architecture
- Procedural with global state (`run_date`, `loaded_username`, `cryptopairs`, `user_string`)
- Data models in `orders.py`, all other logic in `rhood.py`
- `main()` handles argparse and dispatches to `PRINT_ALL_PROFILE_AND_ORDERS()` which is the core orchestrator
- Error handling via `errmsg()` (print) and `errext(code, msg)` (print + sys.exit)
- Error codes: 1=credentials, 2=file I/O, 3=parameter errors

### Data Flow
```
Login (secure/insecure) -> Fetch from API or Load from pickle
  -> Parse orders into multi_orders dicts -> Calculate profits
  -> Print text output -> Optionally save pickle / export CSV
```

### Profit Calculation
```
Net Profit per Symbol = (Sum of Sells) - (Sum of Buys) + (Open Position Value)
Total Net Profit = Sum of all symbol net profits
Total Profit = Total Net Profit + Sum of paid dividends
```

### Storage
- **Pickle** (`dat.pkl`): Serialized dict with run_date, username, all orders, open positions, dividends
- **CSV**: Per-symbol order files (`S-SYMBOL.csv`, `C-SYMBOL.csv`), aggregate files, profile CSVs. Saved to `csv/YYYYMMDD-HHMM-username/`
- **Archives**: `archive/output/` (dated text outputs), `archive/dat/` (dated pickles), compressed to `.xz` by `rotate.sh`

## Sensitive Files (Never Commit)

The `.gitignore` excludes these - never add them to version control:
- `creds*` - Credential files (base64-encoded username/password/authkey)
- `dat*pkl` - Cached order data (contains financial information)
- `output*` - Script output (contains account details)
- `csv/*` contents - CSV exports of financial data
- `archive/dat*`, `archive/output*` - Archived financial data

## Known Limitations and TODOs

- Options parsing (`PARSE_OPTION_ORDERS`, `FORMAT_ORDER_OPTIONS`, `print_all_options_to_csv`) are stub functions (return `None`/`pass`) - not yet implemented
- `LOAD_OPEN_OPTIONS()` returns `[]` due to a bug in robin_stocks v3.0.6 (`get_all_option_positions` requires `account_number` but doesn't work when supplied)
- Margins are untested
- Open position values are estimates based on current ask price (fluctuates in real-time)
- `SELL_STOCK()` has a bug: calls `r.order_buy_market` instead of `r.order_sell_market` (line 136)

## Development Notes

- No CI/CD pipeline configured
- No linter or formatter configured
- No pre-commit hooks
- No build step required (standalone Python scripts)
- The project uses `robin_stocks.robinhood` as `r` (imported globally, also used as a global for the login session)
- When modifying profit calculations, understand the `multi_orders.time_vs_value()` -> `latest_value()` -> `latest_profit()` chain in `orders.py`
- The `cryptopairs` global (populated after login via `r.get_crypto_currency_pairs()`) is required to map crypto currency pair IDs to symbol names
