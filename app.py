import streamlit as st
import requests
import base64
from PIL import Image
import pandas as pd
import io
import json

# Sayfa ayarları
st.set_page_config(
    page_title="İş Güvenliği Risk Değerlendirme",
    page_icon="🦺",
    layout="wide"
)

# Başlık
st.title("🦺 İş Güvenliği Risk Değerlendirme Sistemi")
st.markdown("Fotoğraf yükleyerek iş güvenliği eksikliklerini tespit edin ve risk değerlendirmesi yapın.")

# Sidebar
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

# Tehlike-Risk Tablosu
TEHLIKE_RISK_TABLOSU = {
    "no-helmet": {
        "tehlike": "Baret/Kask Takmama",
        "sonuc": "Kafa travması, beyin hasarı, ölüm",
        "fk_olasilik": 6, "fk_frekans": 6, "fk_siddet": 15,
        "lm_olasilik": 4, "lm_siddet": 5,
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

VARSAYILAN_RISK = {
    "tehlike": "Tespit Edilen Durum",
    "sonuc": "Detaylı değerlendirme gerekli",
    "fk_olasilik": 3, "fk_frekans": 3, "fk_siddet": 7,
    "lm_olasilik": 3, "lm_siddet": 3,
    "onlem": "Uzman değerlendirmesi gerekli"
}

def fine_kinney_skor(o, f, s):
    return o * f * s

def fine_kinney_seviye(skor):
    if skor < 20:
        return "🟢 Önemsiz Risk", "Acil önlem gerekmez"
    elif skor < 70:
        return "🟡 Olası Risk", "Dikkat altında tutulmalı"
    elif skor < 200:
        return "🟠 Önemli Risk", "Yıl içinde önlem alınmalı"
    elif skor < 400:
        return "🔴 Esaslı Risk", "Kısa sürede önlem alınmalı"
    else:
        return "⚫ Kabul Edilemez Risk", "ACİL önlem alınmalı"

def l_matris_skor(o, s):
    return o * s

def l_matris_seviye(skor):
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

def roboflow_workflow_calistir(api_key, image_bytes):
    """Roboflow Workflow API'sine direkt HTTP isteği gönderir"""
    url = "https://serverless.roboflow.com/infer/workflows/hseyins-workspace-vh1ss/detect-count-and-visualize"
    
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    
    payload = {
        "api_key": api_key,
        "inputs": {
            "image": {"type": "base64", "value": image_base64}
        }
    }
    
    response = requests.post(url, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()

# Ana Uygulama
uploaded_file = st.file_uploader(
    "📸 İş alanı fotoğrafı yükleyin",
    type=["jpg", "jpeg", "png"],
    help="JPG, JPEG veya PNG formatında fotoğraf yükleyin"
)

if uploaded_file is not None:
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
                    # Resmi byte olarak hazırla
                    image_rgb = image.convert("RGB")
                    buf = io.BytesIO()
                    image_rgb.save(buf, format="JPEG")
                    image_bytes = buf.getvalue()
                    
                    # Roboflow'a gönder
                    result = roboflow_workflow_calistir(api_key, image_bytes)
                    
                    # Sonucu işle
                    with col2:
                        st.subheader("🎯 Tespit Sonucu")
                        
                        outputs = result.get("outputs", [])
                        if outputs and len(outputs) > 0:
                            output = outputs[0]
                            
                            # İşaretlenmiş görseli göster
                            for key in ["annotated_image", "label_visualization", "detection_visualization"]:
                                if key in output:
                                    img_obj = output[key]
                                    if isinstance(img_obj, dict) and "value" in img_obj:
                                        try:
                                            img_data = base64.b64decode(img_obj["value"])
                                            st.image(img_data, use_column_width=True)
                                            break
                                        except:
                                            pass
                    
                    # Tespit listesi
                    st.markdown("---")
                    st.subheader("📋 Risk Değerlendirme Raporu")
                    
                    predictions = []
                    if outputs and len(outputs) > 0:
                        output = outputs[0]
                        # Predictions farklı yerlerde olabilir
                        for key in ["predictions", "model_predictions"]:
                            if key in output:
                                preds = output[key]
                                if isinstance(preds, dict) and "predictions" in preds:
                                    predictions = preds["predictions"]
                                    break
                                elif isinstance(preds, list):
                                    predictions = preds
                                    break
                    
                    if not predictions:
                        st.info("ℹ️ Fotoğrafta herhangi bir nesne tespit edilemedi.")
                        with st.expander("🔍 Ham Sonuç (Debug)"):
                            st.json(result)
                    else:
                        st.success(f"✅ Toplam {len(predictions)} nesne tespit edildi")
                        
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
                            
                            if risk_method in ["Fine-Kinney", "Her İkisi"]:
                                fk_skor = fine_kinney_skor(
                                    risk_data["fk_olasilik"],
                                    risk_data["fk_frekans"],
                                    risk_data["fk_siddet"]
                                )
                                fk_seviye, _ = fine_kinney_seviye(fk_skor)
                                satir["FK Skor"] = fk_skor
                                satir["FK Seviye"] = fk_seviye
                            
                            if risk_method in ["L Matris (5x5)", "Her İkisi"]:
                                lm_skor = l_matris_skor(
                                    risk_data["lm_olasilik"],
                                    risk_data["lm_siddet"]
                                )
                                lm_seviye, _ = l_matris_seviye(lm_skor)
                                satir["LM Skor"] = lm_skor
                                satir["LM Seviye"] = lm_seviye
                            
                            risk_listesi.append(satir)
                        
                        df = pd.DataFrame(risk_listesi)
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        
                        csv = df.to_csv(index=False).encode("utf-8-sig")
                        st.download_button(
                            label="📥 Raporu CSV Olarak İndir",
                            data=csv,
                            file_name="risk_raporu.csv",
                            mime="text/csv"
                        )
                        
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
                
                except requests.exceptions.HTTPError as e:
                    st.error(f"❌ API Hatası: {e.response.status_code}")
                    st.code(e.response.text)
                except Exception as e:
                    st.error(f"❌ Hata oluştu: {str(e)}")
                    st.info("💡 İpucu: API Key'inizi ve internet bağlantınızı kontrol edin.")

else:
    st.info("👆 Başlamak için yukarıdan bir fotoğraf yükleyin")

st.markdown("---")
st.caption("🦺 İş Güvenliği Risk Değerlendirme Sistemi v1.0 | Roboflow AI ile güçlendirilmiştir")
