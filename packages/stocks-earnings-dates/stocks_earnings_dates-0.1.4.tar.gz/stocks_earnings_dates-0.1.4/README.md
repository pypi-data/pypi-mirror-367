
# 📈 stocks-earnings-dates

A lightweight Python package to query **historical earnings release dates** for all stocks in the **S&P 500** and the **top 100 Nasdaq**.  
It provides access to the last 10 years of earnings dates (or fewer, if the company is more recently listed).

---

##  Installation

Install the package via pip:

```bash
pip install stocks-earnings-dates --upgrade
```

---

##  What’s Inside?

This package uses a built-in SQLite database with over **21,000+ earnings dates** collected from public sources, organized by stock ticker.

You can easily:

- Get all historical earnings dates for a given stock.
- List all supported tickers.
- **Analyze price movement (%) after each earnings date**:  
  - Close → Open  
  - Close → Close  
  - Open → Close

---

##  Usage

### 🔍 Get earnings dates only:

```python
from stocks_earnings_dates import get_earnings, list_all_tickers

# Get earnings dates for a specific ticker
dates = get_earnings("AAPL")
print(dates)
# Output: ['2024-08-01', '2024-05-02', ..., '2014-07-22']

# List all tickers available in the database
tickers = list_all_tickers()
print(tickers)
```

---

### Get price reactions for each earnings date:

```python
from stocks_earnings_dates import get_earnings_price_reactions

reactions = get_earnings_price_reactions("AAPL")
for r in reactions:
    print(
        f"Earnings Date: {r['date']}, "
        f"Close→Open: {r['close_to_open_pct']}%, "
        f"Close→Close: {r['close_to_close_pct']}%, "
        f"Open→Close: {r['open_to_close_pct']}%"
    )
```

Output example:

```
Earnings Date: 2024-04-25, Close→Open: +2.45%, Close→Close: +4.38%, Open→Close: +1.88%
Earnings Date: 2024-01-19, Close→Open: -0.89%, Close→Close: -1.25%, Open→Close: -0.36%
```

These values are automatically calculated using [`yfinance`](https://pypi.org/project/yfinance/).

---

## How It Works

The earnings dates are stored locally in a **bundled SQLite database**. When using the price reaction function, the package:
- Loads the dates from the local database
- Downloads historical price data using `yfinance`
- Calculates price changes around each earnings release

---

##  Data Source

The earnings database was compiled from publicly accessible financial websites.  
The CSV was cleaned, normalized and converted to a bundled SQLite database.
---

## ⚙️ Why SQLite?

This package uses SQLite internally to optimize both speed and memory usage when querying earnings dates.

Instead of loading the entire `.csv` file into memory every time, only the subset of data requested (such as the earnings dates for a single ticker) is loaded when needed.  
This improves the efficiency when accessing multiple tickers.

---

## Limitations

- This is a static dataset. Updates are not (yet) automated.
- EPS data and surprise values are not included (yet).

---

## Future Plans

- Add EPS (expected vs actual) and calculate surprise %
- Automatically update the database monthly from trusted sources
- Add option to export earnings + reactions to CSV or DataFrame

---

## 👨‍💻 Author

Made by **Albert Pérez**  
GitHub: [AlbertPerez7](https://github.com/AlbertPerez7)

---
