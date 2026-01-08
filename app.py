import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ---------------------------------------------------------
# 1. إعدادات الصفحة والتصميم
# ---------------------------------------------------------
st.set_page_config(
    page_title="ResiliChain AI | Strategic Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# تخصيص الألوان والستايل ليبدو احترافياً
st.markdown("""
    <style>
    .metric-card {background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #ff4b4b;}
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. قاعدة بيانات المشتركين (Subscription DB)
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
# 3. المنطق الذكي (Simulation & AI Logic)
# ---------------------------------------------------------
def run_simulation(df, cycles, global_risk):
    results = []
    recommendations = []
    
    for index, row in df.iterrows():
        # استخراج البيانات مع قيم افتراضية للأمان
        risk_score = row.get('Base_Risk_Score', 0.5)
        if pd.isna(risk_score): risk_score = 0.5
        
        # معادلة الخطر
        total_risk = risk_score + (global_risk / 100.0)
        
        # محاكاة مونت كارلو
        events = np.random.binomial(n=cycles, p=min(total_risk, 1.0))
        avg_delay = (events / cycles) * 60 # Max 60 days delay
        
        inv_value = row.get('Inventory_Value_USD', 0)
        loss = inv_value * (avg_delay / 365) * 5 # Loss multiplier
        
        resilience = 100 - (total_risk * 90)
        
        # --- نظام التوصيات الذكي (AI Recommendations) ---
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
            'Category': row.get('Component', 'General'),
            'Inventory ($)': inv_value,
            'Risk Score': risk_score,
            'Predicted Delay (Days)': round(avg_delay, 1),
            'Est. Loss ($)': round(loss, 2),
            'Resilience Score': round(resilience, 1),
            'AI Recommendation': rec_text
        })
        
    return pd.DataFrame(results)

# ---------------------------------------------------------
# 4. واجهة التطبيق (Dashboard)
# ---------------------------------------------------------
if check_login():
    user = st.session_state["user"]
    
    # Sidebar
    with st.sidebar:
        st.title("🎛️ Control Panel")
        st.success(f"User: {user.upper()}")
        
        uploaded_file = st.file_uploader("📂 Upload Data (Excel)", type=['xlsx', 'csv'])
        
        st.markdown("---")
        st.subheader("Simulation Settings")
        cycles = st.slider("Monte Carlo Cycles", 500, 5000, 1000)
        global_risk = st.slider("Global Geo-Political Risk (%)", 0, 100, 20)
        
        if st.button("Logout"):
            st.session_state["authenticated"] = False
            st.rerun()

    # Header
    st.title("🛡️ ResiliChain AI: Strategic Risk Dashboard")
    st.markdown("Advanced Supply Chain Stress-Testing & Optimization Engine")
    
    # Data Loading
    df = None
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            st.toast("Data Loaded Successfully", icon="✅")
        except:
            st.error("Error reading file.")
    else:
        # بيانات تجريبية (Demo) أكثر ثراءً
        data = {
            'Supplier_ID': ['Foxconn', 'Bosch', 'Samsung', 'Intel', 'RedSea-Logistics', 'Tata Steel'],
            'Location': ['China', 'Germany', 'Vietnam', 'USA', 'Yemen', 'India'],
            'Component': ['Electronics', 'Sensors', 'Screens', 'Chips', 'Shipping', 'Raw Material'],
            'Inventory_Value_USD': [500000, 120000, 450000, 800000, 150000, 300000],
            'Base_Risk_Score': [0.6, 0.1, 0.3, 0.05, 0.9, 0.4]
        }
        df = pd.DataFrame(data)
        st.info("ℹ️ Running in **Demo Mode**. Upload your Excel file to see real analysis.")

    if st.button("🚀 Run Advanced Analysis", type="primary"):
        with st.spinner("Processing Algorithms & Generating Strategies..."):
            
            # 1. تشغيل المحرك
            final_df = run_simulation(df, cycles, global_risk)
            
            # 2. KPIs (مؤشرات الأداء الرئيسية)
            k1, k2, k3, k4 = st.columns(4)
            total_exposure = final_df['Est. Loss ($)'].sum()
            avg_res = final_df['Resilience Score'].mean()
            high_risk_count = len(final_df[final_df['Resilience Score'] < 40])
            
            k1.metric("Total Value at Risk", f"${total_exposure:,.0f}", delta="-Potential Loss")
            k2.metric("Network Resilience", f"{avg_res:.1f}%")
            k3.metric("Critical Suppliers", high_risk_count, delta="Requires Action", delta_color="inverse")
            k4.metric("Scenarios Simulated", f"{cycles:,}")

            st.markdown("---")

            # 3. الرسوم البيانية المتقدمة (The Premium Visuals)
            
            # Row 1: Strategy Matrix & Geographic Tree
            c1, c2 = st.columns([1.5, 1])
            
            with c1:
                st.subheader("📊 Strategic Vulnerability Matrix")
                # هذا الرسم يصنف الموردين: من هو المهم ومن هو الخطر
                fig_scatter = px.scatter(
                    final_df, 
                    x="Resilience Score", 
                    y="Inventory ($)", 
                    size="Est. Loss ($)", 
                    color="Resilience Score",
                    hover_name="Supplier",
                    text="Supplier",
                    color_continuous_scale="RdYlGn", # أحمر للأخطر
                    title="Supplier Impact vs. Resilience (Bubble Size = Potential Loss)"
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
                
            with c2:
                st.subheader("🌍 Exposure by Location")
                # رسم Treemap يظهر أين تتركز المخاطر جغرافياً
                fig_tree = px.treemap(
                    final_df, 
                    path=['Location', 'Supplier'], 
                    values='Inventory ($)',
                    color='Resilience Score',
                    color_continuous_scale='RdYlGn',
                    title="Inventory Concentration Map"
                )
                st.plotly_chart(fig_tree, use_container_width=True)

            # Row 2: AI Recommendations Table
            st.subheader("🤖 AI-Driven Action Plan")
            
            # تنسيق الجدول ليظهر التوصيات بألوان
            def highlight_risk(val):
                color = 'red' if 'CRITICAL' in val else 'orange' if 'HIGH RISK' in val else 'green'
                return f'color: {color}; font-weight: bold'

            st.dataframe(
                final_df[['Supplier', 'Location', 'Resilience Score', 'Est. Loss ($)', 'AI Recommendation']]
                .style.applymap(highlight_risk, subset=['AI Recommendation']),
                use_container_width=True
            )

            # 4. زر التحميل (Download Report)
            csv = final_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Full Risk Report (CSV)",
                data=csv,
                file_name='resilichain_risk_report.csv',
                mime='text/csv',
            )
