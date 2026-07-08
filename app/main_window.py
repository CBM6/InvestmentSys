from PySide6.QtWidgets import QHBoxLayout, QWidget, QComboBox
from PySide6.QtWidgets import QVBoxLayout, QLineEdit, QTextEdit
from PySide6.QtWidgets import QPushButton, QLabel, QApplication
from investment.openai_report import generateAiReport
from PySide6.QtCore import QObject, QThread, Signal, Slot

class Reportworker(QObject):
    #Signal is how the worker talks back to the UI Thread
    reportReady = Signal(str)
    errorOccured = Signal(str)
    finished = Signal()
    def __init__(self, prompt_input, prompts_input, risk, currentPosition, cash_display):
        super().__init__()

        #Store the input values before the worker starts
        #Important: these are plain strings =, not UI widgets
        self.prompt_input = prompt_input
        self.prompts_input = prompts_input
        self.risk = risk
        self.currentPosition = currentPosition
        self.cash_display = cash_display

    @Slot()
    def run(self):
        try:
            #This runs in the background thread, so the UI will not freeze
            report = generateAiReport(self.prompt_input, self.prompts_input, self.risk, self.currentPosition,self.cash_display)
            self.reportReady.emit(report)
        except Exception as error:
            #if error happened, sned the error to ui
            self.errorOccured.emit(str(error))
        finally:
            #Worker is done
            self.finished.emit()


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
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.handle_run)
        VLlayout.addWidget(self.run_button)  # button at left
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
        # This is copy Button
        self.copybutton = QPushButton("Copy")
        self.copybutton.clicked.connect(self.handle_copy_report)
        self.copystatus = False
        self.copybutton.setEnabled(self.copystatus)
        VRlayout.addWidget(self.copybutton)
        # Attach the layout to the window, then show the window
        Hlayout.addLayout(VLlayout, 1)
        Hlayout.addLayout(VRlayout, 2)
        self.setLayout(Hlayout)

    def handle_run(self):
        self.copystatus = False
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
            self.copybutton.setEnabled(self.copystatus)
            return
        #Disable the button while the AI request is running
        #Prevents duplicate request
        self.run_button.setEnabled(False)
        self.copybutton.setEnabled(self.copystatus)
        self.status.setText("Running")
        self.output.setPlainText("Generating AI report")

        #Create a background thread and worker for the openAI request
        self.thread = QThread()
        self.worker = Reportworker(prompt_input,prompts_input,risk,currentPosition,cash_display)

        #Move the worker into the background
        self.worker.moveToThread(self.thread)

        #Connect signals
        self.thread.started.connect(self.worker.run)
        self.worker.reportReady.connect(self.handle_report_ready)
        self.worker.errorOccured.connect(self.handle_report_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.handle_thread_finished)

        #Start the thread
        self.thread.start()

    def handle_report_ready(self,report):
        #show the report returned by openai
        self.output.setPlainText(report)
        self.copystatus = True

        # generateAiReport returns setup/request errors as report text,
        # so we check the report content to choose a useful status.
        if report.startswith("# OpenAI Request Failed") or report.startswith("#OpenAI Setup Missing"):
            self.status.setText("Error")
            self.copystatus = False
        else:
            self.status.setText("Done")

    def handle_report_error(self,error):
        self.copystatus = False
        # Show unexpected worker errors in the UI instead of only in the console.
        self.status.setText("Error")
        self.output.setPlainText(f"AI report failed:\n\n{error}")

    def handle_thread_finished(self):
        #Re-enable the Run button after the worker finishes
        self.run_button.setEnabled(True)
        self.copybutton.setEnabled(self.copystatus)
        self.thread = None
        self.worker = None

    def handle_copy_report(self):
        #copy results
        result = self.output.toPlainText().strip()
        QApplication.clipboard().setText(result)
        self.status.setText("Report copied")
