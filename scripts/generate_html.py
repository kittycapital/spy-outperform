#!/usr/bin/env python3
"""
JSON 데이터를 읽어서 대시보드 HTML 생성
"""

import json
from pathlib import Path

def generate_html():
    # 데이터 로드
    data_path = Path(__file__).parent.parent / "data" / "stocks.json"
    
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    last_updated = data["lastUpdated"]
    spy_json = json.dumps(data["spy"], ensure_ascii=False)
    stocks_json = json.dumps(data["stocks"], ensure_ascii=False)
    stock_names_json = json.dumps(data["stockNames"], ensure_ascii=False)
    stock_info_json = json.dumps(data.get("stockInfo", {}), ensure_ascii=False)
    
    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>SPY 대비 상위 종목</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Noto+Sans+KR:wght@400;500;700;900&display=swap" rel="stylesheet">
    <script src="https://t1.kakaocdn.net/kakao_js_sdk/2.7.4/kakao.min.js"></script>
    <style>
        :root {{
            --bg: #000000;
            --surface: #0a0a0a;
            --surface2: #111111;
            --border: #1a1a1a;
            --border-hover: #2a2a2a;
            --text: #e4e4e7;
            --text-dim: #71717a;
            --text-muted: #52525b;
            --green: #22c55e;
            --red: #ef4444;
            --cyan: #22d3ee;
            --blue: #4a90ff;
            --gold: #ffd644;
            --mono: 'JetBrains Mono', monospace;
            --sans: 'Noto Sans KR', -apple-system, sans-serif;
            --radius: 12px;
            --radius-sm: 8px;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ scrollbar-width: none; }}
        html::-webkit-scrollbar {{ display: none; }}
        html, body {{
            height: 100%;
            overflow: hidden;
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
        }}
        body {{
            background: var(--bg);
            color: var(--text);
            font-family: var(--sans);
            padding: 0;
            -webkit-overflow-scrolling: touch;
            -webkit-font-smoothing: antialiased;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
        }}

        /* ====== HEADER ====== */
        .header {{
            padding: 20px 20px 14px;
            text-align: center;
            border-bottom: 1px solid var(--border);
            flex-shrink: 0;
        }}
        .header h1 {{
            font-size: clamp(18px, 4vw, 28px);
            font-weight: 800;
            color: #fff;
            letter-spacing: -0.02em;
            margin-bottom: 4px;
        }}
        .sub {{ font-size: 12px; color: var(--text-dim); }}
        .time {{ font-family: var(--mono); font-size: 10px; color: var(--text-muted); margin-top: 6px; }}

        /* ====== SHARE ====== */
        .share-bar {{ display: flex; gap: 5px; justify-content: center; margin: 10px 0 2px; flex-wrap: wrap; flex-shrink: 0; }}
        .share-btn {{ display: flex; align-items: center; gap: 4px; padding: 5px 10px; border-radius: 6px; border: 1px solid var(--border-hover); background: var(--surface); color: #a1a1aa; font-size: 10px; cursor: pointer; font-family: var(--sans); transition: all 0.2s; -webkit-tap-highlight-color: transparent; touch-action: manipulation; }}
        .share-btn:hover {{ border-color: #444; color: var(--text); }}
        .share-btn svg {{ width: 13px; height: 13px; flex-shrink: 0; }}
        .share-btn.twitter:hover {{ border-color: #1d9bf0; color: #1d9bf0; }}
        .share-btn.kakao:hover {{ border-color: #fee500; color: #fee500; }}
        .share-btn.telegram:hover {{ border-color: #26a5e4; color: #26a5e4; }}
        .share-btn.instagram:hover {{ border-color: #e1306c; color: #e1306c; }}
        .share-btn.instagram.copied {{ border-color: var(--green); color: var(--green); }}
        .share-btn.copy:hover {{ border-color: var(--green); color: var(--green); }}
        .share-btn.copied {{ border-color: var(--green); color: var(--green); }}

        .toast {{ position: fixed; bottom: 20px; right: 20px; background: var(--green); color: #000; padding: 10px 16px; border-radius: var(--radius-sm); font-size: 13px; font-weight: 600; z-index: 9999; opacity: 0; transform: translateY(10px); transition: all 0.3s ease; pointer-events: none; }}
        .toast.show {{ opacity: 1; transform: translateY(0); }}

        /* ====== CONTROLS ====== */
        .controls {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
            padding: 10px 16px;
            flex-wrap: wrap;
            flex-shrink: 0;
        }}
        .spy-info {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            font: 13px var(--mono);
            flex-shrink: 0;
        }}
        .spy-label {{ color: var(--text-muted); }}
        .spy-value {{ font-weight: 600; color: var(--green); }}
        .spy-value.negative {{ color: var(--red); }}

        .period-buttons {{
            display: flex;
            gap: 4px;
            background: var(--surface);
            border: 1px solid var(--border);
            padding: 3px;
            border-radius: var(--radius-sm);
            flex-shrink: 0;
        }}
        .period-btn {{
            padding: 6px 12px;
            border: none;
            background: transparent;
            color: var(--text-dim);
            font: 500 12px var(--sans);
            cursor: pointer;
            border-radius: 6px;
            transition: all 0.2s;
            -webkit-tap-highlight-color: transparent;
            touch-action: manipulation;
        }}
        .period-btn:hover {{ color: var(--text); }}
        .period-btn.active {{ background: var(--cyan); color: #000; font-weight: 600; }}

        /* ====== MAIN CONTENT ====== */
        .main-content {{
            display: grid;
            grid-template-columns: 1fr 340px;
            gap: 12px;
            flex: 1;
            min-height: 0;
            padding: 0 16px;
        }}

        /* ====== CHART ====== */
        .chart-container {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 14px;
            min-height: 0;
            position: relative;
        }}
        .chart-container::after {{
            content: 'Herdvibe.com';
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            font: 700 26px var(--mono);
            color: rgba(255,255,255,0.04);
            pointer-events: none;
            z-index: 2;
            white-space: nowrap;
        }}

        /* ====== TABLE ====== */
        .table-container {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            min-height: 0;
        }}
        .table-header {{
            padding: 12px;
            border-bottom: 1px solid var(--border);
            flex-shrink: 0;
        }}
        .table-title {{ font: 600 13px var(--sans); color: var(--text); }}

        .table-scroll {{
            overflow-y: auto;
            flex: 1;
            -ms-overflow-style: none;
            scrollbar-width: none;
        }}
        .table-scroll::-webkit-scrollbar {{ display: none; }}

        table {{ width: 100%; border-collapse: collapse; }}
        th {{
            text-align: left;
            padding: 8px 10px;
            font: 600 9px var(--mono);
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-bottom: 1px solid var(--border);
            position: sticky;
            top: 0;
            background: var(--surface);
        }}
        td {{
            padding: 7px 10px;
            font-size: 11px;
            border-bottom: 1px solid var(--border);
        }}
        tr {{
            cursor: pointer;
            transition: all 0.2s;
            -webkit-tap-highlight-color: transparent;
        }}
        @media (hover: hover) {{
            tr:hover {{ background: var(--surface2); }}
        }}
        tr:active {{ background: var(--surface2); }}
        tr.selected {{ background: rgba(34,211,238,0.08); }}
        tr.dimmed {{ opacity: 0.4; }}

        .rank {{ color: var(--text-muted); font: 500 11px var(--mono); width: 24px; }}
        .stock-info {{ display: flex; flex-direction: column; gap: 1px; }}
        .stock-symbol {{ font: 600 12px var(--mono); }}
        .stock-name {{ font-size: 9px; color: var(--text-muted); }}

        .perf-value {{ font: 600 11px var(--mono); text-align: right; }}
        .perf-value.positive {{ color: var(--green); }}
        .perf-value.negative {{ color: var(--red); }}

        .vs-spy {{ font: 10px var(--mono); text-align: right; }}
        .vs-spy.positive {{ color: var(--green); }}
        .vs-spy.negative {{ color: var(--red); }}

        /* ====== LEGEND ====== */
        .legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 10px 16px;
            padding: 10px 12px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            font-size: 10px;
            flex-shrink: 0;
            justify-content: center;
            color: var(--text-dim);
        }}
        .legend-item {{ display: flex; align-items: center; gap: 4px; }}
        .legend-dot {{ width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }}
        .legend-spy {{ width: 14px; height: 2px; border-top: 2px dashed var(--text-muted); flex-shrink: 0; }}

        /* ====== STOCK INFO CARD ====== */
        .stock-info-card {{
            display: none;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 16px;
            margin: 10px 16px 0;
            flex-shrink: 0;
        }}
        .stock-info-card.visible {{ display: block; }}
        .info-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
            gap: 12px;
        }}
        .info-title {{ font: 700 16px var(--sans); color: #fff; }}
        .info-sector {{ font-size: 11px; color: var(--text-dim); margin-top: 2px; }}
        .info-close {{
            background: none;
            border: none;
            color: var(--text-muted);
            font-size: 18px;
            cursor: pointer;
            padding: 4px 8px;
            -webkit-tap-highlight-color: transparent;
            touch-action: manipulation;
        }}
        .info-close:hover {{ color: #fff; }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 10px;
            margin-bottom: 12px;
        }}
        .info-item {{
            background: var(--surface2);
            border: 1px solid var(--border);
            padding: 10px;
            border-radius: var(--radius-sm);
        }}
        .info-label {{ font: 10px var(--mono); color: var(--text-muted); margin-bottom: 3px; text-transform: uppercase; letter-spacing: 0.05em; }}
        .info-value {{ font: 600 14px var(--mono); color: var(--text); }}
        .info-description {{
            font-size: 12px;
            color: var(--text-dim);
            line-height: 1.6;
            padding-top: 12px;
            border-top: 1px solid var(--border);
        }}

        /* ====== FOOTER ====== */
        .footer {{
            padding: 8px 16px 16px;
            text-align: center;
            font-size: 9px;
            color: var(--text-muted);
            flex-shrink: 0;
        }}

        /* === TABLET === */
        @media (max-width: 1100px) {{
            .main-content {{
                grid-template-columns: 1fr;
                grid-template-rows: 1fr auto;
            }}
            .table-container {{ max-height: 200px; }}
        }}

        /* === MOBILE === */
        @media (max-width: 600px) {{
            .header {{
                padding: 14px 12px 10px;
            }}
            .header h1 {{ font-size: 16px; }}
            .share-bar {{ gap: 4px; margin: 8px 0 2px; }}
            .share-btn {{ padding: 4px 8px; font-size: 9px; }}
            .share-btn svg {{ width: 11px; height: 11px; }}
            .controls {{
                padding: 8px 12px;
                gap: 6px;
            }}
            .period-buttons {{
                width: 100%;
                justify-content: space-between;
            }}
            .period-btn {{
                flex: 1;
                padding: 7px 2px;
                font-size: 11px;
                text-align: center;
            }}
            .spy-info {{ font-size: 11px; padding: 5px 10px; }}
            .main-content {{
                grid-template-columns: 1fr;
                grid-template-rows: 1fr auto;
                gap: 8px;
                padding: 0 10px;
            }}
            .chart-container {{
                padding: 8px 4px 8px 8px;
                border-radius: 10px;
            }}
            .chart-container::after {{ font-size: 18px; }}
            .table-container {{
                max-height: 180px;
                border-radius: 10px;
            }}
            .table-header {{ padding: 10px; }}
            .table-title {{ font-size: 12px; }}
            th {{ padding: 6px 8px; font-size: 8px; }}
            td {{ padding: 6px 8px; font-size: 10px; }}
            .stock-symbol {{ font-size: 11px; }}
            .stock-name {{ font-size: 8px; }}
            .legend {{
                gap: 6px;
                padding: 8px 10px;
                margin: 8px 10px;
                border-radius: 8px;
                font-size: 9px;
            }}
            .legend-dot {{ width: 6px; height: 6px; }}
            .stock-info-card {{ margin: 8px 10px 0; padding: 12px; }}
            .info-grid {{ grid-template-columns: repeat(3, 1fr); gap: 8px; }}
            .info-value {{ font-size: 12px; }}
            .info-title {{ font-size: 14px; }}
            .info-description {{ font-size: 11px; }}
            .footer {{ padding: 6px 10px 12px; font-size: 8px; }}
        }}

        /* === 아주 작은 화면 === */
        @media (max-width: 420px) {{
            .header {{ padding: 10px 8px 8px; }}
            .header h1 {{ font-size: 14px; }}
            .table-container {{ max-height: 150px; }}
            .legend {{ gap: 4px; padding: 6px 8px; font-size: 8px; }}
            .info-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>SPY 대비 상위 종목</h1>
            <div class="sub">S&P 500 + Nasdaq 100 — SPY 수익률을 초과한 상위 20개 종목</div>
            <div class="time">마지막 업데이트: {last_updated}</div>
        </div>

        <div class="share-bar">
            <button class="share-btn twitter" onclick="shareTwitter()"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>트위터</button>
            <button class="share-btn kakao" onclick="shareKakao()"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 3c-5.52 0-10 3.36-10 7.5 0 2.66 1.74 5 4.36 6.33-.14.53-.9 3.4-.93 3.61 0 0-.02.17.09.23.11.07.24.03.24.03.32-.04 3.7-2.42 4.28-2.83.62.09 1.27.13 1.96.13 5.52 0 10-3.36 10-7.5S17.52 3 12 3z"/></svg>카카오톡</button>
            <button class="share-btn telegram" onclick="shareTelegram()"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.479.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg>텔레그램</button>
            <button class="share-btn instagram" onclick="shareInstagram(this)"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>인스타그램</button>
            <button class="share-btn copy" onclick="copyLink(this)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>링크복사</button>
        </div>

        <div class="controls">
            <div class="spy-info">
                <span class="spy-label">SPY</span>
                <span class="spy-value" id="spy-perf">-</span>
            </div>
            <div class="period-buttons">
                <button class="period-btn" data-period="1W">1주</button>
                <button class="period-btn" data-period="1M">1개월</button>
                <button class="period-btn" data-period="3M">3개월</button>
                <button class="period-btn" data-period="12M">1년</button>
                <button class="period-btn active" data-period="YTD">YTD</button>
            </div>
        </div>

        <div class="main-content">
            <div class="chart-container">
                <canvas id="perfChart"></canvas>
            </div>
            <div class="table-container">
                <div class="table-header">
                    <div class="table-title">상위 20 종목</div>
                </div>
                <div class="table-scroll">
                    <table>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>종목</th>
                                <th style="text-align:right">수익률</th>
                                <th style="text-align:right">vs SPY</th>
                            </tr>
                        </thead>
                        <tbody id="table-body"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <div class="legend" id="legend"></div>

        <div class="stock-info-card" id="stock-info-card">
            <div class="info-header">
                <div>
                    <div class="info-title" id="info-title">-</div>
                    <div class="info-sector" id="info-sector">-</div>
                </div>
                <button class="info-close" id="info-close">✕</button>
            </div>
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">시가총액</div>
                    <div class="info-value" id="info-marketcap">-</div>
                </div>
                <div class="info-item">
                    <div class="info-label">현재가</div>
                    <div class="info-value" id="info-price">-</div>
                </div>
                <div class="info-item">
                    <div class="info-label">52주 최고</div>
                    <div class="info-value" id="info-high52">-</div>
                </div>
                <div class="info-item">
                    <div class="info-label">52주 최저</div>
                    <div class="info-value" id="info-low52">-</div>
                </div>
                <div class="info-item">
                    <div class="info-label">PER</div>
                    <div class="info-value" id="info-per">-</div>
                </div>
                <div class="info-item">
                    <div class="info-label">PBR</div>
                    <div class="info-value" id="info-pbr">-</div>
                </div>
            </div>
            <div class="info-description" id="info-description">-</div>
        </div>

        <div class="footer">데이터 출처: Yahoo Finance · S&P 500 + Nasdaq 100 기준 · 투자 판단은 본인의 책임입니다</div>
    </div>

    <div class="toast" id="toast"></div>

    <script>
        /* ====== SHARE ====== */
        const SHARE_URL = 'https://herdvibe.com/spy-outperformers';
        const SHARE_TITLE = 'SPY 대비 상위 종목 — Herdvibe';
        const SHARE_DESC = 'S&P 500 + Nasdaq 100 SPY 초과 수익 상위 20 종목 | Herdvibe';

        function showToast(msg) {{
            const t = document.getElementById('toast');
            t.textContent = msg;
            t.classList.add('show');
            setTimeout(() => t.classList.remove('show'), 3000);
        }}
        function shareTwitter() {{
            window.open(`https://twitter.com/intent/tweet?text=${{encodeURIComponent(SHARE_TITLE)}}&url=${{encodeURIComponent(SHARE_URL)}}`, '_blank');
        }}
        function shareKakao() {{
            if (window.Kakao && !Kakao.isInitialized()) Kakao.init('a43ed7b39fac35458f4f9df925a279b5');
            if (window.Kakao) {{
                Kakao.Share.sendDefault({{
                    objectType: 'feed',
                    content: {{ title: SHARE_TITLE, description: SHARE_DESC, imageUrl: 'https://herdvibe.com/og-spy.png', link: {{ mobileWebUrl: SHARE_URL, webUrl: SHARE_URL }} }}
                }});
            }}
        }}
        function shareTelegram() {{
            window.open(`https://t.me/share/url?url=${{encodeURIComponent(SHARE_URL)}}&text=${{encodeURIComponent(SHARE_TITLE)}}`, '_blank');
        }}
        function shareInstagram(btn) {{
            try {{
                if (window.parent !== window) {{ window.parent.postMessage({{ type: 'copy', text: SHARE_URL }}, '*'); }}
                else {{ navigator.clipboard.writeText(SHARE_URL); }}
                const orig = btn.innerHTML;
                btn.classList.add('copied');
                btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>복사됨!';
                showToast('링크가 복사되었습니다 - 인스타그램에 붙여넣기 하세요');
                setTimeout(() => {{ btn.classList.remove('copied'); btn.innerHTML = orig; }}, 2000);
            }} catch(e) {{ showToast('복사 실패'); }}
        }}
        function copyLink(btn) {{
            try {{
                if (window.parent !== window) {{ window.parent.postMessage({{ type: 'copy', text: SHARE_URL }}, '*'); }}
                else {{ navigator.clipboard.writeText(SHARE_URL); }}
                const orig = btn.innerHTML;
                btn.classList.add('copied');
                btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>복사됨!';
                showToast('링크가 복사되었습니다');
                setTimeout(() => {{ btn.classList.remove('copied'); btn.innerHTML = orig; }}, 2000);
            }} catch(e) {{ showToast('복사 실패'); }}
        }}

        /* ====== DATA ====== */
        const SPY_DATA = {spy_json};
        const STOCKS = {stocks_json};
        const STOCK_NAMES = {stock_names_json};
        const STOCK_INFO = {stock_info_json};

        const COLORS = [
            '#4a90ff', '#ef4444', '#22c55e', '#ffd644', '#a855f7',
            '#22d3ee', '#ec4899', '#84cc16', '#f97316', '#14b8a6',
            '#8b5cf6', '#eab308', '#64748b', '#dc2626', '#0891b2',
            '#c026d3', '#e11d48', '#ea580c', '#16a34a', '#2563eb'
        ];

        let currentPeriod = 'YTD';
        let chart = null;
        let top20 = [];
        let selectedStock = null;

        function getStartDate(period) {{
            const now = new Date();
            switch(period) {{
                case '1W': return new Date(now - 7 * 24 * 60 * 60 * 1000);
                case '1M': return new Date(now - 30 * 24 * 60 * 60 * 1000);
                case '3M': return new Date(now - 90 * 24 * 60 * 60 * 1000);
                case '12M': return new Date(now - 365 * 24 * 60 * 60 * 1000);
                case 'YTD': return new Date(now.getFullYear(), 0, 1);
                default: return new Date(now.getFullYear(), 0, 1);
            }}
        }}

        function calculatePercentChange(prices, startDate) {{
            const startStr = startDate.toISOString().split('T')[0];
            const filtered = prices.filter(p => p.date >= startStr);
            if (filtered.length === 0) return [];
            const basePrice = filtered[0].price;
            return filtered.map(p => ({{
                x: p.date,
                y: ((p.price - basePrice) / basePrice * 100)
            }}));
        }}

        function getTop20(period) {{
            const spyPerf = SPY_DATA.performance[period] || 0;
            const withVsSpy = STOCKS
                .filter(s => s.performance && s.performance[period] !== undefined)
                .map(s => ({{
                    ...s,
                    vsSpy: s.performance[period] - spyPerf
                }}))
                .sort((a, b) => b.vsSpy - a.vsSpy)
                .slice(0, 20);
            return withVsSpy;
        }}

        function updateChart() {{
            const startDate = getStartDate(currentPeriod);
            const datasets = [];

            const spyData = calculatePercentChange(SPY_DATA.prices, startDate);
            datasets.push({{
                label: 'SPY',
                data: spyData,
                borderColor: '#52525b',
                borderWidth: 2,
                borderDash: [5, 5],
                pointRadius: 0,
                tension: 0.1,
                fill: false
            }});

            top20.forEach((stock, i) => {{
                const stockData = calculatePercentChange(stock.prices, startDate);
                if (stockData.length === 0) return;

                let borderWidth = 2;
                let borderColor = COLORS[i % COLORS.length];

                if (selectedStock) {{
                    if (stock.symbol === selectedStock) {{
                        borderWidth = 4;
                    }} else {{
                        borderWidth = 1;
                        borderColor = COLORS[i % COLORS.length] + '40';
                    }}
                }}

                datasets.push({{
                    label: stock.symbol,
                    data: stockData,
                    borderColor: borderColor,
                    borderWidth: borderWidth,
                    pointRadius: 0,
                    pointHoverRadius: 4,
                    tension: 0.1,
                    fill: false,
                    originalColor: COLORS[i % COLORS.length]
                }});
            }});

            if (chart) {{
                chart.data.datasets = datasets;
                chart.update('none');
            }} else {{
                const ctx = document.getElementById('perfChart').getContext('2d');
                chart = new Chart(ctx, {{
                    type: 'line',
                    data: {{ datasets }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: {{
                            mode: 'index',
                            intersect: false
                        }},
                        plugins: {{
                            legend: {{ display: false }},
                            tooltip: {{
                                backgroundColor: '#18181b',
                                titleColor: '#fff',
                                bodyColor: '#a1a1aa',
                                borderColor: '#2a2a2a',
                                borderWidth: 1,
                                padding: window.innerWidth <= 600 ? 6 : 10,
                                titleFont: {{ family: 'Noto Sans KR' }},
                                bodyFont: {{ family: 'JetBrains Mono', size: window.innerWidth <= 600 ? 10 : 11 }},
                                callbacks: {{
                                    label: (ctx) => `${{ctx.dataset.label}}: ${{ctx.parsed.y >= 0 ? '+' : ''}}${{ctx.parsed.y.toFixed(2)}}%`
                                }}
                            }}
                        }},
                        scales: {{
                            x: {{
                                type: 'time',
                                time: {{
                                    unit: currentPeriod === '1W' ? 'day' :
                                          currentPeriod === '1M' ? 'week' : 'month',
                                    displayFormats: {{
                                        day: 'MM/dd',
                                        week: 'MM/dd',
                                        month: 'yy/MM'
                                    }}
                                }},
                                grid: {{ color: '#1a1a1a' }},
                                ticks: {{ color: '#52525b', font: {{ family: 'JetBrains Mono', size: window.innerWidth <= 600 ? 9 : 10 }} }}
                            }},
                            y: {{
                                grid: {{ color: '#1a1a1a' }},
                                ticks: {{
                                    color: '#52525b',
                                    font: {{ family: 'JetBrains Mono', size: window.innerWidth <= 600 ? 9 : 10 }},
                                    callback: (v) => v + '%'
                                }}
                            }}
                        }}
                    }}
                }});
            }}
        }}

        function updateTable() {{
            const spyPerf = SPY_DATA.performance[currentPeriod] || 0;
            const spyEl = document.getElementById('spy-perf');
            spyEl.textContent = (spyPerf >= 0 ? '+' : '') + spyPerf.toFixed(2) + '%';
            spyEl.className = 'spy-value ' + (spyPerf >= 0 ? '' : 'negative');

            const tbody = document.getElementById('table-body');
            tbody.innerHTML = top20.map((stock, i) => {{
                const perf = stock.performance[currentPeriod];
                const vsSpy = stock.vsSpy;
                const name = STOCK_NAMES[stock.symbol] || stock.symbol;
                const isSelected = selectedStock === stock.symbol;
                const isDimmed = selectedStock && !isSelected;
                return `
                    <tr data-symbol="${{stock.symbol}}" class="${{isSelected ? 'selected' : ''}} ${{isDimmed ? 'dimmed' : ''}}">
                        <td class="rank">${{i + 1}}</td>
                        <td>
                            <div class="stock-info">
                                <span class="stock-symbol" style="color: ${{COLORS[i % COLORS.length]}}">${{stock.symbol}}</span>
                                <span class="stock-name">${{name.substring(0, 25)}}</span>
                            </div>
                        </td>
                        <td class="perf-value ${{perf >= 0 ? 'positive' : 'negative'}}">${{perf >= 0 ? '+' : ''}}${{perf.toFixed(2)}}%</td>
                        <td class="vs-spy ${{vsSpy >= 0 ? 'positive' : 'negative'}}">${{vsSpy >= 0 ? '+' : ''}}${{vsSpy.toFixed(2)}}%</td>
                    </tr>
                `;
            }}).join('');

            tbody.querySelectorAll('tr').forEach(row => {{
                row.addEventListener('click', () => {{
                    const symbol = row.dataset.symbol;
                    if (selectedStock === symbol) {{
                        selectedStock = null;
                    }} else {{
                        selectedStock = symbol;
                    }}
                    updateChart();
                    updateTable();
                    updateInfoCard();
                }});
            }});
        }}

        function updateInfoCard() {{
            const card = document.getElementById('stock-info-card');
            if (!selectedStock) {{
                card.classList.remove('visible');
                return;
            }}
            const info = STOCK_INFO[selectedStock];
            if (!info || !info.name) {{
                card.classList.remove('visible');
                return;
            }}
            document.getElementById('info-title').textContent = `${{selectedStock}} - ${{info.name}}`;
            document.getElementById('info-sector').textContent = info.sector || '-';
            document.getElementById('info-marketcap').textContent = info.marketCap || '-';
            document.getElementById('info-price').textContent = info.price ? `$${{info.price.toLocaleString()}}` : '-';
            document.getElementById('info-high52').textContent = info.high52w ? `$${{info.high52w.toLocaleString()}}` : '-';
            document.getElementById('info-low52').textContent = info.low52w ? `$${{info.low52w.toLocaleString()}}` : '-';
            document.getElementById('info-per').textContent = info.per || '-';
            document.getElementById('info-pbr').textContent = info.pbr || '-';
            document.getElementById('info-description').textContent = info.description || '설명 없음';
            card.classList.add('visible');
        }}

        document.getElementById('info-close').addEventListener('click', () => {{
            selectedStock = null;
            updateChart();
            updateTable();
            updateInfoCard();
        }});

        function updateLegend() {{
            const legend = document.getElementById('legend');
            let html = '<div class="legend-item"><div class="legend-spy"></div><span>SPY</span></div>';
            top20.forEach((stock, i) => {{
                html += `<div class="legend-item"><div class="legend-dot" style="background: ${{COLORS[i % COLORS.length]}}"></div><span>${{stock.symbol}}</span></div>`;
            }});
            legend.innerHTML = html;
        }}

        function update() {{
            top20 = getTop20(currentPeriod);
            selectedStock = null;
            updateChart();
            updateTable();
            updateLegend();
            updateInfoCard();
        }}

        document.querySelectorAll('.period-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentPeriod = btn.dataset.period;
                update();
            }});
        }});

        let resizeTimeout;
        window.addEventListener('resize', () => {{
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {{
                if (chart) {{ chart.update('none'); }}
            }}, 200);
        }});

        update();
    </script>
</body>
</html>'''
    
    output_path = Path(__file__).parent.parent / "index.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    # spy-outperform.html 도 같이 생성
    outperform_path = Path(__file__).parent.parent / "spy-outperform.html"
    with open(outperform_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"✅ HTML 생성 완료: {output_path}")


if __name__ == "__main__":
    generate_html()
