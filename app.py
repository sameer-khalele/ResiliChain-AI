import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ---------------------------------------------------------
# 1. AUTHENTICATION & SECURITY (نظام الاشتراكات)
# ---------------------------------------------------------
st.set_page_config(page_title="ResiliChain AI | Enterprise", layout="wide")

# كلمة السر الخاصة بالعملاء (يمكنك تغييرها لاحقاً)
CLIENT_ACCESS_KEY = "SA-2026-KEY" 

def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        if st.session_state["password"] == CLIENT_ACCESS_KEY:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password
        st.text_input("🔑 Enter License Key to access ResiliChain Engine:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # Password incorrect, show input again
        st.text_input("🔑 Enter License Key to access ResiliChain Engine:", type="password", on_change=password_entered, key="password")
        st.error("😕 Access Denied. Invalid or expired license key.")
        return False
    else:
        # Password correct
        return True

if check_password():
    # ---------------------------------------------------------
    # 2. THE APP STARTS HERE (ONLY AFTER LOGIN)
    # ---------------------------------------------------------
    
    # Sidebar
    with st.sidebar:
        st.title("⚙️ Control Panel")
        st.success("✅ License Verified: Premium Plan")
        
        st.markdown("---")
        st.subheader("1. Data Source")
        
        # File Uploader (للدقة: رفع بيانات حقيقية)
        uploaded_file = st.file_uploader("Upload Supply Chain Data (Excel/CSV)", type=['xlsx', 'csv'])
        
        st.markdown("---")
        st.subheader("2. Simulation Parameters")
        simulation_cycles = st.slider("Monte Carlo Scenarios", 100, 5000, 1000)
        global_risk_factor = st.slider("Global Disruption Probability (%)", 0, 100, 15)

    # Main Screen
    st.title("🛡️ ResiliChain AI: Enterprise Edition")
    
    # Logic to load data (Real vs Demo)
    df = None
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.info("📂 Client Data Loaded Successfully.")
        except Exception as e:
            st.error(f"Error reading file: {e}")
    else:
        st.warning("⚠️ No private data uploaded. Running in **Demo Mode** with synthetic data.")
        # بيانات افتراضية للعرض فقط
        data = {
            'Supplier_ID': ['DEMO-01', 'DEMO-02', 'DEMO-03'],
            'Location': ['China', 'Germany', 'USA'],
            'Lead_Time_Days': [45, 20, 10],
            'Base_Risk_Score': [0.6, 0.2, 0.1], 
            'Inventory_Value_USD': [150000, 80000, 200000]
        }
        df = pd.DataFrame(data)

    if df is not None:
        st.markdown("---")
        
        # زر التشغيل
        if st.button('🚀 Run Stress-Test Simulation'):
            # Simulation Logic (نفس المنطق السابق)
            results = []
            for index, row in df.iterrows():
                total_risk_prob = row.get('Base_Risk_Score', 0.5) + (global_risk_factor / 100.0)
                disruption_events = np.random.binomial(n=simulation_cycles, p=min(total_risk_prob, 1.0))
                avg_delay_days = (disruption_events / simulation_cycles) * 30 
                value_at_risk = row.get('Inventory_Value_USD', 0) * (avg_delay_days / 90) 
                
                results.append({
                    'Supplier_ID': row.get('Supplier_ID', f'SUP-{index}'),
                    'Predicted_Delay_Days': round(avg_delay_days, 1),
                    'Value_at_Risk_USD': round(value_at_risk, 2),
                    'Resilience_Score': round(100 - (total_risk_prob * 100), 1)
                })
            
            final_df = pd.DataFrame(results)
            
            # عرض النتائج
            c1, c2 = st.columns(2)
            c1.metric("Total Value at Risk", f"${final_df['Value_at_Risk_USD'].sum():,.2f}")
            c2.metric("Critical Suppliers", len(final_df[final_df['Resilience_Score'] < 50]))
            
            st.bar_chart(final_df.set_index('Supplier_ID')['Value_at_Risk_USD'])
            st.dataframe(final_df)
