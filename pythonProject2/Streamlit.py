import streamlit as st
from PIL import Image
from transformers import pipeline
from PyPDF2 import PdfReader
import textwrap
from fpdf import FPDF
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

model_name = "stevhliu/my_awesome_billsum_model"
summarizer = pipeline("summarization", model=AutoModelForSeq2SeqLM.from_pretrained(model_name), tokenizer=AutoTokenizer.from_pretrained(model_name))


SECRET_KEY = "AIzaSyAU_9QPsdQI6Fx0eqP3_PIKREMS1tWxLog"


import google.generativeai as genai

genai.configure(api_key=SECRET_KEY)

# Set up the model
generation_config = {
  "temperature": 0.9,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

model = genai.GenerativeModel(model_name="gemini-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

convo = model.start_chat(history=[
])
st.title('EduMystica')
st.header('Answer to your Education needs.')

def resources(Request1,Request2,Request3,Request4):
  convo.send_message(f'Suggest some good study material for a student studying in{Request1} for the subject of {Request2} and the level of student int he subject in a range of 1-10 is {Request4} and also the student is weak in {Request3}, also provide URL for whichever possible')
  details = convo.last.text
  return details
def summarize(path):
  reader = PdfReader(path)
  strk = ""
  for i in range(len(reader.pages)):
    k = reader.pages[i].extract_text()
    strk = summarizer(k)[0]['summary_text'] + strk
  return strk
def Syllabus_Q_P(path,Request1):
  qp = PdfReader(path)
  topics = ""
  for i in range(len(qp.pages)):
      details = qp.pages[i].extract_text()
      topics = topics + details
  convo.send_message(f"can you please summarize from what all topics the questions have been asked in this question paper for {Request1} std (exclude name of subject):\n" + topics)
  syl = convo.last.text
  return syl
from fpdf import FPDF

def text_to_pdf(text, filename):
    a4_width_mm = 210
    pt_to_mm = 0.35
    fontsize_pt = 10
    fontsize_mm = fontsize_pt * pt_to_mm
    margin_bottom_mm = 10
    character_width_mm = 7 * pt_to_mm
    width_text = a4_width_mm / character_width_mm

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(True, margin=margin_bottom_mm)
    pdf.add_page()
    pdf.set_font(family='Courier', size=fontsize_pt)
    splitted = text.split('\n')

    for line in splitted:
        lines = textwrap.wrap(line, width_text)

        if len(lines) == 0:
            pdf.ln()

        for wrap in lines:
            # Encode the text with UTF-8 before adding it to the PDF
            encoded_wrap = wrap.encode('latin1', 'replace').decode('latin1')
            pdf.cell(0, fontsize_mm, encoded_wrap, ln=1)

    # Output the PDF after processing all the text
    pdf.output(filename, 'F')

def QPGenerator(Request1,Marks,path):
  convo.send_message(f"Create a question paper of {Marks} marks for a student in {Request1} std, with marking scheme used and answer key in the end:\n, on syllabus " +Syllabus_Q_P(path,Request1))
  question_paper = convo.last.text
  return text_to_pdf(question_paper,"questionpp")

Decision = st.selectbox(label = 'Choose the feature you want to use',options = ['Resources detailer','Pdf Sumarizer','Syllabus Generator from question paper','Question paper Generator'])

def output(Decision):
    Request1 = st.text_input("Enter which grade you are in :")
    Request2 = st.text_input("Enter which subject you like to know guide to :")
    Request3 = st.text_input("Enter which field you are weak in :")
    Request4 = st.text_input("Enter what is your level in the subject in a scale of 10:")
    if Decision == 'Resources detailer':
        result = resources(Request1, Request2, Request3, Request4)
        st.write(result)
        return result
    elif Decision == 'Pdf Sumarizer':
        path = st.text_input("Path of the file:")
        result = summarize(path)
        st.write(result)
    elif Decision == 'Syllabus Generator from question paper':
        path = st.text_input("Path of the file:")
        result = Syllabus_Q_P(path, Request1)
        st.write(result)
        return result
    elif Decision == 'Question paper Generator':
        path = st.text_input("Path of the file:")
        Marks = st.text_input("Enter your desired full marks of paper")
        result = QPGenerator(Request1, Marks, path)
        if st.button("Generate PDF"):
            st.download_button(
                label="Download PDF",
                data=open("questionpp", "rb").read(),
                key="download_pdf",
                file_name="generated_pdf.pdf",
                mime="application/pdf",
            )
        return result
output(Decision)
