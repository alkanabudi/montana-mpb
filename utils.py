import streamlit as st
import pandas as pd
import gspread
import base64
import json
import requests
import os
import io
from weasyprint import HTML
import google.generativeai as genai
from io import BytesIO
from pypdf import PdfReader
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
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
    if client is None: return pd.DataFrame()
    try:
        sheet = client.open("Daftar Penerimaan TAGIHAN MEMO PERINTAH BAYAR (Jawaban)").get_worksheet(0)
        df = get_clean_df(sheet.get_all_values())
        if "Waktu" in df.columns:
            df["Waktu"] = df["Waktu"].astype(str).str.strip()
            df['waktu_sort'] = pd.to_datetime(df["Waktu"], errors='coerce')
            df = df.sort_values(by="waktu_sort", ascending=False).drop(columns=['waktu_sort'])
            df["Waktu"] = df["Waktu"].replace(['None', 'nan', 'NaT'], '')
        if "NOMINAL TAGIHAN" in df.columns:
            df["NOMINAL TAGIHAN"] = to_numeric_clean(df["NOMINAL TAGIHAN"])
        return df
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=60)
def get_data_mpb_2025():
    client = get_gspread_client()
    if client is None: return pd.DataFrame()
    try:
        sheet = client.open("Memo Perintah Bayar 2025").get_worksheet(0)
        df = get_clean_df(sheet.get_all_values())
        for col in ["Nilai Tagihan", "NOMINAL TAGIHAN"]:
            if col in df.columns:
                df[col] = to_numeric_clean(df[col])
        return df
    except:
        return pd.DataFrame()

# --- 4. SIMPAN DATA ---
def save_data_to_google(data_dict):
    try:
        client = get_gspread_client()
        if client is None: return False, "Gagal koneksi."
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
    if df_dept.empty: return "<li>Belum ada data untuk dianalisis.</li>"
    total_memo = len(df_dept)
    nom_hist = df_dept["NOMINAL TAGIHAN"].sum() if "NOMINAL TAGIHAN" in df_dept.columns else 0
    if total_memo > 15:
        rekomendasi.append(f"<b>Volume Tinggi:</b> Terdeteksi {total_memo} memo periode ini.")
    if nom_hist > 500000000:
        rekomendasi.append(f"<b>Nominal Besar:</b> Total tagihan mencapai Rp {nom_hist:,.0f}.")
    if not rekomendasi:
        rekomendasi.append("<b>Normal:</b> Tren penerimaan stabil.")
    return "".join([f"<li>{r}</li>" for r in rekomendasi])

# --- 6. CETAK PDF (WEASYPRINT) ---
def create_pdf_report_mpb(df_for_report, selected_dept, periode_str):
    try:
        tgl_cetak = datetime.now().strftime("%d/%m/%Y %H:%M")
        total_memo = len(df_for_report)
        nom_total = df_for_report["NOMINAL TAGIHAN"].sum() if "NOMINAL TAGIHAN" in df_for_report.columns else 0
        total_nominal_str = f"Rp {nom_total:,.0f}".replace(",", ".")
        
        # Hitung Deviasi REVISI
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
        if not api_key: return "API Key missing."
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(f"Anda Montana AI Petrokimia. Jawab ringkas: {user_query}")
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"