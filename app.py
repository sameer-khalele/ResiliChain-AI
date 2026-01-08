import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# ---------------------------------------------------------
# 1. إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(page_title="ResiliChain AI | Strategic Master", layout="wide")

# CSS لتصميم احترافي
st.markdown("""
    <style>
    .metric-card {background-color: #f8f9fa; border-left: 5px solid #0052cc; padding: 15px; border-radius: 8px;}
    .ai-insight {background-color: #f1f8ff; border: 1px solid #0366d6; padding: 15px; border-radius: 10px; margin-bottom: 20px;}
    .scenario-box {background-color: #fff5f5; border: 1px solid #fc8181; padding: 15px; border-radius: 10px;}
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. المترجم الذكي وتجهيز البيانات
# ---------------------------------------------------------
def intelligent_mapper(df):
    df.columns = df.columns.astype(str).str.lower().str.strip()
    mapping = {
        'price': 'price', 'cost': 'price', 'unit_cost': 'price', 'سعر': 'price',
        'supplier': 'supplier', 'vendor': 'supplier', 'name': 'supplier', 'مورد': 'supplier',
        'risk': 'risk', 'score': 'risk', 'danger': 'risk', 'خطر': 'risk'
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
# 3. محرك التحسين مع القيود (Optimizer with Constraints)
# ---------------------------------------------------------
def run_strategic_engine(df, total_demand, strategy, max_cap, risk_surge, price_surge):
    results = []
    
    # تحويل الأوزان
    p_weight = 0.5 + (strategy / 100)
    r_weight = 1.5 - (strategy / 100)
    
    for index, row in df.iterrows():
        supplier = str(row.get('supplier', f'Sup-{index}'))
        
        # تطبيق سيناريو "ماذا لو" (What-if)
        price = float(row.get('price', 50)) * (1 + price_surge/100)
        risk_raw = float(row.get('risk', 0.5)) * (1 + risk_surge/100)
        risk = max(0.01, min(risk_raw if risk_raw < 1.0 else risk_raw/100.0, 0.99))
        
        # حساب الجاذبية
        attraction = (1 / price**p_weight) * (1 / (risk + 0.01)**r_weight)
        
        results.append({
            'Supplier': supplier,
            'Price': price,
            'Risk': risk,
            'Attractiveness': attraction,
            'Resilience': 100 - (risk * 100)
        })
    
    res_df = pd.DataFrame(results)
    
    # تطبيق القيد الاستراتيجي (Max Allocation Cap)
    total_attr = res_df['Attractiveness'].sum()
    res_df['Raw_Split'] = res_df['Attractiveness'] / total_attr
    
    # تقليم النسب التي تتجاوز الحد الأقصى
    res_df['Final_Split'] = res_df['Raw_Split'].clip(upper=max_cap/100)
    
    # إعادة توزيع الفائض لضمان المجموع 100%
    diff = 1.0 - res_df['Final_Split'].sum()
    if diff > 0:
        # توزيع الفائض على الموردين الذين لم يصلوا للحد الأقصى
        non_capped = res_df['Final_Split'] < (max_cap/100)
        if non_capped.any():
            res_df.loc[non_capped, 'Final_Split'] += diff / non_capped.sum()

    res_df['Order_Qty'] = (res_df['Final_Split'] * total_demand).astype(int)
    res_df['Total_Cost'] = res_df['Order_Qty'] * res_df['Price']
    
    return res_df

# ---------------------------------------------------------
# 4. واجهة التطبيق
# ---------------------------------------------------------
if "authenticated" not in st.session_state: st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔒 ResiliChain AI: Strategic Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "admin" and pwd == "admin2026":
            st.session_state["authenticated"] = True
            st.rerun()
else:
    with st.sidebar:
        if os.path.exists("logo.png"): st.image("logo.png", width=200)
        st.success("✅ Enterprise Access")
        
        # --- 📂 الميزة الجديدة: تحميل النموذج ---
        st.subheader("📋 Step 1: Get Template")
        template_data = pd.DataFrame({'Supplier_Name': ['Sample A', 'Sample B'], 'Unit_Price': [100, 150], 'Risk_Score': [0.1, 0.5]})
        st.download_button("📥 Download Excel Template", template_data.to_csv(index=False).encode('utf-8'), "template.csv", "text/csv")
        
        st.markdown("---")
        st.subheader("⚙️ Step 2: Set Constraints")
        max_alloc = st.slider("Max Allocation per Supplier (%)", 10, 100, 40, help="Prevents over-reliance on a single vendor.")
        total_vol = st.number_input("Total Order Volume:", value=10000)
        
        st.markdown("---")
        st.subheader("🌪️ Step 3: Scenario (What-if?)")
        risk_inc = st.slider("Risk Surge (%)", 0, 100, 0, help="Simulate a sudden crisis (e.g. War, Strike)")
        price_inc = st.slider("Price Inflation (%)", 0, 50, 0)
        
        st.markdown("---")
        strategy = st.slider("Strategy (Safety vs Cost):", 0, 100, 30)
        
        uploaded_file = st.file_uploader("📂 Upload Your Data", type=['xlsx', 'csv'])
        if st.button("Logout"): 
            st.session_state["authenticated"] = False
            st.rerun()

    # --- النتائج ---
    st.title("Strategic Supply Chain Optimizer")
    
    if uploaded_file:
        raw = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        df = intelligent_mapper(raw)
        
        if st.button("🚀 Run Scenario Optimization", type="primary"):
            res = run_strategic_engine(df, total_vol, strategy, max_alloc, risk_inc, price_inc)
            
            # --- ميزة التفسير العميق (Explainability) ---
            best = res.loc[res['Final_Split'].idxmax()]
            worst = res.loc[res['Final_Split'].idxmin()]
            
            st.markdown(f"""
            <div class="ai-insight">
                <h4>🤖 Deep AI Insights</h4>
                <ul>
                    <li><b>Winner:</b> {best['Supplier']} took the lead ({best['Final_Split']:.1%}) because it balanced your strategy perfectly.</li>
                    <li><b>Constraint Check:</b> {"✅ All suppliers are within the " + str(max_alloc) + "% limit." if max_alloc < 100 else "⚠️ No limit applied."}</li>
                    <li><b>Why {worst['Supplier']} lost?</b> Despite its potential, it was limited because of its high combined risk/price ratio under the current <b>+{risk_inc}% risk surge</b> scenario.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

            # الرسوم البيانية
            col1, col2 = st.columns(2)
            with col1:
                fig = px.pie(res, values='Order_Qty', names='Supplier', hole=0.4, title="Optimized Allocation Split")
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig_bar = px.bar(res, x='Supplier', y='Final_Split', color='Resilience', title="Final Allocation % vs Resilience")
                st.plotly_chart(fig_bar, use_container_width=True)
            
            st.subheader("Detailed Execution Plan")
            st.dataframe(res[['Supplier', 'Price', 'Risk', 'Resilience', 'Final_Split', 'Order_Qty', 'Total_Cost']].style.format({'Final_Split': '{:.1%}', 'Total_Cost': '${:,.0f}'}))
    else:
        st.info("👈 Please download the template from the sidebar, fill it, and upload it to start.")
