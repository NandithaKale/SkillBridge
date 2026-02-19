import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

print("="*70)
print("GENERATING 10,000+ TRAINING RECORDS")
print("="*70)

# Course catalog with associated skills
COURSES_CATALOG = {
    'Python for Data Science': ['python', 'data science', 'pandas', 'numpy'],
    'Machine Learning Fundamentals': ['python', 'machine learning', 'scikit-learn', 'statistics'],
    'Deep Learning Neural Networks': ['python', 'deep learning', 'tensorflow', 'neural networks'],
    'Web Development HTML/CSS/JavaScript': ['html', 'css', 'javascript', 'web development'],
    'React Frontend Development': ['react', 'javascript', 'web development', 'frontend'],
    'SQL Database Management': ['sql', 'database', 'mysql', 'data management'],
    'Data Visualization Tableau': ['tableau', 'data visualization', 'analytics'],
    'Cloud Computing AWS': ['aws', 'cloud computing', 'devops', 'linux'],
    'Natural Language Processing': ['python', 'nlp', 'machine learning', 'text analysis'],
    'Advanced Statistics': ['statistics', 'probability', 'data analysis', 'r'],
    'Full Stack Development': ['javascript', 'python', 'sql', 'web development', 'react'],
    'Data Engineering': ['python', 'sql', 'big data', 'apache spark', 'etl'],
    'DevOps Engineering': ['docker', 'kubernetes', 'ci/cd', 'linux', 'aws'],
    'Mobile App Development': ['react native', 'mobile development', 'javascript'],
    'Business Analytics': ['excel', 'tableau', 'sql', 'business intelligence'],
    'Cybersecurity Fundamentals': ['security', 'networking', 'ethical hacking'],
    'Blockchain Development': ['blockchain', 'solidity', 'web3', 'smart contracts'],
    'Game Development Unity': ['unity', 'c#', 'game development', '3d modeling'],
    'UI/UX Design': ['ui design', 'ux design', 'figma', 'user research'],
    'Digital Marketing': ['seo', 'google analytics', 'social media marketing']
}

# Job catalog with required skills
JOBS_CATALOG = {
    'Data Analyst': ['python', 'sql', 'excel', 'data visualization', 'statistics'],
    'Machine Learning Engineer': ['python', 'machine learning', 'tensorflow', 'deep learning', 'statistics'],
    'Data Scientist': ['python', 'machine learning', 'statistics', 'sql', 'data visualization'],
    'Frontend Developer': ['react', 'javascript', 'html', 'css', 'web development'],
    'Backend Developer': ['python', 'sql', 'api', 'web development', 'database'],
    'Full Stack Developer': ['javascript', 'react', 'python', 'sql', 'web development'],
    'Cloud Engineer': ['aws', 'cloud computing', 'linux', 'devops', 'docker'],
    'DevOps Engineer': ['docker', 'kubernetes', 'ci/cd', 'linux', 'aws'],
    'Data Engineer': ['python', 'sql', 'big data', 'apache spark', 'etl'],
    'NLP Engineer': ['python', 'nlp', 'machine learning', 'deep learning', 'tensorflow'],
    'Business Analyst': ['excel', 'sql', 'tableau', 'business intelligence', 'data analysis'],
    'Mobile Developer': ['react native', 'mobile development', 'javascript', 'api'],
    'Security Analyst': ['security', 'networking', 'ethical hacking', 'linux'],
    'Blockchain Developer': ['blockchain', 'solidity', 'web3', 'smart contracts'],
    'Game Developer': ['unity', 'c#', 'game development', '3d modeling'],
    'UI/UX Designer': ['ui design', 'ux design', 'figma', 'user research'],
    'Digital Marketing Specialist': ['seo', 'google analytics', 'social media marketing']
}

COMPANIES = [
    'TechCorp', 'DataSolutions', 'AI Innovations', 'WebWorks', 'CloudFirst',
    'Analytics Pro', 'DevHub', 'CodeMasters', 'Digital Dynamics', 'FutureTech',
    'SmartData', 'InnovateLabs', 'TechVision', 'DataDrive', 'CloudNine'
]

def generate_students(n=10000):
    """Generate n student records"""
    print(f"\n📊 Generating {n} student records...")
    
    students = []
    for i in range(1, n + 1):
        students.append({
            'student_id': i,
            'name': f'Student_{i}',
            'email': f'student{i}@university.edu',
            'enrollment_date': datetime.now() - timedelta(days=random.randint(0, 1095))
        })
    
    print(f"✓ Generated {len(students)} students")
    return pd.DataFrame(students)

def generate_courses(students_df):
    """Generate course enrollments for all students"""
    print(f"\n📚 Generating course enrollments...")
    
    courses = []
    course_names = list(COURSES_CATALOG.keys())
    
    for student_id in students_df['student_id']:
        # Each student takes 3-8 courses
        num_courses = random.randint(3, 8)
        selected_courses = random.sample(course_names, num_courses)
        
        for course_name in selected_courses:
            # Generate realistic metrics
            progress = random.choices(
                [random.uniform(0.4, 0.7), random.uniform(0.7, 0.9), random.uniform(0.9, 1.0)],
                weights=[0.2, 0.3, 0.5]  # Most students have high progress
            )[0]
            
            grade = random.choices(
                [random.uniform(60, 75), random.uniform(75, 90), random.uniform(90, 100)],
                weights=[0.2, 0.5, 0.3]
            )[0]
            
            time_spent = random.uniform(10, 100)
            
            courses.append({
                'student_id': student_id,
                'course_name': course_name,
                'progress': round(progress * 100, 1),
                'grade': round(grade, 1),
                'time_spent_hours': round(time_spent, 1),
                'completion_date': datetime.now() - timedelta(days=random.randint(0, 365))
            })
    
    print(f"✓ Generated {len(courses)} course enrollments")
    return pd.DataFrame(courses)

def generate_jobs(n=100):
    """Generate n job postings"""
    print(f"\n💼 Generating {n} job postings...")
    
    jobs = []
    job_titles = list(JOBS_CATALOG.keys())
    
    for i in range(1, n + 1):
        job_title = random.choice(job_titles)
        required_skills = JOBS_CATALOG[job_title]
        
        jobs.append({
            'job_id': i,
            'title': job_title,
            'company': random.choice(COMPANIES),
            'required_skills': ', '.join(required_skills),
            'posted_date': datetime.now() - timedelta(days=random.randint(0, 90))
        })
    
    print(f"✓ Generated {len(jobs)} job postings")
    return pd.DataFrame(jobs)

def extract_skills_from_courses(courses_df):
    """Extract skills from course enrollments"""
    print(f"\n🎯 Extracting skills from courses...")
    
    courses_df['extracted_skills'] = courses_df['course_name'].apply(
        lambda course: COURSES_CATALOG.get(course, [])
    )
    
    print(f"✓ Skills extracted")
    return courses_df

def build_training_profiles(courses_df):
    """Build skill profiles for all students"""
    print(f"\n👤 Building student skill profiles...")
    
    profiles = []
    
    for student_id in courses_df['student_id'].unique():
        student_courses = courses_df[courses_df['student_id'] == student_id]
        
        skill_scores = {}
        
        for _, course in student_courses.iterrows():
            # Calculate proficiency weight
            progress_weight = course['progress'] / 100
            grade_weight = course['grade'] / 100
            time_weight = min(course['time_spent_hours'] / 50, 1)
            
            combined_weight = (0.5 * progress_weight + 
                             0.3 * grade_weight + 
                             0.2 * time_weight)
            
            # Add skills
            for skill in course['extracted_skills']:
                if skill in skill_scores:
                    skill_scores[skill].append(combined_weight)
                else:
                    skill_scores[skill] = [combined_weight]
        
        # Average proficiency per skill
        for skill, weights in skill_scores.items():
            profiles.append({
                'student_id': student_id,
                'skill': skill,
                'proficiency': round(np.mean(weights), 3)
            })
    
    print(f"✓ Built {len(profiles)} skill proficiency records")
    return pd.DataFrame(profiles)

def calculate_job_matches(profiles_df, jobs_df):
    """Calculate match scores for training"""
    print(f"\n🤝 Calculating job match scores...")
    
    matches = []
    
    for student_id in profiles_df['student_id'].unique():
        student_skills = profiles_df[profiles_df['student_id'] == student_id]
        student_skill_dict = dict(zip(student_skills['skill'], student_skills['proficiency']))
        
        for _, job in jobs_df.iterrows():
            job_skills = job['required_skills'].split(', ')
            
            # Calculate match
            matched_skills = set(student_skill_dict.keys()).intersection(set(job_skills))
            
            if matched_skills:
                total_weight = sum(student_skill_dict[skill] for skill in matched_skills)
                match_score = total_weight / len(job_skills)
            else:
                match_score = 0.0
            
            matches.append({
                'student_id': student_id,
                'job_id': job['job_id'],
                'job_title': job['title'],
                'match_score': round(match_score, 3)
            })
    
    print(f"✓ Calculated {len(matches)} job matches")
    return pd.DataFrame(matches)

def main():
    # Create directories
    os.makedirs('data/training_data', exist_ok=True)
    
    # Generate data
    students_df = generate_students(10000)
    courses_df = generate_courses(students_df)
    jobs_df = generate_jobs(100)
    
    # Process data
    courses_df = extract_skills_from_courses(courses_df)
    profiles_df = build_training_profiles(courses_df)
    matches_df = calculate_job_matches(profiles_df, jobs_df)
    
    # Save to Excel
    print(f"\n💾 Saving training data...")
    
    students_df.to_excel('data/training_data/students.xlsx', index=False)
    courses_df.to_excel('data/training_data/courses.xlsx', index=False)
    jobs_df.to_excel('data/training_data/jobs.xlsx', index=False)
    profiles_df.to_excel('data/training_data/profiles.xlsx', index=False)
    matches_df.to_excel('data/training_data/matches.xlsx', index=False)
    
    print(f"✓ Saved all training data to data/training_data/")
    
    # Statistics
    print(f"\n📈 Training Data Statistics:")
    print(f"  • Students: {len(students_df)}")
    print(f"  • Course Enrollments: {len(courses_df)}")
    print(f"  • Job Postings: {len(jobs_df)}")
    print(f"  • Skill Profiles: {len(profiles_df)}")
    print(f"  • Job Matches: {len(matches_df)}")
    
    print("\n" + "="*70)
    print("✓ TRAINING DATA GENERATION COMPLETE!")
    print("="*70)

if __name__ == "__main__":
    main()