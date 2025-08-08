"""
Script Name: console_app.py
Author: Deniz
Created: 2024-08-24
Description: Domino UI
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTextEdit, QLineEdit
from PyQt5.QtGui import QFont, QColor, QBrush, QPalette, QLinearGradient, QGradient
from PyQt5.QtCore import Qt

from model import get_response


class ConsoleApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('TRON Console Conversation')
        self.setGeometry(100, 100, 800, 600)

        # Apply TRON-inspired window border
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
                border: 2px solid #ffffff;
            }
        """)

        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Create a futuristic gradient background for the conversation display area
        self.conversation_display = QTextEdit(self)
        self.conversation_display.setReadOnly(True)

        # gradient = QLinearGradient(0, 0, 0, 1)
        # gradient.setCoordinateMode(QGradient.StretchToDeviceMode)
        # gradient.setColorAt(0.0, QColor("#000000"))
        # gradient.setColorAt(1.0, QColor("#1a1a1a"))

        # palette = QPalette()
        # palette.setBrush(QPalette.Base, QBrush(gradient))
        # self.conversation_display.setPalette(palette)

        # Style for the text within the QTextEdit
        self.conversation_display.setStyleSheet("""
            QTextEdit {
                color: #ffffff;
                font-family: 'Arial', sans-serif;
                font-size: 14pt;
                border: 1px solid #ffffff;
                padding: 10px;
                border-radius: 5px;
                selection-background-color: #404040;
                selection-color: #ffffff;
                background-color: #000000;
                background-image: linear-gradient(#1a1a1a 1px, transparent 1px),
                                linear-gradient(90deg, #1a1a1a 1px, transparent 1px);
                background-size: 20px 20px;
            }
        """)
        main_layout.addWidget(self.conversation_display)

        # TRON style for the input area
        self.input_line = QLineEdit(self)
        self.input_line.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                color: #ffffff;
                font-family: 'Arial', sans-serif;
                font-size: 14pt;
                border: 1px solid #ffffff;
                padding: 5px;
                border-radius: 3px;
            }
            QLineEdit:focus {
                border: 1px solid #808080;
                background-color: #2a2a2a;
            }
        """)
        self.input_line.returnPressed.connect(self.handle_input)
        main_layout.addWidget(self.input_line)

    def handle_input(self):
        user_input = self.input_line.text()
        if user_input:
            self.conversation_display.append(f"> {user_input}")
            self.input_line.clear()

            ### THIS PART
            response = get_response(user_input)
            self.conversation_display.append(f"> {response}")


def run():
    app = QApplication(sys.argv)
    ex = ConsoleApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run()
