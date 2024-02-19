import re
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

def gelir_tablo_olustur():
    try:
        gelir_tablo_olustur = """
        CREATE TABLE IF NOT EXISTS GelirTablo ( 
        ID INTEGER PRIMARY KEY AUTOINCREMENT,   
        Tarih TEXT,
        GelirMiktari REAL,  
        Aciklama TEXT
             )"""
        cursor.execute(gelir_tablo_olustur)
        baglanti.commit()
    except Exception as e:
        QMessageBox.critical(None, "Hata", f"Hata: {e}")



def gelir_kayit_ekle():
    gelir_tablo_olustur()
    gelir_yil = ui.ddm_gelir_yil.currentText().strip()
    gelir_ay = ui.ddm_gelir_ay.currentText().strip()
    gelir_gun = ui.ddm_gelir_gun.currentText().strip()

    gelir_tarih = gelir_yil + "/" + gelir_ay + "/" + gelir_gun
    print("gelir tarih " + gelir_tarih)

    if (
        gelir_yil == "Yıl Gir".strip()
        or gelir_ay == "Ay Gir".strip()
        or gelir_gun == "Gün Gir".strip()
    ):
        QMessageBox.warning(None, "Uyarı", "Lütfen tüm tarih bilgilerini girin.")
        return

    gelir_miktari = ui.ln_gelir_miktar.text().strip()
    if not re.match(r"^\d*\.?\d+$", gelir_miktari):
        QMessageBox.warning(
            None, "Uyarı", "Hata: Gelir miktarı sayısal ve pozitif olmalıdır."
        )
        return
    elif float(gelir_miktari) < 0:
        QMessageBox.warning(None, "Uyarı", "Hata: Gelir miktarı pozitif olmalıdır.")
        return

    gelir_aciklama = ui.ln_gelir_aciklama.text().strip()

    tabloya_ekle = """INSERT INTO GelirTablo (Tarih, GelirMiktari, Aciklama) 
                    VALUES (?, ?, ?)"""

    # Parametrelerin bir tuple içinde olduğundan emin olun
    veri_tuple = (
        gelir_tarih,
        float(gelir_miktari),
        gelir_aciklama,
    )

    try:
        cursor.execute(tabloya_ekle, veri_tuple)
        baglanti.commit()
        QMessageBox.information(None, "Başarılı", "Kayıt eklendi.")
        gelir_listele()
        #lnleri_temizle()
    except Exception as e:
        QMessageBox.critical(None, "Hata", f"Hata: {e}")


def gelir_listele():
    try:
        # Tabloyu temizle
        ui.tbl_gelir.clearContents()
        ui.tbl_gelir.setRowCount(0)

        # Veritabanından verileri çek
        cursor.execute("SELECT ID, Tarih, GelirMiktari, Aciklama FROM GelirTablo")
        veriler = cursor.fetchall()

        # Tabloya verileri ekle
        for row_number, row_data in enumerate(veriler):
            ui.tbl_gelir.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                ui.tbl_gelir.setItem(
                    row_number, column_number, QTableWidgetItem(str(data))
                )

        # Toplam gelir miktarını hesapla
        toplam_gelir = sum(row[2] for row in veriler)

        # Toplam gelir miktarını göster
        ui.ln_toplam_gelir.setText(str(toplam_gelir))

        # Tablo başlıklarını ayarla
        ui.tbl_gelir.setHorizontalHeaderLabels(
            ["ID", "Tarih", "Gelir Miktarı", "Açıklama"]
        )

    except Exception as e:
        QMessageBox.critical(None, "Hata", f"Hata: {e}")


def gelir_kayit_sil():
    # Seçilen satırın indeksini al
    selected_row = ui.tbl_gelir.currentRow()

    if selected_row >= 0:  # Geçerli bir satır seçildiyse devam et
        # Seçilen satırdaki ID'yi al
        gelir_id_item = ui.tbl_gelir.item(selected_row, 0)  # ID sütunu
        if gelir_id_item is not None:
            gelir_id = int(gelir_id_item.text())

            # Kullanıcıya silme işlemini onaylat
            confirm_dialog = QMessageBox.question(
                None,
                "Silme Onayı",
                f"ID {gelir_id} numaralı kaydı silmek istediğinize emin misiniz?",
                QMessageBox.Yes | QMessageBox.No,
            )

            if confirm_dialog == QMessageBox.Yes:
                try:
                    # ID'ye göre ilgili kaydı sil
                    cursor.execute("DELETE FROM GelirTablo WHERE ID = ?", (gelir_id,))
                    baglanti.commit()

                    # Kayıt başarıyla silindi mesajı göster
                    QMessageBox.information(
                        None,
                        "Başarılı",
                        f"ID {gelir_id} numaralı kayıt başarıyla silindi.",
                    )

                    # Tabloyu güncelle
                    gelir_listele()
                except Exception as e:
                    print(e)
                    QMessageBox.critical(None, "Hata", f"Hata: {e}")
            else:
                return
        else:
            QMessageBox.warning(None, "Uyarı", "Seçilen satırın ID'si bulunamadı.")
    else:
        QMessageBox.warning(None, "Uyarı", "Lütfen silinecek bir kayıt seçin.")


def gelir_arama():
    # Arama metnini al
    arama_metni = (
        ui.ln_gelir_ara.text().strip().lower()
    )  # Küçük harfe dönüştür ve boşlukları sil

    # Arama metni boşsa, tüm kayıtları göster ve toplamı güncelle
    if not arama_metni:
        gelir_listele()
        return

    # Tabloyu temizle
    ui.tbl_gelir.clearContents()
    ui.tbl_gelir.setRowCount(0)

    try:
        # Veritabanından verileri çek
        cursor.execute(
            "SELECT ID,Tarih, GelirMiktari, Aciklama FROM GelirTablo WHERE LOWER(Aciklama) LIKE ?",
            ("%" + arama_metni + "%",),
        )
        veriler = cursor.fetchall()

        # Toplam gelir miktarını hesaplamak için bir değişken oluştur
        toplam = 0

        # Tabloya verileri ekle
        for row_number, row_data in enumerate(veriler):
            ui.tbl_gelir.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                ui.tbl_gelir.setItem(
                    row_number, column_number, QTableWidgetItem(str(data))
                )
            # GelirMiktari sütunundaki miktarları toplam değişkenine ekle
            gelir_miktari = float(row_data[2])  # GelirMiktari sütunu (1. sütun)
            toplam += gelir_miktari

        # Toplamı gelir_toplamview içinde göster
        ui.ln_toplam_gelir.setText(str(toplam))

    except Exception as e:
        QMessageBox.critical(None, "Hata", f"Hata: {e}")

def gelir_run():
    ui.tbl_gelir.horizontalHeader().setVisible(True)
    ui.btn_gelir_ekle.clicked.connect(gelir_kayit_ekle)
    ui.btn_gelir_sil.clicked.connect(gelir_kayit_sil)
    ui.btn_gelir_ara.clicked.connect(gelir_arama)
    gelir_listele()
    




