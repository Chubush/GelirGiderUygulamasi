import sys
from PyQt5.QtWidgets import QApplication
from main import *
app = QApplication(sys.argv)
# Runner
gider_run()
gelir_run()
cansever_run()
cukurova_run()

ui.page_yenile.clicked.connect(page)
# Uygulamayı başlat
sys.exit(app.exec_())

    
    