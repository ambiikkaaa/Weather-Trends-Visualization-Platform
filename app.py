import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# -------------------------------
# 🌟 Page Config
# -------------------------------
st.set_page_config(page_title="Weather Dashboard", layout="wide")

# -------------------------------
# 🎨 CSS for Styling
# -------------------------------
st.markdown("""
    <style>
    .main {background-color: #f9f9f9;}
    h1, h2, h3 {font-family: 'Arial Black', sans-serif; color: #333;}
    .big-font {font-size:30px !important; font-weight: bold; color:#2E86C1;}
    .medium-font {font-size:20px !important; font-weight: bold;}
    .card {
        padding: 15px;
        border-radius: 10px;
        background-color: #000000;
        text-align: center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    img {max-width: 70%;}
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# 🔑 API Setup (use Streamlit secrets)
# -------------------------------
API_KEY = st.secrets["API_KEY"] # ✅ API key stored safely in Streamlit Cloud
BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"

# -------------------------------
# 📌 User Input
# -------------------------------
st.markdown("<h1 class='big-font'>☁️ Weather Data Visualization</h1>", unsafe_allow_html=True)
city = st.text_input("Enter a City:", "Bengaluru")

# -------------------------------
# 📌 Fetch Data
# -------------------------------
if city:
    url = f"{BASE_URL}?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # Extract forecast
        forecast_list = data["list"]
        weather_data = []
        for item in forecast_list:
            weather_data.append({
                "datetime": datetime.fromtimestamp(item["dt"]),
                "temperature": item["main"]["temp"],
                "humidity": item["main"]["humidity"],
                "wind_speed": item["wind"]["speed"],
                "weather": item["weather"][0]["main"]
            })

        df = pd.DataFrame(weather_data)

        # -------------------------------
        # 📊 Summary Cards
        # -------------------------------
        avg_temp = round(df["temperature"].mean(), 1)
        min_temp = round(df["temperature"].min(), 1)
        max_temp = round(df["temperature"].max(), 1)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<div class='card'><p class='medium-font' style='color:white;'>🌡️ Avg Temp</p><p class='big-font'>{avg_temp}°C</p></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='card'><p class='medium-font' style='color:white;'>❄️ Min Temp</p><p class='big-font'>{min_temp}°C</p></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='card'><p class='medium-font' style='color:white;'>🔥 Max Temp</p><p class='big-font'>{max_temp}°C</p></div>", unsafe_allow_html=True)

        st.markdown("---")

        # -------------------------------
        # 📈 Visualizations
        # -------------------------------
        st.subheader("1️⃣ Temperature Over Time")
        fig1 = px.line(df, x="datetime", y="temperature", markers=True,
                       title="Temperature Forecast",
                       labels={"temperature": "Temperature (°C)", "datetime": "Time"})
        fig1.update_layout(title_font=dict(size=22), font=dict(size=14))
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("2️⃣ Humidity Over Time")
        fig2 = px.bar(df, x="datetime", y="humidity", title="Humidity Levels",
                      labels={"humidity": "Humidity (%)", "datetime": "Time"})
        fig2.update_layout(title_font=dict(size=22), font=dict(size=14))
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("3️⃣ Wind Speed Variation")
        fig3 = px.area(df, x="datetime", y="wind_speed", title="Wind Speed Forecast",
                       labels={"wind_speed": "Wind Speed (m/s)", "datetime": "Time"})
        fig3.update_layout(title_font=dict(size=22), font=dict(size=14))
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader("4️⃣ Weather Condition Distribution")
        fig4 = px.pie(df, names="weather", title="Weather Condition Distribution")
        fig4.update_layout(title_font=dict(size=22), font=dict(size=14))
        st.plotly_chart(fig4, use_container_width=True)

        st.subheader("5️⃣ Temperature & Humidity Heatmap")

        if "datetime" not in df.columns:
            st.error("⚠️ No 'datetime' column found in dataset. Please check your file.")
        else:
            df["datetime"] = pd.to_datetime(df["datetime"])

            # Pivot tables for Temperature and Humidity
            pivot_temp = df.pivot_table(
                values="temperature", 
                index=df["datetime"].dt.date,
                columns=df["datetime"].dt.hour,
                aggfunc="mean"
            )

            pivot_hum = df.pivot_table(
                values="humidity", 
                index=df["datetime"].dt.date,
                columns=df["datetime"].dt.hour,
                aggfunc="mean"
            )

            # Plot side by side
            fig, axes = plt.subplots(1, 2, figsize=(16, 6))

            sns.heatmap(pivot_temp, cmap="coolwarm", ax=axes[0], cbar_kws={'label': '°C'})
            axes[0].set_title("Temperature Heatmap", fontsize=14)
            axes[0].set_xlabel("Hour of Day", fontsize=12)
            axes[0].set_ylabel("Date", fontsize=12)

            sns.heatmap(pivot_hum, cmap="YlGnBu", ax=axes[1], cbar_kws={'label': '%'})
            axes[1].set_title("Humidity Heatmap", fontsize=14)
            axes[1].set_xlabel("Hour of Day", fontsize=12)
            axes[1].set_ylabel("Date", fontsize=12)

            plt.tight_layout()
            st.pyplot(fig)
    else:
        st.error("❌ Could not fetch data. Please check city name or API key.")
