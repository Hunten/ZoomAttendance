import streamlit as st
import requests
import pandas as pd
import base64
import plotly.express as px
from urllib.parse import urlencode
import os
from datetime import datetime

# --- 1. CONFIGURARE ---
st.set_page_config(page_title="Zoom Attendance Dashboard", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

# DATABASE
COURSES_DB = 'courses.csv'
ATTENDANCE_DB = 'attendance_cache.csv'

if not os.path.exists(COURSES_DB):
    pd.DataFrame(columns=["meeting_id", "course_name", "date_added"]).to_csv(COURSES_DB, index=False)
if not os.path.exists(ATTENDANCE_DB):
    pd.DataFrame(columns=["meeting_id", "user_email", "name", "duration_minutes", "sync_date"]).to_csv(ATTENDANCE_DB, index=False)

# --- 2. ZOOM API & AUTH ---
try:
    CLIENT_ID = st.secrets["zoom"]["client_id"]
    CLIENT_SECRET = st.secrets["zoom"]["client_secret"]
    REDIRECT_URI = st.secrets["zoom"]["redirect_uri"]
except:
    st.error("Missing Secrets")
    st.stop()

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

def fetch_meeting_participants(token, meeting_id):
    url = f"https://api.zoom.us/v2/report/meetings/{meeting_id}/participants"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"page_size": 300}
    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 200:
        return res.json().get('participants', [])
    return None

# --- 3. CSS DARK MODE (THEMA MOV) ---
st.markdown("""
<style>
    /* Global Font & Dark Theme Reset */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #f8fafc; /* Text deschis */
    }
    
    /* Background-ul Mov preferat */
    .stApp {
        background: radial-gradient(circle at top left, #4f46e5, #0f172a 50%, #020617);
    }

    /* Hiding Default Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sidebar Styling (Dark Glass) */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.6);
        border-right: 1px solid rgba(255,255,255,0.1);
        padding-top: 20px;
        backdrop-filter: blur(10px);
    }
    
    /* Main Content Area adjustment */
    .block-container {
        padding-top: 2rem !important;
        max-width: 100% !important;
    }

    /* Dashboard Header */
    .dashboard-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: #ffffff;
    }
    .dashboard-subtitle {
        color: #94a3b8;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    /* Card Styling (Dark Glassmorphism) */
    .stat-card {
        background: rgba(30, 41, 59, 0.4); /* Semi-transparent dark blue */
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
        height: 100%;
    }
    .stat-card:hover {
        background: rgba(30, 41, 59, 0.6);
        border-color: rgba(255, 255, 255, 0.2);
        transform: translateY(-2px);
    }
    .stat-label {
        color: #94a3b8;
        font-size: 0.875rem;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
    }
    .stat-value {
        color: #ffffff;
        font-size: 1.875rem;
        font-weight: 700;
    }
    .stat-sub {
        font-size: 0.75rem;
        color: #64748b;
        margin-top: 4px;
    }

    /* Session List Items (Dark) */
    .session-container {
        background: rgba(30, 41, 59, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 0 24px;
        margin-top: 16px;
    }
    .session-item {
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        padding: 16px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .session-item:last-child { border-bottom: none; }
    
    .session-name {
        font-weight: 600;
        color: #f1f5f9;
        font-size: 1rem;
    }
    .session-meta {
        font-size: 0.875rem;
        color: #94a3b8;
        margin-top: 4px;
    }
    
    .status-badge {
        background-color: rgba(245, 158, 11, 0.1);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.2);
        font-size: 0.75rem;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 9999px;
        text-transform: uppercase;
    }

    /* Custom Link Button Override */
    .stLinkButton button {
        background-color: #4f46e5;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        box-shadow: 0 0 15px rgba(79, 70, 229, 0.4);
    }
    .stLinkButton button:hover {
        background-color: #4338ca;
    }
    
    /* Tabs styling fix for dark mode */
    div[data-baseweb="tab-list"] {
        background-color: transparent !important;
    }
    button[data-baseweb="tab"] {
        color: #cbd5e1 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. LOGICA UI ---

def show_sidebar():
    with st.sidebar:
        st.markdown("<h2 style='padding-left:10px; color:#e2e8f0; font-size:1.4rem; margin-bottom:30px; font-weight:700;'>Zoom<span style='color:#6366f1'>Manager</span></h2>", unsafe_allow_html=True)
        
        # Meniu simplu
        selection = st.radio(
            "",
            ["Dashboard", "Participants", "Sessions", "Reports"],
            index=0,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        if st.button("Logout", type="secondary", use_container_width=True):
            del st.session_state["access_token"]
            st.rerun()
            
        return selection

def show_dashboard_content():
    # Header
    st.markdown('<div class="dashboard-title">Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subtitle">Real-time overview of your course attendance</div>', unsafe_allow_html=True)

    # Calculam Datele
    courses = pd.read_csv(COURSES_DB)
    attendance = pd.read_csv(ATTENDANCE_DB)
    
    total_participants = attendance['user_email'].nunique() if not attendance.empty else 0
    total_sessions = len(courses)
    total_hours = (attendance['duration_minutes'].sum() / 60) if not attendance.empty else 0

    # GRID DE CARDURI
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Participants <span>👥</span></div>
            <div class="stat-value">{total_participants}</div>
            <div class="stat-sub">Unique students tracked</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Active Sessions <span>📅</span></div>
            <div class="stat-value">{total_sessions}</div>
            <div class="stat-sub">Scheduled classes</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Total Hours <span>⏱️</span></div>
            <div class="stat-value">{total_hours:.1f}</div>
            <div class="stat-sub">Cumulative time</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Attendance Rate <span>📈</span></div>
            <div class="stat-value">94%</div>
            <div class="stat-sub">Average engagement</div>
        </div>
        """, unsafe_allow_html=True)

    # SECTIUNEA "RECENT SESSIONS"
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown('<h3 style="font-weight:700; margin-bottom:0; color:white;">Recent Sessions</h3>', unsafe_allow_html=True)
    st.markdown('<p style="color:#94a3b8; font-size:0.9rem;">Latest synced meetings</p>', unsafe_allow_html=True)

    # Lista Sesiuni (Design Dark)
    st.markdown('<div class="session-container">', unsafe_allow_html=True)
    
    if not courses.empty:
        courses_rev = courses.iloc[::-1]
        
        for idx, row in courses_rev.iterrows():
            # Date dummy pentru aspect vizual
            p_count = 25 + (idx * 3) 
            duration = 90
            date_str = row['date_added']
            
            st.markdown(f"""
            <div class="session-item">
                <div>
                    <div class="session-name">{row['course_name']}</div>
                    <div class="session-meta">{date_str} • {p_count} participants • {duration} min</div>
                </div>
                <div class="status-badge">completed</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No sessions found. Go to 'Sessions' to add one.")
        
    st.markdown('</div>', unsafe_allow_html=True)

def show_sessions_content():
    st.markdown('<div class="dashboard-title">Manage Sessions</div>', unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("#### Add New Session")
        with st.form("add_s"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Course Name", placeholder="e.g. Python Advanced Module 1")
            mid = c2.text_input("Zoom Meeting ID", placeholder="e.g. 9876543210")
            if st.form_submit_button("Add Session", type="primary"):
                if name and mid:
                    df = pd.read_csv(COURSES_DB)
                    new = pd.DataFrame([{"meeting_id": mid, "course_name": name, "date_added": datetime.now().strftime("%b %d, %Y")}])
                    pd.concat([df, new]).to_csv(COURSES_DB, index=False)
                    st.rerun()
                
    st.markdown("<br>### Active Sessions List", unsafe_allow_html=True)
    courses = pd.read_csv(COURSES_DB)
    
    for _, row in courses.iterrows():
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"**{row['course_name']}**")
            c1.caption(f"Meeting ID: {row['meeting_id']}")
            
            if c2.button("🔄 Sync Data", key=row['meeting_id']):
                with st.spinner("Syncing..."):
                    token = st.session_state.get("access_token")
                    data = fetch_meeting_participants(token, row['meeting_id'])
                    if data:
                        df_p = pd.DataFrame(data)
                        if 'user_email' in df_p.columns:
                            att = pd.read_csv(ATTENDANCE_DB)
                            att = att[att['meeting_id'] != str(row['meeting_id'])] # Clean old
                            
                            new_d = df_p.groupby(['user_email', 'name'])['duration'].sum().reset_index()
                            new_d['duration_minutes'] = (new_d['duration']/60).round(1)
                            new_d['meeting_id'] = str(row['meeting_id'])
                            new_d['sync_date'] = datetime.now().strftime("%Y-%m-%d")
                            
                            pd.concat([att, new_d[['meeting_id','user_email','name','duration_minutes','sync_date']]]).to_csv(ATTENDANCE_DB, index=False)
                            st.success("Synced Successfully!")
                    else:
                        st.error("Sync Failed (Check ID)")

# --- 5. MAIN ---
def main():
    # Auth Check
    if "code" in st.query_params:
        code = st.query_params["code"]
        token_data = exchange_code_for_token(code)
        if "access_token" in token_data:
            st.session_state["access_token"] = token_data["access_token"]
            st.query_params.clear()
            st.rerun()

    if "access_token" not in st.session_state:
        # Landing Page Login - Dark Theme
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<div style='height:15vh'></div>", unsafe_allow_html=True)
            st.markdown("""
            <div style='text-align:center; margin-bottom:40px;'>
                <div style='background:rgba(255,255,255,0.1); width:60px; height:60px; border-radius:16px; display:flex; align-items:center; justify-content:center; margin:0 auto 20px auto; font-size:30px;'>🎓</div>
                <h1 style='font-size:3rem; font-weight:800; margin-bottom:10px;'>Zoom Attendance</h1>
                <p style='color:#94a3b8; font-size:1.1rem;'>Secure, automated tracking for your courses.</p>
            </div>
            """, unsafe_allow_html=True)
            
            url = get_login_url()
            st.link_button("Sign in with Zoom Account", url, type="primary", use_container_width=True)
            
            st.markdown("<div style='text-align:center; margin-top:20px; color:#475569; font-size:0.8rem'>Powered by Zoom OAuth 2.0</div>", unsafe_allow_html=True)

    else:
        # App Layout
        page = show_sidebar()
        
        if page == "Dashboard":
            show_dashboard_content()
        elif page == "Sessions":
            show_sessions_content()
        elif page == "Participants":
            st.markdown('<div class="dashboard-title">Participants Database</div>', unsafe_allow_html=True)
            df = pd.read_csv(ATTENDANCE_DB)
            st.dataframe(df, use_container_width=True)
        else:
            st.title("Reports")
            st.info("Coming soon...")

if __name__ == "__main__":
    main()
