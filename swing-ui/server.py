"""
Interactive Web Application & REST API Server for NSE Swing Trader.
Runs on pure Python 3 standard library (http.server, json, urllib).
Zero pip dependencies required.
"""

import sys
import os
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from swing_core.indicators import enrich_bars
from swing_core.data_feed import fetch_historical_bars
from swing_core.universe import BENCHMARK_INDEX, ACTIVE_UNIVERSE
from swing_regime.regime import evaluate_market_regime
from swing_scanner.scanner import scan_swing_candidates
from swing_backtest.backtest import run_swing_backtest
from swing_paper_trader.paper_trader import (
    load_portfolio, save_portfolio, update_and_evaluate, PORTFOLIO_FILE
)
from swing_budget.budget import calc_delivery_charges

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")


class SwingServerHandler(BaseHTTPRequestHandler):

    def _send_json(self, data: Any, status: int = 200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # 1. Static Web UI
        if path == "/" or path == "/index.html":
            html_file = os.path.join(STATIC_DIR, "index.html")
            if os.path.exists(html_file):
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                with open(html_file, 'rb') as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_error(404, "index.html not found")
                return

        # 2. REST API: /api/regime
        if path == "/api/regime":
            reg = evaluate_market_regime()
            self._send_json(reg)
            return

        # 3. REST API: /api/portfolio
        if path == "/api/portfolio":
            state = load_portfolio()
            # Attach live current prices to open positions
            for pos in state.get('open_positions', []):
                t = pos['ticker']
                try:
                    bars = fetch_historical_bars(t, range_str="5d", interval="1d")
                    pos['current_price'] = bars[-1]['close'] if bars else pos['entry_price']
                except Exception:
                    pos['current_price'] = pos['entry_price']
            self._send_json(state)
            return

        # 4. REST API: /api/scan
        if path == "/api/scan":
            scan_res = scan_swing_candidates(capital=20000.0)
            self._send_json(scan_res)
            return

        # 5. REST API: /api/chart?ticker=XYZ
        if path == "/api/chart":
            ticker = query.get('ticker', ['KOTAKBANK.NS'])[0]
            try:
                # Benchmark for RS
                bm_bars = fetch_historical_bars(BENCHMARK_INDEX, range_str="1y", interval="1d")
                enriched_bm = enrich_bars(bm_bars)

                stock_bars = fetch_historical_bars(ticker, range_str="1y", interval="1d")
                enriched_stock = enrich_bars(stock_bars, benchmark_bars=enriched_bm)
                self._send_json(enriched_stock)
            except Exception as e:
                self._send_json({'error': str(e)}, status=500)
            return

        # 6. REST API: /api/universe
        if path == "/api/universe":
            self._send_json({'universe': ACTIVE_UNIVERSE})
            return

        self.send_error(404, "Path not found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len).decode('utf-8') if content_len > 0 else "{}"
        try:
            req_data = json.loads(body)
        except Exception:
            req_data = {}

        # 1. Backtest Endpoint
        if path == "/api/backtest":
            cap = float(req_data.get('capital', 20000.0))
            pos = int(req_data.get('positions', 2))
            tgt = float(req_data.get('target', 0.12))
            res = run_swing_backtest(capital=cap, max_positions=pos, profit_target_pct=tgt)
            self._send_json(res)
            return

        # 2. Trade Buy Endpoint
        if path == "/api/trade/buy":
            state = load_portfolio()
            ticker = req_data.get('ticker')
            shares = int(req_data.get('shares', 1))
            price = float(req_data.get('price', 0.0))
            stop = float(req_data.get('stop_loss', price * 0.955))
            target = float(req_data.get('target1', price * 1.12))
            strat = req_data.get('strategy', 'MANUAL_SWING')

            cost = shares * price
            charges = cost * (0.001 + 0.00015 + 0.00003)

            if cost + charges > state['cash']:
                self._send_json({'status': 'error', 'message': 'Insufficient cash for purchase'}, status=400)
                return

            if len(state['open_positions']) >= 2:
                self._send_json({'status': 'error', 'message': 'Maximum capacity (2 positions) reached'}, status=400)
                return

            state['cash'] = round(state['cash'] - (cost + charges), 2)
            state['open_positions'].append({
                'ticker': ticker,
                'shares': shares,
                'entry_price': price,
                'stop_loss': stop,
                'target1': target,
                'strategy': strat,
                'entry_date': '2026-10-29',
                'peak_price': price,
                'hold_days': 0
            })
            save_portfolio(state)
            self._send_json({'status': 'ok', 'message': f'Bought {shares} shares of {ticker} @ ₹{price}'})
            return

        # 3. Trade Sell Endpoint
        if path == "/api/trade/sell":
            state = load_portfolio()
            ticker = req_data.get('ticker')
            exit_price = float(req_data.get('exit_price', 0.0))
            reason = req_data.get('reason', 'MANUAL_EXIT')

            found = None
            rem = []
            for p in state['open_positions']:
                if p['ticker'] == ticker and not found:
                    found = p
                else:
                    rem.append(p)

            if not found:
                self._send_json({'status': 'error', 'message': f'Position {ticker} not found'}, status=404)
                return

            cost = found['shares'] * found['entry_price']
            val = found['shares'] * exit_price
            charges = calc_delivery_charges(found['entry_price'], exit_price, found['shares'])
            net_pnl = round((val - cost) - charges['total_charges'], 2)

            state['cash'] = round(state['cash'] + val - charges['total_charges'], 2)
            state['open_positions'] = rem
            state['closed_trades'].append({
                'ticker': ticker,
                'clean_symbol': ticker.replace('.NS', ''),
                'strategy': found.get('strategy', 'SWING'),
                'entry_date': found.get('entry_date', '2026-10-01'),
                'exit_date': '2026-10-29',
                'hold_days': found.get('hold_days', 1),
                'entry_price': found['entry_price'],
                'exit_price': exit_price,
                'shares': found['shares'],
                'cost': round(cost, 2),
                'charges': charges['total_charges'],
                'pnl': net_pnl,
                'roi_pct': round((net_pnl / cost) * 100.0, 2),
                'reason': reason
            })
            save_portfolio(state)
            self._send_json({'status': 'ok', 'message': f'Sold {found["shares"]} shares of {ticker} @ ₹{exit_price} | P&L: ₹{net_pnl:+,.2f}'})
            return

        # 4. Portfolio Reset
        if path == "/api/portfolio/reset":
            if os.path.exists(PORTFOLIO_FILE):
                os.remove(PORTFOLIO_FILE)
            load_portfolio()
            self._send_json({'status': 'ok', 'message': 'Portfolio reset'})
            return

        # 5. Portfolio Price Update
        if path == "/api/portfolio/update":
            state = load_portfolio()
            update_and_evaluate(state)
            self._send_json({'status': 'ok', 'message': 'Updated'})
            return

        self.send_error(404, "Path not found")


def start_server(port: int = 8501):
    server = HTTPServer(('0.0.0.0', port), SwingServerHandler)
    print(f"\n==================================================================")
    print(f"🚀 NSE Swing Trader UI & API Server running at http://localhost:{port}")
    print(f"   • Interactive Live Candlestick Charts with 20/50/200 EMA & Supertrend")
    print(f"   • Real-Time Swing Setup Scanner (Minervini SEPA & Supertrend)")
    print(f"   • Paper Trading Portfolio Manager with Live Delivery Tax Calculations")
    print(f"   • Historical Backtest Simulator")
    print(f"==================================================================\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.server_close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Start NSE Swing Trader Web UI Server.")
    parser.add_argument("--port", type=int, default=8501, help="Port to listen on (default: 8501)")
    args = parser.parse_args()
    start_server(port=args.port)
