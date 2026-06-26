import sys
import PySide6
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QVBoxLayout, QLineEdit, QTextEdit
from PySide6.QtWidgets import QPushButton

def fake_report(prompt, prompts):
    return f"""#This is fake report

            ## Ticker
            {prompt}

            ## User Question
            {prompts}
            """
def handle_run():
    prompt_input = prompt.text().strip()
    prompts_input = prompts.toPlainText().strip()
    #user must enter ticker and questions
    if not prompt_input or not prompts_input:
        output.setPlainText("Please enter both a ticker and questions")
        return
    #Generate fake report
    report = fake_report(prompt_input, prompts_input)
    #show the report
    output.setPlainText(report)

app = QApplication(sys.argv)

window = QWidget()
#main window
title = "Investment Assistant"
window.setWindowTitle(title)
window.resize(900, 600)
#stack widgets
layout = QVBoxLayout()
#text input -singleline
prompt = QLineEdit()
prompt.setPlaceholderText("Enter your investment assistance")
layout.addWidget(prompt)
#text input -multipleline
prompts = QTextEdit()
prompts.setPlaceholderText("Enter your investment assistance")
layout.addWidget(prompts)
#add button
run_button = QPushButton("Run")
run_button.clicked.connect(handle_run)
layout.addWidget(run_button)
#This is output box
output = QTextEdit()
output.setPlainText("Waiting for inputs")
layout.addWidget(output)
#Attach the layout to the window, then show the window
window.setLayout(layout)
window.show()
sys.exit(app.exec())


