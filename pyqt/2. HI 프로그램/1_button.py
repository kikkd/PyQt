from PySide6.QtWidgets import QMainWindow, QApplication
from ui import Ui_MainWindow
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.btn_hi.clicked.connect(self.click)

    def click(self):
        self.ui.btn_hi.setText("인사했어요")
        print("클릭 되었습니다.")
        
if __name__ == "__main__":
    app = QApplication()

    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
