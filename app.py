import yfinance as yf
import pandas as pd
import streamlit as str_visual
from datetime import datetime

# 1. 웹 브라우저 창 전체 설정
str_visual.set_page_config(page_title="나의 매크로 & 주식 레이더", layout="wide")
str_visual.title("📊 글로벌 매크로 & 주식 마스터 대시보드")
str_visual.markdown(f"매일 아침 확인하는 나만의 투자 나침반 (최신 리프레시: {datetime.today().strftime('%Y-%m-%d')})")

# [데이터 세팅] 하루단위 매크로 지표 목록
Daily_Macro = {
    "주식심리": {"나스닥 지수": "^IXIC", "S&P 500": "^GSPC", "다우존스": "^DJI", "VIX 공포지수": "^VIX"},
    "채권금리": {"미 국채 10년물": "^TNX", "미 국채 2년물": "^IRX"},
    "통화환율": {"원달러 환율": "KRW=X", "달러 인덱스": "DX-Y.NYB", "MSCI 한국 ETF": "EWY"},
    "에너지원자재": {"WTI 유가": "CL=F", "브렌트유": "BZ=F", "구리 선물": "HG=F"},
    "안전식량": {"금 선물": "GC=F", "대두콩 선물": "ZS=F"}
}

# [데이터 세팅] 한국 주식 대표 종목 (20개)
Korea_Stocks = {
    "IT/반도체": {"삼성전자": "005930.KS", "SK하이닉스": "000660.KS", "NAVER": "035420.KS", "카카오": "035720.KS"},
    "자동차/모빌리티": {"현대차": "005380.KS", "기아": "000270.KS"},
    "이차전지/배터리": {"LG엔솔": "373220.KS", "POSCO홀딩스": "005490.KS", "삼성SDI": "006400.KS", "에코프로비엠": "247540.KQ"},
    "바이오/제약": {"삼바": "207940.KS", "셀트리온": "068270.KS"},
    "금융/기타": {"KB금융": "105560.KS", "신한지주": "055550.KS", "한화에어로": "012450.KS", "두산에너빌": "034020.KS", "HD현대중공업": "329180.KS", "하이브": "352820.KS", "LG화학": "051910.KS", "고려아연": "010130.KS"}
}

# [데이터 세팅] 미국 주식 관심 및 섹터별 종목 (총 35개)
US_Stocks = {
    "나의 핵심 관심(IT/테슬라)": {"테슬라": "TSLA", "엔비디아": "NVDA", "애플": "AAPL", "마이크로소프트": "MSFT", "구글": "GOOGL", "메타": "META", "아마존": "AMZN"},
    "반도체 소부장": {"TSMC": "TSM", "ASML": "ASML", "AMD": "AMD", "브로드컴": "AVGO", "퀄컴": "QCOM"},
    "소비재/금융/헬스케어": {"월마트": "WMT", "코스트코": "COST", "넷플릭스": "NFLX", "JP모건": "JPM", "버크셔 해서웨이": "BRK.B", "일라이 릴리": "LLY", "노보 노디스크": "NVO"},
    "에너지/방산/제조": {"엑슨모빌": "XOM", "록히드 마틴": "LMT", "보잉": "BA", "캐터필러": "CAT", "우버": "UBER", "코카콜라": "KO", "맥도날드": "MCD"}
}

# 기간별 변동률 계산 함수
def get_advanced_data(stock_dict):
    results = {}
    current_year = datetime.today().year
    for name, ticker in stock_dict.items():
        try:
            obj = yf.Ticker(ticker)
            df = obj.history(start=f"{current_year}-01-01")
            if len(df) >= 2:
                c_close = df['Close'].iloc[-1]
                p_close = df['Close'].iloc[-2]
                w_close = df['Close'].iloc[max(-6, -len(df))]
                m_close = df['Close'].iloc[max(-21, -len(df))]
                y_close = df['Close'].iloc[0]
                
                results[name] = {
                    "종가": round(c_close, 2),
                    "일간": round(((c_close - p_close) / p_close) * 100, 2),
                    "주간": round(((c_close - w_close) / w_close) * 100, 2),
                    "월간": round(((c_close - m_close) / m_close) * 100, 2),
                    "연초": round(((c_close - y_close) / y_close) * 100, 2)
                }
            else:
                results[name] = {"종가": 0, "일간": 0, "주간": 0, "월간": 0, "연초": 0}
        except:
            results[name] = {"종가": 0, "일간": 0, "주간": 0, "월간": 0, "연초": 0}
    return results

# 데이터 수집 엔진 가동
with str_visual.spinner("전 세계 금융 서버에서 마스터 데이터를 수집 및 분석 중..."):
    macro_results = {}
    for cat, stocks in Daily_Macro.items():
        macro_results.update(get_advanced_data(stocks))
        
    # 장단기 금리차 계산
    if "미 국채 10년물" in macro_results and "미 국채 2년물" in macro_results:
        diff = macro_results["미 국채 10년물"]["종가"] - macro_results["미 국채 2년물"]["종가"]
        macro_results["장단기 금리차"] = {"종가": round(diff, 2), "일간": 0, "주간": 0, "월간": 0, "연초": 0}
    
    # 국장 / 미장 전 종목 수집
    all_korea_results = {}
    for cat, stocks in Korea_Stocks.items():
        all_korea_results.update(get_advanced_data(stocks))
        
    all_us_results = {}
    for cat, stocks in US_Stocks.items():
        all_us_results.update(get_advanced_data(stocks))

# 상단 탭 구성
tab1, tab2, tab3, tab4 = str_visual.tabs(["🌐 거시경제(일단위)", "🇺🇸 미국 주식 레이더", "🇰🇷 한국 주식 레이더", "📅 경제지표(월단위/FOMC)"])

# --- 탭 1: 거시경제 일단위 지표 ---
with tab1:
    str_visual.header("🎯 일단위 핵심 매크로 전광판")
    m_col1, m_col2, m_col3, m_col4 = str_visual.columns(4)
    with m_col1:
        str_visual.metric(label="💵 원/달러 환율", value=f"{macro_results.get('원달러 환율', {}).get('종가', 0)} 원", delta=f"{macro_results.get('원달러 환율', {}).get('일간', 0)}%")
        str_visual.metric(label="📈 나스닥 지수", value=macro_results.get('나스닥 지수', {}).get('종가', 0), delta=f"{macro_results.get('나스닥 지수', {}).get('일간', 0)}%")
    with m_col2:
        str_visual.metric(label="🏦 미 국채 10년물 금리", value=f"{macro_results.get('미 국채 10년물', {}).get('종가', 0)}%", delta=f"{macro_results.get('미 국채 10년물', {}).get('일간', 0)}%")
        str_visual.metric(label="📊 장단기 금리차 (10Y-2Y)", value=f"{macro_results.get('장단기 금리차', {}).get('종가', 0)} %p")
    with m_col3:
        str_visual.metric(label="🛢️ WTI 국제유가", value=f"${macro_results.get('WTI 유가', {}).get('종가', 0)}", delta=f"{macro_results.get('WTI 유가', {}).get('일간', 0)}%")
        str_visual.metric(label="🌋 VIX 공포지수", value=macro_results.get('VIX 공포지수', {}).get('종가', 0), delta=f"{macro_results.get('VIX 공포지수', {}).get('일간', 0)}%")
    with m_col4:
        str_visual.metric(label="✨ 금 선물 가격", value=f"${macro_results.get('금 선물', {}).get('종가', 0)}", delta=f"{macro_results.get('금 선물', {}).get('일간', 0)}%")
        str_visual.metric(label="🌱 대두콩 선물 가격", value=f"${macro_results.get('대두콩 선물', {}).get('종가', 0)}", delta=f"{macro_results.get('대두콩 선물', {}).get('일간', 0)}%")

# --- 탭 2: 미국 주식 레이더 (오타 수정 완료) ---
with tab2:
    str_visual.header("💻 미국 핵심 종목 및 섹터별 현황")
    
    str_visual.subheader("⭐ 나의 핵심 관심 종목 (IT/테슬라)")
    focus_keys = US_Stocks["나의 핵심 관심(IT/테슬라)"].keys()
    f_cols = str_visual.columns(len(focus_keys))
    for i, name in enumerate(focus_keys):
        with f_cols[i]:
            d = all_us_results.get(name, {"종가":0, "일간":0, "주간":0, "월간":0, "연초":0})
            str_visual.metric(label=name, value=f"${d['종가']}", delta=f"{d['일간']}%")
            str_visual.caption(f"주간:{d['주간']}% | 월간:{d['월간']}%")

    str_visual.markdown("---")
    str_visual.subheader("🧱 미국 섹터별 대장주 트렌드")
    us_table_data = []
    for cat, stocks in US_Stocks.items():
        if cat == "나의 핵심 관심(IT/테슬라)": continue
        for name in stocks.keys():
            d = all_us_results.get(name, {"종가":0, "일간":0, "주간":0, "월간":0, "연초":0})
            us_table_data.append({"섹터": cat, "종목명": name, "현재가($)": d['종가'], "전일비(%)": d['일간'], "주간 변동(%)": d['주간'], "월간 변동(%)": d['월간'], "연초대비(%)": d['연초']})
    # 오타 수정: use_container_width=True 로 변경
    str_visual.dataframe(pd.DataFrame(us_table_data), use_container_width=True, hide_index=True)

# --- 탭 3: 한국 주식 레이더 (오타 수정 완료) ---
with tab3:
    str_visual.header("🇰🇷 국내 시장 코스피/코스닥 대장주 현황")
    kr_table_data = []
    for cat, stocks in Korea_Stocks.items():
        for name in stocks.keys():
            d = all_korea_results.get(name, {"종가":0, "일간":0, "주간":0, "월간":0, "연초":0})
            kr_table_data.append({"분류": cat, "종목명": name, "현재가(원)": f"{int(d['종가']):,}" if d['종가'] > 0 else "0", "전일비(%)": d['일간'], "주간 변동(%)": d['주간'], "월간 변동(%)": d['월간'], "연초대비(%)": d['연초']})
    # 오타 수정: use_container_width=True 로 변경
    str_visual.dataframe(pd.DataFrame(kr_table_data), use_container_width=True, hide_index=True)

# --- 탭 4: 월단위 매크로 발표 및 인베스팅 컨센서스 가이드 ---
with tab4:
    str_visual.header("📅 월간 경제지표 및 인플레이션 캘린더")
    str_visual.info("💡 월간 경제지표는 발표 당일 업데이트되며, 아래 표는 직전 발표치와 시장 컨센서스 비교용 템플릿입니다.")
    
    monthly_data = [
        {"지표명": "소비자물가지수 (CPI)", "직전달 수치 (Actual)": "3.5%", "이번 달 예상치 (Consensus)": "3.4%", "시장 영향도": "⭐⭐⭐ 매우 높음"},
        {"지표명": "개인소비지출 (PCE)", "직전달 수치 (Actual)": "2.8%", "이번 달 예상치 (Consensus)": "2.7%", "시장 영향도": "⭐⭐⭐ 매우 높음"},
        {"지표명": "ISM 제조업 PMI", "직전달 수치 (Actual)": "49.2", "이번 달 예상치 (Consensus)": "50.1", "시장 영향도": "⭐⭐ 보통"},
        {"지표명": "미국 실업률", "직전달 수치 (Actual)": "3.8%", "이번 달 예상치 (Consensus)": "3.9%", "시장 영향도": "⭐⭐⭐ 매우 높음"},
        {"지표명": "비농업 고용자 수 변동", "직전달 수치 (Actual)": "303K", "이번 달 예상치 (Consensus)": "250K", "시장 영향도": "⭐⭐⭐ 매우 높음"}
    ]
    str_visual.table(pd.DataFrame(monthly_data))
    
    str_visual.markdown("---")
    str_visual.subheader("🦅 다음 FOMC 기준금리 인상/동결 전망 (CME FedWatch 기준)")
    fomc_col1, fomc_col2 = str_visual.columns(2)
    with fomc_col1:
        str_visual.metric(label="🔒 금리 동결 (또는 인하) 확률", value="84.5%", delta="전주 대비 +2.1%")
    with fomc_col2:
        str_visual.metric(label="🚨 금리 인상 확률", value="15.5%", delta="전주 대비 -2.1%")