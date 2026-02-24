import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import time
import os

# ==========================================
# 🛠️ 系統設定
# ==========================================
st.set_page_config(layout="wide", page_title="天機・虎爺矩陣 V5.4", page_icon="🐯")

st.markdown("""
<style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    h1, h2, h3 { color: #ff0055 !important; text-shadow: 0 0 10px #ff0055; font-family: 'Courier New', monospace; }
    div[data-testid="stMetricValue"] { color: #00ff41 !important; text-shadow: 0 0 10px #00ff41; font-family: 'Courier New', monospace; }
    img { border-radius: 10px; border: 1px solid #333; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🐯 1. 扭蛋系統
# ==========================================
LOOT_TABLE = [
    {"tier": "SSR", "threshold": 95, "name": "天金虎爺・財源廣進", "local_img": "tiger_ssr.jpg", "web_img": "https://cdn-icons-png.flaticon.com/512/3747/3747306.png", "msg": "🎉 恭喜發財！虎爺賜你金元寶！", "effect": "balloons"},
    {"tier": "SR",  "threshold": 80, "name": "白銀虎爺・平安順心",   "local_img": "tiger_sr.jpg",  "web_img": "https://cdn-icons-png.flaticon.com/512/3062/3062835.png", "msg": "🍵 平安是福！虎爺保佑你萬事如意。", "effect": "snow"},
    {"tier": "R",   "threshold": 20, "name": "青銅虎爺・廣結善緣",     "local_img": "tiger_r.jpg",   "web_img": "https://cdn-icons-png.flaticon.com/512/2534/2534204.png", "msg": "🤝 結好緣！人脈就是錢脈。", "effect": "none"},
    {"tier": "FAIL","threshold": 0,  "name": "空氣・虎爺去散步了",         "local_img": "none.jpg",      "web_img": "https://cdn-icons-png.flaticon.com/512/744/744922.png",   "msg": "💤 虎爺不在家，請稍後再試...", "effect": "error"}
]

def get_gacha_result(score):
    sorted_table = sorted(LOOT_TABLE, key=lambda x: x['threshold'], reverse=True)
    for loot in sorted_table:
        if score >= loot['threshold']: return loot
    return LOOT_TABLE[-1]

# ==========================================
# 📊 2. 數據生成
# ==========================================
def generate_complex_data():
    hours = np.arange(24)
    zodiac_labels = [
        "子 (23)", "丑 (01)", "寅 (03)", "卯 (05)", "辰 (07)", "巳 (09)", 
        "午 (11)", "未 (13)", "申 (15)", "酉 (17)", "戌 (19)", "亥 (21)"
    ]

    # A. 今日數據
    mu_today, sigma_today = 19, 3.0
    base_curve = np.exp(-((hours - mu_today)**2) / (2 * sigma_today**2))
    traffic_today = (base_curve * 2800) + np.random.normal(0, 100, 24) + 400
    traffic_today = np.maximum(traffic_today, 0).astype(int)
    money_today = (traffic_today * np.random.uniform(400, 900, 24)) / 10000

    df_today = pd.DataFrame({"Hour": hours, "Traffic": traffic_today, "Money": money_today})
    df_today["Zodiac"] = df_today["Hour"].apply(lambda h: zodiac_labels[(h+1)//2%12])

    # B. 歷史數據
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    heatmap_data = []

    for day in days:
        if day in ["Sat", "Sun"]:
            c1 = np.exp(-((hours - 10)**2) / (2 * 3.0**2)) * 2200
            c2 = np.exp(-((hours - 15)**2) / (2 * 4.0**2)) * 2500 
            daily_traffic = c1 + c2 + np.random.normal(0, 150, 24) + 600
        else:
            daily_traffic = (np.exp(-((hours - 19)**2) / (2 * 2.5**2)) * 3000) + np.random.normal(0, 100, 24) + 300

        zodiac_traffic = []
        for i in range(12):
            h1 = (i * 2 - 1) % 24
            h2 = (i * 2) % 24
            val = (daily_traffic[h1] + daily_traffic[h2]) / 2
            zodiac_traffic.append(int(val))
        heatmap_data.append(zodiac_traffic)

    return df_today, days, zodiac_labels, heatmap_data

# ==========================================
# 🎨 3. Plotly 繪圖 (修復 SyntaxError)
# ==========================================

def plot_neon_area(df, y_col, title, unit, color):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Hour"], y=df[y_col], 
        fill='tozeroy', 
        line=dict(color=color, width=3, shape='spline'),
        hovertemplate=f"<b>%{{x}}:00</b><br>{unit}: %{{y:,.0f}}<extra></extra>"
    ))

    # 建立註釋物件 (將橫向標籤設定拉出來寫，避免括號錯誤)
    unit_label = dict(
        x=0, y=1.05,
        xref='paper', yref='paper',
        text=unit,
        showarrow=False,
        xanchor='left', yanchor='bottom',
        font=dict(size=14, color=color)  # 確保這裡括號有閉合
    )

    fig.update_layout(
        title=dict(text=f"// {title} //", font=dict(color=color)),
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#888'),
        margin=dict(l=30, r=20, t=60, b=20), 
        xaxis=dict(showgrid=False, title="Hour (24h)"),
        yaxis=dict(showgrid=True, gridcolor='#222'),
        annotations=[unit_label] # 引用上面的物件
    )
    return fig

def plot_radar_compass(df, value_col, title, color_hex):
    zodiacs_order = [
        "子 (23)", "丑 (01)", "寅 (03)", "卯 (05)", "辰 (07)", "巳 (09)", 
        "午 (11)", "未 (13)", "申 (15)", "酉 (17)", "戌 (19)", "亥 (21)"
    ]
    df_zodiac = df.groupby("Zodiac", sort=False)[value_col].mean().reindex(zodiacs_order).reset_index()

    r_vals = df_zodiac[value_col].tolist()
    theta_vals = df_zodiac["Zodiac"].tolist()
    r_vals.append(r_vals[0])
    theta_vals.append(theta_vals[0])

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=r_vals, theta=theta_vals, fill='toself',
        line=dict(color=color_hex, width=2),
        marker=dict(size=4, color='#fff')
    ))
    fig.update_layout(
        title=dict(text=f"// {title} //", font=dict(color=color_hex)),
        paper_bgcolor='rgba(0,0,0,0)',
        polar=dict(
            bgcolor='rgba(20,20,20,0.5)',
            radialaxis=dict(visible=True, showticklabels=False, linecolor='#333'),
            angularaxis=dict(linecolor='#555', color='#ddd', rotation=90, direction="clockwise")
        ),
        font=dict(color='#888'), margin=dict(l=60, r=60, t=40, b=40)
    )
    return fig

def plot_heatmap_matrix(days, zodiacs, data_matrix):
    fig = go.Figure(data=go.Heatmap(
        z=data_matrix, x=zodiacs, y=days,
        colorscale=[[0, '#000000'], [0.5, '#440022'], [1, '#ff0055']],
        colorbar=dict(title="強度"),
        hovertemplate="<b>%{y} %{x}</b><br>靈壓: %{z:,.0f}<extra></extra>"
    ))
    fig.update_layout(
        title=dict(text="// 歷史時空熱區 (7 Days) //", font=dict(color='#ff0055')),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#888'), xaxis=dict(side="top"), margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

# ==========================================
# 🖥️ 介面
# ==========================================
st.title("🐯 天機・虎爺矩陣 (CYBER ORACLE)")

st.subheader("🧧 啟動靈力連結 (Gacha)")
col1, col2 = st.columns([1, 2])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/4081/4081966.png", width=120)
    cheat = st.checkbox("必中 SSR")
with col2:
    if st.button("🙏 誠心祈求 (Shake)", type="primary", use_container_width=True):
        with st.spinner("🔮 正在解算天機..."):
            time.sleep(1)
            res = get_gacha_result(100 if cheat else np.random.randint(0, 101))
            if res['tier'] == 'SSR': st.balloons()
            elif res['tier'] == 'SR': st.snow()

            st.success(f"**【{res['tier']}】** {res['name']}")
            st.write(res['msg'])

            if os.path.exists(res['local_img']):
                st.image(res['local_img'], caption=res['name'], use_container_width=True)
            else:
                st.warning(f"⚠️ 找不到 `{res['local_img']}`，使用備用影像。")
                st.image(res['web_img'], caption=f"{res['name']} (備用)", width=150)

st.markdown("---")

st.header("📊 全息靈壓戰情室")
df, days, zodiacs, h_data = generate_complex_data()

tab1, tab2, tab3 = st.tabs(["🌊 靈氣脈衝 (Trend)", "🔮 八卦羅盤 (Cycle)", "🔥 時空熱區 (History)"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(plot_neon_area(df, "Traffic", "靈壓走勢 (人)", "人", "#ff0055"), use_container_width=True)
    with c2:
        st.plotly_chart(plot_neon_area(df, "Money", "功德走勢 (萬)", "萬元", "#00ff41"), use_container_width=True)

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(plot_radar_compass(df, "Traffic", "十二時辰靈壓陣", "#ff0055"), use_container_width=True)
    with c2:
        st.plotly_chart(plot_radar_compass(df, "Money", "十二時辰功德陣", "#00ff41"), use_container_width=True)

with tab3:
    st.plotly_chart(plot_heatmap_matrix(days, zodiacs, h_data), use_container_width=True)
    st.info("💡 觀察：平日(Mon-Fri) 人潮集中在晚上(戌/亥)；假日(Sat-Sun) 則從早上(巳)到下午(申)都很旺。")
