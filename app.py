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
import re

# ─── CONFIG & PATHS ──────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "habits_data.json")

CATEGORIES = ["Health", "Fitness", "Learning", "Productivity", "Mindfulness", "Finance", "Social", "Creative", "Other"]
ICONS = {
    "Health": "🩺",
    "Fitness": "💪",
    "Learning": "📚",
    "Productivity": "⚡",
    "Mindfulness": "🧘",
    "Finance": "💰",
    "Social": "🤝",
    "Creative": "🎨",
    "Other": "✨"
}
FREQUENCIES = ["Daily", "Weekly", "Monthly"]
PRIORITIES = ["High", "Medium", "Low"]
COLORS = ["#22c55e", "#16a34a", "#4ade80", "#86efac", "#15803d"]

st.set_page_config(
    page_title="HabitFlow — Habit Tracker",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Sora:wght@400;600;700&display=swap');

* { font-family: 'Plus Jakarta Sans', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 40%, #f0fdf4 100%) !important;
    color: #14532d;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #14532d 0%, #166534 60%, #15803d 100%) !important;
    border-right: 3px solid #22c55e !important;
}
section[data-testid="stSidebar"] * { color: #f0fdf4 !important; }
section[data-testid="stSidebar"] .stRadio label { color: #bbf7d0 !important; font-weight: 600; }
section[data-testid="stSidebar"] .stSelectbox label { color: #bbf7d0 !important; }

.main-title {
    font-family: 'Sora', sans-serif;
    font-size: 2.6rem;
    font-weight: 700;
    color: #14532d;
    letter-spacing: -1px;
    margin-bottom: 0;
}
.main-subtitle { color: #16a34a; font-size: 1rem; margin-top: 2px; margin-bottom: 16px; font-weight: 600; }

.stat-card {
    background: white;
    border-radius: 16px;
    padding: 18px 20px;
    border: 2px solid #bbf7d0;
    box-shadow: 0 4px 20px rgba(34,197,94,0.10);
    text-align: center;
    transition: transform 0.2s, box-shadow 0.2s;
}
.stat-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 30px rgba(34,197,94,0.18);
}
.stat-number {
    font-size: 2.2rem;
    font-weight: 800;
    color: #16a34a;
    font-family: 'Sora', sans-serif;
    line-height: 1.1;
}
.stat-label {
    font-size: 0.82rem;
    color: #4b7c59;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 4px;
}

.habit-card {
    background: white;
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 12px;
    border: 2px solid #bbf7d0;
    box-shadow: 0 2px 10px rgba(34,197,94,0.08);
    transition: all 0.2s ease;
}
.habit-card:hover {
    border-color: #22c55e;
    box-shadow: 0 4px 20px rgba(34,197,94,0.15);
}
.habit-card.completed {
    border-color: #22c55e;
    background: linear-gradient(135deg, #f0fdf4, #dcfce7);
}

.habit-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #14532d;
}
.habit-meta {
    font-size: 0.8rem;
    color: #4b7c59;
    margin-top: 3px;
}
.streak-badge {
    background: linear-gradient(135deg, #22c55e, #16a34a);
    color: white !important;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.76rem;
    font-weight: 700;
    display: inline-block;
    box-shadow: 0 2px 6px rgba(22,163,74,0.3);
}

.section-header {
    font-family: 'Sora', sans-serif;
    font-size: 1.35rem;
    font-weight: 700;
    color: #14532d;
    border-left: 4px solid #22c55e;
    padding-left: 12px;
    margin: 24px 0 14px 0;
}

.progress-bar-bg {
    background: #dcfce7;
    border-radius: 10px;
    height: 10px;
    overflow: hidden;
}
.progress-bar-fill {
    background: linear-gradient(90deg, #22c55e, #16a34a);
    height: 100%;
    border-radius: 10px;
    transition: width 0.4s ease;
}

div[data-testid="stCheckbox"] {
    margin: 0 !important;
    padding-top: 4px !important;
}

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

.motivational-banner {
    background: linear-gradient(135deg, #16a34a, #14532d);
    color: white;
    border-radius: 16px;
    padding: 16px 22px;
    margin-bottom: 20px;
    font-size: 1.02rem;
    font-weight: 600;
    text-align: center;
    letter-spacing: 0.2px;
    box-shadow: 0 4px 16px rgba(20,83,45,0.15);
}

.achievement-badge {
    background: linear-gradient(135deg, #fef9c3, #fef08a);
    border: 2px solid #eab308;
    border-radius: 12px;
    padding: 12px 14px;
    text-align: center;
    margin: 6px;
    box-shadow: 0 2px 8px rgba(234,179,8,0.15);
}
.achievement-icon { font-size: 1.8rem; }
.achievement-name { font-size: 0.8rem; font-weight: 700; color: #713f12; margin-top: 4px; }

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
    padding: 2px 9px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    display: inline-block;
    margin: 2px 2px;
}

.priority-chip {
    padding: 2px 9px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    display: inline-block;
    margin: 2px 2px;
}
.priority-high { background: #fee2e2; color: #b91c1c; }
.priority-medium { background: #fef3c7; color: #b45309; }
.priority-low { background: #e0f2fe; color: #0369a1; }

.info-box {
    background: white;
    border-left: 4px solid #22c55e;
    border-radius: 0 12px 12px 0;
    padding: 14px 18px;
    margin: 12px 0;
    font-size: 0.92rem;
    color: #166534;
    box-shadow: 0 2px 8px rgba(34,197,94,0.06);
}
</style>
""", unsafe_allow_html=True)

# ─── DATA LAYER ──────────────────────────────────────────────────────────────
def load_data():
    defaults = {
        "habits": [],
        "completions": {},
        "notes": {},
        "habit_notes": [],
        "archived": []
    }
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, v in defaults.items():
                    if k not in data:
                        data[k] = v

                # Migrate any legacy habit_note_ keys from notes to habit_notes
                if "notes" in data and isinstance(data["notes"], dict):
                    migrated = False
                    legacy_keys = [k for k in list(data["notes"].keys()) if str(k).startswith("habit_note_")]
                    for lk in legacy_keys:
                        val = data["notes"].pop(lk)
                        parts = lk.split("_")
                        h_name = parts[2] if len(parts) >= 3 else "Habit"
                        h_date = parts[3] if len(parts) >= 4 else date.today().isoformat()
                        data.setdefault("habit_notes", []).append({
                            "habit_name": h_name,
                            "date": h_date,
                            "text": val if isinstance(val, str) else str(val),
                            "timestamp": datetime.now().isoformat()
                        })
                        migrated = True
                    if migrated:
                        save_data(data)

                return data
        except Exception:
            return defaults
    return defaults

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        st.error(f"Error saving data: {e}")

def today_str():
    return date.today().isoformat()

def week_str(d=None):
    if d is None:
        d = date.today()
    return f"{d.isocalendar()[0]}-W{d.isocalendar()[1]:02d}"

def month_str(d=None):
    if d is None:
        d = date.today()
    return d.strftime("%Y-%m")

def get_habit_id(name):
    return hashlib.md5(f"{name}_{datetime.now().timestamp()}".encode()).hexdigest()[:8]

# ─── CORE LOGIC ──────────────────────────────────────────────────────────────
def mark_completion(data, habit_id, period_key, done):
    if habit_id not in data["completions"]:
        data["completions"][habit_id] = {}
    data["completions"][habit_id][period_key] = done
    save_data(data)

def is_completed(data, habit_id, period_key):
    return bool(data.get("completions", {}).get(habit_id, {}).get(period_key, False))

def get_streak(data, habit_id, frequency):
    comps = data.get("completions", {}).get(habit_id, {})
    today = date.today()

    if frequency == "Daily":
        # Check today first
        if comps.get(today.isoformat(), False):
            streak = 1
            cur = today - timedelta(days=1)
            while comps.get(cur.isoformat(), False):
                streak += 1
                cur -= timedelta(days=1)
            return streak
        else:
            # If today is not done yet, check if yesterday was done
            yesterday = today - timedelta(days=1)
            if comps.get(yesterday.isoformat(), False):
                streak = 1
                cur = yesterday - timedelta(days=1)
                while comps.get(cur.isoformat(), False):
                    streak += 1
                    cur -= timedelta(days=1)
                return streak
            return 0

    elif frequency == "Weekly":
        cur_wk = week_str(today)
        if comps.get(cur_wk, False):
            streak = 1
            cur = today - timedelta(weeks=1)
            while comps.get(week_str(cur), False):
                streak += 1
                cur -= timedelta(weeks=1)
            return streak
        else:
            prev_wk_date = today - timedelta(weeks=1)
            prev_wk = week_str(prev_wk_date)
            if comps.get(prev_wk, False):
                streak = 1
                cur = prev_wk_date - timedelta(weeks=1)
                while comps.get(week_str(cur), False):
                    streak += 1
                    cur -= timedelta(weeks=1)
                return streak
            return 0

    elif frequency == "Monthly":
        cur_mo = month_str(today)
        if comps.get(cur_mo, False):
            streak = 1
            first = today.replace(day=1)
            prev_mo_date = first - timedelta(days=1)
            while comps.get(month_str(prev_mo_date), False):
                streak += 1
                prev_mo_date = prev_mo_date.replace(day=1) - timedelta(days=1)
            return streak
        else:
            first = today.replace(day=1)
            prev_mo_date = first - timedelta(days=1)
            if comps.get(month_str(prev_mo_date), False):
                streak = 1
                cur = prev_mo_date.replace(day=1) - timedelta(days=1)
                while comps.get(month_str(cur), False):
                    streak += 1
                    cur = cur.replace(day=1) - timedelta(days=1)
                return streak
            return 0

    return 0

def get_best_streak(data, habit_id, frequency):
    comps = data.get("completions", {}).get(habit_id, {})
    if not comps:
        return 0

    cur_streak = get_streak(data, habit_id, frequency)
    best = cur_streak

    if frequency == "Daily":
        daily_dates = []
        for k, v in comps.items():
            if v and re.match(r"^\d{4}-\d{2}-\d{2}$", str(k)):
                try:
                    daily_dates.append(date.fromisoformat(k))
                except Exception:
                    pass
        if not daily_dates:
            return best
        daily_dates.sort()
        prev = None
        current = 0
        for d in daily_dates:
            if prev and (d - prev).days == 1:
                current += 1
            else:
                current = 1
            best = max(best, current)
            prev = d

    elif frequency == "Weekly":
        weekly_keys = []
        for k, v in comps.items():
            if v and re.match(r"^\d{4}-W\d{2}$", str(k)):
                try:
                    parts = k.split("-W")
                    weekly_keys.append((int(parts[0]), int(parts[1])))
                except Exception:
                    pass
        if not weekly_keys:
            return best
        weekly_keys.sort()
        prev_year, prev_week = None, None
        current = 0
        for yr, wk in weekly_keys:
            if prev_year is not None:
                # Same year adjacent week or new year week 1 following 52/53
                if (yr == prev_year and wk == prev_week + 1) or (yr == prev_year + 1 and prev_week in (52, 53) and wk == 1):
                    current += 1
                else:
                    current = 1
            else:
                current = 1
            best = max(best, current)
            prev_year, prev_week = yr, wk

    elif frequency == "Monthly":
        monthly_keys = []
        for k, v in comps.items():
            if v and re.match(r"^\d{4}-\d{2}$", str(k)):
                try:
                    parts = k.split("-")
                    monthly_keys.append((int(parts[0]), int(parts[1])))
                except Exception:
                    pass
        if not monthly_keys:
            return best
        monthly_keys.sort()
        prev_year, prev_month = None, None
        current = 0
        for yr, mo in monthly_keys:
            if prev_year is not None:
                diff = (yr - prev_year) * 12 + (mo - prev_month)
                if diff == 1:
                    current += 1
                else:
                    current = 1
            else:
                current = 1
            best = max(best, current)
            prev_year, prev_month = yr, mo

    return max(best, cur_streak)

def get_completion_rate(data, habit_id, frequency, days=30):
    comps = data.get("completions", {}).get(habit_id, {})
    all_habits = data.get("habits", []) + data.get("archived", [])
    habit = next((h for h in all_habits if h.get("id") == habit_id), None)

    start_d = None
    if habit and habit.get("start_date"):
        try:
            start_d = date.fromisoformat(habit["start_date"])
        except Exception:
            pass

    today = date.today()
    completed, total = 0, 0

    if frequency == "Daily":
        max_days = days
        if start_d:
            days_since = (today - start_d).days + 1
            max_days = max(1, min(days, days_since))
        for i in range(max_days):
            d = today - timedelta(days=i)
            total += 1
            if comps.get(d.isoformat(), False):
                completed += 1

    elif frequency == "Weekly":
        max_weeks = max(1, days // 7)
        if start_d:
            weeks_since = ((today - start_d).days // 7) + 1
            max_weeks = max(1, min(days // 7, weeks_since))
        for i in range(max_weeks):
            d = today - timedelta(weeks=i)
            wk = week_str(d)
            total += 1
            if comps.get(wk, False):
                completed += 1

    elif frequency == "Monthly":
        cur = today
        for _ in range(3):
            if start_d and cur.replace(day=1) < start_d.replace(day=1):
                break
            mk = month_str(cur)
            total += 1
            if comps.get(mk, False):
                completed += 1
            first = cur.replace(day=1)
            cur = first - timedelta(days=1)

    return (completed / total * 100) if total > 0 else 0

def get_achievements(data, habit_id, frequency):
    badges = []
    streak = get_streak(data, habit_id, frequency)
    best = get_best_streak(data, habit_id, frequency)
    effective_streak = max(streak, best)
    rate = get_completion_rate(data, habit_id, frequency)
    total = sum(1 for v in data.get("completions", {}).get(habit_id, {}).values() if v)

    if effective_streak >= 3:
        badges.append(("🔥", "3-Day Streak"))
    if effective_streak >= 7:
        badges.append(("⚡", "7-Day Streak"))
    if effective_streak >= 21:
        badges.append(("💎", "21-Day Streak"))
    if effective_streak >= 30:
        badges.append(("🏆", "30-Day Champion"))
    if effective_streak >= 66:
        badges.append(("🌟", "Habit Master"))

    if rate >= 80:
        badges.append(("🎯", "80% Rate"))
    if rate >= 100 and total >= 7:
        badges.append(("✅", "Perfect Period"))

    if total >= 10:
        badges.append(("📌", "10 Completions"))
    if total >= 50:
        badges.append(("🥇", "50 Completions"))
    if total >= 100:
        badges.append(("👑", "100 Completions"))

    return badges

MOTIVATIONS = [
    "🌱 Small steps every day lead to massive results.",
    "💚 You're building the life you deserve, one habit at a time.",
    "🔥 Consistency beats perfection — show up today.",
    "🚀 Your future self will thank you for what you do today.",
    "🌿 Progress, not perfection. Keep going!",
    "⚡ Every check means you're one step closer to your goal.",
    "🏆 Champions are made in the moments they don't feel like showing up.",
    "🌟 Don't break the chain. You've got this!",
]

def get_motivation():
    import random
    return random.choice(MOTIVATIONS)

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
def sidebar_nav(data):
    st.markdown("""
    <div style='text-align:center; padding: 18px 0 10px 0;'>
        <div style='font-family:Sora,sans-serif; font-size:2rem; font-weight:800; color:#4ade80; letter-spacing:-1px;'>🌱 HabitFlow</div>
        <div style='font-size:0.8rem; color:#86efac; margin-top:2px;'>Daily Growth & Goal Tracker</div>
    </div>
    """, unsafe_allow_html=True)

    total = len(data.get("habits", []))
    today_done = sum(1 for h in data.get("habits", []) if is_completed(data, h["id"], today_str()))
    st.markdown(f"""
    <div style='background:rgba(255,255,255,0.12); border-radius:12px; padding:12px 16px; margin:10px 0 18px 0; text-align:center; border:1px solid rgba(255,255,255,0.15);'>
        <div style='color:#4ade80; font-size:1.6rem; font-weight:800;'>{today_done} / {total}</div>
        <div style='color:#bbf7d0; font-size:0.75rem; font-weight:700; letter-spacing:0.8px;'>TODAY'S PROGRESS</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation Menu",
        ["📋 Today", "➕ Add Habit", "📊 Analytics", "📅 Calendar", "🏆 Achievements", "⚙️ Manage Habits", "📓 Journal"],
        label_visibility="collapsed"
    )

    st.markdown("<hr style='border-color:rgba(255,255,255,0.2); margin: 16px 0;'>", unsafe_allow_html=True)

    all_streaks = [get_streak(data, h["id"], h.get("frequency", "Daily")) for h in data.get("habits", [])]
    best_s = max(all_streaks) if all_streaks else 0
    st.markdown(f"""
    <div style='color:#86efac; font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;'>QUICK STATS</div>
    <div style='color:#dcfce7; font-size:0.84rem; margin:4px 0;'>🔥 Best active streak: <b>{best_s}</b></div>
    <div style='color:#dcfce7; font-size:0.84rem; margin:4px 0;'>📌 Active habits: <b>{total}</b></div>
    <div style='color:#dcfce7; font-size:0.84rem; margin:4px 0;'>✅ Completed today: <b>{today_done}</b></div>
    """, unsafe_allow_html=True)

    return page.split(" ", 1)[1]

# ─── PAGE: TODAY ─────────────────────────────────────────────────────────────
def page_today(data):
    top_col1, top_col2 = st.columns([0.7, 0.3])
    with top_col1:
        st.markdown('<div class="main-title">Today\'s Habits</div>', unsafe_allow_html=True)
    with top_col2:
        tracking_date = st.date_input("Tracking Date", value=date.today(), max_value=date.today() + timedelta(days=1), key="tracking_date_picker")

    selected_d = tracking_date if isinstance(tracking_date, date) else date.today()
    is_today = (selected_d == date.today())
    date_title = selected_d.strftime("%A, %B %d, %Y") + (" (Today)" if is_today else "")
    st.markdown(f'<div class="main-subtitle">{date_title}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="motivational-banner">{get_motivation()}</div>', unsafe_allow_html=True)

    all_habits = data.get("habits", [])
    daily_habits = [h for h in all_habits if h.get("frequency") == "Daily"]
    weekly_habits = [h for h in all_habits if h.get("frequency") == "Weekly"]
    monthly_habits = [h for h in all_habits if h.get("frequency") == "Monthly"]

    target_day_str = selected_d.isoformat()
    target_wk_str = week_str(selected_d)
    target_mo_str = month_str(selected_d)

    if all_habits:
        def get_target_key(h):
            freq = h.get("frequency", "Daily")
            if freq == "Daily":
                return target_day_str
            elif freq == "Weekly":
                return target_wk_str
            return target_mo_str

        done_count = sum(1 for h in all_habits if is_completed(data, h["id"], get_target_key(h)))
        pct = int(done_count / len(all_habits) * 100) if all_habits else 0

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{done_count} / {len(all_habits)}</div><div class="stat-label">Habits Done</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{pct}%</div><div class="stat-label">Completion</div></div>', unsafe_allow_html=True)
        with c3:
            best_streak = max((get_streak(data, h["id"], h.get("frequency", "Daily")) for h in all_habits), default=0)
            st.markdown(f'<div class="stat-card"><div class="stat-number">{best_streak}</div><div class="stat-label">Best Streak</div></div>', unsafe_allow_html=True)
        with c4:
            total_comps = sum(sum(1 for v in data.get("completions", {}).get(h["id"], {}).values() if v) for h in all_habits)
            st.markdown(f'<div class="stat-card"><div class="stat-number">{total_comps}</div><div class="stat-label">All-Time Done</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='background:white; border-radius:12px; padding:16px 20px; border:2px solid #bbf7d0; margin-bottom:20px; box-shadow:0 2px 10px rgba(34,197,94,0.06);'>
            <div style='display:flex; justify-content:space-between; margin-bottom:8px; align-items:center;'>
                <span style='font-weight:700; color:#14532d; font-size:0.95rem;'>Progress for {selected_d.strftime("%b %d")}</span>
                <span style='font-weight:800; color:#16a34a; font-size:1.1rem;'>{pct}%</span>
            </div>
            <div class='progress-bar-bg'><div class='progress-bar-fill' style='width:{pct}%'></div></div>
        </div>
        """, unsafe_allow_html=True)

    def render_habit_section(habit_list, title, period_key_fn):
        if not habit_list:
            return
        st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)

        categories = sorted(list(set(h.get("category", "Other") for h in habit_list)))
        if len(categories) > 1:
            selected_cat = st.selectbox(
                f"Filter {title}",
                ["All Categories"] + categories,
                key=f"filter_{title}",
                label_visibility="collapsed"
            )
            if selected_cat != "All Categories":
                habit_list = [h for h in habit_list if h.get("category", "Other") == selected_cat]

        for h in habit_list:
            period = period_key_fn(h)
            done = is_completed(data, h["id"], period)
            freq = h.get("frequency", "Daily")
            streak = get_streak(data, h["id"], freq)
            rate = get_completion_rate(data, h["id"], freq)
            cat_icon = ICONS.get(h.get("category", "Other"), "✨")

            card_class = "habit-card completed" if done else "habit-card"
            col1, col2, col3 = st.columns([0.08, 0.72, 0.20])

            with col1:
                chk_key = f"chk_{h['id']}_{period}"
                checked = st.checkbox(f"Complete {h['name']}", value=done, key=chk_key, label_visibility="collapsed")
                if checked != done:
                    mark_completion(data, h["id"], period, checked)
                    st.rerun()

            with col2:
                check_icon = "✅" if done else "⬜"
                tags_html = " ".join([f'<span class="tag-chip">{t}</span>' for t in h.get("tags", [])])
                priority = h.get("priority", "Medium").capitalize()
                pri_class = f"priority-{priority.lower()}"
                pri_chip = f'<span class="priority-chip {pri_class}">{priority}</span>'

                st.markdown(f"""
                <div class="{card_class}">
                    <div style='display:flex; align-items:flex-start; gap:12px;'>
                        <span style='font-size:1.5rem; line-height:1.2;'>{cat_icon}</span>
                        <div style='flex:1;'>
                            <div class='habit-title'>{check_icon} {h['name']}</div>
                            <div class='habit-meta'>
                                <span>{h.get('category','Other')}</span> · 
                                <span>Target: {h.get('target_days',1)}x/{freq.lower()}</span>
                                {pri_chip}
                                {tags_html}
                            </div>
                            {f"<div class='habit-meta' style='color:#15803d; font-style:italic; margin-top:4px;'>\"{h.get('description')}\"</div>" if h.get('description') else ""}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                freq_unit = "days" if freq == "Daily" else "weeks" if freq == "Weekly" else "months"
                st.markdown(f"""
                <div style='text-align:right; padding-top:10px;'>
                    <div><span class='streak-badge'>🔥 {streak} {freq_unit}</span></div>
                    <div style='margin-top:6px; font-size:0.8rem; color:#4b7c59; font-weight:700;'>{rate:.0f}% 30d rate</div>
                </div>
                """, unsafe_allow_html=True)

    render_habit_section(daily_habits, "📅 Daily Habits", lambda h: target_day_str)
    render_habit_section(weekly_habits, "📆 Weekly Habits", lambda h: target_wk_str)
    render_habit_section(monthly_habits, "🗓️ Monthly Habits", lambda h: target_mo_str)

    if not all_habits:
        st.markdown("""
        <div class='info-box'>
            <b>No habits found!</b> Head to <b>➕ Add Habit</b> in the sidebar to create your first habit and kick off your streaks! 🌱
        </div>
        """, unsafe_allow_html=True)

# ─── PAGE: ADD HABIT ─────────────────────────────────────────────────────────
def page_add_habit(data):
    st.markdown('<div class="main-title">Add New Habit</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Build momentum with intentional daily actions</div>', unsafe_allow_html=True)

    with st.form("add_habit_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Habit Name *", placeholder="e.g., Morning Run, Read 30 mins, Drink 2L Water")
            category = st.selectbox("Category", CATEGORIES)
            frequency = st.selectbox("Frequency", FREQUENCIES)
            target_days = st.number_input("Target per period", min_value=1, max_value=31, value=1)
        with col2:
            description = st.text_area("Description (optional)", placeholder="Why this habit matters to you, or specific execution details...")
            tags_input = st.text_input("Tags (comma-separated)", placeholder="health, morning, focus")
            reminder_time = st.time_input("Reminder Time (optional)", value=None)
            priority = st.selectbox("Priority", PRIORITIES, index=1)

        col3, col4 = st.columns(2)
        with col3:
            start_date = st.date_input("Start Date", value=date.today())
        with col4:
            end_date = st.date_input("End Date (optional)", value=None)

        goal_note = st.text_input("Your Why (Personal Motivation)", placeholder="What is your long-term goal with this habit?")

        submitted = st.form_submit_button("🌱 Create Habit", use_container_width=True)

        if submitted:
            cleaned_name = name.strip()
            if not cleaned_name:
                st.error("⚠️ Please enter a habit name.")
            elif any(h["name"].lower() == cleaned_name.lower() for h in data.get("habits", [])):
                st.error(f"⚠️ A habit named '{cleaned_name}' already exists.")
            else:
                tags = [t.strip() for t in tags_input.split(",") if t.strip()]
                start_str = start_date.isoformat() if hasattr(start_date, "isoformat") else str(start_date)
                end_str = end_date.isoformat() if (end_date and hasattr(end_date, "isoformat")) else None

                new_habit = {
                    "id": get_habit_id(cleaned_name),
                    "name": cleaned_name,
                    "category": category,
                    "frequency": frequency,
                    "target_days": int(target_days),
                    "description": description.strip(),
                    "tags": tags,
                    "priority": priority,
                    "start_date": start_str,
                    "end_date": end_str,
                    "goal_note": goal_note.strip(),
                    "reminder_time": str(reminder_time) if reminder_time else None,
                    "created_at": datetime.now().isoformat(),
                }
                data.setdefault("habits", []).append(new_habit)
                save_data(data)
                st.success(f"✅ Habit **{cleaned_name}** added successfully! Check it out in the Today view.")
                st.balloons()

# ─── PAGE: ANALYTICS ─────────────────────────────────────────────────────────
def page_analytics(data):
    st.markdown('<div class="main-title">Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Deep insights into your consistency and progress</div>', unsafe_allow_html=True)

    habits = data.get("habits", [])
    if not habits:
        st.info("🌱 Add some habits first to see analytics and trends.")
        return

    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "📅 Daily Trends", "📊 Habit Stats", "🔥 Streaks"])

    with tab1:
        st.markdown('<div class="section-header">Last 30 Days — Daily Completion Rate</div>', unsafe_allow_html=True)
        daily_habits = [h for h in habits if h.get("frequency") == "Daily"]

        if daily_habits:
            dates = [date.today() - timedelta(days=i) for i in range(29, -1, -1)]
            rows = []
            for d in dates:
                total = len(daily_habits)
                done = sum(1 for h in daily_habits if is_completed(data, h["id"], d.isoformat()))
                pct = (done / total * 100) if total else 0
                rows.append({"date": d.isoformat(), "completed": done, "total": total, "pct": pct})
            df = pd.DataFrame(rows)

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df["date"],
                y=df["pct"],
                marker_color=[f"rgba(34,197,94,{0.35 + 0.65*(p/100)})" for p in df["pct"]],
                hovertemplate="<b>%{x}</b><br>%{y:.0f}% completed<extra></extra>"
            ))
            fig.update_layout(
                height=260,
                margin=dict(l=0, r=0, t=10, b=0),
                plot_bgcolor="white",
                paper_bgcolor="white",
                yaxis=dict(title="% Completed", range=[0, 105], gridcolor="#dcfce7"),
                xaxis=dict(gridcolor="#dcfce7"),
                font=dict(family="Plus Jakarta Sans", color="#14532d")
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No daily habits active yet. Add daily habits to see 30-day overview.")

        # Category breakdown
        st.markdown('<div class="section-header">Completion Rate by Category</div>', unsafe_allow_html=True)
        cat_data = defaultdict(lambda: {"sum_rate": 0, "count": 0})
        for h in habits:
            cat = h.get("category", "Other")
            rate = get_completion_rate(data, h["id"], h.get("frequency", "Daily"))
            cat_data[cat]["sum_rate"] += rate
            cat_data[cat]["count"] += 1

        cats = sorted(list(cat_data.keys()))
        rates = [(cat_data[c]["sum_rate"] / cat_data[c]["count"]) if cat_data[c]["count"] else 0 for c in cats]

        fig2 = go.Figure(go.Bar(
            x=rates,
            y=[f"{ICONS.get(c,'✨')} {c}" for c in cats],
            orientation="h",
            marker_color=["#16a34a" if r >= 75 else "#22c55e" if r >= 45 else "#86efac" for r in rates],
            text=[f"{r:.0f}%" for r in rates],
            textposition="outside"
        ))
        fig2.update_layout(
            height=max(220, len(cats) * 45),
            margin=dict(l=0, r=60, t=10, b=0),
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis=dict(range=[0, 115], gridcolor="#dcfce7", title="Average Completion Rate (%)"),
            font=dict(family="Plus Jakarta Sans", color="#14532d")
        )
        st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.markdown('<div class="section-header">Habit Completion Trend (Last 4 Weeks)</div>', unsafe_allow_html=True)
        daily_habits = [h for h in habits if h.get("frequency") == "Daily"]
        if not daily_habits:
            st.info("Add daily habits to view trends and rolling averages.")
        else:
            fig3 = go.Figure()
            for h in daily_habits[:6]:
                dates = [date.today() - timedelta(days=i) for i in range(27, -1, -1)]
                vals = [1 if is_completed(data, h["id"], d.isoformat()) else 0 for d in dates]
                rolling = []
                for i in range(len(vals)):
                    window = vals[max(0, i - 6):i + 1]
                    rolling.append(sum(window) / len(window) * 100)
                fig3.add_trace(go.Scatter(
                    x=[d.isoformat() for d in dates],
                    y=rolling,
                    name=h["name"],
                    mode="lines+markers",
                    line=dict(width=2.5),
                    marker=dict(size=5)
                ))
            fig3.update_layout(
                height=310,
                margin=dict(l=0, r=0, t=10, b=0),
                plot_bgcolor="white",
                paper_bgcolor="white",
                yaxis=dict(title="7-day Rolling Rate (%)", range=[0, 105], gridcolor="#dcfce7"),
                xaxis=dict(gridcolor="#dcfce7"),
                legend=dict(orientation="h", y=-0.25),
                font=dict(family="Plus Jakarta Sans", color="#14532d")
            )
            st.plotly_chart(fig3, use_container_width=True)

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
                            if is_completed(data, h["id"], d.isoformat()):
                                done += 1
                weekly_data.append({"week": week_label, "pct": (done / total * 100) if total else 0})

            wdf = pd.DataFrame(weekly_data)
            fig4 = go.Figure(go.Bar(
                x=wdf["week"],
                y=wdf["pct"],
                marker_color="#22c55e",
                text=[f"{p:.0f}%" for p in wdf["pct"]],
                textposition="outside"
            ))
            fig4.update_layout(
                height=230,
                margin=dict(l=0, r=0, t=25, b=0),
                plot_bgcolor="white",
                paper_bgcolor="white",
                yaxis=dict(range=[0, 115], gridcolor="#dcfce7"),
                font=dict(family="Plus Jakarta Sans", color="#14532d")
            )
            st.plotly_chart(fig4, use_container_width=True)

    with tab3:
        st.markdown('<div class="section-header">Individual Habit Performance Table</div>', unsafe_allow_html=True)
        rows = []
        for h in habits:
            freq = h.get("frequency", "Daily")
            streak = get_streak(data, h["id"], freq)
            best = get_best_streak(data, h["id"], freq)
            rate = get_completion_rate(data, h["id"], freq)
            total = sum(1 for v in data.get("completions", {}).get(h["id"], {}).values() if v)
            rows.append({
                "Habit": h["name"],
                "Category": h.get("category", "Other"),
                "Frequency": freq,
                "Current Streak": streak,
                "Best Streak": best,
                "30d Rate": f"{rate:.0f}%",
                "Total Done": total,
                "Priority": h.get("priority", "Medium")
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

        cats = sorted(list(set(h.get("category", "Other") for h in habits)))
        if len(cats) >= 3:
            st.markdown('<div class="section-header">Habit Balance Radar</div>', unsafe_allow_html=True)
            vals = []
            for cat in cats:
                cat_habits = [h for h in habits if h.get("category", "Other") == cat]
                avg = sum(get_completion_rate(data, h["id"], h.get("frequency", "Daily")) for h in cat_habits) / len(cat_habits)
                vals.append(avg)

            fig5 = go.Figure(go.Scatterpolar(
                r=vals + [vals[0]],
                theta=cats + [cats[0]],
                fill="toself",
                fillcolor="rgba(34,197,94,0.22)",
                line=dict(color="#16a34a", width=2.5),
                marker=dict(color="#15803d", size=8)
            ))
            fig5.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                height=350,
                margin=dict(l=40, r=40, t=20, b=20),
                paper_bgcolor="white",
                font=dict(family="Plus Jakarta Sans", color="#14532d")
            )
            st.plotly_chart(fig5, use_container_width=True)

    with tab4:
        st.markdown('<div class="section-header">Streak Leaderboard</div>', unsafe_allow_html=True)
        streak_data = [
            (
                h["name"],
                get_streak(data, h["id"], h.get("frequency", "Daily")),
                get_best_streak(data, h["id"], h.get("frequency", "Daily")),
                h.get("frequency", "Daily"),
                h.get("category", "Other")
            )
            for h in habits
        ]
        streak_data.sort(key=lambda x: x[1], reverse=True)

        for i, (name, cur, best, freq, cat) in enumerate(streak_data):
            medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
            bar_pct = min(100, cur * 5) if cur else 0
            unit = "days" if freq == "Daily" else "weeks" if freq == "Weekly" else "months"

            st.markdown(f"""
            <div class='habit-card' style='margin-bottom:10px;'>
                <div style='display:flex; align-items:center; justify-content:space-between;'>
                    <div style='display:flex; align-items:center; gap:14px;'>
                        <span style='font-size:1.6rem;'>{medal}</span>
                        <div>
                            <div class='habit-title'>{name}</div>
                            <div class='habit-meta'>{freq} · {cat} · Best ever: <b>{best} {unit}</b></div>
                        </div>
                    </div>
                    <span class='streak-badge'>🔥 {cur} {unit}</span>
                </div>
                <div class='progress-bar-bg' style='margin-top:10px;'>
                    <div class='progress-bar-fill' style='width:{bar_pct}%'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ─── PAGE: CALENDAR ──────────────────────────────────────────────────────────
def page_calendar(data):
    st.markdown('<div class="main-title">Calendar View</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Visualize your consistency across time</div>', unsafe_allow_html=True)

    habits = data.get("habits", [])
    daily_habits = [h for h in habits if h.get("frequency") == "Daily"]

    col1, col2 = st.columns([0.32, 0.68])
    with col1:
        selected_month = st.date_input("Select Month", value=date.today().replace(day=1), key="cal_month_picker")
        habit_names = ["All Daily Habits"] + [h["name"] for h in daily_habits]
        selected_habit = st.selectbox("Select Habit", habit_names if daily_habits else ["No Habits Available"])

    month = selected_month.month if isinstance(selected_month, date) else date.today().month
    year = selected_month.year if isinstance(selected_month, date) else date.today().year

    target_habits = daily_habits
    if selected_habit != "All Daily Habits" and selected_habit != "No Habits Available":
        target_habits = [h for h in daily_habits if h["name"] == selected_habit]

    cal = calendar.monthcalendar(year, month)
    month_name = date(year, month, 1).strftime("%B %Y")
    today = date.today()

    with col2:
        st.markdown(f"""
        <div style='background:white; border-radius:16px; padding:20px 24px; border:2px solid #bbf7d0; box-shadow:0 4px 16px rgba(34,197,94,0.08);'>
            <div style='text-align:center; font-family:Sora,sans-serif; font-size:1.35rem; font-weight:700; color:#14532d; margin-bottom:14px;'>{month_name}</div>
            <div style='display:grid; grid-template-columns: repeat(7, 1fr); text-align:center; gap:4px; margin-bottom:4px;'>
                {''.join([f"<div style='font-size:0.75rem; font-weight:700; color:#4b7c59; padding:4px;'>{d}</div>" for d in ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']])}
            </div>
        """, unsafe_allow_html=True)

        calendar_html = ""
        for week in cal:
            for day in week:
                if day == 0:
                    calendar_html += "<div></div>"
                else:
                    d = date(year, month, day)
                    if target_habits and d <= today:
                        done = sum(1 for h in target_habits if is_completed(data, h["id"], d.isoformat()))
                        total = len(target_habits)
                        pct = (done / total) if total else 0
                        if pct == 1.0:
                            bg = "#16a34a"
                            color = "white"
                        elif pct >= 0.5:
                            bg = "#4ade80"
                            color = "#14532d"
                        elif pct > 0:
                            bg = "#bbf7d0"
                            color = "#14532d"
                        else:
                            bg = "#f0fdf4"
                            color = "#9ca3af"
                    elif d > today:
                        bg = "#f9fafb"
                        color = "#d1d5db"
                    else:
                        bg = "#f0fdf4"
                        color = "#9ca3af"

                    is_today_border = "border: 2px solid #16a34a;" if d == today else "border: 1px solid #dcfce7;"
                    calendar_html += f"<div style='background:{bg}; color:{color}; border-radius:8px; padding:10px 4px; font-size:0.82rem; font-weight:700; {is_today_border} text-align:center;'>{day}</div>"

        st.markdown(f"""
        <div style='display:grid; grid-template-columns: repeat(7, 1fr); gap:6px;'>
            {calendar_html}
        </div>
        <div style='display:flex; gap:16px; margin-top:16px; justify-content:center; flex-wrap:wrap;'>
            <div style='display:flex; align-items:center; gap:6px; font-size:0.75rem; color:#4b7c59;'><div style='width:14px;height:14px;background:#16a34a;border-radius:4px;'></div>100% Complete</div>
            <div style='display:flex; align-items:center; gap:6px; font-size:0.75rem; color:#4b7c59;'><div style='width:14px;height:14px;background:#4ade80;border-radius:4px;'></div>&ge; 50%</div>
            <div style='display:flex; align-items:center; gap:6px; font-size:0.75rem; color:#4b7c59;'><div style='width:14px;height:14px;background:#bbf7d0;border-radius:4px;'></div>&gt; 0%</div>
            <div style='display:flex; align-items:center; gap:6px; font-size:0.75rem; color:#4b7c59;'><div style='width:14px;height:14px;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:4px;'></div>None</div>
        </div>
        </div>
        """, unsafe_allow_html=True)

    # Monthly Summary
    st.markdown('<div class="section-header">Monthly Summary</div>', unsafe_allow_html=True)
    if daily_habits:
        days_in_month = calendar.monthrange(year, month)[1]
        if year < today.year or (year == today.year and month < today.month):
            elapsed_days = days_in_month
        elif year == today.year and month == today.month:
            elapsed_days = today.day
        else:
            elapsed_days = 0

        num_show = min(4, len(daily_habits))
        if num_show > 0:
            cols = st.columns(num_show)
            for i, h in enumerate(daily_habits[:num_show]):
                done = sum(
                    1 for day in range(1, elapsed_days + 1)
                    if is_completed(data, h["id"], date(year, month, day).isoformat())
                ) if elapsed_days > 0 else 0
                pct = (done / elapsed_days * 100) if elapsed_days > 0 else 0
                with cols[i]:
                    st.markdown(f'<div class="stat-card"><div class="stat-number">{done}/{elapsed_days}</div><div class="stat-label">{h["name"][:16]} ({pct:.0f}%)</div></div>', unsafe_allow_html=True)
    else:
        st.info("No daily habits to calculate monthly statistics.")

# ─── PAGE: ACHIEVEMENTS ──────────────────────────────────────────────────────
def page_achievements(data):
    st.markdown('<div class="main-title">Achievements</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Celebrate your milestones, trophies, and consistency badges</div>', unsafe_allow_html=True)

    habits = data.get("habits", [])
    if not habits:
        st.info("🌱 Add habits and begin tracking to unlock achievements!")
        return

    all_badges = []
    total_score = 0
    for h in habits:
        freq = h.get("frequency", "Daily")
        b = get_achievements(data, h["id"], freq)
        all_badges.extend(b)
        total_score += len(b) * 15

    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #14532d, #16a34a); border-radius:16px; padding:24px; text-align:center; margin-bottom:24px; box-shadow:0 6px 20px rgba(20,83,45,0.25);'>
        <div style='font-family:Sora,sans-serif; font-size:3.2rem; font-weight:800; color:#4ade80; line-height:1.1;'>{total_score}</div>
        <div style='color:#dcfce7; font-size:1rem; font-weight:700; letter-spacing:1px; margin-top:4px;'>TOTAL ACHIEVEMENT POINTS</div>
        <div style='color:#86efac; font-size:0.85rem; margin-top:4px;'>{len(all_badges)} badges unlocked across your habits</div>
    </div>
    """, unsafe_allow_html=True)

    # Per habit badges
    for h in habits:
        freq = h.get("frequency", "Daily")
        badges = get_achievements(data, h["id"], freq)
        streak = get_streak(data, h["id"], freq)
        rate = get_completion_rate(data, h["id"], freq)

        st.markdown(f'<div class="section-header">{ICONS.get(h.get("category","Other"), "✨")} {h["name"]}</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{streak}</div><div class="stat-label">Current Streak</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{rate:.0f}%</div><div class="stat-label">30-Day Rate</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{len(badges)}</div><div class="stat-label">Badges Unlocked</div></div>', unsafe_allow_html=True)

        if badges:
            badge_html = "".join([f"""
            <div class='achievement-badge' style='display:inline-block; min-width:95px;'>
                <div class='achievement-icon'>{icon}</div>
                <div class='achievement-name'>{name}</div>
            </div>
            """ for icon, name in badges])
            st.markdown(f"<div style='margin:12px 0;'>{badge_html}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='info-box'>Complete this habit consistently to earn your first badge! 🌱</div>", unsafe_allow_html=True)

    # All badges catalog
    st.markdown('<div class="section-header">🏅 Badge Catalog</div>', unsafe_allow_html=True)
    catalog = [
        ("🔥", "3-Day Streak", "Complete 3 periods in a row"),
        ("⚡", "7-Day Streak", "Complete 7 periods in a row"),
        ("💎", "21-Day Streak", "Complete 21 periods in a row"),
        ("🏆", "30-Day Champion", "Complete 30 periods in a row"),
        ("🌟", "Habit Master", "Complete 66 periods in a row"),
        ("🎯", "80% Rate", "Maintain 80%+ completion rate"),
        ("✅", "Perfect Period", "100% completion (min 7 done)"),
        ("📌", "10 Completions", "Complete a habit 10 times"),
        ("🥇", "50 Completions", "Complete a habit 50 times"),
        ("👑", "100 Completions", "Complete a habit 100 times"),
    ]
    cols = st.columns(5)
    for i, (icon, name, desc) in enumerate(catalog):
        with cols[i % 5]:
            earned = any(b[1] == name for b in all_badges)
            opacity = "1" if earned else "0.38"
            st.markdown(f"""
            <div style='text-align:center; padding:12px 8px; background:{"#fef9c3" if earned else "#ffffff"}; 
                 border-radius:12px; border:2px solid {"#eab308" if earned else "#bbf7d0"}; 
                 margin:4px 0; opacity:{opacity}; box-shadow:0 2px 8px rgba(0,0,0,0.04);'>
                <div style='font-size:1.8rem;'>{icon}</div>
                <div style='font-size:0.75rem; font-weight:700; color:#14532d; margin-top:4px;'>{name}</div>
                <div style='font-size:0.68rem; color:#4b7c59; margin-top:2px;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

# ─── PAGE: MANAGE HABITS ─────────────────────────────────────────────────────
def page_manage(data):
    st.markdown('<div class="main-title">Manage Habits</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Edit, archive, or remove habits</div>', unsafe_allow_html=True)

    habits = data.get("habits", [])
    if not habits and not data.get("archived"):
        st.info("No habits to manage yet. Go to ➕ Add Habit to create one.")
        return

    for h in habits:
        cat_val = h.get("category", "Other")
        cat_icon = ICONS.get(cat_val, "✨")
        freq_val = h.get("frequency", "Daily")
        streak = get_streak(data, h["id"], freq_val)

        with st.expander(f"{cat_icon} {h['name']} — {freq_val} | 🔥 {streak} streak"):
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Name", value=h["name"], key=f"name_{h['id']}")
                cat_idx = CATEGORIES.index(cat_val) if cat_val in CATEGORIES else 0
                new_cat = st.selectbox("Category", CATEGORIES, index=cat_idx, key=f"cat_{h['id']}")

                freq_idx = FREQUENCIES.index(freq_val) if freq_val in FREQUENCIES else 0
                new_freq = st.selectbox("Frequency", FREQUENCIES, index=freq_idx, key=f"freq_{h['id']}")

                pri_options = ["High", "Medium", "Low"]
                pri_cur = str(h.get("priority", "Medium")).strip().capitalize()
                pri_idx = pri_options.index(pri_cur) if pri_cur in pri_options else 1
                new_priority = st.selectbox("Priority", pri_options, index=pri_idx, key=f"pri_{h['id']}")

            with col2:
                new_desc = st.text_area("Description", value=h.get("description", ""), key=f"desc_{h['id']}")
                new_tags = st.text_input("Tags (comma-separated)", value=", ".join(h.get("tags", [])), key=f"tags_{h['id']}")
                new_goal = st.text_input("Your Why", value=h.get("goal_note", ""), key=f"goal_{h['id']}")

            col3, col4, col5 = st.columns(3)
            with col3:
                if st.button("💾 Save Changes", key=f"save_{h['id']}", use_container_width=True):
                    h["name"] = new_name.strip()
                    h["category"] = new_cat
                    h["frequency"] = new_freq
                    h["priority"] = new_priority
                    h["description"] = new_desc.strip()
                    h["tags"] = [t.strip() for t in new_tags.split(",") if t.strip()]
                    h["goal_note"] = new_goal.strip()
                    save_data(data)
                    st.success("Changes saved successfully!")
                    st.rerun()

            with col4:
                if st.button("🗄️ Archive Habit", key=f"arch_{h['id']}", use_container_width=True):
                    data.setdefault("archived", []).append(h)
                    data["habits"] = [x for x in data["habits"] if x["id"] != h["id"]]
                    save_data(data)
                    st.success(f"Archived {h['name']}!")
                    st.rerun()

            with col5:
                if st.button("🗑️ Delete Permanently", key=f"del_{h['id']}", use_container_width=True):
                    data["habits"] = [x for x in data["habits"] if x["id"] != h["id"]]
                    if h["id"] in data.get("completions", {}):
                        del data["completions"][h["id"]]
                    save_data(data)
                    st.success("Habit deleted!")
                    st.rerun()

            # Insights summary box
            rate = get_completion_rate(data, h["id"], freq_val)
            best_s = get_best_streak(data, h["id"], freq_val)
            unit = "days" if freq_val == "Daily" else "weeks" if freq_val == "Weekly" else "months"
            st.markdown(f"""
            <div style='background:#f0fdf4; border-radius:10px; padding:12px 16px; margin-top:12px; border:1px solid #bbf7d0;'>
                <div style='font-size:0.8rem; font-weight:700; color:#4b7c59; margin-bottom:4px;'>HABIT STATS</div>
                <div style='font-size:0.84rem; color:#166534;'>
                    📅 Started: <b>{h.get('start_date','N/A')}</b> &nbsp;|&nbsp; 
                    📊 30-day rate: <b>{rate:.0f}%</b> &nbsp;|&nbsp;
                    🔥 Streak: <b>{streak} {unit}</b> (Best: <b>{best_s}</b>) &nbsp;|&nbsp;
                    ⚡ Priority: <b>{h.get('priority','Medium')}</b>
                </div>
                {f"<div style='font-size:0.82rem; color:#4b7c59; margin-top:6px; font-style:italic;'>💬 \"{h['goal_note']}\"</div>" if h.get('goal_note') else ""}
            </div>
            """, unsafe_allow_html=True)

    # Archived habits
    archived = data.get("archived", [])
    if archived:
        st.markdown('<div class="section-header">🗄️ Archived Habits</div>', unsafe_allow_html=True)
        for h in archived:
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.markdown(f'<div class="habit-card"><div class="habit-title">🗄️ {h["name"]}</div><div class="habit-meta">{h.get("frequency","Daily")} · {h.get("category","Other")}</div></div>', unsafe_allow_html=True)
            with col2:
                if st.button("↩️ Restore", key=f"restore_{h['id']}", use_container_width=True):
                    data.setdefault("habits", []).append(h)
                    data["archived"] = [x for x in data["archived"] if x["id"] != h["id"]]
                    save_data(data)
                    st.rerun()

# ─── PAGE: JOURNAL ───────────────────────────────────────────────────────────
def page_journal(data):
    st.markdown('<div class="main-title">Habit Journal</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Reflect on daily energy, mindset, and habit progress</div>', unsafe_allow_html=True)

    j_tab1, j_tab2 = st.tabs(["📓 Daily Reflections", "📝 Habit Notes"])

    with j_tab1:
        st.markdown('<div class="section-header">Today\'s Check-in</div>', unsafe_allow_html=True)
        today_k = today_str()

        existing_entry = data.get("notes", {}).get(today_k, {})
        default_mood = existing_entry.get("mood", "🙂 Good") if isinstance(existing_entry, dict) else "🙂 Good"
        default_energy = existing_entry.get("energy", "🔋 High") if isinstance(existing_entry, dict) else "🔋 High"
        default_text = existing_entry.get("text", "") if isinstance(existing_entry, dict) else ""

        col1, col2 = st.columns(2)
        mood_options = ["😔 Struggling", "😐 Neutral", "🙂 Good", "😊 Great", "🤩 Amazing"]
        energy_options = ["🪫 Low", "⚡ Moderate", "🔋 High", "⚡⚡ Peak"]

        mood_idx = mood_options.index(default_mood) if default_mood in mood_options else 2
        energy_idx = energy_options.index(default_energy) if default_energy in energy_options else 2

        with col1:
            mood = st.select_slider("How are you feeling today?", options=mood_options, value=mood_options[mood_idx], key="mood_slider")
        with col2:
            energy = st.select_slider("Energy level?", options=energy_options, value=energy_options[energy_idx], key="energy_slider")

        note_text = st.text_area(
            "Today's reflection (optional):",
            value=default_text,
            placeholder="What went well today? What challenges did you face? Any wins or realizations?",
            height=100,
            key="journal_note"
        )

        if st.button("📓 Save Reflection", use_container_width=True):
            if "notes" not in data or not isinstance(data["notes"], dict):
                data["notes"] = {}
            data["notes"][today_k] = {
                "mood": mood,
                "energy": energy,
                "text": note_text.strip(),
                "timestamp": datetime.now().isoformat()
            }
            save_data(data)
            st.success("Reflection saved successfully! 📓")

        st.markdown('<div class="section-header">Past Journal Entries</div>', unsafe_allow_html=True)
        notes = data.get("notes", {})
        valid_notes = []
        for k, v in notes.items():
            if re.match(r"^\d{4}-\d{2}-\d{2}$", str(k)) and isinstance(v, dict):
                valid_notes.append((k, v))

        if not valid_notes:
            st.info("No reflections logged yet. Record your first check-in above!")
        else:
            valid_notes.sort(key=lambda x: x[0], reverse=True)
            for date_key, entry in valid_notes[:15]:
                try:
                    d = date.fromisoformat(date_key)
                    formatted_d = d.strftime("%A, %B %d, %Y")
                except Exception:
                    formatted_d = str(date_key)

                st.markdown(f"""
                <div class='habit-card' style='margin-bottom:12px;'>
                    <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;'>
                        <div class='habit-title'>📅 {formatted_d}</div>
                        <div style='font-size:0.84rem; color:#15803d; font-weight:700;'>{entry.get('mood','')} · {entry.get('energy','')}</div>
                    </div>
                    {f"<div style='font-size:0.9rem; color:#14532d; font-style:italic;'>\"{entry.get('text')}\"</div>" if entry.get('text') else "<div style='font-size:0.82rem; color:#9ca3af;'>No notes written</div>"}
                </div>
                """, unsafe_allow_html=True)

    with j_tab2:
        st.markdown('<div class="section-header">Add Habit-Specific Note</div>', unsafe_allow_html=True)
        habits = data.get("habits", [])
        if habits:
            habit_names = [h["name"] for h in habits]
            selected_h = st.selectbox("Select Habit", habit_names, key="journal_habit_select")
            habit_note_text = st.text_input("Note for this habit:", placeholder="e.g., increased pace to 5:30/km, finished chapter 4", key="journal_habit_note_input")

            if st.button("💾 Save Habit Note", key="btn_save_habit_note"):
                if habit_note_text.strip():
                    data.setdefault("habit_notes", []).append({
                        "habit_name": selected_h,
                        "date": today_str(),
                        "text": habit_note_text.strip(),
                        "timestamp": datetime.now().isoformat()
                    })
                    save_data(data)
                    st.success(f"Note added for {selected_h}!")
                    st.rerun()
                else:
                    st.warning("Please type a note before saving.")

            st.markdown('<div class="section-header">Past Habit Notes</div>', unsafe_allow_html=True)
            habit_notes = data.get("habit_notes", [])
            if not habit_notes:
                st.info("No habit notes added yet.")
            else:
                for hn in sorted(habit_notes, key=lambda x: x.get("timestamp", x.get("date", "")), reverse=True)[:20]:
                    st.markdown(f"""
                    <div class='habit-card' style='margin-bottom:10px;'>
                        <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;'>
                            <div class='habit-title' style='color:#16a34a;'>📌 {hn.get('habit_name','Habit')}</div>
                            <div style='font-size:0.78rem; color:#4b7c59; font-weight:600;'>{hn.get('date','')}</div>
                        </div>
                        <div style='font-size:0.88rem; color:#14532d;'>{hn.get('text','')}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Add active habits first to log habit-specific notes.")

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
