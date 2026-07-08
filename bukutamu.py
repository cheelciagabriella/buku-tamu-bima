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
# 2. KUSTOMISASI CSS FORMAL & ELEGAN
# ==========================================
st.markdown("""
    <style>
    /* Mengubah font seluruh halaman menjadi Arial/Helvetica yang sangat formal */
    html, body, [class*="css"] {
        font-family: 'Arial', 'Helvetica Neue', Helvetica, sans-serif !important;
    }

    [data-testid="stHeaderToolbar"] { display: none !important; }
    header { background-color: transparent !important; }
    .stAppDeployButton { display: none !important; }
    [data-testid="stActionButton"] { display: none !important; }
    footer { display: none !important; visibility: hidden !important; }
    [data-testid="stEmbedHoverBadge"], div[class*="viewerBadge"], div[class*="styles_viewerBadge"] { display: none !important; }
    
    div[data-testid="stSidebarCollapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        position: fixed !important;
        top: 15px !important;
        left: 15px !important;
        z-index: 999999 !important;
    }
    
    div[data-testid="stSidebarCollapsedControl"] button {
        background-color: #002B49 !important;
        color: #ffffff !important;
        border: 2px solid #ffffff !important;
        border-radius: 50% !important; 
        width: 44px !important;
        height: 44px !important;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.3) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
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

    button[data-testid="stSidebarCollapseButton"] {
        color: #ffffff !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
    }
    button[data-testid="stSidebarCollapseButton"] svg {
        color: #ffffff !important;
        fill: #ffffff !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #002B49 !important;
        border-right: 1px solid #001f36;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    .block-container {
        padding-top: 4rem !important;
        padding-bottom: 2rem !important;
    }

    /* Menebalkan teks pada semua tombol navigasi st.button */
    div[data-testid="stButton"] button p {
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        font-size: 15px !important;
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
            sheet.update_cell(cell.row, 19, status_baru)
            sheet.update_cell(cell.row, 20, waktu_sekarang)
            if link_hasil:
                sheet.update_cell(cell.row, 21, link_hasil)
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
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "E-BUKU TAMU"
if "admin_tab" not in st.session_state:
    st.session_state.admin_tab = "DATABASE TAMU & LAYANAN"

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
    "PORTAL ADMIN & REKAP LAPORAN"
])
st.sidebar.divider()
st.sidebar.caption("SISTEM ADMINISTRASI TERPADU")
st.sidebar.caption("STASIUN METEOROLOGI KELAS II SULTAN MUHAMMAD SALAHUDDIN BIMA")

# ==========================================
# 6. HALAMAN UTAMA LAYANAN PUBLIK
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
    
    # ---------------------------------------------------------
    # TOMBOL KOTAK NAVIGASI 
    # ---------------------------------------------------------
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("E-BUKU TAMU", use_container_width=True, type="primary" if st.session_state.active_tab == "E-BUKU TAMU" else "secondary"):
            st.session_state.active_tab = "E-BUKU TAMU"
            st.rerun()
    with c2:
        if st.button("PERMOHONAN DATA", use_container_width=True, type="primary" if st.session_state.active_tab == "PERMOHONAN DATA" else "secondary"):
            st.session_state.active_tab = "PERMOHONAN DATA"
            st.rerun()
    with c3:
        if st.button("E-KATALOG PNBP", use_container_width=True, type="primary" if st.session_state.active_tab == "E-KATALOG PNBP" else "secondary"):
            st.session_state.active_tab = "E-KATALOG PNBP"
            st.rerun()
    with c4:
        if st.button("LACAK STATUS DATA", use_container_width=True, type="primary" if st.session_state.active_tab == "LACAK STATUS DATA" else "secondary"):
            st.session_state.active_tab = "LACAK STATUS DATA"
            st.rerun()
            
    st.markdown("---")
    
    # ------------------------------------------
    # ISI HALAMAN 1: E-BUKU TAMU
    # ------------------------------------------
    if st.session_state.active_tab == "E-BUKU TAMU":
        if not st.session_state.tamu_terdaftar:
            st.subheader("📖 FORMULIR REGISTRASI PENGUNJUNG")
            st.caption("Mohon lengkapi data registrasi di bawah ini untuk kepentingan administrasi pelayanan publik.")
            
            with st.container(border=True):
                st.markdown("#### **I. IDENTITAS PENGUNJUNG**")
                col1, col2 = st.columns(2)
                with col1:
                    nama = st.text_input("**NAMA LENGKAP** *", placeholder="Contoh: Nama Beserta Gelar")
                    instansi = st.text_input("**ASAL INSTANSI / PERUSAHAAN / UNIVERSITAS** *", placeholder="Contoh: Pemerintah Kota Bima")
                with col2:
                    no_hp = st.text_input("**NOMOR TELEPON / WHATSAPP AKTIF** *", placeholder="Contoh: 0812345678xx")
            
            st.write("")
            
            with st.container(border=True):
                st.markdown("#### **II. MAKSUD KUNJUNGAN**")
                col3, col4 = st.columns(2)
                with col3:
                    tujuan = st.selectbox(
                        "**LAYANAN YANG DITUJU** *", 
                        ["Kunjungan Kerja / Koordinasi", "Studi Banding / Edukasi Publik", "Lain-lain"]
                    )
                with col4:
                    alasan_lainnya = ""
                    if tujuan == "Lain-lain":
                        alasan_lainnya = st.text_input("**URAIKAN MAKSUD KUNJUNGAN SECARA SPESIFIK:** *", placeholder="Tuliskan Keperluan Anda")

            st.write("") 
            submit_button = st.button("SIMPAN DATA KUNJUNGAN", type="primary", use_container_width=True)
            
            if submit_button:
                if not nama or not no_hp or not instansi:
                    st.error("❌ **GAGAL:** Mohon lengkapi kolom Nama, Nomor HP, dan Asal Instansi.")
                elif tujuan == "Lain-lain" and not alasan_lainnya:
                    st.warning("⚠️ **PERHATIAN:** Mohon uraikan maksud kunjungan secara spesifik pada kolom yang tersedia.")
                else:
                    tujuan_final = alasan_lainnya if tujuan == "Lain-lain" else tujuan
                    waktu_sekarang = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
                    
                    row_tamu = [waktu_sekarang, nama, no_hp, instansi, tujuan_final, "Kunjungan Umum Terdaftar", "-", waktu_sekarang]
                    
                    if simpan_ke_google_sheets("Tamu", row_tamu):
                        st.session_state.tamu_terdaftar = True
                        st.session_state.nama_pendaftar = nama
                        st.rerun()

        elif st.session_state.tamu_terdaftar:
            st.success(f"🎉 **DATA BERHASIL TERSIMPAN:** Terima kasih Bapak/Ibu **{st.session_state.nama_pendaftar}**, data kunjungan Anda telah sah tercatat.")
            st.balloons()
            st.write("")
            if st.button("KEMBALI KE REGISTRASI TAMU BARU", type="primary", use_container_width=True):
                st.session_state.tamu_terdaftar = False
                st.session_state.nama_pendaftar = ""
                st.rerun()

    # ------------------------------------------
    # ISI HALAMAN 2: PERMOHONAN DATA
    # ------------------------------------------
    elif st.session_state.active_tab == "PERMOHONAN DATA":
        st.subheader("📝 FORMULIR PERMOHONAN DATA METEOROLOGI")
        
        with st.container(border=True):
            st.markdown("""
            <div style='background-color: rgba(0, 43, 73, 0.05); padding: 15px; border-radius: 8px; border-left: 5px solid #002B49;'>
                <h4 style='color: #002B49; margin-top: 0px;'>📋 PERSYARATAN ADMINISTRASI BERDASARKAN KATEGORI</h4>
                <p style='font-size: 14px; line-height: 1.5; color: var(--text-color); margin-bottom: 5px;'>
                    Sistem akan secara otomatis menyesuaikan formulir unggahan berdasarkan pilihan kategori Anda:
                </p>
                <ul style='font-size: 14px; color: var(--text-color); margin-top: 0px;'>
                    <li><b>Komersial/Swasta (PNBP):</b> <b>Wajib</b> unggah KTP, Surat Permohonan Instansi, dan Bukti Isi SKM.</li>
                    <li><b>Pendidikan/Pemerintah (Rp 0,-):</b> <b>Wajib</b> unggah KTP, Surat Permohonan, Surat Pengantar, Surat Pernyataan Bermeterai, Proposal (khusus Mahasiswa), dan Bukti Isi SKM. <span style='color:red; font-weight:bold;'>Maksimal rentang periode data adalah 5 tahun.</span></li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        st.write("")
        
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
                nama_khusus = st.text_input("**NAMA LENGKAP** *", placeholder="Nama depan dan nama belakang")
                ktp_nim = st.text_input("**NOMOR KTP / NIM** *", placeholder="Masukkan Nomor Induk Kependudukan / Mahasiswa")
                instansi_khusus = st.text_input("**SEKOLAH / UNIVERSITAS / INSTANSI** *", placeholder="Contoh: Universitas Mataram / PT. XYZ")
            with col_k2:
                kontak_khusus = st.text_input("**NOMOR HP WHATSAPP (AKTIF)** *", placeholder="Contoh: 081234567xxx")
                email_khusus = st.text_input("**EMAIL** *", placeholder="Contoh: email_anda@gmail.com")
            
            st.write("")
            st.markdown("#### **III. DATA YANG DIBUTUHKAN**")
            judul_penelitian = st.text_input("**JUDUL KEGIATAN / PROYEK / PENELITIAN** *", placeholder="Masukkan judul penelitian atau proyek")
            jenis_data_khusus = st.selectbox("**JENIS DATA YANG DIBUTUHKAN** *", [
                "Curah Hujan", "Suhu Udara", "Arah dan Kecepatan Angin", 
                "Tekanan Udara", "Lama Penyinaran Matahari", "Penguapan", "Lainnya"
            ])
            
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                tgl_mulai = st.date_input("**PERIODE DATA (TANGGAL MULAI)** *")
            with col_d2:
                tgl_selesai = st.date_input("**PERIODE DATA (TANGGAL SELESAI)** *")
                if "Tarif Rp 0" in kategori_pemohon:
                    st.markdown("<small style='color: red; font-weight: bold;'>⚠️ (Perhatian: Untuk data Tarif Rp. 0,- maksimal periode data adalah 5 tahun)</small>", unsafe_allow_html=True)
                
            lokasi_data = st.text_input("**LOKASI DATA YANG DIMINTA** *", placeholder="Contoh: Kota Bima")
            deskripsi_tujuan = st.text_area("**DESKRIPSI SINGKAT KEBUTUHAN DATA DAN TUJUAN PENGGUNAAN** *", placeholder="Jelaskan secara singkat untuk apa data ini digunakan...")

            st.write("")
            st.markdown(f"#### **IV. UPLOAD BERKAS PENDUKUNG**")
            st.caption(f"Kategori Terpilih: **{kategori_pemohon}**. Maksimal ukuran per file 10MB (.PDF / Gambar)")
            
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                file_ktp = st.file_uploader("**1. KTP / Kartu Identitas (Wajib)** *", type=["pdf", "jpg", "png"])
                file_surat_permohonan = st.file_uploader("**2. Surat Permohonan (Wajib)** *", type=["pdf"])
                if "Pendidikan" in kategori_pemohon:
                    st.write("")
                    file_proposal = st.file_uploader("**5. Proposal & Lembar Pengesahan (Wajib Mahasiswa)** *", type=["pdf"])
                else:
                    file_proposal = None
                    
            with col_u2:
                if "Berbayar PNBP" in kategori_pemohon:
                    st.info("💡 **Informasi Layanan Komersial:** \nAnda berada pada jalur permohonan berbayar (PNBP). Anda cukup melampirkan identitas diri (KTP), Surat Permohonan resmi dari instansi, dan tangkapan layar bukti pengisian SKM di bawah.")
                    file_surat_pengantar = None
                    file_surat_pernyataan = None
                else:
                    st.markdown("📄 **[Download Format Surat Pengantar](https://docs.google.com/document/d/1YNKGAGzif4i36bvLLCZ2jDyz8oYYoQLj/edit)**")
                    file_surat_pengantar = st.file_uploader("**3. Surat Pengantar Instansi (Wajib)** *", type=["pdf"])
                    st.markdown("📄 **[Download Format Surat Pernyataan Bermeterai](https://docs.google.com/document/d/1N6nBHU8PIaGtXIX6u96T9Z0f6cYcnkb6/edit)**")
                    file_surat_pernyataan = st.file_uploader("**4. Surat Pernyataan Bermeterai (Wajib)** *", type=["pdf"])
            
            st.write("")
            st.markdown("#### **V. KONFIRMASI SURVEI KEPUASAN MASYARAKAT (SKM) [WAJIB]**")
            st.info("Berdasarkan standar pelayanan, pemohon diwajibkan untuk mengisi Survei Kepuasan Masyarakat (SKM) sebelum mengirimkan berkas permohonan.")
            st.write("👉 **[KLIK DI SINI UNTUK MENGISI FORMULIR SKM BMKG](https://forms.gle/7msXFJk9sKNhGtrQ7)**")
            
            file_bukti_skm = st.file_uploader("**6. Unggah Bukti Hasil Pengisian SKM (Wajib)** *", type=["pdf", "jpg", "jpeg", "png"])
            cek_skm = st.checkbox("**Saya menyatakan dengan sadar bahwa saya BENAR-BENAR TELAH MENGISI Survei Kepuasan Masyarakat (SKM) pada tautan di atas dan mengunggah buktinya.** *")
            
            st.write("")
            submit_khusus = st.form_submit_button("KIRIM PERMOHONAN DATA", type="primary", use_container_width=True)
            
        if submit_khusus:
            selisih_hari = (tgl_selesai - tgl_mulai).days
            is_valid = True
            
            if not nama_khusus or not ktp_nim or not instansi_khusus or not kontak_khusus or not email_khusus or not judul_penelitian or not lokasi_data or not deskripsi_tujuan or not file_ktp or not file_surat_permohonan or not file_bukti_skm:
                is_valid = False
            
            if "Tarif Rp 0" in kategori_pemohon and (not file_surat_pengantar or not file_surat_pernyataan):
                is_valid = False
                
            if "Pendidikan" in kategori_pemohon and not file_proposal:
                is_valid = False

            if not is_valid:
                st.error("❌ **PROSES GAGAL:** Pastikan seluruh kolom isian dan berkas yang bertanda Wajib (*) telah diisi dan diunggah sesuai dengan kategori permohonan Anda.")
            elif not cek_skm:
                st.error("❌ **PROSES GAGAL:** Anda WAJIB mencentang kotak konfirmasi Survei Kepuasan Masyarakat (SKM).")
            elif "Tarif Rp 0" in kategori_pemohon and selisih_hari > 1825:
                st.error(f"❌ **PROSES GAGAL:** Rentang data yang Anda minta adalah {selisih_hari} hari. Untuk jalur data Rp. 0,- (Gratis), maksimal periode data adalah 5 tahun (1.825 hari).")
            else:
                with st.spinner("🔄 Sedang mengunggah seluruh dokumen ke Cloud Server..."):
                    def proses_upload(file_obj, prefix):
                        if file_obj is not None:
                            ext = file_obj.name.split('.')[-1]
                            nama_file = f"{prefix}_{nama_khusus.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M')}.{ext}"
                            return upload_ke_google_drive(file_obj, nama_file, file_obj.type)
                        return "-"

                    link_ktp = proses_upload(file_ktp, "KTP")
                    link_permohonan = proses_upload(file_surat_permohonan, "Permohonan")
                    link_pengantar = proses_upload(file_surat_pengantar, "Pengantar")
                    link_pernyataan = proses_upload(file_surat_pernyataan, "Pernyataan")
                    link_proposal = proses_upload(file_proposal, "Proposal")
                    link_skm = proses_upload(file_bukti_skm, "Bukti_SKM")
                    
                    waktu_khusus = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
                    periode_gabung = f"{tgl_mulai} sd {tgl_selesai}"
                    
                    row_khusus = [
                        waktu_khusus, nama_khusus, kontak_khusus, instansi_khusus, kategori_pemohon, ktp_nim, email_khusus, 
                        judul_penelitian, jenis_data_khusus, periode_gabung, lokasi_data, deskripsi_tujuan, link_ktp, 
                        link_permohonan, link_pengantar, link_pernyataan, link_proposal, link_skm, 
                        "Menunggu Verifikasi Berkas", waktu_khusus, "-"
                    ]
                    
                    if simpan_ke_google_sheets("Permohonan_Data", row_khusus):
                        st.balloons()
                        st.success("✔️ **DATA BERHASIL TERSIMPAN DI DATABASE!**")
                        
                        # UI WAJIB KONFIRMASI AGAR ADMIN TAHU
                        st.markdown("""
                            <div style='background-color: #ff4b4b; padding: 20px; border-radius: 8px; color: white; text-align: center; margin-top: 15px; margin-bottom: 15px;'>
                                <h3 style='color: white; margin-top: 0;'>⚠️ TAHAP AKHIR: WAJIB KONFIRMASI!</h3>
                                <p style='font-size: 16px;'>Permohonan Anda <b>TIDAK AKAN DIPROSES</b> oleh Admin jika Anda tidak melakukan konfirmasi via WhatsApp.</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if "Berbayar PNBP" in kategori_pemohon:
                            st.write(f"Halo **{nama_khusus}**, permohonan data Anda akan dikenakan tarif PNBP sesuai PP No. 47 Tahun 2018[cite: 1].")
                            pesan_wa = f"Halo%20Admin%20PTSP%20Stamet%20Bima.%20Saya%20*{nama_khusus}*%20baru%20saja%20mengajukan%20permohonan%20data%20jalur%20*Komersial%20(PNBP)*.%20Saya%20ingin%20konfirmasi%20bahwa%20seluruh%20berkas%20telah%20saya%20unggah.%20Mohon%20informasi%20rincian%20tarif%20dan%20kode%20billing-nya.%20Terima%20kasih."
                        else:
                            st.write("Seluruh dokumen syarat digital serta bukti pengisian SKM Anda telah sukses diamankan ke Cloud Server.")
                            pesan_wa = f"Halo%20Admin%20PTSP%20Stamet%20Bima.%20Saya%20*{nama_khusus}*%20baru%20saja%20mengajukan%20permohonan%20data%20jalur%20*Bebas%20Tarif%20(Rp%200)*.%20Saya%20ingin%20konfirmasi%20bahwa%20seluruh%20berkas%20telah%20saya%20unggah.%20Mohon%20segera%20diverifikasi.%20Terima%20kasih."
                            
                        st.link_button("🚨 KLIK DI SINI UNTUK KONFIRMASI KE WA ADMIN (WAJIB) 🚨", f"https://wa.me/{NOMOR_WA_CS}?text={pesan_wa}", type="primary", use_container_width=True)

    # ------------------------------------------
    # ISI HALAMAN 3: E-KATALOG PNBP
    # ------------------------------------------
    elif st.session_state.active_tab == "E-KATALOG PNBP":
        st.markdown("<h3 style='color: #002B49; margin-bottom: 0px;'>💰 Katalog Tarif Resmi Jasa Data dan Informasi</h3>", unsafe_allow_html=True)
        st.caption("Berdasarkan Peraturan Pemerintah Nomor 47 Tahun 2018 tentang Jenis dan Tarif atas Jenis Penerimaan Negara Bukan Pajak (PNBP) yang berlaku pada BMKG.")
        st.write("")
        
        st.markdown("📥 **[Unduh File Asli Peraturan Pemerintah (PP) Nomor 47 Tahun 2018 (.PDF)](https://drive.google.com/file/d/1GYgfIqjigGiQF5z_w1y_qg3oGdI9Xe0K/view?usp=drive_web)**")
        st.write("")
        
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.info("🎓 **Layanan Tarif Rp 0,- (GRATIS)**\nDiperuntukkan secara khusus bagi Mahasiswa/Pelajar (Tugas Akhir/Skripsi), Kegiatan Sosial, Keagamaan, dan Instansi Pemerintah Pusat/Daerah berskala non-komersial.")
        with col_t2:
            st.warning("💼 **Layanan PNBP (BERBAYAR)**\nDiperuntukkan bagi Instansi Swasta, BUMN, Kontraktor, dan Perorangan untuk keperluan operasional proyek, klaim asuransi, dan kegiatan berorientasi profit/komersial.")
        
        st.write("")
        st.markdown("#### **Tabel Rincian Layanan Prioritas Stamet Bima**")
        
        raw_data_ia = {
            "No.": ["1", "2"],
            "Jenis Layanan (Penerimaan Negara Bukan Pajak)": [
                "Informasi Meteorologi untuk Keperluan Klaim Asuransi", 
                "Informasi Meteorologi Khusus untuk Pendukung Kegiatan Proyek, Survei, dan Penelitian Komersial (Jasa Konsultasi Meteorologi)"
            ],
            "Satuan": [
                "per lokasi per hari", 
                "per lokasi"
            ],
            "Tarif Resmi": [
                "Rp 175.000,00", 
                "Rp 3.750.000,00"
            ]
        }
        st.dataframe(pd.DataFrame(raw_data_ia), use_container_width=True, hide_index=True)
        
        st.write("")
        
        with st.expander("💳 **KLIK DI SINI: Informasi Tata Cara Pembayaran Resmi ke Kas Negara (e-Billing SIMPONI)**"):
            st.markdown("""
            Demi menjaga transparansi dan akuntabilitas pelayanan publik, seluruh biaya PNBP langsung disetorkan ke Kas Negara tanpa melalui rekening pribadi petugas. Berikut alurnya:
            
            1. **Penerbitan Kode Billing:** Setelah permohonan data Anda disetujui, Petugas PTSP (Admin) akan membuatkan kode *e-Billing* resmi melalui aplikasi SIMPONI Kementerian Keuangan. Kode ini akan dikirimkan ke WhatsApp Anda.
            2. **Proses Pembayaran:** Anda dapat melakukan pembayaran menggunakan 15 digit kode *billing* tersebut melalui:
               * Teller Bank Persepsi (BRI, BNI, Mandiri, BCA, dll) / Kantor Pos.
               * ATM / Mobile Banking / Internet Banking (Menu: Pembayaran -> Penerimaan Negara / MPN).
               * *E-Commerce* (Tokopedia, Bukalapak) pada menu Penerimaan Negara.
            3. **Konfirmasi & Penerimaan Data:** Setelah berhasil membayar, simpan struk Bukti Penerimaan Negara (BPN), lalu unggah/kirimkan foto struk tersebut ke WhatsApp *Customer Service* kami. Data hasil (softcopy/hardcopy) akan segera kami serahkan.
            """)
        
        st.write("")
        pesan_tanya_tarif = "Halo%20Admin%20PTSP%20Stamet%20Bima,%20saya%20ingin%20konsultasi%20mengenai%20estimasi%20tarif%20PNBP%20untuk%20permintaan%20data%20..."
        st.link_button("📞 Konsultasi Estimasi Biaya via WhatsApp", f"https://wa.me/{NOMOR_WA_CS}?text={pesan_tanya_tarif}", use_container_width=True)

    # ------------------------------------------
    # ISI HALAMAN 4: FITUR TRACKING / LACAK DATA UNTUK KONSUMEN
    # ------------------------------------------
    elif st.session_state.active_tab == "LACAK STATUS DATA":
        st.subheader("🔍 PORTAL PELACAKAN STATUS PERMOHONAN DATA")
        st.caption("Transparansi Pelayanan Publik: Lacak status pemrosesan dokumen data khusus Anda secara real-time.")
        
        with st.form("form_lacak"):
            no_hp_cari = st.text_input("**Masukkan Nomor WhatsApp yang Anda Daftarkan:**", placeholder="Contoh: 081234567xxx")
            btn_lacak = st.form_submit_button("CEK PROGRESS SEKARANG", type="primary", use_container_width=True)
            
        if btn_lacak:
            if not no_hp_cari:
                st.warning("⚠️ Silakan isi nomor WhatsApp Anda terlebih dahulu.")
            else:
                with st.spinner("🔍 Mencari data di database stasiun..."):
                    df_permohonan = ambil_data_google_sheets("Permohonan_Data")
                    if not df_permohonan.empty:
                        df_user = df_permohonan[df_permohonan.iloc[:, 2].astype(str) == str(no_hp_cari)]
                        
                        if not df_user.empty:
                            data_terakhir = df_user.iloc[-1]
                            nama_user = data_terakhir.iloc[1]
                            jenis_data = data_terakhir.iloc[8] if len(data_terakhir) > 8 else "-"
                            waktu_minta = data_terakhir.iloc[0]
                            
                            status_proses = data_terakhir.iloc[18] if len(data_terakhir) >= 19 else "Menunggu Verifikasi Berkas"
                            waktu_update = data_terakhir.iloc[19] if len(data_terakhir) >= 20 else waktu_minta
                            link_hasil_unduh = data_terakhir.iloc[20] if len(data_terakhir) >= 21 else ""
                            
                            st.write("")
                            st.markdown(f"### 📊 Resume Pengajuan: **{nama_user}**")
                            st.markdown(f"**📂 Dokumen Data:** {jenis_data}  \n**⏰ Waktu Registrasi Awal:** {waktu_minta}")
                            st.divider()
                            
                            st.markdown("#### **Progress Alur Kerja Layanan:**")
                            st.caption(f"🕒 Status terakhir diperbarui pada: {waktu_update}")
                            
                            if status_proses == "Menunggu Verifikasi Berkas":
                                st.info("🔎 **STATUS: MENUNGGU VERIFIKASI BERKAS** \nPermohonan Anda telah kami terima. Saat ini tim sedang memverifikasi kelengkapan dan keabsahan seluruh berkas digital dan bukti SKM Anda.")
                            elif status_proses == "Proses Penyiapan Data":
                                st.warning("🔄 **STATUS: PROSES PENYIAPAN DATA** \nBerkas administrasi Anda telah disetujui. Saat ini tim teknis Stamet Bima sedang menyiapkan arsip data meteorologi yang Anda butuhkan.")
                            elif status_proses == "Menunggu Pembayaran PNBP":
                                st.warning("💳 **STATUS: MENUNGGU PEMBAYARAN PNBP** \nData Anda sedang disiapkan, namun Anda diwajibkan menyelesaikan pembayaran PNBP sesuai peraturan yang berlaku. Mohon hubungi Customer Service kami untuk penerbitan e-Billing.")
                            elif status_proses == "Selesai (Data Telah Dikirim / Siap Diambil)":
                                st.success("🎉 **STATUS: SELESAI** \nKabar baik! Permintaan data Anda telah selesai dikerjakan.")
                                if "http" in str(link_hasil_unduh):
                                    st.write("Silakan unduh dokumen data meteorologi Anda melalui tautan di bawah ini:")
                                    st.link_button("📥 UNDUH DATA HASIL PERMOHONAN", link_hasil_unduh, type="primary", use_container_width=True)
                                else:
                                    st.write("Silakan cek dokumen masuk di email/WhatsApp Anda atau datang langsung ke ruang PTSP Stasiun.")
                            elif status_proses == "Ditolak (Berkas Tidak Memenuhi Syarat)":
                                st.error("❌ **STATUS: DITOLAK** \nMohon maaf, permohonan Anda ditolak karena dokumen syarat buram, tidak lengkap, rentang waktu tidak sesuai, atau tidak memenuhi syarat. Silakan lakukan registrasi ulang.")
                            else:
                                st.info(f"🚩 **STATUS:** {status_proses}")
                        else:
                            st.error("❌ Data Tidak Ditemukan. Pastikan nomor WhatsApp yang Anda masukkan sama persis dengan yang diisi pada formulir.")
                    else:
                        st.info("Database kosong atau sedang tidak tersedia.")

# ==========================================
# 7. PORTAL ADMIN & REKAP LAPORAN
# ==========================================
elif menu == "PORTAL ADMIN & REKAP LAPORAN":
    st.title("SISTEM MANAJEMEN DATABASE STASIUN")
    st.divider()

    if not st.session_state.admin_logged_in:
        with st.form("form_login"):
            st.markdown("### 🔐 Otorisasi Akses Dibutuhkan")
            password_input = st.text_input("**Masukkan Password Administrator:**", type="password")
            btn_login = st.form_submit_button("Masuk / Login", type="primary")
            
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
        
        st.markdown("#### 🔗 Akses Cepat Cloud Storage")
        col_sheet, col_drive = st.columns(2)
        with col_sheet:
            st.link_button("📊 Buka Google Sheets (Database Asli)", "https://docs.google.com/spreadsheets/d/1qdrgfAhB_NKPSIxP9p5cY0LF1RmXRzqG-aWUNEx7r94/edit", use_container_width=True)
        with col_drive:
            st.link_button("📁 Buka Google Drive (Folder Arsip)", "https://drive.google.com/drive/folders/1FtwvPLbWcTPpyIOxMRBW88oLHri_rZVH", use_container_width=True)
        st.divider()
        
        ca1, ca2 = st.columns(2)
        with ca1:
            if st.button("DATABASE TAMU & LAYANAN", use_container_width=True, type="primary" if st.session_state.admin_tab == "DATABASE TAMU & LAYANAN" else "secondary"):
                st.session_state.admin_tab = "DATABASE TAMU & LAYANAN"
                st.rerun()
        with ca2:
            if st.button("ARSIP DOKUMEN CLOUD", use_container_width=True, type="primary" if st.session_state.admin_tab == "ARSIP DOKUMEN CLOUD" else "secondary"):
                st.session_state.admin_tab = "ARSIP DOKUMEN CLOUD"
                st.rerun()
                
        st.markdown("---")
        
        if st.session_state.admin_tab == "DATABASE TAMU & LAYANAN":
            st.subheader("1. Tabel Rekapitulasi Buku Tamu")
            with st.spinner("Sedang menarik data Tamu dari Cloud..."):
                df_tamu = ambil_data_google_sheets("Tamu")
                if not df_tamu.empty:
                    st.dataframe(df_tamu, use_container_width=True)
                    csv_tamu = df_tamu.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Unduh Laporan Tamu (.csv)", data=csv_tamu, file_name=f"Laporan_Tamu_Stamet_Bima_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", type="primary")
                else:
                    st.info("Database Tamu masih kosong.")
            
            st.divider()
            
            st.subheader("2. Tabel Rekapitulasi Permohonan Data")
            with st.spinner("Sedang menarik data Permohonan dari Cloud..."):
                df_permohonan = ambil_data_google_sheets("Permohonan_Data")
                if not df_permohonan.empty:
                    st.dataframe(df_permohonan, use_container_width=True)
                    csv_permohonan = df_permohonan.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Unduh Laporan Permohonan (.csv)", data=csv_permohonan, file_name=f"Laporan_Permohonan_Data_Stamet_Bima_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", type="primary")
                else:
                    st.info("Database Permohonan Data masih kosong.")
                    
        elif st.session_state.admin_tab == "ARSIP DOKUMEN CLOUD":
            st.subheader("Galeri Berkas Pemohon Data (Cloud Storage)")
            st.write("Sistem otomatis menarik data dari 21 kolom pangkalan data Google Sheets.")
            st.write("")
            
            df_permohonan = ambil_data_google_sheets("Permohonan_Data")
            
            if not df_permohonan.empty:
                df_khusus = df_permohonan 
                
                if not df_khusus.empty:
                    kolom_nama = df_khusus.columns[1]
                    for index, row in df_khusus.iterrows():
                        with st.container(border=True):
                            col_info, col_links = st.columns([2, 1])
                            
                            kategori_text = row.iloc[4] if len(row) > 4 else "-"
                            nama_pemohon = row.iloc[1] if len(row) > 1 else "-"
                            waktu_reg = row.iloc[0] if len(row) > 0 else "-"
                            instansi_asal = row.iloc[3] if len(row) > 3 else "-"
                            wa_kontak = row.iloc[2] if len(row) > 2 else "-"
                            layanan_data = row.iloc[8] if len(row) > 8 else "-"
                            
                            current_st = row.iloc[18] if len(row) > 18 else "Menunggu Verifikasi Berkas"
                            waktu_up = row.iloc[19] if len(row) > 19 else waktu_reg
                            
                            with col_info:
                                st.markdown(f"### 👤 {nama_pemohon}")
                                st.write(f"**⏰ Waktu Registrasi:** {waktu_reg}")
                                st.write(f"**🏢 Asal Instansi:** {instansi_asal}")
                                st.write(f"**📱 Kontak WA:** {wa_kontak}")
                                st.write(f"**📂 Layanan Diminta:** {layanan_data}")
                                st.write(f"**🏷️ Kategori:** {kategori_text}")
                                
                                st.info(f"🚩 **Status Saat Ini:** {current_st}")
                                st.caption(f"Terakhir diupdate: {waktu_up}")
                            
                            with col_links:
                                st.markdown("**📂 Akses Berkas Pendukung:**")
                                
                                link_ktp = str(row.iloc[12]) if len(row) > 12 else "-"
                                link_permohonan = str(row.iloc[13]) if len(row) > 13 else "-"
                                link_pengantar = str(row.iloc[14]) if len(row) > 14 else "-"
                                link_pernyataan = str(row.iloc[15]) if len(row) > 15 else "-"
                                link_proposal = str(row.iloc[16]) if len(row) > 16 else "-"
                                link_skm_file = str(row.iloc[17]) if len(row) > 17 else "-"
                                
                                def show_link_button(label, url):
                                    if "http" in url:
                                        st.link_button(f"👁️ Lihat {label}", url, use_container_width=True)
                                    elif url and url != "-":
                                        st.caption(f"⚠️ Peringatan: {label} Tidak Ada/Valid")
                                        
                                show_link_button("KTP/Identitas", link_ktp)
                                show_link_button("Surat Permohonan", link_permohonan)
                                show_link_button("Surat Pengantar", link_pengantar)
                                show_link_button("Surat Pernyataan", link_pernyataan)
                                show_link_button("Proposal", link_proposal)
                                show_link_button("Bukti SKM", link_skm_file)
                    
                    st.divider()
                    st.markdown("### ⚙️ PANEL UPDATE STATUS PROGRESS DATA KONSUMEN")
                    st.caption("Ubah status di bawah ini agar pemohon dapat melihat progress pencarian datanya secara langsung.")
                    
                    list_nama_khusus = df_khusus[kolom_nama].tolist()
                    if list_nama_khusus:
                        with st.form("form_update_status"):
                            pilih_nama = st.selectbox("**Pilih Nama Pemohon Khusus:**", list_nama_khusus)
                            pilih_status = st.selectbox("**Set Status Progres Terbaru:**", [
                                "Menunggu Verifikasi Berkas", 
                                "Proses Penyiapan Data", 
                                "Menunggu Pembayaran PNBP",
                                "Selesai (Data Telah Dikirim / Siap Diambil)",
                                "Ditolak (Berkas Tidak Memenuhi Syarat)"
                            ])
                            
                            link_input = st.text_input("**Tautkan Link Google Drive Data Hasil (Hanya jika Selesai):**", placeholder="Paste URL file data di sini (https://...)")
                            
                            btn_simpan_status = st.form_submit_button("SIMPAN PEMBARUAN STATUS", type="primary")
                            
                        if btn_simpan_status:
                            with st.spinner("🔄 Mengupdate status di database cloud..."):
                                if update_status_sheets(pilih_nama, pilih_status, link_input):
                                    st.success(f"Berhasil mengubah status {pilih_nama} menjadi: {pilih_status}!")
                                    st.rerun()
                else:
                    st.info("Belum ada data pemohon khusus baru yang terekam.")
            else:
                st.info("Database Permohonan Data masih kosong.")
