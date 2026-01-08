import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# ---------------------------------------------------------
# 1. إعدادات الصفحة والتصميم
# ---------------------------------------------------------
st.set_page_config(
    page_title="ResiliChain AI | Enterprise Optimizer",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
    <style>
    .metric-card {background-color: #f8f9fa; border-left: 5px solid #0052cc; padding: 15px; border-radius: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);}
    .stTabs [data-baseweb="tab-list"] {gap: 20px;}
    .stTabs [data-baseweb="tab"] {height: 50px; white-space: pre-wrap; background-color: #f0f2f6; border-radius: 4px 4px 0px 0px; gap: 1px; padding-top: 10px; padding-bottom: 10px;}
    .stTabs [aria-selected="true"] {background-color: #ffffff; border-bottom: 2px solid #0052cc;}
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. المترجم الذكي للأعمدة (Smart Data Mapper) - حل مشكلة الأصفار
# ---------------------------------------------------------
def normalize_columns(df):
    """
    هذه الدالة تقوم بتوحيد أسماء الأعمدة مهما كان ما رفعه المستخدم
    """
    df.columns = df.columns.str.lower().str.strip()
    
    # خريطة الترجمة
    col_map = {
        'supplier_id': 'supplier', 'supplier_name': 'supplier', 'name': 'supplier', 'vendor': 'supplier',
        'inventory_value_usd': 'value', 'value_usd': 'value', 'stock_value': 'value', 'inventory ($)': 'value',
        'base_risk_score': 'risk', 'risk_score': 'risk', 'geo_risk': 'risk', 'risk': 'risk',
        'lead_time_days': 'lead_time', 'past_delay_rate_%': 'delay_rate', 'traffic_risk': 'traffic',
        'price_per_unit': 'price', 'unit_cost': 'price' # عمود جديد للسعر
    }
    
    # إعادة التسمية
    new_cols = {}
    for col in df.columns:
        for k, v in col_map.items():
            if k in col:
                new_cols[col] = v
                break
    
    df = df.rename(columns=new_cols)
    return df

# ---------------------------------------------------------
# 3. محرك المحاكاة والتحسين (The Core Engine)
# ---------------------------------------------------------

def run_simulation_and_optimize(df, cycles, mode, total_demand_units=10000):
    results = []
    
    # التأكد من وجود الأعمدة الضرورية بقيم افتراضية
    if 'value' not in df.columns: df['value'] = 100000
    if 'risk' not in df.columns: df['risk'] = 0.5
    if 'price' not in df.columns: df['price'] = 50 # افتراض سعر القطعة 50 دولار
    
    for index, row in df.iterrows():
        supplier = row.get('supplier', f'Sup-{index}')
        
        # --- الحسابات (Global vs Local) ---
        if mode == "Local Operations":
            # المحلي يركز على السرعة والموثوقية
            reliability = 1.0 - (row.get('delay_rate', 10) / 100.0)
            traffic = row.get('traffic', 0.2)
            daily_risk = (1 - reliability) + (traffic * 0.3)
            
            # Simulation
            events = np.random.binomial(n=cycles, p=min(daily_risk, 1.0))
            avg_delay = (events / cycles) * 7 
            score = (reliability * 60) + ((1-traffic) * 40)
            
            results.append({
                'Supplier': supplier,
                'Score': round(score, 1),
                'Risk Factor': round(daily_risk, 2),
                'Avg Delay': round(avg_delay, 1),
                'Unit Price': row['price']
            })
            
        else:
            # العالمي يركز على الخسارة المالية
            risk = row['risk']
            # Simulation
            events = np.random.binomial(n=cycles, p=min(risk, 1.0))
            avg_delay = (events / cycles) * 45
            loss = row['value'] * (avg_delay / 365)
            resilience = 100 - (risk * 100)
            
            results.append({
                'Supplier': supplier,
                'Resilience': round(resilience, 1),
                'Risk Factor': round(risk, 2),
                'Est. Loss': round(loss, 2),
                'Unit Price': row['price']
            })

    results_df = pd.DataFrame(results)

    # --- 🧠 الميزة القوية: خوارزمية تقسيم الطلبات (The Optimizer) ---
    # هذه الخوارزمية تحسب كم نشتري من كل مورد لتقليل المخاطر
    
    # 1. نحسب "وزن الجاذبية" لكل مورد (كلما قل السعر وقل الخطر، زادت الجاذبية)
    # المعادلة: Attractiveness = (1 / Price) * (1 / Risk)
    results_df['Attractiveness'] = (1 / results_df['Unit Price']) * (1 / (results_df['Risk Factor'] + 0.01))
    
    # 2. تحويل الجاذبية إلى نسبة مئوية
    total_score = results_df['Attractiveness'].sum()
    results_df['Recommended Split %'] = (results_df['Attractiveness'] / total_score)
    
    # 3. حساب الكمية المقترحة
    results_df['Order Quantity (Units)'] = (results_df['Recommended Split %'] * total_demand_units).astype(int)
    results_df['Total Order Cost'] = results_df['Order Quantity (Units)'] * results_df['Unit Price']
    
    return results_df

# ---------------------------------------------------------
# 4. واجهة التطبيق (UI)
# ---------------------------------------------------------
SUBSCRIBERS_DB = {"admin": "admin2026", "demo": "demo123"}

def check_login():
    if "authenticated" not in st.session_state: st.session_state["authenticated"] = False
    
    if not st.session_state["authenticated"]:
        st.title("🔒 ResiliChain AI: Enterprise Login")
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if user in SUBSCRIBERS_DB and SUBSCRIBERS_DB[user] == pwd:
                st.session_state["authenticated"] = True
                st.rerun()
            else: st.error("Invalid Credentials")
        return False
    return True

if check_login():
    # --- Sidebar ---
    with st.sidebar:
        if os.path.exists("logo.png"): st.image("logo.png", width=220)
        else: st.header("🛡️ ResiliChain AI")
        
        st.markdown("### ⚙️ Operation Settings")
        mode = st.radio("Mode:", ["Global Logistics", "Local Operations"])
        
        st.info("💡 **New Feature:** Smart Order Optimization is active.")
        total_demand = st.number_input("Total Units Needed:", value=10000, step=500)
        
        uploaded_file = st.file_uploader("Upload Data", type=['xlsx', 'csv'])
        st.markdown("---")
        if st.button("Logout"): 
            st.session_state["authenticated"] = False
            st.rerun()

    # --- Main Dashboard ---
    st.title(f"ResiliChain AI: {mode} Optimizer")
    
    df = None
    if uploaded_file:
        try:
            raw_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            df = normalize_columns(raw_df) # هنا يتم إصلاح الأسماء تلقائياً
            st.toast("Data normalized & loaded successfully!", icon="✅")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        # بيانات تجريبية (Fallback)
        data = {
            'Supplier': ['Supplier A (Cheap/Risky)', 'Supplier B (Avg/Avg)', 'Supplier C (Exp/Safe)'],
            'Risk_Score': [0.7, 0.4, 0.1], # A خطر، C آمن
            'Unit_Cost': [20, 35, 60],     # A رخيص، C غالي
            'Value_USD': [50000, 50000, 50000]
        }
        df = pd.DataFrame(data)
        df = normalize_columns(df)
        st.info("ℹ️ Using Demo Data. Upload your file to see your analysis.")

    if st.button("🚀 Run AI Optimization Engine", type="primary"):
        
        # تشغيل المحرك
        final_df = run_simulation_and_optimize(df, 1000, mode, total_demand)
        
        # --- تبويبات لعرض النتائج باحترافية ---
        tab1, tab2, tab3 = st.tabs(["📊 Risk Analysis", "🧠 AI Order Splitter", "📋 Detailed Data"])
        
        with tab1:
            # عودة الرسومات البيانية القوية
            st.subheader("Risk & Resilience Overview")
            
            if mode == "Global Logistics":
                col1, col2 = st.columns([2, 1])
                with col1:
                    # Bubble Chart (المهم جداً)
                    fig_bubble = px.scatter(final_df, x="Resilience", y="Est. Loss", size="Order Quantity (Units)", 
                                            color="Resilience", color_continuous_scale="RdYlGn",
                                            hover_name="Supplier", size_max=60, title="Strategic Risk Matrix")
                    st.plotly_chart(fig_bubble, use_container_width=True)
                with col2:
                    # Gauge Chart (عداد)
                    avg_res = final_df['Resilience'].mean()
                    fig_gauge = go.Figure(go.Indicator(
                        mode = "gauge+number", value = avg_res,
                        title = {'text': "Network Health"},
                        gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "darkblue"},
                                 'steps': [{'range': [0, 50], 'color': "lightpink"}, {'range': [50, 100], 'color': "lightgreen"}]}
                    ))
                    st.plotly_chart(fig_gauge, use_container_width=True)
            else:
                st.bar_chart(final_df.set_index('Supplier')['Score'])

        with tab2:
            # --- الميزة الجديدة (Optimization) ---
            st.subheader("🤖 Optimized Order Allocation")
            st.markdown("Based on Price vs. Risk trade-off, here is how you should split your order:")
            
            c1, c2 = st.columns([1, 1])
            with c1:
                # Donut Chart للتقسيم
                fig_pie = px.pie(final_df, values='Order Quantity (Units)', names='Supplier', 
                                 title=f"Optimal Split for {total_demand:,} Units", hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with c2:
                # عرض التوفير والمكاسب
                best_supplier = final_df.loc[final_df['Attractiveness'].idxmax()]
                st.success(f"🏆 **AI Recommendation:** Prioritize **{best_supplier['Supplier']}**.")
                st.write(f"They offer the best balance of Price (${best_supplier['Unit Price']}) and Safety.")
                
                # جدول الكميات
                st.dataframe(final_df[['Supplier', 'Unit Price', 'Recommended Split %', 'Order Quantity (Units)', 'Total Order Cost']].style.format({
                    'Recommended Split %': '{:.1%}',
                    'Unit Price': '${:.2f}',
                    'Total Order Cost': '${:,.2f}'
                }))

        with tab3:
            st.dataframe(final_df)
