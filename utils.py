import streamlit as st
import pandas as pd
import gspread
import base64
import json
import os
import io
import re
from io import BytesIO
from pypdf import PdfReader
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from google.oauth2.service_account import Credentials
import google.generativeai as genai

# Proteksi WeasyPrint agar tidak memicu crash jika lib C Linux tidak terpasang
try:
    from weasyprint import HTML
except (ImportError, OSError):
    HTML = None

# --- 1. KONEKSI GOOGLE SHEETS (MENGGUNAKAN GOOGLE-AUTH TERSTANDAR) ---
def get_gspread_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    try:
        # 1. Prioritas Cloud (Streamlit Secrets)
        if "gcp_service_account" in st.secrets:
            creds_info = dict(st.secrets["gcp_service_account"])
            
            # Dukungan jika format base64
            if "encoded_key" in creds_info:
                decoded_bytes = base64.b64decode(creds_info["encoded_key"].strip())
                creds_info = json.loads(decoded_bytes.decode("utf-8"))
            
            # Bersihkan dan perbaiki newline string private_key jika rusak oleh parser TOML
            if "private_key" in creds_info:
                key = str(creds_info["private_key"]).strip()
                if "\\n" in key:
                    key = key.replace("\\n", "\n")
                creds_info["private_key"] = key

            credentials = Credentials.from_service_account_info(creds_info, scopes=scopes)
            return gspread.authorize(credentials)
        
        # 2. Prioritas Lokal (file newcredentials.json di VS Code)
        elif os.path.exists("newcredentials.json"):
            credentials = Credentials.from_service_account_file("newcredentials.json", scopes=scopes)
            return gspread.authorize(credentials)
            
        print("Peringatan: Secrets [gcp_service_account] maupun file newcredentials.json tidak ditemukan.")
        return None
    except Exception as e:
        print(f"Error autentikasi gspread client: {e}")
        return None

# --- 2. PEMBERSIH DATA ---
def to_numeric_clean(series):
    s = series.astype(str).str.replace('Rp', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '', regex=False).str.strip()
    return pd.to_numeric(s, errors='coerce').fillna(0)

def get_clean_df(list_of_lists):
    if not list_of_lists or len(list_of_lists) <= 1:
        return pd.DataFrame()
    raw_headers = list_of_lists[0]
    valid_col_indices = [i for i, h in enumerate(raw_headers) if h.strip() != ""]
    clean_headers = [raw_headers[i].strip() for i in valid_col_indices]
    data_rows = []
    for row in list_of_lists[1:]:
        filtered_row = [row[i] if i < len(row) else "" for i in valid_col_indices]
        data_rows.append(filtered_row)
    return pd.DataFrame(data_rows, columns=clean_headers)

# --- 3. AMBIL DATA ---
@st.cache_data(ttl=60)
def get_data_from_google():
    client = get_gspread_client()
    if client is None:
        return pd.DataFrame()
    try:
        sheet = client.open("Daftar Penerimaan TAGIHAN MEMO PERINTAH BAYAR (Jawaban)").get_worksheet(0)
        df = get_clean_df(sheet.get_all_values())
        if not df.empty:
            if "Waktu" in df.columns:
                df["Waktu"] = df["Waktu"].astype(str).str.strip()
                df['waktu_sort'] = pd.to_datetime(df["Waktu"], errors='coerce')
                df = df.sort_values(by="waktu_sort", ascending=False).drop(columns=['waktu_sort'])
                df["Waktu"] = df["Waktu"].replace(['None', 'nan', 'NaT'], '')
            if "NOMINAL TAGIHAN" in df.columns:
                df["NOMINAL TAGIHAN"] = to_numeric_clean(df["NOMINAL TAGIHAN"])
        return df
    except Exception as e:
        print(f"Error get_data_from_google: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def get_data_mpb_2025():
    client = get_gspread_client()
    if client is None:
        return pd.DataFrame()
    try:
        sheet = client.open("Memo Perintah Bayar 2025").get_worksheet(0)
        df = get_clean_df(sheet.get_all_values())
        if not df.empty:
            for col in ["Nilai Tagihan", "NOMINAL TAGIHAN"]:
                if col in df.columns:
                    df[col] = to_numeric_clean(df[col])
        return df
    except Exception as e:
        print(f"Error get_data_mpb_2025: {e}")
        return pd.DataFrame()

# --- 4. SIMPAN DATA ---
def save_data_to_google(data_dict):
    try:
        client = get_gspread_client()
        if client is None:
            return False, "Gagal koneksi ke Google Sheets."
        spreadsheet = client.open("Daftar Penerimaan TAGIHAN MEMO PERINTAH BAYAR (Jawaban)")
        sheet = spreadsheet.get_worksheet(0)
        existing_data = sheet.get_all_values()
        next_row = len(existing_data) + 1
        row_to_add = list(data_dict.values())
        sheet.insert_row(row_to_add, next_row)
        return True, "Data berhasil tersimpan!"
    except Exception as e:
        return False, f"Gagal simpan: {str(e)}"

# --- 5. LOGIKA REKOMENDASI ---
def generate_rekomendasi_mpb(df_dept):
    rekomendasi = []
    if df_dept.empty:
        return "<li>Belum ada data untuk dianalisis.</li>"
    total_memo = len(df_dept)
    nom_hist = df_dept["NOMINAL TAGIHAN"].sum() if "NOMINAL TAGIHAN" in df_dept.columns else 0
    if total_memo > 15:
        rekomendasi.append(f"<b>Volume Tinggi:</b> Terdeteksi {total_memo} memo periode ini.")
    if nom_hist > 500000000:
        rekomendasi.append(f"<b>Nominal Besar:</b> Total tagihan mencapai Rp {nom_hist:,.0f}.")
    if not rekomendasi:
        rekomendasi.append("<b>Normal:</b> Tren penerimaan stabil.")
    return "".join([f"<li>{r}</li>" for r in rekomendasi])

# --- 6. CETAK PDF (WEASYPRINT AMAN) ---
def create_pdf_report_mpb(df_for_report, selected_dept, periode_str):
    if HTML is None:
        return None, "Fitur cetak PDF WeasyPrint sedang nonaktif di cloud (keterbatasan pustaka sistem)."

    try:
        tgl_cetak = datetime.now().strftime("%d/%m/%Y %H:%M")
        total_memo = len(df_for_report)
        nom_total = df_for_report["NOMINAL TAGIHAN"].sum() if "NOMINAL TAGIHAN" in df_for_report.columns else 0
        total_nominal_str = f"Rp {nom_total:,.0f}".replace(",", ".")
        
        verifikasi_deviasi = 0
        if 'VERIFIKASI' in df_for_report.columns:
            verifikasi_deviasi = len(df_for_report[df_for_report['VERIFIKASI'].astype(str).str.upper() == 'REVISI'])
        
        status_performa = "NORMAL"
        status_class = "selesai"
        if verifikasi_deviasi > 0:
            status_performa = "WASPADA"
            status_class = "proses"

        data_rows = df_for_report.copy()
        if "NOMINAL TAGIHAN" in data_rows.columns:
            data_rows["NOMINAL TAGIHAN"] = data_rows["NOMINAL TAGIHAN"].apply(lambda x: f"{x:,.0f}".replace(",", "."))
        data_rows_list = data_rows.to_dict('records')
        rekomendasi_html = generate_rekomendasi_mpb(df_for_report)

        template_dir = os.path.join(os.getcwd(), 'views')
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template('report_template.html')

        html_out = template.render(
            departemen=selected_dept, periode=periode_str, total_memo=total_memo,
            total_nominal=total_nominal_str, tgl_cetak=tgl_cetak, data_rows=data_rows_list,
            verifikasi_deviasi=verifikasi_deviasi, status_performa=status_performa, 
            status_class=status_class, rekomendasi_html=rekomendasi_html
        )

        pdf_out = HTML(string=html_out).write_pdf()
        return pdf_out, None
    except Exception as e:
        return None, str(e)

# --- 7. AI MONTANA ---
def get_montana_chat_response(user_query):
    try:
        api_key = st.secrets.get("gemini_api_key")
        if not api_key:
            return "API Key missing."
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"Anda Montana AI Petrokimia. Jawab ringkas: {user_query}")
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# --- 8. EKSTRAKSI & VERIFIKASI MEMO PDF ---
def extract_and_verify_memo_pdf(pdf_file):
    extracted_data = {
        "no_memo": None,
        "tanggal_memo": None,
        "nominal": 0,
        "pic": None,
        "departemen": None,
        "raw_text": ""
    }
    
    verification_checks = {
        "format_memo": False,
        "nominal_valid": False,
        "ttd_terdeteksi": False,
        "ext_pic_terdeteksi": False
    }

    try:
        reader = PdfReader(pdf_file)
        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
        
        extracted_data["raw_text"] = full_text

        # 1. Ekstrak Nomor Memo
        memo_pattern = r'(\d+/[A-Z0-9\.-]+/\d{4}|\d+/[A-Z0-9\.-]+/[A-Z0-9\.-]+/\d{4})'
        memo_match = re.search(memo_pattern, full_text)
        if memo_match:
            extracted_data["no_memo"] = memo_match.group(1)
            verification_checks["format_memo"] = True

        # 2. Ekstrak Nominal Tagihan
        nominal_pattern = r'(?:Rp\.?|IDR)\s*([\d\.,]+)'
        nominal_match = re.search(nominal_pattern, full_text, re.IGNORECASE)
        if nominal_match:
            raw_nom = nominal_match.group(1).replace('.', '').replace(',', '')
            if raw_nom.isdigit():
                extracted_data["nominal"] = float(raw_nom)
                if extracted_data["nominal"] > 0:
                    verification_checks["nominal_valid"] = True

        # 3. Pengecekan SOP (Otorisasi & PIC)
        if re.search(r'(Tanda Tangan|Signed|Approve|Disetujui|Menyetujui)', full_text, re.IGNORECASE):
            verification_checks["ttd_terdeteksi"] = True
            
        if re.search(r'(EXT|Ext\.|Extension|Hp|Telp)', full_text, re.IGNORECASE):
            verification_checks["ext_pic_terdeteksi"] = True

        return extracted_data, verification_checks, None

    except Exception as e:
        return None, None, str(e)