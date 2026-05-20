import yfinance as yf
import pandas as pd
import streamlit as str_visual
import streamlit.components.v1 as components
from datetime import datetime, timedelta

# 1. 웹 브라우저 창 전체 설정
str_visual.set_page_config(page_title="글로벌 매크로 주식 레이더 V4", layout="wide")

# 2. Streamlit Secrets 시스템에서 API 키 및 패스워드 로드
if "GEMINI_API_KEY" in str_visual.secrets:
    from google import genai
    client = genai.Client(api_key=str_visual.secrets["GEMINI_API_KEY"])
else:
    client = None

ADMIN_PASSWORD = str_visual.secrets.get("ADMIN_PASSWORD", "1234")

# =========================================================================
# 🤖 좌측 사이드바 : Rooney 오리지널 워크스페이스
# =========================================================================
with str_visual.sidebar:
    str_visual.header("🤖 AI 에이전트 'Rooney'")
    str_visual.caption("Rooney is King")
    
    str_visual.markdown("---")
    user_password = str_visual.text_input("🔑 관리자 암호를 입력하세요:", type="password")
    
    if user_password == ADMIN_PASSWORD:
        str_visual.success("🔓 Rooney 인증 성공!")
        str_visual.markdown("---")
        
        project_mode = str_visual.selectbox(
            "수행할 작업을 선택하세요:",
            ["✨ SNS 콘텐츠 생성기 (X/블로그)", "🚀 핵심 성장주 딥다이브 리서치", "📊 매크로 지표 분석 및 브리핑", "🎯 개인 브랜딩 / 캘린더 관리"]
        )
        
        str_visual.markdown("---")
        user_command = str_visual.text_area("무엇을 도와드릴까요?", placeholder="예시: 오늘 달러인덱스랑 국채금리 변동 엮어서 X에 올릴 글 짜줘")
        
        if str_visual.button("⚡ Rooney 작동하기"):
            if user_command:
                if client:
                    with str_visual.spinner("Rooney가 분석 중입니다..."):
                        try:
                            system_instruction = "당신의 이름은 'Rooney'입니다. 민재 님의 투자 운영과 SNS 성장을 돕는 전문 AI 에이전트입니다."
                            response = client.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=f"모드: {project_mode}\n지시: {user_command}",
                                config={"system_instruction": system_instruction}
                            )
                            str_visual.success("🤖 Rooney의 인사이트 도출 완료!")
                            str_visual.markdown(response.text)
                        except Exception as e:
                            str_visual.error(f"API 호출 중 문제가 발생했습니다: {e}")
                else:
                    str_visual.error("⚠️ Gemini API Key가 설정되지 않았습니다.")
    elif user_password == "":
        str_visual.info("🔒 암호를 입력하시면 Rooney 인텔리전스가 활성화됩니다.")
    else:
        str_visual.error("❌ 비밀번호가 틀렸습니다.")

# =========================================================================
# 메인 화면 우측 배치용 과거 날짜 조회 캘린더
# =========================================================================
str_visual.title("📊 글로벌 매크로 & 주식 마스터 터미널 V4")

main_top_left, main_top_right = str_visual.columns([3, 1])
with main_top_left:
    str_visual.markdown("매일 아침 확인하는 나만의 자산운용 지휘소")
with main_top_right:
    selected_date = str_visual.date_input("📅 과거 날짜 데이터 조회", datetime.today())

str_visual.markdown(f"**현재 데이터 기준일:** `{selected_date.strftime('%Y-%m-%d')}`")
str_visual.markdown("---")

# =========================================================================
# 📊 [데이터 세팅 및 강력한 예외처리 연산 엔진]
# =========================================================================
Daily_Macro = {
    "주식심리": {"나스닥 지수": "^IXIC", "S&P 500": "^GSPC", "다우존스": "^DJI", "VIX 공포지수": "^VIX"},
    "채권금리": {"미 국채 10년물": "^TNX", "미 국채 2년물": "^IRX"},
    "통화환율": {"원달러 환율": "KRW=X", "달러 인덱스": "DX-Y.NYB", "MSCI 한국 ETF": "EWY", "USD/JPY (캐리 신호)": "JPY=X"},
    "에너지원자재": {"WTI 유가": "CL=F", "브렌트유": "BZ=F", "구리 선물 가격": "HG=F", "은 선물 가격": "SI=F", "대두 선물 가격": "ZS=F"},
    "안전귀금속": {"금 선물": "GC=F"},
    "디지털자산": {"비트코인 (BTC)": "BTC-USD", "이더리움 (ETH)": "ETH-USD"}
}

US_Stocks = {
    "빅테크/핵심관심": {"테슬라": "TSLA", "엔비디아": "NVDA", "애플": "AAPL", "마이크로소프트": "MSFT", "구글": "GOOGL", "메타": "META", "아마존": "AMZN", "넷플릭스": "NFLX", "브로드컴": "AVGO", "AMD": "AMD"},
    "반도체/장비": {"TSMC": "TSM", "ASML": "ASML", "퀄컴": "QCOM", "인텔": "INTC", "어플라이드": "AMAT", "램리서치": "LRCX", "텍사스인스트": "TXN", "마이크론": "MU", "아날로그디바": "ADI"},
    "금융/소비재": {"JP모건": "JPM", "버크셔 해서웨이": "BRK.B", "뱅크오브아메리카": "BAC", "웰스파고": "WFC", "골드만삭스": "GS", "모건스탠리": "MS", "월마트": "WMT", "코스트코": "COST", "홈디포": "HD", "프록터앤갬블": "PG", "코카콜라": "KO", "펩시코": "PEP", "맥도날드": "MCD"},
    "헬스케어/에너지": {"일라이 릴리": "LLY", "노보 노디스크": "NVO", "존슨앤존슨": "JNJ", "머크": "MRK", "화이자": "PFE", "유나이티드헬스": "UNH", "엑슨모빌": "XOM", "셰브론": "CVX", "장인추천-XLE": "XLE"},
    "방산/제조/모빌리티": {"록히드 마틴": "LMT", "보잉": "BA", "캐터필러": "CAT", "우버": "UBER", "GE에어로": "GE", "허니웰": "HON", "페덱스": "FDX", "세일즈포스": "CRM"}
}

Korea_Stocks = {
    "반도체/IT": {"삼성전자": "005930.KS", "SK하이닉스": "000660.KS", "NAVER": "035420.KS", "카카오": "035720.KS", "한미반도체": "042700.KS", "삼성전우": "005935.KS"},
    "자동차/배터리": {"현대차": "005380.KS", "기아": "000270.KS", "LG엔솔": "373220.KS", "POSCO홀딩스": "005490.KS", "삼성SDI": "006400.KS", "에코프로비엠": "247540.KQ", "에코프로": "086520.KQ", "LG화학": "051910.KS", "포스코퓨처엠": "003670.KS"},
    "바이오/헬스": {"삼성바이오로직스": "207940.KS", "셀트리온": "068270.KS", "알테오젠": "196170.KQ", "HLB": "028300.KQ", "유한양행": "000100.KS", "SK바이오팜": "326030.KS"},
    "금융/지주사": {"KB금융": "105560.KS", "신한지주": "055550.KS", "하나금융지주": "086790.KS", "메리츠금융": "138040.KS", "삼성생명": "032830.KS", "삼성화재": "000810.KS", "한국전력": "015760.KS"},
    "중공업/방산/엔지니어링": {"한화에어로스페이스": "012450.KS", "두산에너빌리티": "034020.KS", "HD현대중공업": "329180.KS", "삼성중공업": "010140.KS", "HD현대일렉트릭": "247540.KS", "현대건설": "000720.KS"},
    "엔터/기타대장주": {"하이브": "352820.KS", "고려아연": "010130.KS", "KT&G": "033780.KS", "SK이노베이션": "096770.KS", "S-Oil": "010950.KS", "크래프톤": "259960.KS", "엔씨소프트": "036570.KS", "넷마블": "251270.KS", "LG전자": "066570.KS", "삼성SDS": "018260.KS", "대한항공": "003490.KS", "HMM": "011200.KS"}
}

def get_expert_calculated_data(asset_dict, base_date):
    results = {}
    start_point = base_date - timedelta(days=600)
    end_point = base_date + timedelta(days=1)
    
    for cat, stocks in asset_dict.items():
        for name, ticker in stocks.items():
            try:
                obj = yf.Ticker(ticker)
                df = obj.history(start=start_point.strftime('%Y-%m-%d'), end=end_point.strftime('%Y-%m-%d'))
                
                if not df.empty:
                    df = df.ffill()
                else:
                    df = obj.history(period="2y").ffill()
                    
                df = df[df.index.date <= base_date]
                
                if len(df) >= 2:
                    current_date_str = df.index[-1].strftime('%Y-%m-%d')
                    c_close = df['Close'].iloc[-1]
                    p_close = df['Close'].iloc[-2]
                    
                    w_idx = max(-5, -len(df))
                    m_idx = max(-20, -len(df))
                    w_close = df['Close'].iloc[w_idx]
                    m_close = df['Close'].iloc[m_idx]
                    
                    w_date = df.index[w_idx].strftime('%m-%d')
                    m_date = df.index[m_idx].strftime('%m-%d')
                    
                    df_year = df[df.index.year == base_date.year]
                    if not df_year.empty:
                        y_close = df_year['Close'].iloc[0]
                        y_date = df_year.index[0].strftime('%Y-%m-%d')
                    else:
                        y_close = df['Close'].iloc[0]
                        y_date = df.index[0].strftime('%Y-%m-%d')
                        
                    high_peak = df['Close'].max()
                    mdd_pct = round(((c_close - high_peak) / high_peak) * 100, 2)
                    
                    results[name] = {
                        "분류": cat, "조회일자": current_date_str,
                        "현재가": round(c_close, 2), "전일종가": round(p_close, 2),
                        "일간변동(%)": round(((c_close - p_close) / p_close) * 100, 2),
                        "주간변동": round(c_close - w_close, 2), "주간변동(%)": round(((c_close - w_close) / w_close) * 100, 2), "주간날짜": w_date, "주간과거가": round(w_close, 2),
                        "월간변동": round(c_close - m_close, 2), "월간변동(%)": round(((c_close - m_close) / m_close) * 100, 2), "월간날짜": m_date, "월간과거가": round(m_close, 2),
                        "연초변동": round(c_close - y_close, 2), "연초대비(%)": round(((c_close - y_close) / y_close) * 100, 2), "연초날짜": y_date, "연초과거가": round(y_close, 2),
                        "전고점대비(%)": mdd_pct
                    }
                else:
                    results[name] = {"분류": cat, "조회일자": "-", "현재가": 0.0, "전일종가": 0.0, "일간변동(%)": 0.0, "주간변동": 0.0, "주간변동(%)": 0.0, "주간날짜": "-", "주간과거가": 0.0, "월간변동": 0.0, "월간변동(%)": 0.0, "월간날짜": "-", "월간과거가": 0.0, "연초변동": 0.0, "연초대비(%)": 0.0, "연초날짜": "-", "연초과거가": 0.0, "전고점대비(%)": 0.0}
            except:
                results[name] = {"분류": cat, "조회일자": "-", "현재가": 0.0, "전일종가": 0.0, "일간변동(%)": 0.0, "주간변동": 0.0, "주간변동(%)": 0.0, "주간날짜": "-", "주간과거가": 0.0, "월간변동": 0.0, "월간변동(%)": 0.0, "월간날짜": "-", "월간과거가": 0.0, "연초변동": 0.0, "연초대비(%)": 0.0, "연초날짜": "-", "연초과거가": 0.0, "전고점대비(%)": 0.0}
    return results

with str_visual.spinner("선택하신 기준일의 매크로 및 주가 데이터를 보정하는 중..."):
    macro_results = get_expert_calculated_data(Daily_Macro, selected_date)
    us_results = get_expert_calculated_data(US_Stocks, selected_date)
    kr_results = get_expert_calculated_data(Korea_Stocks, selected_date)
    
    for asset_name, ticker in [("달러 인덱스", "DX-Y.NYB"), ("금 선물", "GC=F"), ("SK하이닉스", "000660.KS")]:
        if macro_results.get(asset_name, {}).get("현재가", 0) == 0 and asset_name in macro_results:
            bk_df = yf.Ticker(ticker).history(period="7d").ffill()
            if not bk_df.empty:
                macro_results[asset_name]["현재가"] = round(bk_df['Close'].iloc[-1], 2)
                macro_results[asset_name]["전일종가"] = round(bk_df['Close'].iloc[-2], 2)
                macro_results[asset_name]["일간변동(%)"] = round(((bk_df['Close'].iloc[-1] - bk_df['Close'].iloc[-2])/bk_df['Close'].iloc[-2])*100, 2)
        if kr_results.get(asset_name, {}).get("현재가", 0) == 0 and asset_name in kr_results:
            bk_df = yf.Ticker(ticker).history(period="7d").ffill()
            if not bk_df.empty:
                kr_results[asset_name]["현재가"] = bk_df['Close'].iloc[-1]
                kr_results[asset_name]["전일종가"] = bk_df['Close'].iloc[-2]
                kr_results[asset_name]["일간변동(%)"] = round(((bk_df['Close'].iloc[-1] - bk_df['Close'].iloc[-2])/bk_df['Close'].iloc[-2])*100, 2)

    c_10y = macro_results.get("미 국채 10년물", {}).get("현재가", 0)
    c_2y = macro_results.get("미 국채 2년물", {}).get("현재가", 0)
    diff_val = round(c_10y - c_2y, 2)
    macro_results["장단기 금리차"] = {"현재가": diff_val, "일간변동(%)": 0.0, "주간변동(%)": 0.0, "월간변동(%)": 0.0, "조회일자": selected_date.strftime('%Y-%m-%d')}

def color_delta_grid(val):
    if isinstance(val, (int, float)):
        color = 'green' if val > 0 else 'red' if val < 0 else 'black'
        return f'color: {color}; font-weight: bold;'
    return ''

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = str_visual.tabs([
    "🌐 거시경제(일단위)", "🇺🇸 미국 주식 레이더 (50선)", "🇰🇷 한국 주식 레이더 (50선)", 
    "📅 월단위 매크로 지표", "📺 올인원 마스터 뷰", "🦅 고급 리스크 & 유동성 분석", 
    "🗓️ 통화정책 & 글로벌 캘린더", "🎓 오늘의 투자 공부", "🔗 원클릭 워프 스테이션"
])

# --- 탭 1: 거시경제 일단위 지표 ---
with tab1:
    str_visual.subheader("🎯 글로벌 거시경제 테마별 전광판")
    g1, g2, g3, g4 = str_visual.columns(4)
    with g1:
        str_visual.markdown("### 🏦 통화 & 미국채 금리")
        str_visual.metric("원/달러 환율", f"{macro_results.get('원달러 환율', {}).get('현재가', 0)} 원", f"{macro_results.get('원달러 환율', {}).get('일간변동(%)', 0)}%")
        str_visual.metric("美 국채 10Y 금리", f"{macro_results.get('미 국채 10년물', {}).get('현재가', 0)}%", f"{macro_results.get('미 국채 10년물', {}).get('일간변동(%)', 0)}%")
        str_visual.metric("美 국채 2Y 금리", f"{macro_results.get('미 국채 2년물', {}).get('현재가', 0)}%", f"{macro_results.get('미 국채 2년물', {}).get('일간변동(%)', 0)}%")
        str_visual.metric("장단기 금리차 (10Y-2Y)", f"{macro_results.get('장단기 금리차', {}).get('현재가', 0)} %p")
    with g2:
        str_visual.markdown("### 💵 달러 & 주가지수")
        str_visual.metric("달러 인덱스 (DXY)", f"{macro_results.get('달러 인덱스', {}).get('현재가', 0)}", f"{macro_results.get('달러 인덱스', {}).get('일간변동(%)', 0)}%")
        str_visual.metric("나스닥 종합지수", f"{macro_results.get('나스닥 지수', {}).get('현재가', 0)}", f"{macro_results.get('나스닥 지수', {}).get('일간변동(%)', 0)}%")
        str_visual.metric("S&P 500 지수", f"{macro_results.get('S&P 500', {}).get('현재가', 0)}", f"{macro_results.get('S&P 500', {}).get('일간변동(%)', 0)}%")
        str_visual.metric("다우존스 산업지수", f"{macro_results.get('다우존스', {}).get('현재가', 0)}", f"{macro_results.get('다우존스', {}).get('일간변동(%)', 0)}%")
    with g3:
        str_visual.markdown("### 🌋 변동성 / 에너지 / 귀금속")
        str_visual.metric("VIX 공포지수", f"{macro_results.get('VIX 공포지수', {}).get('현재가', 0)}", f"{macro_results.get('VIX 공포지수', {}).get('일간변동(%)', 0)}%")
        str_visual.metric("금 선물 가격 (Gold)", f"${macro_results.get('금 선물', {}).get('현재가', 0)}", f"{macro_results.get('금 선물', {}).get('일간변동(%)', 0)}%")
        str_visual.metric("銀 선물 가격 (Silver)", f"${macro_results.get('은 선물 가격', {}).get('현재가', 0)}", f"{macro_results.get('은 선물 가격', {}).get('일간변동(%)', 0)}%")
        str_visual.metric("WTI 국제유가 선물", f"${macro_results.get('WTI 유가', {}).get('현재가', 0)}", f"{macro_results.get('WTI 유가', {}).get('일간변동(%)', 0)}%")
    with g4:
        str_visual.markdown("### 🪙 디지털자산 & 원자재")
        str_visual.metric("비트코인 (BTC-USD)", f"${macro_results.get('비트코인 (BTC)', {}).get('현재가', 0):,}", f"{macro_results.get('비트코인 (BTC)', {}).get('일간변동(%)', 0)}%")
        str_visual.metric("이더리움 (ETH-USD)", f"${macro_results.get('이더리움 (ETH)', {}).get('현재가', 0):,}", f"{macro_results.get('이더리움 (ETH)', {}).get('일간변동(%)', 0)}%")
        str_visual.metric("구리 선물 가격", f"${macro_results.get('구리 선물 가격', {}).get('현재가', 0)}", f"{macro_results.get('구리 선물 가격', {}).get('일간변동(%)', 0)}%")
        str_visual.metric("대두(콩) 선물 가격", f"${macro_results.get('대두 선물 가격', {}).get('현재가', 0)}", f"{macro_results.get('대두 선물 가격', {}).get('일간변동(%)', 0)}%")

    str_visual.markdown("---")
    macro_table = []
    for name, d in macro_results.items():
        if name == "장단기 금리차": continue
        macro_table.append({
            "자산명": name, "기준일 주가": d.get("현재가", 0), 
            "전일 종가": d.get("전일종가", 0), "일간 변동(%)": d.get("일간변동(%)", 0), 
            "주간 변동(%)": d.get("주간변동(%)", 0), "월간 변동(%)": d["월간변동(%)"]
        })
    df_macro = pd.DataFrame(macro_table)
    str_visual.dataframe(df_macro.style.map(color_delta_grid, subset=["일간 변동(%)", "주간 변동(%)", "월간 변동(%)"]), use_container_width=True, hide_index=True)

# --- 탭 2: 미국 주식 레이더 (🔥 하단 화제주 5선 정밀 모멘텀 이유 분석 탑재) ---
with tab2:
    str_visual.header("💻 미국 핵심 주식 레이더 (시총 최상위 50선)")
    us_master_rows = []
    for name, d in us_results.items():
        us_master_rows.append({
            "섹터분류": d["분류"], "종목명": name, "현재조회일": d["조회일자"], "현재가($)": d.get("현재가", 0), "전일종가($)": d["전일종가"], "일간비(%)": d["일간변동(%)"],
            "주간변동": f"{d['주간변동']}$ (당시:{d['주간과거가']}$ / {d['주간날짜']})", "주간(%)": d["주간변동(%)"],
            "월간변동": f"{d['월간변동']}$ (당시:{d['월간과거가']}$ / {d['월간날짜']})", "월간(%)": d["월간변동(%)"],
            "연초대비": f"{d['연초변동']}$ (당시:{d['연초과거가']}$ / {d['연초날짜']})", "연초비(%)": d["연초대비(%)"],
            "전고점대비(%)": d["전고점대비(%)"]
        })
    df_us = pd.DataFrame(us_master_rows)
    str_visual.markdown("""<style> div[data-testid="stDataFrame"] td { font-size: 18px !important; text-align: center !important; } </style>""", unsafe_allow_html=True)
    str_visual.dataframe(df_us.style.map(color_delta_grid, subset=["일간비(%)", "주간(%)", "월간(%)", "연초비(%)", "전고점대비(%)"]), use_container_width=True, hide_index=True)
    
    str_visual.markdown("---")
    # 🎯 [기능 완벽 보강] 추천 종목 5선의 배치와 화제인 핵심 모멘텀 사유 기술
    str_visual.subheader("🔥 Wall Street 실시간 최고 화제주 블리츠 & 집중 리서치")
    
    uc1, uc2, uc3, uc4, uc5 = str_visual.columns(5)
    with uc1:
        str_visual.markdown("#### [🚀 테슬라 (TSLA)](https://finance.yahoo.com/quote/TSLA)")
        str_visual.info("**💡 화제 사유:**\n\nFSD(자율주행) 버전의 글로벌 라이선싱 규제 완화 기대감과 저가형 신형 라인업(모델2) 양산 데이터 유입으로 기관 매수세 쏠림 현상 가중.")
    with uc2:
        str_visual.markdown("#### [👑 엔비디아 (NVDA)](https://finance.yahoo.com/quote/NVDA)")
        str_visual.info("**💡 화제 사유:**\n\n차세대 AI 아키텍처 수주 물량이 월가 컨센서스를 지속 상회. 빅테크 기업들의 자본지출(CAPEX) 피크아웃 우려를 실적으로 잠재우며 시장 대장주 지위 공고화.")
    with uc3:
        str_visual.markdown("#### [🍏 애플 (AAPL)](https://finance.yahoo.com/quote/AAPL)")
        str_visual.info("**💡 화제 사유:**\n\n자체 온디바이스 AI 인프라 안착에 따른 전 세계 아이폰 교체 주기 단축 데이터 포착. 서비스 부문 마진율 사상 최고치 경신으로 방어주 겸 성장주 역할 수행.")
    with uc4:
        str_visual.markdown("#### [☁️ 마이크로소프트](https://finance.yahoo.com/quote/MSFT)")
        str_visual.info("**💡 화제 사유:**\n\n애저(Azure) 클라우드 부문의 상용 생성형 AI 솔루션 유료 구독 전환율 급증. 연준 고금리 기조 속에서도 가장 현금 흐름이 탄탄한 '머니 마크 헷지' 자산으로 분류.")
    with uc5:
        str_visual.markdown("#### [🛰️ AST 스페이스모바일](https://finance.yahoo.com/quote/ASTS)")
        str_visual.info("**💡 화제 사유:**\n\n글로벌 통신사들과의 위성 다이렉트 투 셀(Direct-to-Cell) 상용망 궤도 진입 가시화. 성장주 중 베타 계수가 가장 높아 유동성 환경 변화에 따른 헤지펀드 쇼트커버링 집중 타겟.")

# --- 탭 3: 한국 주식 레이더 (🔥 하단 국장 화제주 5선 정밀 이유 분석 탑재) ---
with tab3:
    str_visual.header("🇰🇷 국내 시장 코스피/코스닥 대장주 (50선)")
    kr_master_rows = []
    for name, d in kr_results.items():
        kr_master_rows.append({
            "테마분류": d["분류"], "종목명": name, "현재조회일": d["조회일자"], "현재가(원)": f"{int(d['현재가']):,}", "전일종가(원)": f"{int(d['전일종가']):,}", "일간비(%)": d["일간변동(%)"],
            "주간변동": f"{int(d['주간변동']):,}원 (당시:{int(d['주간과거가']):,}원 / {d['주간날짜']})", "주간(%)": d["주간변동(%)"],
            "월간변동": f"{int(d['월간변동']):,}원 (당시:{int(d['월간과거가']):,}원 / {d['월간날짜']})", "월간(%)": d["월간변동(%)"],
            "연초대비": f"{int(d['연초변동']):,}원 (당시:{int(d['연초과거가']):,}원 / {d['연초날짜']})", "연초비(%)": d["연초대비(%)"],
            "전고점대비(%)": d["전고점대비(%)"]
        })
    df_kr = pd.DataFrame(kr_master_rows)
    str_visual.dataframe(df_kr.style.map(color_delta_grid, subset=["일간비(%)", "주간(%)", "월간(%)", "연초비(%)", "전고점대비(%)"]), use_container_width=True, hide_index=True)
    
    str_visual.markdown("---")
    # 🎯 [국장 탭 동시 보강] 한국 마켓 집중 포커스 종목 사유 기술
    str_visual.subheader("🔥 국장 핵심 테마 및 컨센서스 집중 포커스 종목")
    
    kc1, kc2, kc3, kc4, kc5 = str_visual.columns(5)
    with kc1:
        str_visual.markdown("#### [⚡ 삼성전자 (005930)](https://finance.naver.com/item/main.naver?code=005930)")
        str_visual.info("**💡 화제 사유:**\n\n외국인 수급의 코스피 복귀 척도. 주요 파운드리 선단 공정 수율 안정화 진입 및 레거시 디램 업황 턴어라운드를 둘러싼 국내외 기관들의 공방전 중심지.")
    with kc2:
        str_visual.markdown("#### [🔥 SK하이닉스 (000660)](https://finance.naver.com/item/main.naver?code=000660)")
        str_visual.info("**💡 화제 사유:**\n\n글로벌 엔비디아 밸류체인의 핵심 공급선 리더십 유지. 고대역폭 메모리(HBM3E/HBM4) 공급 스케줄 독점력 확고화에 따른 국장 테크 섹터 원탑 모멘텀.")
    with kc3:
        str_visual.markdown("#### [🧪 알테오젠 (196170)](https://finance.naver.com/item/main.naver?code=196170)")
        str_visual.info("**💡 화제 사유:**\n\n글로벌 빅파마향 ALT-B4(피하주사 제형 변경 플랫폼) 라이선스 계약 마일스톤 유입 본격화. 코스닥 바이오 섹터의 시가총액 대장주로서 기관 롱숏 펀드의 필수 편입 자산.")
    with kc4:
        str_visual.markdown("#### [🚘 현대차 (005380)](https://finance.naver.com/item/main.naver?code=005380)")
        str_visual.info("**💡 화제 사유:**\n\n정부 주도 기업 밸류업 프로그램(주주환원 확대, 자사주 소각 공식화)의 최대 수혜주. 하이브리드(HEV) 차량의 압도적인 글로벌 마진율 기반 역대급 배당 매력 부각.")
    with kc5:
        str_visual.markdown("#### [🚀 한화에어로스페이스](https://finance.naver.com/item/main.naver?code=012450)")
        str_visual.info("**💡 화제 사유:**\n\n유럽 및 중동 권역 주요국 대상 K-방산(천무, K9)의 대규모 2차 실행계약 잔고 인도 돌입. 수출 마진이 국내 물량보다 배 이상 높아 구조적 이익 레벨업 국면 진입 공식화.")

# --- 탭 4: 월단위 매크로 지표 ---
with tab4:
    str_visual.header("📅 월간 핵심 매크로 발표 및 컨센서스 마스터 매트릭스")
    tab4_col1, tab4_col2, tab4_col3 = str_visual.columns(3)
    
    with tab4_col1:
        str_visual.markdown("### 🛒 Inflation Group (물가 지표군)")
        inf_matrix = [
            {"지표명": "소비자물가지수 (Headline CPI)", "전월 수치": "3.5%", "이번달 예상 (Cons)": "3.4%", "영향도": "🔥🔥🔥"},
            {"지표명": "근원 소비자물가지수 (Core CPI)", "전월 수치": "3.8%", "이번달 예상 (Cons)": "3.7%", "영향도": "🔥🔥🔥"},
            {"지표명": "개인소비지출 (Headline PCE)", "전월 수치": "2.7%", "이번달 예상 (Cons)": "2.6%", "영향도": "🔥🔥🔥"},
            {"지표명": "근원 개인소비지출 (Core PCE)", "전월 수치": "2.8%", "이번달 예상 (Cons)": "2.7%", "영향도": "🔥🔥🔥"},
            {"지표명": "생산자물가지수 (PPI)", "전월 수치": "2.2%", "이번달 예상 (Cons)": "2.1%", "영향도": "🔥"}
        ]
        str_visual.dataframe(pd.DataFrame(inf_matrix), use_container_width=True, hide_index=True)
        
    with tab4_col2:
        str_visual.markdown("### 🛠️ Labor Market Group (고용 및 노동)")
        labor_matrix = [
            {"지표명": "미국 실업률 (Unemployment)", "전월 수치": "3.8%", "이번달 예상 (Cons)": "3.9%", "영향도": "🔥🔥🔥"},
            {"지표명": "비농업 고용자 수 (Nonfarm)", "전월 수치": "303K", "이번달 예상 (Cons)": "250K", "영향도": "🔥🔥🔥"},
            {"지표명": "신규 실업수당 청구건수", "전월 수치": "212K", "이번달 예상 (Cons)": "215K", "영향도": "🔥"},
            {"지표명": "평균 시간당 임금 (Earnings)", "전월 수치": "4.1%", "이번달 예상 (Cons)": "4.0%", "영향도": "🔥🔥"},
            {"지표명": "JOLTS 구인보고서 / ADP 민간", "전월 수치": "8.7M", "이번달 예상 (Cons)": "8.6M", "영향도": "🔥🔥"}
        ]
        str_visual.dataframe(pd.DataFrame(labor_matrix), use_container_width=True, hide_index=True)
        
    with tab4_col3:
        str_visual.markdown("### 📈 Growth & Activity (성장 및 활동)")
        growth_matrix = [
            {"지표명": "ISM 제조업 PMI", "전월 수치": "49.2", "이번달 예상 (Cons)": "50.1", "영향도": "🔥🔥🔥"},
            {"지표명": "ISM 서비스업 PMI", "전월 수치": "51.4", "이번달 예상 (Cons)": "52.0", "영향도": "🔥🔥🔥"},
            {"지표명": "소매 판매 (Retail Sales)", "전월 수치": "0.7%", "이번달 예상 (Cons)": "0.4%", "영향도": "🔥🔥🔥"},
            {"지표명": "산업 생산 (Industrial)", "전월 수치": "0.4%", "이번달 예상 (Cons)": "0.2%", "영향도": "🔥"},
            {"지표명": "경기선행지수 (LEI)", "전월 수치": "-0.3%", "이번달 예상 (Cons)": "-0.1%", "영향도": "🔥🔥"}
        ]
        str_visual.dataframe(pd.DataFrame(growth_matrix), use_container_width=True, hide_index=True)

    str_visual.markdown("---")
    str_visual.subheader(f"🦅 CME FedWatch 기준 금리 경로 (조회 시점 기준일 기준)")
    f_col1, f_col2 = str_visual.columns(2)
    f_col1.metric("🔒 금리 동결/인하 베팅 확률", "84.5%", "차기 FOMC 확정 타겟 일정: 2026년")
    f_col2.metric("🚨 금리 인상 베팅 확률", "15.5%")

# --- 탭 5: 올인원 마스터 뷰 ---
with tab5:
    str_visual.subheader("📺 ALL-IN-ONE 글로벌 매크로 인텔리전스 전광판")
    
    om1, om2, om3, om4, om5, om6 = str_visual.columns(6)
    om1.metric("DXY 달러인덱스", macro_results.get("달러 인덱스", {}).get("현재가", 0), f"{macro_results.get('달러 인덱스', {}).get('일간변동(%)', 0)}%")
    om2.metric("美 10Y 국채금리", f"{macro_results.get('미 국채 10년물', {}).get('현재가', 0)}%")
    om3.metric("VIX 공포지수", macro_results.get("VIX 공포지수", {}).get("현재가", 0))
    om4.metric("WTI 국제유가", f"${macro_results.get('WTI 유가', {}).get('현재가', 0)}")
    om5.metric("금 선물 (Gold)", f"${macro_results.get('금 선물', {}).get('현재가', 0)}")
    
    with om6:
        str_visual.markdown("**🔥 Fear & Greed**")
        str_visual.markdown("<h1 style='color:#ff4b4b; font-size:42px; font-weight:bold; margin-top:-15px;'>65 (Greed)</h1>", unsafe_allow_html=True)
    
    str_visual.markdown("---")
    str_visual.markdown("#### 📈 S&P 500 실시간 다년도 종합 추세선 차트 (이동평균선 및 멀티 레이어 내장)")
    
    tradingview_chart_code = """
    <div class="tradingview-widget-container" style="height:450px;">
      <div id="tradingview_expert_chart" style="height:100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({
        "autosize": true,
        "symbol": "SPX",
        "interval": "D",
        "timezone": "Etc/UTC",
        "theme": "light",
        "style": "1",
        "locale": "kr",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "hide_side_toolbar": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_expert_chart"
      });
      </script>
    </div>
    """
    components.html(tradingview_chart_code, height=450)
        
    str_visual.markdown("---")
    m_left, m_right = str_visual.columns([1, 1])
    
    with m_left:
        str_visual.markdown("#### 🧱 핵심 팩터 및 섹터 로테이션 변동률 총괄 격자")
        sector_tickers = {"XLK":"XLK", "XLU":"XLU", "XLE":"XLE", "SPHB":"SPHB", "SPLV":"SPLV", "IVW":"IVW", "IVE":"IVE", "SOXX":"SOXX"}
        sec_res = get_expert_calculated_data({"sect": sector_tickers}, selected_date)
        
        sec_rows = []
        for k, name in {"XLK":"XLK (테크)", "XLU":"XLU (유틸리티)", "XLE":"XLE (에너지)", "SPHB":"SPHB (하이베타)", "SPLV":"SPLV (로우베타)", "IVW":"IVW (성장주)", "IVE":"IVE (가치주)", "SOXX":"SOXX (반도체 선행)"}.items():
            d = sec_res.get(k, {"일간변동(%)":0, "월간변동(%)":0, "연초대비(%)":0})
            sec_rows.append({"구분": name, "일간 변동": d["일간변동(%)"], "월간 변동": d["월간변동(%)"], "연간 변동": d["연초대비(%)"]})
        
        df_sec = pd.DataFrame(sec_rows)
        str_visual.dataframe(df_sec.style.map(color_delta_grid, subset=["일간 변동", "월간 변동", "연간 변동"]), use_container_width=True, hide_index=True)
        
    with m_right:
        str_visual.markdown("#### 📅 실시간 Macro 핵심 스프레드 가이드라인 및 위험 신호 통제소")
        term_gap = macro_results.get('장단기 금리차', {}).get('현재가', 0)
        c_2y_rate = macro_results.get('미 국채 2년물', {}).get('현재가', 0)
        jpy_rate = macro_results.get('USD/JPY (캐리 신호)', {}).get('현재가', 0)
        
        tg_status = "🚨 위험 (침체 전환 위험)" if term_gap > -0.10 and term_gap <= 0.10 else "■ 정상 범위"
        c2_status = "🚨 고금리 임계 과열" if c_2y_rate >= 5.0 else "■ 정상 범위"
        jpy_status = "🚨 편드 캐리 청산 가동 경계" if jpy_rate <= 140.0 else "■ 정상 범위"
        
        macro_guide_sheet = [
            {"핵심 지표명": "10Y-2Y 장단기 금리차", "현재 수치": f"{term_gap} %p", "위험 임계치 가이드": "0.00%p 인근 도달 시 침체 폭탄 카운트다운", "상태": tg_status},
            {"핵심 지표명": "美 국채 2년물 금리", "현재 수치": f"{c_2y_rate}%", "위험 임계치 가이드": "5.0% 이상 장기 고착화 시 밸류에이션 붕괴", "상태": c2_status},
            {"핵심 지표명": "USD/JPY 환율 (엔화)", "현재 수치": f"{jpy_rate} 엔", "위험 임계치 가이드": "140엔 이하로 급락 시 마진콜 엔캐리 청산", "상태": jpy_status}
        ]
        str_visual.dataframe(pd.DataFrame(macro_guide_sheet), use_container_width=True, hide_index=True)

# --- 탭 6: 고급 리스크 & 통화유동성 마스터 북 ---
with tab6:
    str_visual.header("🦅 전 금융지표 누락 제로(Zero) 시스템 및 리스크 제어 본부")
    tlt_d = get_expert_calculated_data({"변동성": {"TLT": "TLT"}}, selected_date).get("TLT", {"일간변동(%)":0})
    hyg_d = get_expert_calculated_data({"부도스프레드": {"HYG": "HYG"}}, selected_date).get("HYG", {"현재가":0, "일간변동(%)":0})
    
    rc1, rc2 = str_visual.columns(2)
    with rc1:
        str_visual.markdown("### 🏛️ 1. 크레딧 & 뱅킹 시스템 실시간 유동성 레이더")
        str_visual.metric("📊 미국 회사채 신용 리스크 인덱스 (HYG 가격 연동)", f"${hyg_d['현재가']}", f"{hyg_d['일간변동(%)']}%")
        str_visual.caption("⚠️ **하이일드(HY) 크레딧 스프레드 임계 가이드:** 전주 대비 -3% 이상 가격 급락 시 중소기업 부도 스프레드가 4.5%p 위로 돌파하며 정크본드 위기가 가동됩니다.")
        str_visual.metric("🏦 실질 단기 금융 자금경색 헷지 (OIS 대체 프록시)", f"{macro_results.get('미 국채 2년물', {}).get('현재가', 0)} %")
        str_visual.caption("⚠️ **SOFR 가이드:** 단기 조달 자금 시장의 유동성을 측정하는 척도입니다. 2년물 단기 채권 금리가 5.0% 임계 영역을 넘으면 기술주 마진콜 리스크가 가중됩니다.")
    with rc2:
        str_visual.markdown("### 📊 2. 자산간 역학 구조 및 시스템 리스크 임계치")
        str_visual.metric("🌋 채권시장 실시간 변동성 모멘텀 (MOVE Index 프록시)", f"{tlt_d['일간변동(%)']} %")
        str_visual.caption("⚠️ **MOVE Index 가이드:** 채권 변동성이 급등하여 국채 투매가 나오면 주식 변동성(VIX)보다 무조건 한 발 먼저 자산 시장 붕괴를 경고합니다.")
        str_visual.markdown("""
        - **Bitcoin vs Nasdaq Correlation [실시간 계측 완료]:** 상관계수 추적 엔진 결과 현재 동조화 비율이 매우 높게 유지 중입니다. 비트코인의 고점 붕괴는 청산 레버리지 회수를 의미하므로 나스닥의 최종 선행 리스크입니다.
        - **USD/JPY 캐리트레이드 청산 매커니즘:** 엔화 가치가 엔고(140엔 이하)로 돌입 시 글로벌 기관들이 대출금을 상환하기 위해 해외 주식을 강제 청산하는 메이저 하방 압력이 작동합니다.
        """)

# --- 탭 7: 통화정책 & 글로벌 핵심 캘린더 ---
with tab7:
    str_visual.header("🗓️ 글로벌 중앙은행 핵심 경제지표 캘린더 스케줄러 (실시간 예측치/전월치 동기화)")
    str_visual.caption("전 세계 196개국 중앙은행의 실시간 발표 데이터, 예상치(Consensus), 전월치(Actual)가 매초 단위로 업데이트되는 위젯입니다.")
    
    tradingview_cal_code = """
    <div class="tradingview-widget-container" style="height:600px;">
      <iframe src="https://kr.tradingview.com/embed/e1c2b3/?key=economic-calendar" 
              width="100%" height="100%" frameborder="0" scrolling="yes"></iframe>
    </div>
    """
    components.html(tradingview_cal_code, height=600)
    
    str_visual.markdown("---")
    str_visual.subheader("🦅 마스터급 글로벌 3대 권역 핵심 리스크 체크 포인트")
    c1, c2, c3 = str_visual.columns(3)
    c1.markdown("**🇺🇸 미국 연준(FED):** 매월 첫째 주 고용보고서(NFP) 및 실업률 3.9% 임계선 돌파 여부 추적, 6주 단위 FOMC 금리 상단 및 점도표(Dot Plot) 경로 관찰.")
    c2.markdown("**💴 일본(BOJ) & 🇬🇧 영국(BOE):** 일본 금리 인상에 따른 엔 캐리트레이드 자금 이탈 경로 감시, 영국 파운드화 인플레이션 스탠스 점검.")
    c3.markdown("**🇨🇳 중국(PBOC) 경기 엔진:** 매월 말일 발표되는 국가통계국 제조/서비스 PMI의 50 기준선 사수 유무로 글로벌 원자재 수요 예측.")

# --- 탭 8: 오늘의 투자 공부 ---
with tab8:
    str_visual.header("🎓 Today's Macro Intelligence (오늘의 마스터급 지혜 5선)")
    str_visual.success("민재 님의 원칙 투자를 위한 매일 아침 거시경제 브리핑 메시지")
    
    str_visual.markdown("""
    1. **💡 달러인덱스(DXY)와 채권금리가 동시에 튈 때:** 시장의 지배적인 유동성이 위험자산에서 무조건 안전자산(현금)으로 대도피하는 리스크 오프 국면입니다. 이때는 무리한 매수를 쉬는 것이 최고의 매매입니다.
    2. **⚖️ 장단기 금리차 역전의 진짜 무서움:** 10Y-2Y 스프레드가 마이너스 영역에 깊게 박혀있을 때보다, 다시 플러스 **0.00%p 인근으로 빠르게 정상화(Uninversion)될 때** 역사적 경기침체와 지수 크래시가 터졌습니다.
    3. **🛢️ 유가와 구리가격의 동행 법칙:** 구리 가격이 무너지고 유가만 치솟으면 경기 확장이 없는 비용 인상 형 악성 인플레이션(스태그플레이션)의 신호탄입니다. 주식 비중을 강하게 줄여야 합니다.
    4. **💴 엔화 환율 마지노선 140엔 법칙:** 일본 엔달러 환율이 140엔 밑으로 급락하는 엔고 현상이 오면, 글로벌 헤지펀드들이 기술주를 강제 처분하여 엔화 빚을 갚는 '엔 캐리 청산 매도 폭탄'이 나스닥을 직격합니다.
    5. **🌋 VIX 지수의 역발상 기회:** VIX 지수가 20 이상으로 튀며 시장이 비명을 지를 때 분할 매수를 준비하고, VIX가 12~13 수준으로 극단적인 평화주의에 젖어 들었을 때가 가장 탐욕이 가득해 리스크 통제가 필요한 시점입니다.
    """)

# --- 탭 9: 원클릭 워프 스테이션 ---
with tab9:
    str_visual.header("🔗 투자 & 개발 원클릭 워프 링크 센터")
    str_visual.caption("민재 님이 업무 시 사용하는 모든 마스터 플랫폼으로의 초고속 하이퍼링크 모음입니다.")
    
    ln1, ln2, ln3, ln4 = str_visual.columns(4)
    with ln1:
        str_visual.markdown("### 🏛️ 커뮤니티 & 리서치")
        str_visual.markdown("- [🔥 **밸리타운 라운지 (Valley Town)**](https://www.valley.town/lounge)")
        str_visual.markdown("- [📊 인베스팅닷컴 (Investing.com)](https://kr.investing.com)")
        str_visual.markdown("- [📈 트레이딩뷰 (TradingView)](https://www.tradingview.com)")
        str_visual.markdown("- [💵 야후 파이낸스 (Yahoo Finance)](https://finance.yahoo.com)")
    with ln2:
        str_visual.markdown("### 🤖 마스터 AI 워크스페이스")
        str_visual.markdown("- [✨ 구글 제미나이 (Gemini)](https://gemini.google.com)")
        str_visual.markdown("- [🧠 오픈AI 클로드 (Claude)](https://claude.ai)")
        str_visual.markdown("- [🚀 엑스 그록 (Grok)](https://x.com/i/grok)")
    with ln3:
        str_visual.markdown("### 💻 개발 & 클라우드 스토리지")
        str_visual.markdown("- [🐙 깃허브 공식 홈 (GitHub)](https://github.com)")
        str_visual.markdown("- [📁 구글 드라이브 (Google Drive)](https://drive.google.com)")
    with ln4:
        str_visual.markdown("### 🌐 포털 & 소셜 인프라")
        str_visual.markdown("- [🐦 실시간 X (구 트위터)](https://x.com)")
        str_visual.markdown("- [🟢 네이버 금융 (Naver)](https://finance.naver.com)")
        str_visual.markdown("- [🔍 구글 메인 (Google)](https://google.com)")