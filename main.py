from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from panel import Ui_MainWindow
import sys
import pymysql

app = QApplication(sys.argv)
pencere = QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(pencere)
pencere.show()

# Database bağlantısı
baglanti = pymysql.connect(
    host="localhost",
    user="root",
    password="safa123+",
    db="safa_db",
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
)
cursor = baglanti.cursor()


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def gider_kayit_ekle():
    hukuk_sirketi = ui.ddm_gider_SirketSec.currentText().strip()

    if hukuk_sirketi == "Hukuk Şirketi Seç":
        QMessageBox.warning(
            None,
            "Uyarı",
            "Lütfen hukuk şirketi veya şirket dışı seçeneklerinden birini seçin.",
        )
        return

    try:
        gider_tablo_olustur = """
                            
                            CREATE TABLE IF NOT EXISTS GiderTablo (
                            ID INTEGER PRIMARY KEY AUTO_INCREMENT,
                            HukukSirketi TEXT,
                            IsimSoyisim TEXT,
                            TcNo TEXT,
                            SigortaSirketi TEXT,
                            PoliceNo TEXT,
                            HkDk TEXT,
                            MagdurPlaka TEXT,
                            KazaTarihi TEXT,
                            OdemeTutari REAL,
                            StkBasvuruNo TEXT,
                            StkBasvuruTarihi TEXT,
                            StkUcreti REAL,
                            BilirkisiUcreti REAL,
                            Diger REAL,
                            Aciklama TEXT,
                            SpesifikToplam REAL
                        )"""
        cursor.execute(gider_tablo_olustur)
        baglanti.commit()
    except Exception as e:
        QMessageBox.critical(None, "Hata", f"Hata: {e}")

    isim_soyisim = ui.ln_gider_isim.text().strip()
    tc_no = ui.ln_gider_tc.text().strip()
    sigorta_sirketi = ui.ln_gider_sigortasirketi.text().strip()
    police_no = ui.ln_gider_policeno.text().strip()
    hk_dk = ui.ln_gider_hkDk.text().strip()
    magdur_plaka = ui.ln_gider_magdurPlaka.text().strip()

    #kaza tarihi manipülasyonlar
    kazaYil=ui.ddm_gider_kazaTarihi_yil.currentText().strip()
    kazaAy=ui.ddm_gider_kazaTarihi_ay.currentText().strip()
    kazaGun=ui.ddm_gider_kazaTarihi_gun.currentText().strip()
    kaza_tarihi = kazaYil+"/"+kazaAy+"/"+kazaGun

    # OdemeTutari değerinin doğrulanması
    odeme_tutari_input = ui.ln_gider_OdemeTutari.text().strip()
    if is_float(odeme_tutari_input):
        odeme_tutari = float(odeme_tutari_input)
    else:
        QMessageBox.warning(
            None, "Uyarı", "Hata: OdemeTutari değeri sayısal olmalıdır."
        )
        return

    stk_basvuru_no = ui.ln_gider_STKbasvuruNo.text().strip()

    basvuruYil=ui.ddm_gider_stkBasvuruTarihi_yil.currentText().strip()
    basvuruAy=ui.ddm_gider_stkBasvuruTarihi_ay.currentText().strip()
    basvuruGun=ui.ddm_gider_stkBasvuruTarihi_gun.currentText().strip()
    stk_basvuru_tarihi = basvuruYil+"/"+basvuruAy+"/"+basvuruGun
    

    # StkUcreti değerinin doğrulanması
    stk_basvuru_ucreti_input = ui.ln_gider_STKUcreti.text().strip()
    if is_float(stk_basvuru_ucreti_input):
        stk_basvuru_ucreti = float(stk_basvuru_ucreti_input)
    else:
        QMessageBox.warning(None, "Uyarı", "Hata: StkUcreti değeri sayısal olmalıdır.")
        return

    # BilirkisiUcreti değerinin doğrulanması
    bilirkisi_ucreti_input = ui.ln_gider_BilirkisiUcreti.text().strip()
    if is_float(bilirkisi_ucreti_input):
        bilirkisi_ucreti = float(bilirkisi_ucreti_input)
    else:
        QMessageBox.warning(
            None, "Uyarı", "Hata: BilirkisiUcreti değeri sayısal olmalıdır."
        )
        return

    # Diğer giderlerin değerinin doğrulanması
    diger_input = ui.ln_gider_Diger.text().strip()
    if is_float(diger_input):
        diger = float(diger_input)
    else:
        QMessageBox.warning(
            None, "Uyarı", "Hata: Diğer gider değeri sayısal olmalıdır."
        )
        return

    aciklama = ui.ln_gider_aciklama.text().strip()

    spesifik_toplam = (
        odeme_tutari + stk_basvuru_ucreti + bilirkisi_ucreti + diger
    )  # Düzgün toplama işlemi yapılmalı

    tabloya_ekle = """INSERT INTO GiderTablo (HukukSirketi, IsimSoyisim, TcNo, SigortaSirketi, PoliceNo, HkDk, MagdurPlaka, KazaTarihi, OdemeTutari, StkBasvuruNo, StkBasvuruTarihi, StkUcreti, BilirkisiUcreti, Diger, Aciklama, SpesifikToplam) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    # Parametrelerin bir tuple içinde olduğundan emin olun
    veri_tuple = (
        hukuk_sirketi,
        isim_soyisim,
        tc_no,
        sigorta_sirketi,
        police_no,
        hk_dk,
        magdur_plaka,
        kaza_tarihi,
        odeme_tutari,
        stk_basvuru_no,
        stk_basvuru_tarihi,
        stk_basvuru_ucreti,
        bilirkisi_ucreti,
        diger,
        aciklama,
        spesifik_toplam,
    )

    try:
        cursor.execute(tabloya_ekle, veri_tuple)
        baglanti.commit()
        QMessageBox.information(None, "Başarılı", "Kayıt eklendi.")
        gider_listele()
    except Exception as e:
        QMessageBox.critical(None, "Hata", f"Hata: {e}")


def gider_listele():
    # Tabloyu temizle
    ui.tbl_gider.clearContents()
    ui.tbl_gider.setRowCount(0)

    # Veritabanından verileri çek
    cursor.execute("SELECT * FROM GiderTablo")
    veriler = cursor.fetchall()

    # ID sütununu çıkar
    veriler_without_id = [
        {key: value for key, value in row.items() if key != "ID"} for row in veriler
    ]

    # Tabloya verileri ekle
    for row_number, row_data in enumerate(veriler_without_id):
        ui.tbl_gider.insertRow(row_number)
        for column_number, data in enumerate(row_data.values()):
            ui.tbl_gider.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    # Toplamı hesapla ve ln_gider_toplamView içinde göster
    spesifik_toplam_list = [row["SpesifikToplam"] for row in veriler]
    toplam = sum(spesifik_toplam_list)
    ui.ln_gider_toplamView.setText(str(toplam))

    # Tablo başlıklarını ayarla (ID sütunu olmadan)
    ui.tbl_gider.setHorizontalHeaderLabels(
        [
            "Hukuk Şirketi",
            "İsim Soyisim",
            "TC No",
            "Sigorta Şirketi",
            "Poliçe No",
            "HK/DK",
            "Mağdur Plaka",
            "Kaza Tarihi",
            "Odeme Tutari",
            "StkBasvuruNo",
            "StkBasvuruTarihi",
            "Stk Ücreti",
            "Bilirkişi Ücreti",
            "Diğer",
            "Açıklama",
            "Spesifik Toplam",
        ]
    )


def gider_kayit_sil():
    # Seçilen satırın indeksini al
    selected_row = ui.tbl_gider.currentRow()

    if selected_row >= 0:  # Geçerli bir satır seçildiyse devam et
        # Seçilen satırdaki poliçe numarasını al
        policy_number_item = ui.tbl_gider.item(selected_row, 4)  # Poliçe No sütunu
        if policy_number_item is not None:
            policy_number = policy_number_item.text()
            # Kullanıcıya silme işlemi hakkında onay mesajı göster
            confirm_dialog = QMessageBox.question(
                None,
                "Silme İşlemi",
                f"Silmek istediğinize emin misiniz?\nPoliçe numarası {policy_number} olan kayıt silinecek.",
                QMessageBox.Yes | QMessageBox.No,
            )
            if confirm_dialog == QMessageBox.Yes:
                try:
                    # Poliçe numarasına göre ilgili kaydı sil
                    cursor.execute(
                        "DELETE FROM GiderTablo WHERE PoliceNo = %s", (policy_number,)
                    )
                    baglanti.commit()

                    # Kayıt başarıyla silindi mesajı göster
                    QMessageBox.information(
                        None,
                        "Başarılı",
                        f"Poliçe numarası {policy_number} olan kayıt başarıyla silindi.",
                    )

                    # Tabloyu güncelle
                    gider_listele()
                except Exception as e:
                    QMessageBox.critical(None, "Hata", f"Hata: {e}")
            else:
                return  # Silme işlemi iptal edildi
        else:
            QMessageBox.warning(
                None, "Uyarı", "Seçilen satırın poliçe numarası bulunamadı."
            )
    else:
        QMessageBox.warning(None, "Uyarı", "Lütfen silinecek bir kayıt seçin.")


def gider_arama():
    # Arama metnini al
    arama_metni = (
        ui.ln_gider_Ara.text().strip().lower()
    )  # Küçük harfe dönüştür ve boşlukları sil

    # Arama metni boşsa, tüm kayıtları göster
    if not arama_metni:
        gider_listele()
        return

    # Tabloyu temizle
    ui.tbl_gider.clearContents()
    ui.tbl_gider.setRowCount(0)

    try:
        # Veritabanından verileri çek
        cursor.execute(
            "SELECT * FROM GiderTablo WHERE LOWER(HukukSirketi) LIKE %s OR LOWER(IsimSoyisim) LIKE %s OR LOWER(TcNo) LIKE %s OR LOWER(SigortaSirketi) LIKE %s OR LOWER(PoliceNo) LIKE %s OR LOWER(HkDk) LIKE %s OR LOWER(MagdurPlaka) LIKE %s OR LOWER(KazaTarihi) LIKE %s OR LOWER(StkBasvuruNo) LIKE %s OR LOWER(StkBasvuruTarihi) LIKE %s OR LOWER(Aciklama) LIKE %s",
            (
                "%" + arama_metni + "%",
                "%" + arama_metni + "%",
                "%" + arama_metni + "%",
                "%" + arama_metni + "%",
                "%" + arama_metni + "%",
                "%" + arama_metni + "%",
                "%" + arama_metni + "%",
                "%" + arama_metni + "%",
                "%" + arama_metni + "%",
                "%" + arama_metni + "%",
                "%" + arama_metni + "%",
            ),
        )
        veriler = cursor.fetchall()

        # ID sütununu çıkar
        veriler_without_id = [
            {key: value for key, value in row.items() if key != "ID"} for row in veriler
        ]

        # Tabloya verileri ekle
        for row_number, row_data in enumerate(veriler_without_id):
            ui.tbl_gider.insertRow(row_number)
            for column_number, data in enumerate(row_data.values()):
                ui.tbl_gider.setItem(
                    row_number, column_number, QTableWidgetItem(str(data))
                )

        # Toplamı hesapla ve ln_gider_toplamView içinde göster
        spesifik_toplam_list = [row["SpesifikToplam"] for row in veriler]
        toplam = sum(spesifik_toplam_list)
        ui.ln_gider_toplamView.setText(str(toplam))

    except Exception as e:
        QMessageBox.critical(None, "Hata", f"Hata: {e}")


# başlıkları gösterme
ui.tbl_gider.horizontalHeader().setVisible(True)

# Gider ekleme butonuna bağlan
ui.btn_gider_Ekle.clicked.connect(gider_kayit_ekle)
ui.btn_gider_Sil.clicked.connect(gider_kayit_sil)
ui.btn_gider_ara.clicked.connect(gider_arama)
gider_listele()


# 2. modül gelir ekleme
def gelir_kayit_ekle():

    gelir_yil = ui.ddm_gelir_yil.currentText().strip()
    gelir_ay = ui.ddm_gelir_ay.currentText().strip()
    gelir_gun = ui.ddm_gelir_gun.currentText().strip()

    gelir_tarih = gelir_yil + "/" + gelir_ay + "/" + gelir_gun
    print("gelir tarih " + gelir_tarih)

    if (
        gelir_yil == "Yıl Gir".strip()
        and gelir_ay == "Ay Gir".strip()
        and gelir_gun == "Gün Gir".strip()
    ):
        QMessageBox.warning(None, "Uyarı", "Lütfen Tarihi girmeyi unutmayınız ")
        return

    try:
        gelir_tablo_olustur = """
        CREATE TABLE IF NOT EXISTS GelirTablo (
        ID INTEGER PRIMARY KEY AUTO_INCREMENT,
        Tarih TEXT,
        GelirMiktari TEXT,
        Aciklama TEXT
        )"""
        cursor.execute(gelir_tablo_olustur)
        baglanti.commit()
    except Exception as e:
        QMessageBox.critical(None, "Hata", f"Hata: {e}")

    gelir_miktari = ui.ln_gelir_miktar.text().strip()
    gelir_aciklama = ui.ln_gelir_aciklama.text().strip()

    if is_float(gelir_miktari):
        gelir_miktari = float(gelir_miktari)
    else:
        QMessageBox.warning(
            None, "Uyarı", "Hata: Gelir miktari değeri sayısal olmalıdır."
        )
        return

    tabloya_ekle = """INSERT INTO GelirTablo (Tarih, GelirMiktari, Aciklama) 
                    VALUES (%s, %s, %s)"""

    # Parametrelerin bir tuple içinde olduğundan emin olun
    veri_tuple = (
        gelir_tarih,
        gelir_miktari,
        gelir_aciklama,
    )

    try:
        cursor.execute(tabloya_ekle, veri_tuple)
        baglanti.commit()
        QMessageBox.information(None, "Başarılı", "Kayıt eklendi.")
        gider_listele()
    except Exception as e:
        QMessageBox.critical(None, "Hata", f"Hata: {e}")
    gelir_listele()    

def gelir_listele():
    # Tabloyu temizle
    ui.tbl_gelir.clearContents()
    ui.tbl_gelir.setRowCount(0)

    # Veritabanından verileri çek
    cursor.execute("SELECT Tarih, GelirMiktari, Aciklama FROM GelirTablo")
    veriler = cursor.fetchall()

    # ID sütununu çıkar
    veriler_without_id = [
        {key: value for key, value in row.items() if key != "ID"} for row in veriler
    ]

    # Tabloya verileri ekle
    for row_number, row_data in enumerate(veriler_without_id):
        ui.tbl_gelir.insertRow(row_number)
        for column_number, data in enumerate(row_data.values()):
            ui.tbl_gelir.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    # Tablo başlıklarını ayarla
    ui.tbl_gelir.setHorizontalHeaderLabels(["Tarih", "Gelir Miktarı", "Açıklama"])

def gelir_kayit_sil():
    # Seçilen satırın indeksini al
    selected_row = ui.tbl_gelir.currentRow()

    if selected_row >= 0:  # Geçerli bir satır seçildiyse devam et
        # Seçilen satırdaki açıklamayı al
        gelir_aciklama_item = ui.tbl_gelir.item(selected_row, 2)  # Açıklama sütunu
        if gelir_aciklama_item is not None:
            gelir_aciklama = gelir_aciklama_item.text()

            # Kullanıcıya silme işlemini onaylat
            confirm_dialog = QMessageBox.question(None, "Silme Onayı", 
                                                   f"'{gelir_aciklama}' açıklamasına sahip kaydı silmek istediğinize emin misiniz?",
                                                   QMessageBox.Yes | QMessageBox.No)

            if confirm_dialog == QMessageBox.Yes:
                try:
                    # Açıklamaya göre ilgili kaydı sil
                    cursor.execute("DELETE FROM GelirTablo WHERE Aciklama = %s", (gelir_aciklama,))
                    baglanti.commit()

                    # Kayıt başarıyla silindi mesajı göster
                    QMessageBox.information(None, "Başarılı", f"Açıklaması '{gelir_aciklama}' olan kayıt başarıyla silindi.")

                    # Tabloyu güncelle
                    gelir_listele()
                except Exception as e:
                    print(e)
                    QMessageBox.critical(None, "Hata", f"Hata: {e}")
            else:
                return
        else:
            QMessageBox.warning(None, "Uyarı", "Seçilen satırın açıklaması bulunamadı.")
    else:
        QMessageBox.warning(None, "Uyarı", "Lütfen silinecek bir kayıt seçin.")

def gelir_kayit_ara():
    # Arama metnini al
    arama_metni = ui.ln_gelir_ara.text().strip().lower()  # Küçük harfe dönüştür ve boşlukları sil

    # Arama metni boşsa, tüm kayıtları göster
    if not arama_metni:
        gelir_listele()
        return

    # Tabloyu temizle
    ui.tbl_gelir.clearContents()
    ui.tbl_gelir.setRowCount(0)

    try:
        # Veritabanından verileri çek
        cursor.execute(
            "SELECT * FROM GelirTablo WHERE LOWER(Tarih) LIKE %s OR LOWER(GelirMiktari) LIKE %s OR LOWER(Aciklama) LIKE %s",
            ("%" + arama_metni + "%", "%" + arama_metni + "%", "%" + arama_metni + "%"),
        )
        veriler = cursor.fetchall()

        # ID sütununu çıkar
        veriler_without_id = [
            {key: value for key, value in row.items() if key != "ID"} for row in veriler
        ]

        # Tabloya verileri ekle
        for row_number, row_data in enumerate(veriler_without_id):
            ui.tbl_gelir.insertRow(row_number)
            for column_number, data in enumerate(row_data.values()):
                ui.tbl_gelir.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    except Exception as e:
        QMessageBox.critical(None, "Hata", f"Hata: {e}")

   



ui.tbl_gelir.horizontalHeader().setVisible(True)

ui.btn_gelir_ekle.clicked.connect(gelir_kayit_ekle)
ui.btn_gelir_sil.clicked.connect(gelir_kayit_sil)
ui.btn_gelir_ara.clicked.connect(gelir_kayit_ara)
gelir_listele()

#Modül 3 toplamGider-ToplamGelir==ToplamKar

def page():
    try:
        # Veritabanından bütün spesifik giderleri çek
        cursor.execute("SELECT SpesifikToplam FROM GiderTablo")
        giderler = cursor.fetchall()

        # Toplam spesifik gider miktarını hesapla
        toplam_gider = sum(int(gider["SpesifikToplam"]) for gider in giderler)

        # Veritabanından bütün gelirleri çek
        cursor.execute("SELECT GelirMiktari FROM GelirTablo")
        gelirler = cursor.fetchall()

        # Toplam gelir miktarını hesapla
        toplam_gelir = sum(int(gelir["GelirMiktari"]) for gelir in gelirler)

        # Toplam gelir miktarını göster
        ui.page_toplamGelir.setText(str(toplam_gelir))

        # Net karı hesapla
        net_kar = toplam_gelir - toplam_gider

        # Net karı göster
        ui.page_netKar.setText(str(net_kar))

    except Exception as e:
        QMessageBox.critical(None, "Hata", f"Hata: {e}")




page()
# Uygulamayı kapat
sys.exit(app.exec_())