def fake_report(prompt, prompts, risk, currentPos, cash):
    return f"""#This is fake report

            ## Ticker
            {prompt}
            ## Risk Level
            {risk}
            ## Current Position
            {currentPos}
            ## New Cash
            {cash}
            ## User Question
            {prompts}
            ## Summary
            This is a fake report. It is used to test the app workflow before connecting OpenAI.

            ## News / Catalyst Placeholder
            - No real news is being fetched yet.
            - Later, this section will summarize recent catalysts and market-moving events.

            ## Research View Placeholder
            - No real fundamental analysis is being performed yet.
            - Later, this section will discuss business quality, growth, valuation, and competitive position.

            ## Portfolio Fit Placeholder
            - No user portfolio profile is being used yet.
            - Later, this section will consider risk profile, cash, current holdings, and position sizing.

            ## Risk Review
            - This stock may lose value.
            - This analysis is incomplete.
            - The user should do more research before making any decision.

            ## Conditional Conclusion
            This fake report does not recommend buying, selling, or shorting. It only confirms that the app can collect input and display structured output.

            ## Disclaimer
            This is research assistance, not financial advice. The app does not execute trades. The user is responsible for final investment decisions.
            """