import pandas as pd
import numpy as np
import os
from src.nlp_matcher import NLPSkillMatcher

class CareerPredictor:
    def __init__(self):
        """Initialize the predictor with job data and NLP matcher"""
        # Load jobs data
        self.jobs_df = pd.read_excel('data/training_data/jobs.xlsx')
        
        # Initialize NLP matcher
        print("🧠 Initializing NLP-based skill matcher...")
        self.nlp_matcher = NLPSkillMatcher(similarity_threshold=0.65)
        
        # Course to skills mapping (expanded)
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
        
        # Skill importance weights (some skills are more valuable)
        self.skill_weights = {
            'python': 1.3,
            'machine learning': 1.4,
            'deep learning': 1.4,
            'sql': 1.2,
            'react': 1.2,
            'aws': 1.3,
            'docker': 1.2,
            'kubernetes': 1.3,
            'data science': 1.3,
            'tensorflow': 1.3
        }
        
        # Calculate statistics from training data
        self.calculate_statistics()
    
    def calculate_statistics(self):
        """Calculate statistics for the system info"""
        try:
            courses_df = pd.read_excel('data/training_data/courses.xlsx')
            profiles_df = pd.read_excel('data/training_data/profiles.xlsx')
            
            self.stats = {
                'total_students': courses_df['student_id'].nunique(),
                'total_jobs': len(self.jobs_df),
                'total_skills': profiles_df['skill'].nunique(),
                'avg_skills_per_student': profiles_df.groupby('student_id').size().mean()
            }
        except:
            self.stats = {
                'total_students': 10000,
                'total_jobs': len(self.jobs_df),
                'total_skills': 50,
                'avg_skills_per_student': 8.5
            }
    
    def build_profile(self, courses_taken):
        """
        Build skill profile from courses
        courses_taken: list of dicts [{'course': 'Python...', 'progress': 90, 'grade': 85, 'hours': 40}]
        """
        skill_scores = {}
        
        for course_data in courses_taken:
            course_name = course_data['course']
            progress = course_data['progress'] / 100
            grade = course_data['grade'] / 100
            time = min(course_data['hours'] / 50, 1)
            
            # Weighted proficiency calculation
            base_weight = 0.5 * progress + 0.3 * grade + 0.2 * time
            
            # Get skills for this course
            skills = self.course_skills.get(course_name, [])
            
            for skill in skills:
                # Apply skill importance multiplier
                skill_multiplier = self.skill_weights.get(skill, 1.0)
                weighted_score = base_weight * skill_multiplier
                
                if skill in skill_scores:
                    skill_scores[skill] = max(skill_scores[skill], weighted_score)
                else:
                    skill_scores[skill] = weighted_score
        
        # Normalize to 0-1 range
        if skill_scores:
            max_score = max(skill_scores.values())
            if max_score > 1:
                skill_scores = {k: min(v / max_score, 1.0) for k, v in skill_scores.items()}
        
        return {k: round(v, 3) for k, v in skill_scores.items()}
    
    def calculate_match_score(self, student_profile, job_skills):
        """Calculate comprehensive match score using NLP-based matching (0-100)"""
        if not student_profile or not job_skills:
            return 0.0, [], []
        
        student_skills = list(student_profile.keys())
        
        # Use NLP matcher to find semantic matches
        match_results = self.nlp_matcher.find_matches(student_skills, job_skills)
        
        matched_pairs = match_results['matched']
        unmatched_job_skills = match_results['unmatched_job_skills']
        
        if not matched_pairs:
            return 0.0, [], job_skills
        
        # 1. Coverage score (0-40 points): How many skills matched
        coverage_score = (len(matched_pairs) / len(job_skills)) * 40
        
        # 2. Proficiency score (0-50 points): How good you are at matched skills
        # Weight by semantic similarity
        weighted_proficiency = 0
        for student_skill, job_skill, similarity in matched_pairs:
            proficiency = student_profile[student_skill]
            # Apply similarity weight (perfect match = 1.0, fair match = 0.65)
            weighted_proficiency += proficiency * similarity
        
        avg_proficiency = weighted_proficiency / len(matched_pairs)
        proficiency_score = avg_proficiency * 50
        
        # 3. Importance bonus (0-10 points): Having high-value skills
        important_matched = sum(
            1 for student_skill, _, _ in matched_pairs 
            if student_skill.lower() in self.skill_weights
        )
        importance_score = min((important_matched / len(matched_pairs)) * 10, 10) if matched_pairs else 0
        
        # Total score (0-100)
        total_score = coverage_score + proficiency_score + importance_score
        
        # Return matched skills (from student's perspective)
        matched_student_skills = [student_skill for student_skill, _, _ in matched_pairs]
        
        return round(total_score, 1), matched_student_skills, unmatched_job_skills
    
    def recommend_jobs(self, profile, top_n=10):
        """Recommend jobs based on skill profile using NLP matching"""
        recommendations = []
        
        for _, job in self.jobs_df.iterrows():
            job_skills = [s.strip() for s in job['required_skills'].split(',')]
            
            match_score, matched_skills, missing_skills = self.calculate_match_score(profile, job_skills)
            
            # Calculate match percentage
            if job_skills:
                match_percentage = round(len(matched_skills) / len(job_skills) * 100, 1)
            else:
                match_percentage = 0
            
            recommendations.append({
                'title': job['title'],
                'company': job['company'],
                'match_score': match_score,
                'match_percentage': match_percentage,
                'matched_skills': sorted(matched_skills),
                'missing_skills': sorted(missing_skills),
                'required_skills': job_skills,
                'num_matched': len(matched_skills),
                'num_required': len(job_skills)
            })
        
        recommendations.sort(key=lambda x: (x['match_score'], x['match_percentage']), reverse=True)
        
        return recommendations[:top_n]
    
    def get_skill_level(self, proficiency):
        """Convert proficiency to skill level"""
        if proficiency >= 0.8:
            return "Expert"
        elif proficiency >= 0.6:
            return "Advanced"
        elif proficiency >= 0.4:
            return "Intermediate"
        else:
            return "Beginner"
    
    def analyze_skill_gaps(self, profile, target_job):
        """Analyze skill gaps for a specific job using NLP matching"""
        job_skills = target_job['required_skills']
        student_skills = list(profile.keys())
        
        # Use NLP to find matches
        match_results = self.nlp_matcher.find_matches(student_skills, job_skills)
        
        matched_pairs = match_results['matched']
        missing_skills = match_results['unmatched_job_skills']
        
        weak_skills = []
        strong_skills = []
        
        # Categorize matched skills by proficiency
        for student_skill, job_skill, similarity in matched_pairs:
            proficiency = profile[student_skill]
            if proficiency < 0.5:
                weak_skills.append((student_skill, proficiency, job_skill, similarity))
            else:
                strong_skills.append((student_skill, proficiency, job_skill, similarity))
        
        recommendations = []
        
        # High priority: Missing skills
        for skill in sorted(missing_skills):
            suggested_courses = [course for course, skills in self.course_skills.items() 
                               if any(self.nlp_matcher.calculate_similarity(skill, s) >= 0.7 for s in skills)]
            recommendations.append({
                'skill': skill,
                'priority': 'HIGH',
                'current_level': 'None',
                'reason': 'Required skill - not yet acquired',
                'suggested_courses': suggested_courses[:2] if suggested_courses else [f"Find courses for {skill}"]
            })
        
        # Medium priority: Weak skills
        for student_skill, proficiency, job_skill, similarity in sorted(weak_skills, key=lambda x: x[1]):
            match_note = f" (matches '{job_skill}')" if similarity < 0.95 else ""
            suggested_courses = [course for course, skills in self.course_skills.items() 
                               if student_skill in skills]
            recommendations.append({
                'skill': student_skill + match_note,
                'priority': 'MEDIUM',
                'current_level': self.get_skill_level(proficiency),
                'reason': f'Low proficiency ({proficiency:.2f}) - needs improvement',
                'suggested_courses': suggested_courses[:2] if suggested_courses else [f"Advanced {student_skill} courses"]
            })
        
        # Estimate learning time
        estimated_weeks = (len(missing_skills) * 4) + (len(weak_skills) * 2)
        
        return {
            'missing_skills': sorted(missing_skills),
            'weak_skills': [s[0] for s in weak_skills],
            'strong_skills': [s[0] for s in strong_skills],
            'recommendations': recommendations,
            'estimated_weeks': estimated_weeks,
            'gap_percentage': round(len(missing_skills) / len(job_skills) * 100, 1) if job_skills else 0
        }
    
    def get_career_insights(self, profile):
        """Get insights about the student's career readiness"""
        tech_skills = ['python', 'javascript', 'sql', 'react', 'java', 'c++', 'c#']
        ml_skills = ['machine learning', 'deep learning', 'tensorflow', 'keras', 'nlp']
        cloud_skills = ['aws', 'azure', 'gcp', 'cloud computing', 'docker', 'kubernetes']
        data_skills = ['data science', 'data analysis', 'statistics', 'tableau', 'pandas']
        
        # Use NLP for flexible matching
        categories = {
            'Software Development': sum(1 for s in profile if any(
                self.nlp_matcher.calculate_similarity(s, tech) >= 0.7 for tech in tech_skills
            )),
            'Machine Learning/AI': sum(1 for s in profile if any(
                self.nlp_matcher.calculate_similarity(s, ml) >= 0.7 for ml in ml_skills
            )),
            'Cloud/DevOps': sum(1 for s in profile if any(
                self.nlp_matcher.calculate_similarity(s, cloud) >= 0.7 for cloud in cloud_skills
            )),
            'Data Science/Analytics': sum(1 for s in profile if any(
                self.nlp_matcher.calculate_similarity(s, data) >= 0.7 for data in data_skills
            ))
        }
        
        dominant = max(categories, key=categories.get) if any(categories.values()) else "General Tech"
        
        avg_proficiency = sum(profile.values()) / len(profile) if profile else 0
        
        if avg_proficiency >= 0.7:
            readiness = "Job Ready"
        elif avg_proficiency >= 0.5:
            readiness = "Almost Ready"
        else:
            readiness = "Still Learning"
        
        return {
            'dominant_category': dominant,
            'skill_categories': categories,
            'readiness_level': readiness,
            'avg_proficiency': round(avg_proficiency, 2),
            'total_skills': len(profile)
        }