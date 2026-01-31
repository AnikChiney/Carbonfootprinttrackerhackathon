import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="CarbonLensAI",
    layout="wide"
)

# ---------------- DATA ----------------
EMISSION_FACTORS = {
    "India": {
        "transport": 0.14,      # kg CO2 per km
        "electricity": 0.82,    # kg CO2 per kWh
        "diet": 1.25,           # kg CO2 per meal
        "waste": 0.1            # kg CO2 per kg
    }
}

# ---------------- FUNCTIONS ----------------
def calculate_emissions(distance, electricity, meals, waste, country):
    factors = EMISSION_FACTORS[country]

    transport = factors["transport"] * distance * 365
    electricity = factors["electricity"] * electricity * 12
    diet = factors["diet"] * meals * 365
    waste = factors["waste"] * waste * 52

    data = {
        "Transportation": round(transport / 1000, 2),
        "Electricity": round(electricity / 1000, 2),
        "Diet": round(diet / 1000, 2),
        "Waste": round(waste / 1000, 2),
    }

    total = round(sum(data.values()), 2)
    return data, total

# ---------------- UI ----------------
st.title("🌱 CarbonLens AI")

st.markdown("""
Estimate your **annual carbon emissions** based on daily habits.  
Small changes can make a **big environmental impact** 🌍
""")

st.divider()

# ---------------- INPUTS ----------------
st.subheader("📍 Location")
country = st.selectbox("Select your country", ["India"])

col1, col2 = st.columns(2)

with col1:
    distance = st.slider("🚗 Daily travel distance (km)", 0.0, 100.0, 10.0)
    electricity = st.slider("💡 Monthly electricity usage (kWh)", 0.0, 1000.0, 200.0)

with col2:
    meals = st.number_input("🍽️ Meals per day", min_value=0, value=3)
    waste = st.slider("🗑️ Waste generated per week (kg)", 0.0, 100.0, 5.0)

st.divider()

# ---------------- CALCULATE ----------------
if st.button("📊 Calculate Carbon Footprint", use_container_width=True):

    emissions, total_emissions = calculate_emissions(
        distance, electricity, meals, waste, country
    )

    st.header("📈 Current Results")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🚗 Transport", f"{emissions['Transportation']} t")
    c2.metric("💡 Electricity", f"{emissions['Electricity']} t")
    c3.metric("🍽️ Diet", f"{emissions['Diet']} t")
    c4.metric("🗑️ Waste", f"{emissions['Waste']} t")

    st.success(f"🌍 **Total: {total_emissions} tonnes CO₂ per year**")

    df = pd.DataFrame.from_dict(emissions, orient="index", columns=["Tonnes CO₂"])
    st.bar_chart(df)

    # ---------------- PREDICTIVE MODEL ----------------
    st.divider()
st.subheader("🔮 Predictive Impact: Lifestyle Changes")

# --- Sliders (inputs only) ---
reduction_transport = st.slider(
    "Reduce daily commute (%)", 0, 50, 30, key="red_transport"
)
reduction_electricity = st.slider(
    "Reduce electricity usage (%)", 0, 50, 40, key="red_electricity"
)
reduction_meals = st.slider(
    "Reduce high-carbon meals (%)", 0, 50, 10, key="red_meals"
)

# --- Button to apply scenario ---
apply_changes = st.button("▶ Apply Lifestyle Changes")

# --- Run only after button click ---
if apply_changes:
    st.session_state["show_prediction"] = True

if st.session_state.get("show_prediction", False):

    # Apply reductions
    pred_distance = distance * (1 - reduction_transport / 100)
    pred_electricity = electricity * (1 - reduction_electricity / 100)
    pred_meals = meals * (1 - reduction_meals / 100)

    factors = EMISSION_FACTORS[country]

    pred_transport = factors["transport"] * pred_distance * 365 / 1000
    pred_electricity = factors["electricity"] * pred_electricity * 12 / 1000
    pred_diet = factors["diet"] * pred_meals * 365 / 1000
    pred_waste = factors["waste"]  # unchanged

    pred_total = round(
        pred_transport + pred_electricity + pred_diet + pred_waste, 2
    )

    reduction_percent = round(
        ((total_emissions - pred_total) / total_emissions) * 100, 2
    )

    # --- Output ---
    st.subheader("🤖 AI Insight")
    st.success(
        f"With these changes, you can reduce your annual emissions by "
        f"**{reduction_percent}%**, saving approximately "
        f"**{round(total_emissions - pred_total, 2)} tonnes CO₂ per year**."
    )


    # ---------------- COMPARISON CHART ----------------
    comparison_df = pd.DataFrame({
        "Category": ["Transportation", "Electricity", "Diet", "Waste"],
        "Current": [
            emissions["Transportation"],
            emissions["Electricity"],
            emissions["Diet"],
            emissions["Waste"]
        ],
        "Predicted": [
            round(pred_transport, 2),
            round(pred_electricity, 2),
            round(pred_diet, 2),
            pred_waste
        ]
    })

    st.subheader("📊 Current vs Predicted Emissions")

    fig, ax = plt.subplots()
    x = range(len(comparison_df))
    bar_width = 0.35

    ax.bar(x, comparison_df["Current"], width=bar_width, label="Current")
    ax.bar(
        [i + bar_width for i in x],
        comparison_df["Predicted"],
        width=bar_width,
        label="Predicted"
    )

    ax.set_xticks([i + bar_width / 2 for i in x])
    ax.set_xticklabels(comparison_df["Category"])
    ax.set_ylabel("Tonnes CO₂ / year")
    ax.set_title("Impact of Lifestyle Changes")
    ax.legend()

    st.pyplot(fig)

    # ---------------- TOTAL COMPARISON ----------------
    st.subheader("🌍 Total Footprint Comparison")

    total_df = pd.DataFrame({
        "Type": ["Current", "Predicted"],
        "Emissions": [total_emissions, pred_total]
    })

    fig2, ax2 = plt.subplots()
    ax2.bar(total_df["Type"], total_df["Emissions"])
    ax2.set_ylabel("Tonnes CO₂ / year")
    ax2.set_title("Overall Carbon Reduction")

    st.pyplot(fig2)
