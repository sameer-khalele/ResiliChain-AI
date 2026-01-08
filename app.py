import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# ---------------------------------------------------------
# 1. إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(
    page_title="ResiliChain AI | Unified Supply Engine",
    page_icon="🛡️",
    layout="wide"
)

# CSS لتحسين المظهر
st.markdown("""
    <style>
    .metric-card {background-color: #f8f9fa; border-left: 5px solid #0052cc; padding: 10px; border-radius: 5px;}
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. نظام الدخول
# ---------------------------------------------------------
SUBSCRIBERS_DB = {
    "admin": "admin2026",
    "local_shop": "shop123",
    "global_corp": "corp99"
}

def check_login():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["user"] = None

    def login_attempt():
        user = st.session_state["input_user"]
        pwd = st.session_state["input_pass"]
        if user in SUBSCRIBERS_DB and SUBSCRIBERS_DB[user] == pwd:
            st.session_state["authenticated"] = True
            st.session_state["user"] = user
        else:
            st.error("⛔ Invalid Credentials")

    if not st.session_state["authenticated"]:
        st.title("🔒 ResiliChain AI: Login")
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            st.text_input("Username", key="input_user")
            st.text_input("Password", type="password", key="input_pass")
            st.button("Login", on_click=login_attempt)
        return False
    return True

# ---------------------------------------------------------
# 3. المنطق الهجين (Global vs Local Logic)
# ---------------------------------------------------------

def run_analysis(df, cycles, mode):
    results = []
    
    for index, row in df.iterrows():
        # --- الوضع المحلي (LOCAL MODE) ---
        if mode == "Local Operations":
            # العوامل: التأخير السابق (History)، السعر (Price)، السرعة (Speed)
            past_delay_rate = row.get('Past_Delay_Rate_%', 10) / 100.0  # الموثوقية التاريخية
            traffic_risk = row.get('Traffic_Risk', 0.2)                  # زحام الطرق
            
            # محاكاة التأخير المحلي (بالساعات أو الأيام القليلة)
            daily_risk = past_delay_rate + (traffic_risk * 0.5)
            events = np.random.binomial(n=cycles, p=min(daily_risk, 1.0))
            avg_delay = (events / cycles) * 5  # Max 5 days delay for local
            
            # المهمة الإضافية: تقييم المورد (Scoring)
            # Score = (Reliability 40%) + (Speed 40%) + (Price Advantage 20%)
            # نفترض وجود عمود 'Performance_Score'
            perf_score = 100 - (daily_risk * 100)
            
            recommendation = "✅ Preferred Supplier"
            if perf_score < 60:
                recommendation = "⚠️ Unreliable (Avoid for urgent orders)"
            elif avg_delay > 2:
                recommendation = "🐢 Slow Delivery Warning"

            results.append({
                'Supplier': row.get('Supplier_Name', f'Vendor-{index}'),
                'Type': 'Local',
                'Performance Score': round(perf_score, 1),
                'Avg Delay (Days)': round(avg_delay, 1),
                'Reliability Risk': f"{round(daily_risk*100, 1)}%",
                'AI Action': recommendation
            })

        # --- الوضع العالمي (GLOBAL MODE) ---
        else:
            # العوامل: جيوسياسي، موانئ
            geo_risk = row.get('Geo_Risk', 0.5)
            port_risk = row.get('Port_Risk', 0.2)
            total_risk = geo_risk + (port_risk * 0.8)
            
            events = np.random.binomial(n=cycles, p=min(total_risk, 1.0))
            avg_delay = (events / cycles) * 45 
            loss = row.get('Value_USD', 0) * (avg_delay / 365)
            
            resilience = 100 - (total_risk * 90)
            
            rec_text = "✅ Stable Route"
            if resilience < 40: rec_text = "🚨 CRITICAL: Reroute Shipment"
            
            results.append({
                'Supplier': row.get('Supplier_Name', f'Sup-{index}'),
                'Type': 'Global',
                'Risk Score': round(total_risk, 2),
                'Est. Loss ($)': round(loss, 2),
                'Resilience Score': round(resilience, 1),
                'AI Action': rec_text
            })
        
    return pd.DataFrame(results)

# ---------------------------------------------------------
# 4. الواجهة (Dashboard)
# ---------------------------------------------------------
if check_login():
    user = st.session_state["user"]
    
    with st.sidebar:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=200)
        else:
            st.header("🛡️ ResiliChain AI")
            
        st.info(f"👤 User: {user.upper()}")
        
        # --- الميزة الجديدة: اختيار النمط ---
        st.markdown("### 🏢 Operation Mode")
        mode = st.radio("Select Scope:", ["Global Logistics", "Local Operations"])
        
        st.markdown("---")
        uploaded_file = st.file_uploader(f"📂 Upload {mode} Data", type=['xlsx', 'csv'])
        
        # زر الدعم
        st.markdown("---")
        st.markdown(f'<a href="mailto:info.astrex@gmail.com" style="text-decoration:none; color:grey;">📞 Contact Support</a>', unsafe_allow_html=True)
        if st.button("Logout"):
            st.session_state["authenticated"] = False
            st.rerun()

    # Main Content
    st.title(f"ResiliChain AI: {mode} Dashboard")
    
    if mode == "Local Operations":
        st.caption("Focus: Supplier Reliability, Traffic Delays, Vendor Scoring.")
    else:
        st.caption("Focus: Geopolitical Risks, Port Congestion, Global Supply Chain.")

    df = None
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            st.toast("Data Loaded Successfully", icon="✅")
        except:
            st.error("Error reading file.")
    else:
        # عرض بيانات تجريبية مختلفة حسب النمط
        if mode == "Local Operations":
            data = {
                'Supplier_Name': ['Local Factory A', 'City Distributor B', 'Fast Transport Co', 'Cheap Wholesaler'],
                'Past_Delay_Rate_%': [5, 20, 2, 40], # نسبة تأخيره في الماضي
                'Traffic_Risk': [0.1, 0.4, 0.1, 0.3], # هل يمر في مناطق زحام؟
                'Price_Index': [1.2, 1.0, 1.5, 0.8]   # 1.0 هو السعر الطبيعي
            }
            st.info("ℹ️ Demo Mode: Simulating **Local Suppliers** (Traffic & Reliability).")
        else:
            data = {
                'Supplier_Name': ['China-Main', 'Germany-Part', 'Vietnam-Backup'],
                'Geo_Risk': [0.6, 0.1, 0.3],
                'Port_Risk': [0.5, 0.1, 0.4],
                'Value_USD': [500000, 120000, 450000]
            }
            st.info("ℹ️ Demo Mode: Simulating **Global Logistics** (Ports & Wars).")
        
        df = pd.DataFrame(data)

    if st.button("🚀 Run Analysis Engine", type="primary"):
        with st.spinner("Analyzing parameters..."):
            
            final_df = run_analysis(df, 1000, mode)
            
            if mode == "Local Operations":
                # --- داشبورد محلي ---
                m1, m2 = st.columns(2)
                best_supplier = final_df.loc[final_df['Performance Score'].idxmax()]
                m1.metric("🏆 Best Supplier Today", best_supplier['Supplier'], delta=f"{best_supplier['Performance Score']} Score")
                m2.metric("Avg Network Delay", f"{final_df['Avg Delay (Days)'].mean():.1f} Days")
                
                st.subheader("📊 Supplier Performance Ranking")
                fig = px.bar(final_df, x='Performance Score', y='Supplier', orientation='h', 
                             color='Performance Score', color_continuous_scale='Bluyl', title="Reliability Score (Higher is Better)")
                st.plotly_chart(fig, use_container_width=True)
                st.caption("💡 **Tip:** Scores combine traffic data and past reliability history.")
                
            else:
                # --- داشبورد عالمي ---
                m1, m2 = st.columns(2)
                m1.metric("Total Risk Exposure", f"${final_df['Est. Loss ($)'].sum():,.0f}")
                m2.metric("Critical Routes", len(final_df[final_df['Resilience Score'] < 40]))
                
                st.subheader("🌍 Global Risk Map")
                fig = px.scatter(final_df, x='Risk Score', y='Est. Loss ($)', size='Est. Loss ($)', color='Resilience Score',
                                 hover_name='Supplier', title="Impact vs. Risk")
                st.plotly_chart(fig, use_container_width=True)

            # الجدول النهائي الموحد
            st.markdown("---")
            st.subheader("📋 Actionable Insights")
            
            def highlight_local(val):
                if isinstance(val, str):
                    if 'Unreliable' in val: return 'color: red; font-weight: bold'
                    if 'Preferred' in val: return 'color: green; font-weight: bold'
                return ''

            st.dataframe(final_df.style.applymap(highlight_local, subset=['AIAction' if 'AIAction' in final_df else 'AI Action']), use_container_width=True)
