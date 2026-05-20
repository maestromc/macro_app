import yfinance as yf
import pandas as pd
import streamlit as str_visual
from datetime import datetime, timedelta

# 1. 웹 브라우저 창 전체 설정
str_visual.set_page_config(page_title="글로벌 매크로 주식 레이더 V2", layout="wide")

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
            [
                "✨ SNS 콘텐츠 생성기 (X/블로그)",
                "🚀 핵심 성장주 딥다이브 리서치",
                "📊 매크로 지표 분석 및 브리핑",
                "🎯 개인 브랜딩 / 캘린더 관리"
            ]
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
str_visual.title("📊 글로벌 매크로 & 주식 마스터 대시보드")

main_top_left, main_top_right = str_visual.columns([3, 1])
with main_top_left:
    str_visual.markdown("매일 아침 확인하는 나만의 투자 나침반")
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
    "바이오/헬스": {"삼성바이오로직스": "207940.KS", "셀트리온": "068270.KS", "알테오জেন": "196170.KQ", "HLB": "028300.KQ", "유한양행": "000100.KS", "SK바이오팜": "326030.KS"},
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

with str_visual.spinner("선택하신 기준일의 매크로 및 귀금속 보정 데이터를 불러오는 중..."):
    macro_results = get_expert_calculated_data(Daily_Macro, selected_date)
    us_results = get_expert_calculated_data(US_Stocks, selected_date)
    kr_results = get_expert_calculated_data(Korea_Stocks, selected_date)
    
    if macro_results.get("미 국채 10년물 금리", {}).get("현재가", 0) > 0 or macro_results.get("미 국채 10년물", {}).get("현재가", 0) > 0:
        c_10y = macro_results.get("미 국채 10년물", {}).get("현재가", 0) if macro_results.get("미 국채 10년물", {}).get("현재가", 0) > 0 else macro_results.get("미 국채 10년물 금리", {}).get("현재가", 0)
        c_2y = macro_results.get("미 국채 2년물", {}).get("현재가", 0)
        diff_val = c_10y - c_2y
        macro_results["장단기 금리차"] = {"현재가": round(diff_val, 2), "일간변동(%)": 0.0, "주간변동(%)": 0.0, "월간변동(%)": 0.0, "조회일자": selected_date.strftime('%Y-%m-%d')}

def color_delta_grid(val):
    if isinstance(val, (int, float)):
        color = 'green' if val > 0 else 'red' if val < 0 else 'black'
        return f'color: {color}; font-weight: bold;'
    return ''

# 🗂️ 7대 마스터 탭 구조 선언
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = str_visual.tabs([
    "🌐 거시경제(일단위)", "🇺🇸 미국 주식 레이더 (50선)", "🇰🇷 한국 주식 레이더 (50선)", 
    "📅 월단위 매크로 지표", "📺 올인원 마스터 뷰", "🦅 고급 리스크 & 유동성 분석", "🗓️ 통화정책 & 글로벌 캘린더"
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
    str_visual.subheader("📦 거시경제 인덱스 시계열 통합 스코어 보드")
    macro_table = []
    for name, d in macro_results.items():
        if name == "장단기 금리차": continue
        macro_table.append({
            "자산명": name, "기준일 주가": d["현재가"], "전일 종가": d["전일종가"], 
            "일간 변동(%)": d["일간변동(%)"], "주간 변동(%)": d["주간변동(%)"], "월간 변동(%)": d["월간변동(%)"]
        })
    df_macro = pd.DataFrame(macro_table)
    str_visual.dataframe(df_macro.style.map(color_delta_grid, subset=["일간 변동(%)", "주간 변동(%)", "월간 변동(%)"]), use_container_width=True, hide_index=True)

# --- 탭 2: 미국 주식 레이더 ---
with tab2:
    str_visual.header("💻 미국 핵심 주식 레이더 (시총 최상위 50선)")
    us_master_rows = []
    for name, d in us_results.items():
        us_master_rows.append({
            "섹터분류": d["분류"], "종목명": name, "현재조회일": d["조회일자"], "현재가($)": d["현재가"], "전일종가($)": d["전일종가"], "일간비(%)": d["일간변동(%)"],
            "주간변동": f"{d['주간변동']}$ (당시:{d['주간과거가']}$ / {d['주간날짜']})", "주간(%)": d["주간변동(%)"],
            "월간변동": f"{d['월간변동']}$ (당시:{d['월간과거가']}$ / {d['월간날짜']})", "월간(%)": d["월간변동(%)"],
            "연초대비": f"{d['연초변동']}$ (당시:{d['연초과거가']}$ / {d['연초날짜']})", "연초비(%)": d["연초대비(%)"],
            "전고점대비(%)": d["전고점대비(%)"]
        })
    df_us = pd.DataFrame(us_master_rows)
    str_visual.markdown("""<style> div[data-testid="stDataFrame"] td { font-size: 18px !important; text-align: center !important; } </style>""", unsafe_allow_html=True)
    str_visual.dataframe(df_us.style.map(color_delta_grid, subset=["일간비(%)", "주간(%)", "월간(%)", "연초비(%)", "전고점대비(%)"]), use_container_width=True, hide_index=True)
    
    str_visual.markdown("---")
    str_visual.subheader("🔥 Wall Street 실시간 최고 화제주 블리츠")
    uc1, uc2, uc3, uc4, uc5 = str_visual.columns(5)
    uc1.markdown("[🚀 테슬라 (TSLA) 실시간 동향](https://finance.yahoo.com/quote/TSLA)")
    uc2.markdown("[👑 엔비디아 (NVDA) 인프라 현황](https://finance.yahoo.com/quote/NVDA)")
    uc3.markdown("[🍏 애플 (AAPL) AI 탑재 스펙](https://finance.yahoo.com/quote/AAPL)")
    uc4.markdown("[☁️ 마이크로소프트 (MSFT) 클라우드](https://finance.yahoo.com/quote/MSFT)")
    uc5.markdown("[🛰️ AST 스페이스모바일 (ASTS) 공급망](https://finance.yahoo.com/quote/ASTS)")

# --- 탭 3: 한국 주식 레이더 ---
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
    str_visual.subheader("🔥 국장 핵심 테마 및 컨센서스 집중 포커스 종목")
    kc1, kc2, kc3, kc4, kc5 = str_visual.columns(5)
    kc1.markdown("[⚡ 삼성전자 (005930) 수급 확인](https://finance.naver.com/item/main.naver?code=005930)")
    kc2.markdown("[🔥 SK하이닉스 (000660) HBM 실황](https://finance.naver.com/item/main.naver?code=000660)")
    kc3.markdown("[🧪 알테오젠 (196170) 바이오 시세](https://finance.naver.com/item/main.naver?code=196170)")
    kc4.markdown("[🚘 현대차 (005380) 밸류업 수혜](https://finance.naver.com/item/main.naver?code=005380)")
    kc5.markdown("[🚀 한화에어로스페이스 (012450) 방산](https://finance.naver.com/item/main.naver?code=012450)")

# --- 탭 4: 월단위 매크로 지표 대포 확장 ---
with tab4:
    str_visual.header("📅 월간 핵심 매크로 발표 및 컨센서스 모니터링 가이드")
    tab4_col1, tab4_col2, tab4_col3 = str_visual.columns(3)
    
    with tab4_col1:
        str_visual.markdown("### 🛒 1. Inflation Group (물가 지표)")
        inf_data = [
            {"지표명": "소비자물가지수 (Headline CPI)", "중요도": "⭐⭐⭐", "컨센서스 트렌드": "전년비 3.4% 기대"},
            {"지표명": "근원 소비자물가지수 (Core CPI)", "중요도": "⭐⭐⭐", "컨센서스 트렌드": "식료품/에너지 제외 흐름 추적"},
            {"지표명": "개인소비지출 (Headline PCE)", "중요도": "⭐⭐⭐", "컨센서스 트렌드": "연준 최종 목표 상단 2.0% 수렴 여부"},
            {"지표명": "근원 개인소비지출 (Core PCE)", "중요도": "⭐⭐⭐", "컨센서스 트렌드": "연준이 통화정책 시 가장 신뢰함"},
            {"지표명": "생산자물가지수 (PPI)", "중요도": "⭐⭐ 보통", "컨센서스 트렌드": "소비자물가의 대표 선행 팩터"}
        ]
        str_visual.table(pd.DataFrame(inf_data))
        
    with tab4_col2:
        str_visual.markdown("### 🛠️ 2. Labor Market Group (고용/노동 지표)")
        labor_data = [
            {"지표명": "미국 실업률 (Unemployment Rate)", "중요도": "⭐⭐⭐", "컨센서스 트렌드": "자연실업률 3.9% 수준 유지 여부"},
            {"지표명": "비농업 고용자 수 (Nonfarm Payrolls)", "중요도": "⭐⭐⭐", "컨센서스 트렌드": "월간 200K~250K가 골디락스 마지노선"},
            {"지표명": "신규 실업수당 청구건수 (Initial Claims)", "중요도": "⭐⭐ 보통", "컨센서스 트렌드": "주간 단위 노동 경색 실시간 체크용"},
            {"지표명": "평균 시간당 임금 (Average Hourly Earnings)", "중요도": "⭐⭐⭐", "컨센서스 트렌드": "임금발 2차 인플레 고착화 유무 판단"},
            {"지표명": "ADP 민간고용 / JOLTS 구인보고서", "중요도": "⭐⭐ 보통", "컨센서스 트렌드": "NFP 발표 전 노동시장 선행 탐색 가이드"}
        ]
        str_visual.table(pd.DataFrame(labor_data))
        
    with tab4_col3:
        str_visual.markdown("### 📈 3. Growth & Activity (성장/경기 지표)")
        growth_data = [
            {"지표명": "ISM 제조업 PMI", "중요도": "⭐⭐⭐", "컨센서스 트렌드": "50 기준선 상회 시 제조업 경기 확장"},
            {"지표명": "ISM 서비스업 PMI", "중요도": "⭐⭐⭐", "컨센서스 트렌드": "미국 경제의 70%인 서비스업 활력 잣대"},
            {"지표명": "소매 판매 (Retail Sales)", "중요도": "⭐⭐⭐", "컨센서스 트렌드": "미국 소비 체력 및 연착륙 강도 증명"},
            {"지표명": "산업 생산 (Industrial Production)", "중요도": "⭐⭐ 보통", "컨센서스 트렌드": "실물 제조업 하드 데이터 리포트"},
            {"지표명": "콘퍼런스보드 경기선행지수 (LEI)", "중요도": "⭐⭐ 보통", "컨센서스 트렌드": "향후 6개월 내 경기 전환점 선행 예측"}
        ]
        str_visual.table(pd.DataFrame(growth_data))

    str_visual.markdown("---")
    str_visual.subheader("🦅 다음 FOMC 기준금리 인상/동결 전망 (CME FedWatch 기준)")
    fomc_col1, fomc_col2 = str_visual.columns(2)
    fomc_col1.metric(label="🔒 금리 동결 (또는 인하) 확률", value="84.5%", delta="전주 대비 +2.1%")
    fomc_col2.metric(label="🚨 금리 인상 확률", value="15.5%", delta="전주 대비 -2.1%")

# --- 탭 5: 올인원 마스터 뷰 ---
with tab5:
    str_visual.subheader("📺 ALL-IN-ONE 글로벌 매크로 인텔리전스 전광판")
    
    om1, om2, om3, om4, om5, om6 = str_visual.columns(6)
    om1.metric("DXY 달러인덱스", macro_results.get("달러 인덱", {}).get("현재가", 0))
    om2.metric("美 10Y 국채금리", f"{macro_results.get('미 국채 10년물', {}).get('현재가', 0)}%")
    om3.metric("VIX 공포지수", macro_results.get("VIX 공포지수", {}).get("현재가", 0))
    om4.metric("WTI 국제유가", f"${macro_results.get('WTI 유가', {}).get('현재가', 0)}")
    om5.metric("금 선물 (Gold)", f"${macro_results.get('금 선물', {}).get('현재가', 0)}")
    
    with om6:
        str_visual.markdown("**🔥 Fear & Greed**")
        str_visual.markdown("<h2 style='color:#ff4b4b; font-size:32px; margin-top:-10px;'>65 (Greed)</h2>", unsafe_allow_html=True)
    
    str_visual.markdown("---")
    
    str_visual.markdown("#### 📈 S&P 500 실시간 시계열 추세 모니터링 차트")
    try:
        spy_obj = yf.Ticker("^GSPC")
        spy_df = spy_obj.history(start=(selected_date - timedelta(days=90)).strftime('%Y-%m-%d'), end=(selected_date + timedelta(days=1)).strftime('%Y-%m-%d'))
        if not spy_df.empty:
            str_visual.line_chart(spy_df['Close'], use_container_width=True)
    except:
        str_visual.info("차트 데이터를 수집하는 중입니다.")
        
    str_visual.markdown("---")
    
    m_left, m_right = str_visual.columns([1, 1])
    
    with m_left:
        str_visual.markdown("#### 🧱 주요 섹터 흐름 및 팩터 상대강도 상세 (일간/월간/연간)")
        sector_tickers = {"XLK":"XLK", "XLU":"XLU", "XLE":"XLE", "SPHB":"SPHB", "SPLV":"SPLV", "IVW":"IVW", "IVE":"IVE", "SOXX":"SOXX"}
        sec_res = get_expert_calculated_data({"섹터": sector_tickers}, selected_date)
        
        sec_rows = []
        for k, name in {"XLK":"XLK (테크)", "XLU":"XLU (유틸리티)", "XLE":"XLE (에너지)", "SPHB":"SPHB (하이베타)", "SPLV":"SPLV (로우베타)", "IVW":"IVW (성장주)", "IVE":"IVE (가치주)", "SOXX":"SOXX (반도체 선행)"}.items():
            d = sec_res.get(k, {"일간변동(%)":0, "월간변동(%)":0, "연초대비(%)":0})
            # 🎯 [KeyError 해결 핵심] 칼럼 이름을 아래 subset에 들어갈 명칭과 정확히 1:1 동기화시킴
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
        jpy_status = "🚨 캐리 청산 폭탄 가동" if jpy_rate <= 140.0 else "■ 정상 범위"
        
        macro_guide_sheet = [
            {"핵심 지표명": "10Y-2Y 장단기 금리차", "현재 수치": f"{term_gap} %p", "위험 경계선 (임계치)": "0.00%p 인근 정상화 도래 시", "현재 상태": tg_status},
            {"핵심 지표명": "美 국채 2년물 금리", "현재 수치": f"{c_2y_rate}%", "위험 경계선 (임계치)": "5.0% 이상 고착화 시 밸류 크래시", "현재 상태": c2_status},
            {"핵심 지표명": "USD/JPY 환율 (엔화)", "현재 수치": f"{jpy_rate} 엔", "위험 경계선 (임계치)": "140엔 이하로 급락 시 마진콜 유발", "현재 상태": jpy_status}
        ]
        str_visual.dataframe(pd.DataFrame(macro_guide_sheet), use_container_width=True, hide_index=True)

# --- 탭 6: 고급 리스크 & 통화유동성 마스터 북 ---
with tab6:
    str_visual.header("🦅 미누락 리스크 & Liquidity 고급 통제 대시보드")
    
    tlt_d = get_expert_calculated_data({"변동성": {"TLT": "TLT"}}, selected_date).get("TLT", {"일간변동(%)":0})
    hyg_d = get_expert_calculated_data({"부도스프레드": {"HYG": "HYG"}}, selected_date).get("HYG", {"현재가":0, "일간변동(%)":0})
    
    rc_1, rc_2 = str_visual.columns(2)
    with rc_1:
        str_visual.markdown("### 🏛️ 통화 유동성 및 은행권 신용 지표 가이드")
        str_visual.markdown("""
        - **TED Spread (은행간 신뢰도):** 3개월 만기 미 국채 금리와 LIBOR 금리 차이. **[임계치: 0.5%p 이상 시 금융위기 신호]**
        - **LIBOR-OIS Spread:** 실질 단기 금융시장의 신용 리스크 리트머스 시험지. 0에 수렴해야 유동성 안전구역.
        - **HY Spread (하이일드 스프레드 프록시):** 현재 고위험 회사채 ETF(HYG) 가격은 `${현재가}` ({일간변동(%)}%). **[임계치: HYG 전주비 3% 이상 폭락 시 한계기업 연쇄 도산 신호]**
        """.replace("${현재가}", str(hyg_d['현재가'])).replace("{일간변동(%)", str(hyg_d['일간변동(%)'])))
        
    with rc_2:
        str_visual.markdown("### 📊 자금 로테이션 및 투기 세력 동조화 레이더")
        str_visual.markdown(f"""
        - **Bitcoin vs Nasdaq Correlation:** 두 자산의 자금 동조성 강도를 파악하여 현재 자금 유입이 '진짜 성장'인지 '단순 투기(Proxy)'인지 진단.
        - **USD/JPY 매커니즘:** 엔달러 환율이 주간 단위로 급락하면 전 세계 헤지펀드들이 빌렸던 엔화를 갚기 위해 나스닥 기술주를 강제로 내다 파는 역발상 마진콜 발동.
        - **MOVE Index 프록시:** 채권 시장 변동성 측정 장치. 현재 TLT 채권 가격 일간 변동 강도는 `{tlt_d['일간변동(%)']}%` 연동 중.
        """)

# --- 탭 7: 통화정책 & 글로벌 핵심 캘린더 ---
with tab7:
    str_visual.header("🗓️ 글로벌 중앙은행 핵심 경제지표 캘린더 스케줄러")
    str_visual.caption("매달 정기적으로 돌아오는 글로벌 마켓 무빙 매커니즘 일정표입니다.")
    
    cal_col1, cal_col2, cal_col3 = str_visual.columns(3)
    
    with cal_col1:
        str_visual.markdown("### 🇺🇸 미국 & 글로벌 메인 스트리트")
        str_visual.table(pd.DataFrame([
            {"일정/날짜": "매월 첫째 주 금요일", "이벤트 및 지표": "미국 비농업 고용보고서 (NFP)", "장인급 리스크 체크 포인트": "실업률 발 스태그플레이션 추적"},
            {"일정/날짜": "매월 10일~14일 사이", "이벤트 및 지표": "미국 소비자물가지수 (CPI)", "장인급 리스크 체크 포인트": "Headline 대 Core 이격 심화 여부"},
            {"일정/날짜": "6주 간격 수요일", "이벤트 및 지표": "연준 FOMC 금리결정 및 기자회견", "장인급 리스크 체크 포인트": "파월 의장의 SOFR 및 QT 속도 발언 본질 파악"}
        ]))
        
    with cal_col2:
        str_visual.markdown("### 💴 일본(BOJ) 캐리 / 🇬🇧 영국(BOE) 캘린더")
        str_visual.table(pd.DataFrame([
            {"일정/날짜": "매월 중하순 (가변)", "이벤트 및 지표": "일본 BOJ 통화정책회의 금리 결정", "장인급 리스크 체크 포인트": "금리 인상 단행 시 USD/JPY 엔화 캐리 청산 방화벽 붕괴 위험"},
            {"일정/날짜": "분기별 중순", "이벤트 및 지표": "영국 BOE 통화정책 자금 리포트", "장인급 리스크 체크 포인트": "유럽 권역 유동성 긴축 강도와 파운드화 연동 분석"},
            {"일정/날짜": "매주 목요일 16:30", "이벤트 및 지표": "연준 대차대조표 (Fed Balance Sheet)", "장인급 리스크 체크 포인트": "연준이 몰래 유동성을 회수하거나 공급하는지 실시간 추적"}
        ]))
        
    with cal_col3:
        str_visual.markdown("### 🇨🇳 중국(PBOC) 핵심 성장 매커니즘")
        str_visual.table(pd.DataFrame([
            {"일정/날짜": "매월 말일 (30/31일)", "이벤트 및 지표": "중국 국가통계국 제조업 PMI", "장인급 리스크 체크 포인트": "50 하회 시 국장 화학, 철강, 반도체 선행 타격"},
            {"일정/날짜": "매월 15일 전후", "이벤트 및 지표": "중국 중기유동성지원창구(MLF) 금리", "장인급 리스크 체크 포인트": "PBOC의 유동성 방출 여부 및 위안화 프록시 체크"},
            {"일정/날짜": "매분기 익월 15일", "이벤트 및 지표": "중국 분기별 GDP 성장률 발표", "장인급 리스크 체크 포인트": "글로벌 원자재(구리, 유가)의 실질 수요 엔진 작동 여부 증명"}
        ]))