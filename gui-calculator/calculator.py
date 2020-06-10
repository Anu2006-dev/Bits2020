import sys
from typing import Dict, Generator, Tuple
import functools
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QKeyEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, \
    QLineEdit, QPushButton, QVBoxLayout, QWidget

__author__ = 'Anupama Dissanayake'


class CalcUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.buttons: Dict[str, CalcCtrl] = {}
        self.chars: str = '789+456-123\u00f7.0\u232B\u00d7=C%'
        self.operations = {'+', '-', '\u00f7', '\u00d7', '%'}
        self.special_charcs = {'C', '=', '\u232B'}
        self.clear = False
        self.setWindowTitle('Calculator')
        self.setFixedSize(450, 500)
        self._central_widget: QWidget = QWidget(self)
        self.setCentralWidget(self._central_widget)
        self.arrangement: QVBoxLayout = QVBoxLayout()
        self._central_widget.setLayout(self.arrangement)
        self._make_display()
        self._make_buttons()
        self.style_sheet: str = open('./style.css').read()
        self.setStyleSheet(self.style_sheet)
        self.event_map = {
            Qt.Key_Backspace: '\u232B',
            Qt.Key_Asterisk: '\u00d7',
            Qt.Key_Slash: '\u00f7',
            Qt.Key_Plus: '+',
            Qt.Key_Equal: '=',
            Qt.Key_Period: '.',
            Qt.Key_Percent: '%',
            Qt.Key_Return: '=',
            Qt.Key_Minus: '-',
            Qt.Key_C: 'C',
            **{getattr(Qt, f'Key_{n}'): str(n) for n in range(10)},
        }

    def keyPressEvent(self, event: QKeyEvent) -> None:
        charac = self.event_map.get(event.key())
        if charac:
            self.buttons[charac].func()

    def _make_display(self):
        self.display: QLineEdit = QLineEdit('0')
        self.display.setFixedSize(400, 65)
        self.display.setFont(QFont("Arial", 27))
        self.display.setAlignment(Qt.AlignRight)
        self.display.setReadOnly(True)
        self.arrangement.addWidget(self.display)

    def _make_buttons(self):
        size = 70
        font: QFont = QFont("Consolas", 13)
        buttons_layout: QGridLayout = QGridLayout()
        positions: Generator[Tuple[int, int]] = (divmod(num, 4) for num in range(20))
        span = [0, 0]

        for pos, symbol in zip(positions, self.chars):
            button: QPushButton = QPushButton(symbol)

            button.setFixedSize(size, size)
            button.setFont(font)
            if symbol == '=':
                span[1] += 1
                pos = [4, 0, 1, 2]
                button.setFixedWidth(180)
            else:
                pos = (x + y for x, y in zip(pos, span))

            if button.text() in self.operations:
                button.setStyleSheet('background-color: red;')

            elif button.text() in self.special_charcs:
                button.setStyleSheet('background-color: yellow; color: black;')

            buttons_layout.addWidget(button, *pos)
            self.buttons[symbol] = CalcCtrl(button, self)

        self.arrangement.addLayout(buttons_layout)


class CalcCtrl:
    def __init__(self, button, window):
        self.button: QPushButton = button
        self.window: CalcUI = window
        self.label: QLineEdit = window.display
        self.text = self.button.text()
        self._expression = '0'
        self.func = None
        self.clear = False
        self._create_connections()

    @property
    def expression(self):
        return self.label.text()

    @expression.setter
    def expression(self, value):
        self._expression = value
        self.label.setText(value)
        self.window.display.setFocus()

    def _create_connections(self):
        self.func = self.make_clear({
            'C': lambda: self.label.setText('0'),
            '\u232B': lambda: self.backspace(self.expression),
            '=': lambda: self.evaluate()  # this does not work when '=': self.evaluate (this is may be a scope issue)
        }.get(self.text, lambda: self.on_click(self.window.operations)))
        self.button.clicked.connect(self.func)
    
    def make_clear(self, func):
        @functools.wraps(func)
        def inner():
            if self.window.clear:
                self.label.setText('0')
                self.window.clear = False
            func()

        return inner

    def backspace(self, text: str):
        label = self.window.display
        if len(text) != 1:
            label.setText(text[:-1])

        else:
            label.setText('0')

    def on_click(self, operations: set):
        if self.expression == '0' and self.text not in {*operations, '.'}:
            self.expression = ''

        if self.text in operations and self.expression[-1] in operations:
            self.expression = self.expression[:-1] + self.text

        else:
            self.expression = self.expression + self.text

    def evaluate(self):
        if self.expression[-1] in self.window.operations:
            return
        self.expression = str(round(eval(self.expression.replace('\u00f7', '/').replace('\u00d7', '*')), 3))
        self.window.clear = True


def main():
    app: QApplication = QApplication(sys.argv)
    window: CalcUI = CalcUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
