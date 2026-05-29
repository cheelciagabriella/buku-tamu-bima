import streamlit as st
from datetime import datetime, timezone, timedelta
import pandas as pd
import streamlit.components.v1 as components
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="E-Buku Tamu Stamet Bima", 
    layout="wide"
)

# ==========================================
# 2. KUSTOMISASI DESAIN WARNA (TEMA PUSAT KOMANDO - DARK MODE)
# ==========================================
st.markdown("""
    <style>
    /* 1. Menghilangkan Header Bawaan Streamlit (Tombol Deploy dan Menu Kanan Atas) */
    [data-testid="stHeader"] {
        display: none !important;
    }
    
    /* 2. Menghilangkan Footer Bawaan Streamlit (Made with Streamlit) */
    footer {
        visibility: hidden !important;
    }
    
    /* 3. Mengubah Latar Belakang Halaman Utama menjadi Biru Gelap Komando */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #020617 0%, #0f172a 100%) !important;
    }
    
    /* 4. Mengubah Latar Belakang Menu Samping (Sidebar) menjadi Biru Tua Pekat */
    [data-testid="stSidebar"] {
        background-color: #001529 !important;
    }
    
    /* 5. Memastikan semua teks di Sidebar tetap Putih Bersih */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span, [data-testid="stSidebar"] div {
        color: #ffffff !important;
    }
    
    /* 6. Mengatur kontainer formulir menjadi Biru Donker BMKG yang solid dan kontras */
    [data-testid="stForm"], .stElementContainer div[data-aria-stable="true"] {
        background-color: #002B49 !important;
        border: 1px solid #004080;
        border-radius: 10px;
        padding: 20px;
    }

    /* 7. KUNCI MUTLAK: Memaksa semua elemen teks di halaman utama berwarna Putih/Terang */
    section.main h1, section.main h2, section.main h3, section.main h4, section.main h5, section.main h6,
    section.main label, section.main p, section.main span,
    section.main div[data-testid="stMarkdownContainer"] p,
    section.main div[data-testid="stWidgetLabel"] p {
        color: #ffffff !important;
    }
    
    /* Memastikan teks penjelasan atau caption berwarna abu-abu terang agar terbaca */
    section.main .stCaptionContainer, section.main div[data-testid="stCaptionContainer"] p {
        color: #cbd5e1 !important;
    }
    
    /* Kolom inputan tetap dibikin putih bersih di dalamnya dengan tulisan hitam agar kontras saat diketik */
    section.main input {
        background-color: #ffffff !important;
        color: #111111 !important;
    }
    
    /* Mengubah warna teks tab menu agar tetap terlihat jelas */
    button[data-baseweb="tab"] p {
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. FUNGSI INTEGRASI GOOGLE SHEETS (CLOUD)
# ==========================================
def simpan_ke_google_sheets(nama_tab, data_list):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        if "gspread" in st.secrets:
            credentials_info = dict(st.secrets["gspread"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_info, scope)
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name("kredensial.json", scope)
            
        client = gspread.authorize(creds)
        sheet = client.open("Buku Tamu Stamet Bima").worksheet(nama_tab)
        sheet.append_row(data_list)
        return True
    except Exception as e:
        st.error(f"Sistem gagal terhubung ke Cloud Database: {e}")
        return False

# ==========================================
# 4. INISIALISASI KONTROL ALUR (SESSION STATE)
# ==========================================
if "tamu_terdaftar" not in st.session_state:
    st.session_state.tamu_terdaftar = False
if "nama_pendaftar" not in st.session_state:
    st.session_state.nama_pendaftar = ""
if "ikm_selesai" not in st.session_state:
    st.session_state.ikm_selesai = False

# ==========================================
# 5. NAVIGASI SAMPING (SIDEBAR)
# ==========================================
try:
    st.sidebar.image("logo.png", width=90) 
except:
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/4/44/Logo_BMKG.png", width=90)

st.sidebar.title("NAVIGASI SISTEM")
menu = st.sidebar.radio("PILIH MENU LAYANAN:", ["FORMULIR KUNJUNGAN PUBLIK", "SURVEI KEPUASAN (IKM)"])
st.sidebar.divider()
st.sidebar.caption("SISTEM ADMINISTRASI TERPADU")
st.sidebar.caption("STASIUN METEOROLOGI KELAS III SULTAN MUHAMMAD SALAHUDDIN BIMA")

# ==========================================
# 6. HALAMAN 1: FORMULIR KUNJUNGAN PUBLIK
# ==========================================
if menu == "FORMULIR KUNJUNGAN PUBLIK":
    
    col_logo, col_text, col_clock = st.columns([1.2, 5.5, 2.3])
    with col_logo:
        try:
            st.image("logo.png", width=120)
        except:
            st.image("https://upload.wikimedia.org/wikipedia/commons/4/44/Logo_BMKG.png", width=120)
            
    with col_text:
        # Teks Judul disesuaikan warnanya agar menyala terang di atas background gelap
        st.markdown("""
            <div style='text-align: center; padding-top: 5px; line-height: 1.2;'>
                <div style='color: #38bdf8; font-size: 30px; font-weight: 900; letter-spacing: 1px; margin-bottom: 2px;'>
                    PORTAL LAYANAN PUBLIK TERINTEGRASI
                </div>
                <div style='color: #4ade80; font-size: 18px; font-weight: 800; letter-spacing: 0.5px; margin-bottom: 2px;'>
                    STASIUN METEOROLOGI KELAS III SULTAN MUHAMMAD SALAHUDDIN BIMA
                </div>
                <div style='color: #e2e8f0; font-size: 14px; font-weight: 700; letter-spacing: 1px; margin-top: 0px;'>
                    BADAN METEOROLOGI, KLIMATOLOGI, DAN GEOFISIKA
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with col_clock:
        # Jam digital kustom warna putih kekuningan agar kontras tinggi
        components.html("""
            <div id="clock" style="font-family: 'Arial', sans-serif; font-size: 14px; font-weight: bold; color: #facc15; text-align: right; padding-top: 25px;"></div>
            <script>
                function updateTime() {
                    const now = new Date();
                    const options = { timeZone: 'Asia/Makassar', weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
                    const timeString = new Intl.DateTimeFormat('id-ID', options).format(now);
                    document.getElementById('clock').innerHTML = timeString.replace(/\\./g, ':') + ' WITA';
                    setTimeout(updateTime, 1000);
                }
                updateTime();
            </script>
        """, height=80)
    
    st.divider()
    
    tab1, tab2 = st.tabs(["E-BUKU TAMU DIGITAL", "E-KATALOG PNBP"])
    
    with tab1:
        if not st.session_state.tamu_terdaftar:
            st.subheader("FORMULIR REGISTRASI PENGUNJUNG")
            st.caption("Mohon lengkapi data registrasi di bawah ini untuk kepentingan administrasi pelayanan publik.")
            
            with st.container(border=True):
                st.markdown("#### **I. IDENTITAS PEMOHON**")
                col1, col2 = st.columns(2)
                with col1:
                    nama = st.text_input("NAMA LENGKAP (SESUAI KTP/IDENTITAS RESMI)", placeholder="Contoh: Nama Beserta Gelar")
                    identitas = st.text_input("NOMOR IDENTITAS (NIK / NIM / NIP)", placeholder="Masukkan Nomor Identitas")
                with col2:
                    no_hp = st.text_input("NOMOR TELEPON / WHATSAPP AKTIF", placeholder="Contoh: 0812345678xx")
                    instansi = st.text_input("ASAL INSTANSI / PERUSAHAAN / UNIVERSITAS", placeholder="Contoh: Pemerintah Kota Bima")
            
            st.write("")
            
            with st.container(border=True):
                st.markdown("#### **II. MAKSUD KUNJUNGAN**")
                col3, col4 = st.columns(2)
                with col3:
                    tujuan = st.selectbox(
                        "LAYANAN YANG DITUJU", 
                        ["Permintaan Data Cuaca/Iklim", "Konsultasi Teknis Meteorologi", "Kunjungan Kerja / Koordinasi", "Studi Banding / Edukasi Publik", "Lain-lain"]
                    )
                with col4:
                    alasan_lainnya = ""
                    if tujuan == "Lain-lain":
                        alasan_lainnya = st.text_input("URAIKAN MAKSUD KUNJUNGAN SECARA SPESIFIK:", placeholder="Tuliskan Keperluan Anda")

            st.write("") 
            
            submit_button = st.button("SIMPAN DATA KUNJUNGAN", type="primary", use_container_width=True)
            
            if submit_button:
                if not nama or not identitas or not instansi:
                    st.error("GAGAL: Mohon lengkapi kolom Nama, Nomor Identitas, dan Asal Instansi.")
                elif tujuan == "Lain-lain" and not alasan_lainnya:
                    st.warning("PERHATIAN: Mohon uraikan maksud kunjungan secara spesifik pada kolom yang tersedia.")
                else:
                    tujuan_final = alasan_lainnya if tujuan == "Lain-lain" else tujuan
                    waktu_sekarang = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
                    
                    row_tamu = [waktu_sekarang, nama, identitas, no_hp, instansi, tujuan_final, "Pelayanan Terdaftar"]
                    
                    if simpan_ke_google_sheets("Tamu", row_tamu):
                        st.session_state.tamu_terdaftar = True
                        st.session_state.nama_pendaftar = nama
                        st.rerun()

        elif st.session_state.tamu_terdaftar and not st.session_state.ikm_selesai:
            st.success(f"DATA BERHASIL TERSIMPAN: Terima kasih Bapak/Ibu {st.session_state.nama_pendaftar}, data kunjungan Anda telah sah tercatat.")
            st.balloons()
            
            st.divider()
            st.subheader("SURVEI INDEKS KEPUASAN MASYARAKAT (IKM)")
            st.info("Mohon perkenan waktu Anda sejenak untuk langsung mengisi evaluasi layanan di bawah ini guna peningkatan kualitas pelayanan kami.")
            
            with st.form("form_ikm_otomatis"):
                st.markdown("#### **FORMULIR EVALUASI KUALITAS LAYANAN**")
                st.markdown(f"Nama Responden: **{st.session_state.nama_pendaftar}**")
                
                st.write("")
                st.markdown("**PETUNJUK:** Berikan penilaian skala 1 (Sangat Buruk) hingga 5 (Sangat Baik) pada pernyataan berikut.")
                
                layanan = st.slider("1. Kemudahan prosedur dan persyaratan layanan di stasiun kami?", 1, 5, 5)
                sikap = st.slider("2. Keramahan dan kecepatan petugas pelayanan?", 1, 5, 5)
                fasilitas = st.slider("3. Pemanfaatan inovasi E-Buku Tamu & E-Katalog ini?", 1, 5, 5)
                
                st.write("")
                saran = st.text_area("KRITIK DAN SARAN KONSTRUKTIF:")
                
                submit_ikm_otomatis = st.form_submit_button("KIRIM PENILAIAN IKM", type="primary", use_container_width=True)
                
                if submit_ikm_otomatis:
                    waktu_survei = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
                    row_survei = [waktu_survei, st.session_state.nama_pendaftar, layanan, sikap, fasilitas, saran]
                    
                    if simpan_ke_google_sheets("Survei", row_survei):
                        st.session_state.ikm_selesai = True
                        st.rerun()

        else:
            st.success("PROSES SELESAI: Terima kasih atas partisipasi Anda dalam mengisi Buku Tamu dan Survei IKM Stasiun Meteorologi Bima.")
            st.info("Kontribusi penilaian Anda sangat berharga bagi peningkatan mutu dan akuntabilitas pelayanan publik kami.")
            
            st.write("")
            if st.button("KEMBALI KE HALAMAN UTAMA (REGISTRASI TAMU BARU)", type="primary", use_container_width=True):
                st.session_state.tamu_terdaftar = False
                st.session_state.nama_pendaftar = ""
                st.session_state.ikm_selesai = False
                st.rerun()

    with tab2:
        st.subheader("KATALOG INFORMASI TARIF PNBP")
        st.info("Dasar Hukum: Peraturan Pemerintah Republik Indonesia Nomor 47 Tahun 2018.")
        st.write("(Salinan infografis katalog pelayanan publik akan ditampilkan pada bagian ini)")

elif menu == "SURVEI KEPUASAN (IKM)":
    
    st.title("SURVEI INDEKS KEPUASAN MASYARAKAT (IKM)")
    st.write("Penilaian Anda sangat berharga untuk meningkatkan kualitas pelayanan publik di Stasiun Meteorologi Bima.")
    st.divider()
    
    with st.form("form_survei_mandiri"):
        st.markdown("#### **FORMULIR EVALUASI KUALITAS LAYANAN**")
        nama_survei = st.text_input("NAMA LENGKAP (OPSIONAL):", placeholder="Boleh Dikosongkan (Anonim)")
        
        st.write("")
        st.markdown("**PETUNJUK:** Berikan penilaian skala 1 (Sangat Buruk) hingga 5 (Sangat Baik) pada pernyataan berikut.")
        
        layanan = st.slider("1. Kemudahan prosedur dan persyaratan layanan di stasiun kami?", 1, 5, 5)
        sikap = st.slider("2. Keramahan dan kecepatan petugas pelayanan?", 1, 5, 5)
        fasilitas = st.slider("3. Pemanfaatan inovasi E-Buku Tamu & E-Katalog ini?", 1, 5, 5)
        
        st.write("")
        saran = st.text_area("KRITIK DAN SARAN KONSTRUKTIF:")
        
        submit_survei = st.form_submit_button("KIRIM PENILAIAN", type="primary", use_container_width=True)
        
        if submit_survei:
            waktu_survei = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
            identitas_survei = nama_survei if nama_survei else "Anonim"
            
            row_survei = [waktu_survei, identitas_survei, layanan, sikap, fasilitas, saran]
            
            if simpan_ke_google_sheets("Survei", row_survei):
                st.success("TERIMA KASIH: Penilaian Anda telah kami terima untuk bahan evaluasi pelayanan.")