import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --------------------------
# Page Config
# --------------------------
st.set_page_config(page_title="Pricing Optimizer", layout="wide")

st.caption("Prototype: Pricing optimization under demand uncertainty (simulated marketplace data)")
st.title("Amazon Pricing Optimizer (Profit-Based)")

# --------------------------
# SKU Selection
# --------------------------
st.sidebar.header("Select Scenario")

sku = st.sidebar.selectbox(
    "Choose Product",
    ["Sashaa Decor (Validation Case)", "Suganda Skincare (Impact Case)"]
)

# --------------------------
# Default parameters
# --------------------------
if sku == "Sashaa Decor (Validation Case)":
    cost = 300
    current_price = 480
    demand_at_current = 500
    b_default = 3
    comp_min, comp_max = 420, 650
else:
    cost = 350
    current_price = 989
    demand_at_current = 300
    b_default = 0.9
    comp_min, comp_max = 700, 1200

# --------------------------
# Sidebar Inputs
# --------------------------
st.sidebar.header("Inputs")

cost = st.sidebar.number_input("Cost Price (₹)", value=cost)
current_price = st.sidebar.number_input("Current Price (₹)", value=current_price)
demand_at_current = st.sidebar.number_input("Demand at Current Price", value=demand_at_current)

b = st.sidebar.slider(
    "Demand Sensitivity (Price Impact)",
    min_value=0.1,
    max_value=10.0,
    value=float(b_default),
    step=0.1
)

comp_min = st.sidebar.number_input("Competitor Min Price", value=comp_min)
comp_max = st.sidebar.number_input("Competitor Max Price", value=comp_max)

# --------------------------
# Model Construction
# --------------------------
a = demand_at_current + b * current_price

def demand(p):
    return a - b * p

def profit(p):
    return (p - cost) * demand(p)

# --------------------------
# Optimization
# --------------------------
prices = np.linspace(comp_min, comp_max, 200)
profits = profit(prices)

optimal_price = prices[np.argmax(profits)]
max_profit = np.max(profits)
current_profit = profit(current_price)

delta_profit = max_profit - current_profit
delta_percent = (delta_profit / current_profit) * 100

# --------------------------
# Display Metrics
# --------------------------
col1, col2, col3 = st.columns(3)

col1.metric("Current Profit", f"₹{int(current_profit):,}")
col2.metric("Optimal Price", f"₹{int(optimal_price)}")
col3.metric(
    "Max Profit",
    f"₹{int(max_profit):,}",
    delta=f"{int(delta_profit):,} ({delta_percent:.1f}%)"
)

# --------------------------
# Plot
# --------------------------
fig, ax = plt.subplots()

ax.plot(prices, profits, label="Profit Curve")
ax.axvline(current_price, linestyle='--', label="Current Price")
ax.axvline(optimal_price, linestyle='--', linewidth=2, label="Optimal Price")

ax.set_xlabel("Price")
ax.set_ylabel("Profit")
ax.set_title("Profit vs Price")
ax.legend()

st.pyplot(fig)

# --------------------------
# Decision Panel
# --------------------------
st.markdown("## Decision Panel")

# Sensitivity analysis
def optimal_for_b(b_val):
    a_temp = demand_at_current + b_val * current_price
    prices_temp = np.linspace(comp_min, comp_max, 200)
    profits_temp = (prices_temp - cost) * (a_temp - b_val * prices_temp)
    return prices_temp[np.argmax(profits_temp)]

low_b = b * 0.7
high_b = b * 1.3

low_price = optimal_for_b(low_b)
high_price = optimal_for_b(high_b)

low_price, high_price = sorted([low_price, high_price])

# Layout
col1, col2 = st.columns([1, 1])

# --- LEFT: Recommendation ---
with col1:
    st.markdown("### Recommendation")

    price_diff = optimal_price - current_price

    if abs(price_diff) < 1:
        st.info(f"Recommended Price: ₹{int(optimal_price)} (≈ current price)")
    else:
        arrow = "↑" if price_diff > 0 else "↓"
        st.success(
            f"Recommended Price: ₹{int(optimal_price)} ({arrow} ₹{abs(int(price_diff))} from ₹{int(current_price)})"
        )

    st.markdown("### Impact")
    st.write(f"Expected Profit Increase: ₹{int(delta_profit):,} (+{delta_percent:.1f}%)")

# --- RIGHT: Robustness ---
with col2:
    st.markdown("### Robust Range")
    st.write(f"₹{int(low_price)} – ₹{int(high_price)}")

    st.markdown("### Interpretation")

    if abs(high_price - low_price) < 50:
        st.write("• Pricing decision is stable across demand scenarios")
    else:
        st.write("• Pricing is sensitive → better demand estimation helps")

    st.write("• Avoid frequent reactive price changes")

# --------------------------
# Explanation
# --------------------------
with st.expander("Model Explanation"):
    st.write("""
    - Demand is modeled as: D(p) = a - b*p  
    - Profit = (Price - Cost) × Demand  
    - Optimization is done within competitor price range  
    - Sensitivity (b) captures how demand reacts to price  
    """)