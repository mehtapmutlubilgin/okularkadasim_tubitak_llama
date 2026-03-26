import streamlit as st
from groq import Groq
import os

# Sayfa Yapılandırması
st.set_page_config(page_title="OkulArkadaşım - AI Asistan", page_icon="🎓")

# 1. API Anahtarı ve Başlık
# Yerel çalışırken os.environ veya streamlit secrets kullanabilirsin
api_key = st.sidebar.text_input("Groq API Key", type="password")
client = Groq(api_key=api_key) if api_key else None

st.title("🎓 OkulArkadaşım")
st.subheader("MEB Yönetmelik Akıllı Bilgi Asistanı")
st.info("Lütfen sorunuzu aşağıya yazın. Cevaplar doğrudan resmi yönetmeliğe dayandırılır.")

# 2. Asistan Fonksiyonu
def okul_asistani_sorgula(soru, vector_db):
    if not client:
        return "Lütfen sol menüden geçerli bir API anahtarı girin."
    
    # Benzerlik araması (vector_db'nin yüklü olduğunu varsayıyoruz)
    docs = vector_db.similarity_search(soru, k=5)
    baglam = "\n\n".join([doc.page_content for doc in docs])

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "Sen MEB Ortaöğretim Kurumları Yönetmeliği uzmanısın. Sadece bağlama dayalı, resmi ve maddeler halinde cevap ver."},
            {"role": "user", "content": f"Bağlam:\n{baglam}\n\nSoru: {soru}"}
        ],
        model="llama-3.1-8b-instant",
        temperature=0
    )
    return chat_completion.choices[0].message.content

# 3. Kullanıcı Arayüzü (Chat Geçmişi)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mesajları ekranda göster
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcıdan girdi al
if prompt := st.chat_input("Sorumluluk sınavına kimler girebilir?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Asistan cevabı üret
    with st.chat_message("assistant"):
        # Not: vector_db'yi burada global veya session_state üzerinden çağırmalısın
        with st.spinner("Yönetmelik taranıyor..."):
            # ÖNEMLİ: vector_db nesnenin burada erişilebilir olduğundan emin ol
            try:
                cevap = okul_asistani_sorgula(prompt, st.session_state.vector_db)
                st.markdown(cevap)
                st.session_state.messages.append({"role": "assistant", "content": cevap})
            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")
