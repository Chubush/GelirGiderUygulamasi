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


def gider_tablo_olustur():
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


def isim_soyisim_kontrol(text):
    pattern = r"^[a-zA-ZğüşıöçĞÜŞİÖÇ\s]+$"
    if re.match(pattern, text):
        return True
    else:
        QMessageBox.critical(None, "Hata", f"İsim yerine {text} ifadesi yanlış sadece harf içermeli")

def tarih_kontrol(yil, ay, gun):
    if yil == "Yıl" or ay == "Ay" or gun == "Gün":
        QMessageBox.critical(None, "Hata", f"Tarih bilgisi giremeyi unutmayın")
    else:
        return True

def aciklama_kontrol(text):
    yasakli_kelimeler = ["%", "drop", "table", "delete"]
    for kelime in yasakli_kelimeler:
        if kelime in text.lower():
            QMessageBox.critical(None, "Hata", f"{text} ifadesi yanlış başka bir ibare deneyin")
        else:
            return False    
    return True

def gider_kayit_ekle():
    gider_tablo_olustur()
    isimSoyisim = ui.ln_gider_isim.text().strip()
    if not isim_soyisim_kontrol(isimSoyisim):
        return

    Yil = ui.ddm_gider_yil.currentText().strip()
    Ay = ui.ddm_gider_ay.currentText().strip()
    Gun = ui.ddm_gider_gun.currentText().strip()
    if not tarih_kontrol(Yil, Ay, Gun):
        return
    tarih = Yil + "/" + Ay + "/" + Gun

    aciklama = ui.ln_gider_aciklama.text().strip()
    if not aciklama_kontrol(aciklama):
        return

    odeme_tutari_input = ui.ln_gider_OdemeTutari.text().strip()
    if is_float(odeme_tutari_input) and float(odeme_tutari_input) >= 0:
        odeme_tutari = float(odeme_tutari_input)
    else:
        QMessageBox.warning(
            None, "Uyarı", "Hata: OdemeTutari değeri sayısal ve pozitif olmalıdır."
        )
        return

    tabloya_ekle = """INSERT INTO GiderTablo (IsimSoyisim, OdemeTutari, Tarih, Aciklama) 
                    VALUES (?,?,?,?)"""

    veri_tuple = (
        isimSoyisim,
        odeme_tutari,
        tarih,        
        aciklama,
    )

    try:
        cursor.execute(tabloya_ekle, veri_tuple)
        baglanti.commit()
        QMessageBox.information(None, "Başarılı", "Kayıt eklendi.")
        gider_listele()
        lnleri_temizle()
    except Exception as e:
        QMessageBox.critical(None, "Hata", f"Hata: {e}")


def gider_listele():
    # Tabloyu temizle
    ui.tbl_gider.clearContents()
    ui.tbl_gider.setRowCount(0)

    # Veritabanından verileri çek
    try:
        cursor.execute("SELECT ID, IsimSoyisim, OdemeTutari, Tarih, Aciklama FROM GiderTablo")
    except Exception as e:
        print(e)
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
            spesifik_toplam = row_data[2]  # OdemeTutari sütunu
            toplam += spesifik_toplam
            toplam=round(toplam,2)
    # Toplamı ln_gider_toplamView içinde göster
    ui.ln_gider_toplamView.setText(str(toplam))

    # Tablo başlıklarını ayarla
    ui.tbl_gider.setHorizontalHeaderLabels(
        [
            "ID",
            "İsim Soyisim",
            "Ödeme Tutarı",   
            "Tarih",                                 
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
    arama_metni = (
        ui.ln_gider_Ara.text().strip().lower()
    )  # Küçük harfe dönüştür ve boşlukları sil

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
            ("%" + arama_metni + "%",)
            * 4,  # 4 parametre için aynı arama metnini tekrarla
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
            spesifik_toplam = row_data[2]  # OdemeTutari sütunu
            toplam += spesifik_toplam

        # Toplamı ln_gider_toplamView içinde göster
        ui.ln_gider_toplamView.setText(str(toplam))

    except Exception as e:
        QMessageBox.critical(None, "Hata", f"Hata: {e}")


# gider Tab Run
def gider_run():
    ui.tbl_gider.horizontalHeader().setVisible(True)
    ui.btn_gider_Ekle.clicked.connect(gider_kayit_ekle)
    ui.btn_gider_Sil.clicked.connect(gider_kayit_sil)
    ui.btn_gider_ara.clicked.connect(gider_arama)
    gider_listele()


##**********Gider Bitti **************************************


# Gelir Başladı ******************************************
# Gelir Tablosu Fonksiyonları
import re


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
    if not aciklama_kontrol(gelir_aciklama):
        return

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
        lnleri_temizle()
    except Exception as e:
        QMessageBox.critical(None, "Hata", f"Hata: {e}")


def gelir_listele():
    try:
        # Tabloyu temizle
        ui.tbl_gelir.clearContents()
        ui.tbl_gelir.setRowCount(0)

        # Veritabanından verileri çek
        cursor.execute("SELECT * FROM GelirTablo")
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
                # Gelir Miktarı sütunu
                if column_number == 2:
                    gelir_miktari = data
                    toplam += gelir_miktari
                    toplam=round(toplam,2)

        # Toplam gelir miktarını göster
        ui.ln_toplam_gelir.setText(str(toplam))

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
    gelir_tablo_olustur()
    ui.tbl_gelir.horizontalHeader().setVisible(True)
    ui.btn_gelir_ekle.clicked.connect(gelir_kayit_ekle)
    ui.btn_gelir_sil.clicked.connect(gelir_kayit_sil)
    ui.btn_gelir_ara.clicked.connect(gelir_arama)
    gelir_listele()


# Gelir Bitti*****************************************************************


# Net Kar********************************************************
def page():
    try:
        # Eğer tarih seçilmişse, o tarihe göre filtrele
        page_yil_index = ui.page_ddm_yil.currentIndex()
        page_ay_index = ui.page_ddm_ay.currentIndex()
        giderler = []
        gelirler = []

        if page_yil_index == 0 and page_ay_index == 0:
            # Yıl ve ay butonlarından herhangi biri seçilmemişse, tüm gelirleri ve giderleri al
            cursor.execute("SELECT OdemeTutari, Tarih FROM GiderTablo")
            giderler = cursor.fetchall()
            cursor.execute("SELECT GelirMiktari, Tarih FROM GelirTablo")
            gelirler = cursor.fetchall()
        else:
            # Veritabanından bütün spesifik giderleri çek
            page_yil = ui.page_ddm_yil.currentText()
            page_ay = ui.page_ddm_ay.currentText()

            cursor.execute("SELECT OdemeTutari, Tarih FROM GiderTablo")
            giderler = [gider for gider in cursor.fetchall() if f"{page_yil}/{page_ay}" in gider[1]]

            # Veritabanından bütün gelirleri çek
            cursor.execute("SELECT GelirMiktari, Tarih FROM GelirTablo")
            gelirler = [gelir for gelir in cursor.fetchall() if f"{page_yil}/{page_ay}" in gelir[1]]
        
        # Toplam spesifik gider miktarını hesapla
        toplam_gider = sum(gider[0] for gider in giderler)
        ui.page_toplamGider.setText(str(toplam_gider))
        
        # Toplam gelir miktarını hesapla
        toplam_gelir = sum(gelir[0] for gelir in gelirler)
        ui.page_toplamGelir.setText(str(toplam_gelir))
        
        # Net karı hesapla
        net_kar = round(toplam_gelir - toplam_gider, 2)
        ui.page_netKar.setText(str(net_kar))

    except Exception as e:
        QMessageBox.critical(None, "Hata", f"Hata: {e}")

# Net Kar Bitiş*******************************************************************************************
def lnleri_temizle():
     # Gider ekranındaki input alanlarını temizle
     try:
         #gider clear
         ui.ln_gider_isim.clear()
         ui.ddm_gider_yil.setCurrentIndex(0)
         ui.ddm_gider_ay.setCurrentIndex(0)
         ui.ddm_gider_gun.setCurrentIndex(0)
         ui.ln_gider_OdemeTutari.clear()
         ui.ln_gider_aciklama.clear()
        #gelir clear
         ui.ddm_gelir_yil.setCurrentIndex(0)
         ui.ddm_gelir_ay.setCurrentIndex(0)
         ui.ddm_gelir_gun.setCurrentIndex(0)
         ui.ln_gelir_miktar.clear()
         ui.ln_gelir_aciklama.clear()
         #cansever clear
         ui.ln_cansever_adSoyad.clear()
         ui.ln_cansever_karsiTarafSigortaSirketi.clear()
         ui.ln_cansever_policeNo.clear()
         ui.ln_cansever_HK_DK.clear()
         ui.ln_cansever_magdur_Plaka.clear()
         ui.ln_cansever_karsi_taraf_plaka.clear()
         ui.ln_cansever_kaza_tarihi.clear()
         ui.ln_tahkim_basvurusundan_once_odeme_tutari.clear()
         ui.ln_cansever_magdur_kusur_orani.clear()
         ui.ln_cansever_sigorta_sirketine_basvuru_tarihi.clear()
         ui.ln_cansever_basvuru_numarasi.clear()
         ui.ln_cansever_tahkim_basvuru_tarihi.clear()
         ui.ln_cansever_tahkim_basvuru_ucreti.clear()
         ui.ln_cansever_bilirkisi_ucreti_ve_tarihi.clear()
         ui.ln_cansever_aciklama.clear()
         # Cukurova clear
         ui.ln_cukurova_isim_soyisim.clear()
         ui.ln_cukurova_sigortasirketi.clear()
         ui.ln_cukurova_policeNo.clear()
         ui.ln_cukurova_talepKonusu.clear()
         ui.ln_cukurova_aracPlaka.clear()
         ui.ln_cukurova_kazaTarihi.clear()
         ui.ln_cukurova_karsiTarafPlakasi.clear()
         ui.ln_cukurova_kusurOrani.clear()
         ui.ln_cukurova_sigortayaBasvuruTarihi.clear()
         ui.ln_cukurova_odemeTutari_tarihi.clear()
         ui.ln_cukurova_stk_basvuru_numarasi.clear()
         ui.ln_cukurova_stkbasvuruTarihi.clear()
         ui.ln_cukurova_stk_basvuru_masrafi.clear()
         ui.ln_cukurova_stk_bilirkisi.clear()
         ui.ln_cukurova_aciklama.clear()





     except Exception as e:
         print(e)


# Cansever Hukuk Başlangıç************************************************************************************************
def cansever_hukuk_tablo_olustur():
    try:
        tablo_olustur = """
        CREATE TABLE IF NOT EXISTS CanseverTablo ( 
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        MagdurAracSahibiAdiSoyadi TEXT,   
        KarsiTarafSigortaSirketi TEXT,
        PoliceNumarasi TEXT,
        HasarFarkiDegerKaybiTalepKonusu TEXT,
        MagdurAracPlaka TEXT,        
        KarsiTarafPlakasi TEXT,
        KazaTarihi TEXT,
        TahkimBasvurusundanOnceOdemeTutari TEXT,
        MagdurKusurOrani TEXT,
        SigortaSirketineBasvuruTarihi TEXT,
        TahkimBasvuruNumarasi TEXT,
        TahkimBasvuruTarihi TEXT,
        TahkimBasvuruUcreti TEXT,
        TahkimBilirkisiUcretiVeTarihi TEXT,
        Aciklama TEXT
             )"""
        cursor.execute(tablo_olustur)
        baglanti.commit()
    except Exception as e:
        QMessageBox.critical(None, "Hata", f"Hata: {e}")

import string

def is_valid_input(text):
    # İzin verilen özel karakterler listesi
    allowed_characters = "/,'\"+"

    # İzin verilen karakterler dışındaki tüm özel karakterler
    special_characters = set(string.punctuation) - set(allowed_characters)

    # Metindeki her bir karakter için kontrol yap
    for char in text:
        if char in special_characters:
            return False

    # Veritabanı komutlarını kontrol et
    database_commands = ["SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE"]
    for command in database_commands:
        if command.lower() in text.lower():
            return False

    # Metin geçerli ise True döndür
    return True
def cansever_kayit_ekle():
    cansever_hukuk_tablo_olustur()
    MagdurAracSahibiAdiSoyadi = ui.ln_cansever_adSoyad.text().strip()
    KarsiTarafSigortaSirketi = ui.ln_cansever_karsiTarafSigortaSirketi.text().strip()
    PoliceNumarasi = ui.ln_cansever_policeNo.text().strip()
    HasarFarkiDegerKaybiTalepKonusu = ui.ln_cansever_HK_DK.text().strip()
    MagdurAracPlaka = ui.ln_cansever_magdur_Plaka.text().strip()
    KarsiTarafPlakasi = ui.ln_cansever_karsi_taraf_plaka.text().strip()
    KazaTarihi = ui.ln_cansever_kaza_tarihi.text().strip()
    TahkimBasvurusundanOnceOdemeTutari = (
        ui.ln_tahkim_basvurusundan_once_odeme_tutari.text().strip()
    )
    MagdurKusurOrani = ui.ln_cansever_magdur_kusur_orani.text().strip()
    SigortaSirketineBasvuruTarihi = (
        ui.ln_cansever_sigorta_sirketine_basvuru_tarihi.text().strip()
    )
    TahkimBasvuruNumarasi = ui.ln_cansever_basvuru_numarasi.text().strip()
    TahkimBasvuruTarihi = ui.ln_cansever_tahkim_basvuru_tarihi.text().strip()
    TahkimBasvuruUcreti = ui.ln_cansever_tahkim_basvuru_ucreti.text().strip()
    TahkimBilirkisiUcretiVeTarihi = (
        ui.ln_cansever_bilirkisi_ucreti_ve_tarihi.text().strip()
    )
    Aciklama = ui.ln_cansever_aciklama.text().strip()

    # Girişlerin boş olup olmadığını kontrol et
    if not all([MagdurAracSahibiAdiSoyadi,
                KarsiTarafSigortaSirketi,
                PoliceNumarasi,
                MagdurAracPlaka,
                KazaTarihi,
                Aciklama]):
        QMessageBox.critical(None, "Hata", "MagdurAracSahibiAdiSoyadi,KarsiTarafSigortaSirketi,PoliceNumarasi,MagdurAracPlaka,KazaTarihi,Aciklama Boş  bırakılamaz!")
        return

    # Kullanıcı girişlerini kontrol et
    if not all(is_valid_input(input_str) for input_str in [MagdurAracSahibiAdiSoyadi,
                                                           KarsiTarafSigortaSirketi,
                                                           PoliceNumarasi,
                                                           HasarFarkiDegerKaybiTalepKonusu,
                                                           MagdurAracPlaka,
                                                           KarsiTarafPlakasi,
                                                           KazaTarihi,
                                                           TahkimBasvurusundanOnceOdemeTutari,
                                                           MagdurKusurOrani,
                                                           SigortaSirketineBasvuruTarihi,
                                                           TahkimBasvuruNumarasi,
                                                           TahkimBasvuruTarihi,
                                                           TahkimBasvuruUcreti,
                                                           TahkimBilirkisiUcretiVeTarihi,
                                                           Aciklama]):
        QMessageBox.critical(None, "Hata", "Geçersiz karakter veya komut girişi.")
        return

    tabloya_ekle = """INSERT INTO CanseverTablo (MagdurAracSahibiAdiSoyadi,
                                                KarsiTarafSigortaSirketi,
                                                PoliceNumarasi,
                                                HasarFarkiDegerKaybiTalepKonusu,
                                                MagdurAracPlaka,
                                                KarsiTarafPlakasi,
                                                KazaTarihi,
                                                TahkimBasvurusundanOnceOdemeTutari,
                                                MagdurKusurOrani,
                                                SigortaSirketineBasvuruTarihi,
                                                TahkimBasvuruNumarasi,
                                                TahkimBasvuruTarihi,
                                                TahkimBasvuruUcreti,
                                                TahkimBilirkisiUcretiVeTarihi,
                                                Aciklama)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    veri_tuple = (
        MagdurAracSahibiAdiSoyadi,
        KarsiTarafSigortaSirketi,
        PoliceNumarasi,
        HasarFarkiDegerKaybiTalepKonusu,
        MagdurAracPlaka,
        KarsiTarafPlakasi,
        KazaTarihi,
        TahkimBasvurusundanOnceOdemeTutari,
        MagdurKusurOrani,
        SigortaSirketineBasvuruTarihi,
        TahkimBasvuruNumarasi,
        TahkimBasvuruTarihi,
        TahkimBasvuruUcreti,
        TahkimBilirkisiUcretiVeTarihi,
        Aciklama,
    )

    try:
        cursor.execute(tabloya_ekle, veri_tuple)
        baglanti.commit()
        QMessageBox.information(None, "Başarılı", "Kayıt eklendi.")
        cansever_kayit_listele()
        # lnleri_temizle()
    except Exception as e:
        QMessageBox.critical(None, "Hata", f"Hata: {e}")
        cansever_kayit_listele()

def cansever_kayit_listele():
    try:
        ui.tbl_cansever.clearContents()
        ui.tbl_cansever.setRowCount(0)

        # Veritabanından verileri çek
        cursor.execute(
            """SELECT ID, MagdurAracSahibiAdiSoyadi, KarsiTarafSigortaSirketi, PoliceNumarasi,
                                HasarFarkiDegerKaybiTalepKonusu, MagdurAracPlaka, KarsiTarafPlakasi,
                                KazaTarihi, TahkimBasvurusundanOnceOdemeTutari, MagdurKusurOrani,
                                SigortaSirketineBasvuruTarihi, TahkimBasvuruNumarasi, TahkimBasvuruTarihi,
                                TahkimBasvuruUcreti, TahkimBilirkisiUcretiVeTarihi, Aciklama 
                         FROM CanseverTablo"""
        )
        veriler = cursor.fetchall()

        # Tabloya verileri ekle
        for row_number, row_data in enumerate(veriler):
            ui.tbl_cansever.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                ui.tbl_cansever.setItem(
                    row_number, column_number, QTableWidgetItem(str(data))
                )

        ui.tbl_cansever.setHorizontalHeaderLabels(
            [
                "ID",
                "MagdurAracSahibiAdiSoyadi",
                "KarsiTarafSigortaSirketi",
                "PoliceNumarasi",
                "HasarFarkiDegerKaybiTalepKonusu",
                "MagdurAracPlaka",
                "KarsiTarafPlakasi",
                "KazaTarihi",
                "TahkimBasvurusundanOnceOdemeTutari",
                "MagdurKusurOrani",
                "SigortaSirketineBasvuruTarihi",
                "TahkimBasvuruNumarasi",
                "TahkimBasvuruTarihi",
                "TahkimBasvuruUcreti",
                "TahkimBilirkisiUcretiVeTarihi",
                "Aciklama",
            ]
        )

    except Exception as e:
        QMessageBox.critical(None, "Hata", f"Hata: {e}")


def cansever_kayit_sil():
    # Seçilen satırın indeksini al
    selected_row = ui.tbl_cansever.currentRow()

    if selected_row >= 0:  # Geçerli bir satır seçildiyse devam et
        # Seçilen satırdaki ID'yi al
        kayit_id_item = ui.tbl_cansever.item(selected_row, 0)  # ID sütunu
        if kayit_id_item is not None:
            kayit_id = int(kayit_id_item.text())

            # Kullanıcıya silme işlemini onaylat
            confirm_dialog = QMessageBox.question(
                None,
                "Silme Onayı",
                f"ID {kayit_id} numaralı kaydı silmek istediğinize emin misiniz?",
                QMessageBox.Yes | QMessageBox.No,
            )

            if confirm_dialog == QMessageBox.Yes:
                try:
                    # ID'ye göre ilgili kaydı sil
                    cursor.execute(
                        "DELETE FROM CanseverTablo WHERE ID = ?", (kayit_id,)
                    )
                    baglanti.commit()

                    # Kayıt başarıyla silindi mesajı göster
                    QMessageBox.information(
                        None,
                        "Başarılı",
                        f"ID {kayit_id} numaralı kayıt başarıyla silindi.",
                    )

                    # Tabloyu güncelle
                    cansever_kayit_listele()
                except Exception as e:
                    print(e)
                    QMessageBox.critical(None, "Hata", f"Hata: {e}")
            else:
                return
        else:
            QMessageBox.warning(None, "Uyarı", "Seçilen satırın ID'si bulunamadı.")
    else:
        QMessageBox.warning(None, "Uyarı", "Lütfen silinecek bir kayıt seçin.")


# Silme işlemi tamamlandıktan sonra tabloyu güncelle



def cansever_arama():
    # Arama metnini al
    arama_metni = ui.ln_arama_cansever.text().strip().lower()

    # Arama metni boşsa, tüm kayıtları göster
    if not arama_metni:
        cansever_kayit_listele()
        return

    try:
        # Veritabanından verileri çek
        cursor.execute(
            """SELECT ID, MagdurAracSahibiAdiSoyadi,KarsiTarafSigortaSirketi,PoliceNumarasi,
               HasarFarkiDegerKaybiTalepKonusu, MagdurAracPlaka, KarsiTarafPlakasi,
               KazaTarihi, TahkimBasvurusundanOnceOdemeTutari, MagdurKusurOrani,
               SigortaSirketineBasvuruTarihi, TahkimBasvuruNumarasi, TahkimBasvuruTarihi,
               TahkimBasvuruUcreti, TahkimBilirkisiUcretiVeTarihi, Aciklama 
        FROM CanseverTablo 
        WHERE LOWER(MagdurAracSahibiAdiSoyadi) LIKE ? OR LOWER(KarsiTarafSigortaSirketi) LIKE ? OR LOWER(PoliceNumarasi) LIKE ?
           OR LOWER(HasarFarkiDegerKaybiTalepKonusu) LIKE ? OR LOWER(MagdurAracPlaka) LIKE ? OR LOWER(KarsiTarafPlakasi) LIKE ?
           OR LOWER(KazaTarihi) LIKE ? OR LOWER(TahkimBasvurusundanOnceOdemeTutari) LIKE ? OR LOWER(MagdurKusurOrani) LIKE ?
           OR LOWER(SigortaSirketineBasvuruTarihi) LIKE ? OR LOWER(TahkimBasvuruNumarasi) LIKE ? OR LOWER(TahkimBasvuruTarihi) LIKE ?
           OR LOWER(TahkimBasvuruUcreti) LIKE ? OR LOWER(TahkimBilirkisiUcretiVeTarihi) LIKE ? OR LOWER(Aciklama) LIKE ?""",
            ("%" + arama_metni + "%",) * 15,
        )
        veriler = cursor.fetchall()

        # Tabloyu temizle
        ui.tbl_cansever.clearContents()
        ui.tbl_cansever.setRowCount(0)

        # Tabloya verileri ekle
        for row_number, row_data in enumerate(veriler):
            ui.tbl_cansever.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                ui.tbl_cansever.setItem(
                    row_number, column_number, QTableWidgetItem(str(data))
                )

    except Exception as e:
        QMessageBox.critical(None, "Hata", f"Hata: {e}")


def cansever_run():
    ui.tbl_cansever.horizontalHeader().setVisible(True)
    cansever_hukuk_tablo_olustur()
    ui.btn_cansever_ekle.clicked.connect(cansever_kayit_ekle)
    ui.btn_cansever_sil.clicked.connect(cansever_kayit_sil)
    ui.btn_ara_cansever.clicked.connect(cansever_arama)
    cansever_kayit_listele()


# cansever Run bitiş ************************************************************************************************

# CukurovaHukuk Başlangıçç***********************    ****************************************************************


def cukurova_hukuk_tablo_olustur():
    try:
        tablo_olustur = """ 
                CREATE TABLE IF NOT EXISTS CukurovaTablo(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                AracSahibiAdiSoyadiTC TEXT,
                SigortaSirketi TEXT,
                PoliceNumarasi TEXT,
                TalepKonusu TEXT,
                AracPlaka TEXT,
                KazaTarihi TEXT,
                KarsiTarafPlakasi TEXT,
                KusurOrani TEXT,
                SigortayaBasvuruTarihi TEXT,
                OdemeTutariTarihi TEXT,
                STKBasvuruNumarasi TEXT,
                STKBasvuruTarihi TEXT,
                STKBasvuruMasrafi TEXT,
                STKBilirkisi TEXT,
                Aciklama TEXT
                )"""
        cursor.execute(tablo_olustur)
        baglanti.commit()
    except Exception as e:
        QMessageBox.critical(None, "Hata", f"Hata: {e}")


def cukurova_kayit_ekle():
    cukurova_hukuk_tablo_olustur()
    AracSahibiAdiSoyadiTC = ui.ln_cukurova_isim_soyisim.text().strip()
    SigortaSirketi = ui.ln_cukurova_sigortasirketi.text().strip()
    PoliceNumarasi = ui.ln_cukurova_policeNo.text().strip()
    TalepKonusu = ui.ln_cukurova_talepKonusu.text().strip()
    AracPlaka = ui.ln_cukurova_aracPlaka.text().strip()
    KazaTarihi = ui.ln_cukurova_kazaTarihi.text().strip()
    KarsiTarafPlakasi = ui.ln_cukurova_karsiTarafPlakasi.text().strip()
    KusurOrani = ui.ln_cukurova_kusurOrani.text().strip()
    SigortayaBasvuruTarihi = ui.ln_cukurova_sigortayaBasvuruTarihi.text().strip()
    OdemeTutariTarihi = ui.ln_cukurova_odemeTutari_tarihi.text().strip()
    STKBasvuruNumarasi = ui.ln_cukurova_stk_basvuru_numarasi.text().strip()
    STKBasvuruTarihi = ui.ln_cukurova_stkbasvuruTarihi.text().strip()
    STKBasvuruMasrafi = ui.ln_cukurova_stk_basvuru_masrafi.text().strip()
    STKBilirkisi = ui.ln_cukurova_stk_bilirkisi.text().strip()
    Aciklama = ui.ln_cukurova_aciklama.text().strip()

    # Girişlerin boş olup olmadığını kontrol et
    if not all([AracSahibiAdiSoyadiTC, SigortaSirketi, PoliceNumarasi, AracPlaka, KazaTarihi, Aciklama]):
        QMessageBox.critical(None, "Hata", "AracSahibiAdiSoyadiTC,SigortaSirketi,PoliceNumarasi,AracPlaka,KazaTarihi,Aciklama boş bırakılamaz.")
        return

    # Kullanıcı girişlerini kontrol et
    if not all(is_valid_input(input_str) for input_str in [AracSahibiAdiSoyadiTC,
                                                           SigortaSirketi,
                                                           PoliceNumarasi,
                                                           TalepKonusu,
                                                           AracPlaka,
                                                           KazaTarihi,
                                                           KarsiTarafPlakasi,
                                                           KusurOrani,
                                                           SigortayaBasvuruTarihi,
                                                           OdemeTutariTarihi,
                                                           STKBasvuruNumarasi,
                                                           STKBasvuruTarihi,
                                                           STKBasvuruMasrafi,
                                                           STKBilirkisi,
                                                           Aciklama]):
        QMessageBox.critical(None, "Hata", "Geçersiz karakter veya komut girişi.")
        return

    cukurova_tabloya_ekle = """INSERT INTO CukurovaTablo (AracSahibiAdiSoyadiTC,SigortaSirketi,PoliceNumarasi,TalepKonusu,AracPlaka,KazaTarihi,KarsiTarafPlakasi,KusurOrani,SigortayaBasvuruTarihi,
    OdemeTutariTarihi,STKBasvuruNumarasi,STKBasvuruTarihi,STKBasvuruMasrafi,STKBilirkisi,Aciklama) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""

    veri_tuple = (
        AracSahibiAdiSoyadiTC,
        SigortaSirketi,
        PoliceNumarasi,
        TalepKonusu,
        AracPlaka,
        KazaTarihi,
        KarsiTarafPlakasi,
        KusurOrani,
        SigortayaBasvuruTarihi,
        OdemeTutariTarihi,
        STKBasvuruNumarasi,
        STKBasvuruTarihi,
        STKBasvuruMasrafi,
        STKBilirkisi,
        Aciklama,
    )
    try:
        cursor.execute(cukurova_tabloya_ekle, veri_tuple)
        baglanti.commit()
        QMessageBox.information(None, "Başarılı", "Kayıt eklendi.")
        cukurova_kayit_listele()
        # lnleri_temizle()
    except Exception as e:
        QMessageBox.critical(None, "Hata", f"Hata: {e}")   


def cukurova_kayit_listele():
    try:
        ui.tbl_cukurova.clearContents()
        ui.tbl_cukurova.setRowCount(0)
        cursor.execute("""SELECT ID, AracSahibiAdiSoyadiTC, SigortaSirketi, PoliceNumarasi,
                                TalepKonusu, AracPlaka, KazaTarihi, KarsiTarafPlakasi, KusurOrani,
                                SigortayaBasvuruTarihi, OdemeTutariTarihi, STKBasvuruNumarasi,
                                STKBasvuruTarihi, STKBasvuruMasrafi, STKBilirkisi, Aciklama
                         FROM CukurovaTablo""")
        veriler = cursor.fetchall()

        # Tabloya verileri ekle
        for row_number, row_data in enumerate(veriler):
            ui.tbl_cukurova.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                ui.tbl_cukurova.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        ui.tbl_cukurova.setHorizontalHeaderLabels(
            ["ID", "AracSahibiAdiSoyadiTC", "SigortaSirketi", "PoliceNumarasi", "TalepKonusu",
             "AracPlaka", "KazaTarihi", "KarsiTarafPlakasi", "KusurOrani", "SigortayaBasvuruTarihi",
             "OdemeTutariTarihi", "STKBasvuruNumarasi", "STKBasvuruTarihi", "STKBasvuruMasrafi",
             "STKBilirkisi", "Aciklama"]
        )
    except Exception as e:
        QMessageBox.critical(None, "Hata", f"Hata: {e}") 

def cukurova_kayit_sil():
    # Seçilen satırın indeksini al
    selected_row = ui.tbl_cukurova.currentRow()

    if selected_row >= 0:  # Geçerli bir satır seçildiyse devam et
        # Seçilen satırdaki ID'yi al
        kayit_id_item = ui.tbl_cukurova.item(selected_row, 0)  # ID sütunu
        if kayit_id_item is not None:
            kayit_id = int(kayit_id_item.text())

            # Kullanıcıya silme işlemini onaylat
            confirm_dialog = QMessageBox.question(
                None,
                "Silme Onayı",
                f"ID {kayit_id} numaralı kaydı silmek istediğinize emin misiniz?",
                QMessageBox.Yes | QMessageBox.No,
            )

            if confirm_dialog == QMessageBox.Yes:
                try:
                    # ID'ye göre ilgili kaydı sil
                    cursor.execute("DELETE FROM CukurovaTablo WHERE ID = ?", (kayit_id,))
                    baglanti.commit()

                    # Kayıt başarıyla silindi mesajı göster
                    QMessageBox.information(
                        None,
                        "Başarılı",
                        f"ID {kayit_id} numaralı kayıt başarıyla silindi.",
                        
                    )

                    # Tabloyu güncelle
                    cukurova_kayit_listele()
                except Exception as e:
                    print(e)
                    QMessageBox.critical(None, "Hata", f"Hata: {e}")
            else:
                return
        else:
            QMessageBox.warning(None, "Uyarı", "Seçilen satırın ID'si bulunamadı.")
    else:
        QMessageBox.warning(None, "Uyarı", "Lütfen silinecek bir kayıt seçin.")

def cukurova_arama():
    # Arama metnini al
    arama_metni = ui.ln_cukurova_arama.text().strip().lower()

    # Arama metni boşsa, tüm kayıtları göster
    if not arama_metni:
        cukurova_kayit_listele()
        return

    try:
        # Veritabanından verileri çek ve arama metnini içeren kayıtları getir
        cursor.execute(
            """SELECT ID, AracSahibiAdiSoyadiTC, SigortaSirketi, PoliceNumarasi,
                       TalepKonusu, AracPlaka, KazaTarihi, KarsiTarafPlakasi,
                       KusurOrani, SigortayaBasvuruTarihi, OdemeTutariTarihi,
                       STKBasvuruNumarasi, STKBasvuruTarihi, STKBasvuruMasrafi,
                       STKBilirkisi, Aciklama 
               FROM CukurovaTablo 
               WHERE LOWER(AracSahibiAdiSoyadiTC) LIKE ? 
               OR LOWER(SigortaSirketi) LIKE ? 
               OR LOWER(PoliceNumarasi) LIKE ? 
               OR LOWER(TalepKonusu) LIKE ? 
               OR LOWER(AracPlaka) LIKE ? 
               OR LOWER(KazaTarihi) LIKE ? 
               OR LOWER(KarsiTarafPlakasi) LIKE ? 
               OR LOWER(KusurOrani) LIKE ? 
               OR LOWER(SigortayaBasvuruTarihi) LIKE ? 
               OR LOWER(OdemeTutariTarihi) LIKE ? 
               OR LOWER(STKBasvuruNumarasi) LIKE ? 
               OR LOWER(STKBasvuruTarihi) LIKE ? 
               OR LOWER(STKBasvuruMasrafi) LIKE ? 
               OR LOWER(STKBilirkisi) LIKE ? 
               OR LOWER(Aciklama) LIKE ?""",
            ("%" + arama_metni + "%",) * 15,  # Placeholder'ları doldur
        )
        veriler = cursor.fetchall()

        # Tabloyu temizle
        ui.tbl_cukurova.clearContents()
        ui.tbl_cukurova.setRowCount(0)

        # Tabloya verileri ekle
        for row_number, row_data in enumerate(veriler):
            ui.tbl_cukurova.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                ui.tbl_cukurova.setItem(
                    row_number, column_number, QTableWidgetItem(str(data))
                )

    except Exception as e:
        QMessageBox.critical(None, "Hata", f"Hata: {e}")

def cukurova_run():
    ui.tbl_cukurova.horizontalHeader().setVisible(True)
    cukurova_hukuk_tablo_olustur()
    ui.btn_cukurova_ekle.clicked.connect(cukurova_kayit_ekle)
    ui.btn_cukurova_kayitsil.clicked.connect(cukurova_kayit_sil)
    ui.btn_cukurova_ara.clicked.connect(cukurova_arama)
    cukurova_kayit_listele()


# Runner
gider_run()
gelir_run()
cansever_run()
cukurova_run()

ui.page_yenile.clicked.connect(page)
# Uygulamayı başlat
sys.exit(app.exec_())
