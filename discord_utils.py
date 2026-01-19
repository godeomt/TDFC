import requests
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# 👇 수정된 부분: 안전하게 URL 가져오기
# ==========================================
def get_webhook_url():
    # 1. 클라우드 (Secrets) 시도
    try:
        if "DISCORD_WEBHOOK_URL" in st.secrets:
            return st.secrets["DISCORD_WEBHOOK_URL"]
    except FileNotFoundError:
        pass # 파일이 없으면(로컬이면) 그냥 무시하고 넘어감
    except Exception:
        pass # 다른 에러도 무시

    # 2. 로컬 (.env) 시도
    return os.getenv("DISCORD_WEBHOOK_URL")

def send_discord_message(text):
    webhook_url = get_webhook_url()
    
    if not webhook_url:
        return "❌ 오류: DISCORD_WEBHOOK_URL이 설정되지 않았습니다."

    data = {
        "content": text,
        "username": "태둥포스 알리미",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/3081/3081840.png"
    }

    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code == 204:
            return "성공"
        else:
            return f"전송 실패: {response.status_code} - {response.text}"
    except Exception as e:
        return f"에러 발생: {e}"