import streamlit as st
import time
import os
import random
from gtts import gTTS
from io import BytesIO

# --- 0. 系統配置 ---
st.set_page_config(
    page_title="阿美語學習 - 高對比清晰版", 
    page_icon="🗣️", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# --- CSS 視覺修正 (解決看不清楚的問題) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&family=Noto+Sans+TC:wght@400;700&display=swap');

    /* 全局背景：極深藍（增加文字浮出感） */
    .stApp { 
        background-color: #050A18;
        font-family: 'Noto Sans TC', sans-serif;
        color: #FFFFFF;
    }
    
    /* Header 區塊 */
    .header-container {
        background: rgba(255, 171, 64, 0.15);
        border: 2px solid #FFAB40;
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        margin-bottom: 30px;
    }
    .main-title { color: #FFAB40; font-size: 36px; font-weight: 800; margin: 0; }
    .sub-title { color: #FFFFFF; font-size: 20px; margin-top: 10px; }

    /* 單字卡片：背景調深，邊框與字體調亮 */
    .word-card {
        background: #101625;
        border: 2px solid #00E5FF;
        border-radius: 12px;
        padding: 20px 10px;
        text-align: center;
        margin-bottom: 15px;
    }
    .amis-word { font-size: 20px; font-weight: 800; color: #FFFFFF; }
    .zh-word { font-size: 16px; color: #00E5FF; font-weight: 600; }

    /* 句子區塊：增加左側鮮艷度 */
    .sentence-box {
        background: #1A2333;
        border-left: 6px solid #FF4081;
        padding: 20px;
        margin-bottom: 15px;
        border-radius: 0 10px 10px 0;
    }
    .sentence-amis { font-size: 20px; color: #FF80AB; font-weight: 800; }
    .sentence-zh { font-size: 16px; color: #FFFFFF; font-weight: 500; }

    /* --- 重點修正：按鈕樣式 (解決截圖中看不清選項的問題) --- */
    .stButton>button {
        width: 100%;
        background-color: #1A2333 !important; /* 深色底 */
        color: #00E5FF !important;           /* 亮青色字 */
        border: 2px solid #00E5FF !important; /* 亮青色框 */
        border-radius: 8px;
        font-size: 18px !important;
        font-weight: 800 !important;
        padding: 12px 0px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #FFAB40 !important; /* 滑鼠移入變橘色 */
        color: #000000 !important;           /* 字變黑色 */
        border: 2px solid #FFAB40 !important;
    }

    /* Tab 分頁標籤修正 */
    .stTabs [data-baseweb="tab"] {
        color: #FFFFFF !important;
        background-color: #101625 !important;
        border: 1px solid #333;
        padding: 10px 30px;
        font-size: 18px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFAB40 !important;
        color: #000000 !important;
        font-weight: 800;
    }

    /* 測驗文字修正 */
    .quiz-question { color: #FFFFFF; font-size: 22px; font-weight: 700; background: #263238; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #444; }
    .highlight-text { color: #FFEB3B; font-size: 24px; } /* 亮黃色突顯關鍵單字 */
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
    {"amis": "Icowa ko niyaro’ iso Rongac?", "zh": "Rongac你的部落在哪裡？"},
    {"amis": "O maan ko tayal iso?", "zh": "你做什麼工作？"},
    {"amis": "O singsi kako, pasifana’ to caciyaw.", "zh": "我是老師，教語文。"},
    {"amis": "Hai, saheto o wawa no Pangcah.", "zh": "是的，都是阿美族的孩子。"},
]

# --- 2. 語音功能 ---
def play_audio(text):
    try:
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
    st.session_state.selected_questions = random.sample(VOCABULARY, 3)

if 'quiz_step' not in st.session_state:
    init_quiz()

# --- 4. 介面呈現 ---
def main():
    st.markdown("""
    <div class="header-container">
        <h1 class="main-title">Cima ko ngangan iso?</h1>
        <div class="sub-title">你叫什麼名字？ - 清晰對比學習版</div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📖 學習模組", "🧠 挑戰任務"])
    
    with tab1:
        st.markdown("### 🏷️ 重點單字")
        cols = st.columns(2) # 改為 2 欄位，讓單字更顯眼
        for idx, item in enumerate(VOCABULARY):
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="word-card">
                    <div style="font-size:30px;">{item['emoji']}</div>
                    <div class="amis-word">{item['amis']}</div>
                    <div class="zh-word">{item['zh']}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🔊 播放 {item['amis']}", key=f"voc_{idx}"):
                    play_audio(item['amis'])

    with tab2:
        if st.session_state.quiz_step < 3:
            q_item = st.session_state.selected_questions[st.session_state.quiz_step]
            st.markdown(f"## 任務 {st.session_state.quiz_step + 1}: 翻譯辨識")
            
            # 使用更清晰的題目樣式
            st.markdown(f"""
            <div class="quiz-question">
                請問 <span class="highlight-text">「 {q_item['amis']} 」</span> 的意思是什麼？
            </div>
            """, unsafe_allow_html=True)
            
            # 產生選項
            wrong_opts = [v['zh'] for v in VOCABULARY if v['zh'] != q_item['zh']]
            options = random.sample(wrong_opts, 2) + [q_item['zh']]
            random.shuffle(options)
            
            # 選項垂直排列，更好點擊
            for opt in options:
                if st.button(opt, key=f"opt_{opt}_{st.session_state.quiz_step}"):
                    if opt == q_item['zh']:
                        st.success("Tatamako! (正確!)")
                        st.session_state.quiz_score += 1
                        time.sleep(1)
                    else:
                        st.error(f"答錯囉！正確答案是: {q_item['zh']}")
                        time.sleep(1)
                    st.session_state.quiz_step += 1
                    st.rerun()
        else:
            st.markdown(f"""
            <div style="text-align:center; padding:40px; border:4px solid #FFAB40; border-radius:20px; background:#101625;">
                <h2 style="color:#FFAB40;">測驗結束</h2>
                <p style="font-size:30px; color:#FFFFFF;">得分：{st.session_state.quiz_score} / 3</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("重新開始任務"):
                init_quiz()
                st.rerun()

if __name__ == "__main__":
    main()
