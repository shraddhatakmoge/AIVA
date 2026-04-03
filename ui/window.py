# from PyQt6.QtWidgets import (
#     QWidget, QLabel, QVBoxLayout, QApplication,
#     QFrame, QHBoxLayout
# )
# from PyQt6.QtCore import Qt, pyqtSignal
# from PyQt6.QtGui import QColor, QPainter, QBrush


# class StatusDot(QWidget):
#     def __init__(self, color="#7dd3fc"):
#         super().__init__()
#         self.color = QColor(color)
#         self.setFixedSize(14, 14)

#     def set_color(self, color):
#         self.color = QColor(color)
#         self.update()

#     def paintEvent(self, event):
#         painter = QPainter(self)
#         painter.setRenderHint(QPainter.RenderHint.Antialiasing)
#         painter.setBrush(QBrush(self.color))
#         painter.setPen(Qt.PenStyle.NoPen)
#         painter.drawEllipse(0, 0, 14, 14)


# class JarvisUI(QWidget):
#     ui_signal = pyqtSignal(str, str)

#     def __init__(self):
#         super().__init__()

#         self.ui_signal.connect(self._apply_ui_update)

#         self.setWindowFlags(
#             Qt.WindowType.FramelessWindowHint |
#             Qt.WindowType.WindowStaysOnTopHint |
#             Qt.WindowType.Tool
#         )
#         self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
#         self.setFixedSize(430, 220)

#         self.container = QFrame(self)
#         self.container.setGeometry(0, 0, 430, 220)
#         self.container.setStyleSheet("""
#             QFrame {
#                 background-color: rgba(17, 24, 39, 245);
#                 border: 1.5px solid rgba(125, 211, 252, 70);
#                 border-radius: 26px;
#             }

#             QLabel {
#                 color: white;
#                 font-family: 'Segoe UI';
#                 background: transparent;
#             }

#             QLabel#assistantName {
#                 font-size: 18px;
#                 font-weight: 700;
#                 color: #7dd3fc;
#             }

#             QLabel#status {
#                 font-size: 13px;
#                 color: #cbd5e1;
#                 font-weight: 500;
#             }

#             QLabel#mainMessage {
#                 font-size: 24px;
#                 font-weight: 700;
#                 color: #f8fafc;
#                 padding-top: 10px;
#             }

#             QLabel#subMessage {
#                 font-size: 14px;
#                 color: #94a3b8;
#                 padding-top: 8px;
#             }
#         """)

#         layout = QVBoxLayout(self.container)
#         layout.setContentsMargins(24, 22, 24, 22)
#         layout.setSpacing(10)

#         top_row = QHBoxLayout()
#         top_row.setSpacing(10)

#         self.dot = StatusDot("#7dd3fc")

#         self.assistant_name = QLabel("JARVIS")
#         self.assistant_name.setObjectName("assistantName")

#         top_row.addWidget(self.dot)
#         top_row.addWidget(self.assistant_name)
#         top_row.addStretch()

#         self.status = QLabel("Idle")
#         self.status.setObjectName("status")

#         self.main_message = QLabel("Say 'Jarvis'")
#         self.main_message.setObjectName("mainMessage")
#         self.main_message.setWordWrap(True)

#         self.sub_message = QLabel("Waiting for your wake word...")
#         self.sub_message.setObjectName("subMessage")
#         self.sub_message.setWordWrap(True)

#         layout.addLayout(top_row)
#         layout.addWidget(self.status)
#         layout.addWidget(self.main_message)
#         layout.addWidget(self.sub_message)

#         screen = QApplication.primaryScreen().availableGeometry()
#         self.move(screen.width() - 470, screen.height() - 280)

#     def update_ui(self, status, message):
#         # SAFE thread-to-UI update
#         self.ui_signal.emit(status, message)

#     def _apply_ui_update(self, status, message):
#         self.status.setText(status)

#         if status.lower() == "idle":
#             self.main_message.setText("Say 'Jarvis'")
#             self.sub_message.setText(message)
#             self.dot.set_color("#7dd3fc")  # cyan

#         elif status.lower() == "active":
#             self.main_message.setText("I'm listening...")
#             self.sub_message.setText(message)
#             self.dot.set_color("#22c55e")  # green

#         elif status.lower() == "you said":
#             self.main_message.setText(message)
#             self.sub_message.setText("Recognized your speech")
#             self.dot.set_color("#facc15")  # yellow

#         elif status.lower() == "error":
#             self.main_message.setText("I didn't catch that")
#             self.sub_message.setText(message)
#             self.dot.set_color("#ef4444")  # red

#         elif status.lower() == "starting":
#             self.main_message.setText("Starting up...")
#             self.sub_message.setText(message)
#             self.dot.set_color("#a78bfa")  # purple

#         else:
#             self.main_message.setText(message)
#             self.sub_message.setText("Assistant status updated")
#             self.dot.set_color("#7dd3fc")

from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QApplication,
    QFrame, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QBrush, QRadialGradient


class GlowOrb(QWidget):
    def __init__(self, color="#7dd3fc"):
        super().__init__()
        self.color = QColor(color)
        self.setFixedSize(42, 42)

    def set_color(self, color):
        self.color = QColor(color)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QRadialGradient(21, 21, 20)
        gradient.setColorAt(0.0, self.color.lighter(170))
        gradient.setColorAt(0.5, self.color)
        gradient.setColorAt(1.0, QColor(0, 0, 0, 0))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, 42, 42)


class JarvisUI(QWidget):
    ui_signal = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()

        self.ui_signal.connect(self._apply_ui_update)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(470, 250)

        self.container = QFrame(self)
        self.container.setGeometry(0, 0, 470, 250)
        self.container.setStyleSheet("""
            QFrame {
                background-color: rgba(12, 18, 28, 245);
                border: 1.5px solid rgba(125, 211, 252, 80);
                border-radius: 28px;
            }

            QLabel {
                color: white;
                font-family: 'Segoe UI';
                background: transparent;
            }

            QLabel#assistantName {
                font-size: 20px;
                font-weight: 700;
                color: #7dd3fc;
                letter-spacing: 1px;
            }

            QLabel#status {
                font-size: 13px;
                color: #cbd5e1;
                font-weight: 500;
            }

            QLabel#mainMessage {
                font-size: 28px;
                font-weight: 700;
                color: #f8fafc;
                padding-top: 6px;
            }

            QLabel#subMessage {
                font-size: 15px;
                color: #94a3b8;
                padding-top: 6px;
            }

            QLabel#footer {
                font-size: 12px;
                color: #64748b;
                padding-top: 14px;
            }
        """)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(28, 24, 28, 22)
        layout.setSpacing(8)

        # Top row
        top_row = QHBoxLayout()
        top_row.setSpacing(14)

        self.orb = GlowOrb("#7dd3fc")

        self.assistant_name = QLabel("JARVIS")
        self.assistant_name.setObjectName("assistantName")

        top_row.addWidget(self.orb)
        top_row.addWidget(self.assistant_name)
        top_row.addStretch()

        # Status line
        self.status = QLabel("Idle")
        self.status.setObjectName("status")

        # Main text
        self.main_message = QLabel("Say 'Jarvis'")
        self.main_message.setObjectName("mainMessage")
        self.main_message.setWordWrap(True)

        # Secondary text
        self.sub_message = QLabel("Waiting for your wake word...")
        self.sub_message.setObjectName("subMessage")
        self.sub_message.setWordWrap(True)

        # Footer
        self.footer = QLabel("Voice Assistant Ready")
        self.footer.setObjectName("footer")

        layout.addLayout(top_row)
        layout.addWidget(self.status)
        layout.addWidget(self.main_message)
        layout.addWidget(self.sub_message)
        layout.addStretch()
        layout.addWidget(self.footer)

        # Position bottom-right
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.width() - 510, screen.height() - 320)

    def update_ui(self, status, message):
        self.ui_signal.emit(status, message)

    def _apply_ui_update(self, status, message):
        self.status.setText(status)

        if status.lower() == "idle":
            self.main_message.setText("Say 'Jarvis'")
            self.sub_message.setText(message)
            self.footer.setText("Waiting for wake word")
            self.orb.set_color("#7dd3fc")  # cyan

        elif status.lower() == "active":
            self.main_message.setText("I'm listening...")
            self.sub_message.setText(message)
            self.footer.setText("Microphone active")
            self.orb.set_color("#22c55e")  # green

        elif status.lower() == "you said":
            self.main_message.setText(message)
            self.sub_message.setText("Recognized your speech")
            self.footer.setText("Speech captured successfully")
            self.orb.set_color("#facc15")  # yellow

        elif status.lower() == "thinking":
            self.main_message.setText("Thinking...")
            self.sub_message.setText(message)
            self.footer.setText("Processing your request")
            self.orb.set_color("#a78bfa")  # purple

        elif status.lower() == "speaking":
            self.main_message.setText("Speaking...")
            self.sub_message.setText(message)
            self.footer.setText("Responding to you")
            self.orb.set_color("#38bdf8")  # bright cyan

        elif status.lower() == "error":
            self.main_message.setText("I didn't catch that")
            self.sub_message.setText(message)
            self.footer.setText("Please try again")
            self.orb.set_color("#ef4444")  # red

        elif status.lower() == "starting":
            self.main_message.setText("Starting up...")
            self.sub_message.setText(message)
            self.footer.setText("Initializing system")
            self.orb.set_color("#f59e0b")  # amber

        else:
            self.main_message.setText(message)
            self.sub_message.setText("Assistant status updated")
            self.footer.setText("Status changed")
            self.orb.set_color("#7dd3fc")