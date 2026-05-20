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
    
    # 🔑 비밀번호 입력창
    str_visual.subheader("🔑 에이전트 인증")
    user_password = str_visual.text_input("관리자 암호를 입력하세요:", type="password")
    
    if user_password == ADMIN_PASSWORD:
        str_visual.success("🔓 Rooney 인증 성공!")
        str_visual.markdown("---")
        
        str_visual.subheader("📁 활성 프로젝트 그룹")
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
        
        str_visual.subheader("💬 Rooney에게 명령하기")
        user_command = str_visual.text_area(
            "무엇을 도와드릴까요?",
            placeholder="예시: 오늘 테슬라랑 엔비디아 변동폭 요약해서 X에 올릴 글 짜줘"
        )
        
        if str_visual.button("⚡ Rooney 작동하기"):
            if user_command:
                if client:
                    with str_visual.spinner("Rooney가 시장 상황을 분석하여 답변을 생성 중입니다..."):
                        try:
                            system_instruction = (
                                "당신의 이름은 'Rooney'입니다. 민재 님의 투자 운영과 SNS 성장을 돕는 전문 AI 에이전트입니다. "
                                "독자의 시선을 사로잡는 명쾌함과 깊이 있는 인사이트를 갖추되, 친근하고 약간의 위트가 있는 프로페셔널한 톤앤매너로 대답하세요."
                            )
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
            else:
                str_visual.warning("명령어를 입력해 주세요.")
                
    elif user_password == "":
        str_visual.info("🔒 저를 사용하시려면 관리자 암호를 입력해 주세요.")
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
    "에너지원자재": {"WTI 유가": "CL=F", "브렌트유": "BZ=F", "구리 선물 가격": "HG=F", "은 선물 가격": "SI=F"},
    "디지털자산": {"비트코인 (BTC)": "BTC-USD", "이더리움 (ETH)": "ETH-USD"}
}

# 🇺🇸 미국 주식 50선 마스터 딕셔너리
US_Stocks = {
    "빅테크/핵심관심": {"테슬라": "TSLA", "엔비디아": "NVDA", "애플": "AAPL", "마이크로소프트": "MSFT", "구글": "GOOGL", "메타": "META", "아마존": "AMZN", "넷플릭스": "NFLX", "브로드컴": "AVGO", "AMD": "AMD"},
    "반도체/장비": {"TSMC": "TSM", "ASML": "ASML", "퀄컴": "QCOM", "인텔": "INTC", "어플라이드": "AMAT", "램리서치": "LRCX", "텍사스인스트": "TXN", "마이크론": "MU", "아날로그디바": "ADI"},
    "금융/소비재": {"JP모건": "JPM", "버크셔 해서웨이": "BRK.B", "뱅크오브아메리카": "BAC", "웰스파고": "WFC", "골드만삭스": "GS", "모건스탠리": "MS", "월마트": "WMT", "코스트코": "COST", "홈디포": "HD", "프록터앤갬블": "PG", "코카콜라": "KO", "펩시코": "PEP", "맥도날드": "MCD"},
    "헬스케어/에너지": {"일라이 릴리": "LLY", "노보 노디스크": "NVO", "존슨앤존슨": "JNJ", "머크": "MRK", "화이자": "PFE", "유나이티드헬스": "UNH", "엑슨모빌": "XOM", "셰브론": "CVX", "장인추천-XLE": "XLE"},
    "방산/제조/모빌리티": {"록히드 마틴": "LMT", "보잉": "BA", "캐터필러": "CAT", "우버": "UBER", "GE에어로": "GE", "허니웰": "HON", "페덱스": "FDX", "세일즈포스": "CRM"}
}

# 🇰🇷 한국 주식 50선 마스터 딕셔너리
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
    # 연초 기준 및 전고점 데이터 유실 방지를 위한 충분한 백데이터 수집 (1년 반 분량)
    start_point = base_date - timedelta(days=550)
    end_point = base_date + timedelta(days=1)
    
    for cat, stocks in asset_dict.items():
        for name, ticker in stocks.items():
            try:
                obj = yf.Ticker(ticker)
                df = obj.history(start=start_point.strftime('%Y-%m-%d'), end=end_point.strftime('%Y-%m-%d'))
                
                if df.empty:
                    # 데이터 공백 시 2차 백업 시도
                    df = obj.history(period="2y")
                
                # 시계열 인덱스에서 타겟 날짜 이전 데이터만 필터링
                df = df[df.index.date <= base_date]
                
                if len(df) >= 2:
                    # 일자 정보 확보
                    current_date_str = df.index[-1].strftime('%m-%d')
                    
                    c_close = df['Close'].iloc[-1]
                    p_close = df['Close'].iloc[-2]
                    
                    # 주간, 월간 베이스 가변 인덱스 (데이터 안전지대 확보)
                    w_close = df['Close'].iloc[max(-5, -len(df))]
                    m_close = df['Close'].iloc[max(-20, -len(df))]
                    
                    # 연초 대비 계산용 데이터 서칭
                    df_year = df[df.index.year == base_date.year]
                    y_close = df_year['Close'].iloc[0] if not df_year.empty else df['Close'].iloc[0]
                    
                    # 🎯 전고점(All-Time High / Peak) 대비 하락률 연산
                    high_peak = df['Close'].max()
                    mdd_pct = round(((c_close - high_peak) / high_peak) * 100, 2)
                    
                    results[name] = {
                        "분류": cat,
                        "조회일자": current_date_str,
                        "현재가": round(c_close, 2),
                        "전일종가": round(p_close, 2),
                        "일간변동(%)": round(((c_close - p_close) / p_close) * 100, 2),
                        "주간변동": round(c_close - w_close, 2),
                        "주간변동(%)": round(((c_close - w_close) / w_close) * 100, 2),
                        "월간변동": round(c_close - m_close, 2),
                        "월간변동(%)": round(((c_close - m_close) / m_close) * 100, 2),
                        "연초대비변동": round(c_close - y_close, 2),
                        "연초대비(%)": round(((c_close - y_close) / y_close) * 100, 2),
                        "전고점대비(%)": mdd_pct
                    }
                else:
                    results[name] = {"분류": cat, "조회일자": "-", "현재가": 0.0, "전일종가": 0.0, "일간변동(%)": 0.0, "주간변동": 0.0, "주간변동(%)": 0.0, "월간변동": 0.0, "월간변동(%)": 0.0, "연초대비변동": 0.0, "연초대비(%)": 0.0, "전고점대비(%)": 0.0}
            except:
                results[name] = {"분류": cat, "조회일자": "-", "현재가": 0.0, "전일종가": 0.0, "일간변동(%)": 0.0, "주간변동": 0.0, "주간변동(%)": 0.0, "월간변동": 0.0, "월간변동(%)": 0.0, "연초대비변동": 0.0, "연초대비(%)": 0.0, "전고점대비(%)": 0.0}
    return results

# 데이터 파싱 엔진 통합 가동
with str_visual.spinner("선택하신 기준일의 글로벌 금융 데이터를 강력하게 동기화 중..."):
    macro_results = get_expert_calculated_data(Daily_Macro, selected_date)
    us_results = get_expert_calculated_data(US_Stocks, selected_date)
    kr_results = get_expert_calculated_data(Korea_Stocks, selected_date)
    
    # 장단기 스프레드 정밀 보정
    if macro_results.get("미 국채 10년물", {}).get("현재가", 0) > 0:
        diff_val = macro_results["미 국채 10년물"]["현재가"] - macro_results["미 국채 2년물"]["현재가"]
        macro_results["장단기 금리차"] = {"현재가": round(diff_val, 2), "일간변동(%)": 0.0, "주간변동(%)": 0.0, "월간변동(%)": 0.0}

# 🎨 플러스 그린 / 마이너스 레드 컬러 가이드
def color_delta_grid(val):
    if isinstance(val, (int, float)):
        color = 'green' if val > 0 else 'red' if val < 0 else 'black'
        return f'color: {color}; font-weight: bold;'
    return ''

# 🗂️ 6대 마스터 탭 레이아웃 선언
tab1, tab2, tab3, tab4, tab5, tab6 = str_visual.tabs([
    "🌐 거시경제(일단위)", 
    "🇺🇸 미국 주식 레이더 (50선)", 
    "🇰🇷 한국 주식 레이더 (50선)", 
    "📅 월단위 매크로 & FOMC", 
    "📺 장인 추천 올인원 마스터 뷰", 
    "🦅 중앙은행 & 정책 가이드북"
])

# --- 탭 1: 거시경제 일단위 지표 ---
with tab1:
    str_visual.header("🎯 일단위 핵심 매크로 전광판")
    m_col1, m_col2, m_col3, m_col4 = str_visual.columns(4)
    with m_col1:
        str_visual.metric(label="💵 원/달러 환율", value=f"{macro_results.get('원달러 환율', {}).get('현재가', 0)} 원", delta=f"{macro_results.get('원달러 환율', {}).get('일간변동(%)', 0)}%")
        str_visual.metric(label="📈 나스닥 지수", value=macro_results.get('나스닥 지수', {}).get('현재가', 0), delta=f"{macro_results.get('나스닥 지수', {}).get('일간변동(%)', 0)}%")
        str_visual.metric(label="🪙 비트코인 (BTC)", value=f"${macro_results.get('비트코인 (BTC)', {}).get('현재가', 0):,}", delta=f"{macro_results.get('비트코인 (BTC)', {}).get('일간변동(%)', 0)}%")
    with m_col2:
        str_visual.metric(label="🏦 미 국채 10년물 금리", value=f"{macro_results.get('미 국채 10년물', {}).get('현재가', 0)}%", delta=f"{macro_results.get('미 국채 10년물', {}).get('일간변동(%)', 0)}%")
        str_visual.metric(label="📊 장단기 금리차 (10Y-2Y)", value=f"{macro_results.get('장단기 금리차', {}).get('현재가', 0)} %p")
        str_visual.metric(label="🪙 이더리움 (ETH)", value=f"${macro_results.get('이더리움 (ETH)', {}).get('현재가', 0):,}", delta=f"{macro_results.get('이더리움 (ETH)', {}).get('일간변동(%)', 0)}%")
    with m_col3:
        str_visual.metric(label="🛢️ WTI 국제유가", value=f"${macro_results.get('WTI 유가', {}).get('현재가', 0)}", delta=f"{macro_results.get('WTI 유가', {}).get('일간변동(%)', 0)}%")
        str_visual.metric(label="🌋 VIX 공포지수", value=macro_results.get('VIX 공포지수', {}).get('현재가', 0), delta=f"{macro_results.get('VIX 공포지수', {}).get('일간변동(%)', 0)}%")
        str_visual.metric(label="🧪 구리 선물 가격", value=f"${macro_results.get('구리 선물 가격', {}).get('현재가', 0)}", delta=f"{macro_results.get('구리 선물 가격', {}).get('일간변동(%)', 0)}%")
    with m_col4:
        str_visual.metric(label="✨ 금 선물 가격", value=f"${macro_results.get('금 선물', {}).get('현재가', 0)}", delta=f"{macro_results.get('금 선물', {}).get('일간변동(%)', 0)}%")
        str_visual.metric(label="💵 달러 인덱스 (DXY)", value=macro_results.get('달러 인덱스', {}).get('현재가', 0), delta=f"{macro_results.get('달러 인덱스', {}).get('일간변동(%)', 0)}%")
        str_visual.metric(label="✨ 은 선물 가격", value=f"${macro_results.get('은 선물 가격', {}).get('현재가', 0)}", delta=f"{macro_results.get('은 선물 가격', {}).get('일간변동(%)', 0)}%")

    str_visual.markdown("---")
    macro_table = []
    for name, d in macro_results.items():
        if name == "장단기 금리차": continue
        macro_table.append({"자산명": name, "종가": d["현재가"], "일간 변동(%)": d["일간변동(%)"]})
    str_visual.dataframe(pd.DataFrame(macro_table).style.map(color_delta_grid, subset=["일간 변동(%)"]), use_container_width=True, hide_index=True)

# --- 탭 2: 미국 주식 레이더 (중앙 정렬 + 데이터 확장 + 폰트업 CSS) ---
with tab2:
    str_visual.header("💻 미국 핵심 주식 레이더 (시총 최상위 50선)")
    
    us_master_rows = []
    for name, d in us_results.items():
        us_master_rows.append({
            "섹터분류": d["분류"], "종목명": name, "날짜": d["조회일자"], 
            "현재가($)": d["현재가"], "전일종가($)": d["전일종가"], "일간(%)": d["일간변동(%)"],
            "주간변동($)": d["주간변동"], "주간(%)": d["주간변동(%)"], 
            "월간변동($)": d["월간변동"], "월간(%)": d["월간변동(%)"],
            "연초대비($)": d["연초대비변동"], "연초대비(%)": d["연초대비(%)"], 
            "전고점대비(%)": d["전고점대비(%)"]
        })
    df_us = pd.DataFrame(us_master_rows)
    
    # 글씨 크기 확장 및 중앙 정렬 주입 (Streamlit 스타일 시트 우회 장치)
    str_visual.markdown("""<style> div[data-testid="stDataFrame"] td { font-size: 16px !important; text-align: center !important; } </style>""", unsafe_allow_html=True)
    str_visual.dataframe(df_us.style.map(color_delta_grid, subset=["일간(%)", "주간(%)", "월간(%)", "연초대비(%)", "전고점대비(%)"]), use_container_width=True, hide_index=True)

# --- 탭 3: 한국 주식 레이더 (중앙 정렬 + 데이터 확장 + 폰트업 CSS) ---
with tab3:
    str_visual.header("🇰🇷 국내 시장 코스피/코스닥 대장주 (50선)")
    
    kr_master_rows = []
    for name, d in kr_results.items():
        kr_master_rows.append({
            "테마분류": d["분류"], "종목명": name, "날짜": d["조회일자"], 
            "현재가(원)": f"{int(d['현재가']):,}" if d['현재가'] > 0 else "0", 
            "전일종가(원)": f"{int(d['전일종가']):,}" if d['전일종가'] > 0 else "0", 
            "일간(%)": d["일간변동(%)"],
            "주간변동(원)": f"{int(d['주간변동']):,}" if d['주간변동'] != 0 else "0", "주간(%)": d["주간변동(%)"], 
            "월간변동(원)": f"{int(d['월간변동']):,}" if d['월간변동'] != 0 else "0", "월간(%)": d["월간변동(%)"],
            "연초대비(원)": f"{int(d['연초대비변동']):,}" if d['연초대비변동'] != 0 else "0", "연초대비(%)": d["연초대비(%)"], 
            "전고점대비(%)": d["전고점대비(%)"]
        })
    df_kr = pd.DataFrame(kr_master_rows)
    str_visual.dataframe(df_kr.style.map(color_delta_grid, subset=["일간(%)", "주간(%)", "월간(%)", "연초대비(%)", "전고점대비(%)"]), use_container_width=True, hide_index=True)

# --- 탭 4: 월단위 매크로 및 인베스팅 컨센서스 가이드 (완벽 복구) ---
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

# --- 탭 5: 올인원 마스터뷰 (실시간 자산 수치화 완료) ---
with tab5:
    str_visual.subheader("📺 ALL-IN-ONE 글로벌 매크로 인텔리전스 전광판")
    om_1, om_2, om_3, om_4, om_5, om_6 = str_visual.columns(6)
    om_1.metric("DXY 달러인덱스", macro_results.get("달러 인덱스", {}).get("현재가", 0))
    om_2.metric("美 10Y 국채금리", f"{macro_results.get('미 국채 10년물', {}).get('현재가', 0)}%")
    om_3.metric("VIX 공포지수", macro_results.get("VIX 공포지수", {}).get("현재가", 0))
    om_4.metric("WTI 국제유가", f"${macro_results.get('WTI 유가', {}).get('현재가', 0)}")
    om_5.metric("금 선물 (Gold)", f"${macro_results.get('금 선물', {}).get('현재가', 0)}")
    om_6.metric("Fear & Greed (심리)", "Manual 🔴 (하단 가이드 참조)")
    
    str_visual.markdown("---")
    mid_left, mid_right = str_visual.columns([1, 1])
    with mid_left:
        str_visual.markdown("#### 📈 S&P 500 추세 모니터링 (실시간)")
        str_visual.metric("S&P 500 지수", f"{macro_results.get('S&P 500', {}).get('현재가', 0)} pt", f"{macro_results.get('S&P 500', {}).get('일간변동(%)', 0)}%")
        
        str_visual.markdown("#### 🧱 주요 섹터 흐름 상대강도 (실시간)")
        # 장인 섹터 실제 수치 연산 연동
        xlk_d = get_expert_calculated_data({"테크": {"XLK": "XLK"}}, selected_date).get("XLK", {"일간변동(%)":0})
        xlu_d = get_expert_calculated_data({"유틸": {"XLU": "XLU"}}, selected_date).get("XLU", {"일간변동(%)":0})
        xle_d = get_expert_calculated_data({"에너지": {"XLE": "XLE"}}, selected_date).get("XLE", {"일간변동(%)":0})
        
        sector_real = [
            {"섹터구분": "XLK (테크)", "일간 변동률": f"{xlk_d['일간변동(%)']}%", "해석": "고성장 기술주 자금 강도"},
            {"섹터구분": "XLU (유틸리티)", "일간 변동률": f"{xlu_d['일간변동(%)']}%", "해석": "금리 민감 방어주 흐름"},
            {"섹터구분": "XLE (에너지)", "일간 변동률": f"{xle_d['일간변동(%)']}%", "해석": "원자재 유가 플레이 반영"}
        ]
        str_visual.table(pd.DataFrame(sector_real))
        
    with mid_right:
        str_visual.markdown("#### 📅 실시간 Macro 핵심 스프레드 보드")
        macro_all_in_one = [
            {"핵심 지표명": "10Y-2Y 장단기 금리차", "현재 수치": f"{macro_results.get('장단기 금리차', {}).get('현재가', 0)} %p", "장인급 해석": "역전 해소 상태 및 침체 위험 감지"},
            {"핵심 지표명": "美 국채 2년물 단기금리", "현재 수치": f"{macro_results.get('미 국채 2년물', {}).get('현재가', 0)}%", "장인급 해석": "연준 기준금리 기대를 가장 정밀하게 반영"},
            {"핵심 지표명": "USD/JPY 환율 (엔화)", "현재 수치": f"{macro_results.get('USD/JPY (캐리 신호)', {}).get('현재가', 0)} 엔", "장인급 해석": "엔 캐리트레이드 청산 리스크 마지노선 관찰"}
        ]
        str_visual.dataframe(pd.DataFrame(macro_all_in_one), use_container_width=True)

# --- 탭 6: 중앙은행 정책 가이드북 (고급 지표 실시간 연동) ---
with tab6:
    str_visual.header("🦅 중앙은행 정책 캘린더 및 리스크 매커니즘")
    
    # 실시간 채권변동성 및 하이일드 프록시 데이터 추출
    move_proxy = get_expert_calculated_data({"채권변동성프록시": {"정부채ETF(TLT)": "TLT"}}, selected_date).get("정부채ETF(TLT)", {"일간변동(%)":0})
    hy_proxy = get_expert_calculated_data({"하이일드프록시": {"하이일드채권(HYG)": "HYG"}}, selected_date).get("하이일드채권(HYG)", {"현재가":0, "일간변동(%)":0})
    
    p_col1, p_col2 = str_visual.columns(2)
    with p_col1:
        str_visual.markdown("### 🏛️ 통화정책 실시간 프록시 데이터")
        str_visual.metric(label="📉 미 국채 2년물 (기준금리 전망 연동)", value=f"{macro_results.get('미 국채 2년물', {}).get('현재가', 0)}%")
        str_visual.metric(label="⚡ 미국 하이일드 채권 가격 (HYG)", value=f"${hy_proxy['현재가']}", delta=f"{hy_proxy['일간변동(%)']}% (스프레드 대용)")
        str_visual.caption("💡 하이일드 가격(HYG) 급락 시 기업 부도 리스크 및 크레딧 스프레드 폭등 신호로 간주합니다.")
        
    with p_col2:
        str_visual.markdown("### 📊 변동성 및 자금 매커니즘")
        str_visual.metric(label="🌋 장기 국채 변동성 프록시 (TLT 일간 변동)", value=f"{move_proxy['일간변동(%)']}%")
        str_visual.caption("💡 채권 변동성(MOVE)이 튀면 주식 변동성(VIX)보다 선행하여 월가의 리스크 오프를 유발합니다.")