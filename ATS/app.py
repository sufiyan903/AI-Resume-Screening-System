from dotenv import load_dotenv
load_dotenv()

import base64
import streamlit as st
import os
import io
from PIL import Image
import pdf2image
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Convert uploaded PDF to image and encode as inline_data format
@st.cache_data(show_spinner=False)
def input_pdf_setup(uploaded_file_bytes):
    try:
        images = pdf2image.convert_from_bytes(
            uploaded_file_bytes,
            poppler_path=r"C:\Program Files (x86)\poppler\Library\bin"
        )
        first_page = images[0]

        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_image_part = {
            "mime_type": "image/jpeg",
            "data": base64.b64encode(img_byte_arr).decode("utf-8")
        }

        return pdf_image_part
    except Exception as e:
        st.error(f"Error processing PDF: {e}")
        return None

# Gemini 1.5 Flash response generator
def get_gemini_flash_response(prompt, pdf_image_part):
    model = genai.GenerativeModel('models/gemini-1.5-flash')

    parts = [
        {
            "inline_data": {
                "mime_type": pdf_image_part["mime_type"],
                "data": pdf_image_part["data"]
            }
        },
        {
            "text": prompt
        }
    ]

    response = model.generate_content(
        contents=[{"role": "user", "parts": parts}]
    )
    return response.text

# ---------- Streamlit App ----------
st.set_page_config(page_title="ATS Resume Expert", layout="centered")
st.header("📄 ATS Resume Screening with Gemini 1.5 Flash")

input_text = st.text_area("📋 Paste Job Description:", key="input", height=200)
uploaded_file = st.file_uploader("📎 Upload Resume (PDF Only)", type=["pdf"])

if uploaded_file is not None:
    st.success("✅ PDF Uploaded Successfully")

submit1 = st.button("🔍 Tell Me About the Resume", key="btn1")
submit3 = st.button("📊 Match Percentage", key="btn3")

input_prompt1 = """
You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description.
Please share your professional evaluation on whether the candidate's profile aligns with the role.
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality.
Your task is to evaluate the resume against the provided job description. 
Give me the percentage of match if the resume matches the job description.
First, the output should come as percentage, then list the keywords missing, and finally provide your overall thoughts.
"""

if submit1:
    if uploaded_file:
        with st.spinner("Analyzing resume..."):
            pdf_image_part = input_pdf_setup(uploaded_file.read())
            if pdf_image_part:
                prompt = input_prompt1 + "\n\nJob Description:\n" + input_text
                response = get_gemini_flash_response(prompt, pdf_image_part)
                st.subheader("📄 Gemini's Evaluation:")
                st.write(response)
    else:
        st.warning("⚠️ Please upload a resume first.")

elif submit3:
    if uploaded_file:
        with st.spinner("Calculating ATS match..."):
            pdf_image_part = input_pdf_setup(uploaded_file.read())
            if pdf_image_part:
                prompt = input_prompt3 + "\n\nJob Description:\n" + input_text
                response = get_gemini_flash_response(prompt, pdf_image_part)
                st.subheader("📊 Match Percentage:")
                st.write(response)
    else:
        st.warning("⚠️ Please upload a resume first.")
