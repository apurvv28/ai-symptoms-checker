import streamlit as st
import pandas as pd
import joblib
import random
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
import requests
# Load trained model and vectorizer
try:
    model = joblib.load("symptom_checker_model.pkl")
    vectorizer = joblib.load("vectorizer.pkl")
except FileNotFoundError as e:
    st.error(f"Error loading model or vectorizer: {e}. Please check the file paths.")
    st.stop()

# Load symptoms from dataset
try:
    df = pd.read_csv("cleaned_dataset.csv")
except FileNotFoundError as e:
    st.error(f"Error loading dataset: {e}. Please check the file path.")
    st.stop()

# Convert symptoms to string and remove None/nan
symptoms = sorted(set(str(s) for s in df.iloc[:, 1:].values.flatten()) - {"None", "nan", ""})

# Streamlit UI
st.markdown("""
    <style>
    body {
        background-color: #f8f9fa;
        font-family: Arial, sans-serif;
    }
    .main-container {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
    <div class='main-container'>
        <h1 style='text-align: center; color: #007bff;'>🤖 AI Symptom Checker </h1>
        <h3 style='color: gray;'>🔍 Enter your symptoms below:</h3>
    </div>
    """, unsafe_allow_html=True)

st.warning("⚠️ This tool is for informational purposes only. Consult a doctor for medical advice.")

# Input fields
name = st.text_input("👤 Enter your Name:")
age = st.number_input("🎂 Enter your Age:", min_value=0, max_value=120, step=1)
gender = st.radio("⚧ Select Gender:", ("Male", "Female", "Other"))
selected_symptoms = st.multiselect("Select symptoms:", symptoms)

# Predict function
def predict_disease(symptoms):
    symptom_text = " ".join(symptoms)
    input_vectorized = vectorizer.transform([symptom_text])
    disease_probabilities = model.predict_proba(input_vectorized)[0]
    top_indices = disease_probabilities.argsort()[-3:][::-1]
    return [(model.classes_[i], round(disease_probabilities[i] * 100, 2)) for i in top_indices]

if st.button("Predict Disease"):
    if selected_symptoms:
        results = predict_disease(selected_symptoms)
        st.subheader("🩺 Possible Diseases (Ranked by Probability):")
        for disease, prob in results:
            st.write(f"🔹 **{disease}** - {prob}% confidence")
    else:
        st.warning("⚠️ Please select at least one symptom!")

# Function to generate PDF
from fpdf import FPDF

def generate_pdf(name, age, gender, symptoms, predicted_diseases):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Set font and add title with a colored rectangle
    pdf.set_fill_color(0, 0, 0)  # Black color
    pdf.set_text_color(255, 255, 255)  # White text
    pdf.set_font("Arial", "B", 20)
    pdf.cell(190, 15, " AI Symptom Checker Report ", ln=True, align="C", fill=True)
    pdf.ln(10)

    # Reset text color for content
    pdf.set_text_color(0, 0, 0)

    # User details
    pdf.set_font("Arial", "", 14)
    pdf.cell(0, 10, f"Name: {name}", ln=True)
    pdf.cell(0, 10, f"Age: {age}", ln=True)
    pdf.cell(0, 10, f"Gender: {gender}", ln=True)
    pdf.ln(5)

    # Symptoms section
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Symptoms:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, ", ".join(symptoms))
    pdf.ln(5)

    # Predicted diseases table
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Predicted Diseases:", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "", 12)
    
    # Table header
    pdf.set_fill_color(200, 200, 200)  # Light gray background
    pdf.cell(120, 10, "Disease", 1, 0, "C", fill=True)
    pdf.cell(50, 10, "Confidence", 1, 1, "C", fill=True)

    # Table rows
    for disease, confidence in predicted_diseases:
        pdf.cell(120, 10, disease, 1)
        pdf.cell(50, 10, f"{confidence:.1f}%", 1, 1, "C")

    # Save PDF
    pdf_file = "AI_Symptom_Checker_Report.pdf"
    pdf.output(pdf_file)

    return pdf_file
    
    c.save()
    return file_name

# PDF Download button
if st.button("Download Report as PDF"):
    if selected_symptoms:
        results = predict_disease(selected_symptoms)
        pdf_file = generate_pdf(name, age, gender, selected_symptoms, results)
        with open(pdf_file, "rb") as f:
            st.download_button("📄 Download Your Health Report", f, file_name="Health_Report.pdf", mime="application/pdf")
    else:
        st.warning("⚠️ Please select symptoms before generating the report!")
# 📍 FIND NEARBY DOCTORS BUTTON (NEW FEATURE)
import requests

def get_user_location():
    """Fetch user location based on IP"""
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        location = data["loc"].split(",")  # Extract latitude & longitude
        return float(location[0]), float(location[1])  # Convert to float
    except Exception as e:
        st.error(f"Error getting user location: {e}")
        return None

def get_nearby_doctors(lat, lon):
    """Fetch nearby doctors using OpenStreetMap Nominatim API"""
    try:
        url = f"https://nominatim.openstreetmap.org/search?format=json&q=doctor&limit=5&bounded=1&viewbox={lon-0.1},{lat+0.1},{lon+0.1},{lat-0.1}"
        response = requests.get(url, headers={"User-Agent": "AI-Symptom-Checker"})
        results = response.json()

        doctors = []
        for doctor in results:
            name = doctor.get("display_name", "Unknown Doctor")
            address = f"📍 {name}"
            doctors.append(address)

        return doctors if doctors else ["No nearby doctors found."]
    except Exception as e:
        st.error(f"Error fetching nearby doctors: {e}")
        return ["Error fetching data."]

# 🗺️ Streamlit UI for Nearby Doctors
st.subheader("🗺️ Find Nearby Doctors")
lat = st.number_input("Enter Latitude:", value=12.9716)  # Default: Bangalore
lon = st.number_input("Enter Longitude:", value=77.5946)  # Default: Bangalore

if st.button("Find Nearby Doctors"):
    doctors = get_nearby_doctors(lat, lon)
    for doc in doctors:
        st.write(doc)

health_tips = [
    "🧘‍♂️ Take care of your body. It's the only place you have to live.",
    "🥗 Eat healthy, stay healthy!",
    "🚶‍♂️ A 30-minute walk a day keeps the doctor away."
]
st.write(random.choice(health_tips))



        
   