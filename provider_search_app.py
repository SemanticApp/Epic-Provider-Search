import os
import glob
import pandas as pd
import streamlit as st
import subprocess

# CONFIG: Directory where your feed lives
DATA_DIR = r"Q:\Kyruus\qceiawfbs001.ucsfmedicalcenter.org\001.ucsfm"

def vpn_connected():
    """
    Checks if GlobalProtect VPN is running.
    This uses Windows 'tasklist' to look for PanGPA (GlobalProtect agent).
    """
    try:
        result = subprocess.run(["tasklist"], capture_output=True, text=True)
        return "PanGPA.exe" in result.stdout
    except Exception:
        return False

def get_latest_file():
    """Get the most recent UCSF_ECHO csv file from the directory."""
    files = glob.glob(os.path.join(DATA_DIR, "UCSF_ECHO_*.CSV"))
    if not files:
        return None
    latest_file = max(files, key=os.path.getmtime)
    return latest_file

def load_data():
    """Load latest CSV into dataframe."""
    file = get_latest_file()
    if file:
        df = pd.read_csv(file, dtype=str)  # read everything as text to avoid parsing errors
        return df, file
    return None, None

# ---------------- STREAMLIT APP ----------------
st.set_page_config(page_title="Provider Search", layout="wide")

st.title("🔍 UCSF Provider Search")

# VPN Check
if not vpn_connected():
    st.error("❌ GlobalProtect VPN is NOT connected. Please log in before using this app.")
    st.stop()
else:
    st.success("✅ GlobalProtect VPN is active")

# Load data
df, latest_file = load_data()

if df is None:
    st.error("No UCSF_ECHO CSV files found in directory.")
    st.stop()

st.caption(f"Loaded file: **{os.path.basename(latest_file)}** ({len(df)} records)")

# Search box
search_mode = st.radio("Search by:", ["Name", "NPI"])
query = st.text_input("Enter search term:")

if query:
    if search_mode == "Name":
        results = df[df.apply(lambda row: query.lower() in str(row).lower(), axis=1)]
    else:  # NPI
        if "NPI" not in df.columns:
            st.error("The CSV file does not contain an 'NPI' column.")
        else:
            results = df[df['NPI'].astype(str).str.contains(query, case=False, na=False)]

    if not results.empty:
        st.dataframe(results, use_container_width=True)
    else:
        st.warning("No matching providers found.")
