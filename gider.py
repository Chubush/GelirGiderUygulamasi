from PyQt5.QtWidgets import *
from panel import Ui_MainWindow

import sys
import sqlite3

app = QApplication(sys.argv)
pencere = QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(pencere)
pencere.show()

baglanti = sqlite3.connect("veritabani.db")
cursor = baglanti.cursor()
baglanti.commit()


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


try:
    gider_tablo_olustur_sorgusu = """
            CREATE TABLE IF NOT EXISTS GiderTablo(
            ID INTEGER PRIMARY KEY AUTOINCREMENT,           
            IsimSoyisim TEXT, 
           	Tarih Text,
            OdemeTutari REAL,
            Aciklama TEXT)
        """
    cursor.execute(gider_tablo_olustur_sorgusu)
    baglanti.commit()
except Exception as e:
    QMessageBox.critical(None, "Hata", f"Hata: {e}")


def gider_kayit_ekle():

    isimSoyisim = ui.ln_gider_isim.text().strip()

    # kaza tarihi manipülasyonlar
    Yil = ui.ddm_gider_yil.currentText().strip()
    Ay = ui.ddm_gider_ay.currentText().strip()
    Gun = ui.ddm_gider_gun.currentText().strip()
    tarih = Yil + "/" + Ay + "/" + Gun

    aciklama = ui.ln_gider_aciklama.text().strip()

    # OdemeTutari değerinin doğrulanması
    odeme_tutari_input = ui.ln_gider_OdemeTutari.text().strip()

    if is_float(odeme_tutari_input) and float(odeme_tutari_input) >= 0:
        odeme_tutari = float(odeme_tutari_input)
    else:
        QMessageBox.warning(
            None, "Uyarı", "Hata: OdemeTutari değeri sayısal ve pozitif olmalıdır."
        )
        return

    tabloya_ekle = """INSERT INTO GiderTablo (IsimSoyisim, Tarih, OdemeTutari, Aciklama) 
                    VALUES (?,?,?,?)"""

    # Parametrelerin bir tuple içinde olduğundan emin olun
    veri_tuple = (
        isimSoyisim,
        tarih,
        odeme_tutari,
        aciklama,
    )

    try:
        cursor.execute(tabloya_ekle, veri_tuple)
        baglanti.commit()
        QMessageBox.information(None, "Başarılı", "Kayıt eklendi.")
        gider_listele()
        # lnleri_temizle()
    except Exception as e:
        QMessageBox.critical(None, "Hata", f"Hata: {e}")


def gider_listele():
    # Tabloyu temizle
    ui.tbl_gider.clearContents()
    ui.tbl_gider.setRowCount(0)

    # Veritabanından verileri çek
    try:
        cursor.execute("SELECT * FROM GiderTablo")
    except Exception as e:
        print(e)    
    veriler = cursor.fetchall()

    # Toplam spesifik gider miktarını hesaplamak için bir değişken oluştur
    toplam = 0

    # Tabloya verileri ekle
    for row_number, row_data in enumerate(veriler):
        ui.tbl_gider.insertRow(row_number)
        for column_number, data in enumerate(row_data):
            ui.tbl_gider.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        # Son sütun, SpesifikToplam değerlerini toplam değişkenine ekle
        spesifik_toplam = row_data[-2]  # Son sütun, SpesifikToplam
        toplam += spesifik_toplam

    # Toplamı ln_gider_toplamView içinde göster
    ui.ln_gider_toplamView.setText(str(toplam))

    # Tablo başlıklarını ayarla
    ui.tbl_gider.setHorizontalHeaderLabels(
        [
            "ID",
            "İsim Soyisim",
            "Tarih",
            "Ödeme Tutarı",
            "Açıklama",           
        ]
    )


def gider_kayit_sil():
    # Seçilen satırın indeksini al
    selected_row = ui.tbl_gider.currentRow()

    if selected_row >= 0:  # Geçerli bir satır seçildiyse devam et
        # Seçilen satırdaki ID değerini al
        id_item = ui.tbl_gider.item(selected_row, 0)  # ID sütunu
        if id_item is not None:
            record_id = id_item.text()
            # Kullanıcıya silme işlemi hakkında onay mesajı göster
            confirm_dialog = QMessageBox.question(
                None,
                "Silme İşlemi",
                f"Silmek istediğinize emin misiniz?\nID {record_id} olan kayıt silinecek.",
                QMessageBox.Yes | QMessageBox.No,
            )
            if confirm_dialog == QMessageBox.Yes:
                try:
                    # ID'ye göre ilgili kaydı sil
                    cursor.execute("DELETE FROM GiderTablo WHERE ID = ?", (record_id,))
                    baglanti.commit()

                    # Kayıt başarıyla silindi mesajı göster
                    QMessageBox.information(
                        None,
                        "Başarılı",
                        f"ID {record_id} olan kayıt başarıyla silindi.",
                    )

                    # Tabloyu güncelle
                    gider_listele()
                except Exception as e:
                    QMessageBox.critical(None, "Hata", f"Hata: {e}")
            else:
                return  # Silme işlemi iptal edildi
        else:
            QMessageBox.warning(None, "Uyarı", "Seçilen satırın ID değeri bulunamadı.")
    else:
        QMessageBox.warning(None, "Uyarı", "Lütfen silinecek bir kayıt seçin.")


def gider_arama():
    # Arama metnini al
    arama_metni = ui.ln_gider_Ara.text().strip().lower()  # Küçük harfe dönüştür ve boşlukları sil

    # Arama metni boşsa, tüm kayıtları göster ve toplamı güncelle
    if not arama_metni:
        gider_listele()
        return

    # Tabloyu temizle
    ui.tbl_gider.clearContents()
    ui.tbl_gider.setRowCount(0)

    try:
        # Veritabanından verileri çek
        cursor.execute(
            "SELECT * FROM GiderTablo WHERE LOWER(IsimSoyisim) LIKE ? OR LOWER(Tarih) LIKE ? OR LOWER(Aciklama) LIKE ? OR LOWER(OdemeTutari) LIKE ?",
            ("%" + arama_metni + "%",) * 4,  # 4 parametre için aynı arama metnini tekrarla
        )
        veriler = cursor.fetchall()

        # Toplam spesifik gider miktarını hesaplamak için bir değişken oluştur
        toplam = 0

        # Tabloya verileri ekle
        for row_number, row_data in enumerate(veriler):
            ui.tbl_gider.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                ui.tbl_gider.setItem(
                    row_number, column_number, QTableWidgetItem(str(data))
                )
            # Son sütun, OdemeTutari değerlerini toplam değişkenine ekle
            spesifik_toplam = row_data[3]  # OdemeTutari sütunu
            toplam += spesifik_toplam

        # Toplamı ln_gider_toplamView içinde göster
        ui.ln_gider_toplamView.setText(str(toplam))

    except Exception as e:
        QMessageBox.critical(None, "Hata", f"Hata: {e}")

#gider Tab Run
def gider_run():
    ui.tbl_gider.horizontalHeader().setVisible(True)
    ui.btn_gider_Ekle.clicked.connect(gider_kayit_ekle)
    ui.btn_gider_Sil.clicked.connect(gider_kayit_sil)
    ui.btn_gider_ara.clicked.connect(gider_arama)
    gider_listele()
    
gider_run()    



