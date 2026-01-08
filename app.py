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
    page_title="ResiliChain AI | Decision Support",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
    <style>
    .metric-card {background-color: #f8f9fa; border-left: 5px solid #0052cc; padding: 15px; border-radius: 8px;}
    .ai-reasoning {background-color: #e3f2fd; padding: 15px; border-radius: 10px; border: 1px solid #2196f3; margin-bottom: 20px;}
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. المترجم الذكي
# ---------------------------------------------------------
def intelligent_mapper(df):
    df.columns = df.columns.astype(str).str.lower().str.strip()
    mapping = {
        'price': 'price', 'cost': 'price', 'unit_cost': 'price', 'سعر': 'price', 'تكلفة': 'price',
        'supplier': 'supplier', 'vendor': 'supplier', 'name': 'supplier', 'مورد': 'supplier',
        'risk': 'risk', 'score': 'risk', 'danger': 'risk', 'خطر': 'risk', 'مخاطر': 'risk',
        'delay': 'delay', 'time': 'delay', 'تأخير': 'delay'
    }
    new_cols = {}
    for col in df.columns:
        matched = False
        for key, val in mapping.items():
            if key in col:
                new_cols[col] = val
                matched = True
                break
        if not matched: new_cols[col] = col
    return df.rename(columns=new_cols)

# ---------------------------------------------------------
# 3. محرك التحليل والذكاء التبريري (Explainable AI)
# ---------------------------------------------------------
def safe_float(val, default=0.5):
    try: return float(val)
    except: return default

def generate_explanation(best_row, strategy_val):
    """توليد نص يشرح سبب الاختيار"""
    supplier = best_row['Supplier']
    risk = best_row['Risk Factor']
    price = best_row['Unit Price ($)']
    
    explanation = f"**Why {supplier} got the biggest share?**\n\n"
    
    if strategy_val < 40: # استراتيجية الأمان
        explanation += f"🎯 **Your Strategy:** Safety First (Conservative).\n"
        explanation += f"✅ **Reason:** {supplier} has a very low Risk Score of **{risk}**. "
        explanation += f"Even though the price (${price}) might be higher, the algorithm prioritized stability to prevent production halts."
    elif strategy_val > 60: # استراتيجية التوفير
        explanation += f"🎯 **Your Strategy:** Cost Reduction (Aggressive).\n"
        explanation += f"✅ **Reason:** {supplier} offers a competitive price of **${price}**. "
        explanation += f"The algorithm accepted the higher risk ({risk}) to maximize your profit margins."
    else: # متوازن
        explanation += f"🎯 **Your Strategy:** Balanced Approach.\n"
        explanation += f"✅ **Reason:** {supplier} offers the best 'Sweet Spot' between Price (${price}) and Reliability ({risk})."
        
    return explanation

def run_engine_v11(df, cycles, total_demand, strategy_slider):
    results = []
    
    # تحويل السلايدر (0-100) إلى أوزان
    # 0 = أمان تام (وزن الخطر عالي)
    # 100 = توفير تام (وزن السعر عالي)
    
    # معادلة الوزن: كلما زاد السلايدر، زاد اهتمامنا بالسعر وقل اهتمامنا بالخطر
    price_weight = 0.5 + (strategy_slider / 100) # من 0.5 إلى 1.5
    risk_weight = 1.5 - (strategy_slider / 100)  # من 1.5 إلى 0.5
    
    if 'supplier' not in df.columns: df['supplier'] = [f"Sup-{i}" for i in range(len(df))]

    for index, row in df.iterrows():
        supplier = str(row['supplier'])
        price = safe_float(row.get('price'), 50)
        risk_raw = safe_float(row.get('risk'), 0.5)
        risk_factor = max(0.01, min(risk_raw if risk_raw < 1.0 else risk_raw/100.0, 0.99))
        
        # Monte Carlo
        events = np.random.binomial(n=cycles, p=risk_factor)
        avg_delay = (events / cycles) * 60
        resilience = 100 - (risk_factor * 100)
        
        # التوصية البسيطة
        rec = "✅ Stable" if resilience > 70 else "⚠️ Caution" if resilience > 40 else "🚨 Risky"

        results.append({
            'Supplier': supplier,
            'Unit Price ($)': round(price, 2),
            'Risk Factor': round(risk_factor, 2),
            'Resilience Score': round(resilience, 1),
            'Avg Delay (Days)': round(avg_delay, 1),
            'AI Recommendation': rec
        })
        
    results_df = pd.DataFrame(results)

    # --- خوارزمية التحسين الديناميكية ---
    # نستخدم الأوزان المتغيرة بناءً على رغبة المستخدم
    # Attractiveness = (1 / Price^Weight1) * (1 / Risk^Weight2)
    results_df['Attractiveness'] = (
        (1 / results_df['Unit Price ($)'] ** price_weight) * (1 / (results_df['Risk Factor'] + 0.01) ** risk_weight)
    )
    
    total_score = results_df['Attractiveness'].sum()
    if total_score == 0: total_score = 1
    
    results_df['Allocated %'] = (results_df['Attractiveness'] / total_score)
    results_df['Order Qty'] = (results_df['Allocated %'] * total_demand).astype(int)
    results_df['Total Cost'] = results_df['Order Qty'] * results_df['Unit Price ($)']
    
    return results_df

# ---------------------------------------------------------
# 4. الواجهة (Dashboard)
# ---------------------------------------------------------
SUBSCRIBERS_DB = {"admin": "admin2026", "demo": "demo123"}

def check_login():
    if "authenticated" not in st.session_state: st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        st.title("🔒 ResiliChain AI: Login")
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if user in SUBSCRIBERS_DB and SUBSCRIBERS_DB[user] == pwd:
                st.session_state["authenticated"] = True
                st.rerun()
            else: st.error("Access Denied")
        return False
    return True

if check_login():
    with st.sidebar:
        if os.path.exists("logo.png"): st.image("logo.png", width=220)
        else: st.header("🛡️ ResiliChain AI")
        
        st.success(f"User: {st.session_state.get('input_user', 'Admin')}")
        
        # --- 🎮 ميزة التحكم الجديدة (Strategy Slider) ---
        st.markdown("### 🎯 Strategy Control")
        st.markdown("Define your priority for this order:")
        strategy = st.slider("Preference:", 0, 100, 30, 
                             help="0 = Maximum Safety (Expensive), 100 = Maximum Savings (Risky)")
        
        if strategy < 40: st.caption("Status: **Safety First** 🛡️")
        elif strategy > 60: st.caption("Status: **Aggressive Savings** 💰")
        else: st.caption("Status: **Balanced** ⚖️")
        
        st.markdown("---")
        total_demand = st.number_input("Order Volume:", 10000)
        uploaded_file = st.file_uploader("Upload Data", type=['xlsx', 'csv'])
        
        if st.button("Logout"): 
            st.session_state["authenticated"] = False
            st.rerun()

    st.title("ResiliChain AI: Strategic Decision Engine")

    df = None
    if uploaded_file:
        try:
            raw = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            df = intelligent_mapper(raw)
            st.toast("Data Loaded", icon="✅")
        except: st.error("File Error")
    else:
        # بيانات ديمو للاختبار
        data = {
            'Supplier': ['Foxconn (Cheap)', 'Intel (Safe)', 'Samsung (Mid)'],
            'Price': [120, 190, 150],
            'Risk': [0.7, 0.05, 0.3]
        }
        df = intelligent_mapper(pd.DataFrame(data))
        st.info("ℹ️ Demo Mode Active")

    if st.button("🚀 Analyze & Optimize", type="primary"):
        
        # تمرير قيمة السلايدر للمحرك
        final_df = run_engine_v11(df, 1000, total_demand, strategy)
        
        # الحصول على الأفضل لكتابة الشرح
        best_supplier_row = final_df.loc[final_df['Allocated %'].idxmax()]
        explanation_text = generate_explanation(best_supplier_row, strategy)
        
        tab1, tab2 = st.tabs(["🧠 AI Reasoning & Allocation", "📊 Risk Data"])
        
        with tab1:
            # --- قسم الشرح الذكي (الجديد) ---
            st.markdown(f"""
            <div class="ai-reasoning">
                <h3>🤖 AI Analyst Insight</h3>
                {explanation_text}
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                fig_pie = px.pie(final_df, values='Order Qty', names='Supplier', hole=0.4, title="Optimal Order Split")
                st.plotly_chart(fig_pie, use_container_width=True)
            with c2:
                st.subheader("Allocation Details")
                st.dataframe(final_df[['Supplier', 'Unit Price ($)', 'Risk Factor', 'Allocated %', 'Order Qty']]
                             .style.format({'Allocated %': '{:.1%}', 'Unit Price ($)': '${:.0f}'}))

        with tab2:
            st.subheader("Risk vs Price Matrix")
            fig = px.scatter(final_df, x="Risk Factor", y="Unit Price ($)", size="Order Qty", color="Supplier",
                             title="Trade-off Analysis (Lower Left is Better)")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(final_df)
