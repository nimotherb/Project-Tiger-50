import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import time
import os
import requests

==========================================
🛠️ 系統基礎設定
==========================================

st.set_page_config(layout="wide", page_title="天機・虎爺矩陣", page_icon="🐯")

下載中文字型 (為了讓雲端伺服器顯示中文)

font_url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/TraditionalChinese/NotoSansCJKtc-Regular.otf"
font_path = "NotoSansTC-Regular.otf"

if not os.path.exists(font_path):
with st.spinner("正在下載中文字型..."):
r = requests.get(font_url)
with open(font_path, 'wb') as f:
f.write(r.content)

設定字型

if os.path.exists(font_path):
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
else:
font_prop = None

CSS 美化

st.markdown("""

<style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    h1, h2, h3 { color: #ff0055 !important; text-shadow: 0 0 10px #ff0055; font-family: sans-serif; }
    div[data-testid="stMetricValue"] { color: #00ff41 !important; text-shadow: 0 0 5px #00ff41; }
    .stButton>button { border: 2px solid #ff0055; color: #ff0055; background-color: transparent; }
    .stButton>button:hover { background-color: #ff0055; color: white; }
</style>


""", unsafe_allow_html=True)

==========================================
🐯 邏輯區
==========================================

LOOT_TABLE = [
{"tier": "SSR", "threshold": 90, "name": "天金虎爺・財源廣進", "asset": "https://cdn-icons-png.flaticon.com/512/3554/3554067.png", "msg": "🎉 恭喜發財！虎爺咬錢來囉！", "effect": "balloons"},
{"tier": "SR",  "threshold": 60, "name": "白銀虎爺・平安順心",   "asset": "https://cdn-icons-png.flaticon.com/512/744/744922.png", "msg": "🍵 平安是福！小人退散。", "effect": "snow"},
{"tier": "R",   "threshold": 0,  "name": "招財貓貓・廣結善緣",     "asset": "https://cdn-icons-png.flaticon.com/512/616/616554.png", "msg": "🤝 先交個朋友，機會在後頭。", "effect": "none"}
]

def get_gacha_result(is_cheat):
score = 100 if is_cheat else np.random.randint(0, 101)
if score >= 90: return LOOT_TABLE[0]
elif score >= 60: return LOOT_TABLE[1]
else: return LOOT_TABLE[2]

def generate_cyber_data():
hours = np.arange(24)
traffic = np.random.randint(100, 3000, 24)
traffic[18:22] = traffic[18:22] * 1.5
money = traffic * np.random.uniform(0.03, 0.08, 24)
df = pd.DataFrame({"Hour": hours, "信眾靈壓": traffic, "功德金_Raw": money})
zodiac = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
df["時辰"] = df["Hour"].apply(lambda h: f"{zodiac[(h+1)//2%12]}時")
return df

==========================================
🖥️ 介面區
==========================================

st.title("🐯 天機・虎爺矩陣 (CYBER TIGER)")
st.caption("Project 財庫 | 數位孿生監控系統 V1.0")

col1, col2 = st.columns([1, 2])
with col1:
st.image("https://cdn-icons-png.flaticon.com/512/4081/4081966.png", width=100)
cheat_mode = st.toggle("開啟大德模式 (必中 SSR)")

with col2:
if st.button("🙏 誠心祈求 (擲筊)", use_container_width=True):
with st.spinner("🔮 虎爺正在嗅聞銅錢的味道..."):
time.sleep(1.5)
res = get_gacha_result(cheat_mode)
if res['effect'] == 'balloons': st.balloons()
elif res['effect'] == 'snow': st.snow()
st.success(f"【{res['tier']}】 {res['name']}")
st.info(res['msg'])
st.image(res['asset'], width=150)

st.divider()

st.subheader("📊 靈壓戰情室")
df = generate_cyber_data()
c1, c2 = st.columns(2)
c1.metric("今日總靈壓", f"{df['信眾靈壓'].sum():,} 人", "+12%")
c2.metric("預估功德金", f"NT$ {df['功德金_Raw'].sum():,.1f} 萬", "+5.8%")

fig, ax = plt.subplots(figsize=(10, 4))
fig.patch.set_facecolor('#0E1117')
ax.set_facecolor('#0E1117')
ax.plot(df["Hour"], df["信眾靈壓"], color='#00FF41', marker='o')
ax.set_title("十二時辰流量監控", color='white', fontproperties=font_prop)
ax.tick_params(colors='white')
ax.spines['bottom'].set_color('white')
ax.spines['left'].set_color('white')
st.pyplot(fig)