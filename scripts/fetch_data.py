#!/usr/bin/env python3
"""
S&P 500 + Nasdaq 100 종목의 SPY 대비 성과 데이터 수집
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import time

try:
    import yfinance as yf
except ImportError:
    import subprocess
    subprocess.check_call(['pip', 'install', 'yfinance', '-q'])
    import yfinance as yf

try:
    import pandas as pd
except ImportError:
    import subprocess
    subprocess.check_call(['pip', 'install', 'pandas', '-q'])
    import pandas as pd


def get_sp500_tickers():
    """S&P 500 티커 목록 가져오기"""
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        tables = pd.read_html(url)
        df = tables[0]
        tickers = df['Symbol'].str.replace('.', '-', regex=False).tolist()
        return tickers
    except Exception as e:
        print(f"  ⚠️ S&P 500 목록 가져오기 실패: {e}")
        return []


def get_nasdaq100_tickers():
    """Nasdaq 100 티커 목록 가져오기"""
    try:
        url = "https://en.wikipedia.org/wiki/Nasdaq-100"
        tables = pd.read_html(url)
        # Nasdaq 100 테이블 찾기
        for table in tables:
            if 'Ticker' in table.columns:
                tickers = table['Ticker'].str.replace('.', '-', regex=False).tolist()
                return tickers
            elif 'Symbol' in table.columns:
                tickers = table['Symbol'].str.replace('.', '-', regex=False).tolist()
                return tickers
        return []
    except Exception as e:
        print(f"  ⚠️ Nasdaq 100 목록 가져오기 실패: {e}")
        return []


def get_date_ranges():
    """기간별 시작 날짜 계산"""
    today = datetime.now()
    return {
        "1W": today - timedelta(days=7),
        "1M": today - timedelta(days=30),
        "3M": today - timedelta(days=90),
        "12M": today - timedelta(days=365),
        "YTD": datetime(today.year, 1, 1),
    }


def fetch_stock_data(symbol, start_date):
    """개별 주식 데이터 가져오기"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(start=start_date, end=datetime.now())
        
        if hist.empty or len(hist) < 2:
            return None
        
        # 날짜와 종가만 추출
        prices = []
        for date, row in hist.iterrows():
            prices.append({
                "date": date.strftime("%Y-%m-%d"),
                "price": round(row["Close"], 2)
            })
        
        return prices
    except Exception as e:
        return None


def calculate_performance(prices, start_date):
    """수익률 계산"""
    if not prices or len(prices) < 2:
        return None
    
    start_str = start_date.strftime("%Y-%m-%d")
    
    # 시작 날짜에 가장 가까운 데이터 찾기
    start_price = None
    for p in prices:
        if p["date"] >= start_str:
            start_price = p["price"]
            break
    
    if not start_price:
        return None
    
    end_price = prices[-1]["price"]
    return round((end_price - start_price) / start_price * 100, 2)


def get_stock_name(symbol):
    """주식 이름 가져오기"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return info.get('shortName', info.get('longName', symbol))
    except:
        return symbol


def main():
    print("=" * 60)
    print("🚀 SPY 대비 상위 종목 데이터 수집 시작")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 티커 목록 수집
    print("\n📋 티커 목록 수집 중...")
    sp500 = get_sp500_tickers()
    print(f"  S&P 500: {len(sp500)}개")
    
    nasdaq100 = get_nasdaq100_tickers()
    print(f"  Nasdaq 100: {len(nasdaq100)}개")
    
    # 중복 제거
    all_tickers = list(set(sp500 + nasdaq100))
    print(f"  중복 제거 후: {len(all_tickers)}개")
    
    # 날짜 범위
    date_ranges = get_date_ranges()
    
    # 가장 긴 기간(12M) 기준으로 데이터 시작점 설정
    start_date = date_ranges["12M"] - timedelta(days=10)  # 여유분
    
    # SPY 데이터 먼저 가져오기
    print("\n📈 SPY 데이터 수집 중...")
    spy_prices = fetch_stock_data("SPY", start_date)
    if not spy_prices:
        print("❌ SPY 데이터를 가져올 수 없습니다")
        return
    
    spy_performance = {}
    for period, period_start in date_ranges.items():
        spy_performance[period] = calculate_performance(spy_prices, period_start)
    
    print(f"  SPY YTD: {spy_performance.get('YTD', 'N/A')}%")
    
    # 모든 종목 데이터 수집
    print(f"\n📊 {len(all_tickers)}개 종목 데이터 수집 중...")
    all_stocks = []
    
    for i, symbol in enumerate(all_tickers):
        if (i + 1) % 50 == 0:
            print(f"  진행: {i + 1}/{len(all_tickers)}")
        
        prices = fetch_stock_data(symbol, start_date)
        if not prices:
            continue
        
        # 기간별 성과 계산
        performance = {}
        for period, period_start in date_ranges.items():
            perf = calculate_performance(prices, period_start)
            if perf is not None:
                performance[period] = perf
        
        if not performance:
            continue
        
        all_stocks.append({
            "symbol": symbol,
            "prices": prices,
            "performance": performance
        })
    
    print(f"  ✅ {len(all_stocks)}개 종목 수집 완료")
    
    # 종목 이름 가져오기 (상위 종목만)
    print("\n📝 종목 이름 수집 중...")
    
    # 각 기간별 상위 30개 종목 선정 (여유분)
    top_symbols = set()
    for period in date_ranges.keys():
        spy_perf = spy_performance.get(period, 0) or 0
        sorted_stocks = sorted(
            [s for s in all_stocks if period in s["performance"]],
            key=lambda x: x["performance"][period] - spy_perf,
            reverse=True
        )[:30]
        for stock in sorted_stocks:
            top_symbols.add(stock["symbol"])
    
    # 이름 가져오기
    stock_names = {}
    for symbol in top_symbols:
        name = get_stock_name(symbol)
        stock_names[symbol] = name
        time.sleep(0.1)  # Rate limiting
    
    print(f"  ✅ {len(stock_names)}개 종목 이름 수집 완료")
    
    # 결과 저장
    output = {
        "lastUpdated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "spy": {
            "prices": spy_prices,
            "performance": spy_performance
        },
        "stocks": all_stocks,
        "stockNames": stock_names
    }
    
    output_path = Path(__file__).parent.parent / "data" / "stocks.json"
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print(f"✅ 완료!")
    print(f"📁 {output_path}")
    print("=" * 60)
    
    # YTD 상위 10개 출력
    spy_ytd = spy_performance.get("YTD", 0) or 0
    print(f"\n📊 YTD 상위 10개 (SPY: {spy_ytd}%):")
    sorted_ytd = sorted(
        [s for s in all_stocks if "YTD" in s["performance"]],
        key=lambda x: x["performance"]["YTD"] - spy_ytd,
        reverse=True
    )[:10]
    
    for i, stock in enumerate(sorted_ytd, 1):
        perf = stock["performance"]["YTD"]
        vs_spy = perf - spy_ytd
        name = stock_names.get(stock["symbol"], stock["symbol"])
        print(f"  {i:2}. {stock['symbol']:6} {name[:20]:20} {perf:+7.2f}% (SPY 대비 {vs_spy:+.2f}%)")


if __name__ == "__main__":
    main()
