import streamlit as st
import time
import os
import random
from gtts import gTTS
from io import BytesIO

# --- 0. 系統配置 ---
st.set_page_config(
    page_title="阿美語學習 - 生活篇 (高對比版)", 
    page_icon="🗣️", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# --- CSS 視覺修正 (解決看不清楚與顯示問題) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700;900&display=swap');

    /* 全局背景：純黑（最省電且對比最高） */
    .stApp { 
        background-color: #000000;
        font-family: 'Noto Sans TC', sans-serif;
        color: #FFFFFF;
    }
    
    /* Header 區塊 */
    .header-container {
        background: #1A1A1A;
        border: 3px solid #FFD600;
        border-radius: 15px;
        padding: 30px;
        text-align: center;
        margin-bottom: 30px;
    }
    .main-title { color: #FFD600; font-size: 32px; font-weight: 900; margin: 0; }
    .sub-title { color: #FFFFFF; font-size: 22px; margin-top: 10px; font-weight: 700; }

    /* 單字卡片：黑底螢光邊框 */
    .word-card {
        background: #000000;
        border: 2px solid #00E5FF;
        border-radius: 12px;
        padding: 20px 10px;
        text-align: center;
        margin-bottom: 15px;
    }
    .amis-word { font-size: 22px; font-weight: 900; color: #FFFFFF; margin-bottom: 5px; }
    .zh-word { font-size: 18px; color: #00E5FF; font-weight: 700; }

    /* 句子區塊：確保文字大且清晰 */
    .sentence-box {
        background: #121212;
        border-left: 8px solid #FF4081;
        padding: 25px;
        margin-bottom: 20px;
        border-radius: 0 15px 15px 0;
        border-top: 1px solid #333;
        border-right: 1px solid #333;
        border-bottom: 1px solid #333;
    }
    .sentence-amis { font-size: 24px; color: #FF80AB; font-weight: 900; line-height: 1.4; }
    .sentence-zh { font-size: 20px; color: #FFFFFF; font-weight: 700; margin-top: 10px; }

    /* --- 按鈕樣式強化 --- */
    .stButton>button {
        width: 100%;
        background-color: #000000 !important;
        color: #00E5FF !important;
        border: 3px solid #00E5FF !important;
        border-radius: 10px;
        font-size: 20px !important;
        font-weight: 900 !important;
        padding: 15px 0px;
        transition: 0.2s;
    }
    .stButton>button:hover {
        background-color: #00E5FF !important;
        color: #000000 !important;
    }

    /* Tab 分頁標籤樣式 */
    .stTabs [data-baseweb="tab"] {
        color: #FFFFFF !important;
        background-color: #333333 !important;
        border: 1px solid #555;
        padding: 15px 40px;
        font-size: 20px;
        font-weight: 700;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFD600 !important;
        color: #000000 !important;
    }

    /* 測驗題目樣式 */
    .quiz-question-box {
        background: #1A1A1A;
        padding: 30px;
        border-radius: 15px;
        border: 2px dashed #FFD600;
        margin-bottom: 25px;
        text-align: center;
    }
    .quiz-text { color: #FFFFFF; font-size: 22px; font-weight: 700; }
    .highlight-word { color: #FFEB3B; font-size: 28px; font-weight: 900; text-decoration: underline; }
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
    {"amis": "’Aloman", "zh": "許多", "emoji": "👨‍👩‍👧‍👦"},
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
    {"amis": "O singsi kako, pasifana’ to caciyaw.", "zh": "我是老師，教阿美族語。"},
    {"amis": "’Aloman ko mitiliday i tira?", "zh": "在那裡有很多學生嗎？"},
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
        st.error("語音播放暫時不可用")

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
        <div class="sub-title">你叫什麼名字？ - 生活族語學習</div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📖 學習模組", "🧠 挑戰任務"])
    
    with tab1:
        st.markdown("### 🏷️ 重點單字 (Vocabularies)")
        cols = st.columns(2)
        for idx, item in enumerate(VOCABULARY):
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="word-card">
                    <div style="font-size:35px;">{item['emoji']}</div>
                    <div class="amis-word">{item['amis']}</div>
                    <div class="zh-word">{item['zh']}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🔊 播放單字", key=f"voc_{idx}"):
                    play_audio(item['amis'])

        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("### 💬 生活對話 (Sentences)")
        # 這裡循環顯示所有句子
        for idx, s in enumerate(SENTENCES):
            st.markdown(f"""
            <div class="sentence-box">
                <div class="sentence-amis">{s['amis']}</div>
                <div class="sentence-zh">{s['zh']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"🔊 播放對話句子", key=f"sen_{idx}"):
                play_audio(s['amis'])

    with tab2:
        if st.session_state.quiz_step < 3:
            q_item = st.session_state.selected_questions[st.session_state.quiz_step]
            st.markdown(f"## 任務 {st.session_state.quiz_step + 1}")
            
            st.markdown(f"""
            <div class="quiz-question-box">
                <p class="quiz-text">請問以下單字的意思是：</p>
                <p class="highlight-word">{q_item['amis']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            wrong_opts = [v['zh'] for v in VOCABULARY if v['zh'] != q_item['zh']]
            options = random.sample(wrong_opts, 2) + [q_item['zh']]
            random.shuffle(options)
            
            for opt in options:
                if st.button(opt, key=f"opt_{opt}_{st.session_state.quiz_step}"):
                    if opt == q_item['zh']:
                        st.success("✅ 正確！")
                        st.session_state.quiz_score += 1
                        time.sleep(1)
                    else:
                        st.error(f"❌ 答錯了，答案是：{q_item['zh']}")
                        time.sleep(1)
                    st.session_state.quiz_step += 1
                    st.rerun()
        else:
            st.markdown(f"""
            <div style="text-align:center; padding:40px; border:5px solid #FFD600; border-radius:20px; background:#1A1A1A;">
                <h2 style="color:#FFD600;">測驗完成！</h2>
                <p style="font-size:32px; color:#FFFFFF; font-weight:900;">總得分：{st.session_state.quiz_score} / 3</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🔄 重新開始挑戰"):
                init_quiz()
                st.rerun()

if __name__ == "__main__":
    main()
