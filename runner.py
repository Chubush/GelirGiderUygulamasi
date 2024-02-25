from main import *


ui.tbl_gider.horizontalHeader().setVisible(True) 

ui.btn_gider_Ekle.clicked.connect(gider_kayit_ekle)    
ui.btn_gider_Sil.clicked.connect(gider_kayit_sil)
ui.btn_gider_ara.clicked.connect(gider_arama)
gider_listele()