import sys
import PySide6
from PySide6.QtWidgets import QApplication, QHBoxLayout
from PySide6.QtWidgets import QWidget, QComboBox
from PySide6.QtWidgets import QVBoxLayout, QLineEdit, QTextEdit
from PySide6.QtWidgets import QPushButton, QLabel

def fake_report(prompt, prompts,risk,currentPos,cash):
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
def handle_run():
    prompt_input = prompt.text().strip()
    prompts_input = prompts.toPlainText().strip()
    risk = riskProfile.currentText().strip()
    currentPosition = currentPos.text().strip()
    if not currentPosition:
        currentPosition = "Not provided"
    newCash = cash.text().strip()
    cashU = cashUnit.currentText().strip()
    if newCash:
        cash_display = f"{newCash} {cashU}"
    else:
        cash_display = "Not provided"

    #user must enter ticker and questions
    if not prompt_input or not prompts_input:
        status.setText("Missing inputs")
        output.setPlainText("Please enter both a ticker and questions")
        return
    #Generate fake report
    report = fake_report(prompt_input, prompts_input,risk,currentPosition,cash_display)
    #show the report
    status.setText("Report Generated")
    output.setPlainText(report)

app = QApplication(sys.argv)

window = QWidget()
#main window
title = "Investment Assistant"
window.setWindowTitle(title)
window.resize(900, 600)
#stack widgets
VLlayout = QVBoxLayout() #Left side of the window
VRlayout = QVBoxLayout()# right side of the window
Hlayout = QHBoxLayout()# The whole window
#Ticker
prompt = QLineEdit()
prompt.setPlaceholderText("Enter your investment assistance")
VLlayout.addWidget(prompt)# Ticker at left
#Risk Profile
riskProfile = QComboBox()
riskProfile.addItems(["Balanced", "Conservative", "Aggressive"])
VLlayout.addWidget(riskProfile)
# current position
currentPos = QLineEdit()
currentPos.setPlaceholderText("How many do you have now")
VLlayout.addWidget(currentPos)
#New Cash
cashrow = QHBoxLayout()
cash=QLineEdit()
cash.setPlaceholderText("How much do you want to put")
cashrow.addWidget(cash)
cashUnit = QComboBox()
cashUnit.addItems(["CAD","USD","CNY","HKD"])
cashrow.addWidget(cashUnit)
VLlayout.addLayout(cashrow)
#Question
prompts = QTextEdit()
prompts.setPlaceholderText("Enter your investment assistance")
VLlayout.addWidget(prompts)# question at left
#add button
run_button = QPushButton("Run")
run_button.clicked.connect(handle_run)
VLlayout.addWidget(run_button)# button at left
#status title
status_title = QLabel("Status")
VRlayout.addWidget(status_title)
#This is status box
status = QLabel("Waiting for input")
status.setStyleSheet("""QLabel{
                                border: 1px solid #cfcfcf;
                                border-radius: 4px;
                                padding: 6px;
                                background-color: #f5f5f5;}""")# QLabel style
VRlayout.addWidget(status)
#This is output box
output = QTextEdit()
output.setPlainText("Waiting for inputs")
output.setReadOnly(True)
VRlayout.addWidget(output)# output at right
#Attach the layout to the window, then show the window
Hlayout.addLayout(VLlayout,1)
Hlayout.addLayout(VRlayout,2)
window.setLayout(Hlayout)
window.show()
sys.exit(app.exec())


