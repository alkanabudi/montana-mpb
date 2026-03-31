import streamlit as st
import pandas as pd
import gspread
import base64
import json
import requests
import google.generativeai as genai
from io import BytesIO
from pypdf import PdfReader
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. KONEKSI GOOGLE SHEETS ---
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        encoded_key = st.secrets["gcp_service_account"]["encoded_key"].strip()
        decoded_bytes = base64.b64decode(encoded_key)
        creds_info = json.loads(decoded_bytes.decode("utf-8"))
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        return gspread.authorize(creds)
    except Exception:
        return None

# --- 2. PEMBERSIH DATA ---
def to_numeric_clean(series):
    s = series.astype(str).str.replace('Rp', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '', regex=False).str.strip()
    return pd.to_numeric(s, errors='coerce').fillna(0)

def fix_duplicate_columns(headers):
    clean_headers = []
    for i, h in enumerate(headers):
        new_h = h.strip() if h.strip() != "" else f"Kolom_{i}"
        if new_h in clean_headers:
            new_h = f"{new_h}_{i}"
        clean_headers.append(new_h)
    return clean_headers

# --- FUNGSI PEMBERSIH HEADER (Hanya Ambil yang Ada Namanya) ---
def get_clean_df(list_of_lists):
    if not list_of_lists or len(list_of_lists) <= 1:
        return pd.DataFrame()
        
    raw_headers = list_of_lists[0]
    # Hanya ambil indeks kolom yang judulnya TIDAK KOSONG
    valid_col_indices = [i for i, h in enumerate(raw_headers) if h.strip() != ""]
    
    # Ambil nama header yang valid saja
    clean_headers = [raw_headers[i].strip() for i in valid_col_indices]
    
    # Ambil data hanya untuk indeks kolom yang valid tadi
    data_rows = []
    for row in list_of_lists[1:]:
        # Pastikan row memiliki jumlah kolom yang cukup, jika tidak beri string kosong
        filtered_row = [row[i] if i < len(row) else "" for i in valid_col_indices]
        data_rows.append(filtered_row)
        
    return pd.DataFrame(data_rows, columns=clean_headers)

# --- UPDATE FUNGSI AMBIL DATA ---
@st.cache_data(ttl=60)
def get_data_from_google():
    client = get_gspread_client()
    if client is None: return pd.DataFrame()
    try:
        sheet = client.open("Daftar Penerimaan TAGIHAN MEMO PERINTAH BAYAR (Jawaban)").get_worksheet(0)
        df = get_clean_df(sheet.get_all_values())
        
        # --- LOGIKA PENGURUTAN WAKTU ---
        if "Waktu" in df.columns:
            # Ubah kolom Waktu ke format datetime agar bisa diurutkan dengan benar
            df["Waktu"] = pd.to_datetime(df["Waktu"], errors='coerce')
            # Urutkan berdasarkan Waktu secara descending (Terbaru di atas)
            df = df.sort_values(by="Waktu", ascending=False)
            # Kembalikan ke format teks biasa agar enak dilihat di tabel
            df["Waktu"] = df["Waktu"].dt.strftime('%d/%m/%Y %H:%M:%S')
        
        if "NOMINAL TAGIHAN" in df.columns:
            df["NOMINAL TAGIHAN"] = to_numeric_clean(df["NOMINAL TAGIHAN"])
            
        return df
    except Exception as e:
        st.error(f"Gagal urutkan data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def get_data_mpb_2025():
    client = get_gspread_client()
    if client is None: return pd.DataFrame()
    try:
        sheet = client.open("Memo Perintah Bayar 2025").get_worksheet(0)
        df = get_clean_df(sheet.get_all_values())
        
        # Bersihkan nominal tanpa menambah kolom baru jika tidak perlu
        for col in ["Nilai Tagihan", "NOMINAL TAGIHAN"]:
            if col in df.columns:
                df[col] = to_numeric_clean(df[col])
        return df
    except:
        return pd.DataFrame()

def get_montana_chat_response(user_query):
    try:
        api_key = st.secrets.get("gemini_api_key")
        if not api_key: return "Kunci API tidak ditemukan."
        genai.configure(api_key=api_key)

        # --- LANGKAH PENTING: Kasih nilai awal agar tidak error ---
        text_knowledge = "Data SOP tidak tersedia sementara." 
        
        file_id = "1jX-yVKyMmIuOOdx7Z-qpEtTYzn_RhNu1" 
        url = f'https://drive.google.com/uc?id={file_id}&export=download'
        
        try:
            resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            if resp.status_code == 200:
                pdf_file = BytesIO(resp.content)
                reader = PdfReader(pdf_file)
                extracted_text = ""
                for page in reader.pages[:5]:
                    extracted_text += page.extract_text() or ""
                
                # Jika berhasil ekstrak, baru timpa variabel text_knowledge
                if extracted_text.strip():
                    text_knowledge = extracted_text
        except Exception:
            # Jika Drive gagal diakses, Montana tetap punya jawaban default
            pass

        # Panggil Model (Gunakan yang paling standar)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"Anda Montana, AI Petrokimia. Jawab ringkas dari data ini: {text_knowledge[:10000]}\n\nUser: {user_query}"
        response = model.generate_content(prompt)
        
        return response.text

    except Exception as e:
        return f"Kendala teknis: {str(e)}"