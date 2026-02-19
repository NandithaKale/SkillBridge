import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

class DataGenerator:
    def __init__(self, num_students=10000, num_jobs=100):
        self.num_students = num_students
        self.num_jobs = num_jobs
        
        # Expanded and diversified job roles with varied skill requirements
        self.job_templates = [
            # Data Science Jobs (5-7 skills, Python heavy)
            {
                'title': 'Data Scientist',
                'company': ['TechCorp', 'DataHub', 'AI Innovations', 'CloudNine', 'DevHub'],
                'skills': ['python', 'machine learning', 'statistics', 'pandas', 'sql', 'data visualization', 'scikit-learn'],
                'num_skills': (5, 7)
            },
            {
                'title': 'Senior Data Scientist',
                'company': ['Google', 'Meta', 'Amazon', 'Microsoft', 'Apple'],
                'skills': ['python', 'machine learning', 'deep learning', 'tensorflow', 'statistics', 'big data', 'nlp', 'sql'],
                'num_skills': (6, 8)
            },
            {
                'title': 'Junior Data Analyst',
                'company': ['StartupX', 'DataCo', 'Analytics Inc', 'Insight Labs'],
                'skills': ['python', 'sql', 'excel', 'data visualization', 'statistics'],
                'num_skills': (3, 5)
            },
            
            # Machine Learning Jobs (6-8 skills, ML heavy)
            {
                'title': 'Machine Learning Engineer',
                'company': ['OpenAI', 'DeepMind', 'NVIDIA', 'Tesla', 'Uber'],
                'skills': ['python', 'machine learning', 'deep learning', 'tensorflow', 'keras', 'pytorch', 'mlops', 'docker'],
                'num_skills': (6, 8)
            },
            {
                'title': 'AI Research Scientist',
                'company': ['MIT Lab', 'Stanford AI', 'IBM Research', 'Samsung AI'],
                'skills': ['python', 'deep learning', 'machine learning', 'tensorflow', 'pytorch', 'research', 'mathematics', 'nlp'],
                'num_skills': (6, 8)
            },
            {
                'title': 'Computer Vision Engineer',
                'company': ['Tesla', 'Waymo', 'Apple', 'Snapchat'],
                'skills': ['python', 'deep learning', 'tensorflow', 'opencv', 'computer vision', 'pytorch', 'image processing'],
                'num_skills': (5, 7)
            },
            
            # Web Development Jobs (4-6 skills, JavaScript heavy)
            {
                'title': 'Frontend Developer',
                'company': ['WebWorks', 'DigitalCraft', 'UIExperts', 'DesignCo'],
                'skills': ['javascript', 'react', 'html', 'css', 'web development', 'ui'],
                'num_skills': (4, 6)
            },
            {
                'title': 'Full Stack Developer',
                'company': ['TechStack', 'DevShop', 'CodeCraft', 'BuildIt'],
                'skills': ['javascript', 'react', 'node.js', 'sql', 'python', 'web development', 'api', 'docker'],
                'num_skills': (5, 8)
            },
            {
                'title': 'Backend Developer',
                'company': ['ServerPro', 'BackendHub', 'APIWorks'],
                'skills': ['python', 'sql', 'api', 'docker', 'linux', 'database'],
                'num_skills': (4, 6)
            },
            {
                'title': 'React Developer',
                'company': ['Facebook', 'Airbnb', 'Netflix', 'Spotify'],
                'skills': ['javascript', 'react', 'redux', 'web development', 'css', 'typescript'],
                'num_skills': (4, 6)
            },
            
            # Cloud/DevOps Jobs (5-7 skills, cloud heavy)
            {
                'title': 'DevOps Engineer',
                'company': ['CloudOps', 'InfraCo', 'AutomateIT', 'ScaleSystems'],
                'skills': ['docker', 'kubernetes', 'aws', 'ci/cd', 'linux', 'terraform', 'jenkins'],
                'num_skills': (5, 7)
            },
            {
                'title': 'Cloud Architect',
                'company': ['AWS', 'Azure', 'Google Cloud', 'IBM Cloud'],
                'skills': ['aws', 'cloud computing', 'kubernetes', 'terraform', 'architecture', 'networking', 'security'],
                'num_skills': (5, 7)
            },
            {
                'title': 'Site Reliability Engineer',
                'company': ['Google', 'Netflix', 'Uber', 'Spotify'],
                'skills': ['linux', 'kubernetes', 'docker', 'monitoring', 'python', 'automation', 'aws'],
                'num_skills': (5, 7)
            },
            
            # Data Engineering Jobs (5-7 skills, data pipeline heavy)
            {
                'title': 'Data Engineer',
                'company': ['DataPipe', 'ETL Solutions', 'BigData Inc', 'StreamCo'],
                'skills': ['python', 'sql', 'apache spark', 'big data', 'etl', 'kafka', 'airflow'],
                'num_skills': (5, 7)
            },
            {
                'title': 'Big Data Engineer',
                'company': ['Hadoop Corp', 'Databricks', 'Snowflake', 'Cloudera'],
                'skills': ['apache spark', 'hadoop', 'python', 'sql', 'big data', 'scala', 'kafka'],
                'num_skills': (5, 7)
            },
            
            # Business/Analytics Jobs (3-5 skills, business tools heavy)
            {
                'title': 'Business Analyst',
                'company': ['ConsultCo', 'StrategyHub', 'BizInsights', 'Analytics Pro'],
                'skills': ['excel', 'sql', 'tableau', 'business intelligence', 'data analysis'],
                'num_skills': (3, 5)
            },
            {
                'title': 'Data Analyst',
                'company': ['Marketing Inc', 'Sales Corp', 'Finance Plus'],
                'skills': ['sql', 'excel', 'tableau', 'python', 'data visualization'],
                'num_skills': (3, 5)
            },
            {
                'title': 'BI Developer',
                'company': ['PowerBI Co', 'Tableau Inc', 'Looker Labs'],
                'skills': ['sql', 'tableau', 'power bi', 'data visualization', 'business intelligence', 'excel'],
                'num_skills': (4, 6)
            },
            
            # Specialized Jobs (varied requirements)
            {
                'title': 'NLP Engineer',
                'company': ['LangTech', 'ChatBotCo', 'Voice AI', 'TextAnalytics'],
                'skills': ['python', 'nlp', 'machine learning', 'tensorflow', 'transformers', 'spacy', 'text analysis'],
                'num_skills': (5, 7)
            },
            {
                'title': 'Mobile Developer',
                'company': ['AppWorks', 'MobileCraft', 'AppFactory'],
                'skills': ['react native', 'javascript', 'mobile development', 'ios', 'android', 'firebase'],
                'num_skills': (4, 6)
            },
            {
                'title': 'Security Engineer',
                'company': ['SecureTech', 'CyberGuard', 'SafeNet'],
                'skills': ['security', 'networking', 'linux', 'python', 'cryptography', 'penetration testing'],
                'num_skills': (4, 6)
            },
            {
                'title': 'Blockchain Developer',
                'company': ['CryptoTech', 'Web3 Labs', 'DeFi Inc'],
                'skills': ['blockchain', 'solidity', 'web3', 'smart contracts', 'ethereum', 'javascript'],
                'num_skills': (4, 6)
            },
            {
                'title': 'Game Developer',
                'company': ['GameStudio', 'PixelWorks', 'IndieGames'],
                'skills': ['unity', 'c#', 'game development', '3d modeling', 'unreal engine'],
                'num_skills': (4, 5)
            },
            {
                'title': 'UI/UX Designer',
                'company': ['DesignHub', 'CreativeStudio', 'UserFirst'],
                'skills': ['ui design', 'ux design', 'figma', 'adobe xd', 'prototyping', 'user research'],
                'num_skills': (4, 6)
            },
            {
                'title': 'QA Engineer',
                'company': ['TestLab', 'QualityFirst', 'BugHunters'],
                'skills': ['testing', 'selenium', 'python', 'automation', 'jenkins', 'quality assurance'],
                'num_skills': (4, 6)
            },
            {
                'title': 'Database Administrator',
                'company': ['DataSafe', 'DB Solutions', 'StorageCo'],
                'skills': ['sql', 'mysql', 'postgresql', 'database', 'backup', 'optimization'],
                'num_skills': (4, 6)
            },
            {
                'title': 'Systems Administrator',
                'company': ['SysOps', 'ServerMaint', 'ITSupport'],
                'skills': ['linux', 'windows server', 'networking', 'bash', 'powershell', 'monitoring'],
                'num_skills': (4, 6)
            },
            {
                'title': 'Python Developer',
                'company': ['PythonPro', 'ScriptWorks', 'CodeBase'],
                'skills': ['python', 'django', 'flask', 'sql', 'api', 'web development'],
                'num_skills': (4, 6)
            },
            {
                'title': 'Java Developer',
                'company': ['Enterprise Inc', 'JavaCorp', 'Spring Solutions'],
                'skills': ['java', 'spring', 'sql', 'maven', 'microservices', 'rest api'],
                'num_skills': (4, 6)
            },
            {
                'title': 'Data Visualization Specialist',
                'company': ['VizWorks', 'ChartMasters', 'InsightViz'],
                'skills': ['tableau', 'd3.js', 'python', 'data visualization', 'javascript', 'power bi'],
                'num_skills': (4, 6)
            }
        ]
        
        # Available courses
        self.courses = [
            'Python for Data Science',
            'Machine Learning Fundamentals',
            'Deep Learning Neural Networks',
            'Web Development HTML/CSS/JavaScript',
            'React Frontend Development',
            'SQL Database Management',
            'Data Visualization Tableau',
            'Cloud Computing AWS',
            'Natural Language Processing',
            'Advanced Statistics',
            'Full Stack Development',
            'Data Engineering',
            'DevOps Engineering',
            'Mobile App Development',
            'Business Analytics',
            'Cybersecurity Fundamentals',
            'Blockchain Development',
            'Game Development Unity',
            'UI/UX Design',
            'Digital Marketing'
        ]
        
        # Course to skills mapping
        self.course_skills = {
            'Python for Data Science': ['python', 'data science', 'pandas', 'numpy', 'data analysis'],
            'Machine Learning Fundamentals': ['python', 'machine learning', 'scikit-learn', 'statistics', 'data analysis'],
            'Deep Learning Neural Networks': ['python', 'deep learning', 'tensorflow', 'neural networks', 'keras'],
            'Web Development HTML/CSS/JavaScript': ['html', 'css', 'javascript', 'web development', 'frontend'],
            'React Frontend Development': ['react', 'javascript', 'web development', 'frontend', 'ui'],
            'SQL Database Management': ['sql', 'database', 'mysql', 'data management', 'queries'],
            'Data Visualization Tableau': ['tableau', 'data visualization', 'analytics', 'dashboards'],
            'Cloud Computing AWS': ['aws', 'cloud computing', 'devops', 'linux', 'infrastructure'],
            'Natural Language Processing': ['python', 'nlp', 'machine learning', 'text analysis', 'nlp libraries'],
            'Advanced Statistics': ['statistics', 'probability', 'data analysis', 'r', 'statistical modeling'],
            'Full Stack Development': ['javascript', 'python', 'sql', 'web development', 'react', 'api'],
            'Data Engineering': ['python', 'sql', 'big data', 'apache spark', 'etl', 'data pipelines'],
            'DevOps Engineering': ['docker', 'kubernetes', 'ci/cd', 'linux', 'aws', 'automation'],
            'Mobile App Development': ['react native', 'mobile development', 'javascript', 'ios', 'android'],
            'Business Analytics': ['excel', 'tableau', 'sql', 'business intelligence', 'analytics'],
            'Cybersecurity Fundamentals': ['security', 'networking', 'ethical hacking', 'cryptography'],
            'Blockchain Development': ['blockchain', 'solidity', 'web3', 'smart contracts', 'ethereum'],
            'Game Development Unity': ['unity', 'c#', 'game development', '3d modeling', 'game engines'],
            'UI/UX Design': ['ui design', 'ux design', 'figma', 'user research', 'prototyping'],
            'Digital Marketing': ['seo', 'google analytics', 'social media marketing', 'content marketing']
        }
    
    def generate_jobs(self):
        """Generate diverse job postings with varied skill requirements"""
        jobs = []
        
        for i in range(self.num_jobs):
            # Select a random job template
            template = np.random.choice(self.job_templates)
            
            # Select number of skills for this job
            num_skills = np.random.randint(template['num_skills'][0], template['num_skills'][1] + 1)
            
            # Randomly select skills from template
            selected_skills = np.random.choice(template['skills'], size=min(num_skills, len(template['skills'])), replace=False)
            
            # Select company
            company = np.random.choice(template['company'])
            
            jobs.append({
                'job_id': i + 1,
                'title': template['title'],
                'company': company,
                'required_skills': ', '.join(selected_skills)
            })
        
        return pd.DataFrame(jobs)
    
    def generate_courses(self):
        """Generate student course enrollment data"""
        courses_data = []
        
        for student_id in range(1, self.num_students + 1):
            # Each student takes 2-8 courses
            num_courses = np.random.randint(2, 9)
            student_courses = np.random.choice(self.courses, size=num_courses, replace=False)
            
            for course in student_courses:
                # Generate realistic course metrics
                progress = np.random.randint(40, 101)
                grade = np.random.randint(50, 100)
                time_spent = np.random.randint(10, 150)
                
                # Add some correlation: higher progress tends to mean higher grades
                if progress > 80:
                    grade = np.random.randint(70, 100)
                
                courses_data.append({
                    'student_id': student_id,
                    'course_name': course,
                    'progress_percentage': progress,
                    'grade_percentage': grade,
                    'time_spent_hours': time_spent
                })
        
        return pd.DataFrame(courses_data)
    
    def generate_skill_profiles(self, courses_df):
        """Generate skill profiles based on courses taken"""
        profiles = []
        
        for student_id in range(1, self.num_students + 1):
            # Get student's courses
            student_courses = courses_df[courses_df['student_id'] == student_id]
            
            # Build skill profile
            skill_scores = {}
            
            for _, course in student_courses.iterrows():
                course_name = course['course_name']
                progress = course['progress_percentage'] / 100
                grade = course['grade_percentage'] / 100
                time = min(course['time_spent_hours'] / 50, 1)
                
                # Calculate proficiency
                base_score = 0.5 * progress + 0.3 * grade + 0.2 * time
                
                # Get skills for this course
                skills = self.course_skills.get(course_name, [])
                
                for skill in skills:
                    if skill not in skill_scores:
                        skill_scores[skill] = base_score
                    else:
                        # Take maximum if skill appears in multiple courses
                        skill_scores[skill] = max(skill_scores[skill], base_score)
            
            # Normalize scores
            if skill_scores:
                max_score = max(skill_scores.values())
                if max_score > 1:
                    skill_scores = {k: min(v / max_score, 1.0) for k, v in skill_scores.items()}
            
            # Add to profiles
            for skill, proficiency in skill_scores.items():
                profiles.append({
                    'student_id': student_id,
                    'skill': skill,
                    'proficiency': round(proficiency, 3)
                })
        
        return pd.DataFrame(profiles)
    
    def generate_matches(self, profiles_df, jobs_df):
        """Generate job matches based on skill profiles"""
        matches = []
        
        for student_id in range(1, self.num_students + 1):
            # Get student's skills
            student_skills = profiles_df[profiles_df['student_id'] == student_id]
            student_skill_dict = dict(zip(student_skills['skill'], student_skills['proficiency']))
            
            # Calculate match for each job
            for _, job in jobs_df.iterrows():
                job_skills = [s.strip() for s in job['required_skills'].split(',')]
                
                # Calculate match score
                matched_skills = set(student_skill_dict.keys()).intersection(set(job_skills))
                
                if not matched_skills:
                    continue
                
                # Coverage score (40 points)
                coverage_score = (len(matched_skills) / len(job_skills)) * 40
                
                # Proficiency score (50 points)
                avg_proficiency = sum(student_skill_dict[s] for s in matched_skills) / len(matched_skills)
                proficiency_score = avg_proficiency * 50
                
                # Bonus (10 points)
                bonus = 10 if len(matched_skills) == len(job_skills) else 5
                
                match_score = coverage_score + proficiency_score + bonus
                
                # Only save matches above 30
                if match_score >= 30:
                    matches.append({
                        'student_id': student_id,
                        'job_id': job['job_id'],
                        'match_score': round(match_score, 2)
                    })
        
        return pd.DataFrame(matches)
    
    def generate_all_data(self):
        """Generate all data files"""
        print("🚀 Starting data generation...")
        
        # Create directories
        os.makedirs('data/training_data', exist_ok=True)
        
        # Generate jobs with diverse requirements
        print("📊 Generating diverse job postings...")
        jobs_df = self.generate_jobs()
        jobs_df.to_excel('data/training_data/jobs.xlsx', index=False)
        print(f"✅ Generated {len(jobs_df)} jobs with varied skill requirements")
        
        # Generate courses
        print("📚 Generating course enrollment data...")
        courses_df = self.generate_courses()
        courses_df.to_excel('data/training_data/courses.xlsx', index=False)
        print(f"✅ Generated {len(courses_df)} course enrollments")
        
        # Generate skill profiles
        print("🎯 Generating skill profiles...")
        profiles_df = self.generate_skill_profiles(courses_df)
        profiles_df.to_excel('data/training_data/profiles.xlsx', index=False)
        print(f"✅ Generated {len(profiles_df)} skill proficiencies")
        
        # Generate matches
        print("🔗 Generating job matches...")
        matches_df = self.generate_matches(profiles_df, jobs_df)
        matches_df.to_excel('data/training_data/matches.xlsx', index=False)
        print(f"✅ Generated {len(matches_df)} job matches")
        
        # Print summary statistics
        print("\n📈 Data Generation Summary:")
        print(f"   Students: {self.num_students:,}")
        print(f"   Jobs: {len(jobs_df)}")
        print(f"   Course Enrollments: {len(courses_df):,}")
        print(f"   Total Skills: {profiles_df['skill'].nunique()}")
        print(f"   Job Matches: {len(matches_df):,}")
        
        # Show skill distribution across jobs
        print("\n🎯 Job Skill Requirements Distribution:")
        skill_counts = jobs_df['required_skills'].apply(lambda x: len(x.split(', ')))
        print(f"   Min skills required: {skill_counts.min()}")
        print(f"   Max skills required: {skill_counts.max()}")
        print(f"   Average skills required: {skill_counts.mean():.1f}")
        
        # Show sample jobs
        print("\n📋 Sample Job Postings:")
        for _, job in jobs_df.head(5).iterrows():
            skills = job['required_skills'].split(', ')
            print(f"   {job['title']} at {job['company']}")
            print(f"      Skills ({len(skills)}): {', '.join(skills)}")
        
        print("\n✅ All data generated successfully!")
        
        return {
            'jobs': jobs_df,
            'courses': courses_df,
            'profiles': profiles_df,
            'matches': matches_df
        }

if __name__ == "__main__":
    generator = DataGenerator(num_students=10000, num_jobs=100)
    generator.generate_all_data()