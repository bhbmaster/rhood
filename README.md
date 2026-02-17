# rhood -- Robinhood Portfolio Analyzer

A Python CLI tool that pulls your entire Robinhood trading history via the [robin_stocks](https://github.com/jmfernandes/robin_stocks) API and calculates **per-symbol net profit** across stocks, crypto, and dividends.

Robinhood's own app doesn't show you true total return per symbol - especially after partial or full sells. rhood does.

> **Privacy warning:** Output contains sensitive financial data. Handle it carefully.

Here is some trivial example output (prior to adding the color functionality)

![Example output](https://user-images.githubusercontent.com/62363157/110397276-66fe8180-8026-11eb-8474-a75a135fbf9b.png)

Example output after adding color (2026-02-17):

<img width="406" height="323" alt="Cursor 2026-02-16 23 57 34" src="https://github.com/user-attachments/assets/94e3b2c3-2aae-4e65-b72d-bbce7ab16410" />

---

## Table of Contents

- [Quick Start](#quick-start)
- [Requirements](#requirements)
- [Authentication](#authentication)
  - [Method 1: Credentials File with 2FA (recommended)](#method-1-credentials-file-with-2fa-recommended)
  - [Method 2: Credentials File without 2FA](#method-2-credentials-file-without-2fa)
  - [Method 3: CLI Arguments](#method-3-cli-arguments)
- [Usage](#usage)
  - [Get All Data](#get-all-data)
  - [Profile or Finance Only](#profile-or-finance-only)
  - [Save and Load (Caching)](#save-and-load-caching)
  - [CSV Export](#csv-export)
  - [Extra Order Detail](#extra-order-detail)
  - [Color Output](#color-output)
  - [Sort Order](#sort-order)
  - [Searching for a Symbol](#searching-for-a-symbol)
- [How Profit is Calculated](#how-profit-is-calculated)
- [CLI Reference](#cli-reference)
- [Scheduling and Archiving](#scheduling-and-archiving)
- [Project Structure](#project-structure)
- [Limitations](#limitations)
- [TODO](#todo)

---

## Quick Start

```bash
git clone https://github.com/bhbmaster/rhood
cd rhood
pip install -r requirements.txt

# Without 2FA:
python rhood.py --all-info -U 'you@email.com' -P 'YourPassword' --insecure

# With 2FA (recommended):
python rhood.py --all-info -U 'you@email.com' -P 'YourPassword' -A 'YOUR2FAKEY'
```

> **What is the 2FA key?** It is the alphanumeric secret (e.g. `TZIJ9PPENAA2X69Z`) shown once when you first enable "authenticator app" 2FA in Robinhood. It is **not** the 6-digit rotating code. See [Robinhood 2FA docs](https://robinhood.com/us/en/support/articles/twofactor-authentication/) and [robin_stocks TOTP guide](https://github.com/jmfernandes/robin_stocks#with-mfa-entered-programmatically-from-time-based-one-time-password-totp).

---

## Requirements

| Requirement | Version |
|---|---|
| Python | 3.9+ (tested on 3.9, 3.10, 3.11) |
| robin-stocks | >= 3.4.0 |
| pyotp | >= 2.9.0 |
| python-dateutil | >= 2.9.0 |

```bash
pip install -r requirements.txt
```

> **Important:** `robin-stocks` 3.4.0+ is required. Older versions (e.g. 3.0.6) have a bug where login errors crash with `KeyError: 'detail'` instead of showing the real error.

---

## Authentication

rhood supports two ways to provide credentials: a **credentials file** (better for scripting) or **CLI arguments** (quick one-off runs). Both methods support 2FA ("secure") and non-2FA ("insecure") login.

> The `--insecure` flag just means "no 2FA". Both modes use the Robinhood API over HTTPS and your credentials are not stored by rhood.

### Method 1: Credentials File with 2FA (recommended)

1. Create a plain text file called `creds` with three lines:

```
you@email.com
YourPassword
YOUR2FAKEY
```

2. Encode it and delete the original:

```bash
cat creds | base64 > creds-encoded
cat creds-encoded | base64 -d   # verify it decodes correctly
rm creds
```

3. Run rhood (it reads `creds-encoded` automatically):

```bash
python rhood.py --all-info
# or all features:
python rhood.py --all-info --extra --save --csv --profile-csv
```

### Method 2: Credentials File without 2FA

Same as above, but with only two lines (email and password) and add `--insecure`:

```
you@email.com
YourPassword
```

```bash
cat creds | base64 > creds-encoded && rm creds
python rhood.py --all-info --insecure
# or all features;
python rhood.py --all-info --extra --save --csv --profile-csv --insecure
```

> If you have 2FA enabled but use `--insecure`, Robinhood will prompt for the MFA code interactively, which makes it unsuitable for scripting.

### Method 3: CLI Arguments

```bash
# With 2FA
python rhood.py --all-info -U 'you@email.com' -P 'YourPassword' -A 'YOUR2FAKEY'

# Without 2FA
python rhood.py --all-info -U 'you@email.com' -P 'YourPassword' --insecure
```

Use `-C` / `--creds-file` to specify a non-default credentials file path:

```bash
python rhood.py --all-info --creds-file /path/to/my-creds-encoded
```

---

## Usage

### Get All Data

The main command that prints everything -- profile info, all orders, open positions, net profits, dividends, and total profit:

```bash
python rhood.py --all-info
```

The "kitchen sink" command that also saves a cache, exports CSVs, and includes extra API detail:

```bash
python rhood.py --all-info --extra --save --csv --profile-csv
```

### Profile or Finance Only

```bash
python rhood.py --profile-info      # only account/profile data
python rhood.py --finance-info      # only orders, positions, profits, dividends
```

Using both `--profile-info --finance-info` together is equivalent to `--all-info`.

### Save and Load (Caching)

Fetching all orders from the API can be slow. Save the data locally and reload it later:

```bash
python rhood.py --all-info --save        # fetches from API, saves to dat.pkl
python rhood.py --all-info --load        # loads from dat.pkl (fast, skips API)
```

The pickle file stores: run date, username, all stock/crypto/option orders, open positions (with prices at save time), and dividends.

Use `-F` / `--finance-file` to change the pickle filename (default: `dat.pkl`).

> `--save` and `--load` cannot be used together.

### CSV Export

```bash
python rhood.py --all-info --csv                # financial data to CSV
python rhood.py --all-info --profile-csv        # profile data to CSV
python rhood.py --all-info --csv --profile-csv  # both
```

CSV files are saved to `csv/YYYYMMDD-HHMM-username/`. Use `-D` / `--csv-dir` to change the output directory.

### Extra Order Detail

By default, rhood only shows essential order fields (date, side, price, quantity, state). Use `--extra` to include all raw API fields:

```bash
python rhood.py --all-info --extra
```

### Color Output

rhood supports ANSI-colored output (profits in green/red, buy/sell highlighting, section headers):

```bash
python rhood.py --all-info --color auto      # default: color when stdout is a TTY
python rhood.py --all-info --color always     # force color (e.g. piping to 'less -R')
python rhood.py --all-info --color never      # plain text (clean for file redirection)
```

### Sort Order

Open positions and net profits are sorted by value (lowest to highest) by default. Sort alphabetically instead:

```bash
python rhood.py --all-info --sort-by-name
```

### Searching for a Symbol

Generate full output to a file, then grep for your symbol:

```bash
python rhood.py --all-info --extra --save > output.txt 2>&1
grep TSLA output.txt
```

This shows all TSLA orders (raw + parsed), open positions, and net profit in one view.

---

## How Profit is Calculated

```
Net Profit per Symbol = (Sum of filled Sells) - (Sum of filled Buys) + (Open Position Value)
Total Net Profit      = Sum of all symbol net profits
Total Dividends       = Sum of all paid dividends
Total Profit          = Total Net Profit + Total Dividends
```

- Only **filled** orders count. Cancelled, pending, and queued orders are ignored.
- Open position values are estimates using the current ask price (fluctuates in real-time).
- Only **paid** dividends are included. Pending dividends use an estimated date.

**Example output:**

```
STOCKS:
* STOCK CBAT net profit $-3.73
* STOCK MGM net profit $27.25 ** currently open **
* STOCK SPCE net profit $169.44
* STOCK total net profit $204.62

CRYPTO:
* CRYPTO BTC net profit $67.34 ** currently open **
* CRYPTO total net profit $64.03

TOTAL NET PROFIT:
* total net profit from stocks, crypto, and options: $268.65

--- Profits from Dividends ---
* dividend from AAPL on 2020-08-14 for $0.60 (paid)
TOTAL DIVIDEND PAY: $0.79

TOTAL PROFIT (NET PROFIT + DIVIDENDS):
* total profit from stocks, crypto, and options + dividends: $269.44
```

---

## CLI Reference

| Flag | Short | Description |
|---|---|---|
| `--all-info` | `-i` | Show all profile + financial data (required for most output) |
| `--profile-info` | | Profile data only |
| `--finance-info` | | Financial data only (orders, positions, profits, dividends) |
| `--save` | `-s` | Save fetched data to pickle file |
| `--load` | `-l` | Load data from pickle file instead of API |
| `--extra` | `-e` | Show all raw API fields for each order |
| `--csv` | `-c` | Export financial data to CSV files |
| `--profile-csv` | `-p` | Export profile data to CSV |
| `--sort-by-name` | `-S` | Sort positions/profits alphabetically (default: by value) |
| `--color` | | `auto` (default), `always`, or `never` |
| `--insecure` | `-I` | Login without 2FA |
| `--username` | `-U` | Robinhood email/username (CLI login) |
| `--password` | `-P` | Robinhood password (CLI login) |
| `--authkey` | `-A` | 2FA TOTP key (CLI login) |
| `--creds-file` | `-C` | Path to credentials file (default: `creds-encoded`) |
| `--finance-file` | `-F` | Path to pickle file (default: `dat.pkl`) |
| `--csv-dir` | `-D` | Output directory for CSVs (default: `csv`) |

```bash
python rhood.py --help    # full help text
```

---

## Scheduling and Archiving

### Automated Runs

Use `run.sh` to run rhood with full options and archive the results:

```bash
./run.sh
```

This saves dated output to `archive/output/` and dated pickle files to `archive/dat/`.

Schedule it with cron (Linux/Mac) or Task Scheduler (Windows via WSL/Cygwin):

```bash
# crontab example: run every hour
0 * * * * cd /path/to/rhood && ./run.sh
```

### Rotation and Compression

Over time, archived files can grow to many GiB. Use the rotation scripts to compress them:

```bash
./archive/rotate.sh    # compress output + dat files to .xz / .tar.xz
./csv/rotate.sh        # compress CSV directories to .tar.xz
```

Schedule rotation weekly (e.g. every Sunday).

### Parsing Historical Output

Analyze archived outputs to track profit trends over time:

```bash
cd archive
./parse-outputs.sh          # display on screen
./parse-outputs.sh save     # save to archive/parse.out
```

This works on both uncompressed and rotated (compressed) files.

---

## Project Structure

```
rhood/
├── rhood.py            # Main application (~1050 lines)
├── orders.py           # Data models: order, multi_orders, dividend
├── colors.py           # ANSI color output (--color auto/always/never)
├── requirements.txt    # Pinned Python dependencies
├── run.sh              # Automated execution wrapper
├── TestSuite.sh        # Bash test harness (22 combinations)
├── README.md           # Original documentation
├── README-better.md    # This file
├── archive/
│   ├── parse-outputs.sh   # Parse archived outputs for profit trends
│   └── rotate.sh          # Compress archived output/dat files
└── csv/
    └── rotate.sh          # Compress CSV directories
```

---

## Limitations

- **Options trading** is not yet implemented (stub functions exist but return nothing).
- **Margins** are untested.
- Open position values are real-time estimates based on current ask price.
- `--load` only works if the logged-in username matches the one in the pickle file.
- Pending dividend pay dates are estimated as the current run date.
- `robin-stocks` v3.4.0 has a known issue where `get_all_option_positions` doesn't work correctly.

---

## TODO

- [ ] Implement options order parsing and profit calculation
- [ ] Test margin account output
- [ ] Per-symbol buy/sell totals and ratios
