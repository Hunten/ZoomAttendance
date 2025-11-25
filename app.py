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

# Fișiere "Baza de date" (CSV-uri locale)
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
    st.error("❌ Lipsesc secretele Zoom! Verifică Settings > Secrets în Streamlit Cloud.")
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

def get_user_info(token):
    url = "https://api.zoom.us/v2/users/me"
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(url, headers=headers)
    return res.json() if res.status_code == 200 else {}

# --- 3. STILURI CSS (DESIGN) ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Navigatie Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }
    
    /* Buton Login Google-Style */
    .google-btn {
        background-color: white;
        color: #374151 !important;
        padding: 12px 24px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 10px;
        border: 1px solid #e5e7eb;
        transition: all 0.2s;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .google-btn:hover {
        background-color: #f9fafb;
        border-color: #d1d5db;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Landing Page Typography */
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. UI PAGINI ---

def show_landing_page():
    # Background Gradient doar pe Landing Page
    st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #020617 100%);
    }
    </style>
    """, unsafe_allow_html=True)
    
    login_url = get_login_url()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.write("") # Spacer
        st.write("")
        st.write("")
        st.markdown('<h1 class="hero-title">Course Attendance<br>Simplified.</h1>', unsafe_allow_html=True)
        st.markdown("""
        <p style="font-size: 1.2rem; color: #94a3b8; margin-bottom: 2rem; line-height: 1.6;">
            Connect your Zoom account to automatically sync participant data, track course hours, and manage your students in one unified dashboard.
        </p>
        """, unsafe_allow_html=True)
        
        # Butonul "Sign in with Zoom" stilizat sa arate a Google/SSO friendly
        st.markdown(f"""
        <a href="{login_url}" target="_self" class="google-btn">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Google_%22G%22_Logo.svg/512px-Google_%22G%22_Logo.svg.png" width="20" height="20">
            Sign in with Zoom (Google SSO supported)
        </a>
        <p style="margin-top: 15px; font-size: 0.85rem; color: #64748b;">
            🔒 Secure connection via Zoom OAuth 2.0
        </p>
        """, unsafe_allow_html=True)

    with col2:
        # Mockup Vizual
        st.markdown("""
        <div style="margin-top: 40px; background: rgba(15, 23, 42, 0.6); border: 1px solid #334155; border-radius: 16px; padding: 24px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);">
            <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
                <div style="font-weight: 600; color: white;">Live Overview</div>
                <div style="color: #34d399; font-size: 0.9rem;">● System Online</div>
            </div>
            <div style="background: #1e293b; padding: 12px; border-radius: 8px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #cbd5e1;">Python Course</span>
                <span style="background: #3730a3; color: #a5b4fc; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem;">Syncing...</span>
            </div>
            <div style="background: #1e293b; padding: 12px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #cbd5e1;">Design Basics</span>
                <span style="color: #94a3b8; font-size: 0.9rem;">24 Students</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_dashboard():
    st.title("📊 Dashboard")
    courses = pd.read_csv(COURSES_DB)
    attendance = pd.read_csv(ATTENDANCE_DB)
    
    # Carduri de statistici
    c1, c2, c3 = st.columns(3)
    c1.metric("Cursuri Active", len(courses))
    c2.metric("Studenți Total", attendance['user_email'].nunique())
    c3.metric("Ore Predate", f"{(attendance['duration_minutes'].sum()/60):.1f}h")
    
    st.divider()
    
    if not attendance.empty:
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.subheader("Activitate Recentă")
            # Chart
            daily_activity = attendance.groupby('sync_date')['duration_minutes'].sum().reset_index()
            fig = px.bar(daily_activity, x='sync_date', y='duration_minutes', title="Minute de curs per Zi")
            st.plotly_chart(fig, use_container_width=True)
            
        with col_right:
            st.subheader("Top Studenți")
            top_students = attendance.groupby('name')['duration_minutes'].sum().sort_values(ascending=False).head(5)
            st.dataframe(top_students, use_container_width=True)
    else:
        st.info("👋 Bine ai venit! Mergi la tab-ul 'Cursuri' pentru a adăuga prima clasă.")

def show_courses():
    st.title("📚 Cursuri & Sincronizare")
    
    with st.expander("➕ Adaugă Curs Nou", expanded=False):
        with st.form("add_c"):
            c_name = st.text_input("Nume Curs")
            c_id = st.text_input("Zoom Meeting ID")
            if st.form_submit_button("Salvează Curs"):
                if c_name and c_id:
                    df = pd.read_csv(COURSES_DB)
                    new_row = pd.DataFrame([{"meeting_id": c_id, "course_name": c_name, "date_added": datetime.now().date()}])
                    pd.concat([df, new_row]).to_csv(COURSES_DB, index=False)
                    st.success("Adăugat!")
                    st.rerun()

    courses = pd.read_csv(COURSES_DB)
    if not courses.empty:
        for _, row in courses.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.write(f"**{row['course_name']}**")
                c1.caption(f"ID: {row['meeting_id']}")
                
                if c2.button("🔄 Sync", key=row['meeting_id']):
                    with st.spinner("Syncing..."):
                        token = st.session_state.get("access_token")
                        parts = fetch_meeting_participants(token, row['meeting_id'])
                        if parts:
                            # Procesare
                            df = pd.DataFrame(parts)
                            if 'user_email' in df.columns:
                                att = pd.read_csv(ATTENDANCE_DB)
                                # Sterge vechi pt acest ID
                                att = att[att['meeting_id'] != str(row['meeting_id'])]
                                
                                new_data = df.groupby(['user_email', 'name'])['duration'].sum().reset_index()
                                new_data['duration_minutes'] = (new_data['duration']/60).round(1)
                                new_data['meeting_id'] = str(row['meeting_id'])
                                new_data['sync_date'] = datetime.now().date()
                                
                                pd.concat([att, new_data[['meeting_id','user_email','name','duration_minutes','sync_date']]]).to_csv(ATTENDANCE_DB, index=False)
                                st.toast(f"Succes! {len(new_data)} studenți actualizați.")
                            else:
                                st.error("Zoom nu a returnat email-uri (verifică setări Zoom).")
                        else:
                            st.error("Eroare la preluare date.")

def show_students():
    st.title("🎓 Studenți")
    att = pd.read_csv(ATTENDANCE_DB)
    if not att.empty:
        search = st.text_input("🔍 Caută student...")
        if search:
            att = att[att['name'].str.contains(search, case=False) | att['user_email'].str.contains(search, case=False)]
        
        st.dataframe(att, use_container_width=True)
    else:
        st.warning("Nu există date.")

# --- 5. MAIN LOGIC ---
def main():
    # Auth Handler
    if "code" in st.query_params:
        code = st.query_params["code"]
        token_data = exchange_code_for_token(code)
        if "access_token" in token_data:
            st.session_state["access_token"] = token_data["access_token"]
            st.query_params.clear()
            st.rerun()
            
    if "access_token" not in st.session_state:
        show_landing_page()
    else:
        # Preluare date user logat (pentru avatar/nume)
        if "user_info" not in st.session_state:
            st.session_state["user_info"] = get_user_info(st.session_state["access_token"])
            
        user = st.session_state.get("user_info", {})
        
        # Sidebar
        with st.sidebar:
            if user.get('pic_url'):
                st.image(user['pic_url'], width=50)
            st.write(f"Hello, **{user.get('first_name', 'Admin')}**!")
            st.divider()
            page = st.radio("Meniu", ["Dashboard", "Cursuri", "Studenți"])
            st.divider()
            if st.button("Deconectare"):
                del st.session_state["access_token"]
                del st.session_state["user_info"]
                st.rerun()
        
        # Routing
        if page == "Dashboard":
            show_dashboard()
        elif page == "Cursuri":
            show_courses()
        elif page == "Studenți":
            show_students()

if __name__ == "__main__":
    main()
