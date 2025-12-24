import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# API 설정
API_KEY = 'AIzaSyCAKT_zkg8_QMYdC5k4GBzGyTUGhJYywiA'
youtube = build('youtube', 'v3', developerKey=API_KEY)

# 화면 구성 (왼쪽 사이드바)
st.set_page_config(page_title="유튜브 트렌드 분석기")
st.title("📊 유튜브 트렌드 분석기")

with st.sidebar:
    st.header("🔍 검색 조건 설정")
    keyword = st.text_input("1. 분석할 키워드", placeholder="예: 해외감동사연")
    
    date_label = st.selectbox("2. 업로드 날짜", ["10일 이내", "1달 이내", "3개월 이내"])
    days = 10 if date_label == "10일 이내" else 30 if date_label == "1달 이내" else 90
    
    dur_label = st.selectbox("3. 영상 길이 선택", ["10분 이내", "20분 이내", "20분 초과"])
    duration_map = {"10분 이내": "medium", "20분 이내": "medium", "20분 초과": "long"}
    
    min_views = st.number_input("4. 최소 조회수", min_value=0, value=10000, step=5000)
    max_results = st.slider("5. 가져올 영상 개수", 1, 50, 10)

# 분석 시작 버튼
if st.button("트렌드 분석 시작 🚀"):
    if not keyword:
        st.warning("키워드를 입력해주세요!")
    else:
        published_after = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
        
        # API 호출
        search_response = youtube.search().list(
            q=keyword, part='snippet', maxResults=max_results,
            publishedAfter=published_after, type='video',
            videoDuration=duration_map[dur_label], order='viewCount'
        ).execute()

        results = []
        for item in search_response['items']:
            video_id = item['id']['videoId']
            video_info = youtube.videos().list(part='statistics', id=video_id).execute()
            views = int(video_info['items'][0]['statistics'].get('viewCount', 0))
            
            if views >= min_views:
                results.append({
                    "제목": item['snippet']['title'],
                    "조회수": f"{views:,}회",
                    "링크": f"https://www.youtube.com/watch?v={video_id}",
                    "업로드일": item['snippet']['publishedAt'][:10]
                })

        if results:
            df = pd.DataFrame(results)
            st.success(f"총 {len(results)}개의 영상을 찾았습니다!")
            st.dataframe(df) # 화면에 표 형태로 출력
            
            # 엑셀 다운로드 버튼
            st.download_button(label="엑셀 파일로 저장", data=df.to_csv(index=False).encode('utf-8-sig'),
                               file_name=f"{keyword}_분석결과.csv", mime='text/csv')
        else:
            st.error("조건에 맞는 영상이 없습니다.")