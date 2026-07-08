import os
from dotenv import load_dotenv
from openai import OpenAI


def generateAiReport(prompt,prompts, risk, currentPos, cash):
    # Load variables from the local .env file into environment variables.
    load_dotenv()
    #read openai api key
    api_key = os.getenv("OPENAI_API_KEY")
    #stop early if the developer has not created a local .env file yet
    if not api_key:
        return """#OpenAI Setup Missing
        Please create a local .env file with your API key:
        OPENAI_API_KEY=your_api_key_here
        This key is only for local development. Do not commit it to git"""
    #Create an openai client using the local api key
    client = OpenAI(api_key=api_key)
    # Build the prompt that tells the model exactly what report shape we expect.
    user_prompt = f"""
                    You are an investment research assistant. 
                    Generate a structured Markdown report for the following stock research request
                    Ticker: 
                    {prompt}
                    Risk Level: 
                    {risk}
                    Current Position:
                    {currentPos}
                    New Cash:
                    {cash}
                    User Question:
                    {prompts}
The report must include sections with these meanings:
- Investment Research Report
- Ticker
- User Question
- Summary
- News / Catalyst View
- Research View
- Portfolio Fit
- Risk Review
- Invalidation Conditions
- Conditional Conclusion
- Disclaimer

Rules:
- Use the same language as the user's question, unless the user explicitly asks for a different language.
- Use the same language for both section headings and body text.
- If the user's question is in Chinese, translate the section headings into natural Chinese.
- The current prototype does not have live data, web search, source retrieval, or citation support.
- Do not claim specific recent news, earnings, partnerships, product launches, guidance, or market events as verified facts.
- In the News / Catalyst View section, discuss general catalyst categories or factors to investigate unless the user provides specific facts.
- Clearly state when live source verification is not available in the current prototype.
- This is research assistance, not financial advice.
- Do not tell the user to buy, sell, short, or hold as an absolute instruction.
- Use conditional language.
- Include uncertainty and risks.
- Mention that the app does not execute trades.
"""

    try:
        # Send the request to OpenAI and get the generated report text.
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=user_prompt,
        )
    except Exception as error:
        # Return the error as report text so the UI can show it instead of crashing.
        return f"""# OpenAI Request Failed

The app could not generate an AI report.

Error:
{error}
"""

    # Return the model's text output to the caller.
    return response.output_text
