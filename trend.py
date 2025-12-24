import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# API 설정
API_KEY = 'AIzaSyCAKT_zkg8_QMYdC5k4GBzGyTUGhJYywiA'
youtube = build('youtube', 'v3', developerKey=API_KEY)

st.set_page_config(page_title="유튜브 프로 분석기", layout="wide")
st.title("🚀 유튜브 트렌드 프로 분석기")

with st.sidebar:
    st.header("🔍 상세 조건")
    keyword = st.text_input("분석할 키워드")
    date_choice = st.selectbox("업로드 날짜", ["10일 이내", "1달 이내", "3개월 이내"])
    days = 10 if date_choice == "10일 이내" else 30 if date_choice == "1달 이내" else 90
    min_views = st.number_input("최소 조회수", value=10000)
    max_results = st.slider("가져올 영상 개수", 1, 20, 5)

if st.button("심층 분석 시작! ✨"):
    published_after = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
    
    # 1. 영상 검색
    search_res = youtube.search().list(
        q=keyword, part='snippet', maxResults=max_results,
        publishedAfter=published_after, type='video', order='viewCount'
    ).execute()

    for item in search_res['items']:
        v_id = item['id']['videoId']
        
        # 2. 영상 상세 정보 (설정, 조회수 등)
        v_res = youtube.videos().list(part='snippet,statistics', id=v_id).execute()
        v_info = v_res['items'][0]
        title = v_info['snippet']['title']
        desc = v_info['snippet']['description']
        views = int(v_info['statistics'].get('viewCount', 0))
        thumb = v_info['snippet']['thumbnails']['medium']['url']

        if views >= min_views:
            st.divider()
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image(thumb, use_container_width=True)
                st.write(f"🔗 [영상 바로가기](https://www.youtube.com/watch?v={v_id})")
                st.metric("조회수", f"{views:,}회")

            with col2:
                st.subheader(title)
                with st.expander("📝 동영상 설명 보기"):
                    st.write(desc)
                
                # 3. 인기 댓글 TOP 5 가져오기
                try:
                    c_res = youtube.commentThreads().list(
                        part='snippet', videoId=v_id, maxResults=5, order='relevance'
                    ).execute()
                    st.write("💬 **인기 댓글 TOP 5**")
                    for c in c_res['items']:
                        comment = c['snippet']['topLevelComment']['snippet']['textDisplay']
                        st.caption(f"• {comment}")
                except:
                    st.write("⚠️ 댓글 기능을 지원하지 않는 영상입니다.")