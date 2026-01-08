# Import necessary libraries
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. Page Configuration (Branding)
# ---------------------------------------------------------
st.set_page_config(
    page_title="ResiliChain AI | Supply Chain Stress-Test",
    page_icon="🔗",
    layout="wide"
)

# Sidebar for User Inputs
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1584/1584892.png", width=80) # Placeholder Icon
    st.title("ResiliChain AI")
    st.subheader("Simulation Parameters")
    
    simulation_cycles = st.slider("Monte Carlo Cycles (Scenarios)", 100, 5000, 1000)
    global_risk_factor = st.slider("Global Disruption Probability (%)", 0, 100, 15)
    
    st.markdown("---")
    st.write("Created by: Sameer Khalele")
    st.write("© 2026 ResiliChain AI")

# ---------------------------------------------------------
# 2. Main Dashboard Header
# ---------------------------------------------------------
st.title("🛡️ ResiliChain AI: Supply Chain Stress-Testing Engine")
st.markdown("""
> **System Status:** Active  
> **Objective:** Proactive detection of supply chain breaks before they occur.
""")

st.markdown("---")

# ---------------------------------------------------------
# 3. Data Generation (Mock Supply Chain Data)
# ---------------------------------------------------------
# In a real app, this would come from an Excel/SQL database
data = {
    'Supplier_ID': ['SUP-001', 'SUP-002', 'SUP-003', 'SUP-004', 'SUP-005'],
    'Location': ['Shanghai, China', 'Hamburg, Germany', 'Ho Chi Minh, Vietnam', 'Texas, USA', 'Mumbai, India'],
    'Component': ['Microchips', 'Steel Chassis', 'Rubber Gaskets', 'Processors', 'Plastic Casings'],
    'Lead_Time_Days': [45, 20, 30, 10, 35],
    'Base_Risk_Score': [0.6, 0.2, 0.5, 0.1, 0.4], # 0 = Safe, 1 = High Risk
    'Inventory_Value_USD': [150000, 80000, 40000, 200000, 50000]
}

df = pd.DataFrame(data)

# ---------------------------------------------------------
# 4. The Simulation Engine (The "Brain")
# ---------------------------------------------------------
def run_stress_test(dataframe, cycles, external_risk):
    """
    Runs a Monte Carlo simulation to predict delays and financial impact.
    """
    results = []
    
    for index, row in dataframe.iterrows():
        # Simulate 'cycles' number of scenarios
        # Logic: Risk = Base Risk + Global External Risk (User Input)
        total_risk_prob = row['Base_Risk_Score'] + (external_risk / 100.0)
        
        # Simulating days delayed based on risk probability
        # Using a binomial distribution to simulate event occurrence
        disruption_events = np.random.binomial(n=cycles, p=min(total_risk_prob, 1.0))
        avg_delay_days = (disruption_events / cycles) * 30 # Assuming max 30 days delay impact
        
        # Calculate Financial Impact (Value at Risk)
        # Simple formula: Value * (Delay / 365) * Severity Factor
        value_at_risk = row['Inventory_Value_USD'] * (avg_delay_days / 90) 
        
        results.append({
            'Supplier_ID': row['Supplier_ID'],
            'Predicted_Delay_Days': round(avg_delay_days, 1),
            'Value_at_Risk_USD': round(value_at_risk, 2),
            'Resilience_Score': round(100 - (total_risk_prob * 100), 1)
        })
        
    return pd.DataFrame(results)

# Run the simulation
if st.button('🚀 Run Stress-Test Simulation'):
    with st.spinner('Simulating global logistics scenarios...'):
        sim_results = run_stress_test(df, simulation_cycles, global_risk_factor)
        
        # Merge results with original data
        final_df = pd.merge(df, sim_results, on='Supplier_ID')
        
        # ---------------------------------------------------------
        # 5. Visualizing the Impact (Dashboard)
        # ---------------------------------------------------------
        
        # KPI Metrics
        col1, col2, col3 = st.columns(3)
        total_risk = final_df['Value_at_Risk_USD'].sum()
        avg_resilience = final_df['Resilience_Score'].mean()
        
        col1.metric("Total Value at Risk (VaR)", f"${total_risk:,.2f}", delta_color="inverse")
        col2.metric("Avg Network Resilience", f"{avg_resilience}%", delta_color="normal" if avg_resilience > 70 else "inverse")
        col3.metric("Scenarios Simulated", f"{simulation_cycles:,}")

        # Charts
        st.subheader("📊 Visual Analysis")
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("**Financial Impact by Supplier**")
            fig_bar = px.bar(final_df, x='Supplier_ID', y='Value_at_Risk_USD', 
                             color='Value_at_Risk_USD', 
                             color_continuous_scale='Reds',
                             title="Revenue at Risk ($)")
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with c2:
            st.markdown("**Resilience vs. Lead Time**")
            fig_scatter = px.scatter(final_df, x='Lead_Time_Days', y='Resilience_Score',
                                     size='Inventory_Value_USD', color='Supplier_ID',
                                     title="Vulnerability Matrix")
            st.plotly_chart(fig_scatter, use_container_width=True)

        # ---------------------------------------------------------
        # 6. Actionable Insights (The "Proactive" Part)
        # ---------------------------------------------------------
        st.subheader("🚨 Critical Alerts & Plan B Suggestions")
        
        critical_suppliers = final_df[final_df['Resilience_Score'] < 50]
        
        if not critical_suppliers.empty:
            for i, row in critical_suppliers.iterrows():
                st.error(f"**CRITICAL ALERT:** {row['Supplier_ID']} ({row['Location']}) has failed the stress test.")
                st.info(f"👉 **Recommendation:** Activate backup supplier in **Mexico** or **Turkey**. Increase safety stock for {row['Component']} by 20%.")
        else:
            st.success("All suppliers passed the stress test within acceptable limits.")

        # Display Data Table
        with st.expander("View Detailed Data Report"):
            st.dataframe(final_df)

else:
    st.info("👈 Adjust parameters in the sidebar and click 'Run Stress-Test Simulation' to start.")
    # Show initial data
    st.write("Current Supply Chain Configuration:")
    st.dataframe(df)