import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import math
import random

# Page Configuration
st.set_page_config(
    page_title="서울시 공영주차장 스마트 안내 시스템",
    page_icon="🅿️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for UI polish
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        font-size: 1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2563EB;
    }
</style>
""", unsafe_allow_dict Amsterdam=True)

# Data Loading & Preprocessing
@st.cache_data
def load_data(file_path="서울시 공영주차장 안내 정보.csv"):
    encodings = ['utf-8', 'cp949', 'euc-kr', 'utf-8-sig']
    df = None
    
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            break
        except Exception:
            continue
            
    if df is None:
        st.error("파일을 로드할 수 없습니다. 파일 경로 및 인코딩을 확인해주세요.")
        return pd.DataFrame()

    # Standardize column names from various Open Data formats
    col_mapping = {
        'PKNAM': '주차장명',
        'ADDR': '주소',
        'TP_NAME': '주차장구분',
        'PAY_YN': '유무료구분',
        'RATES': '기본주차요금',
        'TIME_RATE': '기본주차시간',
        'ADD_RATES': '추가단위요금',
        'ADD_TIME_RATE': '추가단위시간',
        'DAY_MAXIMUM': '일최고요금',
        'LAT': '위도',
        'LNG': '경도',
        'LOT': '경도',
        '주차장 위치 좌표 위도': '위도',
        '주차장 위치 좌표 경도': '경도',
        '기본 주차 요금': '기본주차요금',
        '기본 주차 시간(분)': '기본주차시간',
        '추가 단위 요금': '추가단위요금',
        '추가 단위 시간(분)': '추가단위시간',
        '일 시간 구분의 일 최대 요금': '일최고요금',
        '유무료구분명': '유무료구분',
        '주차장종류명': '주차장구분',
        '주차면수': '구획수'
    }
    
    df = df.rename(columns=col_mapping)
    
    # Fill missing column fallbacks
    required_cols = ['주차장명', '주소', '자치구', '기본주차요금', '기본주차시간', 
                     '추가단위요금', '추가단위시간', '일최고요금', '위도', '경도', '구획수', '유무료구분']
    for col in required_cols:
        if col not in df.columns:
            df[col] = np.nan

    # Extract district (자치구) from address if missing
    if df['자치구'].isna().all() and '주소' in df.columns:
        df['자치구'] = df['주소'].astype(str).str.extract(r'서울시?\s*([\uac00-\ud7a3]+구)')[0]
        df['자치구'] = df['자치구'].fillna(df['주소'].astype(str).str.extract(r'([\uac00-\ud7a3]+구)')[0])
    df['자치구'] = df['자치구'].fillna('기타/미분류')

    # Data type cleaning
    numeric_cols = ['기본주차요금', '기본주차시간', '추가단위요금', '추가단위시간', '일최고요금', '위도', '경도', '구획수']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
        
    df['주차장명'] = df['주차장명'].fillna('이름 없음')
    df['주소'] = df['주소'].fillna('주소 정보 없음')
    df['유무료구분'] = df['유무료구분'].fillna('유료')

    return df

# Fee Calculation Function
def calculate_fee(row, duration_minutes):
    pay_type = str(row['유무료구분'])
    if '무료' in pay_type and '유료' not in pay_type:
        return 0
    if duration_minutes <= 0:
        return 0
        
    base_fee = row['기본주차요금']
    base_time = row['기본주차시간'] if row['기본주차시간'] > 0 else 30
    add_fee = row['추가단위요금']
    add_time = row['추가단위시간'] if row['추가단위시간'] > 0 else 10
    day_max = row['일최고요금']

    if duration_minutes <= base_time:
        total_fee = base_fee
    else:
        extra_time = duration_minutes - base_time
        extra_units = math.ceil(extra_time / add_time)
        total_fee = base_fee + (extra_units * add_fee)

    if day_max > 0 and total_fee > day_max:
        total_fee = day_max

    return int(total_fee)

# Main Application
def main():
    st.markdown('<div class="main-title">🅿️ 서울시 공영주차장 스마트 안내 웹앱</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">서울시 공영주차장 위치, 예상 요금 계산, 최저가 추천 및 통계를 한눈에 확인하세요.</div>', unsafe_allow_html=True)

    # Load Data
    data = load_data()
    if data.empty:
        st.warning("데이터셋을 불러올 수 없어 앱을 중단합니다.")
        return

    # Sidebar Controls
    st.sidebar.header("🔍 검색 및 필터 옵션")
    
    # District Filter
    districts = ['전체'] + sorted([d for d in data['자치구'].unique() if d != '기타/미분류'])
    selected_district = st.sidebar.selectbox("자치구 선택", districts)
    
    # Free/Paid Filter
    pay_filter = st.sidebar.multiselect("유/무료 구분", options=['유료', '무료'], default=['유료', '무료'])
    
    # Search Keyword
    search_keyword = st.sidebar.text_input("주차장명 또는 주소 검색", "").strip()

    # Filter Applied
    filtered_df = data.copy()
    if selected_district != '전체':
        filtered_df = filtered_df[filtered_df['자치구'] == selected_district]
    
    if pay_filter:
        conditions = [filtered_df['유무료구분'].astype(str).str.contains(p) for p in pay_filter]
        filtered_df = filtered_df[np.logical_or.reduce(conditions)]
        
    if search_keyword:
        filtered_df = filtered_df[
            filtered_df['주차장명'].str.contains(search_keyword, case=False, na=False) |
            filtered_df['주소'].str.contains(search_keyword, case=False, na=False)
        ]

    # App Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📍 주차장 지도 & 목록", 
        "💰 예상 주차 요금 계산", 
        "🏷️ 최저가 / 추천 주차장", 
        "🎲 랜덤 추천 (오늘 어디?)", 
        "📊 통계 & 그래프"
    ])

    # ----------------------------------------------------
    # TAB 1: 지도 및 목록
    # ----------------------------------------------------
    with tab1:
        st.subheader("📍 주차장 위치 및 조건 검색")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("검색된 주차장 수", f"{len(filtered_df):,} 개")
        col2.metric("총 주차 구획수", f"{int(filtered_df['구획수'].sum()):,} 면")
        col3.metric("평균 기본요금", f"{int(filtered_df['기본주차요금'].mean()):,} 원")
        col4.metric("평균 기본시간", f"{int(filtered_df['기본주차시간'].mean())} 분")

        st.markdown("---")

        # Map Plotting
        map_df = filtered_df[(filtered_df['위도'] > 33) & (filtered_df['위도'] < 39) & 
                             (filtered_df['경도'] > 124) & (filtered_df['경도'] < 132)]

        if not map_df.empty:
            fig_map = px.scatter_mapbox(
                map_df,
                lat="위도",
                lon="경도",
                hover_name="주차장명",
                hover_data={"주소": True, "기본주차요금": ":,원", "기본주차시간": ":분", "일최고요금": ":,원"},
                color="유무료구분",
                size="구획수",
                size_max=18,
                zoom=11,
                height=500
            )
            fig_map.update_layout(mapbox_style="open-street-map")
            fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("지도에 표시할 좌표 데이터가 없습니다.")

        st.subheader("📋 검색 결과 목록")
        
        display_cols = ['주차장명', '자치구', '주소', '구획수', '유무료구분', '기본주차요금', '기본주차시간', '추가단위요금', '추가단위시간', '일최고요금']
        existing_display_cols = [c for c in display_cols if c in filtered_df.columns]
        
        st.dataframe(filtered_df[existing_display_cols], use_container_width=True, height=350)

        # CSV Download Button
        csv_data = filtered_df[existing_display_cols].to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(
            label="📥 현재 검색 결과 CSV 다운로드",
            data=csv_data,
            file_name="서울시_공영주차장_검색결과.csv",
            mime="text/csv"
        )

    # ----------------------------------------------------
    # TAB 2: 예상 주차요금 계산기
    # ----------------------------------------------------
    with tab2:
        st.subheader("💰 예상 주차 요금 계산기")
        st.write("입력하신 예상 주차 시간에 따른 주차장별 예상 요금을 계산해 드립니다.")

        col_time1, col_time2 = st.columns(2)
        with col_time1:
            hours = st.number_input("주차 시간 (시간)", min_value=0, max_value=72, value=2, step=1)
        with col_time2:
            minutes = st.number_input("주차 분 (분)", min_value=0, max_value=59, value=0, step=10)

        total_input_minutes = (hours * 60) + minutes

        if total_input_minutes <= 0:
            st.warning("주차 시간을 1분 이상 입력해 주세요.")
        else:
            calc_df = filtered_df.copy()
            calc_df['예상요금'] = calc_df.apply(lambda r: calculate_fee(r, total_input_minutes), axis=1)
            
            # Sort by fee ascending
            calc_df = calc_df.sort_values(by=['예상요금', '기본주차요금'])

            st.success(f"⏱️ **총 주차 시간: {hours}시간 {minutes}분 ({total_input_minutes}분)** 기준 요금 계산 결과")

            top_cheapest = calc_df.head(5)
            st.markdown("#### 💡 이 지역에서 가장 저렴한 TOP 5 주차장")
            
            for idx, row in top_cheapest.iterrows():
                with st.expander(f"🥇 [{row['예상요금']:,}원] {row['주차장명']} ({row['자치구']})"):
                    st.write(f"- **주소:** {row['주소']}")
                    st.write(f"- **기본 요금:** {int(row['기본주차요금']):,}원 / {int(row['기본주차시간'])}분")
                    st.write(f"- **추가 요금:** {int(row['추가단위요금']):,}원 / {int(row['추가단위시간'])}분당")
                    st.write(f"- **일 최대 요금:** {int(row['일최고요금']):,}원")

            st.markdown("#### 📊 계산 결과 상세 테이블")
            show_calc_cols = ['주차장명', '예상요금', '자치구', '주소', '기본주차요금', '기본주차시간', '추가단위요금', '추가단위시간', '일최고요금']
            st.dataframe(calc_df[[c for c in show_calc_cols if c in calc_df.columns]], use_container_width=True)

    # ----------------------------------------------------
    # TAB 3: 최저가 / 혜택 주차장 추천
    # ----------------------------------------------------
    with tab3:
        st.subheader("🏷️ 조건별 가성비 추천 주차장")

        col_rec1, col_rec2 = st.columns(2)

        with col_rec1:
            st.markdown("### 🆓 무료 주차장")
            free_df = filtered_df[filtered_df['유무료구분'].astype(str).str.contains('무료')]
            if not free_df.empty:
                st.dataframe(free_df[['주차장명', '자치구', '주소', '구획수']], use_container_width=True)
            else:
                st.info("선택한 조건에 해당하는 무료 주차장이 없습니다.")

        with col_rec2:
            st.markdown("### 💵 기본요금 최저가 TOP 10")
            cheapest_base = filtered_df[filtered_df['기본주차요금'] > 0].sort_values(by='기본주차요금').head(10)
            if not cheapest_base.empty:
                st.dataframe(cheapest_base[['주차장명', '자치구', '기본주차요금', '기본주차시간', '주소']], use_container_width=True)
            else:
                st.info("유료 주차장 정보가 없습니다.")

    # ----------------------------------------------------
    # TAB 4: 랜덤 추천
    # ----------------------------------------------------
    with tab4:
        st.subheader("🎲 행운의 주차장 랜덤 추천")
        st.write("목적지 근처 주차장을 어디로 가야 할지 고민될 때 원클릭으로 추천받아보세요!")

        if st.button("🎲 주차장 뽑기!", type="primary"):
            if not filtered_df.empty:
                random_lot = filtered_df.sample(n=1).iloc[0]
                
                st.balloons()
                st.markdown(f"### 🎉 추천 주차장: **{random_lot['주차장명']}**")
                
                rc1, rc2, rc3 = st.columns(3)
                rc1.metric("자치구", random_lot['자치구'])
                rc2.metric("기본요금", f"{int(random_lot['기본주차요금']):,} 원")
                rc3.metric("기본시간", f"{int(random_lot['기본주차시간'])} 분")

                st.write(f"📍 **주소:** {random_lot['주소']}")
                st.write(f"🚘 **총 주차면수:** {int(random_lot['구획수'])} 면")
                
                # Single Marker Map
                if random_lot['위도'] > 0 and random_lot['경도'] > 0:
                    single_map_df = pd.DataFrame([random_lot])
                    fig_single = px.scatter_mapbox(
                        single_map_df,
                        lat="위도",
                        lon="경도",
                        hover_name="주차장명",
                        zoom=15,
                        height=350
                    )
                    fig_single.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
                    st.plotly_chart(fig_single, use_container_width=True)
            else:
                st.error("선택된 조건에 해당하는 주차장이 없어 추천할 수 없습니다.")

    # ----------------------------------------------------
    # TAB 5: 통계 및 그래프 분석
    # ----------------------------------------------------
    with tab5:
        st.subheader("📊 서울시 공영주차장 통계 분석")

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("##### 🏢 자치구별 주차장 보유 수")
            dist_counts = data['자치구'].value_counts().reset_index()
            dist_counts.columns = ['자치구', '주차장 수']
            fig_bar1 = px.bar(dist_counts, x='자치구', y='주차장 수', color='주차장 수', color_continuous_scale='Blues')
            st.plotly_chart(fig_bar1, use_container_width=True)

        with chart_col2:
            st.markdown("##### 💵 자치구별 평균 기본 주차요금")
            avg_fee = data.groupby('자치구')['기본주차요금'].mean().reset_index()
            fig_bar2 = px.bar(avg_fee, x='자치구', y='기본주차요금', color='기본주차요금', color_continuous_scale='Reds')
            st.plotly_chart(fig_bar2, use_container_width=True)

        st.markdown("##### 🚗 유/무료 주차장 비율")
        pay_counts = data['유무료구분'].value_counts().reset_index()
        pay_counts.columns = ['구분', '수량']
        fig_pie = px.pie(pay_counts, names='구분', values='수량', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)


if __name__ == '__main__':
    main()