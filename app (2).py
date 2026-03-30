import streamlit as st
import time
import os
import random
from gtts import gTTS
from io import BytesIO

# --- 0. 系統配置 ---
st.set_page_config(
    page_title="阿美語 - 生活篇", 
    page_icon="🗣️", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# --- CSS 視覺魔法 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&family=Noto+Sans+TC:wght@400;700&display=swap');

    .stApp { 
        background-color: #0B0E14;
        background-image: radial-gradient(circle at 50% 0%, #1A237E 0%, #0B0E14 80%);
        font-family: 'Noto Sans TC', sans-serif;
        color: #E0F7FA;
    }
    
    .header-container {
        background: rgba(255, 111, 0, 0.1);
        border: 1px solid #FFAB40;
        box-shadow: 0 0 15px rgba(255, 171, 64, 0.3);
        border-radius: 15px;
        padding: 30px;
        text-align: center;
        margin-bottom: 40px;
        backdrop-filter: blur(10px);
    }
    
    .main-title {
        font-family: 'Roboto Mono', monospace;
        color: #FFAB40;
        font-size: 32px;
        font-weight: 700;
        letter-spacing: 2px;
        text-shadow: 0 0 10px #FFAB40;
        margin: 0;
    }
    
    .sub-title { color: #B2EBF2; font-size: 18px; margin-top: 10px; }

    .word-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 15px 5px;
        text-align: center;
        border: 1px solid rgba(255, 171, 64, 0.2);
        margin-bottom: 10px;
    }
    .amis-word { font-size: 16px; font-weight: 700; color: #FFFFFF; font-family: 'Roboto Mono', monospace; }
    .zh-word { font-size: 13px; color: #FFAB40; }

    .sentence-box {
        background: linear-gradient(90deg, rgba(255,171,64,0.1) 0%, rgba(0,0,0,0) 100%);
        border-left: 4px solid #00E5FF;
        padding: 15px;
        margin-bottom: 15px;
        border-radius: 0 10px 10px 0;
    }
    .sentence-amis { font-size: 18px; color: #00E5FF; font-weight: 700; margin-bottom: 5px; }
    .sentence-zh { font-size: 14px; color: #B2EBF2; }

    /* Tab 樣式修正 */
    .stTabs [data-baseweb="tab"] {
        color: #FFFFFF !important; 
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 10px 30px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFAB40 !important;
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 資料設定 ---
VOCABULARY = [
    {"amis": "Cima", "zh": "誰", "emoji": "❓"},
    {"amis": "ngangan", "zh": "名字", "emoji": "🏷️"},
    {"amis": "kako", "zh": "我", "emoji": "🙋‍♂️"},
    {"amis": "kora", "zh": "那個", "emoji": "👈"},
    {"amis": "fafahiyan", "zh": "女生", "emoji": "👩"},
    {"amis": "cingra", "zh": "他/她", "emoji": "👤"},
    {"amis": "widang", "zh": "朋友", "emoji": "🤝"},
    {"amis": "ako", "zh": "我的", "emoji": "🎒"},
    {"amis": "Nga’ay ho", "zh": "你好", "emoji": "👋"},
    {"amis": "Icowa", "zh": "在哪裡", "emoji": "📍"},
    {"amis": "niyaro’", "zh": "部落", "emoji": "🏡"},
    {"amis": "Posong", "zh": "台東", "emoji": "☀️"},
    {"amis": "Kakacawan", "zh": "長濱", "emoji": "⛰️"},
    {"amis": "tayal", "zh": "工作", "emoji": "🔨"},
    {"amis": "singsi", "zh": "老師", "emoji": "👨‍🏫"},
    {"amis": "serangawan", "zh": "文化", "emoji": "🏺"},
    {"amis": "’Aloman", "zh": "人多/許多", "emoji": "👨‍👩‍👧‍👦"},
    {"amis": "mitiliday", "zh": "學生", "emoji": "🎒"},
    {"amis": "saheto", "zh": "都是", "emoji": "✅"},
    {"amis": "Pangcah", "zh": "阿美族", "emoji": "🐚"},
]

SENTENCES = [
    {"amis": "Cima ko ngangan iso?", "zh": "你叫什麼名字？"},
    {"amis": "Ci Panay kako.", "zh": "我是Panay。"},
    {"amis": "Cima kora fafahiyan?", "zh": "那位女生是誰？"},
    {"amis": "Ci Rongac cingra, o widang ako.", "zh": "他叫Rongac，是我的朋友。"},
    {"amis": "Nga’ay ho kiso Rongac?", "zh": "Rongac你好嗎？"},
    {"amis": "Mamaan aca, kiso hani?", "zh": "我很好，你呢？"},
    {"amis": "Icowa ko niyaro’ iso Rongac?", "zh": "Rongac你的部落在哪裡？"},
    {"amis": "I tini i Posong Kakacawan.", "zh": "在臺東縣長濱鄉。"},
    {"amis": "O maan ko tayal iso?", "zh": "你做什麼工作？"},
    {"amis": "O singsi kako, pasifana’ to caciyaw, o radiw ato serangawan no Pangcah.", "zh": "我是老師，教阿美族族語、歌謠和文化。"},
    {"amis": "’Aloman ko mitiliday i tira?", "zh": "在那裡有很多學生嗎？"},
    {"amis": "Hai, saheto o wawa no Pangcah.", "zh": "是的，都是阿美族的孩子。"},
]

# --- 2. 語音功能 ---
def play_audio(text):
    try:
        # 使用印尼語(id)作為阿美語近似發音的備案
        tts = gTTS(text=text, lang='id')
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        st.audio(fp, format='audio/mp3')
    except:
        st.caption("🔇 語音生成失敗")

# --- 3. 測驗邏輯 ---
def init_quiz():
    st.session_state.quiz_score = 0
    st.session_state.quiz_step = 0
    # 隨機選3題測驗
    st.session_state.selected_questions = random.sample(VOCABULARY, 3)

if 'quiz_step' not in st.session_state:
    init_quiz()

# --- 4. 介面呈現 ---
def main():
    st.markdown("""
    <div class="header-container">
        <h1 class="main-title">Cima ko ngangan iso?</h1>
        <div class="sub-title">你叫什麼名字？</div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📖 學習模組", "🧠 挑戰任務"])
    
    with tab1:
        st.markdown("### 🏷️ 重點單字")
        cols = st.columns(3)
        for idx, item in enumerate(VOCABULARY):
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="word-card">
                    <div style="font-size:24px;">{item['emoji']}</div>
                    <div class="amis-word">{item['amis']}</div>
                    <div class="zh-word">{item['zh']}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🔊", key=f"voc_{idx}"):
                    play_audio(item['amis'])

        st.markdown("---")
        st.markdown("### 💬 生活對話")
        for idx, s in enumerate(SENTENCES):
            st.markdown(f"""
            <div class="sentence-box">
                <div class="sentence-amis">{s['amis']}</div>
                <div class="sentence-zh">{s['zh']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"播放語音", key=f"sen_{idx}"):
                play_audio(s['amis'])

    with tab2:
        if st.session_state.quiz_step < 3:
            q_item = st.session_state.selected_questions[st.session_state.quiz_step]
            st.markdown(f"### 任務 {st.session_state.quiz_step + 1}: 翻譯辨識")
            st.info(f"請問「 **{q_item['amis']}** 」的意思是？")
            
            # 產生選項
            wrong_opts = [v['zh'] for v in VOCABULARY if v['zh'] != q_item['zh']]
            options = random.sample(wrong_opts, 2) + [q_item['zh']]
            random.shuffle(options)
            
            for opt in options:
                if st.button(opt, key=f"opt_{opt}"):
                    if opt == q_item['zh']:
                        st.success("Tatamako! (正確!)")
                        st.session_state.quiz_score += 1
                        time.sleep(1)
                    else:
                        st.error(f"錯誤，答案是: {q_item['zh']}")
                        time.sleep(1)
                    st.session_state.quiz_step += 1
                    st.rerun()
        else:
            st.markdown(f"""
            <div style="text-align:center; padding:40px; border:2px solid #FFAB40; border-radius:20px;">
                <h2 style="color:#FFAB40;">測驗完成！</h2>
                <p style="font-size:24px;">得分：{st.session_state.quiz_score} / 3</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("重新挑戰"):
                init_quiz()
                st.rerun()

if __name__ == "__main__":
    main()
