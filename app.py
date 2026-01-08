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
# 🚨 تعليمات لك كمدير للنظام:
# - لإضافة عميل جديد: أضف سطراً جديداً "اسم_مستخدم": "كلمة_مرور"
# - لقطع الخدمة عن عميل لم يدفع: احذف سطره من القائمة أدناه
# ---------------------------------------------------------
SUBSCRIBERS_DB = {
    "admin": "admin2026",         # حسابك الخاص للتجربة
    "tesla_supply": "musk_x99",   # مثال لعميل دافع
    "dhl_global": "logistics_01", # مثال لعميل آخر
    # "unpaid_user": "12345"      # هذا العميل لن يستطيع الدخول إذا حذفت هذا السطر
}

def check_login():
    """نظام التحقق من هوية المستخدم وصلاحية اشتراكه"""
    
    # تهيئة متغيرات الجلسة
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["user"] = None

    # دالة الدخول
    def login_attempt():
        input_user = st.session_state["input_user"]
        input_pass = st.session_state["input_pass"]
        
        if input_user in SUBSCRIBERS_DB and SUBSCRIBERS_DB[input_user] == input_pass:
            st.session_state["authenticated"] = True
            st.session_state["user"] = input_user
        else:
            st.session_state["authenticated"] = False
            st.error("⛔ Access Denied: Incorrect Username/Password or Subscription Expired.")

    # واجهة تسجيل الدخول (إذا لم يسجل الدخول بعد)
    if not st.session_state["authenticated"]:
        st.markdown("""
            <style>
                .main {justify-content: center; align-items: center;}
                .stTextInput {width: 100%;}
            </style>
            """, unsafe_allow_html=True)
        
        st.title("🔒 ResiliChain AI Login")
        st.markdown("Please sign in with your **Enterprise Credentials**.")
        
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            st.text_input("Username", key="input_user")
            st.text_input("Password", type="password", key="input_pass")
            st.button("Secure Login 🚀", on_click=login_attempt)
            
        st.info("ℹ️ Contact sales@resilichain.com to renew your subscription.")
        return False
    
    return True

# ---------------------------------------------------------
# 3. التطبيق الرئيسي (يعمل فقط بعد تسجيل الدخول)
# ---------------------------------------------------------
if check_login():
    # اسم المستخدم الحالي
    current_user = st.session_state["user"]
    
    # --- Sidebar ---
    with st.sidebar:
        st.title("⚙️ Control Center")
        st.success(f"👤 User: {current_user.upper()}")
        st.info("✅ License: Active / Premium")
        
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
        st.caption("Adjust based on geopolitical stability (e.g., Red Sea Crisis = 60%)")

    # --- Main Dashboard ---
    st.title("🛡️ ResiliChain AI: Stress-Testing Engine")
    st.markdown("### Proactive Supply Chain Resilience & Risk Analysis")

    # معالجة البيانات
    df = None
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.toast("File uploaded successfully! Analysis ready.", icon="✅")
        except Exception as e:
            st.error(f"Error reading file: {e}")
    else:
        # وضع العرض التجريبي (Demo Mode)
        st.warning("⚠️ No private data uploaded. Running in **Demo Mode**.")
        st.markdown("Using synthetic data for demonstration purposes.")
        
        data = {
            'Supplier_ID': ['DEMO-CN-01', 'DEMO-DE-99', 'DEMO-VN-42', 'DEMO-US-12'],
            'Location': ['Shanghai, China', 'Hamburg, Germany', 'Hanoi, Vietnam', 'Texas, USA'],
            'Component': ['Chips', 'Steel', 'Rubber', 'Plastics'],
            'Lead_Time_Days': [45, 20, 30, 5],
            'Base_Risk_Score': [0.7, 0.2, 0.4, 0.1], 
            'Inventory_Value_USD': [250000, 80000, 45000, 120000]
        }
        df = pd.DataFrame(data)

    if df is not None:
        st.markdown("---")
        
        # زر تشغيل المحاكاة
        if st.button('🚀 Run Monte Carlo Simulation', type="primary"):
            
            with st.spinner('Running thousands of failure scenarios...'):
                results = []
                
                # خوارزمية المحاكاة
                for index, row in df.iterrows():
                    # التحقق من وجود الأعمدة المطلوبة أو استخدام افتراضيات
                    risk_score = row.get('Base_Risk_Score', 0.5) 
                    if pd.isna(risk_score): risk_score = 0.5
                    
                    # معادلة الخطر = خطر المورد + الخطر العالمي
                    total_risk_prob = risk_score + (global_risk_factor / 100.0)
                    
                    # المحاكاة الاحتمالية
                    disruption_events = np.random.binomial(n=simulation_cycles, p=min(total_risk_prob, 1.0))
                    avg_delay_days = (disruption_events / simulation_cycles) * 45 # Assuming 45 days max impact
                    
                    inv_value = row.get('Inventory_Value_USD', 0)
                    value_at_risk = inv_value * (avg_delay_days / 365) * 4 # Impact factor
                    
                    results.append({
                        'Supplier_ID': row.get('Supplier_ID', f'SUP-{index}'),
                        'Predicted Delay (Days)': round(avg_delay_days, 1),
                        'Potential Loss ($)': round(value_at_risk, 2),
                        'Resilience Score': round(100 - (total_risk_prob * 80), 1) # Score out of 100
                    })
                
                final_df = pd.DataFrame(results)
                
                # --- النتائج (Visualization) ---
                
                # 1. KPIs
                kpi1, kpi2, kpi3 = st.columns(3)
                total_loss = final_df['Potential Loss ($)'].sum()
                avg_resilience = final_df['Resilience Score'].mean()
                
                kpi1.metric("Total Projected Loss", f"${total_loss:,.2f}", delta_color="inverse")
                kpi2.metric("Network Resilience", f"{avg_resilience}%", delta="-Risk" if avg_resilience < 60 else "+Stable")
                kpi3.metric("Scenarios Run", f"{simulation_cycles:,}")
                
                # 2. Charts
                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("📉 Financial Impact Analysis")
                    fig_bar = px.bar(final_df, x='Supplier_ID', y='Potential Loss ($)', 
                                     color='Potential Loss ($)', color_continuous_scale='Reds')
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                with c2:
                    st.subheader("🛡️ Resilience Scoring")
                    fig_radar = px.line_polar(final_df, r='Resilience Score', theta='Supplier_ID', line_close=True)
                    fig_radar.update_traces(fill='toself')
                    st.plotly_chart(fig_radar, use_container_width=True)

                # 3. Action Plan (AI Recommendations)
                st.subheader("🚨 AI Mitigation Recommendations")
                critical_suppliers = final_df[final_df['Resilience Score'] < 50]
                
                if not critical_suppliers.empty:
                    for i, row in critical_suppliers.iterrows():
                        st.error(f"**CRITICAL:** Supplier {row['Supplier_ID']} is failing simulation.")
                        st.caption(f"👉 Suggestion: Split order volume. Activate backup supplier in **Vietnam** or **Mexico** immediately.")
                else:
                    st.success("✅ All suppliers passed the stress test. Supply chain is robust.")

                # 4. Data Table
                with st.expander("📄 View Full Simulation Data"):
                    st.dataframe(final_df)import streamlit as st
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
# 🚨 تعليمات لك كمدير للنظام:
# - لإضافة عميل جديد: أضف سطراً جديداً "اسم_مستخدم": "كلمة_مرور"
# - لقطع الخدمة عن عميل لم يدفع: احذف سطره من القائمة أدناه
# ---------------------------------------------------------
SUBSCRIBERS_DB = {
    "admin": "admin2026",         # حسابك الخاص للتجربة
    "tesla_supply": "musk_x99",   # مثال لعميل دافع
    "dhl_global": "logistics_01", # مثال لعميل آخر
    # "unpaid_user": "12345"      # هذا العميل لن يستطيع الدخول إذا حذفت هذا السطر
}

def check_login():
    """نظام التحقق من هوية المستخدم وصلاحية اشتراكه"""
    
    # تهيئة متغيرات الجلسة
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["user"] = None

    # دالة الدخول
    def login_attempt():
        input_user = st.session_state["input_user"]
        input_pass = st.session_state["input_pass"]
        
        if input_user in SUBSCRIBERS_DB and SUBSCRIBERS_DB[input_user] == input_pass:
            st.session_state["authenticated"] = True
            st.session_state["user"] = input_user
        else:
            st.session_state["authenticated"] = False
            st.error("⛔ Access Denied: Incorrect Username/Password or Subscription Expired.")

    # واجهة تسجيل الدخول (إذا لم يسجل الدخول بعد)
    if not st.session_state["authenticated"]:
        st.markdown("""
            <style>
                .main {justify-content: center; align-items: center;}
                .stTextInput {width: 100%;}
            </style>
            """, unsafe_allow_html=True)
        
        st.title("🔒 ResiliChain AI Login")
        st.markdown("Please sign in with your **Enterprise Credentials**.")
        
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            st.text_input("Username", key="input_user")
            st.text_input("Password", type="password", key="input_pass")
            st.button("Secure Login 🚀", on_click=login_attempt)
            
        st.info("ℹ️ Contact sales@resilichain.com to renew your subscription.")
        return False
    
    return True

# ---------------------------------------------------------
# 3. التطبيق الرئيسي (يعمل فقط بعد تسجيل الدخول)
# ---------------------------------------------------------
if check_login():
    # اسم المستخدم الحالي
    current_user = st.session_state["user"]
    
    # --- Sidebar ---
    with st.sidebar:
        st.title("⚙️ Control Center")
        st.success(f"👤 User: {current_user.upper()}")
        st.info("✅ License: Active / Premium")
        
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
        st.caption("Adjust based on geopolitical stability (e.g., Red Sea Crisis = 60%)")

    # --- Main Dashboard ---
    st.title("🛡️ ResiliChain AI: Stress-Testing Engine")
    st.markdown("### Proactive Supply Chain Resilience & Risk Analysis")

    # معالجة البيانات
    df = None
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.toast("File uploaded successfully! Analysis ready.", icon="✅")
        except Exception as e:
            st.error(f"Error reading file: {e}")
    else:
        # وضع العرض التجريبي (Demo Mode)
        st.warning("⚠️ No private data uploaded. Running in **Demo Mode**.")
        st.markdown("Using synthetic data for demonstration purposes.")
        
        data = {
            'Supplier_ID': ['DEMO-CN-01', 'DEMO-DE-99', 'DEMO-VN-42', 'DEMO-US-12'],
            'Location': ['Shanghai, China', 'Hamburg, Germany', 'Hanoi, Vietnam', 'Texas, USA'],
            'Component': ['Chips', 'Steel', 'Rubber', 'Plastics'],
            'Lead_Time_Days': [45, 20, 30, 5],
            'Base_Risk_Score': [0.7, 0.2, 0.4, 0.1], 
            'Inventory_Value_USD': [250000, 80000, 45000, 120000]
        }
        df = pd.DataFrame(data)

    if df is not None:
        st.markdown("---")
        
        # زر تشغيل المحاكاة
        if st.button('🚀 Run Monte Carlo Simulation', type="primary"):
            
            with st.spinner('Running thousands of failure scenarios...'):
                results = []
                
                # خوارزمية المحاكاة
                for index, row in df.iterrows():
                    # التحقق من وجود الأعمدة المطلوبة أو استخدام افتراضيات
                    risk_score = row.get('Base_Risk_Score', 0.5) 
                    if pd.isna(risk_score): risk_score = 0.5
                    
                    # معادلة الخطر = خطر المورد + الخطر العالمي
                    total_risk_prob = risk_score + (global_risk_factor / 100.0)
                    
                    # المحاكاة الاحتمالية
                    disruption_events = np.random.binomial(n=simulation_cycles, p=min(total_risk_prob, 1.0))
                    avg_delay_days = (disruption_events / simulation_cycles) * 45 # Assuming 45 days max impact
                    
                    inv_value = row.get('Inventory_Value_USD', 0)
                    value_at_risk = inv_value * (avg_delay_days / 365) * 4 # Impact factor
                    
                    results.append({
                        'Supplier_ID': row.get('Supplier_ID', f'SUP-{index}'),
                        'Predicted Delay (Days)': round(avg_delay_days, 1),
                        'Potential Loss ($)': round(value_at_risk, 2),
                        'Resilience Score': round(100 - (total_risk_prob * 80), 1) # Score out of 100
                    })
                
                final_df = pd.DataFrame(results)
                
                # --- النتائج (Visualization) ---
                
                # 1. KPIs
                kpi1, kpi2, kpi3 = st.columns(3)
                total_loss = final_df['Potential Loss ($)'].sum()
                avg_resilience = final_df['Resilience Score'].mean()
                
                kpi1.metric("Total Projected Loss", f"${total_loss:,.2f}", delta_color="inverse")
                kpi2.metric("Network Resilience", f"{avg_resilience}%", delta="-Risk" if avg_resilience < 60 else "+Stable")
                kpi3.metric("Scenarios Run", f"{simulation_cycles:,}")
                
                # 2. Charts
                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("📉 Financial Impact Analysis")
                    fig_bar = px.bar(final_df, x='Supplier_ID', y='Potential Loss ($)', 
                                     color='Potential Loss ($)', color_continuous_scale='Reds')
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                with c2:
                    st.subheader("🛡️ Resilience Scoring")
                    fig_radar = px.line_polar(final_df, r='Resilience Score', theta='Supplier_ID', line_close=True)
                    fig_radar.update_traces(fill='toself')
                    st.plotly_chart(fig_radar, use_container_width=True)

                # 3. Action Plan (AI Recommendations)
                st.subheader("🚨 AI Mitigation Recommendations")
                critical_suppliers = final_df[final_df['Resilience Score'] < 50]
                
                if not critical_suppliers.empty:
                    for i, row in critical_suppliers.iterrows():
                        st.error(f"**CRITICAL:** Supplier {row['Supplier_ID']} is failing simulation.")
                        st.caption(f"👉 Suggestion: Split order volume. Activate backup supplier in **Vietnam** or **Mexico** immediately.")
                else:
                    st.success("✅ All suppliers passed the stress test. Supply chain is robust.")

                # 4. Data Table
                with st.expander("📄 View Full Simulation Data"):
                    st.dataframe(final_df)
