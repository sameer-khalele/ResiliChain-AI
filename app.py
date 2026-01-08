import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ---------------------------------------------------------
# 1. إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(
    page_title="ResiliChain AI | Enterprise Platform",
    page_icon="🛡️",
    layout="wide"
)

# ---------------------------------------------------------
# 2. لوحة تحكم الاشتراكات (Subscription Manager)
# ---------------------------------------------------------
# قائمة المشتركين: "اسم_المستخدم": "كلمة_المرور"
SUBSCRIBERS_DB = {
    "admin": "admin2026",         # حسابك
    "client1": "start123",        # عميل تجريبي
    "dhl_demo": "logistics_go"    # عميل آخر
}

def check_login():
    """نظام التحقق من هوية المستخدم"""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["user"] = None

    def login_attempt():
        input_user = st.session_state["input_user"]
        input_pass = st.session_state["input_pass"]
        
        if input_user in SUBSCRIBERS_DB and SUBSCRIBERS_DB[input_user] == input_pass:
            st.session_state["authenticated"] = True
            st.session_state["user"] = input_user
        else:
            st.session_state["authenticated"] = False
            st.error("⛔ Access Denied: Incorrect Username/Password or Subscription Expired.")

    if not st.session_state["authenticated"]:
        st.markdown("""<style>.stTextInput {width: 100%;}</style>""", unsafe_allow_html=True)
        st.title("🔒 ResiliChain AI Login")
        st.markdown("Please sign in with your **Enterprise Credentials**.")
        
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            st.text_input("Username", key="input_user")
            st.text_input("Password", type="password", key="input_pass")
            st.button("Secure Login 🚀", on_click=login_attempt)
        return False
    
    return True

# ---------------------------------------------------------
# 3. التطبيق الرئيسي
# ---------------------------------------------------------
if check_login():
    current_user = st.session_state["user"]
    
    # --- Sidebar ---
    with st.sidebar:
        st.title("⚙️ Control Center")
        st.success(f"👤 User: {current_user}")
        if st.button("Logout 🔒"):
            st.session_state["authenticated"] = False
            st.rerun()

        st.markdown("---")
        st.header("1. Data Input")
        uploaded_file = st.file_uploader("Upload Supply Chain Data (Excel/CSV)", type=['xlsx', 'csv'])
        
        st.markdown("---")
        st.header("2. Simulation Config")
        simulation_cycles = st.slider("Monte Carlo Scenarios", 500, 10000, 1000)
        global_risk_factor = st.slider("Global External Risk (%)", 0, 100, 15)

    # --- Main Dashboard ---
    st.title("🛡️ ResiliChain AI: Stress-Testing Engine")

    df = None
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.success("📂 Client Data Loaded Successfully.")
        except Exception as e:
            st.error(f"Error reading file: {e}")
    else:
        st.warning("⚠️ No private data uploaded. Running in **Demo Mode**.")
        data = {
            'Supplier_ID': ['DEMO-CN-01', 'DEMO-DE-99', 'DEMO-VN-42'],
            'Location': ['Shanghai', 'Hamburg', 'Hanoi'],
            'Base_Risk_Score': [0.7, 0.2, 0.4], 
            'Inventory_Value_USD': [250000, 80000, 45000]
        }
        df = pd.DataFrame(data)

    if df is not None:
        st.markdown("---")
        if st.button('🚀 Run Monte Carlo Simulation', type="primary"):
            with st.spinner('Running scenarios...'):
                results = []
                for index, row in df.iterrows():
                    risk = row.get('Base_Risk_Score', 0.5) + (global_risk_factor / 100.0)
                    events = np.random.binomial(n=simulation_cycles, p=min(risk, 1.0))
                    delay = (events / simulation_cycles) * 45
                    loss = row.get('Inventory_Value_USD', 0) * (delay / 365) * 4
                    
                    results.append({
                        'Supplier_ID': row.get('Supplier_ID', f'SUP-{index}'),
                        'Predicted Delay (Days)': round(delay, 1),
                        'Potential Loss ($)': round(loss, 2),
                        'Resilience Score': round(100 - (risk * 80), 1)
                    })
                
                final_df = pd.DataFrame(results)
                
                k1, k2 = st.columns(2)
                k1.metric("Total Projected Loss", f"${final_df['Potential Loss ($)'].sum():,.2f}")
                k2.metric("Avg Resilience", f"{final_df['Resilience Score'].mean():.1f}%")
                
                st.subheader("Analysis Results")
                st.bar_chart(final_df.set_index('Supplier_ID')['Potential Loss ($)'])
                st.dataframe(final_df)

