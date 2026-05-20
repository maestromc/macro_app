import yfinance as yf
import pandas as pd
import streamlit as str_visual
import streamlit.components.v1 as components
from datetime import datetime, timedelta


# 1. 웹 브라우저 창 전체 설정 (블룸버그 터미널급 와이드 레이아웃)
str_visual.set_page_config(page_title="글로벌 매크로 주식 레이더 V4", layout="wide")


# 2. 시스템 보안 패스워드 로드
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
        user_command = str_visual.text_area("무엇을 도와드릴까요?", placeholder="요청사항을 입력하세요.")
       
        if str_visual.button("⚡ Rooney 작동하기"):
            if user_command and "GEMINI_API_KEY" in str_visual.secrets:
                from google import genai
                client = genai.Client(api_key=str_visual.secrets["GEMINI_API_KEY"])
                with str_visual.spinner("Rooney가 분석 중입니다..."):
                    try:
                        system_instruction = "당신의 이름은 'Rooney'입니다. 투자 운영과 SNS 성장을 돕는 전문 AI 에이전트입니다."
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=f"모드: {project_mode}\n지시: {user_command}",
                            config={"system_instruction": system_instruction}
                        )
                        str_visual.success("🤖 Rooney의 인사이트 도출 완료!")
                        str_visual.markdown(response.text)
                    except Exception as e:
                        str_visual.error(f"API 호출 중 문제가 발생했습니다: {e}")
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
    "금융/소비재": {"JP모건": "JPM", "버크셔 해서웨이": "BRK-B", "뱅크오브아메리카": "BAC", "웰스파고": "WFC", "골드만삭스": "GS", "모건스탠리": "MS", "월마트": "WMT", "코스트코": "COST", "홈디포": "HD", "프록터앤갬블": "PG", "코카콜라": "KO", "펩시코": "PEP", "맥도날드": "MCD"},
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
                    mdd_pct = round(float((c_close - high_peak) / high_peak) * 100, 2)
                   
                    results[name] = {
                        "분류": cat, "조회일자": current_date_str,
                        "현재가": round(float(c_close), 2), "전일종가": round(float(p_close), 2),
                        "일간금액": round(float(c_close - p_close), 2),
                        "일간변동(%)": round(float(((c_close - p_close) / p_close) * 100), 2),
                        "주간변동": round(float(c_close - w_close), 2), "주간변동(%)": round(float(((c_close - w_close) / w_close) * 100), 2), "주간날짜": w_date, "주간과거가": round(float(w_close), 2),
                        "월간변동": round(float(c_close - m_close), 2), "월간변동(%)": round(float(((c_close - m_close) / m_close) * 100), 2), "월간날짜": m_date, "월간과거가": round(float(m_close), 2),
                        "연초변동": round(float(c_close - y_close), 2), "연초대비(%)": round(float(((c_close - y_close) / y_close) * 100), 2), "연초날짜": y_date, "연초과거가": round(float(y_close), 2),
                        "전고점대비(%)": mdd_pct
                    }
                else:
                    results[name] = {"분류": cat, "조회일자": "-", "현재가": 0.0, "전일종가": 0.0, "일간금액": 0.0, "일간변동(%)": 0.0, "주간변동": 0.0, "주간변동(%)": 0.0, "주간날짜": "-", "주간과거가": 0.0, "월간변동": 0.0, "월간변동(%)": 0.0, "월간날짜": "-", "월간과거가": 0.0, "연초변동": 0.0, "연초대비(%)": 0.0, "연초날짜": "-", "연초과거가": 0.0, "전고점대비(%)": 0.0}
            except:
                results[name] = {"분류": cat, "조회일자": "-", "현재가": 0.0, "전일종가": 0.0, "일간금액": 0.0, "일간변동(%)": 0.0, "주간변동": 0.0, "주간변동(%)": 0.0, "주간날짜": "-", "주간과거가": 0.0, "월간변동": 0.0, "월간변동(%)": 0.0, "월간날짜": "-", "월간과거가": 0.0, "연초변동": 0.0, "연초대비(%)": 0.0, "연초날짜": "-", "연초과거가": 0.0, "전고점대비(%)": 0.0}
    return results


with str_visual.spinner("선택하신 기준일의 매크로 및 주가 데이터를 보정하는 중..."):
    macro_results = get_expert_calculated_data(Daily_Macro, selected_date)
    us_results = get_expert_calculated_data(US_Stocks, selected_date)
    kr_results = get_expert_calculated_data(Korea_Stocks, selected_date)
   
    for asset_name, ticker in [("달러 인덱스", "DX-Y.NYB"), ("금 선물", "GC=F"), ("SK하이닉스", "000660.KS")]:
        if macro_results.get(asset_name, {}).get("현재가", 0) == 0 and asset_name in macro_results:
            bk_df = yf.Ticker(ticker).history(period="7d").ffill()
            if not bk_df.empty:
                macro_results[asset_name]["현재가"] = round(float(bk_df['Close'].iloc[-1]), 2)
                # 수정된 부분: 괄호 위치가 올바르게 수정되었습니다.
                macro_results[asset_name]["전일종가"] = round(float(bk_df['Close'].iloc[-2]), 2)
                macro_results[asset_name]["일간금액"] = round(float(bk_df['Close'].iloc[-1] - bk_df['Close'].iloc[-2]), 2)
                macro_results[asset_name]["일간변동(%)"] = round(float(((bk_df['Close'].iloc[-1] - bk_df['Close'].iloc[-2])/bk_df['Close'].iloc[-2])*100), 2)


    c_10y = macro_results.get("미 국채 10년물", {}).get("현재가", 0)
    c_2y = macro_results.get("미 국채 2년물", {}).get("현재가", 0)
    diff_val = round(float(c_10y - c_2y), 2)
    macro_results["장단기 금리차"] = {"현재가": diff_val, "일간변동(%)": 0.0, "주간변동(%)": 0.0, "월간변동(%)": 0.0, "전고점대비(%)": 0.0, "조회일자": selected_date.strftime('%Y-%m-%d')}


def color_delta_grid(val):
    if isinstance(val, (int, float)):
        color = 'green' if val > 0 else 'red' if val < 0 else 'black'
        return f'color: {color}; font-weight: bold;'
    return ''


# 🗂️ 10대 마스터 정밀 탭 구성
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = str_visual.tabs([
    "🌐 거시경제(일단위)", "🇺🇸 미국 주식 레이더 (50선)", "🇰🇷 한국 주식 레이더 (50선)",
    "📅 월단위 매크로 지표", "📺 올인원 마스터 뷰", "🦅 고급 리스크 & 유동성 분석",
    "🗓️ 글로벌 통화정책 캘린더", "🎓 오늘의 투자 공부", "📚 투자 학습 일지", "🔗 원클릭 워프 스테이션"
])


# --- 탭 1: 거시경제 일단위 지표 ---
with tab1:
    str_visual.subheader("🎯 글로벌 거시경제 테마별 전광판")
    g1, g2, g3, g4 = str_visual.columns(4)
    with g1:
        str_visual.markdown("### 🏦 통화 & 미국채 금리")
        str_visual.metric("원/달러 환율", f"{macro_results.get('원달러 환율', {}).get('현재가', 0):.2f} 원", f"{macro_results.get('원달러 환율', {}).get('일간변동(%)', 0):.2f}%")
        str_visual.metric("美 국채 10Y 금리", f"{macro_results.get('미 국채 10년물', {}).get('현재가', 0):.2f}%", f"{macro_results.get('미 국채 10년물', {}).get('일간변동(%)', 0):.2f}%")
        str_visual.metric("美 국채 2Y 금리", f"{macro_results.get('미 국채 2년물', {}).get('현재가', 0):.2f}%", f"{macro_results.get('미 국채 2년물', {}).get('일간변동(%)', 0):.2f}%")
        str_visual.metric("장단기 금리차 (10Y-2Y)", f"{macro_results.get('장단기 금리차', {}).get('현재가', 0):.2f} %p")
    with g2:
        str_visual.markdown("### 💵 달러 & 주가지수")
        str_visual.metric("달러 인덱스 (DXY)", f"{macro_results.get('달러 인덱스', {}).get('현재가', 0):.2f}", f"{macro_results.get('달러 인덱스', {}).get('일간변동(%)', 0):.2f}%")
        str_visual.metric("나스닥 종합지수", f"{macro_results.get('나스닥 지수', {}).get('현재가', 0):.2f}", f"{macro_results.get('나스닥 지수', {}).get('일간변동(%)', 0):.2f}%")
        str_visual.metric("S&P 500 지수", f"{macro_results.get('S&P 500', {}).get('현재가', 0):.2f}", f"{macro_results.get('S&P 500', {}).get('일간변동(%)', 0):.2f}%")
        str_visual.metric("다우존스 산업지수", f"{macro_results.get('다우존스', {}).get('현재가', 0):.2f}", f"{macro_results.get('다우존스', {}).get('일간변동(%)', 0):.2f}%")
    with g3:
        str_visual.markdown("### 🌋 변동성 / 에너지 / 귀금속")
        str_visual.metric("VIX 공포지수", f"{macro_results.get('VIX 공포지수', {}).get('현재가', 0):.2f}", f"{macro_results.get('VIX 공포지수', {}).get('일간변동(%)', 0):.2f}%")
        str_visual.metric("금 선물 가격 (Gold)", f"${macro_results.get('금 선물', {}).get('현재가', 0):.2f}", f"{macro_results.get('금 선물', {}).get('일간변동(%)', 0):.2f}%")
        str_visual.metric("銀 선물 가격 (Silver)", f"${macro_results.get('은 선물 가격', {}).get('현재가', 0):.2f}", f"{macro_results.get('은 선물 가격', {}).get('일간변동(%)', 0):.2f}%")
        str_visual.metric("WTI 국제유가 선물", f"${macro_results.get('WTI 유가', {}).get('현재가', 0):.2f}", f"{macro_results.get('WTI 유가', {}).get('일간변동(%)', 0):.2f}%")
    with g4:
        str_visual.markdown("### 🪙 디지털자산 & 원자재")
        str_visual.metric("비트코인 (BTC-USD)", f"${macro_results.get('비트코인 (BTC)', {}).get('현재가', 0):,.2f}", f"{macro_results.get('비트코인 (BTC)', {}).get('일간변동(%)', 0):.2f}%")
        str_visual.metric("이더리움 (ETH-USD)", f"${macro_results.get('이더리움 (ETH)', {}).get('현재가', 0):,.2f}", f"{macro_results.get('이더리움 (ETH)', {}).get('일간변동(%)', 0):.2f}%")
        str_visual.metric("구리 선물 가격", f"${macro_results.get('구리 선물 가격', {}).get('현재가', 0):.2f}", f"{macro_results.get('구리 선물 가격', {}).get('일간변동(%)', 0):.2f}%")
        str_visual.metric("대두(콩) 선물 가격", f"${macro_results.get('대두 선물 가격', {}).get('현재가', 0):.2f}", f"{macro_results.get('대두 선물 가격', {}).get('일간변동(%)', 0):.2f}%")


    str_visual.markdown("---")
    str_visual.subheader("📦 거시경제 인덱스 시계열 통합 스코어 보드")
    macro_table = []
    for name, d in macro_results.items():
        macro_table.append({
            "자산명": name, "기준일 주가": round(d.get("현재가", 0), 2), "전고점대비(%)": round(d.get("전고점대비(%)", 0), 2),
            "일간 변동(금액)": round(d.get("일간금액", 0), 2), "일간 변동(%)": round(d.get("일간변동(%)", 0), 2),
            "주간 변동(%)": round(d.get("주간변동(%)", 0), 2), "월간 변동(%)": round(d.get("월간변동(%)", 0), 2), "마지막 기준날짜": d.get("조회일자", "-")
        })
    df_macro = pd.DataFrame(macro_table)
    str_visual.dataframe(df_macro.style.map(color_delta_grid, subset=["일간 변동(금액)", "일간 변동(%)", "주간 변동(%)", "월간 변동(%)", "전고점대비(%)"]), use_container_width=True, hide_index=True)


# --- 탭 2: 미국 주식 레이더 ---
with tab2:
    str_visual.header("💻 미국 핵심 주식 레이더 (시총 최상위 50선)")
    us_master_rows = []
    for name, d in us_results.items():
        us_master_rows.append({
            "전고점대비(%)": round(d["전고점대비(%)"], 2), "현재조회일": d["조회일자"], "섹터분류": d["분류"], "종목명": name, "현재가($)": round(d.get("현재가", 0), 2), "전일종가($)": round(d["전일종가"], 2), "일간비(%)": round(d["일간변동(%)"], 2),
            "주간변동": f"{d['주간변동']:.2f}$ (당시:{d['주간과거가']:.2f}$ / {d['주간날짜']})", "주간(%)": round(d["주간변동(%)"], 2),
            "월간변동": f"{d['월간변동']:.2f}$ (당시:{d['월간과거가']:.2f}$ / {d['월간날짜']})", "월간(%)": round(d["월간변동(%)"], 2),
            "연초대비": f"{d['연초변동']:.2f}$ (당시:{d['연초과거가']:.2f}$ / {d['연초날짜']})", "연초비(%)": round(d["연초대비(%)"], 2)
        })
    df_us = pd.DataFrame(us_master_rows)
    str_visual.markdown("""<style> div[data-testid="stDataFrame"] td { font-size: 20px !important; text-align: center !important; } </style>""", unsafe_allow_html=True)
    str_visual.dataframe(df_us.style.map(color_delta_grid, subset=["일간비(%)", "주간(%)", "월간(%)", "연초비(%)", "전고점대비(%)"]), use_container_width=True, hide_index=True)
   
    str_visual.markdown("---")
    str_visual.subheader("🔥 Wall Street 실시간 최고 화제주 블리츠 & 집중 리서치")
    uc1, uc2, uc3, uc4, uc5 = str_visual.columns(5)
    with uc1:
        str_visual.markdown("#### [🚀 테슬라 (TSLA)](https://finance.yahoo.com/quote/TSLA)")
        str_visual.info("FSD 자율주행 글로벌 라이선싱 규제 해제 기대감 및 신형 저가 라인업 생산 가속 모멘텀 수혜.")
    with uc2:
        str_visual.markdown("#### [👑 엔비디아 (NVDA)](https://finance.yahoo.com/quote/NVDA)")
        str_visual.info("차세대 AI 칩 설계 아키텍처 양산 및 글로벌 빅테크 데이터센터 자본지출 증설 가중 지속.")
    with uc3:
        str_visual.markdown("#### [🍏 애플 (AAPL)](https://finance.yahoo.com/quote/AAPL)")
        str_visual.info("온디바이스 AI 탑재 모델의 본격적 하드웨어 교체 주기 단축 신호 및 마진율 방어력 확보.")
    with uc4:
        str_visual.markdown("#### [☁️ 마이크로소프트 (MSFT)](https://finance.yahoo.com/quote/MSFT)")
        str_visual.info("애저 클라우드 기반 생성형 AI B2B 상용 솔루션의 높은 유료 구독 전환 강도 입증 지속.")
    with uc5:
        str_visual.markdown("#### [🛰️ AST 스페이스모바일 (ASTS)](https://finance.yahoo.com/quote/ASTS)")
        str_visual.info("글로벌 이동통신 협의체 주도 저궤도 위성 통신 다이렉트 투 셀 인프라 선점 랠리 가동.")


# --- 탭 3: 한국 주식 레이더 ---
with tab3:
    str_visual.header("🇰🇷 국내 시장 코스피/코스닥 대장주 (50선)")
    kr_master_rows = []
    for name, d in kr_results.items():
        kr_master_rows.append({
            "전고점대비(%)": round(d["전고점대비(%)"], 2), "현재조회일": d["조회일자"], "테마분류": d["분류"], "종목명": name, "현재가(원)": f"{int(d['현재가']):,}", "전일종가(원)": f"{int(d['전일종가']):,}", "일간비(%)": round(d["일간변동(%)"], 2),
            "주간변동": f"{int(d['주간변동']):,}원 (당시:{int(d['주간과거가']):,}원 / {d['주간날짜']})", "주간(%)": round(d["주간변동(%)"], 2),
            "월간변동": f"{int(d['월간변동']):,}원 (당시:{int(d['월간과거가']):,}원 / {d['월간날짜']})", "월간(%)": round(d["월간변동(%)"], 2),
            "연초대비": f"{int(d['연초변동']):,}원 (당시:{int(d['연초과거가']):,}원 / {d['연초날짜']})", "연초비(%)": round(d["연초대비(%)"], 2)
        })
    df_kr = pd.DataFrame(kr_master_rows)
    str_visual.dataframe(df_kr.style.map(color_delta_grid, subset=["일간비(%)", "주간(%)", "월간(%)", "연초비(%)", "전고점대비(%)"]), use_container_width=True, hide_index=True)
   
    str_visual.markdown("---")
    str_visual.subheader("🔥 국장 핵심 테마 및 컨센서스 집중 포커스 종목")
    kc1, kc2, kc3, kc4, kc5 = str_visual.columns(5)
    with kc1:
        str_visual.markdown("#### [⚡ 삼성전자 (005930)](https://finance.naver.com/item/main.naver?code=005930)")
        str_visual.info("파운드리 선단 공정 수율 궤도 진입 및 레거시 디램 업황 턴어라운드를 겨냥한 외국인 수급 대치 지대.")
    with kc2:
        str_visual.markdown("#### [🔥 SK하이닉스 (000660)](https://finance.naver.com/item/main.naver?code=000660)")
        str_visual.info("엔비디아 밸류체인 내 HBM 공급 스케줄 독점력 유지를 기반으로 한 강력한 실적 모멘텀.")
    with kc3:
        str_visual.markdown("#### [🧪 알테오젠 (196170)](https://finance.naver.com/item/main.naver?code=196170)")
        str_visual.info("글로벌 독점 파트너사향 SC 제형 변경 플랫폼 기술이전 마일스톤 가시화에 따른 코스닥 대장.")
    with kc4:
        str_visual.markdown("#### [🚘 현대차 (005380)](https://finance.naver.com/item/main.naver?code=005380)")
        str_visual.info("정부 밸류업 지수 핵심 편입 및 주주환원 자사주 소각 이행, 하이브리드 고마진 믹스 극대화 효과.")
    with kc5:
        str_visual.markdown("#### [🚀 한화에어로스페이스 (012450)](https://finance.naver.com/item/main.naver?code=012450)")
        str_visual.info("유럽 및 나토 동맹국 대상 방산 하드웨어 대규모 수출 인도기 도래로 실적 서프라이즈 구간 진입.")


# --- 탭 4: 월단위 매크로 지표 ---
with tab4:
    str_visual.header("📅 월간 핵심 매크로 발표 및 컨센서스 마스터 매트릭스")
    tab4_col1, tab4_col2, tab4_col3 = str_visual.columns(3)
    with tab4_col1:
        str_visual.markdown("### 🛒 Inflation Group (물가 지표군)")
        inf_matrix = [
            {"지표명": "소비자물가지수 (Headline CPI)", "전월 수치": "3.5%", "이번달 예상 (Cons)": "3.4%", "중요도": "⭐⭐⭐ 매우 높음"},
            {"지표명": "근원 소비자물가지수 (Core CPI)", "전월 수치": "3.8%", "이번달 예상 (Cons)": "3.7%", "중요도": "⭐⭐⭐ 매우 높음"},
            {"지표명": "개인소비지출 (Headline PCE)", "전월 수치": "2.7%", "이번달 예상 (Cons)": "2.6%", "중요도": "⭐⭐⭐ 매우 높음"},
            {"지표명": "근원 개인소비지출 (Core PCE)", "전월 수치": "2.8%", "이번달 예상 (Cons)": "2.7%", "중요도": "⭐⭐⭐ 매우 높음"},
            {"지표명": "생산자물가지수 (PPI)", "전월 수치": "2.2%", "이번달 예상 (Cons)": "2.1%", "중요도": "⭐⭐ 보통"}
        ]
        str_visual.dataframe(pd.DataFrame(inf_matrix), use_container_width=True, hide_index=True)
    with tab4_col2:
        str_visual.markdown("### 🛠️ Labor Market Group (고용 및 노동)")
        labor_matrix = [
            {"지표명": "미국 실업률 (Unemployment)", "전월 수치": "3.8%", "이번달 예상 (Cons)": "3.9%", "중요도": "⭐⭐⭐ 매우 높음"},
            {"지표명": "비농업 고용자 수 (Nonfarm)", "전월 수치": "303K", "이번달 예상 (Cons)": "250K", "중요도": "⭐⭐⭐ 매우 높음"},
            {"지표명": "신규 실업수당 청구건수", "전월 수치": "212K", "이번달 예상 (Cons)": "215K", "중요도": "⭐⭐ 보통"},
            {"지표명": "평균 시간당 임금 (Earnings)", "전월 수치": "4.1%", "이번달 예상 (Cons)": "4.0%", "중요도": "⭐⭐⭐ 매우 높음"},
            {"지표명": "JOLTS 구인보고서 / ADP 민간", "전월 수치": "8.7M", "이번달 예상 (Cons)": "8.6M", "중요도": "⭐⭐ 보통"}
        ]
        str_visual.dataframe(pd.DataFrame(labor_matrix), use_container_width=True, hide_index=True)
    with tab4_col3:
        str_visual.markdown("### 📈 Growth & Activity (성장 및 활동)")
        growth_matrix = [
            {"지표명": "ISM 제조업 PMI", "전월 수치": "49.2", "이번달 예상 (Cons)": "50.1", "중요도": "⭐⭐⭐ 매우 높음"},
            {"지표명": "ISM 서비스업 PMI", "전월 수치": "51.4", "이번달 예상 (Cons)": "52.0", "중요도": "⭐⭐⭐ 매우 높음"},
            {"지표명": "소비 판매 (Retail Sales)", "전월 수치": "0.7%", "이번달 예상 (Cons)": "0.4%", "중요도": "⭐⭐⭐ 매우 높음"},
            {"지표명": "산업 생산 (Industrial)", "전월 수치": "0.4%", "이번달 예상 (Cons)": "0.2%", "중요도": "⭐⭐ 보통"},
            {"지표명": "경기선행지수 (LEI)", "전월 수치": "-0.3%", "이번달 예상 (Cons)": "-0.1%", "중요도": "⭐⭐ 보통"}
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
    om1.metric("DXY 달러인덱스", f"{macro_results.get('달러 인덱스', {}).get('현재가', 0):.2f}", f"{macro_results.get('달러 인덱스', {}).get('일간변동(%)', 0):.2f}%")
    om2.metric("美 10Y 국채금리", f"{macro_results.get('미 국채 10년물', {}).get('현재가', 0):.2f}%")
    om3.metric("VIX 공포지수", f"{macro_results.get('VIX 공포지수', {}).get('현재가', 0):.2f}")
    om4.metric("WTI 국제유가", f"${macro_results.get('WTI 유가', {}).get('현재가', 0):.2f}")
    om5.metric("금 선물 (Gold)", f"${macro_results.get('금 선물', {}).get('현재가', 0):.2f}")
    with om6:
        str_visual.markdown("**🔥 Fear & Greed**")
        str_visual.markdown("<h1 style='color:#ff4b4b; font-size:42px; font-weight:bold; margin-top:-15px;'>65 (Greed)</h1>", unsafe_allow_html=True)
   
    str_visual.markdown("---")
    str_visual.markdown("#### 📈 S&P 500 실시간 다년도 종합 추세선 차트")
   
    tradingview_chart_code = """
    <div class="tradingview-widget-container" style="height:380px;">
      <div id="tradingview_expert_chart" style="height:100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({
        "autosize": true, "symbol": "SP:SPX", "interval": "D", "timezone": "Etc/UTC",
        "theme": "light", "style": "1", "locale": "kr", "container_id": "tradingview_expert_chart"
      });
      </script>
    </div>
    """
    components.html(tradingview_chart_code, height=380)
       
    str_visual.markdown("---")
    str_visual.markdown("#### 🧱 11대 섹터 및 5대 핵심 팩터 마스터 인프라 맵")
   
    sector_tickers_v4 = {"XLK":"XLK", "XLU":"XLU", "XLE":"XLE", "SPHB":"SPHB", "SPLV":"SPLV", "IVW":"IVW", "IVE":"IVE", "SOXX":"SOXX", "XLY":"XLY", "XLF":"XLF", "XLV":"XLV", "XLI":"XLI", "XLP":"XLP", "XLB":"XLB", "XLC":"XLC", "XLRE":"XLRE"}
    sec_res_v4 = get_expert_calculated_data({"sect": sector_tickers_v4}, selected_date)
   
    sector_definition_data = [
        {"티커": "XLK", "섹터이름": "Technology", "주요 특징 / 대표 종목": "Apple, Microsoft, Nvidia, Broadcom", "로테이션 성격": "Growth / High Beta", "대시보드 추천 용도": "테크 사이클 선행"},
        {"티커": "SPHB", "섹터이름": "S&P500 High Beta", "주요 특징 / 대표 종목": "고베타 변동성 상위 100종목", "로테이션 성격": "High Beta / 쏠림", "대시보드 추천 용도": "시장 탐욕 강도 계측"},
        {"티커": "SPLV", "섹터이름": "S&P500 Low Beta", "주요 특징 / 대표 종목": "저베타 안전 방어성 100종목", "로테이션 성격": "Low Beta / 방어", "대시보드 추천 용도": "하방 지지 체력 필터링"},
        {"티커": "IVW", "섹터이름": "S&P500 Growth", "주요 특징 / 대표 종목": "대형 성장주 인프라 팩터 지수", "로테이션 성격": "Growth / 확장기", "대시보드 추천 용도": "성장주 유동성 추세선"},
        {"티커": "IVE", "섹터이름": "S&P500 Value", "주요 특징 / 대표 종목": "대형 전통 가치주 지수", "로테이션 성격": "Value / 수축기", "대시보드 추천 용도": "가치주 로테이션 포착"},
        {"티커": "SOXX", "섹터이름": "Semiconductor Index", "주요 특징 / 대표 종목": "Nvidia, AMD, Broadcom, Qualcomm", "로테이션 성격": "Cyclical / 핵심 테크", "대시보드 추천 용도": "글로벌 경기 사이클 선행"},
        {"티커": "XLY", "섹터이름": "Consumer Discretionary", "주요 특징 / 대표 종목": "Amazon (~28%), Tesla (~20%), Home Depot", "로테이션 성격": "Cyclical / 소비", "대시보드 추천 용도": "테슬라 민감, 경기회복 proxy"},
        {"티커": "XLF", "섹터이름": "Financials", "주요 특징 / 대표 종목": "JPMorgan, Berkshire, Visa", "로테이션 성격": "Cyclical / 금리 민감", "대시보드 추천 용도": "금리 + 경제 성장"},
        {"티커": "XLE", "섹터이름": "Energy", "주요 특징 / 대표 종목": "Exxon, Chevron", "로테이션 성격": "Cyclical / 원자재", "대시보드 추천 용도": "Oil 가격 연동"},
        {"티커": "XLV", "섹터이름": "Health Care", "주요 특징 / 대표 종목": "Eli Lilly, UnitedHealth, AbbVie", "로테이션 성격": "Defensive", "대시보드 추천 용도": "안정 + 바이오"},
        {"티커": "XLI", "섹터이름": "Industrials", "주요 특징 / 대표 종목": "GE, Caterpillar, Boeing", "로테이션 성격": "Cyclical", "대시보드 추천 용도": "경기 회복"},
        {"티커": "XLP", "섹터이름": "Consumer Staples", "주요 특징 / 대표 종목": "Procter&Gamble, Coca-Cola, Walmart", "로테이션 성격": "Defensive", "대시보드 추천 용도": "방어주"},
        {"티커": "XLU", "섹터이름": "Utilities", "주요 특징 / 대표 종목": "NextEra, Southern", "로테이션 성격": "Defensive / 금리 민감", "대시보드 추천 용도": "안정 + 배당"},
        {"티커": "XLB", "섹터이름": "Materials", "주요 특징 / 대표 종목": "Linde, Sherwin-Williams", "로테이션 성격": "Cyclical", "대시보드 추천 용도": "원자재 / 인프라"},
        {"티커": "XLC", "섹터이름": "Communication Services", "주요 특징 / 대표 종목": "Meta, Alphabet, Netflix, Disney", "로테이션 성격": "Growth", "대시보드 추천 용도": "디지털 미디어"},
        {"티커": "XLRE", "섹터이름": "Real Estate", "주요 특징 / 대표 종목": "Prologis, American Tower", "로테이션 성격": "Defensive / 금리 민감", "대시보드 추천 용도": "REITs"}
    ]
   
    for row in sector_definition_data:
        t = row["티커"]
        target_d = sec_res_v4.get(t, {"현재가":0, "일간변동(%)":0})
        row["현재 금액($)"] = round(float(target_d["현재가"]), 2)
        row["일간 변동(%)"] = round(float(target_d["일간변동(%)"]), 2)
       
    df_expert_sec = pd.DataFrame(sector_definition_data)
    str_visual.dataframe(df_expert_sec.style.map(color_delta_grid, subset=["일간 변동(%)"]), use_container_width=True, hide_index=True)


    str_visual.markdown("---")
    str_visual.markdown("#### 📅 실시간 Macro 핵심 스프레드 가이드라인 및 위험 신호 통제소")
    term_gap = macro_results.get('장단기 금리차', {}).get('현재가', 0)
    c_2y_rate = macro_results.get('미 국채 2년물', {}).get('현재가', 0)
    jpy_rate = macro_results.get('USD/JPY (캐리 신호)', {}).get('현재가', 0)
   
    macro_guide_sheet = [
        {"핵심 지표명": "10Y-2Y 장단기 금리차", "현재 수치": f"{term_gap:.2f} %p", "위험 임계치 가이드": "0.00%p 인근 도달 시 침체 폭탄 카운트다운", "상태": "🚨 리스크 전개" if term_gap > -0.10 else "■ 정상"},
        {"핵심 지표명": "美 국채 10년물 금리", "현재 수치": f"{macro_results.get('미 국채 10년물', {}).get('현재가', 0):.2f}%", "위험 임계치 가이드": "4.5% 돌파 시 자산 시장 멀티플 강한 하방 압박", "상태": "■ 관찰"},
        {"핵심 지표명": "美 국채 2년물 금리", "현재 수치": f"{c_2y_rate:.2f}%", "위험 임계치 가이드": "5.0% 이상 고착화 시 지수 밸류에이션 붕괴", "상태": "■ 관찰"},
        {"핵심 지표명": "USD/JPY 환율 (엔화)", "현재 수치": f"{jpy_rate:.2f} 엔", "위험 임계치 가이드": "140엔 이하로 급락 시 마진콜 엔캐리 청산", "상태": "🚨 경계"},
        {"핵심 지표명": "VIX 변동성 지수", "현재 수치": f"{macro_results.get('VIX 공포지수', {}).get('현재가', 0):.2f}", "위험 임계치 가이드": "25 이상 급등 시 글로벌 패닉셀 국면 도래", "상태": "■ 정상"},
        {"핵심 지표명": "원/달러 환율 브레이크", "현재 수치": f"{macro_results.get('원달러 환율', {}).get('현재가', 0):.2f}원", "위험 임계치 가이드": "1380원 돌파 시 국내 마켓 외국인 이탈 가속", "상태": "■ 정상"}
    ]
    str_visual.dataframe(pd.DataFrame(macro_guide_sheet), use_container_width=True, hide_index=True)


# --- 탭 6: 고급 리스크 & 통화유동성 마스터 북 ---
with tab6:
    str_visual.header("🦅 고급 리스크 및 유동성 깊이 분석 모듈")
    tlt_d = get_expert_calculated_data({"변동성": {"TLT": "TLT"}}, selected_date).get("TLT", {"일간변동(%)":0})
    hyg_d = get_expert_calculated_data({"부도스프레드": {"HYG": "HYG"}}, selected_date).get("HYG", {"현재가":0, "일간변동(%)":0})
   
    rk_col1, rk_col2 = str_visual.columns(2)
    with rk_col2:
        str_visual.markdown("### 📊 자금 로테이션 및 투기 세력 동조화 레이더")
        str_visual.metric("🌋 채권시장 실시간 변동성 모멘텀 (MOVE Index 프록시)", f"{tlt_d['일간변동(%)']:.2f} %")
        str_visual.caption("⚠️ **MOVE Index 가이드:** 채권 변동성이 급등하여 국채 투매가 나오면 주식 변동성(VIX)보다 무조건 한 발 먼저 자산 시장 붕괴를 경고합니다.")
    with rk_col1:
        str_visual.markdown("### 🏛️ 5대 유동성 오케스트레이션 정밀 기술 지표")
        str_visual.markdown(f"""
        1. **SOFR (담보조달 금리 프록시):** 뉴욕 자금시장의 실제 하루짜리 담보 대출 금리 매커니즘입니다. 단기 채권 금리와 이격이 벌어지면 금융 조달 뱅크런 신호입니다. (국채 2Y 기반 동기화)
        2. **TED Spread (은행간 신뢰도 임계):** 3개월 만기 미 국채 금리와 은행간 리보금리의 차이로 **[0.5%p 돌파 시 시스템 신용 크래시]** 신호입니다.
        3. **LIBOR-OIS Spread:** 금리 전환기 자금시장 내 신용 프리미엄 유휴 자금 경색 유무를 판별하는 잣대입니다.
        4. **HY Spread 프록시 (하이일드 채권 스프레드):** 현재 고위험 정크본드 ETF(HYG) 가격은 `${hyg_d['현재가']:.2f}` ({hyg_d['일간변동(%)']:.2f}%). 스프레드 변동 폭 확대 시 한계기업 연쇄 도산 신호입니다.
        5. **Bitcoin vs Nasdaq Correlation:** 두 자산의 자금 동조성 강도를 파악하여 현재 자금 유입이 '진짜 경제 성장'인지 '단순 투기적 레버리지(Proxy)'인지 진단하는 선행 자금줄 매커니즘입니다.
        """)


# --- 탭 7: 글로벌 통화정책 캘린더 ---
with tab7:
    str_visual.header("🗓️ 글로벌 중앙은행 핵심 경제지표 캘린더 스케줄러 (실시간 동기화 완료)")
    str_visual.caption("전 세계 주요 권역의 경제 데이터 및 중앙은행 일정이 동기화되어 표출되는 마스터 경제 허브입니다.")
   
    tradingview_widget_js = """
    <div class="tradingview-widget-container" style="height:3000px; width:100%;">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>
      {
      "colorTheme": "light",
      "isTransparent": false,
      "width": "100%",
      "height": "100%",
      "locale": "kr",
      "importanceFilter": "-1,0,1",
      "countryFilter": "us,eu,gb,jp,cn,kr"
      }
      </script>
    </div>
    """
    components.html(tradingview_widget_js, height=3000)


# --- 탭 8: 오늘의 투자 공부 ---
with tab8:
    str_visual.header("🎓 Today's Macro Intelligence (오늘의 마스터급 지혜 10선)")
    str_visual.success("원칙 투자를 위한 매일 아침 거시경제 브리핑 메시지")
   
    study_text_block = """
    1. **💡 달러인덱스(DXY)와 채권금리가 동시에 튈 때:** 시장의 지배적인 유동성이 위험자산에서 무조건 안전자산(현금)으로 대도피하는 리스크 오프 국면입니다. 이때는 무리한 매수를 쉬는 것이 최고의 매매입니다.
    2. **⚖️ 장단기 금리차 역전의 진짜 무서움:** 10Y-2Y 스프레드가 마이너스 영역에 깊게 박혀있을 때보다, 다시 플러스 **0.00%p 인근으로 빠르게 정상화(Uninversion)될 때** 역사적 경기침체와 지수 크래시가 터졌습니다.
    3. **🛢️ 유가와 구리가격의 동행 법칙:** 구리 가격이 무너지고 유가만 치솟으면 경기 확장이 없는 비용 인상 형 악성 인플레이션(스태그플레이션)의 신호탄입니다. 주식 비중을 강하게 줄여야 합니다.
    4. **💴 엔화 환율 마지노선 140엔 법칙:** 일본 엔달러 환율이 140엔 밑으로 급락하는 엔고 현상이 오면, 글로벌 헤지펀드들이 기술주를 강제 처분하여 엔화 빚을 갚는 '엔 캐리 청산 매도 폭탄'이 나스닥을 직격합니다.
    5. **🌋 VIX 지수의 역발상 기회:** VIX 지수가 20 이상으로 튀며 시장이 비명을 지를 때 분할 매수를 준비하고, VIX가 12~13 수준으로 극단적인 평화주의에 젖어 들었을 때가 가장 탐욕이 가득해 리스크 통제가 필요한 시점입니다.
    6. **🚀 SPHB vs SPLV (하이베타 대 로우베타) 매커니즘:** 고베타 기술주 상승 강도가 로우베타 방어주를 압도하는 동안에는 대세 상승장이 유지되나, 지수 상승 중 SPHB/SPLV 비율이 고꾸라지면 기관들이 몰래 도망치는 분산 국면입니다.
    7. **💻 반도체 지수(SOXX)의 선행 속성:** SOXX 인덱스는 전 세계 글로벌 공급망과 리드타임 경제를 약 6개월 먼저 반영하는 실물 경제의 치트키 영역입니다.
    8. **📊 Shiller PE 및 Buffett Indicator 버퍼:** 총시가총액을 국가 GDP로 나눈 버핏 지수가 150~180%를 초과할 때는 거시경제 펀더멘털 대비 오버슈팅 국면이므로 현금 비중 확보가 유리합니다.
    9. **🏢 하이일드 채권 스프레드 임계점 4.5%:** 부실채권 가산금리가 4.5%p를 상향 돌파하기 시작하면 월가 신용 평가사들의 신용등급 강등 랠리가 이어지며 증시 변동성이 극대화됩니다.
    10. **🏛️ 연준 대차대조표 양적긴축(QT)의 본질:** 기준금리 동결 여부보다 중요한 것은 연준이 매달 채권 만기 상환을 통해 시장에서 실제로 흡수하는 유동성의 유휴 자금 강도입니다.
    """
    str_visual.markdown(study_text_block)


# --- 탭 9: 투자 학습 일지 ---
with tab9:
    str_visual.header("📚 매일 쌓여가는 매크로 투자 학습 일지")
    log_date_str = selected_date.strftime('%Y-%m-%d')
    str_visual.info(f"📝 **{log_date_str} 리서치 노트 및 당일 학습 인텔리전스 아카이브**")
    str_visual.markdown(study_text_block)


# --- 탭 10: 원클릭 워프 스테이션 ---
with tab10:
    str_visual.header("🔗 투자 & 개발 원클릭 워프 링크 센터")
    str_visual.caption("업무 시 사용하는 모든 플랫폼으로의 초고속 하이퍼링크 모음입니다.")
    ln1, ln2, ln3, ln4 = str_visual.columns(4)
    with ln1:
        str_visual.markdown("### 🏛️ 리서치 인프라")
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

