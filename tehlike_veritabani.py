"""
İş Güvenliği Tehlike Veritabanı
Fine-Kinney metoduna göre risk değerleri:
- Olasılık (O): 0.2, 0.5, 1, 3, 6, 10
- Şiddet (Ş): 1, 3, 7, 15, 40, 100
- Frekans (F): 0.5, 1, 2, 3, 6, 10
"""

TEHLIKE_VERITABANI = {
    "no-helmet": {
        "bolum": "İnşaat Sahası / Üretim Alanı",
        "tehlike_kaynagi": "Baret/kask kullanılmaması",
        "tehlike": "Kafa bölgesinin korunmasız olması",
        "risk": "Düşen cisim çarpması, kafa travması, beyin hasarı, ölüm",
        "mevcut_durum": "Çalışan baret kullanmıyor",
        "etkilenecek": "Tüm çalışanlar, ziyaretçiler",
        "olasilik": 6, "siddet": 40, "frekans": 6,
        "onlem": "Baret kullanımı zorunlu hale getirilmeli, sahaya baretsiz girişler engellenmeli, periyodik denetim yapılmalı, çalışanlara KKD eğitimi verilmeli, baret stoğu sürekli mevcut olmalı.",
        "yeni_olasilik": 1, "yeni_siddet": 40, "yeni_frekans": 1
    },
    "helmet": {
        "bolum": "İnşaat Sahası / Üretim Alanı",
        "tehlike_kaynagi": "Baret kullanımı mevcut",
        "tehlike": "Uygun KKD kullanımı sağlanıyor",
        "risk": "Düşük risk - baret koruması var",
        "mevcut_durum": "Baret kullanılıyor",
        "etkilenecek": "Çalışanlar",
        "olasilik": 1, "siddet": 7, "frekans": 1,
        "onlem": "Mevcut uygulama sürdürülmeli, baretlerin periyodik kontrolü yapılmalı, hasarlı baretler değiştirilmeli.",
        "yeni_olasilik": 0.5, "yeni_siddet": 7, "yeni_frekans": 1
    },
    "no-vest": {
        "bolum": "İnşaat Sahası / Üretim Alanı",
        "tehlike_kaynagi": "Reflektörlü güvenlik yeleği kullanılmaması",
        "tehlike": "Çalışanın görünürlüğünün düşük olması",
        "risk": "Araç çarpması, ezilme, çarpışma, yaralanma, ölüm",
        "mevcut_durum": "Çalışan reflektörlü yelek kullanmıyor",
        "etkilenecek": "Tüm çalışanlar",
        "olasilik": 6, "siddet": 15, "frekans": 6,
        "onlem": "Reflektörlü yelek kullanımı zorunlu hale getirilmeli, gece çalışmalarında yüksek görünürlüklü yelekler temin edilmeli, denetim sıklığı artırılmalı.",
        "yeni_olasilik": 1, "yeni_siddet": 15, "yeni_frekans": 1
    },
    "vest": {
        "bolum": "İnşaat Sahası / Üretim Alanı",
        "tehlike_kaynagi": "Güvenlik yeleği kullanımı mevcut",
        "tehlike": "Uygun KKD kullanımı sağlanıyor",
        "risk": "Düşük risk - görünürlük sağlanıyor",
        "mevcut_durum": "Reflektörlü yelek kullanılıyor",
        "etkilenecek": "Çalışanlar",
        "olasilik": 1, "siddet": 7, "frekans": 1,
        "onlem": "Mevcut uygulama sürdürülmeli, yelek temizliği ve reflektör kontrolleri yapılmalı.",
        "yeni_olasilik": 0.5, "yeni_siddet": 7, "yeni_frekans": 1
    },
    "no-mask": {
        "bolum": "Üretim / Toz-Gaz Çıkan Alanlar",
        "tehlike_kaynagi": "Solunum koruyucu maske kullanılmaması",
        "tehlike": "Toz, gaz, kimyasal solunum maruziyeti",
        "risk": "Solunum yolu hastalıkları, meslek hastalığı, akciğer rahatsızlıkları",
        "mevcut_durum": "Çalışan maske kullanmıyor",
        "etkilenecek": "Tüm çalışanlar",
        "olasilik": 6, "siddet": 15, "frekans": 6,
        "onlem": "Toz/gaz çıkan alanlarda uygun filtreli maske kullanımı zorunlu olmalı, ortam ölçümleri yapılmalı, havalandırma iyileştirilmeli.",
        "yeni_olasilik": 1, "yeni_siddet": 15, "yeni_frekans": 1
    },
    "no-gloves": {
        "bolum": "Üretim / Manuel İş Alanları",
        "tehlike_kaynagi": "İş eldiveni kullanılmaması",
        "tehlike": "El bölgesinin korunmasız olması",
        "risk": "Kesilme, ezilme, kimyasal yanık, el yaralanması",
        "mevcut_durum": "Çalışan eldiven kullanmıyor",
        "etkilenecek": "Çalışanlar",
        "olasilik": 6, "siddet": 7, "frekans": 6,
        "onlem": "İşin niteliğine uygun eldiven temin edilmeli (kesim, kimyasal, ısı vb.), kullanım eğitimi verilmeli, periyodik kontrol sağlanmalı.",
        "yeni_olasilik": 1, "yeni_siddet": 7, "yeni_frekans": 1
    },
    "no-boots": {
        "bolum": "İnşaat Sahası / Üretim Alanı",
        "tehlike_kaynagi": "Çelik burunlu iş ayakkabısı kullanılmaması",
        "tehlike": "Ayak bölgesinin korunmasız olması",
        "risk": "Ezilme, delici cisim batması, kayma, ayak yaralanması",
        "mevcut_durum": "Çalışan iş ayakkabısı kullanmıyor",
        "etkilenecek": "Tüm çalışanlar",
        "olasilik": 6, "siddet": 15, "frekans": 6,
        "onlem": "Çelik burunlu iş ayakkabısı zorunlu hale getirilmeli, uygun ayakkabı temin edilmeli, periyodik denetim yapılmalı.",
        "yeni_olasilik": 1, "yeni_siddet": 15, "yeni_frekans": 1
    },
    "no-harness": {
        "bolum": "Yüksekte Çalışma Alanları",
        "tehlike_kaynagi": "Emniyet kemeri/paraşüt tipi emniyet donanımı kullanılmaması",
        "tehlike": "Yüksekten düşme tehlikesi",
        "risk": "Ölümcül düşme, ağır yaralanma, kalıcı sakatlık",
        "mevcut_durum": "Yüksekte çalışan emniyet donanımı kullanmıyor",
        "etkilenecek": "Yüksekte çalışanlar",
        "olasilik": 6, "siddet": 100, "frekans": 6,
        "onlem": "Yüksekte çalışma izin sistemi kurulmalı, paraşüt tipi emniyet kemeri zorunlu olmalı, yaşam hattı ve ankraj noktaları sağlanmalı, yüksekte çalışma eğitimi verilmeli.",
        "yeni_olasilik": 1, "yeni_siddet": 100, "yeni_frekans": 1
    },
    "person": {
        "bolum": "Genel Çalışma Alanı",
        "tehlike_kaynagi": "Çalışan tespit edildi",
        "tehlike": "Genel iş güvenliği değerlendirmesi gerekli",
        "risk": "Çalışan sahada - iş güvenliği prosedürlerine uyum kontrolü",
        "mevcut_durum": "Çalışan görüntülendi",
        "etkilenecek": "Çalışan",
        "olasilik": 3, "siddet": 7, "frekans": 6,
        "onlem": "Genel iş güvenliği talimatlarına uyulması, KKD kontrolü, çalışma izinleri ve eğitim kayıtlarının güncel tutulması.",
        "yeni_olasilik": 1, "yeni_siddet": 7, "yeni_frekans": 3
    }
}

VARSAYILAN_TEHLIKE = {
    "bolum": "Genel Çalışma Alanı",
    "tehlike_kaynagi": "Tespit edilen durum",
    "tehlike": "Detaylı değerlendirme gerekli",
    "risk": "Uzman değerlendirmesi gerekli",
    "mevcut_durum": "İncelemede",
    "etkilenecek": "Çalışanlar",
    "olasilik": 3, "siddet": 7, "frekans": 3,
    "onlem": "İş güvenliği uzmanı tarafından detaylı değerlendirme yapılmalı.",
    "yeni_olasilik": 1, "yeni_siddet": 7, "yeni_frekans": 1
}


def fine_kinney_skor(o, s, f):
    """Fine-Kinney risk skoru = Olasılık × Şiddet × Frekans"""
    return o * s * f


def fine_kinney_seviye(skor):
    """Fine-Kinney risk seviyesi (resmi prosedüre göre)"""
    if skor < 20:
        return "Önemsiz Risk", "🟢", "Önlem öncelikli değildir"
    elif skor < 70:
        return "Olası Risk", "🔵", "Gözetim altında tutulmalıdır"
    elif skor < 200:
        return "Önemli Risk", "🟡", "Yıl içinde iyileştirilmeli"
    elif skor < 400:
        return "Esaslı Risk", "🟠", "Birkaç ay içinde iyileştirilmeli"
    else:
        return "Kabul Edilemez Risk", "🔴", "ACİL önlem alınmalı, faaliyet durdurulmalı"


def l_matris_skor(o, s):
    """L Matris (5x5) risk skoru = Olasılık × Şiddet"""
    return o * s


def l_matris_seviye(skor):
    """L Matris (5x5) risk seviyesi"""
    if skor <= 2:
        return "Önemsiz Risk", "🟢", "Önlem gerekli değil"
    elif skor <= 6:
        return "Düşük Risk", "🔵", "Mevcut önlemler korunmalı"
    elif skor <= 12:
        return "Orta Risk", "🟡", "Risk azaltılmalı"
    elif skor <= 19:
        return "Yüksek Risk", "🟠", "Acil önlem alınmalı"
    else:
        return "Tolere Edilemez Risk", "🔴", "Çalışma durdurulmalı"
