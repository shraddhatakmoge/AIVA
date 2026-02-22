import sys
from PyQt6.QtWidgets import QApplication
from UI.floating_ui import AIVAOverlay


def main():
    app = QApplication(sys.argv)

    overlay = AIVAOverlay()
    overlay.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
