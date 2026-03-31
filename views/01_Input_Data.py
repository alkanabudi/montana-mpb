import streamlit as st
from datetime import datetime
from utils import save_data_to_google

# Judul Halaman
st.title("➕ Input Tagihan MPB Baru")

# --- MENU PARAMETER PERHATIAN ---
with st.expander("ℹ️ INFO PENTING: Parameter & Kelengkapan Tagihan (Klik untuk Lihat)", expanded=False):
    st.markdown("""
    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #4da3ff;">
        <h4 style="color: #1e1e1e; margin-top: 0;">⚠️ Perhatikan Sebelum Submit Tagihan MPB:</h4>
        <table style="width:100%; border-collapse: collapse; color: #1e1e1e;">
            <tr style="background-color: #4da3ff; color: white;">
                <th style="padding: 10px; border: 1px solid #ddd;">Kategori</th>
                <th style="padding: 10px; border: 1px solid #ddd;">Syarat</th>
                <th style="padding: 10px; border: 1px solid #ddd;">Status</th>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><b>Nominal Tagihan</b></td>
                <td style="padding: 8px; border: 1px solid #ddd;">Wajib sesuai Invoice & PO</td>
                <td style="padding: 8px; border: 1px solid #ddd; color: green;">Wajib</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><b>Nomor Memo</b></td>
                <td style="padding: 8px; border: 1px solid #ddd;">Format: XXX/B/KU.00.0x/...</td>
                <td style="padding: 8px; border: 1px solid #ddd; color: orange;">Wajib</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><b>Lampiran PDF</b></td>
                <td style="padding: 8px; border: 1px solid #ddd;">Maksimal 10MB (Jelas/Scan)</td>
                <td style="padding: 8px; border: 1px solid #ddd; color: orange;">Wajib</td>
            </tr>
             <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><b>Verifikasi PIC</b></td>
                <td style="padding: 8px; border: 1px solid #ddd;">Nama Terdaftar di Database</td>
                <td style="padding: 8px; border: 1px solid #ddd; color: blue;">Normal</td>
            </tr>
        </table>
        <p style="font-size: 0.85em; margin-top: 10px; color: #555;">
            *Pastikan semua parameter di atas sudah terpenuhi sebelum menekan tombol <b>SIMPAN</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.write("") # Memberi jarak sedikit ke form bawah
# --- FORM INPUT ---
with st.form("form_input_mpb", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        # Kolom B: ASAL DEPARTEMEN
        asal_dept = st.text_input("ASAL DEPARTEMEN", placeholder="Contoh: KOMUNIKASI KORPORAT")
        # Kolom C: No Memo
        no_memo = st.text_input("No Memo", placeholder="Contoh: 41191/B/KU...")
        
    with col2:
        # Kolom D: NOMINAL TAGIHAN
        nominal = st.number_input("NOMINAL TAGIHAN", min_value=0, step=1)
        # Kolom E: Nama PIC
        pic = st.text_input("Nama PIC (Person In Charge) & EXT", placeholder="Nama dan nomor EXT")

    # Tombol Submit
    submitted = st.form_submit_button("SUBMIT DATA", use_container_width=True, type="primary")

    if submitted:
        # Validasi sederhana
        if asal_dept and no_memo and pic:
            # Kolom A: Waktu (Standar Timestamp)
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            # --- DATA HANYA SAMPAI KOLOM E ---
            # Kita tidak mengirim kolom F dan G agar Dropdown di GSheets tetap utuh
            data_baru = [
                timestamp,          # Kolom A
                asal_dept.upper(),  # Kolom B
                no_memo,            # Kolom C
                nominal,            # Kolom D
                pic                 # Kolom E
            ]
            
            # Eksekusi simpan ke baris terakhir
            hasil = save_data_to_google(data_baru)  
            
            if hasil:
                st.success(f"✅ Data Memo **{no_memo}** berhasil tersimpan! ")
                st.balloons()
            else:
                st.error("❌ Gagal menyimpan. Silakan cek koneksi internet atau permission spreadsheet.")
        else:
            st.warning("⚠️ Mohon lengkapi Departemen, Nomor Memo, dan PIC.")

# --- CSS WIDE LAYOUT ---
st.markdown("<style>.block-container {max-width: 95% !important; padding-top: 2rem;}</style>", unsafe_allow_html=True)

# --- FOOTER SIDEBAR ---
st.sidebar.markdown("---")
st.sidebar.markdown("<div style='text-align: center; color: grey; font-size: 0.8em;'>Developed by <b>Alkana</b><br>© 2026 PT Petrokimia Gresik</div>", unsafe_allow_html=True)