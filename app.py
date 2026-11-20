
import streamlit as st
from pypdf import PdfReader
import google.generativeai as genai
from dotenv import load_dotenv
import os
import re
from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


# -----------------------------
# PAGE CONFIGURATION
# -----------------------------
st.set_page_config(
    page_title="MediSimplify AI | Medical Report Simplifier",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# -----------------------------
# CUSTOM CSS
# -----------------------------
st.markdown("""
<style>
.main {
    background-color: #ffffff;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.feature-card {
    background-color: #f0f7f8;
    border: 1px solid #d5e8eb;
    border-radius: 12px;
    padding: 20px;
    min-height: 155px;
    margin-bottom: 15px;
}

.feature-card h4 {
    color: #167D8D;
    margin-bottom: 10px;
    font-size: 18px;
}

.feature-card p {
    color: #555555;
    font-size: 14px;
    line-height: 1.5;
}

.hero {
    text-align: center;
    padding: 25px 10px;
}

.hero h1 {
    color: #167D8D;
    font-size: 44px;
    margin-bottom: 8px;
}

.hero h3 {
    color: #555555;
    font-weight: 500;
}

.hero p {
    color: #777777;
    font-size: 17px;
}

.section-heading {
    color: #167D8D;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


# -----------------------------
# API KEY SETUP
# -----------------------------
load_dotenv()

api_key = None

try:
    api_key = st.secrets.get("GEMINI_API_KEY", None)
except Exception:
    api_key = None

if not api_key:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error(
        "GEMINI_API_KEY not found. Add it in Streamlit Secrets or your .env file."
    )
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")


# -----------------------------
# PDF GENERATOR
# -----------------------------
def create_pdf(report_text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []

    story.append(
        Paragraph(
            "MediSimplify AI - Medical Report Simplifier",
            styles["Title"]
        )
    )

    story.append(Spacer(1, 12))

    for line in report_text.split("\n"):
        line = line.replace("##", "")
        line = line.replace("**", "")
        line = line.replace("*", "•")
        line = escape(line)

        if line.strip():
            story.append(Paragraph(line, styles["Normal"]))
            story.append(Spacer(1, 6))

    doc.build(story)
    buffer.seek(0)

    return buffer


# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("🏥 MediSimplify AI")

st.sidebar.markdown("""
### Medical Report Simplifier

Understand your medical reports in simple language with the help of Generative AI.

---

### About the Project

MediSimplify AI is designed to make complex medical reports easier to understand.

### How to Use

1. Enter patient details.
2. Upload your medical report PDF.
3. Click Simplify Report.
4. Review the AI-generated explanation.
5. Download your simplified report.

---

### Features

- Medical Report Simplification
- Health Information
- BMI Calculator
- Medicine Explanation
- Chat with Report
- PDF Downloads

---

### Developed By

**Mukesh**

---

<small>For educational purposes only. Not a replacement for professional medical advice.</small>
""", unsafe_allow_html=True)


# -----------------------------
# HOMEPAGE HEADER
# -----------------------------
st.markdown("""
<div class="hero">
    <h1>🏥 MediSimplify AI</h1>
    <h3>AI-Powered Medical Document Intelligence System</h3>
    <p>
        Understand your medical reports in simple language.
        Make more informed conversations with your doctor.
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()


# -----------------------------
# MEDICAL DISCLAIMER
# -----------------------------
st.info(
    "⚠️ Medical Disclaimer: This AI-generated explanation is for educational "
    "purposes only. It is not a medical diagnosis and must not replace advice "
    "from a qualified healthcare professional. Always consult your doctor "
    "before making medical decisions."
)


# -----------------------------
# FEATURE CARDS
# -----------------------------
st.markdown("""
<h2 style="text-align:center; color:#167D8D;">
    Explore MediSimplify AI Features
</h2>
<p style="text-align:center; color:#777;">
    Tools designed to help you understand your medical information.
</p>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h4>📄 Report Simplification</h4>
        <p>
        Convert complex medical reports into simple,
        understandable language.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h4>📊 Health Insights</h4>
        <p>
        Understand important report values and review
        AI-generated summaries.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <h4>💊 Medicine Explanation</h4>
        <p>
        Read general explanations of medicines,
        their purposes and precautions.
        </p>
    </div>
    """, unsafe_allow_html=True)

col4, col5, col6 = st.columns(3)

with col4:
    st.markdown("""
    <div class="feature-card">
        <h4>❤️ Health Information</h4>
        <p>
        Record patient details, BMI, lifestyle
        information and vital signs.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown("""
    <div class="feature-card">
        <h4>💬 Chat with Report</h4>
        <p>
        Ask questions and receive simple explanations
        based on your report.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown("""
    <div class="feature-card">
        <h4>📥 Download Reports</h4>
        <p>
        Download your simplified medical report
        in PDF or text format.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.divider()


# -----------------------------
# PATIENT DETAILS
# -----------------------------
st.markdown("## 👤 Patient Details")

patient_name = st.text_input("Patient Name")

patient_age = st.number_input(
    "Age",
    min_value=1,
    max_value=120,
    step=1,
    value=30
)

patient_gender = st.selectbox(
    "Gender",
    ["Select", "Male", "Female", "Other"]
)

report_date = st.date_input("Report Date")

hospital_name = st.text_input("Hospital / Lab Name")


# -----------------------------
# BMI CALCULATOR
# -----------------------------
st.markdown("## ⚖️ BMI Calculator")

height_cm = st.number_input(
    "Height (cm)",
    min_value=50,
    max_value=250,
    step=1,
    value=170
)

weight_kg = st.number_input(
    "Weight (kg)",
    min_value=10,
    max_value=300,
    step=1,
    value=70
)

bmi = weight_kg / ((height_cm / 100) ** 2)

st.info(f"Your BMI is: {bmi:.2f}")

if bmi < 18.5:
    st.warning("BMI Category: Underweight")
elif bmi < 25:
    st.success("BMI Category: Normal")
elif bmi < 30:
    st.warning("BMI Category: Overweight")
else:
    st.error("BMI Category: Obese")


# -----------------------------
# ADDITIONAL PATIENT INFORMATION
# -----------------------------
st.markdown("## 🩺 Additional Patient Information")

blood_group = st.selectbox(
    "Blood Group",
    ["Select", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
)

emergency_contact = st.text_input(
    "Emergency Contact Number",
    placeholder="Enter emergency contact number"
)

allergies = st.text_area(
    "Known Allergies",
    placeholder="Example: Penicillin, Peanuts, Dust allergy..."
)

medical_history = st.text_area(
    "Previous Medical Conditions",
    placeholder="Example: Diabetes, Hypertension, Asthma..."
)

current_medications = st.text_area(
    "Current Medications",
    placeholder="Example: Paracetamol, Metformin..."
)

past_surgeries = st.text_area(
    "Past Surgeries",
    placeholder="Example: Appendix surgery in 2021"
)

family_history = st.text_area(
    "Family Medical History",
    placeholder="Example: Father has diabetes..."
)


# -----------------------------
# LIFESTYLE INFORMATION
# -----------------------------
st.markdown("## 🏃 Lifestyle Information")

smoking = st.selectbox(
    "Do you smoke?",
    ["No", "Occasionally", "Regularly"]
)

alcohol = st.selectbox(
    "Do you consume alcohol?",
    ["No", "Occasionally", "Regularly"]
)

exercise = st.selectbox(
    "Exercise Frequency",
    [
        "Daily",
        "3-5 times/week",
        "1-2 times/week",
        "Rarely",
        "Never"
    ]
)

diet = st.selectbox(
    "Diet Type",
    ["Vegetarian", "Non-Vegetarian", "Vegan", "Mixed"]
)

sleep_hours = st.slider(
    "Average Sleep (hours/day)",
    1,
    12,
    7
)

water_intake = st.slider(
    "Average Water Intake (Litres/day)",
    1,
    10,
    3
)

stress_level = st.slider(
    "Stress Level",
    1,
    10,
    5
)


# -----------------------------
# VITAL SIGNS
# -----------------------------
st.markdown("## ❤️ Vital Signs")

blood_pressure = st.text_input(
    "Blood Pressure",
    placeholder="Example: 120/80 mmHg"
)

heart_rate = st.number_input(
    "Heart Rate (BPM)",
    min_value=30,
    max_value=200,
    value=72
)

body_temperature = st.number_input(
    "Body Temperature (°C)",
    min_value=30.0,
    max_value=45.0,
    value=36.5,
    step=0.1
)

oxygen_level = st.slider(
    "Oxygen Saturation (SpO₂ %)",
    70,
    100,
    98
)


# -----------------------------
# HEALTH GOALS
# -----------------------------
st.markdown("## 🎯 Health Goals")

health_goal = st.selectbox(
    "Primary Health Goal",
    [
        "General Health Checkup",
        "Weight Loss",
        "Weight Gain",
        "Control Diabetes",
        "Control Blood Pressure",
        "Improve Heart Health",
        "Improve Fitness",
        "Other"
    ]
)


# -----------------------------
# PDF UPLOAD
# -----------------------------
st.markdown("## 📄 Upload Your Medical Report")

uploaded_file = st.file_uploader(
    "Choose your medical report PDF",
    type=["pdf"]
)

if uploaded_file:

    try:
        reader = PdfReader(uploaded_file)
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    except Exception as e:
        st.error(f"Unable to read the PDF: {e}")
        st.stop()

    if not text.strip():
        st.warning(
            "No readable text was found in this PDF. "
            "It may be a scanned document that requires OCR."
        )
        st.stop()

    st.success("✅ PDF uploaded successfully!")

    with st.expander("📄 View Extracted Text (Optional)"):
        st.text_area(
            "Report Content",
            text,
            height=300
        )

    if st.button("✨ Simplify Report", type="primary"):

        if (
            not patient_name.strip()
            or patient_gender == "Select"
            or not hospital_name.strip()
        ):
            st.warning(
                "Please fill Patient Name, Gender, and Hospital/Lab Name "
                "before simplifying."
            )
            st.stop()

        # Limit PDF text to avoid Gemini timeout
        text = text[:12000]

        prompt = f"""
You are an AI Medical Report Simplifier.

Explain the report in simple English.
Do not invent medical values or make a diagnosis.
Clearly distinguish between report findings and general information.
If a value is not available, say that it is not provided.

Patient Information:
Name: {patient_name}
Age: {patient_age}
Gender: {patient_gender}
Report Date: {report_date}
Hospital/Lab: {hospital_name}
Blood Group: {blood_group}
BMI: {bmi:.2f}
Allergies: {allergies}
Medical History: {medical_history}
Current Medications: {current_medications}
Past Surgeries: {past_surgeries}
Family Medical History: {family_history}
Emergency Contact: {emergency_contact}
Health Goal: {health_goal}

Lifestyle:
Smoking: {smoking}
Alcohol: {alcohol}
Exercise: {exercise}
Diet: {diet}
Sleep Hours: {sleep_hours}
Water Intake: {water_intake} litres/day
Stress Level: {stress_level}/10

Vital Signs:
Blood Pressure: {blood_pressure}
Heart Rate: {heart_rate}
Body Temperature: {body_temperature}
Oxygen Level: {oxygen_level}%

Medical Report Text:
{text}

Give the answer in this exact format:

## Simple Summary
Explain the report in very simple English.

## Abnormal Values
List abnormal or important values.
Do not assume a value is abnormal without an appropriate reference range.

## What It Means
Explain possible meanings in simple language.

## Health Risk Assessment
Mention whether any findings need routine follow-up,
prompt medical review, or urgent medical attention.
Do not label a person healthy based only on this report.

## Diet Suggestions
Give general, relevant diet suggestions.
Avoid unsupported treatment claims.

## Lifestyle Suggestions
Give suggestions based on smoking, alcohol, exercise,
sleep, water intake and stress.

## Questions to Ask Doctor
Give 5 useful questions.

## Health Score
If a meaningful score cannot be calculated from the available information,
say so. Do not invent a score.
If you provide one, explain its limitations and use this format:
Health Score: 65/100

At the end write:
⚠️ This explanation is for educational purposes only.
"""

        try:
            with st.spinner("⏳ Analyzing your medical report..."):
                response = model.generate_content(prompt)
                report_text = response.text

                if not report_text:
                    st.error("The AI returned an empty response. Please try again.")
                    st.stop()

        except Exception as e:
            st.error(f"Gemini Error: {e}")
            st.stop()

        st.markdown("---")
        st.subheader("📋 AI Medical Report Explanation")

        st.write(report_text)


        # -----------------------------
        # HEALTH SCORE
        # -----------------------------
        match = re.search(
            r"Health Score:\s*(\d+)",
            report_text,
            re.IGNORECASE
        )

        if match:

            health_score = int(match.group(1))
            health_score = max(0, min(100, health_score))

            st.subheader("📊 Health Score")

            st.write(f"Health Score: {health_score}/100")

            st.progress(health_score / 100)

            st.caption(
                "This is an AI-generated informational score, "
                "not a clinically validated health assessment."
            )

        else:
            st.warning(
                "A health score was not provided. "
                "Please review the written explanation."
            )


        # -----------------------------
        # EMERGENCY NOTICE
        # -----------------------------
        emergency_words = [
            "critical",
            "emergency",
            "urgent",
            "heart attack",
            "stroke",
            "icu",
            "severe",
            "immediate",
            "danger",
            "high risk"
        ]

        report_lower = report_text.lower()

        if any(word in report_lower for word in emergency_words):

            st.error(
                "⚠️ The AI explanation contains terms that may indicate "
                "important findings. Please review the report with a "
                "qualified healthcare professional. If you have severe "
                "or sudden symptoms, seek emergency care."
            )

        else:

            st.info(
                "No emergency-related keywords were detected by the "
                "automated text check. This does not confirm that the "
                "report is normal or rule out a medical emergency."
            )


        # -----------------------------
        # MEDICINE EXPLANATION
        # -----------------------------
        if current_medications.strip():

            st.subheader("💊 Medicine Explanation")

            medicine_prompt = f"""
Explain these medicines in simple English:

Medicines: {current_medications}

For each medicine, explain:
1. Common purpose or uses.
2. Common side effects.
3. Important precautions.

Do not recommend changing or stopping prescribed medicines.
Mention that the patient should confirm medicine-related
questions with their doctor or pharmacist.
"""

            try:

                with st.spinner("💊 Explaining medicines..."):

                    medicine_response = model.generate_content(
                        medicine_prompt
                    )

                st.write(medicine_response.text)

            except Exception as e:

                st.warning(
                    f"Medicine explanation could not be generated: {e}"
                )


        # -----------------------------
        # DOWNLOAD REPORTS
        # -----------------------------
        st.success("✅ Report explanation generated successfully!")

        st.download_button(
            label="📥 Download AI Report",
            data=report_text,
            file_name="MediSimplify_AI_Report.txt",
            mime="text/plain"
        )

        st.markdown("---")

        pdf_file = create_pdf(report_text)

        st.download_button(
            label="📥 Download Simplified Report as PDF",
            data=pdf_file,
            file_name="MediSimplify_AI_Report.pdf",
            mime="application/pdf"
        )

        st.session_state["latest_report_text"] = report_text


# -----------------------------
# CHAT WITH REPORT
# -----------------------------
if "latest_report_text" in st.session_state:

    st.markdown("---")

    st.subheader("💬 Chat with Your Medical Report")

    user_question = st.text_input(
        "Ask a question about your report",
        key="report_question"
    )

    if user_question:

        chat_prompt = f"""
You are a medical report explanation assistant.

Answer the user's question using the report explanation below.
Use simple English.
Do not diagnose, prescribe, or recommend changing medication.
If the report does not contain the answer, say so.
Encourage the user to consult a qualified doctor for medical decisions.

Report Explanation:
{st.session_state["latest_report_text"][:8000]}

User Question:
{user_question}
"""

        try:

            with st.spinner("💬 Answering your question..."):

                chat_response = model.generate_content(chat_prompt)

            st.write(chat_response.text)

        except Exception as e:

            st.error(f"Chat Error: {e}")


# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")

st.markdown("""
<div style="text-align:center; padding:15px; color:#888;">
    <h4 style="color:#167D8D;">🏥 MediSimplify AI</h4>
    <p>Making medical information easier to understand.</p>
    <small>
        For educational purposes only. Always consult a qualified doctor.
    </small>
</div>
""", unsafe_allow_html=True)
