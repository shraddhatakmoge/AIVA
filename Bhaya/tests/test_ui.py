from PyQt6.QtWidgets import QApplication, QLabel
import sys

print("START")

app = QApplication(sys.argv)

label = QLabel("UI Working ✅")
label.show()

print("UI SHOULD SHOW")

sys.exit(app.exec())