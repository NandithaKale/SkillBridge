import PyPDF2
import re

class ResumeParser:
    def __init__(self, course_skills):
        self.course_skills = course_skills
        self.all_skills = set()
        for skills_list in course_skills.values():
            self.all_skills.update([s.lower() for s in skills_list])
        
        self.skill_patterns = {
            'Python': [r'\bpython\b', r'\bpy\b'],
            'Java': [r'\bjava\b'],
            'JavaScript': [r'\bjavascript\b', r'\bjs\b'],
            'Machine Learning': [r'\bmachine learning\b', r'\bml\b', r'\bdeep learning\b'],
            'Data Analysis': [r'\bdata analysis\b', r'\banalytics\b', r'\bpandas\b'],
            'SQL': [r'\bsql\b', r'\bmysql\b', r'\bpostgresql\b'],
            'Web Development': [r'\bweb dev\b', r'\bhtml\b', r'\bcss\b', r'\breact\b'],
            'Cloud Computing': [r'\baws\b', r'\bazure\b', r'\bcloud\b'],
        }
        
        self.education_patterns = {
            'PhD': r'\bph\.?d\b|\bdoctorate\b',
            'Masters': r'\bmasters?\b|\bm\.?s\.?\b|\bmba\b',
            'Bachelors': r'\bbachelors?\b|\bb\.?s\.?\b|\bb\.?tech\b',
        }
    
    def extract_text_from_pdf(self, pdf_file):
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text.strip()
        except:
            return None
    
    def detect_skills(self, text):
        text_lower = text.lower()
        detected = {}
        for skill, patterns in self.skill_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    detected[skill] = True
                    break
        return list(detected.keys())
    
    def detect_education(self, text):
        text_lower = text.lower()
        for level, pattern in self.education_patterns.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                return level
        return "Not specified"
    
    def estimate_experience(self, text):
        years = re.findall(r'\b(19|20)\d{2}\b', text)
        if len(years) >= 2:
            years_int = [int(y) for y in years]
            return min(max(years_int) - min(years_int), 25)
        return 0
    
    def extract_email(self, text):
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(pattern, text)
        return emails[0] if emails else None
    
    def extract_phone(self, text):
        patterns = [r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', r'\+\d{1,3}\s?\d{10}\b']
        for pattern in patterns:
            phones = re.findall(pattern, text)
            if phones:
                return phones[0]
        return None
    
    def suggest_courses(self, detected_skills):
        suggested = []
        for course, skills in self.course_skills.items():
            skills_lower = [s.lower() for s in skills]
            for skill in detected_skills:
                if skill.lower() in skills_lower:
                    if course not in suggested:
                        suggested.append(course)
                    break
        return suggested
    
    def parse_resume(self, pdf_file):
        text = self.extract_text_from_pdf(pdf_file)
        if not text or len(text) < 50:
            return None, "Failed to extract text from PDF"
        
        return {
            'skills': self.detect_skills(text),
            'education': self.detect_education(text),
            'experience_years': self.estimate_experience(text),
            'email': self.extract_email(text),
            'phone': self.extract_phone(text),
            'suggested_courses': self.suggest_courses(self.detect_skills(text)),
            'text_preview': text[:500]
        }, None