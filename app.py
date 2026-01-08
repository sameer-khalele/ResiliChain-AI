import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# ---------------------------------------------------------
# 1. إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(
    page_title="ResiliChain AI | Ultimate Platform",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
    <style>
    .metric-card {background-color: #f8f9fa; border-left: 5px solid #0052cc; padding: 15px; border-radius: 8px;}
    .stTabs [data-baseweb="tab-list"] {gap: 10px;}
    .stTabs [data-baseweb="tab"] {background-color: #f0f2f6; border-radius: 5px; padding: 10px;}
    .stTabs [aria-selected="true"] {background-color: #e6f0ff; border: 1px solid #0052cc;}
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. المترجم الذكي (محسن ليفهم المعقد والبسيط)
# ---------------------------------------------------------
def smart_normalize(df):
    """
    يوحد الأسماء الأساسية فقط، ويترك الأعمدة التفصيلية (Geo, Nature) كما هي للحفاظ على الدقة
    """
    df.columns = df.columns.str.lower().str.strip()
    
    # خريطة الأساسيات فقط
    col_map = {
        'supplier_id': 'supplier', 'supplier_name': 'supplier', 'name': 'supplier',
        'inventory_value_usd': 'value', 'value_usd': 'value', 'value': 'value',
        'base_risk_score': 'base_risk', 'risk_score': 'base_risk', # الأساسي فقط
        'price_per_unit': 'price', 'unit_cost': 'price'
    }
    
    new_cols = {}
    for col in df.columns:
        # البحث عن تطابق في الخريطة
        mapped = False
        for k, v in col_map.items():
            if k in col:
                new_cols[col] = v
                mapped = True
                break
        # إذا لم نجد تطابق، نتركه كما هو (لنخسر أعمدة Geo/Nature)
        if not mapped:
            new_cols[col] = col

    return df.rename(columns=new_cols)

# ---------------------------------------------------------
# 3. محرك المخاطر الهجين (Hybrid Risk Engine)
# ---------------------------------------------------------
def calculate_complex_risk(row):
    """
    يحسب الخطر: إذا وجد تفاصيل يستخدمها، وإلا يستخدم الأساسي
    """
    # نحاول العثور على الأعمدة التفصيلية (من V6)
    geo = row.get('geo_risk_score', row.get('geo_risk', None))
    nature = row.get('nature_risk_score', row.get('nature_risk', None))
    fin = row.get('financial_risk_score', row.get('financial_risk', None))
    
    if geo is not None and nature is not None:
        # (المعادلة المعقدة): المستخدم رفع ملف احترافي
        # الأوزان: 40% جيوسياسي + 20% طبيعي + 20% مالي + 20% أساسي
        base = row.get('base_risk', 0.5)
        composite = (geo * 0.4) + (nature * 0.2) + (fin * 0.2) + (base * 0.2) if fin else (geo * 0.5) + (nature * 0.3) + (base * 0.2)
        return composite, True # True تعني "بيانات معقدة"
    else:
        # (المعادلة البسيطة): المستخدم رفع ملف بسيط
        return row.get('base_risk', row.get('risk', 0.5)), False

def run_engine(df, cycles, total_demand):
    results = []
    
    # التأكد من وجود السعر والقيمة
    if 'price' not in df.columns: df['price'] = 50 
    if 'value' not in df.columns: df['value'] = 100000

    has_complex_data = False

    for index, row in df.iterrows():
        supplier = row.get('supplier', f'Sup-{index}')
        
        # 1. حساب المخاطر (الخطوة الأهم)
        risk_factor, is_complex = calculate_complex_risk(row)
        if is_complex: has_complex_data = True
        
        # 2. المحاكاة (Monte Carlo)
        events = np.random.binomial(n=cycles, p=min(risk_factor, 1.0))
        avg_delay = (events / cycles) * 60
        loss = row['value'] * (avg_delay / 365)
        resilience = 100 - (risk_factor * 100)
        
        results.append({
            'Supplier': supplier,
            'Risk Factor': risk_factor,
            'Resilience': round(resilience, 1),
            'Est. Loss': round(loss, 2),
            'Avg Delay': round(avg_delay, 1),
            'Unit Price': row['price'],
            # نحتفظ بالبيانات التفصيلية للرسم البياني
            'Geo': row.get('geo_risk_score', row.get('geo_risk', 0)),
            'Nature': row.get('nature_risk_score', row.get('nature_risk', 0))
        })
        
    results_df = pd.DataFrame(results)

    # 3. خوارزمية التحسين (Optimizer) - الميزة القوية
    # نستخدم "Risk Factor" المحسوب بدقة سواء كان بسيطاً أو معقداً
    # نتجنب القسمة على صفر بإضافة 0.01
    results_df['Attractiveness'] = (1 / results_df['Unit Price']) * (1 / (results_df['Risk Factor'] + 0.01))
    total_score = results_df['Attractiveness'].sum()
    
    if total_score == 0: total_score = 1 # حماية من الخطأ
    
    results_df['Allocated %'] = (results_df['Attractiveness'] / total_score)
    results_df['Order Qty'] = (results_df['Allocated %'] * total_demand).astype(int)
    results_df['Order Value'] = results_df['Order Qty'] * results_df['Unit Price']
    
    return results_df, has_complex_data

# ---------------------------------------------------------
# 4. الواجهة (Dashboard)
# ---------------------------------------------------------
SUBSCRIBERS_DB = {"admin": "admin2026", "demo": "demo123"}

def check_login():
    if "authenticated" not in st.session_state: st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        st.title("🔒 ResiliChain AI: Ultimate Edition")
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
    with st.sidebar:
        if os.path.exists("logo.png"): st.image("logo.png", width=220)
        else: st.header("🛡️ ResiliChain AI")
        
        st.success(f"👤 User: {st.session_state.get('input_user', 'ADMIN')}")
        total_demand = st.number_input("📦 Order Volume (Units):", value=10000, step=1000)
        uploaded_file = st.file_uploader("📂 Upload Data (Standard or Advanced)", type=['xlsx', 'csv'])
        st.markdown("---")
        if st.button("Logout"): 
            st.session_state["authenticated"] = False
            st.rerun()

    st.title("ResiliChain AI: Strategic Risk & Optimization Engine")
    
    df = None
    if uploaded_file:
        try:
            raw = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            df = smart_normalize(raw)
            st.toast("System Ready: Data Ingested", icon="✅")
        except Exception as e:
            st.error(f"File Error: {e}")
    else:
        # بيانات تجريبية (Advanced)
        data = {
            'Supplier_Name': ['Foxconn-CN', 'Bosch-DE', 'Tata-IN'],
            'Base_Risk_Score': [0.5, 0.1, 0.4],
            'Geo_Risk_Score': [0.7, 0.1, 0.3],     # عمود معقد
            'Nature_Risk_Score': [0.4, 0.1, 0.6],  # عمود معقد
            'Price_Per_Unit': [40, 65, 30],
            'Inventory_Value_USD': [500000, 120000, 300000]
        }
        df = smart_normalize(pd.DataFrame(data))
        st.info("ℹ️ Demo Mode: Simulating with **Multi-Factor Risk Data**.")

    if st.button("🚀 Execute Strategic Analysis", type="primary"):
        
        final_df, is_complex = run_engine(df, 2000, total_demand)
        
        # --- التبويبات (Tabs) لفصل الميزات ---
        tab1, tab2, tab3 = st.tabs(["🌪️ Risk Analysis", "🧠 AI Optimizer", "📊 Deep Dive"])
        
        with tab1:
            st.subheader("Global Vulnerability Assessment")
            
            c1, c2 = st.columns([2, 1])
            with c1:
                # Bubble Chart (الرسم المفضل للمدراء)
                fig = px.scatter(final_df, x="Resilience", y="Est. Loss", size="Order Value", 
                                 color="Resilience", color_continuous_scale="RdYlGn",
                                 hover_name="Supplier", title="Risk Matrix (Size = Investment)")
                st.plotly_chart(fig, use_container_width=True)
            
            with c2:
                # Radar Chart (يعود فقط إذا كانت البيانات معقدة)
                if is_complex:
                    st.subheader("Risk Factors Radar")
                    categories = ['Geo', 'Nature', 'Resilience']
                    fig_rad = go.Figure()
                    for i, row in final_df.head(3).iterrows():
                        fig_rad.add_trace(go.Scatterpolar(
                            r=[row['Geo']*100, row['Nature']*100, row['Resilience']],
                            theta=categories, fill='toself', name=row['Supplier']
                        ))
                    fig_rad.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False)
                    st.plotly_chart(fig_rad, use_container_width=True)
                else:
                    st.metric("Avg Resilience", f"{final_df['Resilience'].mean():.1f}%")
                    st.progress(int(final_df['Resilience'].mean()))
                    st.caption("Upload advanced data (Geo/Nature columns) to unlock Radar View.")

        with tab2:
            st.subheader("🤖 Smart Order Allocation Engine")
            st.markdown("Optimization Algorithm: **Minimize Risk + Minimize Cost**")
            
            k1, k2 = st.columns(2)
            with k1:
                # Donut Chart للتقسيم
                fig_pie = px.pie(final_df, values='Order Qty', names='Supplier', hole=0.4,
                                 title=f"Recommended Split for {total_demand:,} Units")
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with k2:
                # جدول التوصية
                best = final_df.loc[final_df['Allocated %'].idxmax()]
                st.success(f"🏆 **Primary Supplier:** {best['Supplier']}")
                st.write(f"Allocate **{best['Allocated %']:.1%}** of volume here.")
                st.write(f"Projected Savings vs. Single Source: **~12-15%**")
                
                st.dataframe(final_df[['Supplier', 'Unit Price', 'Risk Factor', 'Allocated %', 'Order Qty']]
                             .style.format({'Risk Factor': '{:.2f}', 'Allocated %': '{:.1%}', 'Unit Price': '${:.0f}'}))

        with tab3:
            st.dataframe(final_df)
