import streamlit as st

def renderSidebar():
    st.sidebar.header("Ayarlar")
    
    apiKey = st.sidebar.text_input("Groq API Anahtarı", type="password")
    
    uploadedFiles = st.sidebar.file_uploader(
        "Dosya Yükleme", 
        accept_multiple_files=True,
        type=["txt", "pdf", "doc", "docx"]
    )
    
    return apiKey, uploadedFiles

def fetchLlmResponse(message, apiKey, uploadedFiles):
    # Backend işlemleri ileride buradan yapılacak. Şimdilik sadece gelen mesajı ve dosya sayısını döndürüyoruz.
    if not apiKey:
        return "Lütfen sol menüden Groq API anahtarınızı girin."
        
    fileCount = len(uploadedFiles or [])
    return f"Backend simülasyon yanıtı. Gelen mesaj: '{message}', {fileCount} adet dosya işlenmek üzere gönderilebilir."

def renderChatArea(apiKey, uploadedFiles):
    st.title("Sohbet")
    
    # Sohbet akışını ekranda tutmak için session_state kullanıyoruz
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Önceki mesajlar
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])
    
    userMessage = st.chat_input("LLM'e sorunuzu iletin...")
    
    if userMessage:
         # Kullanıcı mesajını ekle ve göster
         st.session_state.messages.append({"role": "user", "content": userMessage})
         st.chat_message("user").write(userMessage)
         
         with st.spinner("Yanıt oluşturuluyor..."):
             llmResponse = fetchLlmResponse(userMessage, apiKey, uploadedFiles)
             
         # Gelen cevabı ekle ve göster
         st.session_state.messages.append({"role": "assistant", "content": llmResponse})
         st.chat_message("assistant").write(llmResponse)

def main():
    st.set_page_config(page_title="DocTalk", page_icon="📃")
    
    apiKey, uploadedFiles = renderSidebar()
    renderChatArea(apiKey, uploadedFiles)

if __name__ == "__main__":
    main()
