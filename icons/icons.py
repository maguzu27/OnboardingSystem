# need PySide6
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

import sys

class Example(QWidget):
    def __init__(self):
        super(Example, self).__init__()
        self.initUI()
        self.Button()

    def initUI(self):
        style = self.style()
        icon = style.standardIcon(QStyle.StandardPixmap.SP_TitleBarMenuButton)
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon(icon))
        self.setWindowIcon(QIcon(icon))
        self.setGeometry(300, 300, 300, 300)

    def Button(self):
        Styles = list(QStyle.StandardPixmap)

        btn = [QToolButton(self) for i in range(len(Styles))]
        self.myHLayout = QGridLayout()
        j = 0
        k = 0
        style = self.style()
        for i in range(len(Styles)):
            btn[i].setText("%s" % (Styles[i].name))
            btn[i].setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            icon = style.standardIcon(Styles[i])
            btn[i].setIcon(QIcon(icon))
            self.myHLayout.addWidget(btn[i], j, k)

            if i == 0:
                k += 1
                pass
            elif 0 == i % 5:
                j += 1
                k = 0
            else:
                k += 1
        self.setLayout(self.myHLayout)

def main():
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    app.exec()

if __name__ == '__main__':
    main()