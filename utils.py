import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Ambil data dasar dari Secrets yang sudah berhasil di-Save tadi
    creds_info = dict(st.secrets["gcp_service_account"])
    
    # Masukkan Private Key (Versi Bersih & Pad Kelipatan 4)
    creds_info["private_key"] = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDys2JW+cCtR/79\n+Jn1IUNAyQYmsbqzGCUVEZSNZe09AfUajwwvPTChAo3CnGv3x2BfHDOgDye0w6d1\nUhs9RSA2bDof0ki6LLiCyqPsYMjMeUjJvt5TWQu+hiLTb7ujSwu20fb0U7nKtLGI\necO8vBdGutzSKi9IAUuQEq7Pj5sK76WFVizS7foicuv0OGXNYTHxzEne83kjrmKV\nSpD+pig1fLP+4vJ2WoFUUxZzIqFt2ctTCj2kDG/gv5kiSwjjoHPTOgV9/h1GfS93\nXsJiHcDkxz2yxmWXSKBp0vAQI6xz1B01iEy95dgo3C90ANhmR4ctiqEEQcsEULA5\n2GFfdP9DAgMBAAECggEABzKS/HUNrwy81eVVE4ZluOhGbNp8xDxcEuLhladZd6OQ\ngf78UWCcLnETYAkgYyUyZJsegNLSPDO2XKTGSSvhfolm2HQsd7D8Hh8lxIOL/qWH\nS8xfJYp+W/SKs5LTbQVO4A4cAzc5AgmFhAmeH28xtYVruaPcoRnlTaPLoWGd4jGD\n3Y/6ubG/DT9D6smiIqHJ29J/kfFEK8AJ9NYdat42GpVEKTZvw17rsBhrKwl5i3PA\nEELIi/Ea111tuq96f+DdoiQVrlt+TZ6yNN3MEx68rlnCkQFRvFuECrzruxK4DOgr\nkHzaXivqOvC25BXJNyrUpQGK32CxrOMLDRa7udi2oQKBgQD6OFSfeSbAitKqtkWO\boTlQnmW6Wt84Jwoh+MR3oPkhcinMfZMkD+WBPTNzB/SvIMSA1Y/ALvKfb8BG1p+\nkf8bDRUIsbKn3y0Wno0MMstu2AvGo6D0JgkPlRS5/eN7Wt8Wu8ksRgraql0mcSh5\nOD2Bf6De7roasv02KrCjHdKW8QKBgQD4TpaZJ3AoBLh4EQ4PbYwrlM0ReSzJAN2U\nM0qi13mwqV6s1EJq1w5N6C7LKSzEXz2cbScG9BWNhZbepk7Jg7WoYt4XU+IS5wpF\nzQ7uCx/XyWLP541mwm17bAPAiyUKvff0fovaDZ4CVIrfz3FxZoVCFVebUEawbehv\n7/K0aghBcwKBgBn5TPd86QPlpTapUxEU8eCmhN6gflLpMeyXJoANXB2VsZ2BdzK9\naoxVGWBfhxImFWkCRaqmldfQM8qWn08yMowJUJylbYk1hoWpkbSpdSqdbKODCsst\Q5WFgTBJZZrBdRT0C074Olo2gxLhfjUPHHtb10Qs/c6Vs+kyh0F3cAvRAoGAYVaV\nbMZsDhQDqHWvGFcuWqtDVHU3HDito/oTaRClEJ7kkUXIH4/ceKfrKBMlDHn1cgvL\n/8rRZCAZS4DQY+iw3qibPXPRrO1LNp+zGZfczL+Sb8Pqx3yyZG6sbd9eDv73Y63z\n7u/loC46HpB4fSbeWFB7flQS0fjT5IWglB74y4cCgYEAjSPT8Sjm4CPbcph3jBIa\nkfZvWn92Ovf1ZmAxKIPDRYySw8RnfS+Jtz4WMaSGD8thAH3MqGXTeZa9/XGnD2g8\nbCkJcJ/9mb6SPLIFMbv4xTtRUYDN2pzxo5tLIMnzfBHXhRiH8jDae3xzJ0gh4HO1\rfp2LBqdxuEIF62E+mUeUcE=\n-----END PRIVATE KEY-----\n"

    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
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