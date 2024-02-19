import sys
from PyQt5.QtWidgets import QApplication
from gider import gider_run
from gelir import gelir_run
app = QApplication(sys.argv)
def main():

    gider_run()
    gelir_run()

    # Tüm PyQt uygulamalarının döngüsel çalışmasını başlat
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    
    