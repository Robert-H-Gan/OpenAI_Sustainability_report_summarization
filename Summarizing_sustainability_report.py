# libraries import
import openai
import pdfplumber
import time

# for exponential backoff
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  

openai.api_key = ' < YOUR-API-KEY > '

# 1. LOAD PDF FILES
Volkswagen_reportFilePath = '/content/drive/MyDrive/volkswagen-sustainability-report-2021.pdf'
Volkswagen_reportContent = pdfplumber.open(Volkswagen_reportFilePath).pages

bp_reportFilePath = '/content/drive/MyDrive/bp-sustainability-report-2021.pdf'
bp_reportContent = pdfplumber.open(bp_reportFilePath).pages


# Set up parameters
engine = 'text-davinci-002'
temperature = 0.7
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


# bp _report_summary
bp_report_summary = showReportSummary(bp_reportContent)
print(bp_report_summary)

# Volkswagen_report_summary
Volkswagen_report_summary= showReportSummary(Volkswagen_reportContent)
print(Volkswagen_report_summary)




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

# bp_report_summary_summarized
bp_report_summary_summarized = SummarizeSummary(bp_report_summary)
print(bp_report_summary_summarized)

# Volkswagen_report_summary_summarized
Volkswagen_report_summary_summarized = SummarizeSummary(Volkswagen_report_summary)
print(Volkswagen_report_summary_summarized)

