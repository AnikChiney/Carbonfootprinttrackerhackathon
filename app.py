import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
if "emissions" not in st.session_state:
    st.session_state.emissions = None
    st.session_state.total_emissions = None
if "prediction" not in st.session_state:
    st.session_state.prediction = None



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

    st.session_state.emissions = emissions
    st.session_state.total_emissions = total_emissions

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
    if st.session_state.get("show_prediction", False):

        emissions = st.session_state.emissions
        total_emissions = st.session_state.total_emissions
        factors = EMISSION_FACTORS[country]
    
        pred_distance = distance * (1 - reduction_transport / 100)
        pred_electricity = electricity * (1 - reduction_electricity / 100)
        pred_meals = meals * (1 - reduction_meals / 100)
    
        prediction_breakdown = {
            "Transportation": round(factors["transport"] * pred_distance * 365 / 1000, 2),
            "Electricity": round(factors["electricity"] * pred_electricity * 12 / 1000, 2),
            "Diet": round(factors["diet"] * pred_meals * 365 / 1000, 2),
            "Waste": emissions["Waste"]  # unchanged
        }
    
        pred_total = round(sum(prediction_breakdown.values()), 2)
    
        reduction_percent = round(
            ((total_emissions - pred_total) / total_emissions) * 100, 2
        )
    
        # ✅ STORE everything safely
        st.session_state.prediction = {
            "breakdown": prediction_breakdown,
            "total": pred_total,
            "reduction_percent": reduction_percent
        }
    
        st.subheader("🤖 AI Insight")
        st.success(
            f"With these changes, you can reduce your annual emissions by "
            f"**{reduction_percent}%**, saving approximately "
            f"**{round(total_emissions - pred_total, 2)} tonnes CO₂ per year**."
        )

    # ---------------- COMPARISON CHART ----------------
    if st.session_state.prediction:

    comparison_df = pd.DataFrame({
        "Category": ["Transportation", "Electricity", "Diet", "Waste"],
        "Current": [
            st.session_state.emissions["Transportation"],
            st.session_state.emissions["Electricity"],
            st.session_state.emissions["Diet"],
            st.session_state.emissions["Waste"]
        ],
        "Predicted": [
            st.session_state.prediction["breakdown"]["Transportation"],
            st.session_state.prediction["breakdown"]["Electricity"],
            st.session_state.prediction["breakdown"]["Diet"],
            st.session_state.prediction["breakdown"]["Waste"]
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
