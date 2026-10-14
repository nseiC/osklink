import sys
from linux_env import clean_snap_environment

clean_snap_environment()

from PyQt5.QtWidgets import QApplication
from generate_app import generate_main

def main():
    app = QApplication(sys.argv)
    janela = generate_main()
    janela.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

