import streamlit as st
from datetime import datetime, timezone, timedelta
import pandas as pd
import streamlit.components.v1 as components
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="E-Buku Tamu Stamet Bima", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. KUSTOMISASI DESAIN WARNA (SUPER FIX PANAH SIDEBAR LATSAR)
# ==========================================
st.markdown("""
    <style>
    .stAppDeployButton { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    footer { visibility: hidden !important; }
    
    /* --- 1. MEMAKSA KONTAINER HEADER AGAR TIDAK MEMOTONG TOMBOL PANAH --- */
    [data-testid="stHeader"] { 
        background-color: transparent !important; 
        box-shadow: none !important;
        overflow: visible !important;
        z-index: 999999 !important;
    }
    
    /* --- 2. TEMBAK KONTROL SIDEBAR SAAT TERTUTUP (VERSI STREAMLIT BARU) --- */
    [data-testid="stSidebarCollapsedControl"], 
    .stSidebarCollapsedControl {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        position: fixed !important;
        top: 12px !important;
        left: 12px !important;
        z-index: 99999999 !important;
    }
    
    /* --- 3. STYLING TOMBOL PANAH (KEBAL VERSI & KEBAL BAHASA BROWSER) --- */
    [data-testid="stSidebarCollapsedControl"] button,
    .stSidebarCollapsedControl button,
    button[aria-label="Expand sidebar"],
    button[aria-label="Buka bilah sisi"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        background-color: #002B49 !important; /* Warna biru gelap resmi BMKG */
        color: #ffffff !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.4) !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        width: auto !important;
        height: auto !important;
    }
    
    /* --- 4. MEMAKSA IKON SVG PANAH DI DALAMNYA BERWARNA PUTIH MENYALA --- */
    [data-testid="stSidebarCollapsedControl"] button svg,
    .stSidebarCollapsedControl button svg,
    button[aria-label="Expand sidebar"] svg,
    button[aria-label="Buka bilah sisi"] svg {
        fill: #ffffff !important; 
        color: #ffffff !important;
        stroke: #ffffff !important;
        width: 24px !important;
        height: 24px !important;
    }
    
    /* --- DESIGN UTK TOMBOL TUTUP (Saat Sidebar Terbuka) --- */
    [data-testid="stSidebar"] button[aria-label="Close sidebar"],
    [data-testid="stSidebar"] button[aria-label="Tutup bilah sisi"] {
        background-color: rgba(255, 255, 255, 0.15) !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] button[aria-label="Close sidebar"] svg,
    [data-testid="stSidebar"] button[aria-label="Tutup bilah sisi"] svg {
        fill: #ffffff !important;
        color: #ffffff !important;
    }

    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #e0f2fe 0%, #e8f5e9 100%) !important; }
    [data-testid="stSidebar"] { background-color: #002B49 !important; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span, [data-testid="stSidebar"] div {
        color: #ffffff !important;
    }
    [data-testid="stForm"], .stElementContainer div[data-aria-stable="true"] {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #cbd5e1;
    }
    section.main h1, section.main h2, section.main h3, section.main h4, section.main h5, section.main h6,
    section.main label, section.main p, section.main span,
    section.main div[data-testid="stMarkdownContainer"] p,
    section.main div[data-testid="stWidgetLabel"] p {
        color: #003366 !important;
    }
    section.main .stCaptionContainer, section.main div[data-testid="stCaptionContainer"] p { color: #334155 !important; }
    section.main input { color: #000000 !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. FUNGSI INTEGRASI GOOGLE CLOUD (SHEETS & DRIVE)
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
        sheet = client.open("Buku Tamu Stamet Bima").worksheet(nama_tab)
        sheet.append_row(data_list)
        return True
    except Exception as e:
        st.error(f"Sistem gagal terhubung ke Cloud Database: {e}")
        return False

def ambil_data_google_sheets(nama_tab):
    try:
        creds = dapatkan_kredensial()
        client = gspread.authorize(creds)
        sheet = client.open("Buku Tamu Stamet Bima").worksheet(nama_tab)
        data = sheet.get_all_values()
        if len(data) > 1:
            df = pd.DataFrame(data[1:], columns=data[0])
            return df
        elif len(data) == 1:
            return pd.DataFrame(columns=data[0])
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Gagal mengambil data: {e}")
        return pd.DataFrame()

def upload_ke_google_drive(file_buffer, nama_file, mime_type):
    try:
        creds = dapatkan_kredensial()
        service = build('drive', 'v3', credentials=creds)
        
        # ⚠️ MASUKKAN ID FOLDER GOOGLE DRIVE MU DI SINI ⚠️
        FOLDER_ID = "1234567890abcdefghijklmnopqrstuvwxyz" 

        file_metadata = {
            'name': nama_file,
            'parents': [FOLDER_ID]
        }
        
        media = MediaIoBaseUpload(io.BytesIO(file_buffer.getvalue()), mimetype=mime_type, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        
        return file.get('webViewLink')
    except Exception as e:
        st.error(f"Gagal mengunggah arsip berkas ke Cloud Storage: {e}")
        return "Gagal Upload"

# ==========================================
# 4. INISIALISASI KONTROL ALUR (SESSION STATE)
# ==========================================
if "tamu_terdaftar" not in st.session_state:
    st.session_state.tamu_terdaftar = False
if "nama_pendaftar" not in st.session_state:
    st.session_state.nama_pendaftar = ""
if "ikm_selesai" not in st.session_state:
    st.session_state.ikm_selesai = False
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# ==========================================
# 5. NAVIGASI SAMPING (SIDEBAR)
# ==========================================
try:
    st.sidebar.image("logo.png", width=90) 
except:
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/4/44/Logo_BMKG.png", width=90)

st.sidebar.title("NAVIGASI SISTEM")
menu = st.sidebar.radio("PILIH MENU LAYANAN:", [
    "FORMULIR KUNJUNGAN PUBLIK", 
    "SURVEI KEPUASAN (IKM)", 
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
                <div style='color: #003366; font-size: 30px; font-weight: 900; letter-spacing: 1px; margin-bottom: 2px;'>
                    PORTAL LAYANAN PUBLIK TERINTEGRASI
                </div>
                <div style='color: #1b5e20; font-size: 18px; font-weight: 800; letter-spacing: 0.5px; margin-bottom: 2px;'>
                    STASIUN METEOROLOGI KELAS II SULTAN MUHAMMAD SALAHUDDIN BIMA
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
    
    tab1, tab2, tab3 = st.tabs(["E-BUKU TAMU DIGITAL", "PERMOHONAN DATA KHUSUS (RP 0,00)", "E-KATALOG PNBP"])
    
    # --- TAB 1: E-BUKU TAMU ---
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
            st.success("PROSES SELESAI: Terima kasih atas partisipasi Anda dalam mengisi Buku Tamu dan Survei IKM.")
            st.write("")
            if st.button("KEMBALI KE HALAMAN UTAMA (REGISTRASI TAMU BARU)", type="primary", use_container_width=True):
                st.session_state.tamu_terdaftar = False
                st.session_state.nama_pendaftar = ""
                st.session_state.ikm_selesai = False
                st.rerun()

    # --- TAB 2: PORTAL DATA KHUSUS (UPLOAD KE GOOGLE DRIVE CLOUD) ---
    with tab2:
        st.subheader("FORMULIR PERMOHONAN DATA BEBAS TARIF (RP 0,00)")
        st.info("Sesuai aturan PP No. 47 Tahun 2018, layanan ini dikhususkan untuk keperluan Pendidikan, Penelitian non-komersial, dan Instansi Pemerintah.")
        st.warning("⚠️ PENTING: Pemohon WAJIB mengunggah berkas identitas resmi untuk validasi tertib administrasi arsip negara.")
        
        with st.form("form_permohonan_bebas_biaya"):
            st.markdown("#### **I. DATA LAYANAN BEBAS BIAYA**")
            col_k1, col_k2 = st.columns(2)
            
            with col_k1:
                nama_khusus = st.text_input("NAMA LENGKAP PEMOHON:", placeholder="Masukkan nama lengkap")
                instansi_khusus = st.text_input("ASAL KAMPUS / SEKOLAH / INSTANSI:", placeholder="Contoh: Universitas Mataram")
            with col_k2:
                kontak_khusus = st.text_input("NOMOR WHATSAPP AKTIF:", placeholder="Contoh: 081234xxxxxx")
                jenis_data_khusus = st.text_input("JENIS DATA YANG DIMINTA:", placeholder="Contoh: Data Curah Hujan 2015-2025")
            
            st.write("")
            st.markdown("#### **II. UNGGAH BERKAS BUKTI PENDUKUNG (ARSIP CLOUD STASIUN)**")
            col_f1, col_f2 = st.columns(2)
            
            with col_f1:
                file_ktp = st.file_uploader("1. Unggah Foto KTP / Kartu Mahasiswa (Format: JPG / PNG)", type=["jpg", "jpeg", "png"])
            with col_f2:
                file_surat = st.file_uploader("2. Unggah Surat Pengantar (Format: PDF / JPG / PNG)", type=["pdf", "jpg", "jpeg", "png"])
            
            st.write("")
            submit_khusus = st.form_submit_button("KIRIM PERMOHONAN DATA KHUSUS", type="primary", use_container_width=True)
            
            if submit_khusus:
                if not nama_khusus or not instansi_khusus or not file_ktp:
                    st.error("❌ PROSES GAGAL: Kolom Nama, Instansi, dan Berkas Foto KTP wajib diisi serta diunggah untuk kelengkapan arsip!")
                else:
                    with st.spinner("🔄 Sedang mengamankan dokumen arsip ke Google Drive Cloud..."):
                        ext_ktp = file_ktp.name.split('.')[-1]
                        nama_file_ktp = f"KTP_{nama_khusus.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext_ktp}"
                        link_ktp = upload_ke_google_drive(file_ktp, nama_file_ktp, file_ktp.type)
                        
                        link_surat = "Tidak Ada Surat"
                        if file_surat is not None:
                            ext_surat = file_surat.name.split('.')[-1]
                            nama_file_surat = f"Surat_{nama_khusus.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext_surat}"
                            link_surat = upload_ke_google_drive(file_surat, nama_file_surat, file_surat.type)
                        
                        waktu_khusus = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
                        teks_database = f"Link KTP: {link_ktp} | Link Surat: {link_surat}"
                        row_khusus = [waktu_khusus, nama_khusus, "Pemohon Khusus (Rp 0,00)", kontak_khusus, instansi_khusus, jenis_data_khusus, teks_database]
                        
                        if simpan_ke_google_sheets("Tamu", row_khusus):
                            st.success(f"✔️ BERHASIL: Dokumen digital Anda telah sukses diarsip secara aman ke Cloud Storage stasiun!")
                            st.balloons()

    # --- TAB 3: E-KATALOG PNBP ---
    with tab3:
        st.subheader("KATALOG TARIF RESMI JASA DATA DAN INFORMASI (ROMAWI I)")
        st.info("Dasar Hukum: Peraturan Pemerintah Nomor 47 Tahun 2018 tentang Jenis dan Tarif atas Penerimaan Negara Bukan Pajak yang Berlaku pada BMKG.")
        
        st.markdown("### **A. Informasi Khusus Meteorologi, Klimatologi, dan Geofisika**")
        raw_data_ia = {
            "Jenis Penerimaan Negara Bukan Pajak": [
                "1. Informasi Cuaca untuk Penerbangan", "2. Informasi Cuaca untuk Pelayaran",
                "3. Informasi Cuaca untuk Pelabuhan", "4. Informasi Cuaca untuk Pengeboran Lepas Pantai",
                "5.a. Analisis dan Prakiraan Hujan Bulanan", "5.b. Prakiraan Musim Kemarau"
            ],
            "Satuan": [
                "per route unit", "per route per hari", "per lokasi per hari", "per dokumen per lokasi per hari",
                "per buku", "per buku"
            ],
            "Tarif": [
                "4% dari biaya navigasi", "Rp 250.000,00", "Rp 225.000,00", "Rp 330.000,00",
                "Rp 65.000,00", "Rp 230.000,00"
            ]
        }
        st.dataframe(pd.DataFrame(raw_data_ia), use_container_width=True, hide_index=True)

# ==========================================
# 7. HALAMAN 2: SURVEI KEPUASAN (IKM)
# ==========================================
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

# ==========================================
# 8. HALAMAN 3: PORTAL ADMIN & REKAP LAPORAN
# ==========================================
elif menu == "🔒 PORTAL ADMIN & REKAP LAPORAN":
    st.title("SISTEM MANAJEMEN DATABASE STASIUN")
    st.write("Area khusus petugas dan pimpinan untuk audit dan rekapitulasi data.")
    st.divider()

    if not st.session_state.admin_logged_in:
        with st.container(border=True):
            st.markdown("### 🔐 Otorisasi Akses Dibutuhkan")
            password_input = st.text_input("Masukkan Password Administrator:", type="password")
            btn_login = st.button("Masuk / Login", type="primary")
            
            if btn_login:
                if password_input == "adminbima2026":  
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else:
                    st.error("❌ Akses Ditolak: Password Salah!")
    else:
        col_A, col_B = st.columns([8, 2])
        with col_A:
            st.success("✔️ Otorisasi Berhasil. Selamat bertugas, Admin!")
        with col_B:
            if st.button("Keluar / Logout", use_container_width=True):
                st.session_state.admin_logged_in = False
                st.rerun()
        
        st.write("")
        
        tab_db_tamu, tab_db_ikm, tab_arsip = st.tabs(["DATABASE TAMU & LAYANAN", "DATABASE SURVEI IKM", "AUDIT ARSIP DOKUMEN CLOUD (GOOGLE DRIVE)"])
        
        with tab_db_tamu:
            st.subheader("Tabel Rekapitulasi Tamu (Google Sheets Cloud)")
            with st.spinner("Sedang menarik data dari Cloud..."):
                df_tamu = ambil_data_google_sheets("Tamu")
                if not df_tamu.empty:
                    st.dataframe(df_tamu, use_container_width=True)
                    csv_tamu = df_tamu.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Unduh Laporan (.csv)", data=csv_tamu, file_name=f"Laporan_Tamu_Stamet_Bima_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", type="primary")
                else:
                    st.info("Database Tamu masih kosong atau gagal ditarik.")

        with tab_db_ikm:
            st.subheader("Tabel Rekapitulasi Survei IKM (Google Sheets Cloud)")
            with st.spinner("Sedang menarik data IKM dari Cloud..."):
                df_ikm = ambil_data_google_sheets("Survei")
                if not df_ikm.empty:
                    st.dataframe(df_ikm, use_container_width=True)
                    csv_ikm = df_ikm.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Unduh Laporan IKM (.csv)", data=csv_ikm, file_name=f"Laporan_IKM_Stamet_Bima_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", type="primary")
                else:
                    st.info("Database Survei IKM masih kosong atau gagal ditarik.")
                    
        with tab_arsip:
            st.subheader("Galeri Audit Berkas Pemohon Bebas Biaya (Cloud Storage)")
            st.write("Daftar di bawah ini secara otomatis menyandingkan data Sheets dengan arsip dokumen fisik di Google Drive.")
            st.write("")
            
            df_tamu = ambil_data_google_sheets("Tamu")
            
            if not df_tamu.empty:
                if len(df_tamu.columns) >= 7:
                    kolom_target = df_tamu.columns[6]
                    df_khusus = df_tamu[df_tamu[kolom_target].astype(str).str.contains("KTP:", na=False)]
                    
                    if not df_khusus.empty:
                        for index, row in df_khusus.iterrows():
                            with st.container(border=True):
                                col_info, col_links = st.columns([2, 1])
                                
                                teks_detail = str(row[kolom_target])
                                link_ktp = ""
                                link_surat = ""
                                
                                try:
                                    if "|" in teks_detail:
                                        parts = teks_detail.split("|")
                                        link_ktp = parts[0].split("KTP:")[1].strip()
                                        link_surat = parts[1].split("Surat:")[1].strip()
                                except Exception:
                                    pass
                                
                                with col_info:
                                    st.markdown(f"### 👤 {row[df_tamu.columns[1]]}")
                                    st.write(f"**⏰ Waktu Kunjungan:** {row[df_tamu.columns[0]]}")
                                    st.write(f"**🏢 Asal Instansi:** {row[df_tamu.columns[4]]}")
                                    st.write(f"**📱 Kontak WA:** {row[df_tamu.columns[3]]}")
                                    st.write(f"**📂 Layanan Diminta:** {row[df_tamu.columns[5]]}")
                                
                                with col_links:
                                    st.markdown("**📂 Akses Berkas Google Drive:**")
                                    if "http" in link_ktp:
                                        st.link_button("👁️ Lihat Identitas / KTP", link_ktp, use_container_width=True, type="primary")
                                    else:
                                        st.error("⚠️ File KTP menggunakan sistem lama lokal.")
                                    
                                    st.write("")
                                    if "http" in link_surat:
                                        st.link_button("👁️ Lihat Surat Pengantar", link_surat, use_container_width=True)
                                    elif link_surat == "Tidak Ada Surat":
                                        st.info("❌ Pemohon tidak melampirkan Surat.")
                                    else:
                                        st.error("⚠️ File Surat menggunakan sistem lama lokal.")
                    else:
                        st.info("Belum ada data pemohon khusus yang terekam.")
                else:
                    st.warning("Struktur Google Sheets belum sesuai. Pastikan ada minimal 7 kolom data.")
            else:
                st.info("Database Tamu masih kosong.")
