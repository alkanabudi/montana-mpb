import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # --- LOGIKA SAKTI CLOUD VS LOKAL ---
    # Jika aplikasi jalan di internet (Cloud), dia pakai Secrets
    if "gcp_service_account" in st.secrets:
        creds_info = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(creds_info), scope)
    
    # Jika aplikasi jalan di laptop Mas Bram, dia cari file lokal
    else:
        # PENTING: Jangan pakai D:\Latihan, cukup nama filenya saja
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json.json", scope)
        except:
            creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        
    return gspread.authorize(creds)

@st.cache_data(ttl=600)
def get_data_from_google():
    try:
        client = get_gspread_client()
        nama_file = "Daftar Penerimaan TAGIHAN MEMO PERINTAH BAYAR (Jawaban)"
        sheet = client.open(nama_file).worksheet("Form Responses 1")
        list_of_lists = sheet.get_all_values()
        if not list_of_lists: return pd.DataFrame()
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
        list_of_lists = sheet.get_all_values()
        if not list_of_lists: return pd.DataFrame()
        header_idx = 0
        max_cols = 0
        for i, row in enumerate(list_of_lists[:20]):
            filled_cols = len([c for c in row if c.strip() != ""])
            if filled_cols > max_cols:
                max_cols = filled_cols
                header_idx = i
        headers = [h.strip() for h in list_of_lists[header_idx]]
        df = pd.DataFrame(list_of_lists[header_idx + 1:], columns=headers)
        df = df.loc[:, (df.columns != "") & (df.columns.notna())]
        df = df.replace('', pd.NA).dropna(how='all')
        if "Tanggal Dokumen Masuk Akuntansi" in df.columns:
            df = df[df["Tanggal Dokumen Masuk Akuntansi"].notna()]
        col_nilai = "Nilai Tagihan"
        if col_nilai in df.columns:
            df[col_nilai] = df[col_nilai].astype(str).str.replace(r'[^\d]', '', regex=True)
            df[col_nilai] = pd.to_numeric(df[col_nilai], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"Gagal koneksi ke Sheet MPB 2025: {e}")
        return pd.DataFrame()