import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
from typing import List, Dict, Any

# Ensure src can be imported when running from dashboard folder
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.predictor import CareerPredictor
from src.auth import AuthManager

# ---------------------- App Configuration ---------------------- #

st.set_page_config(
    page_title="SkillBridge – Career Readiness Dashboard",
    page_icon="🧭",
    layout="wide"
)

# ---------------------- Styles ---------------------- #

def inject_css():
    st.markdown(
        """
        <style>
            .main {
                background-color: #0e1117;
                color: #f5f5f5;
            }
            .metric-card {
                padding: 1rem 1.25rem;
                border-radius: 0.8rem;
                background: #111827;
                border: 1px solid #1f2937;
                box-shadow: 0 18px 45px rgba(15,23,42,0.45);
            }
            .section-header {
                font-size: 1.4rem;
                font-weight: 600;
                margin-bottom: 0.2rem;
            }
            .subtle {
                color: #9ca3af;
                font-size: 0.9rem;
            }
            .job-card {
                padding: 1rem 1.2rem;
                margin-bottom: 0.8rem;
                border-radius: 0.8rem;
                border: 1px solid #1f2937;
                background: linear-gradient(135deg,#020617,#020617 55%,#0b1120);
            }
            .badge {
                display: inline-block;
                padding: 0.15rem 0.55rem;
                border-radius: 999px;
                font-size: 0.7rem;
                margin-right: 0.25rem;
                margin-bottom: 0.25rem;
                background: #111827;
                border: 1px solid #1f2937;
            }
            .skill-badge-strong {
                border-color: #22c55e;
                color: #bbf7d0;
            }
            .skill-badge-missing {
                border-color: #ef4444;
                color: #fecaca;
            }
            .skill-badge-weak {
                border-color: #eab308;
                color: #fef9c3;
            }
            .nav-pill {
                padding: 0.35rem 0.75rem;
                border-radius: 999px;
                border: 1px solid #1f2937;
                background: #020617;
                font-size: 0.85rem;
                margin-right: 0.25rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

inject_css()

# ---------------------- Helpers ---------------------- #

@st.cache_resource(show_spinner=True)
def get_predictor() -> CareerPredictor:
    return CareerPredictor()

@st.cache_resource(show_spinner=True)
def get_auth_manager() -> AuthManager:
    db_path = os.path.join(PROJECT_ROOT, "data", "users.db")
    return AuthManager(db_path=db_path)

def ensure_session_state():
    defaults = {
        "is_authenticated": False,
        "current_user": None,
        "courses": [],
        "profile": None,
        "recommendations": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

ensure_session_state()

# ---------------------- Auth Views ---------------------- #

def login_view():
    st.title("🔐 SkillBridge Login")
    st.caption("Smart, skill-aware career path mapping for students.")

    tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

    auth = get_auth_manager()

    with tab_login:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", type="primary", use_container_width=True)

        if submitted:
            ok, msg, user = auth.login_user(username, password)

            if ok:
                st.success("Welcome back, " + (user.get("full_name") or user["username"]) + " 👋")
                st.session_state.is_authenticated = True
                st.session_state.current_user = user
                st.rerun()
            else:
                st.error(msg)

    with tab_signup:
        with st.form("signup_form"):
            full_name = st.text_input("Full name")
            username = st.text_input("Choose a username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm = st.text_input("Confirm password", type="password")
            submitted = st.form_submit_button("Create account", use_container_width=True)

        if submitted:
            if password != confirm:
                st.error("Passwords do not match.")
            elif not username or not email or not password:
                st.error("Please fill all required fields.")
            else:
                ok, msg = auth.register_user(username=username, email=email, password=password, full_name=full_name)
                if ok:
                    st.success(msg + " You can now log in.")
                else:
                    st.error(msg)

# ---------------------- Core Logic ---------------------- #

def build_profile_from_courses(courses: List[Dict[str, Any]]):
    if not courses:
        return None
    predictor = get_predictor()
    profile = predictor.build_profile(courses)
    return profile

def ensure_profile_up_to_date():
    """Rebuild profile whenever courses list changes."""
    st.session_state.profile = build_profile_from_courses(st.session_state.courses)
    if st.session_state.profile:
        predictor = get_predictor()
        st.session_state.recommendations = predictor.recommend_jobs(st.session_state.profile, top_n=20)
    else:
        st.session_state.recommendations = None

# ---------------------- Pages ---------------------- #

def page_overview():
    st.title("📊 My Career Overview")

    predictor = get_predictor()
    stats = getattr(predictor, "stats", None)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 🔎 Readiness Snapshot")
        if st.session_state.profile:
            insights = predictor.get_career_insights(st.session_state.profile)

            # Gauge chart for readiness
            fig = go.Figure(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=insights["avg_proficiency"] * 100,
                    title={"text": f"Readiness: {insights['readiness_level']}"},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"thickness": 0.3},
                        "steps": [
                            {"range": [0, 50], "color": "#1f2937"},
                            {"range": [50, 70], "color": "#374151"},
                            {"range": [70, 100], "color": "#16a34a"},
                        ],
                    },
                )
            )
            st.plotly_chart(fig, use_container_width=True)

            # Category distribution
            cat_df = pd.DataFrame(
                {
                    "Category": list(insights["skill_categories"].keys()),
                    "Skills": list(insights["skill_categories"].values()),
                }
            )
            cat_df = cat_df[cat_df["Skills"] > 0]
            if not cat_df.empty:
                bar = px.bar(cat_df, x="Category", y="Skills", title="Skill Category Distribution")
                st.plotly_chart(bar, use_container_width=True)
        else:
            st.info("Add a few courses in **My Courses & Skills** to see your readiness insights.")

    with col2:
        st.markdown("### 📌 System Stats")
        with st.container():
            if stats:
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Students (training data)", f"{int(stats['total_students']):,}")
                    st.metric("Jobs catalogued", stats["total_jobs"])
                with c2:
                    st.metric("Unique skills", stats["total_skills"])
                    st.metric("Avg skills per student", f"{stats['avg_skills_per_student']:.1f}")
            st.caption("These are dataset-level statistics used to train SkillBridge.")

        st.markdown("### ⭐ Quick Tips")
        st.write(
            "- Aim for **70%+ average proficiency** to be considered job-ready.\n"
            "- Increasing course **completion** and **grade** boosts your inferred skill scores.\n"
            "- Explore **Skill Gap Analysis** to see exactly which skills to learn next."
        )

def page_courses():
    st.title("🎓 My Courses & Skills")

    st.markdown("Add the certification courses you've completed or are currently pursuing.")
    st.caption("SkillBridge will use this information (hours, progress and score) to build a skill profile.")

    with st.expander("➕ Add / Edit Course", expanded=True):
        with st.form("course_form"):
            course_name = st.text_input("Course name", placeholder="e.g., Python for Data Science")
            col1, col2, col3 = st.columns(3)
            with col1:
                hours = st.number_input("Total hours spent", min_value=1, max_value=500, value=40)
            with col2:
                progress = st.slider("Progress (%)", 0, 100, 100)
            with col3:
                grade = st.slider("Final score / grade (%)", 0, 100, 85)

            submitted = st.form_submit_button("Add course", use_container_width=True)
        if submitted:
            if not course_name.strip():
                st.error("Please enter a course name.")
            else:
                st.session_state.courses.append(
                    {
                        "course": course_name.strip(),
                        "hours": float(hours),
                        "progress": float(progress),
                        "grade": float(grade),
                    }
                )
                ensure_profile_up_to_date()
                st.success(f"Added course: {course_name}")

    if st.session_state.courses:
        st.markdown("### 📚 Your courses")
        df = pd.DataFrame(st.session_state.courses)
        st.dataframe(df, use_container_width=True, hide_index=True)

        col_a, col_b = st.columns([1, 1])
        with col_a:
            if st.button("Recalculate skill profile", use_container_width=True):
                ensure_profile_up_to_date()
                st.success("Profile updated from courses.")
        with col_b:
            if st.button("Clear all courses", use_container_width=True, type="secondary"):
                st.session_state.courses = []
                ensure_profile_up_to_date()
                st.warning("All courses removed. Profile reset.")

    else:
        st.info("No courses added yet. Start by adding at least one course above.")

def page_jobs():
    st.title("💼 Job Recommendations")

    if not st.session_state.profile:
        st.warning("Add some courses first in **My Courses & Skills**. I need your skill profile to recommend jobs.")
        return

    predictor = get_predictor()
    if st.session_state.recommendations is None:
        st.session_state.recommendations = predictor.recommend_jobs(st.session_state.profile, top_n=20)

    recs = st.session_state.recommendations or []
    if not recs:
        st.info("No recommendations could be generated. Try adding more courses or skills.")
        return

    # Filters
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        min_match = st.slider("Minimum match percentage", 0, 100, 50, 5)
    with col2:
        sort_by = st.selectbox("Sort by", ["Match score", "Match %", "Missing skills"])
    with col3:
        max_results = st.selectbox("Number of results", [5, 10, 15, 20], index=1)

    # Apply filters
    def sort_key(rec):
        if sort_by == "Match score":
            return rec["match_score"]
        elif sort_by == "Match %":
            return rec["match_percentage"]
        else:
            return -len(rec["missing_skills"])

    filtered = [r for r in recs if r["match_percentage"] >= min_match]
    filtered = sorted(filtered, key=sort_key, reverse=True)[: max_results]

    st.markdown(f"#### Showing {len(filtered)} recommended roles")

    for rec in filtered:
        with st.container():
            st.markdown(
                f"""
                <div class="job-card">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <div style="font-size:1.05rem;font-weight:600;">{rec['title']}</div>
                            <div class="subtle">{rec['company']}</div>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-size:0.8rem;">Match</div>
                            <div style="font-size:1.3rem;font-weight:700;">{rec['match_percentage']}%</div>
                            <div style="font-size:0.8rem;color:#9ca3af;">Score {rec['match_score']}</div>
                        </div>
                    </div>
                """,
                unsafe_allow_html=True,
            )

            col_a, col_b = st.columns(2)
            with col_a:
                st.caption("Strong / matched skills")
                if rec["matched_skills"]:
                    st.markdown(
                        " ".join(
                            [f'<span class="badge skill-badge-strong">{s}</span>' for s in rec["matched_skills"]]
                        ),
                        unsafe_allow_html=True,
                    )
                else:
                    st.write("—")

            with col_b:
                st.caption("Missing skills")
                if rec["missing_skills"]:
                    st.markdown(
                        " ".join(
                            [f'<span class="badge skill-badge-missing">{s}</span>' for s in rec["missing_skills"]]
                        ),
                        unsafe_allow_html=True,
                    )
                else:
                    st.write("You meet all listed skills for this role 🎉")

            st.markdown("</div>", unsafe_allow_html=True)

    # Aggregate view
    with st.expander("📈 Summary view"):
        df = pd.DataFrame(filtered)
        if not df.empty:
            chart = px.bar(
                df,
                x="title",
                y="match_percentage",
                hover_data=["company"],
                title="Match percentage by role",
            )
            st.plotly_chart(chart, use_container_width=True)
            st.dataframe(
                df[["title", "company", "match_percentage", "match_score", "num_matched", "num_missing"]],
                use_container_width=True,
            )

def page_skill_gaps():
    st.title("🧩 Skill Gap Analysis")

    if not st.session_state.profile:
        st.warning("I need your skill profile first. Please add courses in **My Courses & Skills**.")
        return

    if not st.session_state.recommendations:
        predictor = get_predictor()
        st.session_state.recommendations = predictor.recommend_jobs(st.session_state.profile, top_n=20)

    recs = st.session_state.recommendations or []
    if not recs:
        st.info("No recommendations yet. Try widening your filters in the Jobs page.")
        return

    predictor = get_predictor()

    job_titles = [f"{r['title']} — {r['company']}" for r in recs]
    choice = st.selectbox("Choose a target job to analyse", options=job_titles)

    selected = recs[job_titles.index(choice)]
    analysis = predictor.analyze_skill_gaps(st.session_state.profile, selected)

    st.markdown(f"### Target role: **{selected['title']}** at **{selected['company']}**")

    col1, col2, col3 = st.columns(3)
    col1.metric("Current match", f"{selected['match_percentage']}%")
    col2.metric("Gap percentage", f"{analysis['gap_percentage']}%")
    col3.metric("Estimated time to close gap", f"~{analysis['estimated_weeks']} weeks")

    st.markdown("#### Missing skills (high priority)")
    if analysis["missing_skills"]:
        st.markdown(
            " ".join(
                [f'<span class="badge skill-badge-missing">{s}</span>' for s in analysis["missing_skills"]]
            ),
            unsafe_allow_html=True,
        )
    else:
        st.write("No completely missing skills for this role 🎉")

    st.markdown("#### Weak skills (need improvement)")
    weak = analysis["weak_skills"]
    if weak:
        st.markdown(
            " ".join([f'<span class="badge skill-badge-weak">{s}</span>' for s in weak]),
            unsafe_allow_html=True,
        )
    else:
        st.write("No weak skills detected for this specific role.")

    st.markdown("#### Recommended upskilling actions")
    rec_df = pd.DataFrame(analysis["recommendations"])
    st.dataframe(rec_df, use_container_width=True, hide_index=True)

def page_admin():
    st.title("🛠️ Admin / Data View")

    st.caption("Lightweight inspection tools for datasets backing SkillBridge.")
    predictor = get_predictor()

    tab_jobs, tab_stats = st.tabs(["Jobs dataset", "Training stats"])

    with tab_jobs:
        try:
            df = predictor.jobs_df.copy()
            st.dataframe(df.head(50), use_container_width=True)
            st.info(f"Total jobs loaded: {len(df)}")
        except Exception as e:
            st.error(f"Could not load jobs dataframe: {e}")

    with tab_stats:
        stats = getattr(predictor, "stats", None)
        if stats:
            st.json(stats)
        else:
            st.write("No stats available.")

# ---------------------- Main Layout ---------------------- #

def main():
    ensure_session_state()

    if not st.session_state.is_authenticated:
        login_view()
        return

    user = st.session_state.current_user
    with st.sidebar:
        st.markdown(f"### 👋 Hi, {user.get('full_name') or user['username']}")
        st.caption("Welcome to your SkillBridge career cockpit.")

        page = st.radio(
            "Navigate",
            options=[
                "Overview",
                "My Courses & Skills",
                "Job Recommendations",
                "Skill Gap Analysis",
                "Admin / Data (demo)",
            ],
        )

        if st.button("Logout", use_container_width=True):
            st.session_state.is_authenticated = False
            st.session_state.current_user = None
            st.session_state.courses = []
            st.session_state.profile = None
            st.session_state.recommendations = None
            st.rerun()

    if page == "Overview":
        page_overview()
    elif page == "My Courses & Skills":
        page_courses()
    elif page == "Job Recommendations":
        page_jobs()
    elif page == "Skill Gap Analysis":
        page_skill_gaps()
    elif page == "Admin / Data (demo)":
        page_admin()

if __name__ == "__main__":
    main()
