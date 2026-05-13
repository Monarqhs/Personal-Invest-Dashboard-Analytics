"""Initial ticker universe — ~50 tickers for MVP.

IDX tickers use ".JK" suffix as required by yfinance.
Scale target: 500 tickers. Current: 50.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class TickerDef:
    symbol: str
    name: str
    market: str       # 'IDX' | 'US'
    asset_type: str   # 'stock' | 'etf' | 'index'
    currency: str
    exchange: str


# ── IDX — LQ45 subset (most liquid Indonesian stocks) ────────────────────────
IDX_TICKERS: list[TickerDef] = [
    TickerDef("BBCA.JK",  "Bank Central Asia",          "IDX", "stock", "IDR", "IDX"),
    TickerDef("BBRI.JK",  "Bank Rakyat Indonesia",       "IDX", "stock", "IDR", "IDX"),
    TickerDef("BMRI.JK",  "Bank Mandiri",                "IDX", "stock", "IDR", "IDX"),
    TickerDef("TLKM.JK",  "Telkom Indonesia",            "IDX", "stock", "IDR", "IDX"),
    TickerDef("ASII.JK",  "Astra International",         "IDX", "stock", "IDR", "IDX"),
    TickerDef("UNVR.JK",  "Unilever Indonesia",          "IDX", "stock", "IDR", "IDX"),
    TickerDef("GOTO.JK",  "GoTo Gojek Tokopedia",        "IDX", "stock", "IDR", "IDX"),
    TickerDef("EMTK.JK",  "Elang Mahkota Teknologi",     "IDX", "stock", "IDR", "IDX"),
    TickerDef("BYAN.JK",  "Bayan Resources",             "IDX", "stock", "IDR", "IDX"),
    TickerDef("ADRO.JK",  "Adaro Energy Indonesia",      "IDX", "stock", "IDR", "IDX"),
    TickerDef("PTBA.JK",  "Bukit Asam",                  "IDX", "stock", "IDR", "IDX"),
    TickerDef("INDF.JK",  "Indofood Sukses Makmur",      "IDX", "stock", "IDR", "IDX"),
    TickerDef("ICBP.JK",  "Indofood CBP",                "IDX", "stock", "IDR", "IDX"),
    TickerDef("KLBF.JK",  "Kalbe Farma",                 "IDX", "stock", "IDR", "IDX"),
    TickerDef("SMGR.JK",  "Semen Indonesia",             "IDX", "stock", "IDR", "IDX"),
    TickerDef("PGAS.JK",  "Perusahaan Gas Negara",       "IDX", "stock", "IDR", "IDX"),
    TickerDef("ANTM.JK",  "Aneka Tambang",               "IDX", "stock", "IDR", "IDX"),
    TickerDef("MDKA.JK",  "Merdeka Copper Gold",         "IDX", "stock", "IDR", "IDX"),
    TickerDef("CPIN.JK",  "Charoen Pokphand Indonesia",  "IDX", "stock", "IDR", "IDX"),
    TickerDef("EXCL.JK",  "XL Axiata",                   "IDX", "stock", "IDR", "IDX"),
]

# ── US — Blue chips + growth + popular retail ────────────────────────────────
US_TICKERS: list[TickerDef] = [
    TickerDef("AAPL",  "Apple Inc.",              "US", "stock", "USD", "NASDAQ"),
    TickerDef("MSFT",  "Microsoft Corporation",   "US", "stock", "USD", "NASDAQ"),
    TickerDef("NVDA",  "NVIDIA Corporation",       "US", "stock", "USD", "NASDAQ"),
    TickerDef("GOOGL", "Alphabet Inc.",            "US", "stock", "USD", "NASDAQ"),
    TickerDef("META",  "Meta Platforms",           "US", "stock", "USD", "NASDAQ"),
    TickerDef("AMZN",  "Amazon.com Inc.",          "US", "stock", "USD", "NASDAQ"),
    TickerDef("TSLA",  "Tesla Inc.",               "US", "stock", "USD", "NASDAQ"),
    TickerDef("BRKB",  "Berkshire Hathaway B",     "US", "stock", "USD", "NYSE"),
    TickerDef("JPM",   "JPMorgan Chase",           "US", "stock", "USD", "NYSE"),
    TickerDef("V",     "Visa Inc.",                "US", "stock", "USD", "NYSE"),
    TickerDef("ASML",  "ASML Holding",             "US", "stock", "USD", "NASDAQ"),
    TickerDef("TSM",   "Taiwan Semiconductor",     "US", "stock", "USD", "NYSE"),
    TickerDef("AMD",   "Advanced Micro Devices",   "US", "stock", "USD", "NASDAQ"),
    TickerDef("PLTR",  "Palantir Technologies",    "US", "stock", "USD", "NYSE"),
    TickerDef("COIN",  "Coinbase Global",          "US", "stock", "USD", "NASDAQ"),
    TickerDef("SOFI",  "SoFi Technologies",        "US", "stock", "USD", "NASDAQ"),
]

# ── US ETFs — broad + thematic ───────────────────────────────────────────────
US_ETFS: list[TickerDef] = [
    TickerDef("SPY",  "SPDR S&P 500 ETF",         "US", "etf", "USD", "NYSE"),
    TickerDef("QQQ",  "Invesco QQQ Trust",         "US", "etf", "USD", "NASDAQ"),
    TickerDef("IWM",  "iShares Russell 2000 ETF",  "US", "etf", "USD", "NYSE"),
    TickerDef("VNQ",  "Vanguard Real Estate ETF",  "US", "etf", "USD", "NYSE"),
    TickerDef("GLD",  "SPDR Gold Shares",          "US", "etf", "USD", "NYSE"),
    TickerDef("TLT",  "iShares 20+ Year Treasury", "US", "etf", "USD", "NASDAQ"),
    TickerDef("SOXX", "iShares Semiconductor ETF", "US", "etf", "USD", "NASDAQ"),
    TickerDef("ARKK", "ARK Innovation ETF",        "US", "etf", "USD", "NYSE"),
    TickerDef("EIDO", "iShares MSCI Indonesia ETF","US", "etf", "USD", "NYSE"),
    TickerDef("VT",   "Vanguard Total World ETF",  "US", "etf", "USD", "NYSE"),
]

ALL_TICKERS: list[TickerDef] = IDX_TICKERS + US_TICKERS + US_ETFS
