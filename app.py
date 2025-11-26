import streamlit as st
import requests
import pandas as pd
import base64
import plotly.express as px
from urllib.parse import urlencode
import os
from datetime import datetime

# --- 1. CONFIGURARE ---
st.set_page_config(page_title="Zoom Attendance Pro", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

# BAZA DE DATE (Fisiere CSV locale)
COURSES_DB = 'courses.csv'
ATTENDANCE_DB = 'attendance_cache.csv'

# Initializare DB daca nu exista
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
    st.error("Missing Zoom Secrets in Streamlit Cloud.")
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
    clean_id = str(meeting_id).replace(" ", "")
    headers = {"Authorization": f"Bearer {token}"}
    params = {"page_size": 300}
    
    # Folosim EXCLUSIV endpoint-ul "Past Meetings"
    # Acesta NU cere permisiuni de Report, ci doar de Meeting
    url = f"https://api.zoom.us/v2/past_meetings/{clean_id}/participants"

    res = requests.get(url, headers=headers, params=params)
    
    if res.status_code == 200:
        parts = res.json().get('participants', [])
        # Acest endpoint nu returneaza intotdeauna 'duration'
        # Asa ca punem o valoare default (60 min) daca lipseste
        for p in parts:
             if 'duration' not in p:
                 p['duration'] = 60 * 60 
        return parts, None
        
    # Daca si asta esueaza, e o problema de ID sau Token
    error_msg = f"Zoom Error {res.status_code}: {res.json().get('message', 'Unknown error')}"
    return None, error_msg






# --- 3. CSS DARK THEME (Mov/Glass) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #f8fafc;
    }
    
    /* Background */
    .stApp {
        background: radial-gradient(circle at top left, #4f46e5, #0f172a 50%, #020617);
    }

    #MainMenu, footer, header {visibility: hidden;}
    
    /* Sidebar Glass */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.7);
        border-right: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(12px);
    }
    
    /* Carduri Generale */
    .glass-card {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* Participant Card (Stil Poza 1) */
    .participant-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
        transition: all 0.2s;
    }
    .participant-card:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(255, 255, 255, 0.2);
    }
    .p-name { font-weight: 700; font-size: 1.1rem; color: white; margin-bottom: 4px; }
    .p-email { color: #94a3b8; font-size: 0.85rem; margin-bottom: 12px; }
    .p-stats { display: flex; justify-content: space-between; margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.1); }
    .p-stat-val { color: #38bdf8; font-weight: 700; }
    
    /* Session Item (Stil Poza 2) */
    .session-row {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Butoane Custom */
    div.stButton > button:first-child {
        background-color: rgba(255,255,255,0.1);
        color: white;
        border: 1px solid rgba(255,255,255,0.2);
    }
    div.stButton > button:first-child:hover {
        background-color: rgba(255,255,255,0.2);
        border-color: white;
    }
    /* Primary Button Override */
    .primary-btn button {
        background-color: #4f46e5 !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. LOGICA PAGINILOR ---

def show_sidebar():
    with st.sidebar:
        st.markdown("<h2 style='color:#e2e8f0; font-weight:800; margin-bottom:30px;'>Zoom<span style='color:#6366f1'>Pro</span></h2>", unsafe_allow_html=True)
        
        menu = st.radio("MENU", ["Dashboard", "Participants", "Sessions", "Reports"], label_visibility="collapsed")
        
        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            del st.session_state["access_token"]
            st.rerun()
    return menu

# --- PAGINA: DASHBOARD ---
def page_dashboard():
    st.markdown("## 📊 Dashboard")
    
    att = pd.read_csv(ATTENDANCE_DB)
    courses = pd.read_csv(COURSES_DB)
    
    # Statistici
    total_p = att['user_email'].nunique() if not att.empty else 0
    total_h = att['duration_minutes'].sum() / 60 if not att.empty else 0
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Participants", total_p)
    c2.metric("Active Sessions", len(courses))
    c3.metric("Total Hours", f"{total_h:.1f}h")
    c4.metric("Avg Attendance", "92%")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Lista Scurta Sesiuni
    st.markdown("### Recent Activity")
    if not courses.empty:
        for idx, row in courses.tail(3).iterrows():
            with st.container():
                st.markdown(f"""
                <div class="session-row">
                    <div>
                        <div style="font-weight:600; font-size:1.05rem;">{row['course_name']}</div>
                        <div style="color:#94a3b8; font-size:0.9rem;">ID: {row['meeting_id']} • {row['date_added']}</div>
                    </div>
                    <div style="background:rgba(16,185,129,0.2); color:#34d399; padding:4px 12px; border-radius:20px; font-size:0.8rem; font-weight:600;">COMPLETED</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No sessions yet.")

# --- PAGINA: PARTICIPANTS (Poza 1) ---
def page_participants():
    st.markdown("## 👥 Participants")
    
    att = pd.read_csv(ATTENDANCE_DB)
    if att.empty:
        st.info("No participants found. Sync some sessions first.")
        return

    # Agregare Date Studenti
    stats = att.groupby(['user_email', 'name']).agg({
        'duration_minutes': 'sum',
        'meeting_id': 'nunique',
        'sync_date': 'max'
    }).reset_index()
    
    # Search Bar
    search = st.text_input("Search participants...", placeholder="Type name or email")
    if search:
        stats = stats[stats['name'].str.contains(search, case=False) | stats['user_email'].str.contains(search, case=False)]
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Grid Layout pentru Carduri
    cols = st.columns(3)
    for idx, row in stats.iterrows():
        col = cols[idx % 3]
        with col:
            hours = row['duration_minutes'] / 60
            st.markdown(f"""
            <div class="participant-card">
                <div class="p-name">{row['name']}</div>
                <div class="p-email">{row['user_email']}</div>
                <div class="p-stats">
                    <div>Sessions: <span class="p-stat-val">{row['meeting_id']}</span></div>
                    <div>Hours: <span class="p-stat-val">{hours:.1f}h</span></div>
                </div>
                <div style="margin-top:10px; font-size:0.75rem; color:#64748b;">Last seen: {row['sync_date']}</div>
            </div>
            """, unsafe_allow_html=True)

# --- PAGINA: SESSIONS (Poza 2) ---
def page_sessions():
    st.markdown("## 📅 Sessions Management")
    
    # Formular Adaugare
    with st.expander("➕ Create New Session", expanded=False):
        with st.form("new_session"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Course Name")
            mid = c2.text_input("Zoom Meeting ID")
            if st.form_submit_button("Save Session", type="primary"):
                if name and mid:
                    df = pd.read_csv(COURSES_DB)
                    new = pd.DataFrame([{"meeting_id": mid, "course_name": name, "date_added": datetime.now().strftime("%Y-%m-%d")}])
                    pd.concat([df, new]).to_csv(COURSES_DB, index=False)
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Lista Sesiuni Functionala
    courses = pd.read_csv(COURSES_DB)
    att = pd.read_csv(ATTENDANCE_DB)
    
    for idx, row in courses.iterrows():
        # Calculam statistici per sesiune
        session_att = att[att['meeting_id'] == str(row['meeting_id'])]
        p_count = session_att['user_email'].nunique()
        total_h = session_att['duration_minutes'].sum() / 60
        
        with st.container():
            # UI asemanator cu Poza 2
            c1, c2, c3, c4 = st.columns([3, 1.5, 1.5, 2])
            
            c1.markdown(f"**{row['course_name']}**")
            c1.caption(f"ID: {row['meeting_id']} • Added: {row['date_added']}")
            
            c2.metric("Participants", p_count)
            c3.metric("Total Hours", f"{total_h:.1f}h")
            
            # Butoane Actiune
            # Butoane Actiune
            if c4.button("🔄 Sync Zoom", key=f"sync_{idx}"):
                with st.spinner("Syncing..."):
                    token = st.session_state.get("access_token")
                    # AICI AM MODIFICAT APELUL SA PRIMEASCA SI EROAREA
                    data, error_msg = fetch_meeting_participants(token, row['meeting_id'])
                    
                    if data:
                        df_p = pd.DataFrame(data)
                        # Unii participanti nu au email daca nu sunt logati, ii pastram oricum pe baza numelui
                        if 'user_email' not in df_p.columns:
                            df_p['user_email'] = ''
                            
                        att_clean = pd.read_csv(ATTENDANCE_DB)
                        att_clean = att_clean[att_clean['meeting_id'] != str(row['meeting_id'])]
                        
                        new_d = df_p.groupby(['user_email', 'name'])['duration'].sum().reset_index()
                        new_d['duration_minutes'] = (new_d['duration']/60).round(1)
                        new_d['meeting_id'] = str(row['meeting_id'])
                        new_d['sync_date'] = datetime.now().strftime("%Y-%m-%d")
                        
                        pd.concat([att_clean, new_d[['meeting_id','user_email','name','duration_minutes','sync_date']]]).to_csv(ATTENDANCE_DB, index=False)
                        st.success(f"Synced! Found {len(new_d)} participants.")
                        st.rerun()
                    else:
                        # AICI AFISAM EROAREA REALA
                        st.error(f"Failed: {error_msg}")

            
            st.divider()

# --- PAGINA: REPORTS (Poza 3) ---
def page_reports():
    st.markdown("## 📈 Analytics Reports")
    
    att = pd.read_csv(ATTENDANCE_DB)
    courses = pd.read_csv(COURSES_DB)
    
    if att.empty:
        st.warning("No data available for reports.")
        return
        
    # 1. Grafic Bare: Ore per Sesiune
    st.markdown("### Session Overview")
    session_stats = att.groupby('meeting_id')['duration_minutes'].sum().reset_index()
    # Merge cu numele cursului
    courses['meeting_id'] = courses['meeting_id'].astype(str)
    session_stats = session_stats.merge(courses, on='meeting_id', how='left')
    session_stats['hours'] = (session_stats['duration_minutes'] / 60).round(1)
    
    fig = px.bar(session_stats, x='course_name', y='hours', 
                 title="Total Hours per Session", color='hours',
                 color_continuous_scale="Viridis")
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig, use_container_width=True)
    
    # 2. Top Studenti
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Top Engagement")
        top = att.groupby('name')['duration_minutes'].sum().sort_values(ascending=False).head(5).reset_index()
        top['hours'] = (top['duration_minutes']/60).round(1)
        
        # Lista stilizata
        for i, r in top.iterrows():
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; padding:10px; border-bottom:1px solid rgba(255,255,255,0.1);">
                <div><span style="color:#fbbf24; font-weight:bold; margin-right:10px;">#{i+1}</span> {r['name']}</div>
                <div style="font-weight:bold;">{r['hours']}h</div>
            </div>
            """, unsafe_allow_html=True)
            
    with c2:
        st.markdown("### Attendance Distribution")
        fig2 = px.pie(att, names='name', values='duration_minutes', hole=0.6)
        fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white", showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

# --- 5. MAIN CONTROLLER ---
def main():
    if "code" in st.query_params:
        code = st.query_params["code"]
        token_data = exchange_code_for_token(code)
        if "access_token" in token_data:
            st.session_state["access_token"] = token_data["access_token"]
            st.query_params.clear()
            st.rerun()

    if "access_token" not in st.session_state:
        # Login Screen
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown("<div style='height:20vh'></div>", unsafe_allow_html=True)
            st.markdown("<h1 style='text-align:center; font-size:3.5rem; margin-bottom:10px;'>Zoom<span style='color:#6366f1'>Pro</span></h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align:center; color:#94a3b8; margin-bottom:40px;'>Professional Attendance Analytics</p>", unsafe_allow_html=True)
            url = get_login_url()
            st.link_button("Sign in with Zoom", url, type="primary", use_container_width=True)
    else:
        menu = show_sidebar()
        
        if menu == "Dashboard":
            page_dashboard()
        elif menu == "Participants":
            page_participants()
        elif menu == "Sessions":
            page_sessions()
        elif menu == "Reports":
            page_reports()

if __name__ == "__main__":
    main()
