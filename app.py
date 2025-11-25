import streamlit as st
import requests
import pandas as pd
import base64
import plotly.express as px
from urllib.parse import urlencode

# --- CONFIGURATION ---
st.set_page_config(page_title="Zoom Attendance Manager", page_icon="🎓", layout="wide")

# Stiluri CSS minime pentru Streamlit
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 0px; padding-bottom: 0px; padding-left: 0px; padding-right: 0px; max-width: 100%;}
</style>
""", unsafe_allow_html=True)

# --- SECRETS ---
try:
    CLIENT_ID = st.secrets["zoom"]["client_id"]
    CLIENT_SECRET = st.secrets["zoom"]["client_secret"]
    REDIRECT_URI = st.secrets["zoom"]["redirect_uri"]
except:
    st.error("Lipsesc secretele din Streamlit Cloud.")
    st.stop()

# --- OAUTH ---
AUTHORIZE_URL = "https://zoom.us/oauth/authorize"
TOKEN_URL = "https://zoom.us/oauth/token"

def get_login_url():
    params = {"response_type": "code", "client_id": CLIENT_ID, "redirect_uri": REDIRECT_URI}
    return f"{AUTHORIZE_URL}?{urlencode(params)}"

def exchange_code_for_token(auth_code):
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_string.encode()).decode()
    headers = {"Authorization": f"Basic {b64_auth}", "Content-Type": "application/x-www-form-urlencoded"}
    params = {"grant_type": "authorization_code", "code": auth_code, "redirect_uri": REDIRECT_URI}
    try:
        return requests.post(TOKEN_URL, headers=headers, params=params).json()
    except:
        return {"error": "Connection failed"}

def get_attendance_report(token, meeting_id):
    url = f"https://api.zoom.us/v2/report/meetings/{meeting_id}/participants"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"page_size": 300}
    res = requests.get(url, headers=headers, params=params)
    return (res.json().get('participants', []), None) if res.status_code == 200 else (None, res.text)

# --- LANDING PAGE ---
def show_landing_page():
    login_url = get_login_url()
    
    # IMPORTANT: String-ul HTML este definit fara indentare, lipit de margine
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="https://cdn.tailwindcss.com"></script>
<style>
    body {{ font-family: sans-serif; margin: 0; }}
    .gradient-bg {{ background: radial-gradient(circle at top left, #4f46e5, #0f172a 50%, #020617); }}
</style>
</head>
<body class="bg-slate-950 text-slate-50">
<div class="min-h-screen gradient-bg flex flex-col">
    <header class="w-full border-b border-slate-800/60 bg-slate-950/50 backdrop-blur-md sticky top-0 z-50">
    <div class="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <div class="flex items-center gap-2">
        <div class="h-8 w-8 rounded bg-indigo-600 flex items-center justify-center font-bold text-white">ZA</div>
        <span class="font-semibold text-slate-100">ZoomAttendance.io</span>
        </div>
        <a href="{login_url}" target="_self" class="text-xs font-semibold px-4 py-2 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white transition">
            Sign in
        </a>
    </div>
    </header>
    <main class="flex-1 flex items-center">
    <section class="max-w-6xl mx-auto px-4 py-20 grid lg:grid-cols-2 gap-10 items-center">
        <div>
        <h1 class="text-5xl font-bold text-white mb-6">Track Course Attendance<br/>with Zoom</h1>
        <p class="text-slate-300 text-lg mb-8">Sync attendance automatically and get detailed reports.</p>
        <a href="{login_url}" target="_self" class="inline-block px-8 py-4 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold shadow-lg transition">
            Connect Zoom & Start
        </a>
        </div>
        <div class="hidden lg:block bg-slate-900/80 border border-slate-700 rounded-2xl p-6">
             <div class="text-slate-400 text-sm mb-4">Live Preview</div>
             <div class="space-y-2">
                <div class="flex justify-between text-xs p-2 bg-slate-800 rounded border border-slate-700 text-slate-200">
                    <span>Alex Chen</span><span class="text-emerald-400">Present</span>
                </div>
                <div class="flex justify-between text-xs p-2 bg-slate-800 rounded border border-slate-700 text-slate-200">
                    <span>Maria Lopez</span><span class="text-amber-400">Late</span>
                </div>
             </div>
        </div>
    </section>
    </main>
</div>
</body>
</html>"""
    
    # Folosim st.components.v1.html pentru randare sigura daca st.markdown face probleme
    import streamlit.components.v1 as components
    components.html(html_content, height=800, scrolling=True)

# --- MAIN ---
def main():
    if "code" in st.query_params:
        auth_code = st.query_params["code"]
        token_data = exchange_code_for_token(auth_code)
        if "access_token" in token_data:
            st.session_state["access_token"] = token_data["access_token"]
            st.query_params.clear()
            st.rerun()
    
    if "access_token" not in st.session_state:
        show_landing_page()
    else:
        # Dashboard Mode
        st.markdown("""<style>.block-container {padding: 2rem 1rem !important;}</style>""", unsafe_allow_html=True)
        
        with st.sidebar:
            st.title("ZoomAttendance")
            if st.button("Logout"):
                del st.session_state["access_token"]
                st.rerun()
        
        st.title("📊 Attendance Dashboard")
        meeting_id = st.text_input("Meeting ID")
        
        if st.button("Get Report") and meeting_id:
            data, err = get_attendance_report(st.session_state["access_token"], meeting_id)
            if data:
                df = pd.DataFrame(data)
                if 'user_email' in df.columns:
                    summary = df.groupby('user_email').agg({'duration': 'sum', 'name': 'first'}).reset_index()
                    summary['minutes'] = (summary['duration']/60).round(1)
                    st.metric("Participants", len(summary))
                    st.dataframe(summary)
                else:
                    st.warning("No email data found.")
            elif err:
                st.error(err)

if __name__ == "__main__":
    main()
