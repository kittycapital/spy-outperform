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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SPY 대비 상위 종목</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Inter', -apple-system, sans-serif; 
            background: #000; 
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        
        .header {{ 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            margin-bottom: 20px;
            flex-wrap: wrap;
            gap: 16px;
        }}
        .title {{ font-size: 24px; font-weight: 700; }}
        .updated {{ font-size: 12px; color: #6b7280; }}
        
        .period-buttons {{
            display: flex;
            gap: 8px;
            background: #111;
            padding: 4px;
            border-radius: 8px;
        }}
        .period-btn {{
            padding: 8px 16px;
            border: none;
            background: transparent;
            color: #9ca3af;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            border-radius: 6px;
            transition: all 0.2s;
        }}
        .period-btn:hover {{ color: #fff; }}
        .period-btn.active {{ background: #3b82f6; color: #fff; }}
        
        .spy-info {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: #111;
            border-radius: 8px;
            font-size: 14px;
        }}
        .spy-label {{ color: #6b7280; }}
        .spy-value {{ font-weight: 600; color: #22c55e; }}
        .spy-value.negative {{ color: #ef4444; }}
        
        .main-content {{
            display: grid;
            grid-template-columns: 1fr 380px;
            gap: 20px;
        }}
        @media (max-width: 1100px) {{
            .main-content {{ grid-template-columns: 1fr; }}
        }}
        
        .chart-container {{
            background: #111;
            border-radius: 12px;
            padding: 20px;
            height: 500px;
        }}
        
        .table-container {{
            background: #111;
            border-radius: 12px;
            overflow: hidden;
            max-height: 500px;
            display: flex;
            flex-direction: column;
        }}
        .table-header {{
            padding: 16px;
            border-bottom: 1px solid #222;
            flex-shrink: 0;
        }}
        .table-title {{ font-size: 14px; font-weight: 600; }}
        
        .table-scroll {{
            overflow-y: auto;
            flex: 1;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th {{
            text-align: left;
            padding: 10px 12px;
            font-size: 10px;
            font-weight: 600;
            color: #6b7280;
            text-transform: uppercase;
            border-bottom: 1px solid #222;
            position: sticky;
            top: 0;
            background: #111;
        }}
        td {{
            padding: 10px 12px;
            font-size: 12px;
            border-bottom: 1px solid #1a1a1a;
        }}
        tr {{
            cursor: pointer;
            transition: all 0.2s;
        }}
        tr:hover {{ background: #1a1a1a; }}
        tr.selected {{ background: #1e3a5f; }}
        tr.dimmed {{ opacity: 0.4; }}
        
        .rank {{ 
            color: #6b7280; 
            font-weight: 500;
            width: 30px;
        }}
        .stock-info {{
            display: flex;
            flex-direction: column;
            gap: 2px;
        }}
        .stock-symbol {{ font-weight: 600; font-size: 13px; }}
        .stock-name {{ font-size: 10px; color: #6b7280; }}
        
        .perf-value {{
            font-weight: 600;
            text-align: right;
        }}
        .perf-value.positive {{ color: #22c55e; }}
        .perf-value.negative {{ color: #ef4444; }}
        
        .vs-spy {{
            font-size: 11px;
            text-align: right;
        }}
        .vs-spy.positive {{ color: #22c55e; }}
        .vs-spy.negative {{ color: #ef4444; }}
        
        .legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 16px;
            padding: 12px;
            background: #111;
            border-radius: 8px;
            font-size: 11px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 4px;
        }}
        .legend-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }}
        .legend-spy {{
            width: 16px;
            height: 2px;
            border-top: 2px dashed #6b7280;
        }}
        
        .stock-info-card {{
            display: none;
            background: #111;
            border-radius: 12px;
            padding: 20px;
            margin-top: 16px;
        }}
        .stock-info-card.visible {{
            display: block;
        }}
        .info-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 16px;
            gap: 16px;
        }}
        .info-title {{
            font-size: 18px;
            font-weight: 700;
        }}
        .info-sector {{
            font-size: 12px;
            color: #9ca3af;
            margin-top: 4px;
        }}
        .info-close {{
            background: none;
            border: none;
            color: #6b7280;
            font-size: 20px;
            cursor: pointer;
            padding: 4px 8px;
        }}
        .info-close:hover {{
            color: #fff;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 16px;
            margin-bottom: 16px;
        }}
        .info-item {{
            background: #1a1a1a;
            padding: 12px;
            border-radius: 8px;
        }}
        .info-label {{
            font-size: 11px;
            color: #6b7280;
            margin-bottom: 4px;
        }}
        .info-value {{
            font-size: 16px;
            font-weight: 600;
        }}
        .info-description {{
            font-size: 13px;
            color: #9ca3af;
            line-height: 1.5;
            padding-top: 16px;
            border-top: 1px solid #222;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1 class="title">📈 SPY 대비 상위 종목</h1>
                <p class="updated">마지막 업데이트: {last_updated} · S&P 500 + Nasdaq 100</p>
            </div>
            <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
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
        </div>
        
        <div class="main-content">
            <div class="chart-container">
                <canvas id="perfChart"></canvas>
            </div>
            
            <div class="table-container">
                <div class="table-header">
                    <div class="table-title">🏆 상위 20 종목</div>
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
                        <tbody id="table-body">
                        </tbody>
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
    </div>

    <script>
        const SPY_DATA = {spy_json};
        const STOCKS = {stocks_json};
        const STOCK_NAMES = {stock_names_json};
        const STOCK_INFO = {stock_info_json};
        
        // 색상 팔레트
        const COLORS = [
            '#3b82f6', '#ef4444', '#22c55e', '#f59e0b', '#8b5cf6',
            '#06b6d4', '#ec4899', '#84cc16', '#f97316', '#14b8a6',
            '#a855f7', '#eab308', '#64748b', '#dc2626', '#0891b2',
            '#c026d3', '#e11d48', '#ea580c', '#16a34a', '#2563eb'
        ];
        
        let currentPeriod = 'YTD';
        let chart = null;
        let top20 = [];
        let selectedStock = null;
        
        // 기간별 날짜 계산
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
        
        // 가격 데이터를 % 변화로 변환
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
        
        // 상위 20개 계산
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
        
        // 차트 업데이트
        function updateChart() {{
            const startDate = getStartDate(currentPeriod);
            const datasets = [];
            
            // SPY 데이터 (점선)
            const spyData = calculatePercentChange(SPY_DATA.prices, startDate);
            datasets.push({{
                label: 'SPY',
                data: spyData,
                borderColor: '#6b7280',
                borderWidth: 2,
                borderDash: [5, 5],
                pointRadius: 0,
                tension: 0.1,
                fill: false
            }});
            
            // 상위 20개 종목
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
                                backgroundColor: '#1f2937',
                                titleColor: '#fff',
                                bodyColor: '#d1d5db',
                                padding: 10,
                                bodyFont: {{ size: 11 }},
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
                                grid: {{ color: '#222' }},
                                ticks: {{ color: '#6b7280', font: {{ size: 10 }} }}
                            }},
                            y: {{
                                grid: {{ color: '#222' }},
                                ticks: {{
                                    color: '#6b7280',
                                    font: {{ size: 10 }},
                                    callback: (v) => v + '%'
                                }}
                            }}
                        }}
                    }}
                }});
            }}
        }}
        
        // 테이블 업데이트
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
            
            // 클릭 이벤트
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
        
        // 종목 정보 카드 업데이트
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
        
        // 정보 카드 닫기 버튼
        document.getElementById('info-close').addEventListener('click', () => {{
            selectedStock = null;
            updateChart();
            updateTable();
            updateInfoCard();
        }});
        
        // 범례 업데이트
        function updateLegend() {{
            const legend = document.getElementById('legend');
            
            let html = '<div class="legend-item"><div class="legend-spy"></div><span>SPY</span></div>';
            
            top20.forEach((stock, i) => {{
                html += `<div class="legend-item"><div class="legend-dot" style="background: ${{COLORS[i % COLORS.length]}}"></div><span>${{stock.symbol}}</span></div>`;
            }});
            
            legend.innerHTML = html;
        }}
        
        // 전체 업데이트
        function update() {{
            top20 = getTop20(currentPeriod);
            selectedStock = null;
            updateChart();
            updateTable();
            updateLegend();
        }}
        
        // 기간 버튼 이벤트
        document.querySelectorAll('.period-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentPeriod = btn.dataset.period;
                update();
            }});
        }});
        
        // 초기화
        update();
    </script>
</body>
</html>'''
    
    output_path = Path(__file__).parent.parent / "index.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"✅ HTML 생성 완료: {output_path}")


if __name__ == "__main__":
    generate_html()
