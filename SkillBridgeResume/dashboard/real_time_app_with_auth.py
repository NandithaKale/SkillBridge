import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
import hashlib
import json
import sqlite3

# HARDCODED PATH (change if needed)
sys.path.insert(0, r'C:\Users\Rishika Gitta\OneDrive\Desktop\SkillBridgeResume')
sys.path.insert(0, r'C:\Users\Rishika Gitta\OneDrive\Desktop\SkillBridgeResume\src')

# Now import
from predictor import CareerPredictor
from auth import AuthManager
from email_service import EmailService
from resume_parser import ResumeParser

# Rest of your code...

# Page config
st.set_page_config(
    page_title="SkillBridge - Real-Time Career Predictor",
    page_icon="🎓",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .big-font {
        font-size: 24px !important;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-card {
        background-color: #f0f8ff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .skill-badge {
        display: inline-block;
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 5px 12px;
        border-radius: 15px;
        margin: 3px;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize
@st.cache_resource
def load_predictor():
    try:
        return CareerPredictor()
    except Exception as e:
        st.error(f"❌ Error loading system: {e}")
        st.info("Make sure you've run: python setup_system.py")
        st.stop()

@st.cache_resource
def load_auth():
    return AuthManager()

# ADD THESE TWO FUNCTIONS HERE (before show_login_page)
@st.cache_data(ttl=3600)
def analyze_courses(courses_json):
    """Cache analysis results to avoid recomputing"""
    courses_data = json.loads(courses_json)
    predictor = load_predictor()
    
    profile = predictor.build_profile(courses_data)
    recommendations = predictor.recommend_jobs(profile, top_n=10)
    insights = predictor.get_career_insights(profile)
    
    return profile, recommendations, insights

def get_courses_hash(courses_data):
    """Create a hash of courses data for caching"""
    sorted_courses = sorted(courses_data, key=lambda x: x['course'])
    courses_str = json.dumps(sorted_courses, sort_keys=True)
    return hashlib.md5(courses_str.encode()).hexdigest()

predictor = load_predictor()
auth_manager = load_auth()

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'profile' not in st.session_state:
    st.session_state['profile'] = None
if 'recommendations' not in st.session_state:
    st.session_state['recommendations'] = None
if 'insights' not in st.session_state:
    st.session_state['insights'] = None
if 'courses_data' not in st.session_state:
    st.session_state['courses_data'] = None
if 'courses_hash' not in st.session_state:
    st.session_state['courses_hash'] = None

# NOW your show_login_page() and show_main_app() functions continue...
def show_login_page():
    # ... rest of your code
    """Display login/signup page"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div style='text-align: center; padding: 40px 0 20px 0;'>
                <h1 style='color: #1f77b4; font-size: 48px;'>🎓 SkillBridge</h1>
                <p style='color: #666; font-size: 20px;'>Your AI-Powered Career Matching Platform</p>
            </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        with tab1:
            st.markdown("### Login to Your Account")
            st.markdown("---")
            
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                
                col_a, col_b, col_c = st.columns([1, 2, 1])
                with col_b:
                    login_btn = st.form_submit_button("Login", use_container_width=True, type="primary")
                
                if login_btn:
                    if username and password:
                        success, user_data = auth_manager.login_user(username, password)
                        if success:
                            st.session_state['logged_in'] = True
                            st.session_state['user'] = user_data
                            # Don't load courses here - just login instantly
                            st.success(f"✅ Welcome back, {user_data['full_name'] or username}!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password")
                    else:
                        st.warning("⚠️ Please fill in all fields")
        
        with tab2:
            st.markdown("### Create New Account")
            st.markdown("---")
            
            with st.form("signup_form"):
                new_username = st.text_input("Username*", placeholder="Choose a username")
                new_email = st.text_input("Email*", placeholder="your.email@example.com")
                new_fullname = st.text_input("Full Name", placeholder="Your full name (optional)")
                new_password = st.text_input("Password*", type="password", placeholder="Create a password (min 6 characters)")
                confirm_password = st.text_input("Confirm Password*", type="password", placeholder="Re-enter password")
                
                col_a, col_b, col_c = st.columns([1, 2, 1])
                with col_b:
                    signup_btn = st.form_submit_button("Sign Up", use_container_width=True, type="primary")
                
                if signup_btn:
                    if new_username and new_email and new_password:
                        if new_password == confirm_password:
                            if len(new_password) < 6:
                                st.error("❌ Password must be at least 6 characters long")
                            else:
                                success, message = auth_manager.register_user(
                                    new_username, new_email, new_password, new_fullname
                                )
                                if success:
                                    st.success("✅ Registration successful! Please login.")
                                else:
                                    st.error(f"❌ {message}")
                        else:
                            st.error("❌ Passwords don't match")
                    else:
                        st.warning("⚠️ Please fill in all required fields (*)")
        
        st.markdown("---")
        st.markdown("""
            <div style='text-align: center; color: #666; padding: 20px;'>
                <p style='font-size: 14px;'>
                    Trained on 10,000+ student profiles | 100+ job postings | 50+ unique skills
                </p>
            </div>
        """, unsafe_allow_html=True)

# ============================================================================
# MAIN APPLICATION
# ============================================================================
def show_main_app():
    """Display main application after login"""
    
    # Title with user info and logout
    col1, col2 = st.columns([5, 1])
    
    with col1:
        st.markdown("# 🎓 SkillBridge - Real-Time Career Predictor")
        st.markdown(f"### Welcome back, {st.session_state['user']['full_name'] or st.session_state['user']['username']}!")
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            # Clear session state
            for key in ['logged_in', 'user', 'profile', 'recommendations', 'insights', 'courses_data']:
                if key in st.session_state:
                    st.session_state[key] = None if key != 'logged_in' else False
            st.rerun()
    
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.markdown("""
            <div style='background: #4CAF50; padding: 20px; border-radius: 10px; text-align: center;'>
                <h2 style='color: white; margin: 0;'>🎓 SkillBridge</h2>
                <p style='color: #e8f5e9; margin: 5px 0 0 0;'>Career Matching System</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        
        # User info
        st.markdown(f"### 👤 {st.session_state['user']['username']}")
        st.markdown(f"📧 {st.session_state['user']['email']}")
        
        # Quick check for saved courses without loading them
        has_courses = auth_manager.has_saved_courses(st.session_state['user']['user_id'])
        if has_courses:
            # Just count, don't load
            import sqlite3
            conn = sqlite3.connect(auth_manager.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM user_courses WHERE user_id = ?', 
                          (st.session_state['user']['user_id'],))
            count = cursor.fetchone()[0]
            conn.close()
            st.success(f"📚 {count} courses saved")
        
        st.markdown("---")
        st.markdown("### 📊 System Info")
        st.info(f"""
        **Matching Algorithm:** NLP-Powered Semantic Matching
        
        **NLP Features:**
        - 🧠 Semantic skill understanding
        - 🔄 Synonym matching (ML = machine learning)
        - 📊 Similarity scoring using spaCy
        
        **Training Data:**
        - Students: {predictor.stats['total_students']:,}
        - Jobs: {predictor.stats['total_jobs']}
        - Unique Skills: {predictor.stats['total_skills']}
        
        **Match Score (0-100):**
        - 40 pts: Skill Coverage
        - 50 pts: Proficiency Level (weighted by similarity)
        - 10 pts: High-Value Skills
        
        **How it works:**
        1. Select courses you've taken
        2. Enter progress, grades, hours
        3. NLP builds your skill profile
        4. Semantic matching finds jobs (0-100 score)
        5. Shows skill gaps & learning paths
        """)
        
        st.markdown("---")
        st.success("✅ **NLP-Powered Matching** - Understands skill variations & synonyms!")

    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Input & Predict", "💼 Job Recommendations", "📊 Analysis", "🎯 Career Insights"])

# ... (keep all imports and initialization code same as before until TAB 1)

    # ============================================================================
    # TAB 1: INPUT & PREDICT - MODIFIED TO SHOW ALL COURSES
    # ============================================================================
    with tab1:
        st.subheader("📝 Manage Your Courses")
        
        # ============================================================================
        # RESUME PARSER - NEW FEATURE
        # ============================================================================
        st.markdown("---")
        st.markdown("### 🚀 Quick Start: Upload Your Resume")
        
        with st.expander("📄 Upload Resume to Auto-Detect Skills", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.info("""
                **Automatically extract skills from your resume!**
                
                Upload your PDF resume and we'll:
                - 🔍 **Extract your skills** automatically
                - 📚 **Suggest relevant courses** based on skills
                - 📊 **Estimate your experience** level
                - ⚡ **Add missing skills** to your profile
                - 💾 **Save time** on manual entry
                
                *Your resume is processed locally and never stored.*
                """)
            
            with col2:
                uploaded_file = st.file_uploader(
                    "Upload Resume (PDF)",
                    type=['pdf'],
                    help="Upload your resume in PDF format (text-based, not scanned)",
                    key="resume_upload"
                )
            
            if uploaded_file is not None:
                # Parse the resume
                with st.spinner("🔍 Analyzing your resume... This may take a few seconds."):
                    parser = ResumeParser(predictor.course_skills)
                    result, error = parser.parse_resume(uploaded_file)
                
                if error:
                    st.error(f"❌ {error}")
                    st.info("💡 **Tips:**\n- Make sure your PDF is text-based (not a scanned image)\n- Try converting your resume to PDF again\n- Use a different PDF viewer to save it")
                else:
                    st.success("✅ Resume parsed successfully!")
                    
                    # Display results in columns
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("🔧 Skills Found", len(result['skills']))
                    with col2:
                        st.metric("⏱️ Experience", f"{result['experience_years']} years")
                    with col3:
                        st.metric("🎓 Education", result['education'])
                    with col4:
                        st.metric("📚 Suggested Courses", len(result['suggested_courses']))
                    
                    st.markdown("---")
                    
                    # Show detected skills
                    if result['skills']:
                        st.markdown("#### 🔧 Detected Skills from Your Resume")
                        skills_html = "".join([
                            f'<span class="skill-badge">{skill}</span>' 
                            for skill in result['skills']
                        ])
                        st.markdown(skills_html, unsafe_allow_html=True)
                        st.caption(f"Found {len(result['skills'])} skills in your resume")
                    else:
                        st.warning("⚠️ No specific technical skills detected. You can still add courses manually below.")
                    
                    st.markdown("---")
                    
                    # Show suggested courses based on detected skills
                    if result['suggested_courses']:
                        st.markdown("#### 📚 Recommended Courses Based on Your Skills")
                        st.success(f"We found **{len(result['suggested_courses'])} relevant courses** for you!")
                        
                        # Get currently enrolled courses
                        saved_courses = auth_manager.get_user_courses(st.session_state['user']['user_id'])
                        enrolled_course_names = [c['course'] for c in saved_courses] if saved_courses else []
                        
                        # Filter out already enrolled courses
                        available_suggestions = [c for c in result['suggested_courses'] if c not in enrolled_course_names]
                        
                        if not available_suggestions:
                            st.info("✅ Great! You've already enrolled in all recommended courses based on your resume skills.")
                        else:
                            st.markdown(f"**Select courses to add to your profile:** ({len(available_suggestions)} new courses available)")
                            
                            # Show suggested courses with checkboxes
                            selected_courses = []
                            
                            # Show in 2 columns for better layout
                            col1, col2 = st.columns(2)
                            
                            for idx, course in enumerate(available_suggestions[:15]):  # Show max 15
                                with col1 if idx % 2 == 0 else col2:
                                    # Get skills for this course
                                    course_skills = predictor.course_skills.get(course, [])
                                    skills_preview = ', '.join(course_skills[:3])
                                    if len(course_skills) > 3:
                                        skills_preview += f" +{len(course_skills)-3} more"
                                    
                                    if st.checkbox(
                                        f"📖 **{course}**",
                                        key=f"suggest_{idx}",
                                        help=f"Skills: {skills_preview}"
                                    ):
                                        selected_courses.append(course)
                            
                            if selected_courses:
                                st.markdown("---")
                                st.markdown("**💡 Set default values for selected courses:**")
                                st.caption("You can adjust these values later from your course history")
                                
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    default_progress = st.slider(
                                        "Default Progress (%)", 
                                        0, 100, 75, 5,
                                        help="Estimated completion percentage",
                                        key="def_prog"
                                    )
                                with col2:
                                    default_grade = st.slider(
                                        "Default Grade (%)", 
                                        0, 100, 80, 5,
                                        help="Expected or average grade",
                                        key="def_grade"
                                    )
                                with col3:
                                    default_hours = st.number_input(
                                        "Default Hours", 
                                        0, 200, 40, 5,
                                        help="Estimated hours spent learning",
                                        key="def_hours"
                                    )
                                
                                # Add courses button
                                col1, col2, col3 = st.columns([1, 2, 1])
                                with col2:
                                    if st.button(
                                        f"➕ Add {len(selected_courses)} Selected Course(s) to Profile",
                                        type="primary",
                                        use_container_width=True
                                    ):
                                        # Create courses data
                                        new_courses = [
                                            {
                                                'course': course,
                                                'progress': default_progress,
                                                'grade': default_grade,
                                                'hours': default_hours
                                            }
                                            for course in selected_courses
                                        ]
                                        
                                        # Save to database
                                        with st.spinner("💾 Saving courses and recalculating..."):
                                            auth_manager.save_courses(
                                                st.session_state['user']['user_id'],
                                                new_courses
                                            )
                                            
                                            # Get all courses and analyze
                                            all_courses = auth_manager.get_user_courses(
                                                st.session_state['user']['user_id']
                                            )
                                            
                                            courses_json = json.dumps(all_courses, sort_keys=True)
                                            profile, recommendations, insights = analyze_courses(courses_json)
                                            
                                            st.session_state['profile'] = profile
                                            st.session_state['recommendations'] = recommendations
                                            st.session_state['insights'] = insights
                                            st.session_state['courses_data'] = all_courses
                                            st.session_state['courses_hash'] = get_courses_hash(all_courses)
                                        
                                        st.success(f"✅ Added {len(selected_courses)} courses from your resume!")
                                        st.balloons()
                                        st.info("📊 Your profile has been updated with resume skills. Check Tab 2 for new job recommendations!")
                                        st.rerun()
                            else:
                                st.info("👆 Select courses above to add them to your profile")
                    else:
                        st.info("💡 No direct course matches found. You can manually add courses below.")
                    
                    # Show contact info if found
                    if result['email'] or result['phone']:
                        st.markdown("---")
                        with st.expander("📞 Contact Information Detected"):
                            if result['email']:
                                st.write(f"📧 **Email:** {result['email']}")
                            if result['phone']:
                                st.write(f"📱 **Phone:** {result['phone']}")
        
        st.markdown("---")
        
        # ============================================================================
        # REST OF YOUR EXISTING TAB 1 CODE (Course Management)
        # ============================================================================
        # ... keep all your existing code for showing saved courses, adding manually, etc.        
        # Always load saved courses if they exist
        saved_courses = auth_manager.get_user_courses(st.session_state['user']['user_id'])
        
        if saved_courses:
            # Show all saved courses
            st.success(f"📚 You have {len(saved_courses)} courses in your profile")
            
            # Option to view courses
            with st.expander(f"📖 View All {len(saved_courses)} Saved Courses", expanded=False):
                for i, course in enumerate(saved_courses, 1):
                    col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{i}. {course['course']}**")
                    with col2:
                        st.markdown(f"📈 {course['progress']}%")
                    with col3:
                        st.markdown(f"🎓 {course['grade']}%")
                    with col4:
                        st.markdown(f"⏱️ {course['hours']}h")
                    with col5:
                        # Delete individual course button
                        if st.button("🗑️", key=f"del_{i}", help="Delete this course"):
                            auth_manager.delete_course(
                                st.session_state['user']['user_id'],
                                course['course']
                            )
                            st.success(f"✅ Deleted {course['course']}")
                            # Clear cached results
                            st.session_state['courses_hash'] = None
                            st.rerun()
                    
                    st.markdown("---")
            
            # Buttons for actions
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔄 Recalculate Results from All Courses", use_container_width=True, type="primary"):
                    with st.spinner("⚡ Calculating from all courses..."):
                        # Use all saved courses
                        courses_hash = get_courses_hash(saved_courses)
                        courses_json = json.dumps(saved_courses, sort_keys=True)
                        profile, recommendations, insights = analyze_courses(courses_json)
                        
                        st.session_state['profile'] = profile
                        st.session_state['recommendations'] = recommendations
                        st.session_state['insights'] = insights
                        st.session_state['courses_data'] = saved_courses
                        st.session_state['courses_hash'] = courses_hash
                    
                    st.success(f"✅ Results calculated from all {len(saved_courses)} courses!")
                    st.rerun()
            
            with col2:
                if st.button("➕ Add More Courses", use_container_width=True):
                    st.session_state['show_add_form'] = True
                    st.rerun()
            
            with col3:
                if st.button("🗑️ Delete All Courses", use_container_width=True, type="secondary"):
                    if st.session_state.get('confirm_delete'):
                        auth_manager.delete_all_courses(st.session_state['user']['user_id'])
                        st.session_state['courses_data'] = None
                        st.session_state['profile'] = None
                        st.session_state['recommendations'] = None
                        st.session_state['insights'] = None
                        st.session_state['courses_hash'] = None
                        st.session_state['confirm_delete'] = False
                        st.success("✅ All courses deleted!")
                        st.rerun()
                    else:
                        st.session_state['confirm_delete'] = True
                        st.warning("⚠️ Click again to confirm deletion")
            
            # Show current results if available
            if st.session_state['profile']:
                st.markdown("---")
                st.markdown("### 📊 Current Results Overview")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    top_match = st.session_state['recommendations'][0]['match_score'] if st.session_state['recommendations'] else 0
                    st.metric("🎯 Best Match Score", f"{top_match:.1f}/100")
                
                with col2:
                    st.metric("🔧 Total Skills", len(st.session_state['profile']))
                
                with col3:
                    st.metric("💼 Career Path", st.session_state['insights']['dominant_category'])
                
                with col4:
                    st.metric("📈 Readiness", st.session_state['insights']['readiness_level'])
                
                st.info("💡 These results are based on all your saved courses. Add more courses to improve your profile!")
            
            st.markdown("---")
        
        # Show form to add new courses (or first-time entry)
        show_form = not saved_courses or st.session_state.get('show_add_form', False)
        
        if show_form:
            if saved_courses:
                st.subheader("➕ Add More Courses to Your Profile")
                st.info(f"Currently you have {len(saved_courses)} courses. Add more below:")
            else:
                st.subheader("📝 Enter Your First Courses")
            
            # Available courses - exclude already taken ones
            available_courses = list(predictor.course_skills.keys())
            if saved_courses:
                taken_courses = [c['course'] for c in saved_courses]
                available_courses = [c for c in available_courses if c not in taken_courses]
                
                if not available_courses:
                    st.warning("⚠️ You've already added all available courses!")
                    if st.button("Done Adding Courses"):
                        st.session_state['show_add_form'] = False
                        st.rerun()
                    return
            
            # Number of NEW courses to add
            num_courses = st.number_input(
                "How many NEW courses do you want to add?", 
                min_value=1, 
                max_value=min(15, len(available_courses)), 
                value=min(3, len(available_courses))
            )
            
            st.markdown("---")
            
            # Input for each NEW course
            new_courses_data = []
            
            for i in range(num_courses):
                with st.container():
                    st.markdown(f"### 📚 New Course {i+1}")
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        course_name = st.selectbox(
                            "Course Name",
                            available_courses,
                            key=f"new_course_{i}"
                        )
                    
                    with col2:
                        st.markdown("**Skills you'll gain:**")
                        skills = predictor.course_skills[course_name]
                        skills_html = "".join([f'<span class="skill-badge">{s}</span>' for s in skills[:4]])
                        st.markdown(skills_html, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        progress = st.slider(
                            "📈 Progress (%)",
                            0, 100, 80,
                            help="How much of the course have you completed?",
                            key=f"new_progress_{i}"
                        )
                    
                    with col2:
                        grade = st.slider(
                            "🎓 Grade (%)",
                            0, 100, 85,
                            help="Your grade/score in this course",
                            key=f"new_grade_{i}"
                        )
                    
                    with col3:
                        hours = st.number_input(
                            "⏱️ Hours Spent",
                            0, 200, 40,
                            help="Total hours spent learning",
                            key=f"new_hours_{i}"
                        )
                    
                    new_courses_data.append({
                        'course': course_name,
                        'progress': progress,
                        'grade': grade,
                        'hours': hours
                    })
                    
                    st.markdown("---")
            
            # Save/Add button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if saved_courses:
                    button_text = f"➕ Add {len(new_courses_data)} Course(s) & Recalculate"
                else:
                    button_text = f"🚀 Save & Analyze {len(new_courses_data)} Course(s)"
                
                add_btn = st.button(button_text, type="primary", use_container_width=True)
            
            if add_btn:
                with st.spinner("💾 Saving courses and recalculating..."):
                    # Save NEW courses to database (will add to existing ones)
                    auth_manager.save_courses(st.session_state['user']['user_id'], new_courses_data)
                    
                    # Get ALL courses (old + new)
                    all_courses = auth_manager.get_user_courses(st.session_state['user']['user_id'])
                    
                    # Analyze ALL courses together
                    courses_json = json.dumps(all_courses, sort_keys=True)
                    profile, recommendations, insights = analyze_courses(courses_json)
                    
                    # Save to session state
                    st.session_state['profile'] = profile
                    st.session_state['recommendations'] = recommendations
                    st.session_state['insights'] = insights
                    st.session_state['courses_data'] = all_courses
                    st.session_state['courses_hash'] = get_courses_hash(all_courses)
                    st.session_state['show_add_form'] = False
                
                st.balloons()
                st.success(f"✅ Added {len(new_courses_data)} new course(s)! Total: {len(all_courses)} courses. Results updated!")
                st.rerun()
            
            # Cancel button if adding to existing
            if saved_courses:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("❌ Cancel", use_container_width=True):
                        st.session_state['show_add_form'] = False
                        st.rerun()
  
    # ============================================================================
    # TAB 2: JOB RECOMMENDATIONS
    # ============================================================================
    with tab2:
        if st.session_state['recommendations'] is None:
            st.info("👈 Please enter your course information in the 'Input & Predict' tab first!")
        else:
            recommendations = st.session_state['recommendations']
            profile = st.session_state['profile']
            
            st.subheader("💼 Your Top Job Matches")
            st.markdown(f"*Based on your {len(profile)} acquired skills*")
            
            # Add explanation
            with st.expander("ℹ️ Understanding Match Scores", expanded=False):
                st.markdown("""
                **Match Score is calculated out of 100 points:**
                
                - **40 points** - Skill Coverage (How many required skills you have)
                - **50 points** - Proficiency Level (How good you are at those skills)
                - **10 points** - High-Value Skills Bonus (Having in-demand skills like Python, ML, AWS)
                
                **Score Ranges:**
                - **80-100**: Excellent match - You're highly qualified!
                - **60-79**: Good match - You have most skills needed
                - **40-59**: Fair match - Some skill gaps exist
                - **Below 40**: Poor match - Significant gaps
                
                **Why coverage % differs from score:**
                - You might have 80% of skills but only at beginner level → Lower score (e.g., 55/100)
                - You might have 60% of skills but at expert level → Higher score (e.g., 70/100)
                
                **Focus on:** Jobs with scores above 70 for best fit!
                """)
            
            st.markdown("---")
            
            # Display top 5 recommendations
            for i, rec in enumerate(recommendations[:5], 1):
                
                # Color based on match score
                if rec['match_score'] >= 80:
                    header_color = "🟢"
                    badge_color = "success"
                elif rec['match_score'] >= 60:
                    header_color = "🟡"
                    badge_color = "warning"
                else:
                    header_color = "🟠"
                    badge_color = "error"
                
                with st.expander(
                    f"{header_color} **#{i}** {rec['title']} at {rec['company']} - **{rec['match_score']:.0f}/100 Match** ({rec['match_percentage']:.0f}% skills)",
                    expanded=(i==1)
                ):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        # Match metrics
                        metric_col1, metric_col2, metric_col3 = st.columns(3)
                        with metric_col1:
                            st.metric("Overall Score", f"{rec['match_score']:.0f}/100")
                        with metric_col2:
                            st.metric("Skills Match", f"{rec['num_matched']}/{rec['num_required']}")
                        with metric_col3:
                            st.metric("Coverage", f"{rec['match_percentage']:.0f}%")
                        
                        st.markdown("---")
                        
                        # Matched skills
                        st.markdown("**✅ Your Matching Skills:**")
                        if rec['matched_skills']:
                            for skill in rec['matched_skills']:
                                prof = profile.get(skill, 0)
                                level = predictor.get_skill_level(prof)
                                
                                # Color code by level
                                if level == "Expert":
                                    level_color = "🟢"
                                elif level == "Advanced":
                                    level_color = "🔵"
                                elif level == "Intermediate":
                                    level_color = "🟡"
                                else:
                                    level_color = "🟠"
                                
                                st.markdown(f"{level_color} **{skill}** → {level} ({prof:.2f})")
                        else:
                            st.warning("No matching skills found")
                        
                        # Missing skills
                        if rec['missing_skills']:
                            st.markdown("**❌ Skills You Need to Learn:**")
                            missing_html = "".join([f'<span class="skill-badge" style="background-color: #ffebee; color: #c62828;">{s}</span>' 
                                                  for s in rec['missing_skills']])
                            st.markdown(missing_html, unsafe_allow_html=True)
                    
                    with col2:
                        # Gauge chart
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=rec['match_score'],
                            title={'text': "Score", 'font': {'size': 16}},
                            domain={'x': [0, 1], 'y': [0, 1]},
                            gauge={
                                'axis': {'range': [0, 100], 'tickwidth': 1},
                                'bar': {'color': "darkgreen" if rec['match_score'] >= 70 else "orange"},
                                'bgcolor': "white",
                                'borderwidth': 2,
                                'bordercolor': "gray",
                                'steps': [
                                    {'range': [0, 40], 'color': '#ffcdd2'},
                                    {'range': [40, 60], 'color': '#fff9c4'},
                                    {'range': [60, 80], 'color': '#c8e6c9'},
                                    {'range': [80, 100], 'color': '#81c784'}
                                ],
                                'threshold': {
                                    'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75,
                                    'value': 70
                                }
                            }
                        ))
                        fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
                        st.plotly_chart(fig, use_container_width=True, key=f"gauge_{i}")
                    
                    # Learning path button
                    st.markdown("---")
                    if st.button(f"📚 View Learning Path for {rec['title']}", key=f"gap_btn_{i}"):
                        gap_analysis = predictor.analyze_skill_gaps(profile, rec)
                        
                        st.markdown("### 🎯 Recommended Learning Path")
                        
                        if gap_analysis['recommendations']:
                            for j, rec_item in enumerate(gap_analysis['recommendations'][:5], 1):
                                priority_emoji = "🔴" if rec_item['priority'] == "HIGH" else "🟡"
                                
                                st.markdown(f"{priority_emoji} **{j}. {rec_item['skill']}**")
                                st.markdown(f"   *Current Level:* {rec_item['current_level']}")
                                st.markdown(f"   *Reason:* {rec_item['reason']}")
                                
                                if rec_item['suggested_courses']:
                                    st.markdown(f"   📖 *Suggested Courses:*")
                                    for course in rec_item['suggested_courses']:
                                        st.markdown(f"      - {course}")
                                st.markdown("")
                            
                            st.info(f"⏱️ **Estimated time to close all gaps:** {gap_analysis['estimated_weeks']} weeks ({gap_analysis['estimated_weeks']/4:.1f} months)")
                        else:
                            st.success("🎉 You already have all required skills! You're ready to apply.")
            
            # Comparison chart
            st.markdown("---")
            st.subheader("📊 Job Match Comparison")
            
            # Create dataframe for plotting
            plot_df = pd.DataFrame({
                'Job': [f"{rec['title']}\n({rec['company']})" for rec in recommendations[:10]],
                'Match Score': [rec['match_score'] for rec in recommendations[:10]],
                'Coverage %': [rec['match_percentage'] for rec in recommendations[:10]]
            })
            
            fig = px.bar(
                plot_df,
                x='Job',
                y='Match Score',
                color='Match Score',
                color_continuous_scale='RdYlGn',
                range_color=[0, 100],
                labels={'Match Score': 'Match Score (0-100)'},
                title="Top 10 Job Matches by Score",
                text='Match Score'
            )
            fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')
            fig.update_layout(xaxis_tickangle=-45, height=450)
            st.plotly_chart(fig, use_container_width=True, key="job_comparison_chart")
            st.markdown("---")
            st.markdown("### 📧 Email Your Results")
        
            col1, col2 = st.columns([2, 1])
        
            with col1:
                st.info("""
                **Get these results in your inbox!**
            
                We'll send you:
                - ✅ Top 5 job recommendations
                - 📊 Your skill profile summary  
                - 🎯 Career readiness analysis
                - 💡 Next steps and tips
                """)
        
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("📧 Email Me These Results", type="primary", use_container_width=True):
                    with st.spinner("Sending email..."):
                        email_service = EmailService()
                        success, message = email_service.send_recommendations_email(
                            user_email=st.session_state['user']['email'],
                            user_name=st.session_state['user']['full_name'] or st.session_state['user']['username'],
                            recommendations=st.session_state['recommendations'],
                            profile=st.session_state['profile'],
                            insights=st.session_state['insights']
                        )
                
                    if success:
                        st.success(f"✅ {message}")
                        st.balloons()
                        st.info(f"📬 Email sent to: {st.session_state['user']['email']}")
                    else:
                        st.error(f"❌ {message}")
                        st.warning("💡 Check your SendGrid API key in email_service.py")

    # ============================================================================
    # TAB 3: ANALYSIS
    # ============================================================================
    with tab3:
        if st.session_state['profile'] is None:
            st.info("👈 Please enter your course information in the 'Input & Predict' tab first!")
        else:
            profile = st.session_state['profile']
            courses_data = st.session_state['courses_data']
            
            st.subheader("📊 Your Detailed Skill Profile")
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Skills", len(profile))
            with col2:
                avg_prof = sum(profile.values()) / len(profile) if profile else 0
                st.metric("Avg Proficiency", f"{avg_prof:.2f}")
            with col3:
                max_prof = max(profile.values()) if profile else 0
                st.metric("Peak Proficiency", f"{max_prof:.2f}")
            with col4:
                expert_skills = sum(1 for p in profile.values() if p >= 0.8)
                st.metric("Expert Level Skills", expert_skills)
            
            st.markdown("---")
            
            # Skill proficiency chart
            st.subheader("🎯 Skill Proficiency Breakdown")
            
            sorted_profile = dict(sorted(profile.items(), key=lambda x: x[1], reverse=True))
            
            # Color code by proficiency level
            colors = []
            for prof in sorted_profile.values():
                if prof >= 0.8:
                    colors.append('#2e7d32')  # Dark green - Expert
                elif prof >= 0.6:
                    colors.append('#558b2f')  # Light green - Advanced
                elif prof >= 0.4:
                    colors.append('#f9a825')  # Yellow - Intermediate
                else:
                    colors.append('#ff6f00')  # Orange - Beginner
            
            fig = go.Figure(go.Bar(
                x=list(sorted_profile.values()),
                y=list(sorted_profile.keys()),
                orientation='h',
                marker=dict(color=colors),
                text=[predictor.get_skill_level(p) for p in sorted_profile.values()],
                textposition='auto',
            ))
            fig.update_layout(
                xaxis_title="Proficiency Score",
                yaxis_title="Skill",
                height=max(400, len(profile) * 35),
                showlegend=False,
                margin=dict(l=150)
            )
            st.plotly_chart(fig, use_container_width=True, key="skill_proficiency_chart")
            
            # Legend
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown("🟢 **Expert** (0.8+)")
            with col2:
                st.markdown("🟢 **Advanced** (0.6-0.8)")
            with col3:
                st.markdown("🟡 **Intermediate** (0.4-0.6)")
            with col4:
                st.markdown("🟠 **Beginner** (<0.4)")
            
            # Course performance
            st.markdown("---")
            st.subheader("📚 Course Performance Analysis")
            
            courses_df = pd.DataFrame(courses_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    courses_df,
                    x='course',
                    y='progress',
                    title="📈 Progress by Course",
                    labels={'progress': 'Progress (%)', 'course': 'Course'},
                    color='progress',
                    color_continuous_scale='Blues',
                    text='progress'
                )
                fig.update_traces(texttemplate='%{text}%', textposition='outside')
                fig.update_layout(xaxis_tickangle=-45, height=400)
                st.plotly_chart(fig, use_container_width=True, key="progress_chart")
            
            with col2:
                fig = px.bar(
                    courses_df,
                    x='course',
                    y='grade',
                    title="🎓 Grades by Course",
                    labels={'grade': 'Grade (%)', 'course': 'Course'},
                    color='grade',
                    color_continuous_scale='Greens',
                    text='grade'
                )
                fig.update_traces(texttemplate='%{text}%', textposition='outside')
                fig.update_layout(xaxis_tickangle=-45, height=400)
                st.plotly_chart(fig, use_container_width=True, key="grade_chart")
            
            # Time investment
            st.markdown("---")
            fig = px.pie(
                courses_df,
                values='hours',
                names='course',
                title="⏱️ Time Investment by Course",
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True, key="time_pie_chart")
            
            # Detailed course table
            st.markdown("---")
            st.subheader("📋 Detailed Course Information")
            
            display_df = courses_df.copy()
            display_df['Progress'] = display_df['progress'].astype(str) + '%'
            display_df['Grade'] = display_df['grade'].astype(str) + '%'
            display_df['Hours'] = display_df['hours'].astype(str) + ' hrs'
            display_df['Course'] = display_df['course']
            
            st.dataframe(
                display_df[['Course', 'Progress', 'Grade', 'Hours']], 
                use_container_width=True, 
                hide_index=True
            )

    # ============================================================================
    # TAB 4: CAREER INSIGHTS
    # ============================================================================
    with tab4:
        if st.session_state['insights'] is None:
            st.info("👈 Please enter your course information in the 'Input & Predict' tab first!")
        else:
            insights = st.session_state['insights']
            profile = st.session_state['profile']
            recommendations = st.session_state['recommendations']
            
            st.subheader("🎯 Career Readiness Analysis")
            
            # Main metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                readiness_emoji = {
                    "Job Ready": "🟢",
                    "Almost Ready": "🟡",
                    "Still Learning": "🟠"
                }
                emoji = readiness_emoji.get(insights['readiness_level'], "⚪")
                st.metric(
                    "Overall Readiness",
                    insights['readiness_level'],
                    f"{emoji}"
                )
            
            with col2:
                st.metric(
                    "Primary Career Path",
                    insights['dominant_category']
                )
            
            with col3:
                st.metric(
                    "Average Skill Level",
                    f"{insights['avg_proficiency']:.0%}"
                )
            
            st.markdown("---")
            
            # Career path breakdown
            st.subheader("🛤️ Career Path Analysis")
            
            categories_df = pd.DataFrame({
                'Category': list(insights['skill_categories'].keys()),
                'Skills': list(insights['skill_categories'].values())
            })
            categories_df = categories_df[categories_df['Skills'] > 0].sort_values('Skills', ascending=False)
            
            if not categories_df.empty:
                fig = px.bar(
                    categories_df,
                    x='Skills',
                    y='Category',
                    orientation='h',
                    title="Skills by Career Category",
                    color='Skills',
                    color_continuous_scale='Viridis',
                    text='Skills'
                )
                fig.update_traces(texttemplate='%{text}', textposition='outside')
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True, key="category_chart")
            
            st.markdown("---")
            
            # Job market fit
            st.subheader("💼 Job Market Fit")
            
            # Calculate average match across all jobs
            avg_match = sum(r['match_score'] for r in recommendations) / len(recommendations)
            good_matches = sum(1 for r in recommendations if r['match_score'] >= 70)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Avg Match Score", f"{avg_match:.1f}/100")
            with col2:
                st.metric("Strong Matches (≥70)", f"{good_matches}/{len(recommendations)}")
            with col3:
                best_match = recommendations[0]['match_score'] if recommendations else 0
                st.metric("Best Match", f"{best_match:.0f}/100")
            
            # Match distribution
            match_dist = {
                'Excellent (80-100)': sum(1 for r in recommendations if r['match_score'] >= 80),
                'Good (60-79)': sum(1 for r in recommendations if 60 <= r['match_score'] < 80),
                'Fair (40-59)': sum(1 for r in recommendations if 40 <= r['match_score'] < 60),
                'Poor (<40)': sum(1 for r in recommendations if r['match_score'] < 40)
            }
            
            fig = go.Figure(data=[
                go.Pie(
                    labels=list(match_dist.keys()),
                    values=list(match_dist.values()),
                    hole=0.4,
                    marker=dict(colors=['#2e7d32', '#558b2f', '#f9a825', '#ff6f00'])
                )
            ])
            fig.update_layout(title="Job Match Score Distribution", height=400)
            st.plotly_chart(fig, use_container_width=True, key="match_dist_pie")
            
            st.markdown("---")
            
            # Recommendations
            st.subheader("💡 Personalized Recommendations")
            
            if insights['readiness_level'] == "Job Ready":
                st.success("""
                🎉 **Congratulations!** You're ready to start applying for jobs!
                
                **Next Steps:**
                1. Update your resume with your skills
                2. Build a portfolio showcasing your projects
                3. Apply to jobs with scores above 70
                4. Prepare for technical interviews
                """)
            elif insights['readiness_level'] == "Almost Ready":
                st.info("""
                📚 **You're on the right track!** A few more skills and you'll be job-ready.
                
                **Recommended Actions:**
                1. Focus on the missing skills for your top job matches
                2. Build 2-3 projects demonstrating your skills
                3. Consider internships or freelance work
                4. Keep learning and practicing
                """)
            else:
                st.warning("""
                🌱 **Keep learning!** You're building a solid foundation.
                
                **Focus Areas:**
                1. Complete your current courses with high grades
                2. Spend more time practicing coding/skills
                3. Take additional courses in your target domain
                4. Build small projects to apply your knowledge
                """)
            
            # Top skills to develop
            st.markdown("---")
            st.subheader("🎯 Skills to Develop Next")
            
            # Find most demanded skills you don't have
            all_job_skills = []
            for rec in recommendations:
                all_job_skills.extend(rec['missing_skills'])
            
            from collections import Counter
            skill_demand = Counter(all_job_skills).most_common(10)
            
            if skill_demand:
                st.markdown("**Most in-demand skills you should learn:**")
                for i, (skill, count) in enumerate(skill_demand, 1):
                    st.markdown(f"{i}. **{skill}** - Required by {count} jobs")
                    # Find courses teaching this skill
                    courses = [c for c, skills in predictor.course_skills.items() if skill in skills]
                    if courses:
                        st.markdown(f"   *Recommended: {courses[0]}*")
            else:
                st.success("🎉 You have all the key skills! Focus on deepening your expertise.")

    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p style='font-size: 18px;'><strong>🎓 SkillBridge</strong> - AI-Powered Career Matching</p>
            <p>Using advanced skill-based algorithms with 100-point scoring system</p>
            <p style='font-size: 12px; margin-top: 10px;'>
                Trained on 10,000+ student profiles | 100+ job postings | 50+ unique skills
            </p>
        </div>
    """, unsafe_allow_html=True)

# ============================================================================
# MAIN APP ROUTING
# ============================================================================
if not st.session_state['logged_in']:
    show_login_page()
else:
    show_main_app()