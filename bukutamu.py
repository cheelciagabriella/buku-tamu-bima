import streamlit as st
from datetime import datetime
import pandas as pd
import streamlit.components.v1 as components
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ==========================================
# 1. KONFIGURASI HALAMAN 
# ==========================================
st.set_page_config(
    page_title="E-Buku Tamu Stamet Bima", 
    page_icon="🌤️", 
    layout="wide"
)

# ==========================================
# 2. KUSTOMISASI DESAIN WARNA (TEMA FORMAL BMKG)
# ==========================================
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #e0f2fe 0%, #e8f5e9 100%) !important;
    }
    [data-testid="stSidebar"] {
        background-color: #002B49 !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
        color: #ffffff !important;
    }
    [data-testid="stForm"], .stElementContainer div[data-aria-stable="true"] {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-radius: 10px;
        padding: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. FUNGSI INTEGRASI GOOGLE SHEETS (CLOUD)
# ==========================================
def simpan_ke_google_sheets(nama_tab, data_list):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # Sistem Otomatis: Membaca dari Cloud Secrets jika ada, jika tidak membaca file lokal
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
# 4. NAVIGASI SAMPING (SIDEBAR)
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
# 5. HALAMAN 1: FORMULIR KUNJUNGAN PUBLIK
# ==========================================
if menu == "FORMULIR KUNJUNGAN PUBLIK":
    
    col_logo, col_text, col_clock = st.columns([1.2, 5.5, 2.3])
    with col_logo:
        try:
            st.image("logo.png", width=120)
        except:
            st.image("https://upload.wikimedia.org/wikipedia/commons/4/44/Logo_BMKG.png", width=120)
            
    with col_text:
        st.markdown("""
            <div style='text-align: center; padding-top: 5px; line-height: 1.2;'>
                <div style='color: #003366; font-size: 30px; font-weight: 900; letter-spacing: 1px; margin-bottom: 2px;'>
                    PORTAL LAYANAN PUBLIK TERINTEGRASI
                </div>
                <div style='color: #1b5e20; font-size: 18px; font-weight: 800; letter-spacing: 0.5px; margin-bottom: 2px;'>
                    STASIUN METEOROLOGI KELAS III SULTAN MUHAMMAD SALAHUDDIN BIMA
                </div>
                <div style='color: #444444; font-size: 14px; font-weight: 700; letter-spacing: 1px; margin-top: 0px;'>
                    BADAN METEOROLOGI, KLIMATOLOGI, DAN GEOFISIKA
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with col_clock:
        components.html("""
            <div id="clock" style="font-family: 'Arial', sans-serif; font-size: 14px; font-weight: bold; color: #003366; text-align: right; padding-top: 25px;"></div>
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
                waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                row_tamu = [waktu_sekarang, nama, identitas, no_hp, instansi, tujuan_final, "Pelayanan Terdaftar"]
                
                if simpan_ke_google_sheets("Tamu", row_tamu):
                    st.success(f"DATA BERHASIL TERSIMPAN: Terima kasih Bapak/Ibu {nama}, data Anda telah tercatat secara sah.")
                    st.balloons()

    with tab2:
        st.subheader("KATALOG INFORMASI TARIF PNBP")
        st.info("Dasar Hukum: Peraturan Pemerintah Republik Indonesia Nomor 47 Tahun 2018.")
        st.write("(Salinan infografis katalog pelayanan publik akan ditampilkan pada bagian ini)")

elif menu == "SURVEI KEPUASAN (IKM)":
    
    st.title("SURVEI INDEKS KEPUASAN MASYARAKAT (IKM)")
    st.write("Penilaian Anda sangat berharga untuk meningkatkan kualitas pelayanan publik di Stasiun Meteorologi Bima.")
    st.divider()
    
    with st.form("form_survei"):
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
            waktu_survei = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            identitas_survei = nama_survei if nama_survei else "Anonim"
            
            row_survei = [waktu_survei, identitas_survei, layanan, sikap, fasilitas, saran]
            
            if simpan_ke_google_sheets("Survei", row_survei):
                st.success("TERIMA KASIH: Penilaian Anda telah kami terima untuk bahan evaluasi pelayanan.")