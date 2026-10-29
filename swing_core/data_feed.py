"""
Data Feed Module for NSE Swing Trading.
Fetches daily and weekly historical bars from Yahoo Finance with robust caching.
Standard library only (urllib, json, ssl, os).
"""

import os
import json
import ssl
import urllib.request
import urllib.parse
import datetime
from typing import List, Dict, Any, Optional

DEFAULT_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data_cache")


def get_ssl_context():
    """Returns an SSL context tolerant of local macOS certificate bundles."""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl._create_unverified_context()


def fetch_historical_bars(
    ticker: str,
    range_str: str = "2y",
    interval: str = "1d",
    cache_dir: Optional[str] = None,
    use_cache: bool = True
) -> List[Dict[str, Any]]:
    """
    Fetches historical OHLCV bars for an NSE ticker (e.g. 'RELIANCE.NS' or '^NSEI').
    Automatically uses/updates local JSON cache.
    """
    if cache_dir is None:
        cache_dir = DEFAULT_CACHE_DIR
    os.makedirs(cache_dir, exist_ok=True)

    clean_symbol = ticker.replace('^', '').replace('.NS', '')
    cache_file = os.path.join(cache_dir, f"{clean_symbol}_{interval}.json")

    # 1. Check local cache
    if use_cache and os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f:
                cached_data = json.load(f)
            bars = parse_yahoo_chart_json(cached_data)
            if len(bars) >= 50:
                return bars
        except Exception:
            pass

    # 2. Fetch from Yahoo Finance
    url_symbol = urllib.parse.quote(ticker)
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{url_symbol}?range={range_str}&interval={interval}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    req = urllib.request.Request(url, headers=headers)
    ctx = get_ssl_context()

    try:
        with urllib.request.urlopen(req, timeout=12, context=ctx) as response:
            raw_bytes = response.read()
        json_obj = json.loads(raw_bytes.decode('utf-8'))

        # Save to cache
        try:
            with open(cache_file, "w") as f:
                json.dump(json_obj, f)
        except Exception:
            pass

        return parse_yahoo_chart_json(json_obj)
    except Exception as e:
        # If network error and cache exists, fallback
        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                return parse_yahoo_chart_json(json.load(f))
        raise RuntimeError(f"Failed to fetch data for {ticker}: {e}")


def parse_yahoo_chart_json(json_obj: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parses Yahoo Finance chart API v8 response into a clean list of bar dictionaries."""
    result = json_obj.get('chart', {}).get('result', [])
    if not result:
        return []

    item = result[0]
    timestamps = item.get('timestamp', [])
    quote = item.get('indicators', {}).get('quote', [{}])[0]

    opens = quote.get('open', [])
    highs = quote.get('high', [])
    lows = quote.get('low', [])
    closes = quote.get('close', [])
    volumes = quote.get('volume', [])

    bars: List[Dict[str, Any]] = []
    n = len(timestamps)

    for i in range(n):
        c = closes[i] if i < len(closes) else None
        o = opens[i] if i < len(opens) else None
        h = highs[i] if i < len(highs) else None
        l = lows[i] if i < len(lows) else None
        v = volumes[i] if i < len(volumes) else 0

        if c is not None and o is not None and h is not None and l is not None:
            dt = datetime.datetime.fromtimestamp(timestamps[i])
            bars.append({
                'date': dt.strftime('%Y-%m-%d'),
                'timestamp': timestamps[i],
                'open': round(float(o), 2),
                'high': round(float(h), 2),
                'low': round(float(l), 2),
                'close': round(float(c), 2),
                'volume': float(v) if v is not None else 0.0
            })

    return bars
