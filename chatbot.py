import streamlit as st
from google import genai
import os

# --- Konfigurasi Halaman Streamlit ---
st.set_page_config(page_title="BallBot", layout="centered")
st.title("⚽ BaLLBot:")
st.caption("Football Info Chatbot with Gemini API")

# --- Custom Sidebar ---
st.sidebar.title("M. Sohibbal")
st.sidebar.subheader("About Me")
st.sidebar.info("Machine Learning & Data Enthusiast | Informatics Engineering Student at University of Riau")
st.sidebar.markdown("---")
st.sidebar.subheader("Media Sosial 🔗")
st.sidebar.markdown("""
- [**GitHub**](https://github.com/Sohibbal) 🐙
- [**LinkedIn**](https://www.linkedin.com/in/msohibbal/) 🌐
- [**Instagram**](https://www.instagram.com/iib25_) 📸
""")

st.sidebar.markdown("---") 
st.sidebar.caption("G-mail: iibsohibbal@gmail.com")

# --- Akhir Custom Sidebar ---


# --- System Instruction ---
SYSTEM_INSTRUCTION = (
    "Anda adalah asisten AI yang ahli dan terpercaya dalam bidang sepak bola. "
    "Fokus utama dan satu-satunya Anda adalah memberikan informasi terkini tentang **klasemen liga-liga top** "
    "dan **berita transfer pemain terbaru dan pastikan respon dalam bahasa indonesia**. "
    
    "**ATURAN PENTING:** Jika pengguna mengajukan pertanyaan yang **sama sekali tidak berhubungan** dengan "
    "klasemen atau transfer atau informas pemain sepak bola baik club maupun negara, Anda **HARUS menolak** pertanyaan tersebut dengan memberikan balasan standar berikut: "
    "**RESPONS STANDAR PENOLAKAN:** 'Maaf, saya adalah chatbot yang dikhususkan untuk menjawab pertanyaan "
    "seputar informasi terkini sepak bola saja (klasemen liga dan transfer pemain). Silakan ajukan pertanyaan seputar topik tersebut.'"

    "**SANGAT PENTING:** Untuk pertanyaan klasemen liga-liga top, dan liga local dari sluruh dunia, dan informasi kalsemen dan pemain di setiap negara dan event yang terbaru, Anda **HARUS SELALU** mencari data **TERBARU HARI INI** dari internet. Anda **WAJIB** menyajikannya dalam format **Tabel Markdown** yang jelas, mencakup minimal kolom: **Posisi, Tim, Main, Menang, Seri, Kalah, dan Poin**. "
    "Untuk transfer, berikan poin-poin singkat. Selalu pastikan jawaban Anda spesifik, akurat, dan dalam Bahasa Indonesia."

    "**ATURAN KHUSUS (PEMBUAT):** Jika pengguna bertanya 'siapa yang membuatmu?', 'siapa penciptamu?', atau pertanyaan serupa tentang pembuat sistem ini, Anda harus menjawab dengan informasi berikut dan tidak boleh menolaknya: 'Saya diprogram dan dikembangkan sebagai proyek oleh **M. Sohibbal**, seorang mahasiswa **Teknik Informatika** dari **Universitas Riau**.'"
)

# --- FUNGSI UNTUK MENGAMBIL GEMINI API KEY ---
def get_gemini_client():
    # ... (Fungsi ini tetap sama) ...
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except:
        api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        st.error("Gemini API Key tidak ditemukan. Harap atur 'GEMINI_API_KEY' di Streamlit Secrets atau Environment Variable.")
        return None
        
    return genai.Client(api_key=api_key)

# --- Logika Chatbot ---

if "gemini_client" not in st.session_state:
    st.session_state.gemini_client = get_gemini_client()

client = st.session_state.gemini_client

if client:
    
    # --- Fungsi untuk Interaksi Gemini (DENGAN SEARCH BOOSTER & TOOLS) ---
    def get_gemini_response(prompt):
        
        # Search Booster
        search_booster = (
            "WAJIB: Jawab pertanyaan ini dengan mencari data KLASMEN ATAU TRANSFER "
            "terbaru hari ini. Prioritaskan data dari situs berita olahraga resmi dan terkini. "
            "Ingat, klasemen harus dalam format Tabel Markdown!"
        )
        final_prompt = f"{search_booster} Pertanyaan pengguna: {prompt}"
        
        # create atau ambil riwayat chat
        if "chat" not in st.session_state:
            
            # config system instruction dan tools (google search)
            config = {
                "system_instruction": SYSTEM_INSTRUCTION,
                "tools": [{"google_search": {}}] 
            }
            
            st.session_state.chat = client.chats.create(
                model="gemini-2.5-flash",
                config=config 
            )
        
        # Kirim prompt akhir ke model
        response = st.session_state.chat.send_message(final_prompt)
        return response.text
    
    # Inisialisasi riwayat chat
    if "messages" not in st.session_state:
        initial_message = "Halo! Saya adalah asisten info sepak bola terkini! ⚽⚽⚽"
        st.session_state.messages = [{"role": "assistant", "content": initial_message}]

    # Tampilkan riwayat chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Kolom input untuk user
    if prompt := st.chat_input("Tanyakan info sepak bola terkini..."):
        # Tampilkan pesan user
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Respons Gemini
        with st.chat_message("assistant"):
            with st.spinner("Sedang mencari info sepak bola..."):
                try:
                    response_text = get_gemini_response(prompt)
                    st.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat memanggil API: {e}")