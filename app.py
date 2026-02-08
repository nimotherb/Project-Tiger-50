import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import time
import os
import requests

# ==========================================
# 🛠️ 系統基礎設定與資源下載
# ==========================================
st.set_page_config(layout="wide", page_title="天機・虎爺矩陣 V4.1", page_icon="🐯")

# 自動下載中文字型 (避免圖表亂碼)
font_filename = 'NotoSansTC-Regular.otf'
font_url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/TraditionalChinese/NotoSansCJKtc-Regular.otf"

if not os.path.exists(font_filename):
    with st.spinner("正在下載中文字型..."):
        try:
            response = requests.get(font_url)
            with open(font_filename, 'wb') as f:
                f.write(response.content)
        except Exception as e:
            st.error(f"字型下載失敗: {e}")

# 設定字型
if os.path.exists(font_filename):
    font_prop = fm.FontProperties(fname=font_filename)
    plt.rcParams['font.family'] = font_prop.get_name()
else:
    font_prop = None # 如果下載失敗，使用預設字型

# 賽博龐克 CSS 樣式
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    h1, h2, h3 { color: #ff0055 !important; text-shadow: 0 0 10px #ff0055; font-family: sans-serif; }
    div[data-testid="stMetricValue"] { color: #00ff41 !important; text-shadow: 0 0 5px #00ff41; }
    /* 讓圖片容器自動適應 */
    img { max-width: 100%; height: auto; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🐯 1. 扭蛋系統 (Gacha)
# ==========================================
# 為了確保程式能直接運行，圖片已改為網路連結
LOOT_TABLE = [
    {"tier": "SSR", "threshold": 95, "name": "天金虎爺・財源廣進", "asset": "https://cdn-icons-png.flaticon.com/512/3554/3554067.png", "msg": "🎉 恭喜發財！虎爺賜你金元寶！", "effect": "balloons"},
    {"tier": "SR",  "threshold": 80, "name": "白銀虎爺・平安順心",   "asset": "https://cdn-icons-png.flaticon.com/512/744/744922.png", "msg": "🍵 平安是福！虎爺保佑你萬事如意。", "effect": "snow"},
    {"tier": "R",   "threshold": 20, "name": "青銅虎爺・廣結善緣",     "asset": "https://cdn-icons-png.flaticon.com/512/616/616554.png", "msg": "🤝 結好緣！人脈就是錢脈。", "effect": "none"},
    {"tier": "FAIL","threshold": 0,  "name": "空氣・虎爺去散步了",         "asset": "https://cdn-icons-png.flaticon.com/512/4201/4201973.png", "msg": "💤 虎爺不在家，請稍後再試...", "effect": "error"}
]

def get_gacha_result(score):
    sorted_table = sorted(LOOT_TABLE, key=lambda x: x['threshold'], reverse=True)
    for loot in sorted_table:
        if score >= loot['threshold']: return loot
    return LOOT_TABLE[-1]

# ==========================================
# 📊 2. 數據生成與繪圖 (Data & Plot)
# ==========================================
def generate_cyber_data():
    hours = np.arange(24)
    # 模擬人流 (高峰 2500人)
    mu, sigma = 14, 3.5
    base_curve = np.exp(-((hours - mu)**2) / (2 * sigma**2))
    traffic = (base_curve * 2500) + np.random.normal(0, 50, 24) + 300
    traffic = np.maximum(traffic, 0).astype(int)

    # 模擬金流 (單位：萬元)
    money_raw = traffic * np.random.uniform(300, 800, 24)
    money_wan = money_raw / 10000 

    df = pd.DataFrame({"Hour": hours, "信眾靈壓": traffic, "功德金_Raw": money_wan})

    # 時段與時辰
    def get_period(h):
        if 5 <= h < 13: return "陽初 (早)"
        elif 13 <= h < 19: return "陽盛 (午)"
        else: return "陰虛 (晚)"
    df["時段"] = df["Hour"].apply(get_period)

    zodiac = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    df["時辰"] = df["Hour"].apply(lambda h: f"{zodiac[(h+1)//2%12]}時")

    # 強度分級
    mx = df["信眾靈壓"].max()
    df["強度"] = df["信眾靈壓"].apply(lambda t: "🟥 極高" if t > mx*0.8 else ("🟨 中庸" if t > mx*0.5 else "⬛ 微弱"))

    return df

def plot_cyber_bar(df, x_col, y_col, title, unit_label):
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(8, 4))

    max_idx = df[y_col].idxmax()
    colors = ['#333333'] * len(df)
    colors[max_idx] = '#ff0055'

    ax.bar(df[x_col], df[y_col], color=colors)

    # 標題與字型
    ax.set_title(f"// {title} //", color='#00ff41', fontsize=14, fontproperties=font_prop)

    # 設定 Y 軸單位標籤
    ax.set_ylabel(f"單位：{unit_label}", color='#888', fontproperties=font_prop)

    # 標示最大值
    peak_x = df.iloc[max_idx][x_col]
    peak_y = df.iloc[max_idx][y_col]
    val_str = f"{int(peak_y):,}" if peak_y > 100 else f"{peak_y:.1f}"

    ax.text(peak_x, peak_y + (peak_y*0.05), f"MAX: {val_str} {unit_label}",
            ha='center', color='#ff0055', fontweight='bold', fontproperties=font_prop)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(colors='#888')
    return fig

def plot_cyber_pie(df_grouped, title):
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(4, 4))

    max_idx = df_grouped.idxmax()
    labels = df_grouped.index
    colors = ['#ff0055' if l == max_idx else '#444444' for l in labels]
    explode = [0.1 if l == max_idx else 0 for l in labels]

    wedges, texts, autotexts = ax.pie(df_grouped, labels=labels, autopct='%1.1f%%',
                                      colors=colors, explode=explode, startangle=90)

    for t in texts:
        t.set_fontproperties(font_prop)
        t.set_color('#cccccc')
    for at in autotexts: at.set_color('white')

    ax.set_title(f"// {title} //", color='#00ff41', fontproperties=font_prop)
    return fig

# ==========================================
# 🖥️ 介面組裝
# ==========================================
st.title("🐯 天機・虎爺矩陣 (CYBER ORACLE)")

# --- Part 1: 扭蛋機 ---
st.subheader("🧧 線上求錢母 (Gacha)")
col1, col2 = st.columns([1, 2])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/4081/4081966.png", width=120)
    cheat = st.checkbox("必中 SSR")
with col2:
    if st.button("🙏 啟動靈力 (Shake)", type="primary", use_container_width=True):
        with st.spinner("🔮 讀取天機中..."):
            time.sleep(1)
            res = get_gacha_result(100 if cheat else np.random.randint(0, 101))

            if res['tier'] == 'SSR': st.balloons()
            elif res['tier'] == 'SR': st.snow()

            st.success(f"**【{res['tier']}】** {res['name']}")
            st.write(res['msg'])
            st.image(res['asset'], width=150)

st.markdown("---")

# --- Part 2: 戰情室 ---
st.header("📊 靈壓戰情室 (Dashboard)")
df = generate_cyber_data()

# 繪圖區
c1, c2 = st.columns(2)
with c1:
    # 靈壓 (人)
    gp_t = df.groupby("時段")["信眾靈壓"].sum()
    st.pyplot(plot_cyber_pie(gp_t, "時段靈壓佔比"))
    st.markdown("####") 
    st.pyplot(plot_cyber_bar(df, "Hour", "信眾靈壓", "十二時辰靈壓走勢", "人"))

with c2:
    # 功德 (萬)
    gp_m = df.groupby("時段")["功德金_Raw"].sum()
    st.pyplot(plot_cyber_pie(gp_m, "時段功德佔比"))
    st.markdown("####") 
    st.pyplot(plot_cyber_bar(df, "Hour", "功德金_Raw", "十二時辰功德走勢", "萬元"))

st.markdown("---")
st.subheader("🏆 黃金時辰榜 (Top 3)")

# 表格區
top3 = df.nlargest(3, "信眾靈壓")[["時辰", "強度", "信眾靈壓", "功德金_Raw"]]
# 為了表格顯示好看，重新命名欄位
top3.columns = ["時辰", "強度", "靈壓(人)", "功德(萬)"]
top3["功德(萬)"] = top3["功德(萬)"].apply(lambda x: f"NT$ {x:,.1f} 萬")
top3["靈壓(人)"] = top3["靈壓(人)"].apply(lambda x: f"{x:,}")

def highlight_first(row):
    color = '#ff0055' if row.name == top3.index[0] else '#888'
    bg = '#330011' if row.name == top3.index[0] else '#111'
    font_weight = 'bold' if row.name == top3.index[0] else 'normal'
    return [f'background-color: {bg}; color: {color}; font-weight: {font_weight}']*len(row)

st.dataframe(
    top3.style.apply(highlight_first, axis=1),
    use_container_width=True,
    hide_index=True
)