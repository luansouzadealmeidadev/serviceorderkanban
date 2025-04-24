import sys
from PyQt5.QtWidgets import QApplication
from views.Main_window import MainWindow
from styles import apply_modern_style
def main():
    app = QApplication(sys.argv)
    
    apply_modern_style(app)
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()