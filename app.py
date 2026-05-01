# === BAŞLANGIÇ ===
import streamlit as st
from inference_sdk import InferenceHTTPClient
from PIL import Image
import pandas as pd
import io
import base64

# Sayfa ayarları
st.set_page_config(
    page_title="İş Güvenliği Risk Değerlendirme",
    page_icon="🦺",
    layout="wide"
)

# Başlık
st.title("🦺 İş Güvenliği Risk Değerlendirme Sistemi")
st.markdown("Fotoğraf yükleyerek iş güvenliği eksikliklerini tespit edin ve risk değerlendirmesi yapın.")

# Sidebar - Ayarlar
with st.sidebar:
    st.header("⚙️ Ayarlar")
    api_key = st.text_input("Roboflow API Key", type="password", help="Roboflow hesabınızdan alın")
    
    st.markdown("---")
    st.header("📊 Risk Yöntemi")
    risk_method = st.radio(
        "Risk değerlendirme yöntemi:",
        ["Fine-Kinney", "L Matris (5x5)", "Her İkisi"]
    )
    
    st.markdown("---")
    st.markdown("### ℹ️ Hakkında")
    st.info("Bu uygulama Roboflow AI modeli ile iş güvenliği eksikliklerini tespit eder ve otomatik risk değerlendirmesi yapar.")

# Tehlike-Risk Eşleştirme Tablosu (Modelinize göre özelleştirilebilir)
TEHLIKE_RISK_TABLOSU = {
    # Fine-Kinney: Olasılık (O) x Frekans (F) x Şiddet (Ş)
    # L Matris: Olasılık (O) x Şiddet (Ş)
    "no-helmet": {
        "tehlike": "Baret/Kask Takmama",
        "sonuc": "Kafa travması, beyin hasarı, ölüm",
        "fk_olasilik": 6,    # Yüksek olasılık
        "fk_frekans": 6,     # Sürekli
        "fk_siddet": 15,     # Çok ciddi (ölümcül)
        "lm_olasilik": 4,    # Yüksek
        "lm_siddet": 5,      # Çok ciddi
        "onlem": "Kişisel koruyucu donanım (baret) zorunluluğu, eğitim, denetim"
    },
    "helmet": {
        "tehlike": "Baret Mevcut",
        "sonuc": "Uygun kullanım sağlanıyor",
        "fk_olasilik": 1, "fk_frekans": 1, "fk_siddet": 1,
        "lm_olasilik": 1, "lm_siddet": 1,
        "onlem": "Mevcut uygulamayı sürdür"
    },
    "no-vest": {
        "tehlike": "Güvenlik Yeleği Takmama",
        "sonuc": "Görünürlük azlığı, çarpma, ezilme riski",
        "fk_olasilik": 6, "fk_frekans": 6, "fk_siddet": 7,
        "lm_olasilik": 4, "lm_siddet": 4,
        "onlem": "Reflektörlü yelek zorunluluğu, eğitim, denetim"
    },
    "vest": {
        "tehlike": "Yelek Mevcut",
        "sonuc": "Uygun kullanım sağlanıyor",
        "fk_olasilik": 1, "fk_frekans": 1, "fk_siddet": 1,
        "lm_olasilik": 1, "lm_siddet": 1,
        "onlem": "Mevcut uygulamayı sürdür"
    },
    "person": {
        "tehlike": "Çalışan Tespit Edildi",
        "sonuc": "Genel iş güvenliği değerlendirmesi gerekli",
        "fk_olasilik": 3, "fk_frekans": 6, "fk_siddet": 3,
        "lm_olasilik": 3, "lm_siddet": 3,
        "onlem": "Genel iş güvenliği talimatlarına uyulması"
    }
}

# Varsayılan (bilinmeyen sınıflar için)
VARSAYILAN_RISK = {
    "tehlike": "Tespit Edilen Durum",
    "sonuc": "Detaylı değerlendirme gerekli",
    "fk_olasilik": 3, "fk_frekans": 3, "fk_siddet": 7,
    "lm_olasilik": 3, "lm_siddet": 3,
    "onlem": "Uzman değerlendirmesi gerekli"
}

def fine_kinney_skor(o, f, s):
    """Fine-Kinney risk skoru = Olasılık x Frekans x Şiddet"""
    return o * f * s

def fine_kinney_seviye(skor):
    """Fine-Kinney risk seviyesi"""
    if skor < 20:
        return "🟢 Önemsiz Risk", "Acil önlem gerekmez"
    elif skor < 70:
        return "🟡 Olası Risk", "Dikkat altında tutulmalı"
    elif skor < 200:
        return "🟠 Önemli Risk", "Yıl içinde önlem alınmalı"
    elif skor < 400:
        return "🔴 Esaslı Risk", "Kısa sürede önlem alınmalı"
    else:
        return "⚫ Kabul Edilemez Risk", "ACİL önlem alınmalı, çalışma durdurulmalı"

def l_matris_skor(o, s):
    """L Matris risk skoru = Olasılık x Şiddet"""
    return o * s

def l_matris_seviye(skor):
    """L Matris risk seviyesi"""
    if skor <= 2:
        return "🟢 Önemsiz Risk", "Önlem gerekli değil"
    elif skor <= 6:
        return "🟡 Düşük Risk", "Mevcut önlemler korunmalı"
    elif skor <= 12:
        return "🟠 Orta Risk", "Risk azaltılmalı"
    elif skor <= 19:
        return "🔴 Yüksek Risk", "Acil önlem alınmalı"
    else:
        return "⚫ Tolere Edilemez Risk", "Çalışma durdurulmalı"

# Ana Uygulama
uploaded_file = st.file_uploader(
    "📸 İş alanı fotoğrafı yükleyin",
    type=["jpg", "jpeg", "png"],
    help="JPG, JPEG veya PNG formatında fotoğraf yükleyin"
)

if uploaded_file is not None:
    # Resmi göster
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📷 Yüklenen Fotoğraf")
        image = Image.open(uploaded_file)
        st.image(image, use_column_width=True)
    
    if not api_key:
        st.warning("⚠️ Lütfen sol taraftaki menüden Roboflow API Key girin!")
    else:
        if st.button("🔍 Analiz Et", type="primary", use_container_width=True):
            with st.spinner("🤖 Yapay zeka modeli analiz yapıyor..."):
                try:
                    # Geçici dosya oluştur
                    temp_path = "temp_image.jpg"
                    image.save(temp_path)
                    
                    # Roboflow API'ye gönder
                    client = InferenceHTTPClient(
                        api_url="https://serverless.roboflow.com",
                        api_key=api_key
                    )
                    
                    result = client.run_workflow(
                        workspace_name="hseyins-workspace-vh1ss",
                        workflow_id="detect-count-and-visualize",
                        images={"image": temp_path},
                        use_cache=True
                    )
                    
                    # Sonuçları işle
                    with col2:
                        st.subheader("🎯 Tespit Sonucu")
                        
                        # İşaretlenmiş görsel
                        if result and len(result) > 0:
                            output = result[0]
                            
                            # Görsel çıktıyı göster
                            if "label_visualization" in output or "annotated_image" in output:
                                annotated = output.get("label_visualization") or output.get("annotated_image")
                                if isinstance(annotated, dict) and "value" in annotated:
                                    img_data = base64.b64decode(annotated["value"])
                                    st.image(img_data, use_column_width=True)
                                elif isinstance(annotated, str):
                                    img_data = base64.b64decode(annotated)
                                    st.image(img_data, use_column_width=True)
                    
                    # Tespit edilen nesneler
                    st.markdown("---")
                    st.subheader("📋 Risk Değerlendirme Raporu")
                    
                    predictions = []
                    if result and len(result) > 0:
                        output = result[0]
                        # Predictions farklı yerlerde olabilir
                        if "predictions" in output:
                            preds = output["predictions"]
                            if isinstance(preds, dict) and "predictions" in preds:
                                predictions = preds["predictions"]
                            elif isinstance(preds, list):
                                predictions = preds
                    
                    if not predictions:
                        st.info("ℹ️ Fotoğrafta herhangi bir nesne tespit edilemedi.")
                    else:
                        st.success(f"✅ Toplam {len(predictions)} nesne tespit edildi")
                        
                        # Her tespit için risk değerlendirmesi
                        risk_listesi = []
                        for idx, pred in enumerate(predictions, 1):
                            sinif = pred.get("class", "bilinmeyen").lower()
                            guven = pred.get("confidence", 0) * 100
                            
                            risk_data = TEHLIKE_RISK_TABLOSU.get(sinif, {
                                **VARSAYILAN_RISK,
                                "tehlike": f"Tespit: {sinif}"
                            })
                            
                            satir = {
                                "No": idx,
                                "Tespit": sinif,
                                "Güven (%)": f"{guven:.1f}",
                                "Tehlike": risk_data["tehlike"],
                                "Sonuç": risk_data["sonuc"],
                                "Önlem": risk_data["onlem"]
                            }
                            
                            # Fine-Kinney
                            if risk_method in ["Fine-Kinney", "Her İkisi"]:
                                fk_skor = fine_kinney_skor(
                                    risk_data["fk_olasilik"],
                                    risk_data["fk_frekans"],
                                    risk_data["fk_siddet"]
                                )
                                fk_seviye, fk_aciklama = fine_kinney_seviye(fk_skor)
                                satir["FK Skor"] = fk_skor
                                satir["FK Seviye"] = fk_seviye
                            
                            # L Matris
                            if risk_method in ["L Matris (5x5)", "Her İkisi"]:
                                lm_skor = l_matris_skor(
                                    risk_data["lm_olasilik"],
                                    risk_data["lm_siddet"]
                                )
                                lm_seviye, lm_aciklama = l_matris_seviye(lm_skor)
                                satir["LM Skor"] = lm_skor
                                satir["LM Seviye"] = lm_seviye
                            
                            risk_listesi.append(satir)
                        
                        # Tablo göster
                        df = pd.DataFrame(risk_listesi)
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        
                        # CSV indir
                        csv = df.to_csv(index=False).encode("utf-8-sig")
                        st.download_button(
                            label="📥 Raporu CSV Olarak İndir",
                            data=csv,
                            file_name="risk_raporu.csv",
                            mime="text/csv"
                        )
                        
                        # Özet
                        st.markdown("---")
                        st.subheader("📊 Genel Değerlendirme")
                        
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Toplam Tespit", len(predictions))
                        with col_b:
                            riskli = sum(1 for p in predictions if p.get("class", "").lower().startswith("no-"))
                            st.metric("Riskli Durum", riskli)
                        with col_c:
                            uyumlu = len(predictions) - riskli
                            st.metric("Uyumlu Durum", uyumlu)
                
                except Exception as e:
                    st.error(f"❌ Hata oluştu: {str(e)}")
                    st.info("💡 İpucu: API Key'inizi ve internet bağlantınızı kontrol edin.")

else:
    st.info("👆 Başlamak için yukarıdan bir fotoğraf yükleyin")

# Footer
st.markdown("---")
st.caption("🦺 İş Güvenliği Risk Değerlendirme Sistemi v1.0 | Roboflow AI ile güçlendirilmiştir")
# === SON ===
