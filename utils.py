import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Helper untuk koneksi agar tidak nulis berulang-ulang
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # 1. Coba baca dari Streamlit Secrets (untuk Online/Cloud)
    if "gcp_service_account" in st.secrets:
        creds_info = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(creds_info), scope)
    
    # 2. Jika tidak ada Secrets, baca dari file lokal (untuk di laptop Mas Bram)
    else:
        # Sesuaikan nama file JSON-nya dengan yang ada di folder laptop Mas Bram
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json.json", scope)
        
    return gspread.authorize(creds)

@st.cache_data(ttl=600)
def get_data_from_google():
    try:
        client = get_gspread_client()
        nama_file = "Daftar Penerimaan TAGIHAN MEMO PERINTAH BAYAR (Jawaban)"
        sheet = client.open(nama_file).worksheet("Form Responses 1")
        
        list_of_lists = sheet.get_all_values()
        df = pd.DataFrame(list_of_lists[1:], columns=list_of_lists[0])
        df = df.loc[:, df.columns != '']
        
        if "NOMINAL TAGIHAN" in df.columns:
            df["NOMINAL TAGIHAN"] = df["NOMINAL TAGIHAN"].astype(str).str.replace('.', '', regex=False)
            df["NOMINAL TAGIHAN"] = pd.to_numeric(df["NOMINAL TAGIHAN"], errors='coerce').fillna(0)
            
        return df
    except Exception as e:
        st.error(f"Error Raw Data: {e}")
        return pd.DataFrame()

def save_data_to_google(data_row):
    try:
        client = get_gspread_client()
        nama_file = "Daftar Penerimaan TAGIHAN MEMO PERINTAH BAYAR (Jawaban)"
        sheet = client.open(nama_file).worksheet("Form Responses 1")
        sheet.append_row(data_row)
        return True
    except Exception as e:
        st.error(f"Gagal menyimpan ke Google Sheets: {e}")
        return False

def get_data_mpb_2025():
    try:
        client = get_gspread_client()
        nama_file = "Memo Perintah Bayar 2025"
        sheet = client.open(nama_file).worksheet("MPB")
        
        # Ambil semua data
        list_of_lists = sheet.get_all_values()
        
        if not list_of_lists:
            return pd.DataFrame()

        # --- LOGIKA DETEKSI HEADER BARU ---
        # Mencari baris mana yang punya kolom terbanyak yang berisi teks
        # Ini lebih aman daripada mencari kata kunci "Unit Kerja"
        header_idx = 0
        max_cols = 0
        for i, row in enumerate(list_of_lists[:20]): # Cek 20 baris pertama saja
            # Hitung berapa banyak kolom yang tidak kosong di baris ini
            filled_cols = len([c for c in row if c.strip() != ""])
            if filled_cols > max_cols:
                max_cols = filled_cols
                header_idx = i

        headers = [h.strip() for h in list_of_lists[header_idx]]
        data = list_of_lists[header_idx + 1:]
        
        df = pd.DataFrame(data, columns=headers)

        # --- CLEANING ---
        # 1. Buang kolom tanpa nama
        df = df.loc[:, (df.columns != "") & (df.columns.notna())]
        
        # 2. Buang baris yang benar-benar kosong
        df = df.replace('', pd.NA).dropna(how='all')

        # 3. Filter agar hanya baris yang ada 'Nomor' atau 'Tanggal' yang diambil
        # (Menghindari baris footer/catatan di bawah tabel GSheet)
        if "Tanggal Dokumen Masuk Akuntansi" in df.columns:
            df = df[df["Tanggal Dokumen Masuk Akuntansi"].notna()]
        
        # 4. Konversi Nilai Tagihan
        col_nilai = "Nilai Tagihan"
        if col_nilai in df.columns:
            df[col_nilai] = df[col_nilai].astype(str).str.replace(r'[^\d]', '', regex=True)
            df[col_nilai] = pd.to_numeric(df[col_nilai], errors='coerce').fillna(0)
            
        return df

    except Exception as e:
        st.error(f"Gagal koneksi ke Sheet MPB 2025: {e}")
        return pd.DataFrame()