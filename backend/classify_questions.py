import google.generativeai as genai
import os

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file")
genai.configure(api_key=API_KEY)

def classify_question(question):
    prompt =f'''
       Classify the following statement into one of the two categories:  

        - "personal budgeting"  
        - "financial education"  

        Return only one of these two options in lowercase without any additional text.  

        Statement: {question}   '''

    model = genai.GenerativeModel("gemini-1.5-flash-002")
    response = model.generate_content(prompt)

    if response and response.text:
        return response.text
    return "financial education"