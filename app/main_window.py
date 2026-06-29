from PySide6.QtWidgets import QHBoxLayout, QWidget, QComboBox
from PySide6.QtWidgets import QVBoxLayout, QLineEdit, QTextEdit
from PySide6.QtWidgets import QPushButton, QLabel
from investment.fake_report import fake_report

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        #Main Window
        title = "Investment Assistant"
        self.setWindowTitle(title)
        self.resize(900, 600)
        #stack Widgets
        VLlayout = QVBoxLayout()  # Left side of the window
        VRlayout = QVBoxLayout()  # right side of the window
        Hlayout = QHBoxLayout()  # The whole window
        #Ticker
        self.prompt = QLineEdit()
        self.prompt.setPlaceholderText("Enter your investment assistance")
        VLlayout.addWidget(self.prompt)  # Ticker at left
        # Risk Profile
        self.riskProfile = QComboBox()
        self.riskProfile.addItems(["Balanced", "Conservative", "Aggressive"])
        VLlayout.addWidget(self.riskProfile)
        # current position
        self.currentPos = QLineEdit()
        self.currentPos.setPlaceholderText("How many do you have now")
        VLlayout.addWidget(self.currentPos)
        # New Cash
        cashrow = QHBoxLayout()
        self.cash = QLineEdit()
        self.cash.setPlaceholderText("How much do you want to put")
        cashrow.addWidget(self.cash)

        self.cashUnit = QComboBox()
        self.cashUnit.addItems(["CAD", "USD", "CNY", "HKD"])
        cashrow.addWidget(self.cashUnit)
        VLlayout.addLayout(cashrow)
        # Question
        self.prompts = QTextEdit()
        self.prompts.setPlaceholderText("Enter your investment assistance")
        VLlayout.addWidget(self.prompts)  # question at left
        # add button
        run_button = QPushButton("Run")
        run_button.clicked.connect(self.handle_run)
        VLlayout.addWidget(run_button)  # button at left
        # status title
        status_title = QLabel("Status")
        VRlayout.addWidget(status_title)
        # This is status box
        self.status = QLabel("Waiting for input")
        self.status.setStyleSheet("""QLabel{
                                        border: 1px solid #cfcfcf;
                                        border-radius: 4px;
                                        padding: 6px;
                                        background-color: #f5f5f5;}""")  # QLabel style
        VRlayout.addWidget(self.status)
        # This is output box
        self.output = QTextEdit()
        self.output.setPlainText("Waiting for inputs")
        self.output.setReadOnly(True)
        VRlayout.addWidget(self.output)  # output at right
        # Attach the layout to the window, then show the window
        Hlayout.addLayout(VLlayout, 1)
        Hlayout.addLayout(VRlayout, 2)
        self.setLayout(Hlayout)

    def handle_run(self):
        prompt_input = self.prompt.text().strip()
        prompts_input = self.prompts.toPlainText().strip()
        risk = self.riskProfile.currentText().strip()
        currentPosition = self.currentPos.text().strip()
        if not currentPosition:
            currentPosition = "Not provided"
        newCash = self.cash.text().strip()
        cashU = self.cashUnit.currentText().strip()
        if newCash:
            cash_display = f"{newCash} {cashU}"
        else:
            cash_display = "Not provided"

        # user must enter ticker and questions
        if not prompt_input or not prompts_input:
            self.status.setText("Missing inputs")
            self.output.setPlainText("Please enter both a ticker and questions")
            return
        # Generate fake report
        report = fake_report(prompt_input, prompts_input, risk, currentPosition, cash_display)
        # show the report
        self.status.setText("Report Generated")
        self.output.setPlainText(report)