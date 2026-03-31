import streamlit as st
import json
import os
from datetime import datetime, date, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from collections import defaultdict
import calendar
import hashlib

# ─── CONFIG ──────────────────────────────────────────────────────────────────
DATA_FILE = "habits_data.json"
CATEGORIES = ["Health", "Fitness", "Learning", "Productivity", "Mindfulness", "Finance", "Social", "Creative", "Other"]
ICONS = {"Health": "🩺", "Fitness": "💪", "Learning": "📚", "Productivity": "⚡",
         "Mindfulness": "🧘", "Finance": "💰", "Social": "🤝", "Creative": "🎨", "Other": "✨"}
FREQUENCIES = ["Daily", "Weekly", "Monthly"]
COLORS = ["#22c55e", "#16a34a", "#4ade80", "#86efac", "#15803d"]

st.set_page_config(
    page_title="HabitFlow",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Sora:wght@400;600;700&display=swap');

* { font-family: 'Plus Jakarta Sans', sans-serif; }

html, body, [class*="css"] {
    background-color: #f0fdf4 !important;
    color: #14532d !important;
}

.stApp { background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 40%, #f0fdf4 100%) !important; }

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #14532d 0%, #166534 60%, #15803d 100%) !important;
    border-right: 3px solid #22c55e !important;
}
section[data-testid="stSidebar"] * { color: #f0fdf4 !important; }
section[data-testid="stSidebar"] .stRadio label { color: #bbf7d0 !important; }
section[data-testid="stSidebar"] .stSelectbox label { color: #bbf7d0 !important; }

.main-title {
    font-family: 'Sora', sans-serif;
    font-size: 2.8rem;
    font-weight: 700;
    color: #14532d;
    letter-spacing: -1px;
    margin-bottom: 0;
}
.main-subtitle { color: #4ade80; font-size: 1rem; margin-top: 0; font-weight: 500; }

.stat-card {
    background: white;
    border-radius: 16px;
    padding: 20px 24px;
    border: 2px solid #bbf7d0;
    box-shadow: 0 4px 20px rgba(34,197,94,0.10);
    text-align: center;
    transition: transform 0.2s;
}
.stat-card:hover { transform: translateY(-3px); box-shadow: 0 8px 30px rgba(34,197,94,0.18); }
.stat-number { font-size: 2.4rem; font-weight: 800; color: #16a34a; font-family: 'Sora', sans-serif; }
.stat-label { font-size: 0.85rem; color: #4b7c59; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }

.habit-card {
    background: white;
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 12px;
    border: 2px solid #bbf7d0;
    box-shadow: 0 2px 10px rgba(34,197,94,0.08);
    transition: all 0.2s;
}
.habit-card:hover { border-color: #22c55e; box-shadow: 0 4px 20px rgba(34,197,94,0.15); }
.habit-card.completed { border-color: #22c55e; background: linear-gradient(135deg, #f0fdf4, #dcfce7); }

.habit-title { font-size: 1.05rem; font-weight: 700; color: #14532d; }
.habit-meta { font-size: 0.78rem; color: #4b7c59; margin-top: 2px; }
.streak-badge {
    background: linear-gradient(135deg, #22c55e, #16a34a);
    color: white;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
}
.section-header {
    font-family: 'Sora', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: #14532d;
    border-left: 4px solid #22c55e;
    padding-left: 12px;
    margin: 24px 0 16px 0;
}

.progress-bar-bg {
    background: #dcfce7;
    border-radius: 10px;
    height: 8px;
    overflow: hidden;
}
.progress-bar-fill {
    background: linear-gradient(90deg, #22c55e, #16a34a);
    height: 100%;
    border-radius: 10px;
    transition: width 0.4s ease;
}

div[data-testid="stCheckbox"] { margin: 0 !important; }

.stButton > button {
    background: linear-gradient(135deg, #22c55e, #16a34a) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 8px 20px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(34,197,94,0.3) !important;
}

.delete-btn > button {
    background: linear-gradient(135deg, #fee2e2, #fecaca) !important;
    color: #dc2626 !important;
}
.delete-btn > button:hover { background: #dc2626 !important; color: white !important; }

.stTextInput > div > input, .stTextArea > div > textarea,
.stSelectbox > div > div, .stNumberInput > div > input {
    border: 2px solid #bbf7d0 !important;
    border-radius: 10px !important;
    background: white !important;
    color: #14532d !important;
}
.stTextInput > div > input:focus, .stTextArea > div > textarea:focus {
    border-color: #22c55e !important;
    box-shadow: 0 0 0 3px rgba(34,197,94,0.15) !important;
}

.motivational-banner {
    background: linear-gradient(135deg, #16a34a, #14532d);
    color: white;
    border-radius: 16px;
    padding: 18px 24px;
    margin-bottom: 20px;
    font-size: 1.05rem;
    font-weight: 600;
    text-align: center;
    letter-spacing: 0.2px;
}

.calendar-day {
    width: 28px; height: 28px;
    border-radius: 6px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.7rem;
    font-weight: 600;
    margin: 1px;
}

.achievement-badge {
    background: linear-gradient(135deg, #fef9c3, #fef08a);
    border: 2px solid #eab308;
    border-radius: 12px;
    padding: 12px 16px;
    text-align: center;
    margin: 6px;
}
.achievement-icon { font-size: 1.8rem; }
.achievement-name { font-size: 0.8rem; font-weight: 700; color: #713f12; }

div.stTabs [data-baseweb="tab-list"] {
    background: white;
    border-radius: 12px;
    padding: 4px;
    border: 2px solid #bbf7d0;
    gap: 4px;
}
div.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    color: #4b7c59 !important;
    font-weight: 600 !important;
}
div.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #22c55e, #16a34a) !important;
    color: white !important;
}

.tag-chip {
    background: #dcfce7;
    color: #15803d;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    display: inline-block;
    margin: 2px;
}

.info-box {
    background: white;
    border-left: 4px solid #22c55e;
    border-radius: 0 12px 12px 0;
    padding: 14px 18px;
    margin: 10px 0;
    font-size: 0.9rem;
    color: #166534;
}
</style>
""", unsafe_allow_html=True)

# ─── DATA LAYER ──────────────────────────────────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"habits": [], "completions": {}, "notes": {}, "archived": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def today_str():
    return date.today().isoformat()

def week_str(d=None):
    if d is None: d = date.today()
    return f"{d.isocalendar()[0]}-W{d.isocalendar()[1]:02d}"

def month_str(d=None):
    if d is None: d = date.today()
    return d.strftime("%Y-%m")

def get_habit_id(name):
    return hashlib.md5(name.encode()).hexdigest()[:8]

# ─── CORE LOGIC ──────────────────────────────────────────────────────────────
def mark_completion(data, habit_id, period_key, done):
    if habit_id not in data["completions"]:
        data["completions"][habit_id] = {}
    data["completions"][habit_id][period_key] = done
    save_data(data)

def is_completed(data, habit_id, period_key):
    return data["completions"].get(habit_id, {}).get(period_key, False)

def get_streak(data, habit_id, frequency):
    comps = data["completions"].get(habit_id, {})
    streak = 0
    if frequency == "Daily":
        d = date.today()
        while True:
            if comps.get(d.isoformat(), False):
                streak += 1
                d -= timedelta(days=1)
            else:
                break
    elif frequency == "Weekly":
        d = date.today()
        while True:
            wk = f"{d.isocalendar()[0]}-W{d.isocalendar()[1]:02d}"
            if comps.get(wk, False):
                streak += 1
                d -= timedelta(weeks=1)
            else:
                break
    elif frequency == "Monthly":
        d = date.today()
        for _ in range(24):
            mk = d.strftime("%Y-%m")
            if comps.get(mk, False):
                streak += 1
                first = d.replace(day=1)
                d = first - timedelta(days=1)
            else:
                break
    return streak

def get_completion_rate(data, habit_id, frequency, days=30):
    comps = data["completions"].get(habit_id, {})
    completed, total = 0, 0
    if frequency == "Daily":
        for i in range(days):
            d = date.today() - timedelta(days=i)
            total += 1
            if comps.get(d.isoformat(), False): completed += 1
    elif frequency == "Weekly":
        for i in range(days // 7):
            d = date.today() - timedelta(weeks=i)
            wk = f"{d.isocalendar()[0]}-W{d.isocalendar()[1]:02d}"
            total += 1
            if comps.get(wk, False): completed += 1
    elif frequency == "Monthly":
        for i in range(3):
            d = date.today()
            for _ in range(i):
                first = d.replace(day=1)
                d = first - timedelta(days=1)
            mk = d.strftime("%Y-%m")
            total += 1
            if comps.get(mk, False): completed += 1
    return (completed / total * 100) if total > 0 else 0

def get_best_streak(data, habit_id, frequency):
    comps = data["completions"].get(habit_id, {})
    if not comps: return 0
    best, current = 0, 0
    if frequency == "Daily":
        all_dates = sorted([k for k, v in comps.items() if v])
        if not all_dates: return 0
        prev = None
        for ds in all_dates:
            d = date.fromisoformat(ds)
            if prev and (d - prev).days == 1:
                current += 1
            else:
                current = 1
            best = max(best, current)
            prev = d
    return best

def get_achievements(data, habit_id, frequency):
    badges = []
    streak = get_streak(data, habit_id, frequency)
    best = get_best_streak(data, habit_id, frequency)
    rate = get_completion_rate(data, habit_id, frequency)
    total = sum(1 for v in data["completions"].get(habit_id, {}).values() if v)
    if streak >= 3:  badges.append(("🔥", "3-Day Streak"))
    if streak >= 7:  badges.append(("⚡", "7-Day Streak"))
    if streak >= 21: badges.append(("💎", "21-Day Streak"))
    if streak >= 30: badges.append(("🏆", "30-Day Champion"))
    if streak >= 66: badges.append(("🌟", "Habit Master"))
    if rate >= 80:   badges.append(("🎯", "80% Rate"))
    if rate >= 100:  badges.append(("✅", "Perfect Month"))
    if total >= 10:  badges.append(("📌", "10 Completions"))
    if total >= 50:  badges.append(("🥇", "50 Completions"))
    if total >= 100: badges.append(("👑", "100 Completions"))
    return badges

MOTIVATIONS = [
    "🌱 Small steps every day lead to massive results.",
    "💚 You're building the life you deserve, one habit at a time.",
    "🔥 Consistency beats perfection — show up today.",
    "🚀 Your future self will thank you for what you do today.",
    "🌿 Progress, not perfection. Keep going!",
    "⚡ Every check means you're one step closer to your goal.",
    "🏆 Champions are made in the moments they don't feel like showing up.",
]

def get_motivation():
    import random
    return random.choice(MOTIVATIONS)

# ─── PAGES ───────────────────────────────────────────────────────────────────

def sidebar_nav(data):
    st.markdown("""
    <div style='text-align:center; padding: 20px 0 10px 0;'>
        <div style='font-family:Sora,sans-serif; font-size:2rem; font-weight:800; color:#4ade80; letter-spacing:-1px;'>🌱 HabitFlow</div>
        <div style='font-size:0.78rem; color:#86efac; margin-top:2px;'>Your daily growth companion</div>
    </div>
    """, unsafe_allow_html=True)

    total = len(data["habits"])
    today_done = sum(1 for h in data["habits"] if is_completed(data, h["id"], today_str()))
    st.markdown(f"""
    <div style='background:rgba(255,255,255,0.1); border-radius:12px; padding:12px 16px; margin:10px 0 20px 0; text-align:center;'>
        <div style='color:#4ade80; font-size:1.5rem; font-weight:800;'>{today_done}/{total}</div>
        <div style='color:#bbf7d0; font-size:0.78rem; font-weight:600;'>TODAY'S PROGRESS</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("", ["📋 Today", "➕ Add Habit", "📊 Analytics", "📅 Calendar", "🏆 Achievements", "⚙️ Manage Habits", "📓 Journal"], label_visibility="collapsed")
    
    st.markdown("<hr style='border-color:rgba(255,255,255,0.2); margin: 20px 0;'>", unsafe_allow_html=True)
    
    # Quick stats
    all_streaks = [get_streak(data, h["id"], h["frequency"]) for h in data["habits"]]
    st.markdown(f"""
    <div style='color:#86efac; font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;'>QUICK STATS</div>
    <div style='color:#dcfce7; font-size:0.85rem; margin:4px 0;'>🔥 Best streak: {max(all_streaks) if all_streaks else 0} days</div>
    <div style='color:#dcfce7; font-size:0.85rem; margin:4px 0;'>📌 Total habits: {total}</div>
    <div style='color:#dcfce7; font-size:0.85rem; margin:4px 0;'>✅ Completed today: {today_done}</div>
    """, unsafe_allow_html=True)

    return page.split(" ", 1)[1]

def page_today(data):
    st.markdown('<div class="main-title">Today\'s Habits</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="main-subtitle">{date.today().strftime("%A, %B %d %Y")}</div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="motivational-banner">{get_motivation()}</div>', unsafe_allow_html=True)

    habits = [h for h in data["habits"] if h["frequency"] == "Daily"]
    weekly = [h for h in data["habits"] if h["frequency"] == "Weekly"]
    monthly = [h for h in data["habits"] if h["frequency"] == "Monthly"]

    # Overall progress
    all_habits = data["habits"]
    if all_habits:
        def period_key(h):
            if h["frequency"] == "Daily": return today_str()
            if h["frequency"] == "Weekly": return week_str()
            return month_str()
        done = sum(1 for h in all_habits if is_completed(data, h["id"], period_key(h)))
        pct = int(done / len(all_habits) * 100)
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{done}/{len(all_habits)}</div><div class="stat-label">Habits Done</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{pct}%</div><div class="stat-label">Completion</div></div>', unsafe_allow_html=True)
        with c3:
            best_streak = max((get_streak(data, h["id"], h["frequency"]) for h in all_habits), default=0)
            st.markdown(f'<div class="stat-card"><div class="stat-number">{best_streak}</div><div class="stat-label">Best Streak</div></div>', unsafe_allow_html=True)
        with c4:
            total_comps = sum(sum(1 for v in data["completions"].get(h["id"], {}).values() if v) for h in all_habits)
            st.markdown(f'<div class="stat-card"><div class="stat-number">{total_comps}</div><div class="stat-label">All-Time Done</div></div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='background:white; border-radius:12px; padding:16px; border:2px solid #bbf7d0; margin-bottom:20px;'>
            <div style='display:flex; justify-content:space-between; margin-bottom:8px;'>
                <span style='font-weight:700; color:#14532d;'>Overall Progress</span>
                <span style='font-weight:800; color:#16a34a;'>{pct}%</span>
            </div>
            <div class='progress-bar-bg'><div class='progress-bar-fill' style='width:{pct}%'></div></div>
        </div>
        """, unsafe_allow_html=True)

    def render_habit_section(habit_list, title, period_fn):
        if not habit_list: return
        st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)
        
        # Filter
        categories = list(set(h.get("category","Other") for h in habit_list))
        selected_cat = st.selectbox(f"Filter {title}", ["All"] + categories, key=f"filter_{title}", label_visibility="collapsed")
        if selected_cat != "All":
            habit_list = [h for h in habit_list if h.get("category","Other") == selected_cat]

        for h in habit_list:
            period = period_fn(h)
            done = is_completed(data, h["id"], period)
            streak = get_streak(data, h["id"], h["frequency"])
            rate = get_completion_rate(data, h["id"], h["frequency"])
            cat_icon = ICONS.get(h.get("category","Other"), "✨")
            
            card_class = "habit-card completed" if done else "habit-card"
            col1, col2, col3 = st.columns([0.08, 0.72, 0.2])
            
            with col1:
                checked = st.checkbox("", value=done, key=f"chk_{h['id']}_{period}")
                if checked != done:
                    mark_completion(data, h["id"], period, checked)
                    st.rerun()
            
            with col2:
                check_icon = "✅" if done else "⬜"
                tags = " ".join([f'<span class="tag-chip">{t}</span>' for t in h.get("tags", [])])
                st.markdown(f"""
                <div class="{card_class}">
                    <div style='display:flex; align-items:center; gap:8px;'>
                        <span style='font-size:1.3rem;'>{cat_icon}</span>
                        <div>
                            <div class='habit-title'>{check_icon} {h['name']}</div>
                            <div class='habit-meta'>{h.get('category','Other')} · Target: {h.get('target_days',1)}x/{h['frequency'].lower()} {tags}</div>
                            {f"<div class='habit-meta' style='color:#4b7c59; font-style:italic; margin-top:3px;'>{h.get('description','')}</div>" if h.get('description') else ""}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style='text-align:right; padding-top:8px;'>
                    <div><span class='streak-badge'>🔥 {streak} streak</span></div>
                    <div style='margin-top:6px; font-size:0.78rem; color:#4b7c59; font-weight:600;'>{rate:.0f}% rate</div>
                </div>
                """, unsafe_allow_html=True)

    render_habit_section(habits, "📅 Daily Habits", lambda h: today_str())
    render_habit_section(weekly, "📆 Weekly Habits", lambda h: week_str())
    render_habit_section(monthly, "🗓️ Monthly Habits", lambda h: month_str())

    if not all_habits:
        st.markdown("""
        <div class='info-box'>
            <b>No habits yet!</b> Go to <b>Add Habit</b> in the sidebar to create your first habit. 🌱
        </div>
        """, unsafe_allow_html=True)

def page_add_habit(data):
    st.markdown('<div class="main-title">Add New Habit</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Define your next growth goal</div>', unsafe_allow_html=True)
    
    with st.form("add_habit_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Habit Name *", placeholder="e.g., Morning Run, Read 30 mins")
            category = st.selectbox("Category", CATEGORIES)
            frequency = st.selectbox("Frequency", FREQUENCIES)
            target_days = st.number_input("Target per period", min_value=1, max_value=31, value=1)
        with col2:
            description = st.text_area("Description (optional)", placeholder="Why this habit matters to you...")
            tags_input = st.text_input("Tags (comma-separated)", placeholder="health, morning, energy")
            reminder_time = st.time_input("Reminder Time (optional)", value=None)
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        
        col3, col4 = st.columns(2)
        with col3:
            start_date = st.date_input("Start Date", value=date.today())
        with col4:
            end_date = st.date_input("End Date (optional)", value=None)
        
        goal_note = st.text_input("Your Why (motivation)", placeholder="Why do you want to build this habit?")
        
        submitted = st.form_submit_button("🌱 Add Habit", use_container_width=True)
        
        if submitted:
            if not name.strip():
                st.error("Please enter a habit name.")
            elif any(h["name"].lower() == name.strip().lower() for h in data["habits"]):
                st.error("A habit with this name already exists.")
            else:
                tags = [t.strip() for t in tags_input.split(",") if t.strip()]
                new_habit = {
                    "id": get_habit_id(name + str(datetime.now())),
                    "name": name.strip(),
                    "category": category,
                    "frequency": frequency,
                    "target_days": int(target_days),
                    "description": description.strip(),
                    "tags": tags,
                    "priority": priority,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat() if end_date else None,
                    "goal_note": goal_note.strip(),
                    "reminder_time": str(reminder_time) if reminder_time else None,
                    "created_at": datetime.now().isoformat(),
                }
                data["habits"].append(new_habit)
                save_data(data)
                st.success(f"✅ Habit **{name}** added successfully! Go to Today to start tracking.")
                st.balloons()

def page_analytics(data):
    st.markdown('<div class="main-title">Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Deep insights into your habit patterns</div>', unsafe_allow_html=True)
    
    if not data["habits"]:
        st.info("Add some habits first to see analytics.")
        return

    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "📅 Daily Trends", "📊 Habit Stats", "🔥 Streaks"])

    with tab1:
        # Weekly heatmap-style overview
        st.markdown('<div class="section-header">Last 30 Days — Daily Completion</div>', unsafe_allow_html=True)
        
        daily_habits = [h for h in data["habits"] if h["frequency"] == "Daily"]
        if daily_habits:
            dates = [date.today() - timedelta(days=i) for i in range(29, -1, -1)]
            rows = []
            for d in dates:
                total = len(daily_habits)
                done = sum(1 for h in daily_habits if is_completed(data, h["id"], d.isoformat()))
                rows.append({"date": d.isoformat(), "completed": done, "total": total, "pct": done/total*100 if total else 0})
            df = pd.DataFrame(rows)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df["date"], y=df["pct"],
                marker_color=[f"rgba(34,197,94,{0.3 + 0.7*p/100})" for p in df["pct"]],
                hovertemplate="<b>%{x}</b><br>%{y:.0f}% completed<extra></extra>"
            ))
            fig.update_layout(
                height=250, margin=dict(l=0,r=0,t=10,b=0),
                plot_bgcolor="white", paper_bgcolor="white",
                yaxis=dict(title="% Completed", range=[0,100], gridcolor="#dcfce7"),
                xaxis=dict(gridcolor="#dcfce7"),
                font=dict(family="Plus Jakarta Sans", color="#14532d")
            )
            st.plotly_chart(fig, use_container_width=True)

        # Category breakdown
        st.markdown('<div class="section-header">Completion Rate by Category</div>', unsafe_allow_html=True)
        cat_data = defaultdict(lambda: {"done": 0, "total": 0})
        for h in data["habits"]:
            cat = h.get("category","Other")
            rate = get_completion_rate(data, h["id"], h["frequency"])
            cat_data[cat]["done"] += rate
            cat_data[cat]["total"] += 1
        
        cats = list(cat_data.keys())
        rates = [cat_data[c]["done"]/cat_data[c]["total"] for c in cats]
        
        fig2 = go.Figure(go.Bar(
            x=rates, y=[f"{ICONS.get(c,'✨')} {c}" for c in cats],
            orientation="h",
            marker_color=["#22c55e" if r >= 70 else "#4ade80" if r >= 40 else "#86efac" for r in rates],
            text=[f"{r:.0f}%" for r in rates], textposition="outside"
        ))
        fig2.update_layout(
            height=max(200, len(cats)*50), margin=dict(l=0,r=60,t=10,b=0),
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(range=[0,110], gridcolor="#dcfce7", title="Completion Rate (%)"),
            font=dict(family="Plus Jakarta Sans", color="#14532d")
        )
        st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.markdown('<div class="section-header">Habit Completion Trend (Last 4 Weeks)</div>', unsafe_allow_html=True)
        daily_habits = [h for h in data["habits"] if h["frequency"] == "Daily"]
        if not daily_habits:
            st.info("No daily habits to analyze.")
        else:
            fig3 = go.Figure()
            for h in daily_habits[:6]:  # Show up to 6
                dates = [date.today() - timedelta(days=i) for i in range(27, -1, -1)]
                vals = [1 if is_completed(data, h["id"], d.isoformat()) else 0 for d in dates]
                # 7-day rolling
                rolling = []
                for i in range(len(vals)):
                    window = vals[max(0,i-6):i+1]
                    rolling.append(sum(window)/len(window)*100)
                fig3.add_trace(go.Scatter(
                    x=[d.isoformat() for d in dates], y=rolling,
                    name=h["name"], mode="lines+markers",
                    line=dict(width=2), marker=dict(size=5)
                ))
            fig3.update_layout(
                height=300, margin=dict(l=0,r=0,t=10,b=0),
                plot_bgcolor="white", paper_bgcolor="white",
                yaxis=dict(title="7-day rate (%)", range=[0,105], gridcolor="#dcfce7"),
                legend=dict(orientation="h", y=-0.2),
                font=dict(family="Plus Jakarta Sans", color="#14532d")
            )
            st.plotly_chart(fig3, use_container_width=True)
        
        # Week-over-week
        st.markdown('<div class="section-header">Week-Over-Week Performance</div>', unsafe_allow_html=True)
        weekly_data = []
        for w in range(7, -1, -1):
            week_start = date.today() - timedelta(weeks=w, days=date.today().weekday())
            week_label = week_start.strftime("W%U %b %d")
            total, done = 0, 0
            for h in daily_habits:
                for day_offset in range(7):
                    d = week_start + timedelta(days=day_offset)
                    if d <= date.today():
                        total += 1
                        if is_completed(data, h["id"], d.isoformat()): done += 1
            weekly_data.append({"week": week_label, "pct": done/total*100 if total else 0})
        
        wdf = pd.DataFrame(weekly_data)
        fig4 = go.Figure(go.Bar(
            x=wdf["week"], y=wdf["pct"],
            marker_color="#22c55e",
            text=[f"{p:.0f}%" for p in wdf["pct"]], textposition="outside"
        ))
        fig4.update_layout(
            height=220, margin=dict(l=0,r=0,t=30,b=0),
            plot_bgcolor="white", paper_bgcolor="white",
            yaxis=dict(range=[0,110], gridcolor="#dcfce7"),
            font=dict(family="Plus Jakarta Sans", color="#14532d")
        )
        st.plotly_chart(fig4, use_container_width=True)

    with tab3:
        st.markdown('<div class="section-header">Individual Habit Performance</div>', unsafe_allow_html=True)
        rows = []
        for h in data["habits"]:
            streak = get_streak(data, h["id"], h["frequency"])
            best = get_best_streak(data, h["id"], h["frequency"])
            rate = get_completion_rate(data, h["id"], h["frequency"])
            total = sum(1 for v in data["completions"].get(h["id"],{}).values() if v)
            rows.append({
                "Habit": h["name"],
                "Category": h.get("category","Other"),
                "Frequency": h["frequency"],
                "Current Streak": streak,
                "Best Streak": best,
                "Completion %": f"{rate:.0f}%",
                "Total Done": total,
                "Priority": h.get("priority","Medium")
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Radar chart
        if len(data["habits"]) >= 3:
            st.markdown('<div class="section-header">Habit Balance Radar</div>', unsafe_allow_html=True)
            cats = list(set(h.get("category","Other") for h in data["habits"]))
            vals = []
            for cat in cats:
                cat_habits = [h for h in data["habits"] if h.get("category","Other") == cat]
                avg = sum(get_completion_rate(data, h["id"], h["frequency"]) for h in cat_habits) / len(cat_habits)
                vals.append(avg)
            
            fig5 = go.Figure(go.Scatterpolar(
                r=vals + [vals[0]], theta=cats + [cats[0]],
                fill="toself",
                fillcolor="rgba(34,197,94,0.2)",
                line=dict(color="#22c55e", width=2),
                marker=dict(color="#16a34a", size=8)
            ))
            fig5.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0,100])),
                height=350, margin=dict(l=40,r=40,t=20,b=20),
                paper_bgcolor="white",
                font=dict(family="Plus Jakarta Sans", color="#14532d")
            )
            st.plotly_chart(fig5, use_container_width=True)

    with tab4:
        st.markdown('<div class="section-header">Streak Leaderboard</div>', unsafe_allow_html=True)
        streak_data = [(h["name"], get_streak(data, h["id"], h["frequency"]), 
                       get_best_streak(data, h["id"], h["frequency"]), h["frequency"]) 
                      for h in data["habits"]]
        streak_data.sort(key=lambda x: x[1], reverse=True)
        
        for i, (name, cur, best, freq) in enumerate(streak_data):
            medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
            bar_pct = min(100, cur * 3.33) if cur else 0
            st.markdown(f"""
            <div class='habit-card' style='margin-bottom:8px;'>
                <div style='display:flex; align-items:center; justify-content:space-between;'>
                    <div style='display:flex; align-items:center; gap:12px;'>
                        <span style='font-size:1.4rem;'>{medal}</span>
                        <div>
                            <div class='habit-title'>{name}</div>
                            <div class='habit-meta'>{freq} · Best: {best} streak</div>
                        </div>
                    </div>
                    <span class='streak-badge'>🔥 {cur} days</span>
                </div>
                <div class='progress-bar-bg' style='margin-top:8px;'>
                    <div class='progress-bar-fill' style='width:{bar_pct}%'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def page_calendar(data):
    st.markdown('<div class="main-title">Calendar View</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Track your consistency over time</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([0.3, 0.7])
    with col1:
        selected_month = st.date_input("Select Month", value=date.today().replace(day=1))
        habit_names = ["All Habits"] + [h["name"] for h in data["habits"] if h["frequency"] == "Daily"]
        selected_habit = st.selectbox("Select Habit", habit_names)
    
    month = selected_month.month
    year = selected_month.year
    
    daily_habits = [h for h in data["habits"] if h["frequency"] == "Daily"]
    if selected_habit != "All Habits":
        daily_habits = [h for h in daily_habits if h["name"] == selected_habit]
    
    # Build calendar
    cal = calendar.monthcalendar(year, month)
    month_name = date(year, month, 1).strftime("%B %Y")
    
    with col2:
        st.markdown(f"""
        <div style='background:white; border-radius:16px; padding:20px; border:2px solid #bbf7d0;'>
            <div style='text-align:center; font-family:Sora,sans-serif; font-size:1.3rem; font-weight:700; color:#14532d; margin-bottom:16px;'>{month_name}</div>
            <div style='display:grid; grid-template-columns: repeat(7, 1fr); text-align:center; gap:4px;'>
                {''.join([f"<div style='font-size:0.7rem; font-weight:700; color:#4b7c59; padding:4px;'>{d}</div>" for d in ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']])}
        """, unsafe_allow_html=True)
        
        calendar_html = ""
        today = date.today()
        for week in cal:
            for day in week:
                if day == 0:
                    calendar_html += "<div></div>"
                else:
                    d = date(year, month, day)
                    if daily_habits and d <= today:
                        done = sum(1 for h in daily_habits if is_completed(data, h["id"], d.isoformat()))
                        total = len(daily_habits)
                        pct = done / total if total else 0
                        if pct == 1:
                            bg = "#16a34a"; color = "white"
                        elif pct > 0.5:
                            bg = "#4ade80"; color = "#14532d"
                        elif pct > 0:
                            bg = "#bbf7d0"; color = "#14532d"
                        else:
                            bg = "#f0fdf4"; color = "#9ca3af"
                    elif d > today:
                        bg = "#f9fafb"; color = "#d1d5db"
                    else:
                        bg = "#f0fdf4"; color = "#9ca3af"
                    
                    is_today = "border:2px solid #22c55e;" if d == today else ""
                    calendar_html += f"<div style='background:{bg}; color:{color}; border-radius:8px; padding:8px 4px; font-size:0.8rem; font-weight:600; {is_today} text-align:center;'>{day}</div>"
        
        st.markdown(f"""
        <div style='display:grid; grid-template-columns: repeat(7, 1fr); gap:4px;'>
            {calendar_html}
        </div>
        <div style='display:flex; gap:16px; margin-top:16px; justify-content:center; flex-wrap:wrap;'>
            <div style='display:flex; align-items:center; gap:6px; font-size:0.75rem; color:#4b7c59;'><div style='width:14px;height:14px;background:#16a34a;border-radius:4px;'></div>100%</div>
            <div style='display:flex; align-items:center; gap:6px; font-size:0.75rem; color:#4b7c59;'><div style='width:14px;height:14px;background:#4ade80;border-radius:4px;'></div>&gt;50%</div>
            <div style='display:flex; align-items:center; gap:6px; font-size:0.75rem; color:#4b7c59;'><div style='width:14px;height:14px;background:#bbf7d0;border-radius:4px;'></div>&gt;0%</div>
            <div style='display:flex; align-items:center; gap:6px; font-size:0.75rem; color:#4b7c59;'><div style='width:14px;height:14px;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:4px;'></div>None</div>
        </div>
        </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Monthly stats
    st.markdown('<div class="section-header">Monthly Summary</div>', unsafe_allow_html=True)
    if daily_habits:
        days_in_month = calendar.monthrange(year, month)[1]
        cols = st.columns(len(daily_habits[:4]))
        for i, h in enumerate(daily_habits[:4]):
            done = sum(1 for day in range(1, min(days_in_month+1, today.day+1 if month == today.month and year == today.year else days_in_month+1))
                      if is_completed(data, h["id"], date(year, month, day).isoformat()))
            total_days = min(days_in_month, (today - date(year, month, 1)).days + 1 if month == today.month and year == today.year else days_in_month)
            pct = done/total_days*100 if total_days else 0
            with cols[i]:
                st.markdown(f'<div class="stat-card"><div class="stat-number">{done}/{total_days}</div><div class="stat-label">{h["name"][:15]}</div></div>', unsafe_allow_html=True)

def page_achievements(data):
    st.markdown('<div class="main-title">Achievements</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Your milestones & badges</div>', unsafe_allow_html=True)
    
    if not data["habits"]:
        st.info("Add habits and start tracking to earn achievements!")
        return
    
    # Overall score
    total_score = 0
    all_badges = []
    for h in data["habits"]:
        badges = get_achievements(data, h["id"], h["frequency"])
        all_badges.extend(badges)
        total_score += len(badges) * 10
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #14532d, #16a34a); border-radius:16px; padding:24px; text-align:center; margin-bottom:24px;'>
        <div style='font-family:Sora,sans-serif; font-size:3rem; font-weight:800; color:#4ade80;'>{total_score}</div>
        <div style='color:#dcfce7; font-size:1rem; font-weight:600; letter-spacing:1px;'>TOTAL ACHIEVEMENT POINTS</div>
        <div style='color:#86efac; font-size:0.85rem; margin-top:4px;'>{len(all_badges)} badges earned across all habits</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Per habit
    for h in data["habits"]:
        badges = get_achievements(data, h["id"], h["frequency"])
        streak = get_streak(data, h["id"], h["frequency"])
        rate = get_completion_rate(data, h["id"], h["frequency"])
        
        st.markdown(f'<div class="section-header">{ICONS.get(h.get("category","Other"), "✨")} {h["name"]}</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{streak}</div><div class="stat-label">Current Streak</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{rate:.0f}%</div><div class="stat-label">Completion Rate</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{len(badges)}</div><div class="stat-label">Badges Earned</div></div>', unsafe_allow_html=True)
        
        if badges:
            badge_html = "".join([f"""
            <div class='achievement-badge' style='display:inline-block; min-width:90px;'>
                <div class='achievement-icon'>{icon}</div>
                <div class='achievement-name'>{name}</div>
            </div>
            """ for icon, name in badges])
            st.markdown(f"<div style='margin:12px 0;'>{badge_html}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='info-box'>Keep going! Complete this habit to earn badges. 🌱</div>", unsafe_allow_html=True)
    
    # All badges catalog
    st.markdown('<div class="section-header">🏅 Badge Catalog</div>', unsafe_allow_html=True)
    catalog = [
        ("🔥","3-Day Streak","Complete 3 days in a row"),
        ("⚡","7-Day Streak","Complete 7 days in a row"),
        ("💎","21-Day Streak","Complete 21 days in a row"),
        ("🏆","30-Day Champion","Complete 30 days in a row"),
        ("🌟","Habit Master","Complete 66 days in a row"),
        ("🎯","80% Rate","Maintain 80% completion rate"),
        ("✅","Perfect Month","100% completion in a period"),
        ("📌","10 Completions","Complete a habit 10 times"),
        ("🥇","50 Completions","Complete a habit 50 times"),
        ("👑","100 Completions","Complete a habit 100 times"),
    ]
    cols = st.columns(5)
    for i, (icon, name, desc) in enumerate(catalog):
        with cols[i % 5]:
            earned = any(b[1] == name for b in all_badges)
            opacity = "1" if earned else "0.35"
            st.markdown(f"""
            <div style='text-align:center; padding:12px; background:{"#fef9c3" if earned else "#f0fdf4"}; 
                 border-radius:12px; border:2px solid {"#eab308" if earned else "#bbf7d0"}; 
                 margin:4px; opacity:{opacity};'>
                <div style='font-size:1.6rem;'>{icon}</div>
                <div style='font-size:0.72rem; font-weight:700; color:#14532d; margin-top:4px;'>{name}</div>
                <div style='font-size:0.65rem; color:#4b7c59; margin-top:2px;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

def page_manage(data):
    st.markdown('<div class="main-title">Manage Habits</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Edit, pause, or delete your habits</div>', unsafe_allow_html=True)
    
    if not data["habits"]:
        st.info("No habits to manage yet.")
        return
    
    for h in data["habits"]:
        cat_icon = ICONS.get(h.get("category","Other"), "✨")
        streak = get_streak(data, h["id"], h["frequency"])
        with st.expander(f"{cat_icon} {h['name']} — {h['frequency']} | 🔥 {streak} streak"):
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Name", value=h["name"], key=f"name_{h['id']}")
                new_cat = st.selectbox("Category", CATEGORIES, index=CATEGORIES.index(h.get("category","Other")), key=f"cat_{h['id']}")
                new_freq = st.selectbox("Frequency", FREQUENCIES, index=FREQUENCIES.index(h["frequency"]), key=f"freq_{h['id']}")
                new_priority = st.selectbox("Priority", ["High","Medium","Low"], index=["High","Medium","Low"].index(h.get("priority","Medium")), key=f"pri_{h['id']}")
            with col2:
                new_desc = st.text_area("Description", value=h.get("description",""), key=f"desc_{h['id']}")
                new_tags = st.text_input("Tags", value=", ".join(h.get("tags",[])), key=f"tags_{h['id']}")
                new_goal = st.text_input("Your Why", value=h.get("goal_note",""), key=f"goal_{h['id']}")
            
            col3, col4, col5 = st.columns(3)
            with col3:
                if st.button("💾 Save Changes", key=f"save_{h['id']}"):
                    h["name"] = new_name.strip()
                    h["category"] = new_cat
                    h["frequency"] = new_freq
                    h["priority"] = new_priority
                    h["description"] = new_desc.strip()
                    h["tags"] = [t.strip() for t in new_tags.split(",") if t.strip()]
                    h["goal_note"] = new_goal.strip()
                    save_data(data)
                    st.success("Saved!")
                    st.rerun()
            with col4:
                if st.button("🗄️ Archive", key=f"arch_{h['id']}"):
                    data["archived"].append(h)
                    data["habits"] = [x for x in data["habits"] if x["id"] != h["id"]]
                    save_data(data)
                    st.success("Archived!")
                    st.rerun()
            with col5:
                if st.button("🗑️ Delete", key=f"del_{h['id']}"):
                    data["habits"] = [x for x in data["habits"] if x["id"] != h["id"]]
                    if h["id"] in data["completions"]: del data["completions"][h["id"]]
                    save_data(data)
                    st.success("Deleted!")
                    st.rerun()
            
            # Progress summary
            rate = get_completion_rate(data, h["id"], h["frequency"])
            st.markdown(f"""
            <div style='background:#f0fdf4; border-radius:10px; padding:12px; margin-top:8px;'>
                <div style='font-size:0.8rem; font-weight:700; color:#4b7c59; margin-bottom:6px;'>HABIT INSIGHTS</div>
                <div style='font-size:0.85rem; color:#166534;'>📅 Started: {h.get('start_date','N/A')} &nbsp;|&nbsp; 
                📊 30-day rate: {rate:.0f}% &nbsp;|&nbsp;
                🔥 Streak: {streak} &nbsp;|&nbsp;
                ⚡ Priority: {h.get('priority','Medium')}</div>
                {f"<div style='font-size:0.8rem; color:#4b7c59; margin-top:4px; font-style:italic;'>💬 \"{h['goal_note']}\"</div>" if h.get('goal_note') else ""}
            </div>
            """, unsafe_allow_html=True)
    
    # Archived habits
    if data.get("archived"):
        st.markdown('<div class="section-header">🗄️ Archived Habits</div>', unsafe_allow_html=True)
        for h in data["archived"]:
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.markdown(f'<div class="habit-card"><div class="habit-title">🗄️ {h["name"]}</div><div class="habit-meta">{h["frequency"]} · {h.get("category","Other")}</div></div>', unsafe_allow_html=True)
            with col2:
                if st.button("↩️ Restore", key=f"restore_{h['id']}"):
                    data["habits"].append(h)
                    data["archived"] = [x for x in data["archived"] if x["id"] != h["id"]]
                    save_data(data)
                    st.rerun()

def page_journal(data):
    st.markdown('<div class="main-title">Habit Journal</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Reflect on your journey</div>', unsafe_allow_html=True)
    
    today = today_str()
    
    # Mood tracker
    st.markdown('<div class="section-header">Today\'s Check-in</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        mood = st.select_slider("How are you feeling today?", 
            options=["😔 Struggling", "😐 Neutral", "🙂 Good", "😊 Great", "🤩 Amazing"],
            value="🙂 Good", key="mood_slider")
    with col2:
        energy = st.select_slider("Energy level?",
            options=["🪫 Low", "⚡ Moderate", "🔋 High", "⚡⚡ Peak"],
            value="🔋 High", key="energy_slider")
    
    note_text = st.text_area("Today's reflection (optional):", 
        placeholder="What went well? What was challenging? Any insights about your habits?",
        height=100, key="journal_note")
    
    if st.button("📓 Save Journal Entry", use_container_width=True):
        if "notes" not in data: data["notes"] = {}
        data["notes"][today] = {
            "mood": mood, "energy": energy, "text": note_text,
            "timestamp": datetime.now().isoformat()
        }
        save_data(data)
        st.success("Journal entry saved! 📓")
    
    # Past entries
    st.markdown('<div class="section-header">Past Journal Entries</div>', unsafe_allow_html=True)
    notes = data.get("notes", {})
    if not notes:
        st.info("No journal entries yet. Write your first reflection above!")
    else:
        sorted_notes = sorted(notes.items(), key=lambda x: x[0], reverse=True)
        for date_key, entry in sorted_notes[:10]:
            d = date.fromisoformat(date_key)
            formatted = d.strftime("%A, %B %d %Y")
            st.markdown(f"""
            <div class='habit-card' style='margin-bottom:10px;'>
                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;'>
                    <div class='habit-title'>📅 {formatted}</div>
                    <div style='font-size:0.8rem; color:#4b7c59;'>{entry.get('mood','')} · {entry.get('energy','')}</div>
                </div>
                {f"<div style='font-size:0.88rem; color:#166534; font-style:italic;'>\"{entry.get('text','')}\"</div>" if entry.get('text') else "<div style='font-size:0.8rem; color:#9ca3af;'>No note written</div>"}
            </div>
            """, unsafe_allow_html=True)
    
    # Habit notes
    st.markdown('<div class="section-header">Quick Habit Notes</div>', unsafe_allow_html=True)
    if data["habits"]:
        selected = st.selectbox("Select habit", [h["name"] for h in data["habits"]])
        quick_note = st.text_input("Add a note for this habit:", placeholder="e.g., felt great today, improved my time")
        if st.button("💾 Save Habit Note"):
            habit_notes_key = f"habit_note_{selected}_{today}"
            data["notes"][habit_notes_key] = quick_note
            save_data(data)
            st.success("Note saved!")

# ─── MAIN ────────────────────────────────────────────────────────────────────
def main():
    data = load_data()
    
    with st.sidebar:
        page = sidebar_nav(data)
    
    if page == "Today":
        page_today(data)
    elif page == "Add Habit":
        page_add_habit(data)
    elif page == "Analytics":
        page_analytics(data)
    elif page == "Calendar":
        page_calendar(data)
    elif page == "Achievements":
        page_achievements(data)
    elif page == "Manage Habits":
        page_manage(data)
    elif page == "Journal":
        page_journal(data)

if __name__ == "__main__":
    main()
