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
    st.header("🔍 상세 조건 설정")
    keyword = st.text_input("1. 분석할 키워드", placeholder="예: 해외감동사연")
    
    date_choice = st.selectbox("2. 업로드 날짜", ["10일 이내", "1달 이내", "3개월 이내"])
    days = 10 if date_choice == "10일 이내" else 30 if date_choice == "1달 이내" else 90
    
    # 누락되었던 영상 길이 선택 기능 복구
    dur_label = st.selectbox("3. 영상 길이 선택", ["10분 이내", "20분 이내", "20분 초과"])
    duration_map = {"10분 이내": "medium", "20분 이내": "medium", "20분 초과": "long"}
    
    min_views = st.number_input("4. 최소 조회수", value=10000, step=5000)
    max_results = st.slider("5. 가져올 영상 개수", 1, 20, 5)

if st.button("심층 분석 시작! ✨"):
    if not keyword:
        st.warning("키워드를 입력해주세요!")
    else:
        published_after = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
        
        # 1. 영상 검색 (영상 길이 조건 추가됨)
        search_res = youtube.search().list(
            q=keyword, part='snippet', maxResults=max_results,
            publishedAfter=published_after, type='video', 
            videoDuration=duration_map[dur_label], order='viewCount'
        ).execute()

        if not search_res.get('items'):
            st.error("조건에 맞는 영상이 없습니다.")
        
        for item in search_res['items']:
            v_id = item['id']['videoId']
            
            # 2. 영상 상세 정보
            v_res = youtube.videos().list(part='snippet,statistics', id=v_id).execute()
            v_info = v_res['items'][0]
            title = v_info['snippet']['title']
            desc = v_info['snippet']['description']
            views = int(v_info