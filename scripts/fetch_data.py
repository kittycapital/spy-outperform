#!/usr/bin/env python3
"""
S&P 500 + Nasdaq 100 종목의 SPY 대비 성과 데이터 수집
- 티커 목록 하드코딩 (Wikipedia 의존성 제거)
- yfinance 배치 다운로드 (빠르고 안정적)
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

# ============================================
# S&P 500 + Nasdaq 100 티커 (하드코딩)
# 중복 제거된 약 550개 종목
# ============================================

TICKERS = [
    # Mega Cap Tech
    "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA", "META", "TSLA", "AVGO", "ORCL",
    # Nasdaq 100 주요 종목
    "ADBE", "AMD", "ADP", "ABNB", "ALGN", "AMGN", "ADI", "ANSS", "ASML", "AZN",
    "TEAM", "ADSK", "BKR", "BIIB", "BKNG", "CDNS", "CDW", "CHTR", "CTAS", "CSCO",
    "CTSH", "CMCSA", "CEG", "CPRT", "CSGP", "COST", "CRWD", "DDOG", "DXCM", "FANG",
    "DLTR", "EA", "EXC", "FAST", "FTNT", "GEHC", "GILD", "GFS", "HON", "IDXX",
    "ILMN", "INTC", "INTU", "ISRG", "KDP", "KLAC", "KHC", "LRCX", "LIN", "LULU",
    "MAR", "MRVL", "MELI", "MDLZ", "MNST", "MU", "MCHP", "NFLX", "NXPI", "ODFL",
    "ON", "ORLY", "PCAR", "PANW", "PAYX", "PDD", "PYPL", "PEP", "QCOM", "REGN",
    "ROP", "ROST", "SBUX", "SNPS", "TTWO", "TMUS", "TXN", "VRSK", "VRTX", "WBD",
    "WDAY", "XEL", "ZS",
    # S&P 500 추가 종목 (A)
    "A", "AAL", "AAP", "ABBV", "ABC", "ABT", "ACN", "ADM",
    "AEE", "AEP", "AES", "AFL", "AIG", "AIZ", "AJG", "AKAM", "ALB",
    "ALK", "ALL", "ALLE", "AMAT", "AMCR", "AME", "AMP", "AMT",
    "ANET", "AON", "AOS", "APA", "APD", "APH", "APTV", "ARE", "ATO",
    "AVB", "AVY", "AWK", "AXP", "AZO",
    # S&P 500 (B)
    "BA", "BAC", "BALL", "BAX", "BBWI", "BBY", "BDX", "BEN", "BG", "BIO",
    "BK", "BLK", "BMY", "BR", "BRO", "BSX", "BWA",
    # S&P 500 (C)
    "C", "CAG", "CAH", "CARR", "CAT", "CB", "CBOE", "CBRE", "CCI", "CCL", "CDAY",
    "CE", "CF", "CFG", "CHD", "CHRW", "CI", "CINF",
    "CL", "CLX", "CMA", "CME", "CMG", "CMI", "CMS", "CNC", "CNP", "COF",
    "COO", "COP", "CPB", "CPT", "CRL", "CRM",
    "CSX", "CTLT", "CTRA", "CTVA", "CVS", "CVX", "CZR",
    # S&P 500 (D)
    "D", "DAL", "DD", "DE", "DFS", "DG", "DGX", "DHI", "DHR", "DIS", "DLR",
    "DOV", "DOW", "DPZ", "DRI", "DTE", "DUK", "DVA", "DVN",
    # S&P 500 (E)
    "EBAY", "ECL", "ED", "EFX", "EG", "EIX", "EL", "ELV", "EMN", "EMR",
    "ENPH", "EOG", "EPAM", "EQIX", "EQR", "EQT", "ES", "ESS", "ETN", "ETR",
    "ETSY", "EVRG", "EW", "EXPD", "EXPE", "EXR",
    # S&P 500 (F)
    "F", "FCX", "FDS", "FDX", "FE", "FFIV", "FI", "FICO", "FIS",
    "FITB", "FLT", "FMC", "FOX", "FOXA", "FRT", "FSLR", "FTV",
    # S&P 500 (G)
    "GD", "GE", "GEN", "GIS", "GL", "GLW", "GM", "GNRC",
    "GPC", "GPN", "GRMN", "GS", "GWW",
    # S&P 500 (H)
    "HAL", "HAS", "HBAN", "HCA", "HD", "HES", "HIG", "HII", "HLT", "HOLX",
    "HPE", "HPQ", "HRL", "HSIC", "HST", "HSY", "HUBB", "HUM", "HWM",
    # S&P 500 (I)
    "IBM", "ICE", "IEX", "IFF", "INCY", "INVH",
    "IP", "IPG", "IQV", "IR", "IRM", "IT", "ITW", "IVZ",
    # S&P 500 (J)
    "J", "JBHT", "JCI", "JKHY", "JNJ", "JNPR", "JPM",
    # S&P 500 (K)
    "K", "KEY", "KEYS", "KIM", "KMB", "KMI", "KMX", "KO", "KR",
    # S&P 500 (L)
    "L", "LDOS", "LEN", "LH", "LHX", "LKQ", "LLY", "LMT", "LNC", "LNT",
    "LOW", "LUV", "LVS", "LW", "LYB", "LYV",
    # S&P 500 (M)
    "MA", "MAA", "MAS", "MCD", "MCK", "MCO", "MDT", "MET",
    "MGM", "MHK", "MKC", "MKTX", "MLM", "MMC", "MMM", "MO", "MOH",
    "MOS", "MPC", "MPWR", "MRK", "MRNA", "MRO", "MS", "MSCI", "MSI", "MTB",
    "MTCH", "MTD",
    # S&P 500 (N)
    "NCLH", "NDAQ", "NDSN", "NEE", "NEM", "NI", "NKE", "NOC", "NOW", "NRG",
    "NSC", "NTAP", "NTRS", "NUE", "NVR", "NWL", "NWS", "NWSA",
    # S&P 500 (O)
    "O", "OGN", "OKE", "OMC", "OXY",
    # S&P 500 (P)
    "PARA", "PAYC", "PCG", "PEAK", "PEG", "PFE",
    "PFG", "PG", "PGR", "PH", "PHM", "PKG", "PKI", "PLD", "PM", "PNC", "PNR",
    "PNW", "POOL", "PPG", "PPL", "PRU", "PSA", "PSX", "PTC", "PWR", "PXD",
    # S&P 500 (Q)
    "QRVO",
    # S&P 500 (R)
    "RCL", "REG", "RF", "RHI", "RJF", "RL", "RMD", "ROK", "ROL",
    "RSG", "RTX",
    # S&P 500 (S)
    "SBAC", "SCHW", "SHW", "SJM", "SLB", "SNA", "SO", "SPG",
    "SPGI", "SRE", "STE", "STLD", "STT", "STX", "STZ", "SWK", "SWKS", "SYF",
    "SYK", "SYY",
    # S&P 500 (T)
    "T", "TAP", "TDG", "TDY", "TECH", "TEL", "TER", "TFC", "TFX", "TGT", "TJX",
    "TMO", "TPR", "TRGP", "TRMB", "TROW", "TRV", "TSCO", "TSN",
    "TT", "TXT", "TYL",
    # S&P 500 (U)
    "UAL", "UDR", "UHS", "ULTA", "UNH", "UNP", "UPS", "URI", "USB",
    # S&P 500 (V)
    "V", "VFC", "VICI", "VLO", "VMC", "VRSN", "VTR", "VTRS", "VZ",
    # S&P 500 (W)
    "WAB", "WAT", "WBA", "WDC", "WEC", "WELL", "WFC", "WHR", "WM", "WMB",
    "WMT", "WRB", "WRK", "WST", "WTW", "WY", "WYNN",
    # S&P 500 (X-Z)
    "XOM", "XRAY", "XYL", "YUM", "ZBH", "ZBRA", "ZION", "ZTS",
    # 인기 성장주 추가
    "PLTR", "COIN", "MSTR", "SMCI", "ARM", "RKLB", "IONQ", "RIVN", "LCID", "NIO",
    "SOFI", "AFRM", "UPST", "HOOD", "DKNG", "ROKU", "SNAP", "PINS", "SQ", "SHOP",
    "SNOW", "NET", "OKTA", "TWLO", "DOCU", "ZM", "U", "PATH", "MDB", "BILL"
]

# 중복 제거
TICKERS = list(set(TICKERS))


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


def calculate_performance(prices, start_date):
    """수익률 계산"""
    if prices is None or len(prices) < 2:
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


def main():
    print("=" * 60)
    print("🚀 SPY 대비 상위 종목 데이터 수집 시작")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 총 {len(TICKERS)}개 종목")
    print("=" * 60)
    
    date_ranges = get_date_ranges()
    
    # 가장 긴 기간(12M) 기준으로 데이터 시작점 설정
    start_date = date_ranges["12M"] - timedelta(days=10)
    
    # SPY + 모든 종목 한번에 다운로드
    all_symbols = ["SPY"] + TICKERS
    
    print(f"\n📡 {len(all_symbols)}개 종목 데이터 다운로드 중...")
    print("  (약 2-5분 소요)")
    
    try:
        data = yf.download(all_symbols, start=start_date, end=datetime.now(), progress=True, threads=True)
        close_data = data["Close"]
    except Exception as e:
        print(f"❌ 다운로드 오류: {e}")
        return
    
    print(f"\n✅ 다운로드 완료")
    
    # SPY 데이터 추출
    print("\n📈 SPY 데이터 처리 중...")
    spy_prices = []
    spy_series = close_data["SPY"].dropna()
    for date, price in spy_series.items():
        spy_prices.append({
            "date": date.strftime("%Y-%m-%d"),
            "price": round(float(price), 2)
        })
    
    spy_performance = {}
    for period, period_start in date_ranges.items():
        spy_performance[period] = calculate_performance(spy_prices, period_start)
    
    print(f"  SPY YTD: {spy_performance.get('YTD', 'N/A')}%")
    
    # 개별 종목 데이터 처리
    print(f"\n📊 개별 종목 처리 중...")
    all_stocks = []
    stock_names = {}
    
    for symbol in TICKERS:
        try:
            if symbol not in close_data.columns:
                continue
                
            series = close_data[symbol].dropna()
            if len(series) < 10:
                continue
            
            prices = []
            for date, price in series.items():
                prices.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "price": round(float(price), 2)
                })
            
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
            
        except Exception as e:
            continue
    
    print(f"  ✅ {len(all_stocks)}개 종목 처리 완료")
    
    # 종목 이름 가져오기 (상위 종목만)
    print("\n📝 종목 이름 수집 중...")
    
    # 각 기간별 상위 30개 종목 선정
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
    
    # 종목 정보 가져오기
    stock_info = {}
    for symbol in top_symbols:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            name = info.get('shortName', info.get('longName', symbol))
            stock_names[symbol] = name
            
            # 섹터 한국어 변환
            sector_map = {
                'Technology': '기술',
                'Healthcare': '헬스케어',
                'Financial Services': '금융',
                'Consumer Cyclical': '경기소비재',
                'Consumer Defensive': '필수소비재',
                'Communication Services': '커뮤니케이션',
                'Industrials': '산업재',
                'Energy': '에너지',
                'Utilities': '유틸리티',
                'Real Estate': '부동산',
                'Basic Materials': '소재'
            }
            sector_en = info.get('sector', 'N/A')
            sector_kr = sector_map.get(sector_en, sector_en)
            
            # 시가총액 포맷
            market_cap = info.get('marketCap', 0)
            if market_cap >= 1e12:
                market_cap_str = f"${market_cap/1e12:.2f}T"
            elif market_cap >= 1e9:
                market_cap_str = f"${market_cap/1e9:.2f}B"
            elif market_cap >= 1e6:
                market_cap_str = f"${market_cap/1e6:.2f}M"
            else:
                market_cap_str = "N/A"
            
            stock_info[symbol] = {
                "name": name,
                "sector": sector_kr,
                "sectorEn": sector_en,
                "marketCap": market_cap_str,
                "price": round(info.get('currentPrice', info.get('regularMarketPrice', 0)) or 0, 2),
                "high52w": round(info.get('fiftyTwoWeekHigh', 0) or 0, 2),
                "low52w": round(info.get('fiftyTwoWeekLow', 0) or 0, 2),
                "per": round(info.get('trailingPE', 0) or 0, 2),
                "pbr": round(info.get('priceToBook', 0) or 0, 2),
                "description": (info.get('longBusinessSummary', '') or '')[:200]
            }
            
            time.sleep(0.15)
        except Exception as e:
            stock_names[symbol] = symbol
            stock_info[symbol] = {"name": symbol}
    
    print(f"  ✅ {len(stock_info)}개 종목 정보 수집 완료")
    
    # 결과 저장
    output = {
        "lastUpdated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "spy": {
            "prices": spy_prices,
            "performance": spy_performance
        },
        "stocks": all_stocks,
        "stockNames": stock_names,
        "stockInfo": stock_info
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
        print(f"  {i:2}. {stock['symbol']:6} {perf:+7.2f}% (SPY 대비 {vs_spy:+.2f}%)")


if __name__ == "__main__":
    main()
