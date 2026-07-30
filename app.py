import streamlit as st
import random

# Page Config
st.set_page_config(
    page_title="✨ MBTI 여행지 추천소 ✨",
    page_icon="✈️",
    layout="centered"
)

# 귀여운 파스텔톤 커스텀 CSS 적용
st.markdown("""
<style>
    /* 전체 배경 및 폰트 */
    .stApp {
        background-color: #FFF9F5;
        font-family: 'Pretendard', sans-serif;
    }
    
    /* 타이틀 스타일ing */
    .main-title {
        text-align: center;
        color: #FF7B9C;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 5px;
    }
    .sub-title {
        text-align: center;
        color: #6C5CE7;
        font-size: 1.1rem;
        margin-bottom: 25px;
    }

    /* 카드 스타일 */
    .recommend-card {
        background-color: #FFFFFF;
        padding: 24px;
        border-radius: 20px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.05);
        border: 2px solid #FFEAA7;
        margin-bottom: 20px;
    }
    .card-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2D3436;
    }
    .tag {
        display: inline-block;
        background-color: #FFEAA7;
        color: #D63031;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: bold;
        margin-right: 5px;
    }
    .tip-box {
        background-color: #E8F8F5;
        border-left: 5px solid #1ABC9C;
        padding: 12px;
        border-radius: 8px;
        margin-top: 15px;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)

# MBTI별 추천 여행지 데이터베이스
mbti_travel_data = {
    "ISTJ": {
        "title": "🇯🇵 정갈함과 규칙이 느껴지는 '교토'",
        "subtitle": "계획대로 착착 진행되는 완벽한 여행",
        "tag": "역사 & 유적, 정갈함, 철저한 계획",
        "image": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800",
        "description": "치안이 좋고 대중교통이 체계적인 교토는 ISTJ에게 마음의 평화를 제공합니다. 고즈넉한 사찰과 정갈한 음식을 즐겨보세요.",
        "tips": "🕒 인기 관광지는 아침 일찍 방문해야 혼잡을 피할 수 있어요!"
    },
    "ISFJ": {
        "title": "🇦🇹 다정함과 따뜻함이 가득한 '비엔나'",
        "subtitle": "편안하고 안전한 예술과 클래식의 도시",
        "tag": "안전, 클래식 음악, 미술관 Tour",
        "image": "https://images.unsplash.com/photo-1516550893923-42d28e5677af?w=800",
        "description": "배려심 깊고 안정적인 분위기를 선사하는 비엔나입니다. 고풍스러운 카페에서 비엔나 커피 한 잔과 함께 오케스트라 연주를 즐겨보세요.",
        "tips": "☕ 궁전 근처 전통 카페에서 비엔나 커피(멜랑쥐)를 드셔보세요!"
    },
    "INFJ": {
        "title": "🇨🇭 깊은 영감을 주는 '체르마트'",
        "subtitle": "웅장한 대자연 속 혼자만의 힐링 타임",
        "tag": "대자연, 사색, 영감",
        "image": "https://images.unsplash.com/photo-1530122037265-a5f1f91d3b99?w=800",
        "description": "마테호른의 웅장한 풍경 속에서 생각을 정리하기 좋은 장소입니다. 친환경 청정 마을에서 한적하게 산책을 즐겨보세요.",
        "tips": "🚂 하이킹 스틱을 챙겨 가벼운 산책 코스를 걸어보세요!"
    },
    "INTJ": {
        "title": "🇮🇸 지적 호기심을 자극하는 '아이슬란드'",
        "subtitle": "지구 같지 않은 경이로운 탐험의 연속",
        "tag": "오로라, 로드트립, 탐험",
        "image": "https://images.unsplash.com/photo-1504893524553-b855bce32c67?w=800",
        "description": "화산, 빙하, 오로라까지! 주체적이고 효율적인 동선 계획을 통해 대자연의 경이로움을 만끽할 수 있습니다.",
        "tips": "🚗 렌터카 이용 시 기상 상황 앱(Vedur)을 꼭 확인하세요!"
    },
    "ISTP": {
        "title": "🇳🇿 스릴 만점 액티비티 천국 '퀸스타운'",
        "subtitle": "마음이 시키는 대로, 자유로운 레포츠",
        "tag": "액티비티, 번지점프, 자유",
        "image": "https://images.unsplash.com/photo-1507699622108-4be3abd695ad?w=800",
        "description": "번지점프, 스카이다이빙, 젯보드 등 현실의 스트레스를 날려버릴 액티비티가 가득한 도시입니다.",
        "tips": "🪂 인기 액티비티는 사전 예약이 필수입니다!"
    },
    "ISFP": {
        "title": "🇮🇩 여유와 예술이 흐르는 '발리 우붓'",
        "subtitle": "평화로운 자연 속 요가와 힐링 라이프",
        "tag": "힐링, 요가, 감성 카페",
        "image": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800",
        "description": "울창한 정글 속 리조트, 감성 카페, 요가 클래스까지! 쫓기지 않고 나만의 속도로 시간을 보낼 수 있습니다.",
        "tips": "🧘 아침 요가 클래스를 체험하며 하루를 시작해 보세요!"
    },
    "INFP": {
        "title": "🇨🇿 동화 속 세상을 걷는 '프라하'",
        "subtitle": "낭만과 감성이 넘치는 붉은 지붕의 도시",
        "tag": "낭만, 동화 속 풍경, 야경",
        "image": "https://images.unsplash.com/photo-1541849546-216549ae216d?w=800",
        "description": "골목길마다 감성이 묻어나는 프라하입니다. 카를교 위의 야경을 바라보며 나만의 문학적 영감을 떠올려보세요.",
        "tips": "🌉 해질녘 카를교에서 버스킹 음악을 들으며 야경을 관람해보세요!"
    },
    "INTP": {
        "title": "🇬🇧 박물관과 호기심의 도시 '런던'",
        "subtitle": "지적 지평을 넓혀주는 지식 여행",
        "tag": "무료 박물관, 역사, 지적 탐구",
        "image": "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=800",
        "description": "세계적인 박물관과 미술관이 대부분 무료! 관심 있는 주제를 깊이 파고들며 혼자 탐구하기에 최적입니다.",
        "tips": "🏛️ 대영박물관과 내셔널갤러리는 미리 동선을 계획하면 좋아요!"
    },
    "ESTP": {
        "title": "🇺🇸 화려함의 끝판왕 '라스베이거스'",
        "subtitle": "자극과 즐거움이 도사리는 잠들지 않는 도시",
        "tag": "화려한 쇼, 카지노, 핫플레이스",
        "image": "https://images.unsplash.com/photo-1605833559746-6d16002d8cc6?w=800",
        "description": "화려한 호텔 쇼, 밤문화, 그랜드 캐니언 투어까지! 한순간도 지루할 틈이 없는 액티브한 여행지입니다.",
        "tips": "🎰 벨라지오 분수 쇼는 무료이니 꼭 시간을 확인하고 감상하세요!"
    },
    "ESFP": {
        "title": "🇪🇸 흥과 열정이 넘치는 '바르셀로나'",
        "subtitle": "햇살 아래 즐기는 축제와 가우디의 예술",
        "tag": "해변, 타파스, 열정",
        "image": "https://images.unsplash.com/photo-1539037116277-4db20889f2d4?w=800",
        "description": "맛있는 타파스, 와인, 바르셀로네타 해변, 독창적인 가우디 건축물까지! 누구와 가도 신나게 즐길 수 있습니다.",
        "tips": "🍷 밤에는 타파스 바 투어로 현지 분위기를 느껴보세요!"
    },
    "ENFP": {
        "title": "🇹🇭 에너지와 다양성의 '방콕'",
        "subtitle": "언제나 새로운 이벤트가 기다리는 곳",
        "tag": "야시장, 스트리트 푸드, 활력",
        "image": "https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=800",
        "description": "시끌벅적한 야시장, 루프탑 바, 저렴한 맛집과 마사지까지! 매일 새로운 재미를 발견할 수 있습니다.",
        "tips": "🍹 짜오프라야 강변의 루프탑 바에서 노을을 감상해 보세요!"
    },
    "ENTP": {
        "title": "🇩🇪 혁신과 창의성의 도시 '베를린'",
        "subtitle": "트렌디한 예술과 자유로운 분위기",
        "tag": "클럽, 현대 미술, 자유로움",
        "image": "https://images.unsplash.com/photo-1560969184-10fe8719e047?w=800",
        "description": "스트리트 아트, 독립 갤러리, 세계적인 클럽 문화까지! 틀에 매이지 않는 사람들과 교류하기에 최적의 도시입니다.",
        "tips": "🎨 이스트 사이드 갤러리 벼룩시장에서 유니크한 템을 찾아보세요!"
    },
    "ESTJ": {
        "title": "🇸🇬 완벽한 시스템과 효율의 '싱가포르'",
        "subtitle": "쾌적하고 알찬 최고급 도시 여행",
        "tag": "도심 힐링, 야경, 완벽한 치안",
        "image": "https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=800",
        "description": "깨끗하고 안전하며 효율적인 동선! 마리나 베이 샌즈부터 가든스 바이 더 베이까지 완벽한 일정을 짜기 쉽습니다.",
        "tips": "🌳 가든스 바이 더 베이 라이트 쇼 시간에 맞춰 방문해보세요!"
    },
    "ESFJ": {
        "title": "🇺🇸 따뜻한 햇살과 즐거움의 '하와이'",
        "subtitle": "소중한 사람들과 함께 만들어가는 추억",
        "tag": "휴양, 쇼핑, 드라이브",
        "image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800",
        "description": "친절한 알로하 정신, 눈부신 해변, 쇼핑 스팟! 가족, 친구, 연인과 함께 가면 만족도 200%인 휴양지입니다.",
        "tips": "🚗 72번 국도 해안 드라이브 코스를 강력 추천합니다!"
    },
    "ENFJ": {
        "title": "🇮🇹 아름다운 이야기와 예술 '피렌체'",
        "subtitle": "모두의 감동을 끌어내는 로맨틱 도시",
        "tag": "르네상스, 예술, 로맨틱",
        "image": "https://images.unsplash.com/photo-1543429776-2782fc8e1acd?w=800",
        "description": "르네상스 예술의 탄생지이자 피렌체 두오모 성당의 감동! 타인을 잘 챙기는 ENFJ가 함께 감동을 나누기 좋습니다.",
        "tips": "🌅 미켈란젤로 언덕에서 피렌체 시내 노을을 감상해 보세요!"
    },
    "ENTJ": {
        "title": "🇺🇸 세계의 중심, 트렌드를 이끄는 '뉴욕'",
        "subtitle": "끊임없이 도파민을 자극하는 대도시",
        "tag": "뮤지컬, 스카이라인, 비즈니스",
        "image": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=800",
        "description": "브로드웨이 뮤지컬, 센트럴 파크, 세계적인 미술관! 성공과 도전을 자극하는 에너지 넘치는 도시입니다.",
        "tips": "🎭 브로드웨이 데이티켓/로터리로 가성비 있게 뮤지컬을 즐기세요!"
    }
}

# --- UI 영역 ---

# 헤더
st.markdown("<div class='main-title'>✈️ 뺩뺩! MBTI 여행지 추천소 💖</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>나의 성향에 딱 맞는 맞춤형 여행지를 찾아볼까요?</div>", unsafe_allow_html=True)

# 탭 메뉴 구성
tab1, tab2 = st.tabs(["🎯 MBTI로 찾기", "❓ 내 MBTI 모르겠어요"])

# Tab 1: MBTI 선택 및 추천
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        mbti_list = list(mbti_travel_data.keys())
        selected_mbti = st.selectbox(
            "👉 당신의 MBTI를 선택해 주세요!",
            options=mbti_list,
            index=0
        )
    
    with col2:
        companion = st.selectbox(
            "👥 누구와 가시나요?",
            ["혼자서", "친구와", "연인과", "가족과"]
        )

    # 추천 버튼
    if st.button("✨ 추천 여행지 보러가기!", use_container_width=True):
        data = mbti_travel_data[selected_mbti]
        
        st.write("") # 간격
        
        # 카드 형태로 결과 출력
        st.markdown(f"""
        <div class="recommend-card">
            <div style="margin-bottom: 8px;">
                <span class="tag">{selected_mbti}</span>
                <span class="tag">동행: {companion}</span>
            </div>
            <div class="card-header">{data['title']}</div>
            <p style="color: #636E72; font-style: italic; margin-top: 4px;">"{data['subtitle']}"</p>
            <p style="margin-top: 15px; line-height: 1.6;">{data['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 이미지 출력
        st.image(data['image'], use_column_width=True, caption=f"✨ {data['title'].split()[-1]} 대표 풍경")
        
        # 꿀팁 박스
        st.markdown(f"""
        <div class="tip-box">
            <b>💡 여행 꿀팁!</b><br>{data['tips']}
        </div>
        """, unsafe_allow_html=True)
        
        st.balloons() # 축하 이펙트

# Tab 2: 간이 MBTI 미니 테스트
with tab2:
    st.subheader("🧩 퀵 MBTI 테스트 (30초 소요)")
    st.write("간단한 선택으로 나의 성향을 파악해 보세요!")
    
    q1 = st.radio("1. 주말에 나는?", ["사람들을 만나며 에너지를 얻는다 (E)", "집에서 혼자 쉬며 충전한다 (I)"])
    q2 = st.radio("2. 여행 계획을 짤 때?", ["일자별, 시간별로 구체적으로 짠다 (J)", "큰 틀만 잡고 당일 기분에 따라 움직인다 (P)"])
    
    if st.button("결과 확인하기"):
        res_e_i = "E" if "E" in q1 else "I"
        res_j_p = "J" if "J" in q2 else "P"
        
        st.info(f"💡 당신은 **{res_e_i}** 성향과 **{res_j_p}** 성향이 강하시네요! 탭 1에서 해당 문자가 들어간 MBTI를 선택해 보세요.")

# 푸터
st.markdown("---")
st.markdown("<p style='text-align: center; color: #888888; font-size: 0.8rem;'>Made with 💕 for Streamlit Cloud</p>", unsafe_allow_html=True)
