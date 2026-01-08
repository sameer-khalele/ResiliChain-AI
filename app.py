import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# ---------------------------------------------------------
# 1. إعدادات الصفحة والتصميم
# ---------------------------------------------------------
st.set_page_config(page_title="ResiliChain AI | Enterprise v13", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f9fbfd; }
    .metric-card { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 4px solid #0052cc; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #f0f2f6; border-radius: 5px; padding: 10px 20px; font-weight: bold; }
    .stTabs [aria-selected="true"] { background-color: #0052cc; color: white; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. المترجم الذكي (Smart Mapper)
# ---------------------------------------------------------
def smart_mapper(df):
    df.columns = df.columns.astype(str).str.lower().str.strip()
    mapping = {
        'price': 'price', 'cost': 'price', 'سعر': 'price', 'تكلفة': 'price',
        'supplier': 'supplier', 'name': 'supplier', 'مورد': 'supplier',
        'risk': 'risk_score', 'خطر': 'risk_score', 'score': 'risk_score'
    }
    new_cols = {}
    for col in df.columns:
        for key, val in mapping.items():
            if key in col:
                new_cols[col] = val
                break
        else: new_cols[col] = col
    return df.rename(columns=new_cols)

# ---------------------------------------------------------
# 3. محرك الحسابات الدقيق
# ---------------------------------------------------------
def run_precision_engine(df, total_demand, strategy, max_cap):
    results = []
    
    # موازنة الاستراتيجية (كلما زادت زاد الاهتمام بالتوفير)
    p_weight = 0.4 + (strategy / 100)
    r_weight = 1.6 - (strategy / 100)
    
    for index, row in df.iterrows():
        name = str(row.get('supplier', f'Vendor-{index}'))
        price = float(row.get('price', 100))
        
        # حساب الخطر (التأكد من أنه بين 0 و 1)
        raw_risk = float(row.get('risk_score', 0.5))
        risk = max(0.01, min(raw_risk if raw_risk <= 1.0 else raw_risk/100, 0.99))
        
        # الصمود (Resilience) = عكس الخطر
        resilience = (1 - risk) * 100
        
        # الجاذبية الرياضية (Optimization Formula)
        attraction = (1 / (price ** p_weight)) * (1 / (risk ** r_weight))
        
        results.append({
            'Supplier': name,
            'Unit Price': price,
            'Risk Factor': risk,
            'Resilience %': round(resilience, 1),
            'Attraction': attraction
        })
    
    res_df = pd.DataFrame(results)
    
    # تحويل الجاذبية إلى نسب مئوية مع احترام القيد (Max Cap)
    total_attr = res_df['Attraction'].sum()
    res_df['Raw_Split'] = res_df['Attractiveness' if 'Attractiveness' in res_df else 'Attraction'] / total_attr
    
    # تطبيق القيد (Constraint)
    res_df['Final_Split'] = res_df['Raw_Split'].clip(upper=max_cap/100)
    
    # إعادة توزيع الفائض
    diff = 1.0 - res_df['Final_Split'].sum()
    if diff > 0:
        non_capped = res_df['Final_Split'] < (max_cap/100)
        if non_capped.any():
            res_df.loc[non_capped, 'Final_Split'] += diff / non_capped.sum()
            
    res_df['Order Qty'] = (res_df['Final_Split'] * total_demand).astype(int)
    res_df['Total Cost'] = res_df['Order Qty'] * res_df['Unit Price']
    
    return res_df

# ---------------------------------------------------------
# 4. واجهة المستخدم (The Dashboard)
# ---------------------------------------------------------
if "authenticated" not in st.session_state: st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🛡️ ResiliChain AI: Strategic Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "admin" and pwd == "admin2026":
            st.session_state["authenticated"] = True
            st.rerun()
else:
    with st.sidebar:
        if os.path.exists("logo.png"): st.image("logo.png", width=200)
        else: st.title("ResiliChain AI")
        
        st.markdown("### ⚙️ Optimization Settings")
        max_alloc = st.slider("Max Allocation per Supplier (%)", 10, 100, 40)
        strategy = st.slider("Strategy (Safety vs Cost):", 0, 100, 30, help="0=Safe, 100=Cheap")
        total_vol = st.number_input("Total Order Volume:", value=10000)
        
        st.markdown("---")
        uploaded_file = st.file_uploader("📂 Upload Data", type=['xlsx', 'csv'])
        if st.button("Logout"):
            st.session_state["authenticated"] = False
            st.rerun()

    st.title("🛡️ Enterprise Risk & Decision Dashboard")

    if uploaded_file:
        raw_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        df = smart_mapper(raw_df)
        
        if st.button("🚀 Execute Strategic Analysis", type="primary"):
            final_df = run_precision_engine(df, total_vol, strategy, max_alloc)
            
            # --- الـ KPIs العلوية ---
            k1, k2, k3 = st.columns(3)
            with k1: st.markdown(f'<div class="metric-card"><h4>Total Cost</h4><h2>${final_df["Total Cost"].sum():,.0f}</h2></div>', unsafe_allow_html=True)
            with k2: st.markdown(f'<div class="metric-card"><h4>Avg Resilience</h4><h2>{final_df["Resilience %"].mean():.1f}%</h2></div>', unsafe_allow_html=True)
            with k3: st.markdown(f'<div class="metric-card"><h4>Critical Points</h4><h2>{len(final_df[final_df["Resilience %"] < 40])}</h2></div>', unsafe_allow_html=True)

            st.markdown("---")

            # --- التبويبات (Tabs) لترتيب الشكل ---
            tab1, tab2, tab3 = st.tabs(["📊 Risk Matrix", "🧠 AI Strategy", "📋 Raw Data"])

            with tab1:
                col1, col2 = st.columns([2, 1])
                with col1:
                    # Bubble Chart (الرسمة الأهم)
                    fig = px.scatter(final_df, x="Resilience %", y="Unit Price", size="Order Qty", 
                                     color="Resilience %", color_continuous_scale="RdYlGn",
                                     hover_name="Supplier", title="Supplier Strategic Map (Size = Order Volume)",
                                     labels={'Resilience %': 'Reliability Score', 'Unit Price': 'Cost Per Unit'})
                    st.plotly_chart(fig, use_container_width=True)
                    st.caption("💡 **Interpretation:** Top-Right is Safe but Expensive. Bottom-Right is the 'Golden Spot' (Safe & Cheap).")
                with col2:
                    # Radar/Bar Chart للتنويع
                    fig_bar = px.bar(final_df, x='Final_Split', y='Supplier', orientation='h', color='Resilience %',
                                     title="Volume Distribution %", color_continuous_scale="RdYlGn")
                    st.plotly_chart(fig_bar, use_container_width=True)

            with tab2:
                # تبرير القرار
                best = final_df.loc[final_df['Final_Split'].idxmax()]
                st.info(f"🤖 **Decision Logic:** System prioritized **{best['Supplier']}** with **{best['Final_Split']:.1%}** of the total volume.")
                
                c1, c2 = st.columns(2)
                with c1:
                    fig_pie = px.pie(final_df, values='Final_Split', names='Supplier', hole=0.4, title="Order Quantity Split")
                    st.plotly_chart(fig_pie, use_container_width=True)
                with c2:
                    st.subheader("Allocation Plan")
                    st.dataframe(final_df[['Supplier', 'Unit Price', 'Resilience %', 'Final_Split', 'Order Qty']]
                                 .style.format({'Final_Split': '{:.1%}', 'Unit Price': '${:.1f}'}))

            with tab3:
                st.dataframe(final_df)
    else:
        st.info("👈 Please upload your supplier Excel file to begin the analysis.")
