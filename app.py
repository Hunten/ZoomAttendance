import streamlit as st
import requests
import pandas as pd
import base64
import plotly.express as px
from urllib.parse import urlencode
import os
from datetime import datetime

# --- 1. CONFIGURARE & INIT ---
st.set_page_config(page_title="Zoom Academy Manager", page_icon="🎓", layout="wide")

# Fișiere "Baza de date"
COURSES_DB = 'courses.csv'
ATTENDANCE_DB = 'attendance_cache.csv'

# Inițializare fișiere dacă nu există
if not os.path.exists(COURSES_DB):
    pd.DataFrame(columns=["meeting_id", "course_name", "date_added"]).to_csv(COURSES_DB, index=False)
if not os.path.exists(ATTENDANCE_DB):
    pd.DataFrame(columns=["meeting_id", "user_email", "name", "duration_minutes", "sync_date"]).to_csv(ATTENDANCE_DB, index=False)

# --- 2. SECRETE & ZOOM API ---
try:
    CLIENT_ID = st.secrets["zoom"]["client_id"]
    CLIENT_SECRET = st.secrets["zoom"]["client_secret"]
    REDIRECT_URI = st.secrets["zoom"]["redirect_uri"]
except:
    st.error("❌ Lipsesc secretele Zoom! Verifică Settings > Secrets în Streamlit.")
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

# --- 3. STILURI CSS (DESIGN) ---
st.markdown("""
<style>
    /* Global Reset */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Navigatie Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }
    
    /* Carduri Dashboard */
    .metric-card {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #334155;
        color: white;
        text-align: center;
    }
    
    /* Landing Page Specific */
    .landing-container {
        padding: 4rem 2rem;
        text-align: left;
        color: white;
    }
    
    /* Buton Login Custom */
    .login-btn {
        background-color: #4f46e5;
        color: white !important;
        padding: 10px 25px;
        border-radius: 30px;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
        margin-top: 20px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .login-btn:hover { background-color: #4338ca; }
</style>
""", unsafe_allow_html=True)

# --- 4. PAGINI (UI) ---

def show_landing_page():
    # Aplicam un background special doar pentru landing page
    st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #4f46e5, #0f172a 50%, #020617);
    }
    </style>
    """, unsafe_allow_html=True)
    
    login_url = get_login_url()
    
    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown(f"""
        <div class="landing-container">
            <div style="display:inline-block; padding:5px 12px; background:rgba(79, 70, 229, 0.2); border-radius:20px; color:#a5b4fc; font-size:0.8rem; margin-bottom:20px;">
                🚀 BETA VERSION 1.0
            </div>
            <h1 style="font-size: 4rem; line-height: 1.1; font-weight: 800; margin-bottom: 20px;">
                Manage Zoom Courses<br>Like a Pro
            </h1>
            <p style="font-size: 1.2rem; color: #cbd5e1; max-width: 500px;">
                Centralize your course attendance, track student hours automatically, and generate reports in seconds.
            </p>
            <a href="{login_url}" target="_self" class="login-btn">Connect with Zoom Account</a>
            <p style="margin-top:10px; font-size:0.8rem; color:#64748b;">Secure OAuth 2.0 • No Password Required</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Imagine / Mockup UI
        st.markdown("""
        <div style="margin-top: 80px; background: rgba(30, 41, 59, 0.7); padding: 30px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1);">
            <h3 style="color:white; margin-bottom:20px; font-size:1.2rem;">Live Dashboard Preview</h3>
            <div style="display:flex; justify-content:space-between; margin-bottom:15px; border-bottom:1px solid #334155; padding-bottom:10px;">
                <span style="color:#94a3b8;">Total Hours</span>
                <span style="color:#34d399; font-weight:bold;">1,240h</span>
            </div>
             <div style="display:flex; justify-content:space-between; margin-bottom:15px; border-bottom:1px solid #334155; padding-bottom:10px;">
                <span style="color:#94a3b8;">Active Students</span>
                <span style="color:white; font-weight:bold;">42</span>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span style="color:#94a3b8;">Courses</span>
                <span style="color:white; font-weight:bold;">5 Active</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_dashboard():
    st.title("📊 Dashboard")
    
    # Citim datele
    courses = pd.read_csv(COURSES_DB)
    attendance = pd.read_csv(ATTENDANCE_DB)
    
    # Metrice Principale
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cursuri Active", len(courses))
    c2.metric("Total Studenți Unici", attendance['user_email'].nunique())
    total_hours = (attendance['duration_minutes'].sum() / 60)
    c3.metric("Total Ore Predate", f"{total_hours:.1f}h")
    c4.metric("Ultimul Sync", str(datetime.now().strftime("%H:%M")))

    st.divider()
    
    # Top Studenți
    if not attendance.empty:
        st.subheader("🏆 Top Studenți după Ore")
        student_stats = attendance.groupby(['name', 'user_email'])['duration_minutes'].sum().reset_index()
        student_stats['hours'] = (student_stats['duration_minutes'] / 60).round(1)
        student_stats = student_stats.sort_values('hours', ascending=False).head(10)
        
        fig = px.bar(student_stats, x='hours', y='name', orientation='h', title="Top Engagement", color='hours')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nu există date de prezență încă. Mergi la pagina 'Cursuri' pentru a sincroniza.")

def show_courses_page():
    st.title("📚 Management Cursuri")
    
    # Formular adaugare curs
    with st.form("add_course"):
        c1, c2 = st.columns(2)
        new_name = c1.text_input("Nume Curs", placeholder="Ex: Python Avansat")
        new_id = c2.text_input("Meeting ID (Zoom)", placeholder="Ex: 987654321")
        submitted = st.form_submit_button("Adaugă Curs")
        
        if submitted and new_name and new_id:
            courses = pd.read_csv(COURSES_DB)
            # Verificăm duplicate
            if str(new_id) not in courses['meeting_id'].astype(str).values:
                new_row = pd.DataFrame([{"meeting_id": new_id, "course_name": new_name, "date_added": datetime.now().date()}])
                new_row.to_csv(COURSES_DB, mode='a', header=False, index=False)
                st.success(f"Cursul '{new_name}' a fost adăugat!")
                st.rerun()
            else:
                st.warning("Acest Meeting ID există deja.")

    # Tabel Cursuri
    courses = pd.read_csv(COURSES_DB)
    if not courses.empty:
        st.write("### Lista Cursuri")
        for index, row in courses.iterrows():
            with st.expander(f"📘 {row['course_name']} (ID: {row['meeting_id']})"):
                col_a, col_b = st.columns([3,1])
                col_a.write(f"Adăugat la: {row['date_added']}")
                
                # Buton Sync
                if col_b.button("🔄 Sync Zoom Data", key=f"sync_{row['meeting_id']}"):
                    with st.spinner("Se descarcă datele de la Zoom..."):
                        token = st.session_state.get("access_token")
                        participants = fetch_meeting_participants(token, row['meeting_id'])
                        
                        if participants:
                            # Procesare
                            df = pd.DataFrame(participants)
                            if 'user_email' in df.columns and 'duration' in df.columns:
                                # Curatam datele vechi pentru acest meeting
                                current_att = pd.read_csv(ATTENDANCE_DB)
                                current_att = current_att[current_att['meeting_id'] != str(row['meeting_id'])] # Stergem vechi
                                
                                # Cream noile date
                                new_data = df.groupby(['user_email', 'name'])['duration'].sum().reset_index()
                                new_data['duration_minutes'] = (new_data['duration'] / 60).round(1)
                                new_data['meeting_id'] = str(row['meeting_id'])
                                new_data['sync_date'] = datetime.now().date()
                                new_data = new_data[['meeting_id', 'user_email', 'name', 'duration_minutes', 'sync_date']]
                                
                                # Salvam
                                pd.concat([current_att, new_data]).to_csv(ATTENDANCE_DB, index=False)
                                st.success(f"Sincronizat! {len(new_data)} studenți găsiți.")
                            else:
                                st.warning("Date incomplete de la Zoom (lipsesc email-uri).")
                        else:
                            st.error("Nu s-au găsit date sau Meeting ID invalid.")

def show_students_page():
    st.title("🎓 Bază de Date Studenți")
    attendance = pd.read_csv(ATTENDANCE_DB)
    
    if not attendance.empty:
        # Centralizator
        summary = attendance.groupby(['user_email', 'name']).agg({
            'duration_minutes': 'sum',
            'meeting_id': 'nunique' # La cate cursuri a participat
        }).reset_index()
        
        summary.columns = ['Email', 'Nume', 'Total Minute', 'Cursuri Participat']
        summary['Total Ore'] = (summary['Total Minute'] / 60).round(1)
        
        st.dataframe(summary, use_container_width=True)
        
        st.download_button("Descarcă Raport Complet CSV", summary.to_csv(index=False), "studenti_raport.csv")
    else:
        st.info("Nu există date. Sincronizează întâi cursurile.")

# --- 5. LOGICA PRINCIPALĂ ---
def main():
    # Auth Check
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
        # Meniu Sidebar
        st.sidebar.title("ZoomManager")
        page = st.sidebar.radio("Navigare", ["Dashboard", "Cursuri", "Studenți"])
        st.sidebar.divider()
        if st.sidebar.button("Logout"):
            del st.session_state["access_token"]
            st.rerun()
            
        # Router Pagini
        if page == "Dashboard":
            show_dashboard()
        elif page == "Cursuri":
            show_courses_page()
        elif page == "Studenți":
            show_students_page()

if __name__ == "__main__":
    main()
