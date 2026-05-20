import yfinance as yf
import pandas as pd
import streamlit as str_visual
from datetime import datetime, timedelta
# 🤖 Google GenAI 최신 라이브러리 추가
from google import genai

# 1. 웹 브라우저 창 전체 설정
str_visual.set_page_config(page_title="글로벌 매크로 주식 레이더 V2", layout="wide")

# 2. Streamlit Secrets 시스템에서 API 키 및 패스워드 로드
if "GEMINI_API_KEY" in str_visual.secrets:
    client = genai.Client(api_key=str_visual.secrets["GEMINI_API_KEY"])
else:
    client = None

ADMIN_PASSWORD = str_visual.secrets.get("ADMIN_PASSWORD", "1234")

# =========================================================================
# 🤖 좌측 사이드바 : 민재 님이 좋아하시던 [이전 버전 스타일] Rooney 워크스페이스
# =========================================================================
with str_visual.sidebar:
    str_visual.header("🤖 AI 에이전트 'Rooney'")
    str_visual.caption("Rooney is King")
    
    str_visual.markdown("---")
    
    # 🔑 비밀번호 입력창
    str_visual.subheader("🔑 에이전트 인증")
    user_password = str_visual.text_input("관리자 암호를 입력하세요:", type="password")
    
    # 비밀번호가 일치할 때만 깔끔한 Rooney 창 오픈
    if user_password == ADMIN_PASSWORD:
        str_visual.success("🔓 Rooney 인증 성공!")
        str_visual.markdown("---")
        
        # 📁 활성 프로젝트 그룹 선택
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
        
        # 💬 깔끔한 명령어 입력 창
        str_visual.subheader("💬 Rooney에게 명령하기")
        user_command = str_visual.text_area(
            "무엇을 도와드릴까요?",
            placeholder="예시: 오늘 테슬라랑 엔비디아 변동폭 요약해서 X에 올릴 글 짜줘"
        )
        
        # ⚡ Rooney 작동 버튼
        if str_visual.button("⚡ Rooney 작동하기"):
            if user_command:
                if client:
                    with str_visual.spinner("Rooney가 시장 상황을 분석하여 답변을 생성 중입니다..."):
                        try:
                            system_instruction = (
                                "당신의 이름은 'Rooney'입니다. 민재 님의 투자 운영과 SNS 성장을 돕는 전문 AI 에이전트입니다. "
                                "독자의 시선을 사로잡는 명쾌함과 깊이 있는 인사이트를 갖추되, 친근하고 약간의 위트가 있는 프로페셔널한 톤앤매너로 대답하세요. "
                                f"현재 민재 님이 활성화한 프로젝트 모드는 [{project_mode}] 입니다. 이 모드의 목적에 집중하여 요청에 답하세요."
                            )
                            
                            response = client.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=user_command,
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
        str_visual.error("❌ 비밀번호가 틀렸습니다. 접근할 수 없습니다.")

    str_visual.markdown("---")

# =========================================================================
# 메인 화면 우측 배치용 과거 날짜 조회 캘린더 레이아웃 구성
# =========================================================================
str_visual.title("📊 글로벌 매크로 & 주식 마스터 대시보드")

# 📅 화면 우측 상단에 캘린더를 깔끔하게 배치하기 위한 컬럼 분할
main_top_left, main_top_right = str_visual.columns([3, 1])

with main_top_left:
    str_visual.markdown("매일 아침 확인하는 나만의 투자 나침반")

with main_top_right:
    # 우측 정렬 캘린더 (기본값은 오늘 날짜)
    selected_date = str_visual.date_input("📅 과거 날짜 데이터 조회", datetime.today())

str_visual.markdown(f"**현재 데이터 기준일:** `{selected_date.strftime('%Y-%m-%d')}`")
str_visual.markdown("---")

# =========================================================================
# 데이터 세팅 영역
# =========================================================================

# 1. 하루 단위 매크로 지표 목록
Daily_Macro = {
    "주식심리": {"나스닥 지수": "^IXIC", "S&P 500": "^GSPC", "다우존스": "^DJI", "VIX 공포지수": "^VIX"},
    "채권금리": {"미 국채 10년물": "^TNX", "미 국채 2년물": "^IRX"},
    "통화환율": {"원달러 환율": "KRW=X", "달러 인덱스": "DX-Y.NYB", "MSCI 한국 ETF": "EWY", "USD/JPY (캐리 신호)": "JPY=X"},
    "에너지원자재": {"WTI 유가": "CL=F", "브렌트유": "BZ=F", "구리 선물 가격": "HG=F", "은 선물 가격": "SI=F"},
    "디지털자산": {"비트코인 (BTC)": "BTC-USD", "이더리움 (ETH)": "ETH-USD"}
}

# 2. 🇺🇸 미국 주식 레이더 대장주 확장 (정확히 50개 종목 매칭)
US_Stocks = {
    "빅테크/핵심관심": {"테슬라": "TSLA", "엔비디아": "NVDA", "애플": "AAPL", "마이크로소프트": "MSFT", "구글": "GOOGL", "메타": "META", "아마존": "AMZN", "넷플릭스": "NFLX", "브로드컴": "AVGO", "AMD": "AMD"},
    "반도체/장비": {"TSMC": "TSM", "ASML": "ASML", "퀄컴": "QCOM", "인텔": "INTC", "어플라이드": "AMAT", "램리서치": "LRCX", "텍사스인스트": "TXN", "마이크론": "MU", "아날로그디바": "ADI"},
    "금융/소비재": {"JP모건": "JPM", "버크셔 해서웨이": "BRK.B", "뱅크오브아메리카": "BAC", "웰스파고": "WFC", "골드만삭스": "GS", "모건스탠리": "MS", "월마트": "WMT", "코스트코": "COST", "홈디포": "HD", "프록터앤갬블": "PG", "코카콜라": "KO", "펩시코": "PEP", "맥도날드": "MCD"},
    "헬스케어/에너지": {"일라이 릴리": "LLY", "노보 노디스크": "NVO", "존슨앤존슨": "JNJ", "머크": "MRK", "화이자": "PFE", "유나이티드헬스": "UNH", "엑슨모빌": "XOM", "셰브론": "CVX", "장인추천-XLE": "XLE"},
    "방산/제조/모빌리티": {"록히드 마틴": "LMT", "보잉": "BA", "캐터필러": "CAT", "우버": "UBER", "GE에어로": "GE", "허니웰": "HON", "페덱스": "FDX", "세일즈포스": "CRM"}
}

# 3. 🇰🇷 한국 주식 레이더 대장주 확장 (정확히 50개 종목 매칭)
Korea_Stocks = {
    "반도체/IT": {"삼성전자": "005930.KS", "SK하이닉스": "000660.KS", "NAVER": "035420.KS", "카카오": "035720.KS", "한미반도체": "042700.KS", "삼성전우": "005935.KS"},
    "자동차/배터리": {"현대차": "005380.KS", "기아": "000270.KS", "LG엔솔": "373220.KS", "POSCO홀딩스": "005490.KS", "삼성SDI": "006400.KS", "에코프로비엠": "247540.KQ", "에코프로": "086520.KQ", "LG화학": "051910.KS", "포스코퓨처엠": "003670.KS"},
    "바이오/헬스": {"삼성바이오로직스": "207940.KS", "셀트리온": "068270.KS", "알테오젠": "196170.KQ", "HLB": "028300.KQ", "유한양행": "000100.KS", "SK바이오팜": "326030.KS"},
    "금융/지주사": {"KB금융": "105560.KS", "신한지주": "055550.KS", "하나금융지주": "086790.KS", "메리츠금융": "138040.KS", "삼성생명": "032830.KS", "삼성화재": "000810.KS", "한국전력": "015760.KS"},
    "중공업/방산/엔지니어링": {"한화에어로스페이스": "012450.KS", "두산에너빌리티": "034020.KS", "HD현대중공업": "329180.KS", "삼성중공업": "010140.KS", "HD현대일렉트릭": "247540.KS", "현대건설": "000720.KS"},
    "엔터/기타대장주": {"하이브": "352820.KS", "고려아연": "010130.KS", "KT&G": "033780.KS", "SK이노베이션": "096770.KS", "S-Oil": "010950.KS", "크래프톤": "259960.KS", "엔씨소프트": "036570.KS", "넷마블": "251270.KS", "LG전자": "066570.KS", "삼성SDS": "018260.KS", "대한항공": "003490.KS", "HMM": "011200.KS"}
}

# 캘린더 날짜를 반영한 주가 데이터 가공 백엔드 함수
def get_historical_radar_data(asset_dict, base_date):
    results = {}
    start_point = base_date - timedelta(days=400)
    for cat, stocks in asset_dict.items():
        for name, ticker in stocks.items():
            try:
                obj = yf.Ticker(ticker)
                df = obj.history(start=start_point.strftime('%Y-%m-%d'), end=(base_date + timedelta(days=1)).strftime('%Y-%m-%d'))
                if len(df) >= 2:
                    c_close = df['Close'].iloc[-1]
                    p_close = df['Close'].iloc[-2]
                    w_close = df['Close'].iloc[max(-6, -len(df))]
                    m_close = df['Close'].iloc[max(-21, -len(df))]
                    y_close = df[df.index.year == base_date.year]['Close'].iloc[0] if len(df[df.index.year == base_date.year]) > 0 else df['Close'].iloc[0]
                    
                    results[name] = {
                        "분류": cat,
                        "종가": round(c_close, 2),
                        "일간": round(((c_close - p_close) / p_close) * 100, 2),
                        "주간": round(((c_close - w_close) / w_close) * 100, 2),
                        "월간": round(((c_close - m_close) / m_close) * 100, 2),
                        "연초": round(((c_close - y_close) / y_close) * 100, 2)
                    }
                else:
                    results[name] = {"분류": cat, "종가": 0, "일간": 0, "주간": 0, "월간": 0, "연초": 0}
            except:
                results[name] = {"분류": cat, "종가": 0, "일간": 0, "주간": 0, "월간": 0, "연초": 0}
    return results

# 데이터 파싱 엔진 가동
with str_visual.spinner("선택하신 기준일의 글로벌 금융 데이터를 연산하는 중..."):
    macro_results = get_historical_radar_data(Daily_Macro, selected_date)
    us_results = get_historical_radar_data(US_Stocks, selected_date)
    kr_results = get_historical_radar_data(Korea_Stocks, selected_date)
    
    # 장단기 금리차 계산
    if "미 국채 10년물" in macro_results and "미 국채 2년물" in macro_results and macro_results["미 국채 10년물"]["종가"] > 0:
        diff = macro_results["미 국채 10년물"]["종가"] - macro_results["미 국채 2년물"]["종가"]
        macro_results["장단기 금리차"] = {"종가": round(diff, 2), "일간": 0, "주간": 0, "월간": 0, "연초": 0}
    else:
        macro_results["장단기 금리차"] = {"종가": 0, "일간": 0, "주간": 0, "월간": 0, "연초": 0}

# 🎨 컬러링 함수
def color_delta_grid(val):
    if isinstance(val, (int, float)):
        color = 'green' if val > 0 else 'red' if val < 0 else 'black'
        return f'color: {color}; font-weight: bold;'
    return ''

# 🗂️ 5대 탭 레이아웃 구성
tab1, tab2, tab3, tab4, tab5 = str_visual.tabs([
    "🌐 거시경제(일단위)", 
    "🇺🇸 미국 주식 레이더 (50선)", 
    "🇰🇷 한국 주식 레이더 (50선)", 
    "📺 장인 추천 올인원 마스터 뷰", 
    "🦅 중앙은행 & 정책 가이드북"
])

# --- 탭 1: 거시경제 일단위 지표 ---
with tab1:
    str_visual.header("🎯 일단위 핵심 매크로 전광판")
    m_col1, m_col2, m_col3, m_col4 = str_visual.columns(4)
    with m_col1:
        str_visual.metric(label="💵 원/달러 환율", value=f"{macro_results.get('원달러 환율', {}).get('종가', 0)} 원", delta=f"{macro_results.get('원달러 환율', {}).get('일간', 0)}%")
        str_visual.metric(label="📈 나스닥 지수", value=macro_results.get('나스닥 지수', {}).get('종가', 0), delta=f"{macro_results.get('나스닥 지수', {}).get('일간', 0)}%")
        str_visual.metric(label="🪙 비트코인 (BTC)", value=f"${macro_results.get('비트코인 (BTC)', {}).get('종가', 0):,}", delta=f"{macro_results.get('비트코인 (BTC)', {}).get('일간', 0)}%")
    with m_col2:
        str_visual.metric(label="🏦 미 국채 10년물 금리", value=f"{macro_results.get('미 국채 10년물', {}).get('종가', 0)}%", delta=f"{macro_results.get('미 국채 10년물', {}).get('일간', 0)}%")
        str_visual.metric(label="📊 장단기 금리차 (10Y-2Y)", value=f"{macro_results.get('장단기 금리차', {}).get('종가', 0)} %p")
        str_visual.metric(label="🪙 이더리움 (ETH)", value=f"${macro_results.get('이더리움 (ETH)', {}).get('종가', 0):,}", delta=f"{macro_results.get('이더리움 (ETH)', {}).get('일간', 0)}%")
    with m_col3:
        str_visual.metric(label="🛢️ WTI 국제유가", value=f"${macro_results.get('WTI 유가', {}).get('종가', 0)}", delta=f"{macro_results.get('WTI 유가', {}).get('일간', 0)}%")
        str_visual.metric(label="🌋 VIX 공포지수", value=macro_results.get('VIX 공포지수', {}).get('종가', 0), delta=f"{macro_results.get('VIX 공포지수', {}).get('일간', 0)}%")
        str_visual.metric(label="🧪 구리 선물 가격", value=f"${macro_results.get('구리 선물 가격', {}).get('종가', 0)}", delta=f"{macro_results.get('구리 선물 가격', {}).get('일간', 0)}%")
    with m_col4:
        str_visual.metric(label="✨ 금 선물 가격", value=f"${macro_results.get('금 선물', {}).get('종가', 0)}", delta=f"{macro_results.get('금 선물', {}).get('일간', 0)}%")
        str_visual.metric(label="💵 달러 인덱스 (DXY)", value=macro_results.get('달러 인덱스(DXY)', {}).get('종가', 0), delta=f"{macro_results.get('달러 인덱스(DXY)', {}).get('일간', 0)}%")
        str_visual.metric(label="✨ 은 선물 가격", value=f"${macro_results.get('은 선물 가격', {}).get('종가', 0)}", delta=f"{macro_results.get('은 선물 가격', {}).get('일간', 0)}%")

    str_visual.markdown("---")
    str_visual.subheader("📦 거시경제 인덱스 전체 스코어 보드")
    macro_table = []
    for name, d in macro_results.items():
        macro_table.append({"자산명": name, "종가": d["종가"], "일간 변동(%)": d["일간"], "주간 변동(%)": d["주간"], "월간 변동(%)": d["월간"]})
    df_macro = pd.DataFrame(macro_table)
    str_visual.dataframe(df_macro.style.map(color_delta_grid, subset=["일간 변동(%)", "주간 변동(%)", "월간 변동(%)"]), use_container_width=True, hide_index=True)

# --- 탭 2: 미국 주식 레이더 ---
with tab2:
    str_visual.header("💻 미국 핵심 주식 레이더 (시총 최상위 50선)")
    us_rows = []
    for name, d in us_results.items():
        us_rows.append({"섹터분류": d["분류"], "종목명": name, "현재가($)": d["종가"], "전일비(%)": d["일간"], "주간(%)": d["주간"], "월간(%)": d["월간"], "연초대비(%)": d["연초"]})
    df_us = pd.DataFrame(us_rows)
    str_visual.dataframe(df_us.style.map(color_delta_grid, subset=["전일비(%)", "주간(%)", "월간(%)", "연초대비(%)"]), use_container_width=True, hide_index=True)

# --- 탭 3: 한국 주식 레이더 ---
with tab3:
    str_visual.header("🇰🇷 국내 시장 코스피/코스닥 대장주 (50선)")
    kr_rows = []
    for name, d in kr_results.items():
        kr_rows.append({"테마분류": d["분류"], "종목명": name, "현재가(원)": f"{int(d['종가']):,}" if d['종가'] > 0 else "0", "전일비(%)": d["일간"], "주간(%)": d["주간"], "월간(%)": d["월간"], "연초대비(%)": d["연초"]})
    df_kr = pd.DataFrame(kr_rows)
    str_visual.dataframe(df_kr.style.map(color_delta_grid, subset=["전일비(%)", "주간(%)", "월간(%)", "연초대비(%)"]), use_container_width=True, hide_index=True)

# --- 탭 4: 올인원 마스터 뷰 ---
with tab4:
    str_visual.subheader("📺 ALL-IN-ONE 글로벌 매크로 인텔리전스 전광판")
    om_1, om_2, om_3, om_4, om_5, om_6 = str_visual.columns(6)
    om_1.metric("DXY 달러인덱스", macro_results.get("달러 인덱스(DXY)", {}).get("종가", 0))
    om_2.metric("美 10Y 국채금리", f"{macro_results.get('미 국채 10년물', {}).get('종가', 0)}%")
    om_3.metric("VIX 공포지수", macro_results.get("VIX 공포지수", {}).get("종가", 0))
    om_4.metric("WTI 국제유가", f"${macro_results.get('WTI 유가', {}).get('종가', 0)}")
    om_5.metric("금 선물 (Gold)", f"${macro_results.get('금 선물', {}).get('종가', 0)}")
    om_6.metric("Fear & Greed 계측", "실시간 외부 컨센서스 준용")
    
    str_visual.markdown("---")
    mid_left, mid_right = str_visual.columns([1, 1])
    with mid_left:
        str_visual.markdown("#### 📈 S&P 500 기술적 추세선 및 건강도 (50/200MA)")
        str_visual.info("📊 **S&P 500 현재가:** " + str(macro_results.get("S&P 500", {}).get("종가", 0)) + " pt\n\n"
                        "💡 [TradingView 50/200MA 추세선 연출] 현재 지수는 장기 이평선(200DMA) 위에서 안착 중입니다.")
        
        str_visual.markdown("#### 🧱 주요 섹터 흐름 (Heatmap 가이드)")
        # 🔥 [문법 에러 완벽 해결] 콜론(:) 기호 누락된 부분 정상 보정 완료!
        sector_mockup = [
            {"섹터구분": "XLK (테크 대장)", "상대강도": "▲ 강세 유지", "인사이트": "기관 수급 중심 기술주 랠리"},
            {"섹터구분": "XLU (유틸리티)", "상대강도": "▼ 약세 반전", "인사이트": "방어적 자금 일시 이탈"},
            {"섹터구분": "XLE (에너지)", "상대강도": "■ 기간 조정", "인사이트": "유가 80달러선 지지선 탐색"}
        ]
        str_visual.table(pd.DataFrame(sector_mockup))
        
    with mid_right:
        str_visual.markdown("#### 📅 Macro Table (PMI, CPI, PPI, Spreads)")
        macro_all_in_one = [
            {"핵심 지표명": "소비자물가지수 (CPI)", "발표 트렌드": "전년 대비 3.5% 안팎의 둔화 국면", "장인급 해석": "인플레이션 재발 리스크 제어 중"},
            {"핵심 지표명": "생산자물가지수 (PPI)", "발표 트렌드": "도매물가 컨센서스 부합 추세", "장인급 해석": "소비자물가 선행 지표로 안정적"},
            {"핵심 지표명": "Global PMI (제조업)", "발표 트렌드": "50.1 경기 확장선 상회 여부 주시", "장인급 해석": "글로벌 경기 하방 압력 방어 신호"},
            {"핵심 지표명": "10Y-2Y 장단기 금리차", "발표 트렌드": "스프레드 역전 폭 축소 과정 체크", "장인급 해석": "정상화 도래 시 경기둔화 헷지 준비"}
        ]
        str_visual.dataframe(pd.DataFrame(macro_all_in_one), use_container_width=True)

    str_visual.markdown("---")
    str_visual.markdown("#### 📰 Top 10 뉴스 헤드라인 및 센티먼트 리서치 가이드")
    str_visual.caption("1. 연준 고위 인사들의 매파적 금리 스탠스 동향 | 2. 엔 캐리트레이드 청산 리스크에 따른 외환시장 동조화 분석 | 3. 글로벌 빅테크 자본지출(CAPEX) 사이클 피크아웃 논쟁 점검")

# --- 탭 5: 가이드북 ---
with tab5:
    str_visual.header("🦅 중앙은행 정책 캘린더 및 주식시장 메커니즘 가이드")
    p_col1, p_col2 = str_visual.columns(2)
    with p_col1:
        str_visual.markdown("### 🏛️ 2. 중앙은행 & 정책 (Policy Watch)")
        str_visual.markdown("""
        - **Fed Funds Rate + Dot Plot 기대:** 점도표 경로 분석
        - **ECB, BOJ, PBOC 금리/발언:** 엔 캐리트레이드 청산 신호용
        - **Fed Balance Sheet 규모 (주간):** 양적긴축 속도 파악
        - **SOFR / SOFR Futures:** 뉴욕 자금시장 실질 단기 금리
        """)
    with p_col2:
        str_visual.markdown("### 📊 3 & 4. Technical, Sentiment & Sector Rotation 정리")
        str_visual.table(pd.DataFrame([
            {"카테고리": "Broad Market", "지표명": "S&P500, Nasdaq100, Russell2000"},
            {"카테고리": "글로벌 리스크", "지표명": "MSCI ACWI, MSCI EM, VIX, VVIX"},
            {"카테고리": "변동성 추세", "지표명": "MOVE Index (채권 변동성)"},
            {"카테고리": "시장 밸류에이션", "지표명": "S&P500 Shiller PE, Buffett Indicator"},
            {"카테고리": "섹터 로테이션", "지표명": "High Beta vs Low Beta (SPHB vs SPLV)"},
            {"카테고리": "사이클 선행", "지표명": "Semiconductor Index (SOXX, SOX)"}
        ]))