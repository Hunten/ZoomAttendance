import streamlit as st
import requests
import pandas as pd
import base64
import plotly.express as px
from urllib.parse import urlencode

# --- CONFIGURATION ---
st.set_page_config(page_title="Zoom Attendance Manager", page_icon="🎓", layout="wide")

# --- CSS PENTRU FULL SCREEN & DESIGN MODERN ---
# Acesta repara aspectul "rau" eliminand padding-ul standard Streamlit si setand fundalul corect
st.markdown("""
<style>
    /* Ascunde elementele default Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Elimina spatiile albe de pe margini */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100% !important;
    }
    
    /* Fundalul intregii pagini */
    .stApp {
        background: radial-gradient(circle at top left, #4f46e5, #0f172a 50%, #020617);
        color: white;
    }
    
    /* Stiluri pentru Landing Page */
    .hero-container {
        padding: 4rem 2rem;
        max-width: 1200px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: space-between;
        min-height: 80vh;
    }
    
    .hero-text h1 {
        font-size: 3.5rem;
        font-weight: 700;
        line-height: 1.2;
        margin-bottom: 1.5rem;
        color: #f8fafc;
    }
    
    .hero-text p {
        font-size: 1.125rem;
        color: #cbd5e1;
        margin-bottom: 2rem;
        max-width: 500px;
    }
    
    /* Butonul de Login stilizat custom */
    .login-btn {
        display: inline-block;
        background-color: #4f46e5;
        color: white !important;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border-radius: 9999px;
        text-decoration: none;
        transition: background-color 0.2s;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .login-btn:hover {
        background-color: #4338ca;
        border-color: white;
    }
    
    /* Cardul din dreapta */
    .preview-card {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(51, 65, 85, 0.5);
        border-radius: 1.5rem;
        padding: 2rem;
        width: 100%;
        max-width: 450px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
    }

    /* Ascunde link-urile implicite Streamlit din markdown */
    a { text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# --- SECRETS ---
try:
    CLIENT_ID = st.secrets["zoom"]["client_id"]
    CLIENT_SECRET = st.secrets["zoom"]["client_secret"]
    REDIRECT_URI = st.secrets["zoom"]["redirect_uri"]
except:
    st.warning("⚠️ Secretele lipsesc. Configurați .streamlit/secrets.toml sau Secrets în Cloud.")
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

# --- UI FUNCTIONS ---

def show_landing_page():
    login_url = get_login_url()
    
    # Folosim HTML simplu, fara tag-uri <html> sau <body>, doar structura div-urilor
    # Link-ul are target="_self" care merge garantat
    st.markdown(f"""
    <nav style="display:flex; justify-content:space-between; align-items:center; padding: 1.5rem 2rem; border-bottom: 1px solid rgba(255,255,255,0.1);">
        <div style="display:flex; align-items:center; gap:10px;">
            <div style="background:#4f46e5; width:32px; height:32px; border-radius:8px; display:flex; align-items:center; justify-content:center; font-weight:bold;">ZA</div>
            <span style="font-weight:600;">ZoomAttendance</span>
        </div>
        <a href="{login_url}" target="_self" class="login-btn" style="padding: 0.5rem 1.5rem; font-size:0.9rem;">Sign in</a>
    </nav>

    <div class="hero-container">
        <div class="hero-text">
            <div style="display:inline-block; padding:5px 12px; background:rgba(79, 70, 229, 0.1); border:1px solid rgba(79, 70, 229, 0.3); border-radius:50px; color:#a5b4fc; font-size:0.8rem; margin-bottom:1rem; font-weight:600; text-transform:uppercase; letter-spacing:1px;">
                Live Course Tools
            </div>
            <h1>Track Attendance<br>with Zoom Integration</h1>
            <p>Stop worrying about spreadsheets. Automatically sync participant data, track duration, and export reports in seconds.</p>
            
            <div style="margin-top:2rem;">
                <a href="{login_url}" target="_self" class="login-btn">
                    Connect Zoom Account
                </a>
                <p style="margin-top:1rem; font-size:0.8rem; color:#64748b;">Safe & Secure OAuth 2.0 Connection</p>
            </div>
        </div>

        <!-- Partea vizuala (Card Dummy) -->
        <div class="preview-card" style="display:none; @media (min-width: 1024px) { display:block; }">
             <div style="display:flex; justify-content:space-between; margin-bottom:1.5rem;">
                <span style="font-size:0.85rem; color:#94a3b8;">Live Session Preview</span>
                <span style="font-size:0.8rem; color:#34d399;">● Sync Active</span>
             </div>
             <div style="background:rgba(30, 41, 59, 0.6); padding:10px; border-radius:8px; margin-bottom:10px; border:1px solid rgba(255,255,255,0.05); display:flex; justify-content:space-between; align-items:center;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <div style="width:24px; height:24px; background:#475569; border-radius:50%;"></div>
                    <span style="font-size:0.9rem;">Alex Chen</span>
                </div>
                <span style="font-size:0.8rem; color:#34d399;">Present</span>
             </div>
             <div style="background:rgba(30, 41, 59, 0.6); padding:10px; border-radius:8px; border:1px solid rgba(255,255,255,0.05); display:flex; justify-content:space-between; align-items:center;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <div style="width:24px; height:24px; background:#475569; border-radius:50%;"></div>
                    <span style="font-size:0.9rem;">Maria Lopez</span>
                </div>
                <span style="font-size:0.8rem; color:#fbbf24;">Late (15m)</span>
             </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- MAIN APP ---
def main():
    # 1. Auth Logic
    if "code" in st.query_params:
        auth_code = st.query_params["code"]
        token_data = exchange_code_for_token(auth_code)
        if "access_token" in token_data:
            st.session_state["access_token"] = token_data["access_token"]
            st.query_params.clear()
            st.rerun()
    
    # 2. Display Logic
    if "access_token" not in st.session_state:
        show_landing_page()
    else:
        # --- DASHBOARD INTERFACE ---
        
        # Resetam CSS-ul de padding pentru dashboard ca sa putem folosi elementele native Streamlit corect
        st.markdown("""
        <style>
            .block-container { padding: 3rem 1rem !important; max-width: 60rem !important; }
            .hero-container { display: none; }
        </style>
        """, unsafe_allow_html=True)

        with st.sidebar:
            st.title("ZoomAttendance")
            st.caption("Logged in via Zoom")
            if st.button("Logout"):
                del st.session_state["access_token"]
                st.rerun()
        
        st.title("📊 Attendance Dashboard")
        st.markdown("Generate participant reports from past meetings.")
        
        meeting_id = st.text_input("Enter Meeting ID (Past Session)")
        
        if st.button("Get Report", type="primary") and meeting_id:
            data, err = get_attendance_report(st.session_state["access_token"], meeting_id)
            
            if data:
                df = pd.DataFrame(data)
                if 'user_email' in df.columns:
                    summary = df.groupby('user_email').agg({
                        'duration': 'sum', 
                        'name': 'first'
                    }).reset_index()
                    summary['minutes'] = (summary['duration']/60).round(1)
                    summary = summary.sort_values('minutes', ascending=False)
                    
                    c1, c2 = st.columns(2)
                    c1.metric("Participants", len(summary))
                    c2.metric("Avg Duration", f"{summary['minutes'].mean():.0f} min")
                    
                    st.dataframe(summary, use_container_width=True)
                else:
                    st.warning("Data incomplete (missing emails). Check Zoom permissions.")
            elif err:
                st.error(f"Error: {err}")

if __name__ == "__main__":
    main()
