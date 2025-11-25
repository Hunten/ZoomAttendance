import streamlit as st
import requests
import pandas as pd
import base64
import plotly.express as px
from urllib.parse import urlencode

# --- CONFIGURATION ---
st.set_page_config(page_title="Zoom Attendance Manager", page_icon="🎓", layout="wide")

# CSS pentru a ascunde meniul Streamlit
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {padding-top: 0px; padding-bottom: 0px; padding-left: 0px; padding-right: 0px; max-width: 100%;}
    </style>
""", unsafe_allow_html=True)

# --- SECRETS & AUTH SETUP ---
try:
    CLIENT_ID = st.secrets["zoom"]["client_id"]
    CLIENT_SECRET = st.secrets["zoom"]["client_secret"]
    REDIRECT_URI = st.secrets["zoom"]["redirect_uri"]
except Exception as e:
    st.error("❌ Eroare: Nu am găsit secretele. Verifică 'Settings > Secrets' în Streamlit Cloud.")
    st.stop()

AUTHORIZE_URL = "https://zoom.us/oauth/authorize"
TOKEN_URL = "https://zoom.us/oauth/token"

# --- FUNCȚII AUXILIARE ---

def get_login_url():
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI
    }
    return f"{AUTHORIZE_URL}?{urlencode(params)}"

def exchange_code_for_token(auth_code):
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_string.encode()).decode()
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    params = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI
    }
    try:
        response = requests.post(TOKEN_URL, headers=headers, params=params)
        return response.json()
    except:
        return {"error": "Connection failed"}

def get_attendance_report(token, meeting_id):
    url = f"https://api.zoom.us/v2/report/meetings/{meeting_id}/participants"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"page_size": 300}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get('participants', []), None
    return None, response.text

# --- LANDING PAGE HTML ---
# IMPORTANT: HTML-ul este pus aici, lipit de marginea din stânga, pentru a nu fi interpretat ca "code block"
def show_landing_page():
    login_url = get_login_url()
    
    html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="https://cdn.tailwindcss.com"></script>
<style>
    body {{ font-family: system-ui, -apple-system, sans-serif; margin: 0; }}
    .gradient-bg {{ background: radial-gradient(circle at top left, #4f46e5, #0f172a 50%, #020617); }}
    .card-shadow {{ box-shadow: 0 18px 45px rgba(15, 23, 42, 0.4); }}
</style>
</head>
<body class="bg-slate-950 text-slate-50 antialiased">
<div class="min-h-screen gradient-bg flex flex-col">
    <!-- Navbar -->
    <header class="w-full border-b border-slate-800/60 bg-slate-950/50 backdrop-blur-md sticky top-0 z-50">
    <div class="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <div class="flex items-center gap-2">
        <div class="h-8 w-8 rounded-xl bg-indigo-500/90 flex items-center justify-center text-xs font-bold text-white">ZA</div>
        <span class="text-sm font-semibold text-slate-100">ZoomAttendance.io</span>
        </div>
        <div class="flex items-center gap-3">
        <a href="{login_url}" target="_self" class="text-xs font-medium px-3 py-1.5 rounded-full border border-slate-600/80 text-slate-200 hover:bg-slate-800 transition decoration-transparent">
            Sign in
        </a>
        <a href="{login_url}" target="_self" class="text-xs font-semibold px-4 py-2 rounded-full bg-indigo-500 hover:bg-indigo-400 text-white transition decoration-transparent">
            Start free trial
        </a>
        </div>
    </div>
    </header>

    <!-- Hero Section -->
    <main class="flex-1">
    <section class="max-w-6xl mx-auto px-4 py-20 grid lg:grid-cols-[3fr,2fr] gap-14 items-center">
        <div>
        <div class="inline-flex items-center gap-2 rounded-full border border-indigo-500/40 bg-indigo-500/10 px-3 py-1 mb-4">
            <span class="h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
            <span class="text-[11px] font-medium uppercase tracking-widest text-indigo-100">Designed for live courses</span>
        </div>
        <h1 class="text-5xl font-semibold tracking-tight text-slate-50 mb-6">
            Track Course Attendance<br/>with Zoom Integration
        </h1>
        <p class="text-base text-slate-300 max-w-xl mb-8">
            Monitor participant engagement, sync attendance from Zoom meetings, and generate comprehensive reports — all in one secure platform.
        </p>
        <div class="flex gap-4 mb-8">
            <a href="{login_url}" target="_self" class="inline-flex justify-center items-center px-6 py-3 rounded-full bg-indigo-600 hover:bg-indigo-500 text-sm font-semibold text-white transition shadow-lg shadow-indigo-500/25 decoration-transparent">
            Connect Zoom & Get Started
            </a>
        </div>
        <p class="text-xs text-slate-400">No credit card required. Secure by design.</p>
        </div>

        <!-- Visual Element -->
        <div class="relative hidden lg:block">
        <div class="absolute inset-0 rounded-3xl bg-indigo-500/30 blur-3xl opacity-60 -z-10"></div>
        <div class="bg-slate-900/90 border border-slate-700/70 rounded-3xl p-6 card-shadow">
            <div class="flex items-center justify-between mb-4">
            <span class="text-xs font-medium text-slate-300">Live Session Preview</span>
            <span class="text-[11px] font-medium text-emerald-300 flex items-center gap-1">• Sync Active</span>
            </div>
            <div class="space-y-3">
            <div class="flex items-center justify-between text-xs p-2 rounded bg-slate-800/50 border border-slate-700">
                <div class="flex items-center gap-2">
                <div class="w-6 h-6 rounded-full bg-slate-700"></div>
                <div><p class="text-slate-200">Alex Chen</p><p class="text-[10px] text-slate-400">94% Attendance</p></div>
                </div>
                <span class="text-emerald-400">Present</span>
            </div>
            <div class="flex items-center justify-between text-xs p-2 rounded bg-slate-800/50 border border-slate-700">
                <div class="flex items-center gap-2">
                <div class="w-6 h-6 rounded-full bg-slate-700"></div>
                <div><p class="text-slate-200">Maria Lopez</p><p class="text-[10px] text-slate-400">81% Attendance</p></div>
                </div>
                <span class="text-amber-400">Late</span>
            </div>
            </div>
        </div>
        </div>
    </section>
    </main>
</div>
</body>
</html>
"""
    st.markdown(html_code, unsafe_allow_html=True)

# --- MAIN LOGIC ---

def main():
    # 1. Auth Flow
    if "code" in st.query_params:
        auth_code = st.query_params["code"]
        with st.spinner("Authenticating..."):
            token_data = exchange_code_for_token(auth_code)
            if "access_token" in token_data:
                st.session_state["access_token"] = token_data["access_token"]
                st.query_params.clear()
                st.rerun()
            else:
                st.error("Login failed.")

    # 2. Display Logic
    if "access_token" not in st.session_state:
        show_landing_page()
    else:
        st.markdown("""<style>.block-container {padding: 2rem 1rem !important;}</style>""", unsafe_allow_html=True)
        
        with st.sidebar:
            st.title("ZoomAttendance")
            st.success("✅ Logged in")
            if st.button("Logout", type="primary"):
                del st.session_state["access_token"]
                st.rerun()
            st.divider()
            st.caption("Connected via OAuth")

        st.title("📊 Attendance Dashboard")
        st.markdown("Generează rapoarte pentru cursurile anterioare.")

        token = st.session_state["access_token"]
        
        col1, col2 = st.columns([3, 1])
        with col1:
            meeting_id = st.text_input("Meeting ID", placeholder="Ex: 1234567890")
        with col2:
            st.write("")
            st.write("")
            generate_btn = st.button("Generate Report", type="primary", use_container_width=True)
        
        if generate_btn and meeting_id:
            with st.spinner("Fetching..."):
                participants, error = get_attendance_report(token, meeting_id)
                
                if participants:
                    df = pd.DataFrame(participants)
                    if 'user_email' in df.columns and 'duration' in df.columns:
                        summary = df.groupby(['user_email', 'name']).agg({
                            'duration': 'sum',
                            'join_time': 'min',
                            'leave_time': 'max'
                        }).reset_index()
                        summary['duration_minutes'] = (summary['duration'] / 60).round(1)
                        summary = summary.sort_values('duration_minutes', ascending=False)

                        st.divider()
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Participants", len(summary))
                        m2.metric("Avg Time", f"{summary['duration_minutes'].mean():.1f} m")
                        m3.metric("Top", summary.iloc[0]['name'] if not summary.empty else "-")
                        
                        fig = px.bar(summary.head(15), x='name', y='duration_minutes', title="Top Engagement")
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.dataframe(summary, use_container_width=True)
                        st.download_button("📥 Download CSV", summary.to_csv(index=False).encode('utf-8'), f"report_{meeting_id}.csv", "text/csv")
                    else:
                        st.warning("Data incomplete (missing email/duration). Check Zoom Plan.")
                elif error:
                    st.error(f"Error: {error}")
                else:
                    st.info("No participants found.")

if __name__ == "__main__":
    main()
