import streamlit as st
import requests
import pandas as pd
import base64
import plotly.express as px
from urllib.parse import urlencode
import os
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="ZoomAttendance.io", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# DATABASE (Local CSV files)
COURSES_DB = 'courses.csv'
ATTENDANCE_DB = 'attendance_cache.csv'

# Initialize DB if not exists
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
    
    # Using "Past Meetings" endpoint (Works with Basic/Pro permissions)
    url = f"https://api.zoom.us/v2/past_meetings/{clean_id}/participants"

    res = requests.get(url, headers=headers, params=params)
    
    if res.status_code == 200:
        parts = res.json().get('participants', [])
        for p in parts:
             if 'duration' not in p:
                 p['duration'] = 60 * 60 # Default 60 mins if missing
        return parts, None
        
    error_msg = f"Zoom Error {res.status_code}: {res.json().get('message', 'Unknown error')}"
    return None, error_msg

# --- 3. LANDING PAGE (YOUR NEW DESIGN) ---
def show_landing_page():
    login_url = get_login_url()
    
    # We use target="_top" to force the link to open in the main window, breaking out of the iframe
    # This fixes "refused to connect"
    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <script src="https://cdn.tailwindcss.com"></script>
      <style>
        body {{ font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 0; }}
        .gradient-bg {{ background: radial-gradient(circle at top left, #4f46e5, #0f172a 50%, #020617); }}
        .card-shadow {{ box-shadow: 0 18px 45px rgba(15, 23, 42, 0.4); }}
        a {{ text-decoration: none; }}
      </style>
    </head>
    <body class="bg-slate-950 text-slate-50 antialiased">
      <div class="min-h-screen gradient-bg flex flex-col">
        <!-- Nav -->
        <header class="w-full border-b border-slate-800/60">
          <div class="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
            <div class="flex items-center gap-2">
              <div class="h-8 w-8 rounded-xl bg-indigo-500/90 flex items-center justify-center text-xs font-bold tracking-tight text-white">
                ZA
              </div>
              <span class="text-sm font-semibold tracking-tight text-slate-100">
                ZoomAttendance.io
              </span>
            </div>
            <nav class="hidden sm:flex items-center gap-6 text-xs font-medium text-slate-300">
              <a href="#features" class="hover:text-white transition-colors">Features</a>
              <a href="#how-it-works" class="hover:text-white transition-colors">How it works</a>
              <a href="#faq" class="hover:text-white transition-colors">FAQ</a>
            </nav>
            <div class="flex items-center gap-3">
              <a href="{login_url}" target="_top" class="hidden sm:inline-flex text-xs font-medium px-3 py-1.5 rounded-full border border-slate-600/80 text-slate-200 hover:bg-slate-800/70 transition">
                Sign in
              </a>
              <a href="{login_url}" target="_top" class="text-xs font-semibold px-4 py-2 rounded-full bg-indigo-500 hover:bg-indigo-400 text-white transition">
                Start free trial
              </a>
            </div>
          </div>
        </header>

        <!-- Hero -->
        <main class="flex-1">
          <section class="max-w-6xl mx-auto px-4 py-12 lg:py-20 grid lg:grid-cols-[3fr,2fr] gap-10 lg:gap-14 items-center">
            <div>
              <div class="inline-flex items-center gap-2 rounded-full border border-indigo-500/40 bg-indigo-500/10 px-3 py-1 mb-4">
                <span class="h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
                <span class="text-[11px] font-medium uppercase tracking-[0.18em] text-indigo-100">
                  Designed for live courses
                </span>
              </div>

              <h1 class="text-3xl sm:text-4xl lg:text-5xl font-semibold tracking-tight text-slate-50 mb-4">
                Track Course Attendance<br class="hidden sm:block" />
                with Zoom Integration
              </h1>

              <p class="text-sm sm:text-base text-slate-300 max-w-xl mb-6">
                Monitor participant engagement, sync attendance from Zoom meetings, and generate
                comprehensive reports &mdash; all in one secure platform.
              </p>

              <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 mb-6">
                <a href="{login_url}" target="_top" class="inline-flex justify-center items-center px-5 py-2.5 rounded-full bg-indigo-500 hover:bg-indigo-400 text-sm font-semibold text-white transition">
                  Connect Zoom &amp; get started
                </a>
                <button class="inline-flex justify-center items-center px-5 py-2.5 rounded-full border border-slate-700 text-sm font-medium text-slate-200 hover:bg-slate-900/60 transition">
                  Book a 15‑min demo
                </button>
              </div>

              <p class="text-[11px] text-slate-400">
                No credit card required. Secure by design. Ready in under 5 minutes.
              </p>
            </div>

            <!-- Hero card (Visual only) -->
            <div class="relative">
              <div class="absolute inset-0 rounded-3xl bg-indigo-500/30 blur-3xl opacity-60 -z-10"></div>
              <div class="bg-slate-900/90 border border-slate-700/70 rounded-3xl p-5 sm:p-6 card-shadow">
                <div class="flex items-center justify-between mb-4">
                  <span class="text-xs font-medium text-slate-300">Today’s live session</span>
                  <span class="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-300">
                    • Live sync on
                  </span>
                </div>

                <div class="mb-4 border border-slate-700/80 rounded-2xl px-4 py-3 bg-slate-900/70">
                  <div class="flex items-center justify-between mb-1.5">
                    <div>
                      <p class="text-xs font-semibold text-slate-100">Advanced React Bootcamp</p>
                      <p class="text-[11px] text-slate-400">09:00–11:00 &middot; Zoom Meeting #4821</p>
                    </div>
                    <span class="inline-flex items-center px-2 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/40 text-[10px] font-semibold text-emerald-200">Syncing</span>
                  </div>
                  <div class="mt-3 grid grid-cols-3 gap-3 text-[11px] text-slate-300">
                    <div><p class="text-slate-400 mb-0.5">Participants</p><p class="font-semibold text-slate-50">42 / 50</p></div>
                    <div><p class="text-slate-400 mb-0.5">Avg. attendance</p><p class="font-semibold text-slate-50">92%</p></div>
                    <div><p class="text-slate-400 mb-0.5">Avg. duration</p><p class="font-semibold text-slate-50">1h 47m</p></div>
                  </div>
                </div>
                
                 <p class="text-[11px] uppercase tracking-[0.18em] text-slate-400 mb-2">
                  Live attendance stream
                </p>

                <div class="space-y-2.5 max-h-44 overflow-hidden">
                  <div class="flex items-center justify-between text-xs">
                    <div class="flex items-center gap-2">
                      <span class="h-6 w-6 rounded-full bg-slate-800 border border-slate-700/90"></span>
                      <div><p class="text-slate-100 text-[11px] font-medium">Alex Chen</p><p class="text-[10px] text-slate-400">Joined · 09:01 | Present</p></div>
                    </div>
                    <span class="text-[10px] px-2 py-1 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/30">1h 44m</span>
                  </div>
                  <div class="flex items-center justify-between text-xs">
                    <div class="flex items-center gap-2">
                      <span class="h-6 w-6 rounded-full bg-slate-800 border border-slate-700/90"></span>
                      <div><p class="text-slate-100 text-[11px] font-medium">Maria Lopez</p><p class="text-[10px] text-slate-400">Joined · 09:15 | Present</p></div>
                    </div>
                    <span class="text-[10px] px-2 py-1 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/30">1h 21m</span>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <!-- Features -->
          <section id="features" class="max-w-6xl mx-auto px-4 pb-16">
             <!-- Simplified for brevity in Streamlit, content preserved -->
             <div class="border border-slate-800/70 rounded-3xl bg-slate-950/60 px-5 sm:px-8 py-8 sm:py-10">
                <h2 class="text-xl sm:text-2xl font-semibold text-slate-50 mb-6">Everything you need for reliable attendance</h2>
                <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 text-sm">
                    <div class="border border-slate-800 rounded-2xl p-4 bg-slate-900/60">
                        <p class="text-xs font-semibold text-indigo-300 mb-1">Session Tracking</p>
                        <h3 class="text-sm font-semibold text-slate-50 mb-1.5">Schedule & auto-sync</h3>
                        <p class="text-sm text-slate-400">Schedule sessions once and let Zoom attendance flow in automatically.</p>
                    </div>
                    <div class="border border-slate-800 rounded-2xl p-4 bg-slate-900/60">
                        <p class="text-xs font-semibold text-indigo-300 mb-1">Reports</p>
                        <h3 class="text-sm font-semibold text-slate-50 mb-1.5">Export CSV</h3>
                        <p class="text-sm text-slate-400">Generate clean CSV files per session, cohort, or course.</p>
                    </div>
                    <div class="border border-slate-800 rounded-2xl p-4 bg-slate-900/60">
                        <p class="text-xs font-semibold text-indigo-300 mb-1">Duration</p>
                        <h3 class="text-sm font-semibold text-slate-50 mb-1.5">Accurate time</h3>
                        <p class="text-sm text-slate-400">Track total time attended per participant per session.</p>
                    </div>
                </div>
             </div>
          </section>
        </main>
        <footer class="border-t border-slate-800/70"><div class="max-w-6xl mx-auto px-4 py-5 text-[11px] text-slate-500 text-center">&copy; 2025 ZoomAttendance.io</div></footer>
      </div>
    </body>
    </html>
    """
    components.html(html_code, height=1200, scrolling=True)

# --- 4. APP STYLING & LOGIC (Logged In) ---
def show_dashboard_interface():
    # Apply Dark Theme CSS for Streamlit Elements
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #f8fafc; }
        .stApp { background: radial-gradient(circle at top left, #4f46e5, #0f172a 50%, #020617); }
        section[data-testid="stSidebar"] { background-color: rgba(15, 23, 42, 0.7); border-right: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(12px); }
        .glass-card { background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; padding: 20px; }
        .session-row { background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 16px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; }
        .participant-card { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 16px; margin-bottom: 16px; }
        .p-name { font-weight: 700; font-size: 1.1rem; color: white; }
        .p-email { color: #94a3b8; font-size: 0.85rem; margin-bottom: 10px; }
        .p-stats { display: flex; justify-content: space-between; margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.1); padding-top:8px;}
        div.stButton > button:first-child { background-color: rgba(255,255,255,0.1); color: white; border: 1px solid rgba(255,255,255,0.2); }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("<h2 style='color:#e2e8f0; font-weight:800; margin-bottom:30px;'>Zoom<span style='color:#6366f1'>Pro</span></h2>", unsafe_allow_html=True)
        menu = st.radio("MENU", ["Dashboard", "Participants", "Sessions", "Reports"], label_visibility="collapsed")
        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            del st.session_state["access_token"]
            st.rerun()

    # Router
    if menu == "Dashboard":
        page_dashboard()
    elif menu == "Participants":
        page_participants()
    elif menu == "Sessions":
        page_sessions()
    elif menu == "Reports":
        page_reports()

# --- PAGE FUNCTIONS ---
def page_dashboard():
    st.markdown("## 📊 Dashboard")
    att = pd.read_csv(ATTENDANCE_DB)
    courses = pd.read_csv(COURSES_DB)
    
    total_p = att['user_email'].nunique() if not att.empty else 0
    total_h = att['duration_minutes'].sum() / 60 if not att.empty else 0
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Participants", total_p)
    c2.metric("Active Sessions", len(courses))
    c3.metric("Total Hours", f"{total_h:.1f}h")
    c4.metric("Avg Attendance", "92%")

    st.markdown("<br>### Recent Activity", unsafe_allow_html=True)
    if not courses.empty:
        for idx, row in courses.tail(3).iterrows():
            st.markdown(f"""
            <div class="session-row">
                <div><div style="font-weight:600;">{row['course_name']}</div><div style="color:#94a3b8; font-size:0.85rem;">ID: {row['meeting_id']}</div></div>
                <div style="color:#34d399; font-size:0.8rem; font-weight:600;">ACTIVE</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No sessions yet.")

def page_participants():
    st.markdown("## 👥 Participants")
    att = pd.read_csv(ATTENDANCE_DB)
    if att.empty:
        st.info("No participants data. Sync a session first.")
        return

    stats = att.groupby(['user_email', 'name']).agg({'duration_minutes': 'sum', 'meeting_id': 'nunique'}).reset_index()
    
    search = st.text_input("Search...", placeholder="Name or email")
    if search:
        stats = stats[stats['name'].str.contains(search, case=False) | stats['user_email'].str.contains(search, case=False)]
    
    st.markdown("<br>", unsafe_allow_html=True)
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
                    <div>Sessions: <b>{row['meeting_id']}</b></div>
                    <div>Hours: <b>{hours:.1f}h</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def page_sessions():
    st.markdown("## 📅 Sessions")
    with st.expander("➕ Add Session"):
        with st.form("new_sess"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Name")
            mid = c2.text_input("ID")
            if st.form_submit_button("Save"):
                if name and mid:
                    df = pd.read_csv(COURSES_DB)
                    new = pd.DataFrame([{"meeting_id": mid, "course_name": name, "date_added": datetime.now().strftime("%Y-%m-%d")}])
                    pd.concat([df, new]).to_csv(COURSES_DB, index=False)
                    st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    courses = pd.read_csv(COURSES_DB)
    att = pd.read_csv(ATTENDANCE_DB)
    
    for idx, row in courses.iterrows():
        session_att = att[att['meeting_id'] == str(row['meeting_id'])]
        p_count = session_att['user_email'].nunique()
        
        with st.container():
            c1, c2, c3, c4 = st.columns([3, 1.5, 1.5, 2])
            c1.markdown(f"**{row['course_name']}**")
            c1.caption(f"ID: {row['meeting_id']}")
            c2.metric("Participants", p_count)
            c3.metric("Hours", f"{(session_att['duration_minutes'].sum()/60):.1f}h")
            
            if c4.button("🔄 Sync", key=f"s_{idx}"):
                with st.spinner("Syncing..."):
                    token = st.session_state.get("access_token")
                    data, err = fetch_meeting_participants(token, row['meeting_id'])
                    if data:
                        df_p = pd.DataFrame(data)
                        if 'user_email' not in df_p.columns: df_p['user_email'] = ''
                        
                        att_clean = pd.read_csv(ATTENDANCE_DB)
                        att_clean = att_clean[att_clean['meeting_id'] != str(row['meeting_id'])]
                        
                        new_d = df_p.groupby(['user_email', 'name'])['duration'].sum().reset_index()
                        new_d['duration_minutes'] = (new_d['duration']/60).round(1)
                        new_d['meeting_id'] = str(row['meeting_id'])
                        new_d['sync_date'] = datetime.now().strftime("%Y-%m-%d")
                        
                        pd.concat([att_clean, new_d[['meeting_id','user_email','name','duration_minutes','sync_date']]]).to_csv(ATTENDANCE_DB, index=False)
                        st.success(f"Synced {len(new_d)} people!")
                        st.rerun()
                    else:
                        st.error(f"Failed: {err}")
            st.divider()

def page_reports():
    st.markdown("## 📈 Reports")
    att = pd.read_csv(ATTENDANCE_DB)
    courses = pd.read_csv(COURSES_DB)
    if att.empty:
        st.warning("No data.")
        return
    
    stats = att.groupby('meeting_id')['duration_minutes'].sum().reset_index()
    courses['meeting_id'] = courses['meeting_id'].astype(str)
    stats = stats.merge(courses, on='meeting_id', how='left')
    stats['hours'] = (stats['duration_minutes']/60).round(1)
    
    fig = px.bar(stats, x='course_name', y='hours', title="Total Hours per Session")
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig, use_container_width=True)

# --- 5. MAIN EXECUTION ---
def main():
    # 1. Check for Auth Callback
    if "code" in st.query_params:
        code = st.query_params["code"]
        token_data = exchange_code_for_token(code)
        if "access_token" in token_data:
            st.session_state["access_token"] = token_data["access_token"]
            st.query_params.clear()
            st.rerun()

    # 2. Render App based on Auth State
    if "access_token" not in st.session_state:
        # Remove default padding for the Landing Page to look like a real site
        st.markdown("""
            <style>
                .block-container { padding-top: 0rem !important; padding-bottom: 0rem !important; padding-left: 0rem !important; padding-right: 0rem !important; max-width: 100% !important; }
                div[data-testid="stSidebar"] { display: none; }
            </style>
        """, unsafe_allow_html=True)
        show_landing_page()
    else:
        show_dashboard_interface()

if __name__ == "__main__":
    main()
