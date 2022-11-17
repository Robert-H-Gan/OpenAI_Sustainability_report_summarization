# import required libraries
import streamlit as st
import pdfplumber 
import openai
import time

# write title and subtitle of application
"# Summarizing Sustainability Reports"
"### A tool for investment analysts to gain a better insight on company sustainability reports"

# # example markdown
# st.write("Let's go!")

from PIL import Image
# image = Image.open("/Users/matth/Dropbox/PC/Desktop/OpenAI-Hackathon/netzero2.jpg")
image = Image.open("/Users/Charles/Desktop/Robert/Coding/OpenAI Hackathon for climate change/streamlit app/netzero2.jpg")
# image = Image.open(streamlit app\netzero2.jpg)

st.image(image, caption='Illustration by Petmal | iStock ')

# for exponential backoff
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  

openai.api_key = ' < YOUR-API-KEY > '

# initialise reportContent
reportContent = ""  

uploaded_file = st.file_uploader('Upload your sustainability .pdf file here:', type="pdf")
if uploaded_file is not None:
    # extract text from pdf
    # st.write("A file has been uploaded!")
    reportContent = pdfplumber.open(uploaded_file).pages
    fileLoaded = True
else:
    fileLoaded = False

# Set up parameters
engine = 'text-davinci-002'
temperature = 0.8
max_tokens = 60
top_p = 1
frequency_penalty=0
presence_penalty=0
stop=["\n"]

# Rate limit workaround
# solution 1: completion with backoff
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
def completion_with_backoff(**kwargs):
    return openai.Completion.create(**kwargs)


# 2. SUMMARIZATION LEVEL 1
# Report Summary function
def showReportSummary(reportContent):
    # Add tag for tl;dr summarization
    tldr_tag = "\n tl;dr:"
    ReportSummary = ''
    for page_index in range(len(reportContent)):
        text = reportContent[page_index] 
    for page in reportContent:    
        text = page.extract_text() + tldr_tag

        response = completion_with_backoff(
            engine = engine,
            prompt = text,
            temperature = temperature,
            max_tokens = max_tokens,
            top_p = top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop
        )
        ReportSummary = ReportSummary + response["choices"][0]["text"]
    return ReportSummary


# 3. SUMMARIZATION LEVEL 2

def SummarizeSummary(report_summary):
    tldr_tag = "\n tl;dr:"
    report_summary_summarized = ''
    response = openai.Completion.create(
        engine = engine,
        prompt = report_summary + tldr_tag,
        temperature = temperature,
        max_tokens = 2000,
        top_p = top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        stop=stop
    )
    report_summary_summarized = response["choices"][0]["text"]
    return report_summary_summarized


# 4. OUTPUT

# # initialise reportContent
# reportContent = ""    

with st.spinner('In progress...'):
    # summarize reports
    report_summary = showReportSummary(reportContent)
    report_summary_summarized = SummarizeSummary(report_summary)
    # print report summaries
    if (fileLoaded == True):
        st.subheader(report_summary_summarized)
        st.write(report_summary)


