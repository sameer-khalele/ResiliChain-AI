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
    page_title="ResiliChain AI | Bulletproof Edition",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
    <style>
    .metric-card {background-color: #f8f9fa; border-left: 5px solid #0052cc; padding: 15px; border-radius: 8px;}
    .stTabs [data-baseweb="tab-list"] {gap: 10px;}
    .stTabs [data-baseweb="tab"] {background-color: #f0f2f6; border-radius: 5px;}
    .stTabs [aria-selected="true"] {background-color: #e6f0ff; border: 1px solid #0052cc;}
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. المترجم الذكي (يدعم العربية والإنجليزية)
# ---------------------------------------------------------
def intelligent_mapper(df):
    """
    يحاول فهم الأعمدة بذكاء شديد لتجنب القيم الافتراضية
    """
    # تنظيف أسماء الأعمدة
    df.columns = df.columns.astype(str).str.lower().str.strip()
    
    # قاموس الترجمة (عربي + إنجليزي)
    mapping = {
        # السعر
        'price': 'price', 'cost': 'price', 'unit_cost': 'price', 'سعر': 'price', 'تكلفة': 'price', 'قيمة': 'price',
        # المورد
        'supplier': 'supplier', 'vendor': 'supplier', 'name': 'supplier', 'مورد': 'supplier', 'المورد': 'supplier', 'الاسم': 'supplier',
        # الخطر
        'risk': 'risk', 'score': 'risk', 'danger': 'risk', 'خطر': 'risk', 'مخاطر': 'risk', 'rate': 'risk',
        # التأخير
        'delay': 'delay', 'time': 'delay', 'تأخير': 'delay', 'وقت': 'delay'
    }
    
    new_cols = {}
    for col in df.columns:
        matched = False
        for key, val in mapping.items():
            if key in col:
                new_cols[col] = val
                matched = True
                break
        if not matched:
            new_cols[col] = col # إبقاء الاسم كما هو إذا لم نجد تطابق
            
    df = df.rename(columns=new_cols)
    return df

# ---------------------------------------------------------
# 3. محرك التحليل (محمي من الأخطاء)
# ---------------------------------------------------------
def safe_float(val, default=0.5):
    """تحويل القيم إلى أرقام بأمان لتجنب الانهيار"""
    try:
        return float(val)
    except:
        return default

def run_bulletproof_engine(df, cycles, total_demand):
    results = []
    
    # التأكد من وجود الأعمدة، إذا لم توجد ننشئها بذكاء
    if 'supplier' not in df.columns:
        # إذا لم يوجد عمود اسم، نستخدم المؤشر
        df['supplier'] = [f"Supplier-{i}" for i in range(len(df))]

    for index, row in df.iterrows():
        supplier = str(row['supplier'])
        
        # 1. استخراج البيانات بأمان (بدون أخطاء)
        # إذا لم يجد سعراً، يولد سعراً عشوائياً بناءً على اسم المورد (ثابت لنفس الاسم)
        seed = sum(ord(c) for c in supplier) # رقم مميز للاسم
        np.random.seed(seed)
        
        price = safe_float(row.get('price'), np.random.randint(40, 120)) # سعر تقديري إذا كان مفقوداً
        risk_raw = safe_float(row.get('risk'), np.random.uniform(0.1, 0.8)) # خطر تقديري إذا كان مفقوداً
        
        # تصحيح قيمة الخطر لتكون بين 0.01 و 0.99
        risk_factor = max(0.01, min(risk_raw if risk_raw < 1.0 else risk_raw/100.0, 0.99))
        
        # 2. المحاكاة (Monte Carlo)
        # نستخدم float() للتأكد من أنها ليست Series وتسبب الخطأ السابق
        p_val = float(risk_factor)
        events = np.random.binomial(n=cycles, p=p_val)
        avg_delay = (events / cycles) * 60
        
        # القيمة المعرضة للخطر (نفترض حجم طلب افتراضي للحساب)
        exposure = (total_demand / len(df)) * price * (avg_delay / 365)
        
        resilience = 100 - (risk_factor * 100)
        
        # 3. تحديد نوع التوصية
        if resilience < 40:
            rec = "🚨 Critical: Replace"
        elif avg_delay > 15:
            rec = "⚠️ Warning: Slow"
        else:
            rec = "✅ Excellent"

        results.append({
            'Supplier': supplier,
            'Unit Price ($)': round(price, 2),
            'Risk Factor': round(risk_factor, 2),
            'Resilience Score': round(resilience, 1),
            'Avg Delay (Days)': round(avg_delay, 1),
            'Risk Exposure ($)': round(exposure, 2),
            'AI Recommendation': rec
        })
        
    results_df = pd.DataFrame(results)

    # 4. خوارزمية تقسيم الطلبات (Optimizer)
    # المعادلة: الجاذبية = (1/السعر) * (1/الخطر)
    # نستخدم .apply لحماية القسمة من الصفر
    results_df['Attractiveness'] = results_df.apply(
        lambda x: (1 / max(x['Unit Price ($)'], 1)) * (1 / max(x['Risk Factor'], 0.01)), axis=1
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
        st.title("🔒 ResiliChain AI: Secure Login")
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
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
        
        st.success("✅ System Online")
        mode = st.radio("Analysis Mode:", ["Global Supply Chain", "Local Vendors"])
        total_demand = st.number_input("Total Units Required:", value=10000, step=100)
        uploaded_file = st.file_uploader("📂 Upload Excel/CSV", type=['xlsx', 'csv'])
        
        st.markdown("---")
        if st.button("Logout"): 
            st.session_state["authenticated"] = False
            st.rerun()

    st.title(f"ResiliChain AI: {mode} Optimizer")
    
    df = None
    if uploaded_file:
        try:
            raw = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            df = intelligent_mapper(raw) # الترجمة الذكية
            st.toast("File Processed Successfully", icon="✅")
        except Exception as e:
            st.error(f"File Error: {e}")
    else:
        # بيانات تجريبية (تختلف حسب النمط)
        if mode == "Local Vendors":
            data = {
                'المورد': ['مصنع الشرق', 'مورد الجملة - وسط البلد', 'موزع الشمال'],
                'السعر': [50, 45, 60],
                'مخاطر التأخير': [0.1, 0.4, 0.05]
            }
        else:
            data = {
                'Supplier': ['Foxconn-CN', 'Bosch-DE', 'Samsung-VN'],
                'Price': [120, 150, 130],
                'Risk Score': [0.6, 0.1, 0.3]
            }
        df = intelligent_mapper(pd.DataFrame(data))
        st.info("ℹ️ Running in **Demo Mode**. Upload your file to override.")

    if st.button("🚀 Run AI Analysis", type="primary"):
        
        final_df = run_bulletproof_engine(df, 1000, total_demand)
        
        # --- التبويبات (Tabs) ---
        tab1, tab2, tab3 = st.tabs(["📊 Risk Dashboard", "🧠 AI Optimizer", "📋 Data Table"])
        
        with tab1:
            st.subheader("Risk vs. Resilience Analysis")
            c1, c2 = st.columns([2, 1])
            with c1:
                # Bubble Chart
                fig = px.scatter(final_df, x="Resilience Score", y="Risk Exposure ($)", size="Total Cost", 
                                 color="Resilience Score", color_continuous_scale="RdYlGn",
                                 hover_name="Supplier", title="Strategic Risk Matrix", size_max=60)
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                # Recommendation Bar
                fig_bar = px.bar(final_df, x='Resilience Score', y='Supplier', orientation='h',
                                 color='AI Recommendation', title="Resilience Ranking")
                st.plotly_chart(fig_bar, use_container_width=True)

        with tab2:
            st.subheader("🤖 Smart Order Allocation")
            st.markdown("Optimal split to minimize cost while maximizing safety:")
            
            c1, c2 = st.columns(2)
            with c1:
                fig_pie = px.pie(final_df, values='Order Qty', names='Supplier', hole=0.4,
                                 title="Suggested Volume Split")
                st.plotly_chart(fig_pie, use_container_width=True)
            with c2:
                best = final_df.loc[final_df['Allocated %'].idxmax()]
                st.success(f"🏆 **Best Vendor:** {best['Supplier']}")
                st.write(f"Allocation: **{best['Allocated %']:.1%}** ({best['Order Qty']:,} Units)")
                st.caption(f"Reason: Best balance of Price (${best['Unit Price ($)']}) and Low Risk.")
                
                st.dataframe(final_df[['Supplier', 'Allocated %', 'Order Qty', 'Total Cost']].style.format({
                    'Allocated %': '{:.1%}', 'Total Cost': '${:,.2f}'
                }))

        with tab3:
            st.dataframe(final_df)
