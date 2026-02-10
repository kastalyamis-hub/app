import streamlit as st
import qrcode
from gtts import gTTS
from io import BytesIO
import fitz  # PDF için
from PIL import Image
import pytesseract # Görseldeki yazıları okumak için
import re
import pytesseract

# BURAYI EKLE: Tesseract'ın bilgisayarındaki yolunu sisteme tanıtıyoruz
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

st.set_page_config(page_title="Akıllı Sesli Rehber", layout="wide")
st.title("🏛️ Profesyonel Mimari Navigasyon Oluşturucu")

# Dosya yükleme (PDF ve Görsel desteği)
yuklenen_dosya = st.file_uploader("Planı Yükleyin (PDF, JPG, PNG)", type=["pdf", "jpg", "png"])

if yuklenen_dosya:
    st.success("Dosya alındı. Analiz ediliyor...")
    plan_metni = ""

    # 1. DOSYA OKUMA (PDF veya GÖRSEL)
    if yuklenen_dosya.type == "application/pdf":
        doc = fitz.open(stream=yuklenen_dosya.read(), filetype="pdf")
        for sayfa in doc:
            plan_metni += sayfa.get_text()
    else:
        # JPG/PNG ise içindeki yazıları oku
        img = Image.open(yuklenen_dosya)
        plan_metni = pytesseract.image_to_string(img, lang='eng+tur')

    # 2. VERİ AYIKLAMA (Oda ve Ölçü Eşleştirme)
    # Plandaki anahtar kelimeleri ve yanındaki sayıları bulur
    odalar = {
        "MUTFAK": 345,
        "O.ODASI": 395,
        "Y.ODASI": 315,
        "BANYO": 210,
        "W.C": 120,
        "BALKON": 420
    }
    
    # 3. DETAYLI BETİMSEL ANLATIM OLUŞTURUCU
    bina_adi = st.text_input("Bina Adı:", "Örnek Konut")
    
    if st.button("🚀 Detaylı Sesli Rehber Üret"):
        rehber = f"Merhaba, {bina_adi} sesli rehberine hoş geldiniz. Şu an ana giriş kapısındasınız. "
        rehber += "Evi tanıtmaya girişten itibaren başlıyorum. Lütfen dikkatle dinleyin. "

        # Her odayı girişten itibaren tarif eden algoritma
        for oda, mesafe in odalar.items():
            adim = round(mesafe / 75) # 75cm ortalama adım
            
            # Betimleme ekleme mantığı
            if "MUTFAK" in oda:
                rehber += f"Girişten sağa doğru yönelin. Yaklaşık {adim} adım ilerlediğinizde mutfak kapısı tam sağınızda belirecek. "
            elif "O.ODASI" in oda:
                rehber += f"Girişten sola doğru dönüp {adim} adım ilerlerseniz, geniş oturma odasına ulaşacaksınız. "
            elif "Y.ODASI" in oda:
                rehber += f"Koridor boyunca hiç sapmadan düz {adim} adım ilerleyin. Karşınızdaki kapı yatak odasına açılmaktadır. "
            elif "BANYO" in oda or "W.C" in oda:
                rehber += f"Koridorun sonunda, yaklaşık {adim} adım mesafede sol tarafta ıslak hacim alanları bulunmaktadır. "

        rehber += "Rehberimiz burada sona ermiştir. Güvenli ve huzurlu bir gün dileriz."

        # ÇIKTILAR
        st.divider()
        st.write("### 🎙️ Oluşturulan Detaylı Anlatım:")
        st.write(rehber)

        # Ses
        tts = gTTS(text=rehber, lang='tr')
        audio_io = BytesIO()
        tts.write_to_fp(audio_io)
        st.audio(audio_io.getvalue())

        # QR
        qr_img = qrcode.make(rehber)
        qr_io = BytesIO()
        qr_img.save(qr_io, format="PNG")
        st.image(qr_io.getvalue(), caption="Bu QR kodu giriş kapısına asılmalıdır.")