import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor

def interpolate_color_rgb(start_color, end_color, factor):
    r = start_color.red() + (end_color.red() - start_color.red()) * factor
    g = start_color.green() + (end_color.green() - start_color.green()) * factor
    b = start_color.blue() + (end_color.blue() - start_color.blue()) * factor
    return QColor(int(r), int(g), int(b))

class PythonIDE(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 1600, 1000)
        self.setWindowTitle('Python IDE')

        self.text_editor = QTextEdit(self)
        self.text_editor.setGeometry(10, 50, 780, 940)
        self.text_editor.installEventFilter(self)

        self.output_widget = QTextEdit(self)
        self.output_widget.setGeometry(800, 50, 780, 940)

        self.run_button = QPushButton('Run', self)
        self.run_button.setGeometry(10, 10, 780, 30)
        self.run_button.clicked.connect(self.run_code)

        # Color setup
        self.start_color = QColor(255, 255, 255)  # white
        self.end_color = QColor(100, 100, 255)    # noticeable blue
        self.num_steps = 100
        self.transition_step = 0
        self.is_faded = False
        self.is_transitioning = False

        # Timers
        self.inactivity_timer = QTimer()
        self.inactivity_timer.setInterval(5000)  # 5 seconds idle
        self.inactivity_timer.timeout.connect(self.handle_inactivity)
        self.inactivity_timer.start()

        self.color_timer = QTimer()
        self.color_timer.setInterval(5000)  #milisecs fade
        self.color_timer.timeout.connect(self.step_color_transition)

    def run_code(self):
        from io import StringIO
        import contextlib

        code = self.text_editor.toPlainText()
        output_stream = StringIO()
        with contextlib.redirect_stdout(output_stream):
            try:
                exec(code)
            except Exception as e:
                print(e)
        self.output_widget.setPlainText(output_stream.getvalue())

    def eventFilter(self, source, event):
        if source == self.text_editor and event.type() in (event.KeyPress, event.MouseButtonPress):
            self.reset_on_input()
        return super().eventFilter(source, event)

    def reset_on_input(self):
        # Restart inactivity timer, stop color transition
        self.inactivity_timer.start()
        if self.color_timer.isActive():
            self.color_timer.stop()
        self.transition_step = 0
        self.is_faded = False
        self.is_transitioning = False
        self.text_editor.setStyleSheet("background-color: white;")

    def handle_inactivity(self):
        if not self.is_faded and not self.is_transitioning:
            self.transition_step = 0
            self.is_transitioning = True
            self.color_timer.start()

    def step_color_transition(self):
        if self.transition_step >= self.num_steps:
            self.color_timer.stop()
            self.inactivity_timer.stop()  #Prevent looping
            self.is_faded = True
            self.is_transitioning = False
            return

        factor = self.transition_step / (self.num_steps - 1)
        color = interpolate_color_rgb(self.start_color, self.end_color, factor)
        self.text_editor.setStyleSheet(f"background-color: {color.name()};")
        self.transition_step += 1

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ide = PythonIDE()
    ide.show()
    sys.exit(app.exec_())
