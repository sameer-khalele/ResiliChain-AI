import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# ---------------------------------------------------------
# 1. إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(
    page_title="ResiliChain AI | Enterprise Platform",
    page_icon="🛡️",
    layout="wide"
)

# تحسين التصميم (CSS)
st.markdown("""
    <style>
    .metric-card {background-color: #f0f2f6; border-left: 5px solid #0052cc;}
    .reportview-container .main .block-container{padding-top: 1rem;}
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. قاعدة بيانات المشتركين
# ---------------------------------------------------------
SUBSCRIBERS_DB = {
    "admin": "admin2026",
    "demo": "demo123",
    "client_a": "pass_a"
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
        st.title("🔒 ResiliChain AI: Enterprise Login")
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            st.text_input("Username", key="input_user")
            st.text_input("Password", type="password", key="input_pass")
            st.button("Login", on_click=login_attempt)
        return False
    return True

# ---------------------------------------------------------
# 3. منطق المحاكاة (Core Logic)
# ---------------------------------------------------------
def run_simulation(df, cycles, global_risk):
    results = []
    
    for index, row in df.iterrows():
        risk_score = row.get('Base_Risk_Score', 0.5)
        if pd.isna(risk_score): risk_score = 0.5
        
        total_risk = risk_score + (global_risk / 100.0)
        events = np.random.binomial(n=cycles, p=min(total_risk, 1.0))
        avg_delay = (events / cycles) * 60 
        inv_value = row.get('Inventory_Value_USD', 0)
        loss = inv_value * (avg_delay / 365) * 5 
        resilience = 100 - (total_risk * 90)
        
        # التوصيات الذكية
        rec_text = "✅ Stable"
        if resilience < 30:
            rec_text = "🚨 CRITICAL: Find alternative supplier immediately."
        elif resilience < 50:
            rec_text = "⚠️ HIGH RISK: Split inventory to reduce exposure."
        elif avg_delay > 15:
            rec_text = "📦 Logistics Warning: Expect shipping delays."
            
        results.append({
            'Supplier': row.get('Supplier_ID', f'Sup-{index}'),
            'Location': row.get('Location', 'Unknown'),
            'Inventory ($)': inv_value,
            'Est. Loss ($)': round(loss, 2),
            'Resilience Score': round(resilience, 1),
            'AI Recommendation': rec_text
        })
        
    return pd.DataFrame(results)

# ---------------------------------------------------------
# 4. واجهة التطبيق
# ---------------------------------------------------------
if check_login():
    user = st.session_state["user"]
    
    # --- القائمة الجانبية (Sidebar) ---
    with st.sidebar:
        # 1. عرض الشعار (إذا كان موجوداً)
        if os.path.exists("logo.png"):
            st.image("logo.png", width=200)
        else:
            st.header("🛡️ ResiliChain AI") # بديل نصي في حال عدم وجود الصورة
            
        st.markdown("---")
        st.success(f"👤 User: {user.upper()}")
        
        # 2. زر رفع البيانات
        uploaded_file = st.file_uploader("📂 Upload Data (Excel)", type=['xlsx', 'csv'])
        
        st.markdown("---")
        st.subheader("⚙️ Simulation Parameters")
        cycles = st.slider("Monte Carlo Cycles", 500, 5000, 1000)
        global_risk = st.slider("Global Geo-Political Risk (%)", 0, 100, 20)
        
        st.markdown("---")
        
        # 3. قسم الدعم الفني (Support)
        st.markdown("### 📞 Support Center")
        st.info("Need help interpreting results?")
        st.markdown(f"""
            <a href="mailto:info.astrex@gmail.com" style="
                text-decoration: none; 
                background-color: #f63366; 
                color: white; 
                padding: 10px 20px; 
                border-radius: 5px; 
                display: block; 
                text-align: center;">
                📧 Contact Support Team
            </a>
            """, unsafe_allow_html=True)
        
        if st.button("Logout", key="logout"):
            st.session_state["authenticated"] = False
            st.rerun()

    # --- الشاشة الرئيسية ---
    st.title("ResiliChain AI: Strategic Risk Dashboard")
    st.markdown("Advanced Supply Chain Stress-Testing & Optimization Engine")
    
    # تحميل البيانات
    df = None
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            st.toast("Data Loaded Successfully", icon="✅")
        except:
            st.error("Error reading file.")
    else:
        # Demo Data
        data = {
            'Supplier_ID': ['Foxconn', 'Bosch', 'Samsung', 'Intel', 'RedSea-Logistics', 'Tata Steel'],
            'Location': ['China', 'Germany', 'Vietnam', 'USA', 'Yemen', 'India'],
            'Inventory_Value_USD': [500000, 120000, 450000, 800000, 150000, 300000],
            'Base_Risk_Score': [0.6, 0.1, 0.3, 0.05, 0.9, 0.4]
        }
        df = pd.DataFrame(data)
        st.info("ℹ️ Running in **Demo Mode**. Upload your Excel file to see real analysis.")

    if st.button("🚀 Run Advanced Analysis", type="primary"):
        with st.spinner("Processing Algorithms & Generating Strategies..."):
            
            final_df = run_simulation(df, cycles, global_risk)
            
            # KPIs
            k1, k2, k3, k4 = st.columns(4)
            total_loss = final_df['Est. Loss ($)'].sum()
            avg_res = final_df['Resilience Score'].mean()
            high_risk = len(final_df[final_df['Resilience Score'] < 40])
            
            k1.metric("Total Value at Risk", f"${total_loss:,.0f}", delta="-Potential Loss")
            k2.metric("Network Resilience", f"{avg_res:.1f}%")
            k3.metric("Critical Suppliers", high_risk, delta="Requires Action", delta_color="inverse")
            k4.metric("Scenarios Simulated", f"{cycles:,}")

            st.markdown("---")

            # الرسوم البيانية مع الشرح (Tooltips)
            c1, c2 = st.columns([1.5, 1])
            
            with c1:
                st.subheader("📊 Strategic Vulnerability Matrix")
                fig_scatter = px.scatter(
                    final_df, x="Resilience Score", y="Inventory ($)", size="Est. Loss ($)", 
                    color="Resilience Score", hover_name="Supplier", text="Supplier",
                    color_continuous_scale="RdYlGn", title="Supplier Impact vs. Resilience"
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
                # 4. شرح المخطط الأول
                st.caption("💡 **How to read:** **Large Bubbles** = High financial risk. **Red Bubbles** = Vulnerable suppliers. Ideally, you want all suppliers in the **Top-Right (Green)** area.")
                
            with c2:
                st.subheader("🌍 Exposure by Location")
                fig_tree = px.treemap(
                    final_df, path=['Location', 'Supplier'], values='Inventory ($)',
                    color='Resilience Score', color_continuous_scale='RdYlGn',
                    title="Inventory Concentration Map"
                )
                st.plotly_chart(fig_tree, use_container_width=True)
                # 4. شرح المخطط الثاني
                st.caption("💡 **How to read:** **Box Size** = Amount of inventory invested. **Red Color** = Region is currently unstable. Use this to identify risky geographic concentration.")

            st.markdown("---")
            st.subheader("🤖 AI-Driven Action Plan")
            
            # تلوين الجدول
            def highlight_risk(val):
                color = 'red' if 'CRITICAL' in val else 'orange' if 'HIGH RISK' in val else 'green'
                return f'color: {color}; font-weight: bold'

            st.dataframe(
                final_df[['Supplier', 'Location', 'Resilience Score', 'Est. Loss ($)', 'AI Recommendation']]
                .style.applymap(highlight_risk, subset=['AI Recommendation']),
                use_container_width=True
            )
            
            st.caption("ℹ️ **AI Note:** Recommendations are generated based on Monte Carlo probability simulations (1000+ scenarios).")
