import streamlit as st
import pandas as pd

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

st.markdown(
    """
    Estimate your **annual carbon emissions** based on daily habits.
    Small changes can make a **big environmental impact** 🌍
    """
)

st.divider()

# ---------------- INPUTS ----------------
st.subheader("📍 Location")
country = st.selectbox("Select your country", ["India"])

col1, col2 = st.columns(2)

with col1:
    distance = st.slider(
        "🚗 Daily travel distance (km)",
        0.0, 100.0, 10.0,
        help="Includes commute and personal travel"
    )

    electricity = st.slider(
        "💡 Monthly electricity usage (kWh)",
        0.0, 1000.0, 200.0,
        help="Approximate household electricity usage"
    )

with col2:
    meals = st.number_input(
        "🍽️ Meals per day",
        min_value=0,
        value=3,
        help="Average number of meals you consume daily"
    )

    waste = st.slider(
        "🗑️ Waste generated per week (kg)",
        0.0, 100.0, 5.0,
        help="Household waste including food & packaging"
    )

st.divider()

# ---------------- CALCULATE ----------------
if st.button("📊 Calculate Carbon Footprint", use_container_width=True):

    emissions, total = calculate_emissions(
        distance, electricity, meals, waste, country
    )

    st.header("📈 Results")

    # -------- METRICS --------
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🚗 Transport", f"{emissions['Transportation']} t")
    c2.metric("💡 Electricity", f"{emissions['Electricity']} t")
    c3.metric("🍽️ Diet", f"{emissions['Diet']} t")
    c4.metric("🗑️ Waste", f"{emissions['Waste']} t")

    st.subheader("🌍 Total Carbon Footprint")
    st.success(f"**{total} tonnes CO₂ per year**")

    # -------- CHART --------
    df = pd.DataFrame.from_dict(
        emissions, orient="index", columns=["Tonnes CO₂"]
    )

    st.bar_chart(df)

    # -------- INSIGHT --------
    st.info(
        """
        🇮🇳 **India’s per-capita CO₂ emissions (2021): ~1.9 tonnes/year**

        - If your footprint is **above this**, consider energy-efficient appliances,
          public transport, or dietary changes.
        - If it's **below**, you're already contributing positively 🌱
        """
    )
