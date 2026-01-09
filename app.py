import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# ---------------------------------------------------------
# 1. إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(page_title="ResiliChain AI | Enterprise Commander", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .metric-card {background-color: #ffffff; border-left: 5px solid #0052cc; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);}
    .scenario-active {background-color: #fff3cd; border: 1px solid #ffeeba; padding: 10px; border-radius: 5px; color: #856404;}
    .reason-box {font-size: 0.9em; color: #555;}
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. المترجم الذكي & القالب
# ---------------------------------------------------------
def intelligent_mapper(df):
    df.columns = df.columns.astype(str).str.lower().str.strip()
    mapping = {
        'price': 'price', 'cost': 'price', 'unit_cost': 'price', 'سعر': 'price', 'تكلفة': 'price',
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

def get_template_csv():
    # نموذج قياسي ليحمله العميل
    df = pd.DataFrame({
        'Supplier_Name': ['Vendor A', 'Vendor B', 'Vendor C'],
        'Unit_Cost': [100, 120, 90],
        'Risk_Score_0_to_1': [0.1, 0.05, 0.4]
    })
    return df.to_csv(index=False).encode('utf-8')

# ---------------------------------------------------------
# 3. محرك السيناريوهات والقيود (The Core Logic)
# ---------------------------------------------------------
def run_enterprise_engine(df, total_demand, strategy, max_cap, risk_surge, price_surge, excluded_suppliers):
    results = []
    
    # تحويل استراتيجية المستخدم (0-100) إلى أوزان رياضية
    # Strategy 0 = Safety (Risk Weight High), 100 = Cost (Price Weight High)
    p_weight = 0.5 + (strategy / 100)
    r_weight = 1.5 - (strategy / 100)
    
    for index, row in df.iterrows():
        supplier = str(row.get('supplier', f'Sup-{index}'))
        
        # 1️⃣ تطبيق السيناريوهات (What-If Analysis)
        base_price = float(row.get('price', 50))
        base_risk = float(row.get('risk', 0.5))
        
        # تعديل الأسعار والمخاطر بناءً على السيناريو
        simulated_price = base_price * (1 + price_surge/100)
        simulated_risk = base_risk * (1 + risk_surge/100)
        simulated_risk = max(0.01, min(simulated_risk, 0.99)) # تثبيت الخطر بين 1% و 99%
        
        # التحقق من الاستبعاد (Supplier Unavailable Scenario)
        is_excluded = supplier in excluded_suppliers
        
        # حساب الجاذبية (Attractiveness Score)
        if is_excluded:
            attraction = 0
            reason = "⛔ Excluded by Scenario"
        else:
            attraction = (1 / (simulated_price ** p_weight)) * (1 / (simulated_risk ** r_weight))
            reason = "✅ Active"

        results.append({
            'Supplier': supplier,
            'Base Price': base_price,
            'Simulated Price': round(simulated_price, 2),
            'Simulated Risk': round(simulated_risk, 2),
            'Resilience %': round((1 - simulated_risk) * 100, 1),
            'Attraction': attraction,
            'Status Note': reason
        })
    
    res_df = pd.DataFrame(results)
    
    # 2️⃣ تطبيق القيود (Constraints Logic)
    total_attr = res_df['Attraction'].sum()
    
    if total_attr == 0:
        res_df['Allocated %'] = 0
    else:
        res_df['Raw_Split'] = res_df['Attraction'] / total_attr
        
        # تطبيق الحد الأقصى (Max Cap) وإعادة توزيع الفائض
        # نقوم بعملية التوزيع على مرحلتين لضمان الدقة
        res_df['Allocated %'] = res_df['Raw_Split'].clip(upper=max_cap/100)
        
        # حساب الفائض
        remainder = 1.0 - res_df['Allocated %'].sum()
        
        # توزيع الفائض على الموردين الذين لم يصلوا للحد الأقصى (وغير مستبعدين)
        if remainder > 0.001:
            eligible = (res_df['Allocated %'] < (max_cap/100)) & (res_df['Attraction'] > 0)
            if eligible.any():
                # نوزع الفائض بالتناسب
                res_df.loc[eligible, 'Allocated %'] += remainder * (res_df.loc[eligible, 'Allocated %'] / res_df.loc[eligible, 'Allocated %'].sum())
                # تأكيد أخير للقيد
                res_df['Allocated %'] = res_df['Allocated %'].clip(upper=max_cap/100)

    # حساب الكميات النهائية
    res_df['Order Qty'] = (res_df['Allocated %'] * total_demand).astype(int)
    res_df['Total Cost'] = res_df['Order Qty'] * res_df['Simulated Price']
    
    # 3️⃣ التبرير العميق (Why Not?)
    # نضيف عمود يشرح لماذا حصل هذا المورد على هذه النسبة
    def explain_logic(row):
        if row['Status Note'].startswith("⛔"):
            return "Forcefully excluded by user scenario."
        if row['Allocated %'] >= (max_cap/100 - 0.01):
            return f"⚠️ Capped at {max_cap}% constraint limit (Could have taken more)."
        if row['Allocated %'] < 0.05:
            if row['Simulated Price'] > res_df['Simulated Price'].mean():
                return f"📉 Share limited due to High Price (+${row['Simulated Price'] - res_df['Simulated Price'].mean():.0f} vs avg)."
            if row['Simulated Risk'] > res_df['Simulated Risk'].mean():
                return "📉 Share limited due to High Risk instability."
        return "✅ Balanced allocation based on strategy."

    res_df['AI Reasoning'] = res_df.apply(explain_logic, axis=1)
    
    return res_df

# ---------------------------------------------------------
# 4. واجهة التطبيق
# ---------------------------------------------------------
SUBSCRIBERS_DB = {"admin": "admin2026", "demo": "demo123"}

if "authenticated" not in st.session_state: st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔒 ResiliChain AI: Enterprise Login")
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if user in SUBSCRIBERS_DB and SUBSCRIBERS_DB[user] == pwd:
                st.session_state["authenticated"] = True
                st.rerun()
else:
    # --- Sidebar ---
    with st.sidebar:
        if os.path.exists("logo.png"): st.image("logo.png", width=200)
        else: st.title("ResiliChain AI")
        
        st.markdown("### 📥 Step 1: Data Standard")
        st.download_button("Download Excel Template", get_template_csv(), "resilichain_template.csv", help="Use this file for best accuracy.")
        uploaded_file = st.file_uploader("Upload Data", type=['xlsx', 'csv'])
        
        st.markdown("---")
        st.markdown("### ⚙️ Step 2: Constraints")
        max_alloc = st.slider("Max Cap per Supplier (%)", 10, 100, 40, help="No single supplier gets more than this.")
        strategy = st.slider("Strategy:", 0, 100, 30, help="0=Safety First, 100=Cost First")
        
        st.markdown("---")
        st.markdown("### 🌪️ Step 3: What-If Scenario")
        st.caption("Simulate market disruptions:")
        risk_surge = st.slider("Global Risk Surge (%)", 0, 100, 0)
        price_surge = st.slider("Price Inflation (%)", 0, 50, 0)
        
        # القائمة المنسدلة لاستبعاد موردين تظهر فقط بعد تحميل البيانات
        exclude_list = []
        if uploaded_file:
             # قراءة سريعة فقط لجلب الأسماء للقائمة
             try:
                 temp_df = intelligent_mapper(pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file))
                 exclude_list = st.multiselect("Simulate Supplier Failure:", temp_df['supplier'].unique())
             except: pass

        if st.button("Logout"): 
            st.session_state["authenticated"] = False
            st.rerun()

    # --- Main Dashboard ---
    st.title("🛡️ Supply Chain Command Center")
    
    if uploaded_file:
        df = intelligent_mapper(pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file))
        
        # تشغيل المحرك مع السيناريوهات
        final_df = run_enterprise_engine(df, 10000, strategy, max_alloc, risk_surge, price_surge, exclude_list)
        
        # تنبيه إذا كان هناك سيناريو نشط
        if risk_surge > 0 or price_surge > 0 or exclude_list:
            st.markdown(f"""
            <div class="scenario-active">
                ⚠️ <b>Active Scenario Simulation:</b> Risk +{risk_surge}% | Price +{price_surge}% | Excluded: {len(exclude_list)}
            </div>
            """, unsafe_allow_html=True)
            
        # --- تبويبات النتائج ---
        tab1, tab2, tab3 = st.tabs(["🧠 AI Optimization", "🌪️ Scenario Impact", "📋 Explainable Data"])
        
        with tab1:
            st.subheader("Optimized Allocation")
            c1, c2 = st.columns([1, 1])
            with c1:
                fig = px.pie(final_df, values='Order Qty', names='Supplier', hole=0.5, 
                             title="Suggested Split", color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                # عرض أفضل مورد مع السبب
                winner = final_df.loc[final_df['Allocated %'].idxmax()]
                st.success(f"🏆 **Winner:** {winner['Supplier']} ({winner['Allocated %']:.1%})")
                st.info(f"💡 **Why?** {winner['AI Reasoning']}")
                
                # عرض من تم تقييدهم
                capped = final_df[final_df['AI Reasoning'].str.contains("Capped")]
                if not capped.empty:
                    st.warning(f"⚠️ **Constraint Applied:** {len(capped)} supplier(s) hit the {max_alloc}% limit.")

        with tab2:
            st.subheader("Scenario vs Baseline Analysis")
            # مقارنة سريعة
            total_cost = final_df['Total Cost'].sum()
            avg_risk = final_df['Simulated Risk'].mean() * 100
            
            k1, k2, k3 = st.columns(3)
            k1.metric("Projected Cost", f"${total_cost:,.0f}", delta=f"{price_surge}% Inflation", delta_color="inverse")
            k2.metric("Network Risk", f"{avg_risk:.1f}%", delta=f"{risk_surge}% Surge", delta_color="inverse")
            k3.metric("Active Suppliers", len(final_df[final_df['Allocated %'] > 0]), delta=f"-{len(exclude_list)} Unavailable")
            
            # Bubble Chart مع التأثير
            
            fig_bub = px.scatter(final_df, x="Simulated Risk", y="Simulated Price", size="Order Qty", color="Supplier",
                                 title="Scenario Risk Map (Size = Allocation)", hover_data=['AI Reasoning'])
            st.plotly_chart(fig_bub, use_container_width=True)

        with tab3:
            st.subheader("Deep Explainability Report")
            # جدول تفاعلي يشرح الأسباب
            st.dataframe(
                final_df[['Supplier', 'Allocated %', 'Simulated Price', 'Simulated Risk', 'AI Reasoning']]
                .style.format({'Allocated %': '{:.1%}', 'Simulated Price': '${:.1f}', 'Simulated Risk': '{:.2f}'})
                .applymap(lambda v: 'color: red;' if 'Excluded' in str(v) else ('color: orange;' if 'Capped' in str(v) else ''), subset=['AI Reasoning'])
            )
            
    else:
        st.info("👈 Start by downloading the Template, filling it, and uploading it.")
