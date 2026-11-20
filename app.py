
import streamlit as st
from pypdf import PdfReader
import google.generativeai as genai
from dotenv import load_dotenv
import os
import re
from io import BytesIO
from datetime import date, datetime
from xml.sax.saxutils import escape
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="MediSimplify AI | Medical Report Simplifier",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>
.main {
    background-color: #ffffff;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.hero {
    background: linear-gradient(120deg, #eaf7f8, #f5f9fc);
    padding: 30px;
    border-radius: 15px;
    text-align: center;
    border: 1px solid #d5e8eb;
}

.hero h1 {
    color: #087F8C;
    font-size: 42px;
    font-weight: 700;
}

.hero h3 {
    color: #183B56;
    font-weight: 500;
}

.hero p {
    color: #555555;
    font-size: 16px;
}

.feature-card {
    background-color: #f0f7f8;
    border: 1px solid #d5e8eb;
    border-radius: 12px;
    padding: 20px;
    min-height: 145px;
    margin-bottom: 15px;
}

.feature-card h4 {
    color: #087F8C;
}

.feature-card p {
    color: #555555;
    font-size: 14px;
}

.section-heading {
    color: #087F8C;
    font-weight: 600;
}

.small-note {
    color: #777777;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

default_values = {
    "latest_report_text": "",
    "latest_medicine_text": "",
    "report_history": [],
    "chat_history": [],
    "analysis_completed": False
}

for key, value in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# API KEY SETUP
# ============================================================

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
        "GEMINI_API_KEY not found. "
        "Add it to Streamlit Secrets or your .env file."
    )
    st.stop()

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")


# ============================================================
# PDF GENERATOR
# ============================================================

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

            story.append(
                Paragraph(line, styles["Normal"])
            )

            story.append(Spacer(1, 6))

    doc.build(story)

    buffer.seek(0)

    return buffer


# ============================================================
# REPORT SECTION PARSER
# ============================================================

def display_organized_report(report_text):

    sections = re.split(
        r"(?=^##\s+)",
        report_text,
        flags=re.MULTILINE
    )

    displayed_sections = 0

    for section in sections:

        section = section.strip()

        if not section:
            continue

        lines = section.split("\n")

        heading = lines[0].replace("##", "").strip()

        content = "\n".join(lines[1:]).strip()

        if heading:

            displayed_sections += 1

            with st.expander(
                f"📌 {heading}",
                expanded=(displayed_sections == 1)
            ):

                st.markdown(content)

    if displayed_sections == 0:
        st.markdown(report_text)


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

st.sidebar.markdown(
    """
    <h2 style="color:#087F8C;">🏥 MediSimplify AI</h2>
    <p style="color:#777;">Understand • Learn • Stay Informed</p>
    """,
    unsafe_allow_html=True
)

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "👤 Patient Information",
        "📄 Medical Report Analysis",
        "❤️ Health Information",
        "💬 Chat with Report",
        "⚙️ About & Privacy"
    ],
    key="navigation"
)

st.sidebar.divider()

st.sidebar.markdown("""
### How to Use

1. Enter patient information.
2. Add health information if desired.
3. Upload a medical report PDF.
4. Analyse the report.
5. Review the explanation.
6. Download your simplified report.

---

**MediSimplify AI**

For educational purposes only.
""")


# ============================================================
# COMMON MEDICAL DISCLAIMER
# ============================================================

st.warning(
    "Medical Disclaimer: MediSimplify AI provides AI-generated "
    "educational explanations only. It does not diagnose diseases, "
    "prescribe treatment or replace a qualified healthcare professional. "
    "Always discuss medical findings and decisions with your doctor. "
    "Do not delay urgent medical care based on this application."
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

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

    st.subheader("Welcome to MediSimplify AI")

    st.write(
        "A simple platform designed to help users understand "
        "complex medical reports using Generative AI."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>📄 Report Simplification</h4>
            <p>Convert complex medical reports into simple language.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>📊 Health Information</h4>
            <p>Organise patient details, lifestyle and vital signs.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <h4>💊 Medicine Explanation</h4>
            <p>Understand general medicine information and precautions.</p>
        </div>
        """, unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown("""
        <div class="feature-card">
            <h4>⚖️ BMI Calculator</h4>
            <p>Calculate BMI using height and weight.</p>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown("""
        <div class="feature-card">
            <h4>💬 Chat with Report</h4>
            <p>Ask questions about your latest report explanation.</p>
        </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown("""
        <div class="feature-card">
            <h4>📥 Report Downloads</h4>
            <p>Download your simplified report in PDF or TXT format.</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.subheader("Your Session Overview")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Reports Analysed",
            len(st.session_state.report_history)
        )

    with col2:
        st.metric(
            "Latest Report Available",
            "Yes" if st.session_state.latest_report_text else "No"
        )

    st.caption(
        "Report history is temporary and limited to the current session."
    )


# ============================================================
# PATIENT INFORMATION
# ============================================================

elif page == "👤 Patient Information":

    st.title("👤 Patient Information")

    st.write(
        "Enter basic patient details. These details can be used "
        "to provide context when explaining the uploaded report."
    )

    st.text_input(
        "Patient Name",
        key="patient_name"
    )

    st.number_input(
        "Age",
        min_value=1,
        max_value=120,
        value=30,
        step=1,
        key="patient_age"
    )

    st.selectbox(
        "Gender",
        ["Select", "Male", "Female", "Other"],
        key="patient_gender"
    )

    st.date_input(
        "Report Date",
        value=date.today(),
        key="report_date"
    )

    st.text_input(
        "Hospital / Lab Name",
        key="hospital_name"
    )

    st.selectbox(
        "Blood Group",
        [
            "Select",
            "A+",
            "A-",
            "B+",
            "B-",
            "AB+",
            "AB-",
            "O+",
            "O-"
        ],
        key="blood_group"
    )

    st.text_input(
        "Emergency Contact Number",
        placeholder="Enter emergency contact number",
        key="emergency_contact"
    )

    st.text_area(
        "Known Allergies",
        placeholder="Example: Penicillin, peanuts, dust allergy",
        key="allergies"
    )

    st.text_area(
        "Previous Medical Conditions",
        placeholder="Example: Diabetes, hypertension, asthma",
        key="medical_history"
    )

    st.text_area(
        "Current Medications",
        placeholder="Enter currently prescribed medicines",
        key="current_medications"
    )

    st.text_area(
        "Past Surgeries",
        placeholder="Enter previous surgery details if applicable",
        key="past_surgeries"
    )

    st.text_area(
        "Family Medical History",
        placeholder="Enter relevant family medical history",
        key="family_history"
    )

    st.success(
        "Patient information is maintained in the current Streamlit session."
    )


# ============================================================
# HEALTH INFORMATION
# ============================================================

elif page == "❤️ Health Information":

    st.title("❤️ Health Information")

    st.subheader("BMI Calculator")

    col1, col2 = st.columns(2)

    with col1:

        st.number_input(
            "Height (cm)",
            min_value=50,
            max_value=250,
            value=170,
            key="height_cm"
        )

    with col2:

        st.number_input(
            "Weight (kg)",
            min_value=10,
            max_value=300,
            value=70,
            key="weight_kg"
        )

    height = st.session_state.get("height_cm", 170)
    weight = st.session_state.get("weight_kg", 70)

    bmi = weight / ((height / 100) ** 2)

    st.metric("Your BMI", f"{bmi:.2f}")

    if bmi < 18.5:
        st.info("BMI category: Underweight")

    elif bmi < 25:
        st.info("BMI category: Normal range")

    elif bmi < 30:
        st.info("BMI category: Overweight range")

    else:
        st.info("BMI category: Obesity range")

    st.caption(
        "BMI is a screening measure, not a diagnosis. "
        "Interpret it with a healthcare professional."
    )

    st.divider()

    st.subheader("Lifestyle Information")

    st.selectbox(
        "Do you smoke?",
        ["No", "Occasionally", "Regularly"],
        key="smoking"
    )

    st.selectbox(
        "Do you consume alcohol?",
        ["No", "Occasionally", "Regularly"],
        key="alcohol"
    )

    st.selectbox(
        "Exercise Frequency",
        [
            "Daily",
            "3-5 times/week",
            "1-2 times/week",
            "Rarely",
            "Never"
        ],
        key="exercise"
    )

    st.selectbox(
        "Diet Type",
        ["Vegetarian", "Non-Vegetarian", "Vegan", "Mixed"],
        key="diet"
    )

    st.slider(
        "Average Sleep (hours/day)",
        1,
        12,
        7,
        key="sleep_hours"
    )

    st.slider(
        "Average Water Intake (litres/day)",
        1,
        10,
        3,
        key="water_intake"
    )

    st.slider(
        "Stress Level",
        1,
        10,
        5,
        key="stress_level"
    )

    st.divider()

    st.subheader("Vital Signs")

    st.text_input(
        "Blood Pressure",
        placeholder="Example: 120/80 mmHg",
        key="blood_pressure"
    )

    st.number_input(
        "Heart Rate (BPM)",
        min_value=30,
        max_value=200,
        value=72,
        key="heart_rate"
    )

    st.number_input(
        "Body Temperature (°C)",
        min_value=30.0,
        max_value=45.0,
        value=36.5,
        step=0.1,
        key="body_temperature"
    )

    st.slider(
        "Oxygen Saturation (SpO₂ %)",
        70,
        100,
        98,
        key="oxygen_level"
    )

    st.divider()

    st.subheader("Health Goals")

    st.selectbox(
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
        ],
        key="health_goal"
    )


# ============================================================
# MEDICAL REPORT ANALYSIS
# ============================================================

elif page == "📄 Medical Report Analysis":

    st.title("📄 Medical Report Analysis")

    st.write(
        "Upload a medical report PDF to receive an AI-generated "
        "explanation in simple English."
    )

    uploaded_file = st.file_uploader(
        "Choose your medical report PDF",
        type=["pdf"],
        key="medical_pdf"
    )

    if uploaded_file:

        try:

            reader = PdfReader(uploaded_file)

            extracted_text = ""

            for pdf_page in reader.pages:

                page_text = pdf_page.extract_text()

                if page_text:
                    extracted_text += page_text + "\n"

        except Exception as error:

            st.error(f"Unable to read PDF: {error}")
            st.stop()

        if not extracted_text.strip():

            st.warning(
                "No readable text was found. "
                "This may be a scanned PDF requiring OCR."
            )
            st.stop()

        st.success("PDF uploaded successfully!")

        with st.expander("View Extracted PDF Text"):

            st.text_area(
                "Extracted Text",
                extracted_text,
                height=250
            )

        if st.button(
            "✨ Simplify Medical Report",
            type="primary",
            use_container_width=True
        ):

            patient_name = st.session_state.get("patient_name", "").strip()

            patient_gender = st.session_state.get(
                "patient_gender", "Select"
            )

            hospital_name = st.session_state.get(
                "hospital_name", ""
            ).strip()

            if not patient_name or not hospital_name or patient_gender == "Select":

                st.warning(
                    "Please enter Patient Name, Gender and Hospital/Lab "
                    "in the Patient Information section first."
                )

                st.stop()

            report_text_input = extracted_text[:12000]

            bmi_height = st.session_state.get("height_cm", 170)
            bmi_weight = st.session_state.get("weight_kg", 70)

            bmi_value = bmi_weight / ((bmi_height / 100) ** 2)

            prompt = f"""
You are MediSimplify AI, an assistant that explains medical reports
in simple English.

IMPORTANT RULES:

1. Do not diagnose diseases.
2. Do not invent medical values or findings.
3. Do not assume a value is abnormal without a suitable reference range.
4. Clearly distinguish report findings from general information.
5. Do not prescribe medicines or recommend changing prescribed treatment.
6. If information is missing, say it is not provided.
7. Do not claim that a person is healthy based on one report.
8. Use simple, understandable language.
9. Recommend professional medical review when appropriate.
10. Do not calculate or invent a clinical health score.

PATIENT INFORMATION:

Name: {patient_name}
Age: {st.session_state.get("patient_age", 30)}
Gender: {patient_gender}
Report Date: {st.session_state.get("report_date", date.today())}
Hospital/Lab: {hospital_name}
Blood Group: {st.session_state.get("blood_group", "Not provided")}
BMI: {bmi_value:.2f}

Allergies:
{st.session_state.get("allergies", "")}

Medical History:
{st.session_state.get("medical_history", "")}

Current Medications:
{st.session_state.get("current_medications", "")}

Past Surgeries:
{st.session_state.get("past_surgeries", "")}

Family History:
{st.session_state.get("family_history", "")}

LIFESTYLE:

Smoking: {st.session_state.get("smoking", "Not provided")}
Alcohol: {st.session_state.get("alcohol", "Not provided")}
Exercise: {st.session_state.get("exercise", "Not provided")}
Diet: {st.session_state.get("diet", "Not provided")}
Sleep: {st.session_state.get("sleep_hours", "Not provided")} hours
Water Intake: {st.session_state.get("water_intake", "Not provided")} litres/day
Stress: {st.session_state.get("stress_level", "Not provided")}/10
Health Goal: {st.session_state.get("health_goal", "Not provided")}

VITAL SIGNS:

Blood Pressure: {st.session_state.get("blood_pressure", "Not provided")}
Heart Rate: {st.session_state.get("heart_rate", "Not provided")}
Body Temperature: {st.session_state.get("body_temperature", "Not provided")}
Oxygen Level: {st.session_state.get("oxygen_level", "Not provided")}%

MEDICAL REPORT TEXT:

{report_text_input}

Prepare the explanation using these sections:

## Simple Summary
Explain the report in simple English.

## Important Findings
List the important values and observations.
Include reference ranges when present in the report.

## Abnormal Values
Explain values marked high, low or abnormal by the report.
Do not independently label a value abnormal without sufficient context.

## What It Means
Explain the possible meaning of the findings.
Avoid making a diagnosis.

## Follow-up Guidance
Explain which findings may need routine follow-up,
prompt medical review or urgent medical attention.
Do not claim that this automated explanation can rule out emergencies.

## Diet Suggestions
Provide general and relevant suggestions.
Do not claim that diet can treat or cure a disease.

## Lifestyle Suggestions
Give general suggestions based on the provided lifestyle information.

## Questions to Ask Your Doctor
Provide five useful questions based on the report.

## Important Limitations
Mention any missing information or limitations that affect interpretation.

End with:
This explanation is for educational purposes only and is not a medical diagnosis.
"""

            progress = st.progress(0)

            status = st.empty()

            try:

                status.info("Step 1 of 3: Preparing the report...")

                progress.progress(20)

                status.info("Step 2 of 3: Analysing the report with AI...")

                response = model.generate_content(prompt)

                report_text = response.text

                if not report_text:

                    st.error(
                        "The AI returned an empty response. Please try again."
                    )

                    st.stop()

                progress.progress(75)

                status.info("Step 3 of 3: Preparing your results...")

                st.session_state.latest_report_text = report_text

                st.session_state.latest_medicine_text = ""

                st.session_state.chat_history = []

                report_record = {
                    "patient": patient_name,
                    "date": str(
                        st.session_state.get("report_date", date.today())
                    ),
                    "created_at": datetime.now().strftime(
                        "%d %b %Y, %I:%M %p"
                    ),
                    "report": report_text
                }

                st.session_state.report_history.append(report_record)

                current_medications = st.session_state.get(
                    "current_medications", ""
                ).strip()

                if current_medications:

                    medicine_prompt = f"""
Explain the following medicines in simple English.

Medicines:
{current_medications}

For each medicine explain:

1. General purpose or common uses.
2. Common side effects.
3. Important precautions.

Do not recommend starting, stopping or changing any medicine.
Do not assume the reason a particular patient was prescribed it.
Tell the user to confirm medicine-related questions with their
doctor or pharmacist.
"""

                    try:

                        medicine_response = model.generate_content(
                            medicine_prompt
                        )

                        st.session_state.latest_medicine_text = (
                            medicine_response.text or ""
                        )

                    except Exception as medicine_error:

                        st.warning(
                            "The report was analysed, but medicine "
                            f"information could not be generated: {medicine_error}"
                        )

                progress.progress(100)

                status.success("Analysis completed successfully!")

                st.session_state.analysis_completed = True

            except Exception as error:

                status.empty()

                st.error(f"Gemini Error: {error}")

                st.stop()

    # --------------------------------------------------------
    # DISPLAY LATEST REPORT
    # --------------------------------------------------------

    if st.session_state.latest_report_text:

        st.divider()

        st.subheader("📋 Your AI Report Explanation")

        display_organized_report(
            st.session_state.latest_report_text
        )

        # ----------------------------------------------------
        # MEDICINE EXPLANATION
        # ----------------------------------------------------

        if st.session_state.latest_medicine_text:

            st.divider()

            st.subheader("💊 Medicine Explanation")

            st.markdown(
                st.session_state.latest_medicine_text
            )

        # ----------------------------------------------------
        # DOWNLOAD REPORTS
        # ----------------------------------------------------

        st.divider()

        st.subheader("📥 Download Your Report")

        col1, col2 = st.columns(2)

        with col1:

            st.download_button(
                label="Download TXT Report",
                data=st.session_state.latest_report_text,
                file_name="MediSimplify_AI_Report.txt",
                mime="text/plain",
                use_container_width=True
            )

        with col2:

            pdf_file = create_pdf(
                st.session_state.latest_report_text
            )

            st.download_button(
                label="Download PDF Report",
                data=pdf_file,
                file_name="MediSimplify_AI_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    # --------------------------------------------------------
    # REPORT HISTORY
    # --------------------------------------------------------

    st.divider()

    st.subheader("📚 Recent Report History")

    if st.session_state.report_history:

        for index, item in enumerate(
            reversed(st.session_state.report_history),
            start=1
        ):

            with st.expander(
                f"Report {index} | {item['patient']} | {item['created_at']}"
            ):

                st.markdown(item["report"])

    else:

        st.info(
            "No reports have been analysed in this session yet."
        )

    st.caption(
        "History is temporary. It is not a permanent medical record "
        "or a secure patient database."
    )


# ============================================================
# CHAT WITH REPORT
# ============================================================

elif page == "💬 Chat with Report":

    st.title("💬 Chat with Your Medical Report")

    st.write(
        "Ask questions about your latest AI-generated report explanation."
    )

    if not st.session_state.latest_report_text:

        st.info(
            "Please analyse a medical report first to use this feature."
        )

    else:

        for message in st.session_state.chat_history:

            with st.chat_message(message["role"]):

                st.markdown(message["content"])

        user_question = st.chat_input(
            "Ask a question about your report..."
        )

        if user_question:

            st.session_state.chat_history.append({
                "role": "user",
                "content": user_question
            })

            with st.chat_message("user"):
                st.markdown(user_question)

            chat_prompt = f"""
You are MediSimplify AI.

Answer the user's question using the report explanation below.

Rules:
1. Use simple English.
2. Do not diagnose diseases.
3. Do not prescribe medication.
4. Do not recommend stopping or changing medicines.
5. If the report does not contain the answer, say so.
6. Encourage consultation with a qualified healthcare professional.
7. Do not claim that the report rules out a medical emergency.

REPORT EXPLANATION:

{st.session_state.latest_report_text[:10000]}

USER QUESTION:

{user_question}
"""

            try:

                with st.chat_message("assistant"):

                    with st.spinner("Preparing your answer..."):

                        chat_response = model.generate_content(
                            chat_prompt
                        )

                        answer = (
                            chat_response.text
                            or "I could not generate an answer. Please try again."
                        )

                    st.markdown(answer)

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as error:

                st.error(f"Chat Error: {error}")


# ============================================================
# ABOUT AND PRIVACY
# ============================================================

elif page == "⚙️ About & Privacy":

    st.title("⚙️ About MediSimplify AI")

    st.subheader("About the Project")

    st.write(
        "MediSimplify AI is an AI-powered medical document "
        "intelligence system designed to explain complex medical "
        "reports in simple and understandable language."
    )

    st.subheader("Technology Used")

    st.markdown("""
    - **Python:** Main programming language.
    - **Streamlit:** User interface and application framework.
    - **Google Gemini:** Generative AI for report explanations.
    - **PyPDF:** Extracts text from PDF medical reports.
    - **ReportLab:** Generates downloadable PDF reports.
    """)

    st.divider()

    st.subheader("Privacy Information")

    st.markdown("""
    - Patient details and report history are maintained in the
      current Streamlit session.
    - This version does not provide a permanent patient database.
    - Session information may disappear when the session ends
      or is reset.
    - Uploaded report content is sent to the configured AI service
      for analysis.
    - Do not upload information unless you are comfortable with
      the applicable service privacy terms.
    - Avoid uploading unnecessary personal identifiers.
    """)

    st.divider()

    st.subheader("Medical Disclaimer")

    st.warning(
        "This application is an educational information tool. "
        "It is not a substitute for a doctor, laboratory professional "
        "or other qualified healthcare provider. AI-generated content "
        "may be incomplete or inaccurate. Always verify medical "
        "information with a qualified professional."
    )

    st.divider()

    st.subheader("Developer")

    st.write("MediSimplify AI")

    st.caption("Understand • Learn • Stay Informed")


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown("""
<div style="text-align:center; padding:15px; color:#888;">
    <h4 style="color:#087F8C;">🏥 MediSimplify AI</h4>
    <p>Understand • Learn • Stay Informed</p>
    <small>
        AI-generated educational information only.
        Always consult a qualified healthcare professional.
    </small>
</div>
""", unsafe_allow_html=True)
