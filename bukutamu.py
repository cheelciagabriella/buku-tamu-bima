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
# 2. KUSTOMISASI DESAIN WARNA (TEMA TERANG RESPONSIF)
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
    
    /* 3. Latar Belakang Halaman Utama (Gradasi Biru-Hijau Lembut) */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #e0f2fe 0%, #e8f5e9 100%) !important;
    }
    
    /* 4. Latar Belakang Menu Samping (Sidebar) tetap Biru Tua BMKG */
    [data-testid="stSidebar"] {
        background-color: #002B49 !important;
    }
    
    /* 5. Memastikan semua teks di Sidebar berwarna putih bersih */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span, [data-testid="stSidebar"] div {
        color: #ffffff !important;
    }
    
    /* 6. Mengatur kontainer formulir agar semi-transparan putih elegan */
    [data-testid="stForm"], .stElementContainer div[data-aria-stable="true"] {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #cbd5e1;
    }

    /* 7. Mengunci semua elemen teks halaman utama agar berwarna Biru Navy Gelap */
    section.main h1, section.main h2, section.main h3, section.main h4, section.main h5, section.main h6,
    section.main label, section.main p, section.main span,
    section.main div[data-testid="stMarkdownContainer"] p,
    section.main div[data-testid="stWidgetLabel"] p {
        color: #003366 !important;
    }
    
    /* Memastikan teks penjelasan atau caption tetap berwarna abu-abu tua */
    section.main .stCaptionContainer, section.main div[data-testid="stCaptionContainer"] p {
        color: #334155 !important;
    }
    
    /* Memastikan tulisan yang sedang diketik di dalam kolom input berwarna gelap tajam */
    section.main input {
        color: #000000 !important;
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
            st.success("PROSES SELESAI: Terima kasih atas partisipasi Anda dalam mengisi Buku Tamu dan Survei IKM Stasiun Meteorologi Bima.")
            st.info("Kontribusi penilaian Anda sangat berharga bagi peningkatan mutu dan akuntabilitas pelayanan publik kami.")
            
            st.write("")
            if st.button("KEMBALI KE HALAMAN UTAMA (REGISTRASI TAMU BARU)", type="primary", use_container_width=True):
                st.session_state.tamu_terdaftar = False
                st.session_state.nama_pendaftar = ""
                st.session_state.ikm_selesai = False
                st.rerun()

    # --- TAB 2: E-KATALOG PNBP TABEL DATA DINAMIS & RESPONSIF ---
    with tab2:
        st.subheader("KATALOG TARIF RESMI JASA DATA DAN INFORMASI (ROMAWI I)")
        st.info("Dasar Hukum: Peraturan Pemerintah Nomor 47 Tahun 2018 tentang Jenis dan Tarif atas Penerimaan Negara Bukan Pajak yang Berlaku pada BMKG.")
        
        # --- TABEL 1: KATEGORI I.A ---
        st.markdown("### **A. Informasi Khusus Meteorologi, Klimatologi, dan Geofisika**")
        
        raw_data_ia = {
            "Jenis Penerimaan Negara Bukan Pajak": [
                "1. Informasi Cuaca untuk Penerbangan",
                "2. Informasi Cuaca untuk Pelayaran",
                "3. Informasi Cuaca untuk Pelabuhan",
                "4. Informasi Cuaca untuk Pengeboran Lepas Pantai",
                "5.a. Analisis dan Prakiraan Hujan Bulanan",
                "5.b. Prakiraan Musim Kemarau",
                "5.c. Prakiraan Musim Hujan",
                "5.d. Atlas Kesesuaian Agroklimat",
                "5.e. Atlas Normal Temperatur Periode 1981-2010",
                "5.f. Atlas Windrose Wilayah Indonesia Periode 1981-2010",
                "5.g. Atlas Curah Hujan di Indonesia Rata-rata Periode 1981-2010",
                "6.a. Kualitas Udara: Particulate Matter (PM10)",
                "6.b. Kualitas Udara: Particulate Matter (PM2.5)",
                "6.c. Kualitas Udara: Sulfur Dioksida (SO2)",
                "6.d. Kualitas Udara: Nitrogen Oksida (NOx)",
                "6.e. Kualitas Udara: Ozon (O3)",
                "6.f. Kualitas Udara: Karbon Monoksida (CO)",
                "6.g. Kualitas Udara: Karbon Dioksida (CO2)",
                "6.h. Kualitas Udara: Methan (CH4)",
                "7.a. Peta Kegempaan",
                "7.b. Peta Percepatan Tanah",
                "8.a. Klaim Asuransi: Informasi Meteorologi",
                "8.b. Klaim Asuransi: Informasi Geofisika"
            ],
            "Satuan": [
                "per route unit", "per route per hari", "per lokasi per hari", "per dokumen per lokasi per hari",
                "per buku", "per buku", "per buku", "per buku", "per buku", "per buku", "per buku",
                "per stasiun per tahun", "per stasiun per tahun", "per stasiun per tahun", "per stasiun per tahun",
                "per stasiun per tahun", "per stasiun per tahun", "per sampel", "per sampel",
                "per provinsi per tahun", "per provinsi per tahun", "per lokasi per hari", "per lokasi per hari"
            ],
            "Tarif": [
                "4% dari biaya navigasi", "Rp 250.000,00", "Rp 225.000,00", "Rp 330.000,00",
                "Rp 65.000,00", "Rp 230.000,00", "Rp 230.000,00", "Rp 470.000,00", "Rp 1.500.000,00", "Rp 1.500.000,00", "Rp 1.500.000,00",
                "Rp 70.000,00", "Rp 70.000,00", "Rp 60.000,00", "Rp 60.000,00", "Rp 60.000,00", "Rp 60.000,00", "Rp 80.000,00", "Rp 80.000,00",
                "Rp 250.000,00", "Rp 250.000,00", "Rp 175.000,00", "Rp 185.000,00"
            ]
        }
        df_ia = pd.DataFrame(raw_data_ia)
        st.dataframe(df_ia, use_container_width=True, hide_index=True)
        
        st.write("")
        st.divider()
        st.write("")
        
        # --- TABEL 2: KATEGORI I.B ---
        st.markdown("### **B. Informasi Khusus Meteorologi, Klimatologi, dan Geofisika Sesuai Permintaan**")
        
        raw_data_ib = {
            "Jenis Penerimaan Negara Bukan Pajak": [
                "1.a. Cuaca Khusus untuk Kegiatan Olah Raga",
                "1.b. Cuaca Khusus untuk Kegiatan Komersial Outdoor/Indoor",
                "1.c. Informasi Radar Cuaca (per 10 menit)",
                "2.a.1) Peta Spasial Informasi Maritim",
                "2.a.2) Informasi Tabular dan Grafik Maritim",
                "2.b. Atlas Potensi Rawan Banjir",
                "3.a.1) Publikasi Informasi Perubahan Iklim dan Kualitas Udara",
                "3.a.2.a) Atlas Kerentanan Perubahan Iklim",
                "3.a.2.b) Atlas Potensi Energi Matahari di Indonesia",
                "3.a.2.c) Atlas Potensi Energi Angin di Indonesia",
                "3.b.1) Pengambilan Sampel: Sulfur Dioksida (SO2)",
                "3.b.2) Pengambilan Sampel: Nitrogen Oksida (NO2)",
                "3.b.3) Pengambilan Sampel: Karbon Dioksida (CO2)",
                "3.b.4) Pengambilan Sampel: Ozon (O3)",
                "3.b.5) Pengambilan Sampel: Suspended Particulate Matter (SPM)",
                "3.b.6) Pengambilan Sampel: Debu Particulate Matter (PM10)",
                "3.b.7) Pengambilan Sampel: Debu Particulate Matter (PM2.5)",
                "3.b.8) Pengambilan Sampel: Kimia Air Hujan",
                "3.b.9) Pengambilan Sampel: Methan (CH4)",
                "3.c.1) Pengujian Sampel: Sulfur Dioksida (SO2)",
                "3.c.2) Pengujian Sampel: Nitrogen Oksida (NO2)",
                "3.c.3) Pengujian Sampel: Karbon Dioksida (CO2)",
                "3.c.4) Pengujian Sampel: Ozon (O3)",
                "3.c.5) Pengujian Sampel: Suspended Particulate Matter (SPM)",
                "3.c.6) Pengujian Sampel: Debu Particulate Matter (PM10)",
                "3.c.7) Pengujian Sampel: Debu Particulate Matter (PM2.5)",
                "3.c.8) Pengujian Sampel: Kimia Air Hujan",
                "3.c.9) Pengujian Sampel: Methan (CH4)",
                "4.a. Buku dan Peta Variasi Magnet Bumi (Epoch)",
                "4.b. Peta Tingkat Kerawanan Petir",
                "4.c. Waktu Terbit dan Terbenam Matahari atau Bulan",
                "4.d. Buku Almanak BMKG",
                "4.e. Buku Peta Ketinggian Hilal",
                "4.f. Titik Dasar Gaya Berat (Gravitasi)",
                "4.g. Kejadian Petir"
            ],
            "Satuan": [
                "per lokasi per hari", "per lokasi per hari", "per data per lokasi", "per peta per bulan",
                "per tabel per bulan", "per atlas", "per buku", "per atlas", "per atlas", "per atlas",
                "per sampel", "per sampel", "per sampel", "per sampel", "per sampel", "per sampel",
                "per sampel", "per sampel", "per sampel", "per sampel", "per sampel", "per sampel",
                "per sampel", "per sampel", "per sampel", "per sampel", "per sampel", "per sampel",
                "per buku", "per lokasi per tahun", "per lokasi per tahun", "per buku per tahun",
                "per buku per tahun", "per titik dasar gaya berat", "per lokasi per hari"
            ],
            "Tarif": [
                "Rp 100.000,00", "Rp 100.000,00", "Rp 70.000,00", "Rp 300.000,00",
                "Rp 350.000,00", "Rp 350.000,00", "Rp 100.000,00", "Rp 450.000,00", "Rp 300.000,00", "Rp 300.000,00",
                "Rp 30.000,00", "Rp 30.000,00", "Rp 40.000,00", "Rp 30.000,00", "Rp 60.000,00", "Rp 60.000,00",
                "Rp 90.000,00", "Rp 230.000,00", "Rp 40.000,00", "Rp 20.000,00", "Rp 20.000,00", "Rp 30.000,00",
                "Rp 20.000,00", "Rp 50.000,00", "Rp 50.000,00", "Rp 70.000,00", "Rp 240.000,00", "Rp 30.000,00",
                "Rp 300.000,00", "Rp 200.000,00", "Rp 50.000,00", "Rp 150.000,00", "Rp 150.000,00", "Rp 150.000,00", "Rp 75.000,00"
            ]
        }
        df_ib = pd.DataFrame(raw_data_ib)
        st.dataframe(df_ib, use_container_width=True, hide_index=True)
        
        st.write("")
        
        # --- INFORMASI BEBAS BIAYA ---
        with st.container(border=True):
            st.markdown("### **KETENTUAN KHUSUS BEBAS BIAYA (TARIF RP 0,00 / GRATIS)**")
            st.markdown("""
            Seluruh tarif kategori Romawi I di atas dapat dibebaskan menjadi **Rp 0,00 (Gratis 100%)** apabila ditujukan demi pemenuhan kebutuhan non-komersial berikut:
            1. **Pendidikan dan Penelitian:** Guna pembuatan Tugas Akhir, Skripsi, Tesis, atau Disertasi pelajar/mahasiswa dengan menyertakan Surat Pengantar Resmi dari Sekolah/Kampus.
            2. **Keselamatan dan Penanggulangan:** Keperluan darurat evakuasi bencana alam, kegiatan sosial keagamaan non-profit, serta operasional kedaulatan TNI/POLRI.
            """)

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