import streamlit as st
from datetime import datetime
from utils import save_data_to_google

# 1. Konfigurasi Layout (Diletakkan paling atas)
st.markdown("<style>.block-container {max-width: 95% !important; padding-top: 2rem;}</style>", unsafe_allow_html=True)

# Judul Halaman
st.title("➕ Input Tagihan MPB Baru")

# --- MENU PARAMETER PERHATIAN (HTML CLEAN VERSION) ---
with st.expander("ℹ️ INFO PENTING: Syarat Kelengkapan Tagihan (Klik untuk Lihat)", expanded=False):
    st.markdown("""
    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #4da3ff;">
        <h4 style="color: #1e1e1e; margin-top: 0;">⚠️ Perhatikan Sebelum Submit Tagihan MPB:</h4>
        <table style="width:100%; border-collapse: collapse; color: #1e1e1e; background-color: white;">
            <tr style="background-color: #4da3ff; color: white;">
                <th style="padding: 10px; border: 1px solid #ddd;">Kategori</th>
                <th style="padding: 10px; border: 1px solid #ddd;">Ketentuan</th>
                <th style="padding: 10px; border: 1px solid #ddd;">Status</th>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><b>Asal Departemen</b></td>
                <td style="padding: 8px; border: 1px solid #ddd;">Wajib sesuai Invoice & PO</td>
                <td style="padding: 8px; border: 1px solid #ddd; color: #007bff;"><b>Wajib</b></td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><b>Nominal Tagihan</b></td>
                <td style="padding: 8px; border: 1px solid #ddd;">Wajib sesuai Invoice & PO</td>
                <td style="padding: 8px; border: 1px solid #ddd; color: #007bff;"><b>Wajib</b></td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><b>Nomor Memo</b></td>
                <td style="padding: 8px; border: 1px solid #ddd;">Format: XXX/B/KU.00.0x/...</td>
                <td style="padding: 8px; border: 1px solid #ddd; color: #007bff;"><b>Wajib</b></td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><b>Nama PIC</b></td>
                <td style="padding: 8px; border: 1px solid #ddd;">Nama PIC dan ext kantor/no WA</td>
                <td style="padding: 8px; border: 1px solid #ddd; color: #007bff;"><b>Wajib</b></td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><b>Lampiran PDF</b></td>
                <td style="padding: 8px; border: 1px solid #ddd;">Maksimal 10MB (Jelas/Scan)</td>
                <td style="padding: 8px; border: 1px solid #ddd; color: #ff8c00;"><b>Tahap Pengembangan</b></td>
            </tr>
        </table>
        <p style="font-size: 0.85em; margin-top: 10px; color: #555;">
            *Pastikan semua syarat dan ketentuan di atas sudah terpenuhi sebelum menekan tombol <b>SUBMIT DATA</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.write("") 

# --- FORM INPUT ---
with st.form("form_input_mpb", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        asal_dept = st.text_input("ASAL DEPARTEMEN", placeholder="Contoh: KOMUNIKASI KORPORAT")
        no_memo = st.text_input("No Memo", placeholder="Contoh: 41191/B/KU...")
        
    with col2:
        nominal = st.number_input("NOMINAL TAGIHAN", min_value=0, step=1)
        pic = st.text_input("Nama PIC (Person In Charge) & EXT", placeholder="Nama dan nomor EXT")

    submitted = st.form_submit_button("SUBMIT DATA", use_container_width=True, type="primary")

    if submitted:
        if asal_dept and no_memo and pic and nominal > 0:
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            # Data Dictionary untuk utils.py
            data_baru = {
                "Waktu": timestamp,
                "ASAL DEPARTEMEN": asal_dept.upper(),
                "No Memo": no_memo,
                "NOMINAL TAGIHAN": nominal,
                "PIC": pic
            }
            
            success, msg = save_data_to_google(data_baru)
            
            if success:
                st.success(f"✅ Data Memo **{no_memo}** berhasil tersimpan!")
                st.balloons()
                st.cache_data.clear()
            else:
                st.error(f"❌ Gagal menyimpan: {msg}")
        else:
            st.warning("⚠️ Mohon lengkapi semua kolom dan pastikan Nominal lebih dari 0.")

# --- FOOTER SIDEBAR ---
st.sidebar.markdown("---")
st.sidebar.markdown("<div style='text-align: center; color: grey; font-size: 0.8em;'>Developed by <b>Alkana</b><br>© 2026 PT Petrokimia Gresik</div>", unsafe_allow_html=True)