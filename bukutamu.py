import streamlit as st
from datetime import datetime, timezone, timedelta
import pandas as pd
import streamlit.components.v1 as components
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import requests  
import base64    

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="E-Buku Tamu Stamet Bima", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. KUSTOMISASI CSS (KUNCI SIDEBAR, HAPUS FORK GITHUB & UKURAN)
# ==========================================
st.markdown("""
    <style>
    /* 🚫 HAPUS TOTAL FORK, GITHUB ICON & TOOLBAR BAWAAN DI KANAN ATAS */
    [data-testid="stHeaderToolbar"] { display: none !important; }
    header { background-color: transparent !important; }
    .stAppDeployButton { display: none !important; }
    [data-testid="stActionButton"] { display: none !important; }
    footer { display: none !important; visibility: hidden !important; }
    [data-testid="stEmbedHoverBadge"], div[class*="viewerBadge"], div[class*="styles_viewerBadge"] { display: none !important; }
    
    /* 🛠️ MEKANISME PAKSA: Jika sidebar tertutup di browser, buat tombol pembukanya jadi lingkaran Navy mencolok */
    div[data-testid="stSidebarCollapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        position: fixed !important;
        top: 15px !important;
        left: 15px !important;
        z-index: 999999 !important;
    }
    
    /* Styling Tombol Bulat Buka Sidebar */
    div[data-testid="stSidebarCollapsedControl"] button {
        background-color: #002B49 !important; /* Navy Khas BMKG */
        color: #ffffff !important;
        border: 2px solid #ffffff !important; /* Bingkai putih tebal */
        border-radius: 50% !important; 
        width: 44px !important;
        height: 44px !important;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.3) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Paksa Icon Panah bawaan berwarna putih bersih */
    div[data-testid="stSidebarCollapsedControl"] button svg {
        color: #ffffff !important;
        fill: #ffffff !important;
        width: 22px !important;
        height: 22px !important;
    }
    
    div[data-testid="stSidebarCollapsedControl"] button:hover {
        transform: scale(1.08) !important;
        background-color: #003a63 !important;
    }

    /* Modifikasi tombol silang (X) saat posisi terbuka */
    button[data-testid="stSidebarCollapseButton"] {
        color: #ffffff !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
    }
    button[data-testid="stSidebarCollapseButton"] svg {
        color: #ffffff !important;
        fill: #ffffff !important;
    }
    
    /* SIDEBAR KIRI: Tema Gelap Navy */
    [data-testid="stSidebar"] {
        background-color: #002B49 !important;
        border-right: 1px solid #001f36;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* Jarak atas halaman utama */
    .block-container {
        padding-top: 4rem !important;
        padding-bottom: 2rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2.b TOMBOL WHATSAPP MELAYANG
# ==========================================
NOMOR_WA_CS = "628113908535" 
PESAN_OTOMATIS = "Halo%20Admin%20PTSP%20Stamet%20Bima,%20saya%20ingin%20bertanya%20mengenai%20layanan%20data..."

st.markdown(f"""
    <style>
    .float-wa {{
        position: fixed;
        width: 55px; 
        height: 55px;
        bottom: 85px; 
        right: 25px;
        background-color: #25d366;
        color: white;
        border-radius: 50px;
        text-align: center;
        box-shadow: 2px 5px 15px rgba(0,0,0,0.3);
        z-index: 99999;
        display: flex;
        align-items: center;
        justify-content: center;
        text-decoration: none;
        transition: all 0.3s ease;
    }}
    .float-wa:hover {{
        transform: scale(1.1);
        background-color: #20ba5a;
    }}
    .float-wa img {{
        width: 30px;
        height: 30px;
    }}
    </style>
    <a href="https://wa.me/{NOMOR_WA_CS}?text={PESAN_OTOMATIS}" class="float-wa" target="_blank" rel="noopener noreferrer" title="Hubungi CS via WhatsApp">
        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" alt="WhatsApp CS">
    </a>
""", unsafe_allow_html=True)

# ==========================================
# 3. FUNGSI INTEGRASI GOOGLE CLOUD
# ==========================================
def dapatkan_kredensial():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    if "gspread" in st.secrets:
        credentials_info = dict(st.secrets["gspread"])
        return ServiceAccountCredentials.from_json_keyfile_dict(credentials_info, scope)
    else:
        return ServiceAccountCredentials.from_json_keyfile_name("kredensial.json", scope)

def simpan_ke_google_sheets(nama_tab, data_list):
    try:
        creds = dapatkan_kredensial()
        client = gspread.authorize(creds)
        sheet = client.open_by_key("1qdrgfAhB_NKPSIxP9p5cY0LF1RmXRzqG-aWUNEx7r94").worksheet(nama_tab)
        sheet.append_row(data_list)
        return True
    except Exception as e:
        st.error(f"Sistem gagal terhubung ke Cloud Database: {e}")
        return False

def ambil_data_google_sheets(nama_tab):
    try:
        creds = dapatkan_kredensial()
        client = gspread.authorize(creds)
        sheet = client.open_by_key("1qdrgfAhB_NKPSIxP9p5cY0LF1RmXRzqG-aWUNEx7r94").worksheet(nama_tab)
        data = sheet.get_all_values()
        
        if len(data) > 0:
            headers = data[0]
            kolom_unik = []
            for i, col in enumerate(headers):
                nama_kolom = col.strip()
                if nama_kolom == "" or nama_kolom in kolom_unik:
                    nama_kolom = f"Kolom_Data_{i}"
                kolom_unik.append(nama_kolom)
                
            if len(data) > 1:
                return pd.DataFrame(data[1:], columns=kolom_unik)
            else:
                return pd.DataFrame(columns=kolom_unik)
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Gagal mengambil data database: {e}")
        return pd.DataFrame()

def upload_ke_google_drive(file_buffer, nama_file, mime_type):
    url_gas = "https://script.google.com/macros/s/AKfycbwS4JlhvQnHGSj6rZ8nLo7P5Ompf--jv7EPuUkSvSq13N7ThP9vyP5RrYC1fv3oq3lo/exec" 
    
    try:
        file_bytes = file_buffer.getvalue()
        encoded_file = base64.b64encode(file_bytes).decode('utf-8')
        
        payload = {
            "fileData": encoded_file,
            "mimeType": mime_type,
            "fileName": nama_file
        }
        
        response = requests.post(url_gas, data=payload)
        
        try:
            result = response.json()
            if result.get("status") == "success":
                return result.get("url") 
            else:
                return f"Gagal mendapat URL. File tersimpan: {nama_file}"
        except Exception:
            return f"Gagal mendapat URL. File tersimpan: {nama_file}"
            
    except Exception as e:
        return f"Gagal mendapat URL. File tersimpan: {nama_file}"

def update_status_sheets(nama_pemohon, status_baru, link_hasil=""):
    try:
        creds = dapatkan_kredensial()
        client = gspread.authorize(creds)
        sheet = client.open_by_key("1qdrgfAhB_NKPSIxP9p5cY0LF1RmXRzqG-aWUNEx7r94").worksheet("Permohonan_Data")
        cell = sheet.find(nama_pemohon)
        if cell:
            waktu_sekarang = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
            sheet.update_cell(cell.row, 7, status_baru)
            sheet.update_cell(cell.row, 8, waktu_sekarang)
            if link_hasil:
                sheet.update_cell(cell.row, 9, link_hasil)
            return True
        return False
    except Exception as e:
        st.error(f"Gagal memperbarui status di sistem Cloud: {e}")
        return False

# ==========================================
# 4. INISIALISASI KONTROL ALUR
# ==========================================
if "tamu_terdaftar" not in st.session_state:
    st.session_state.tamu_terdaftar = False
if "nama_pendaftar" not in st.session_state:
    st.session_state.nama_pendaftar = ""
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# ==========================================
# 5. NAVIGASI SAMPING
# ==========================================
try:
    st.sidebar.image("logo.png", width=90) 
except:
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/4/44/Logo_BMKG.png", width=90)

st.sidebar.title("NAVIGASI SISTEM")
menu = st.sidebar.radio("PILIH MENU LAYANAN:", [
    "FORMULIR KUNJUNGAN PUBLIK", 
    "🔒 PORTAL ADMIN & REKAP LAPORAN"
])
st.sidebar.divider()
st.sidebar.caption("SISTEM ADMINISTRASI TERPADU")
st.sidebar.caption("STASIUN METEOROLOGI KELAS II SULTAN MUHAMMAD SALAHUDDIN BIMA")

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
        st.markdown("""
            <div style='text-align: center; padding-top: 5px; line-height: 1.2;'>
                <div style='color: #002B49; font-size: 40px; font-weight: 900; letter-spacing: 1px; margin-bottom: 5px;'>
                    PORTAL LAYANAN PUBLIK TERINTEGRASI
                </div>
                <div style='color: #003a63; font-size: 25px; font-weight: 800; letter-spacing: 0.5px; margin-bottom: 5px;'>
                    STASIUN METEOROLOGI KELAS II SULTAN MUHAMMAD SALAHUDDIN BIMA
                </div>
                <div style='color: var(--text-color); opacity: 0.8; font-size: 18px; font-weight: 700; letter-spacing: 1px; margin-top: 0px;'>
                    BADAN METEOROLOGI, KLIMATOLOGI, DAN GEOFISIKA
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with col_clock:
        components.html("""
            <div id="clock" style="font-family: 'Arial', sans-serif; font-size: 14px; font-weight: bold; color: #002B49; text-align: right; padding-top: 25px;"></div>
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
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "E-BUKU TAMU", 
        "PERMOHONAN DATA", 
        "E-KATALOG PNBP",
        "🔍 LACAK STATUS DATA"
    ])
    
    # --- TAB 1: E-BUKU TAMU ---
    with tab1:
        if not st.session_state.tamu_terdaftar:
            st.subheader("FORMULIR REGISTRASI PENGUNJUNG")
            st.caption("Mohon lengkapi data registrasi di bawah ini untuk kepentingan administrasi pelayanan publik.")
            
            with st.container(border=True):
                st.markdown("#### **I. IDENTITAS PENGUNJUNG**")
                col1, col2 = st.columns(2)
                with col1:
                    nama = st.text_input("NAMA LENGKAP", placeholder="Contoh: Nama Beserta Gelar")
                    instansi = st.text_input("ASAL INSTANSI / PERUSAHAAN / UNIVERSITAS", placeholder="Contoh: Pemerintah Kota Bima")
                with col2:
                    no_hp = st.text_input("NOMOR TELEPON / WHATSAPP AKTIF", placeholder="Contoh: 0812345678xx")
            
            st.write("")
            
            with st.container(border=True):
                st.markdown("#### **II. MAKSUD KUNJUNGAN**")
                col3, col4 = st.columns(2)
                with col3:
                    tujuan = st.selectbox(
                        "LAYANAN YANG DITUJU", 
                        ["Kunjungan Kerja / Koordinasi", "Studi Banding / Edukasi Publik", "Lain-lain"]
                    )
                with col4:
                    alasan_lainnya = ""
                    if tujuan == "Lain-lain":
                        alasan_lainnya = st.text_input("URAIKAN MAKSUD KUNJUNGAN SECARA SPESIFIK:", placeholder="Tuliskan Keperluan Anda")

            st.write("") 
            submit_button = st.button("SIMPAN DATA KUNJUNGAN", type="primary", use_container_width=True)
            
            if submit_button:
                if not nama or not no_hp or not instansi:
                    st.error("GAGAL: Mohon lengkapi kolom Nama, Nomor HP, dan Asal Instansi.")
                elif tujuan == "Lain-lain" and not alasan_lainnya:
                    st.warning("PERHATIAN: Mohon uraikan maksud kunjungan secara spesifik pada kolom yang tersedia.")
                else:
                    tujuan_final = alasan_lainnya if tujuan == "Lain-lain" else tujuan
                    waktu_sekarang = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
                    
                    row_tamu = [waktu_sekarang, nama, no_hp, instansi, tujuan_final, "Kunjungan Umum Terdaftar", "-", waktu_sekarang]
                    
                    if simpan_ke_google_sheets("Tamu", row_tamu):
                        st.session_state.tamu_terdaftar = True
                        st.session_state.nama_pendaftar = nama
                        st.rerun()

        elif st.session_state.tamu_terdaftar:
            st.success(f"DATA BERHASIL TERSIMPAN: Terima kasih Bapak/Ibu {st.session_state.nama_pendaftar}, data kunjungan Anda telah sah tercatat.")
            st.balloons()
            st.write("")
            if st.button("KEMBALI KE REGISTRASI TAMU BARU", type="primary", use_container_width=True):
                st.session_state.tamu_terdaftar = False
                st.session_state.nama_pendaftar = ""
                st.rerun()

    # --- TAB 2: PERMOHONAN DATA (DINAMIS RP 0 VS BERBAYAR) ---
    with tab2:
        st.subheader("FORMULIR PERMOHONAN DATA METEOROLOGI")
        
        with st.container(border=True):
            st.markdown("""
            <div style='background-color: rgba(0, 43, 73, 0.05); padding: 15px; border-radius: 8px; border-left: 5px solid #002B49;'>
                <h4 style='color: #002B49; margin-top: 0px;'>📋 PERSYARATAN ADMINISTRASI BERDASARKAN KATEGORI</h4>
                <p style='font-size: 14px; line-height: 1.5; color: var(--text-color); margin-bottom: 5px;'>
                    Sistem akan secara otomatis menyesuaikan formulir unggahan berdasarkan pilihan kategori Anda:
                </p>
                <ul style='font-size: 14px; color: var(--text-color); margin-top: 0px;'>
                    <li><b>Komersial/Swasta (PNBP):</b> Wajib unggah KTP dan Surat Permohonan Instansi.</li>
                    <li><b>Pendidikan/Pemerintah (Rp 0,-):</b> Wajib unggah KTP, Surat Permohonan, Surat Pengantar, Surat Pernyataan Bermeterai, dan Proposal (khusus Mahasiswa).</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        st.write("")
        
        # PILIHAN KATEGORI DI LUAR FORM UNTUK MEMICU PERUBAHAN LAYOUT DINAMIS
        st.markdown("#### **I. TENTUKAN KATEGORI PERMOHONAN**")
        kategori_pemohon = st.radio("Silakan pilih kategori instansi / tujuan Anda:", [
            "Pendidikan / Penelitian Non-Komersial (Tarif Rp 0)",
            "Instansi Pemerintah Pusat / Daerah (Tarif Rp 0)",
            "Komersial / Swasta / Perorangan Umum (Berbayar PNBP)"
        ])
        st.write("")
        
        with st.form("form_permohonan_data"):
            st.markdown("#### **II. IDENTITAS PEMOHON DATA**")
            col_k1, col_k2 = st.columns(2)
            
            with col_k1:
                nama_khusus = st.text_input("NAMA LENGKAP *", placeholder="Nama depan dan nama belakang")
                ktp_nim = st.text_input("NOMOR KTP / NIM *", placeholder="Masukkan Nomor Induk Kependudukan / Mahasiswa")
                instansi_khusus = st.text_input("SEKOLAH / UNIVERSITAS / INSTANSI *", placeholder="Contoh: Universitas Mataram / PT. XYZ")
            with col_k2:
                kontak_khusus = st.text_input("NOMOR HP WHATSAPP (AKTIF) *", placeholder="Contoh: 081234567xxx")
                email_khusus = st.text_input("EMAIL *", placeholder="Contoh: email_anda@gmail.com")
            
            st.write("")
            st.markdown("#### **III. DATA YANG DIBUTUHKAN**")
            judul_penelitian = st.text_input("JUDUL KEGIATAN / PROYEK / PENELITIAN *", placeholder="Masukkan judul penelitian atau proyek")
            jenis_data_khusus = st.selectbox("JENIS DATA YANG DIBUTUHKAN *", [
                "Curah Hujan", "Suhu Udara", "Arah dan Kecepatan Angin", 
                "Tekanan Udara", "Lama Penyinaran Matahari", "Penguapan", "Lainnya"
            ])
            
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                tgl_mulai = st.date_input("PERIODE DATA (TANGGAL MULAI) *")
            with col_d2:
                tgl_selesai = st.date_input("PERIODE DATA (TANGGAL SELESAI) *")
                
            lokasi_data = st.text_input("LOKASI DATA YANG DIMINTA *", placeholder="Contoh: Kota Bima")
            deskripsi_tujuan = st.text_area("DESKRIPSI SINGKAT KEBUTUHAN DATA DAN TUJUAN PENGGUNAAN *", placeholder="Jelaskan secara singkat untuk apa data ini digunakan...")

            st.write("")
            st.markdown(f"#### **IV. UPLOAD BERKAS PENDUKUNG**")
            st.caption(f"Kategori Terpilih: **{kategori_pemohon}**. Maksimal ukuran per file 10MB (.PDF)")
            
            col_u1, col_u2 = st.columns(2)
            
            with col_u1:
                file_ktp = st.file_uploader("1. KTP / Kartu Identitas (Wajib) *", type=["pdf", "jpg", "png"])
                file_surat_permohonan = st.file_uploader("2. Surat Permohonan Permintaan Data (Wajib) *", type=["pdf"])
                
                if "Pendidikan" in kategori_pemohon:
                    st.write("")
                    file_proposal = st.file_uploader("5. Proposal & Lembar Pengesahan (Wajib Mahasiswa) *", type=["pdf"])
                else:
                    file_proposal = None
                    
            with col_u2:
                if "Berbayar PNBP" in kategori_pemohon:
                    st.info("💡 **Informasi Layanan Komersial:** \nAnda berada pada jalur permohonan berbayar (PNBP). Anda cukup melampirkan identitas diri (KTP) dan Surat Permohonan resmi dari perusahaan/instansi Anda.")
                    file_surat_pengantar = None
                    file_surat_pernyataan = None
                else:
                    st.markdown("📄 **[Download Format Surat Pengantar](https://docs.google.com/document/d/1YNKGAGzif4i36bvLLCZ2jDyz8oYYoQLj/edit)**")
                    file_surat_pengantar = st.file_uploader("3. Surat Pengantar Sekolah/Univ/Instansi (Wajib) *", type=["pdf"])
                    
                    st.markdown("📄 **[Download Format Surat Pernyataan Bermeterai](https://docs.google.com/document/d/1N6nBHU8PIaGtXIX6u96T9Z0f6cYcnkb6/edit)**")
                    file_surat_pernyataan = st.file_uploader("4. Surat Pernyataan Bermeterai (Wajib) *", type=["pdf"])
            
            st.write("")
            st.markdown("#### **V. KONFIRMASI SURVEI KEPUASAN MASYARAKAT (SKM)**")
            st.info("Berdasarkan standar pelayanan, pemohon diwajibkan untuk mengisi Survei Kepuasan Masyarakat (SKM) sebelum mengirimkan berkas.")
            st.write("👉 **[KLIK DI SINI UNTUK MENGISI FORMULIR SKM BMKG](https://forms.gle/7msXFJk9sKNhGtrQ7)**")
            
            cek_skm = st.checkbox("Saya menyatakan dengan sadar bahwa saya TELAH MENGISI Survei Kepuasan Masyarakat (SKM) pada tautan di atas. *")
            
            st.write("")
            submit_khusus = st.form_submit_button("KIRIM PERMOHONAN DATA", type="primary", use_container_width=True)
            
            if submit_khusus:
                # Validasi Form Umum
                if not nama_khusus or not ktp_nim or not instansi_khusus or not kontak_khusus or not email_khusus or not judul_penelitian or not lokasi_data or not deskripsi_tujuan:
                    st.error("❌ PROSES GAGAL: Mohon lengkapi seluruh kolom teks isian (Identitas & Kebutuhan Data)!")
                elif not file_ktp or not file_surat_permohonan:
                    st.error("❌ PROSES GAGAL: Identitas (KTP) dan Surat Permohonan WAJIB diunggah!")
                elif not cek_skm:
                    st.error("❌ PROSES GAGAL: Anda WAJIB mencentang kotak konfirmasi Survei Kepuasan Masyarakat (SKM) sebelum mengirimkan formulir.")
                
                # Validasi Form Dinamis (Rp 0 vs PNBP)
                elif "Tarif Rp 0" in kategori_pemohon and (not file_surat_pengantar or not file_surat_pernyataan):
                    st.error("❌ PROSES GAGAL: Surat Pengantar Instansi dan Surat Pernyataan Bermeterai WAJIB dilampirkan untuk permohonan jalur Bebas Tarif (Rp 0)!")
                elif "Pendidikan" in kategori_pemohon and not file_proposal:
                    st.error("❌ PROSES GAGAL: Proposal Penelitian WAJIB dilampirkan untuk permohonan jalur Pendidikan/Mahasiswa!")
                
                else:
                    # Jika semua validasi lulus, jalankan upload
                    with st.spinner("🔄 Sedang mengunggah dokumen ke Cloud Server... (Mohon tunggu
