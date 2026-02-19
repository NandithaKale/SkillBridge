"""
NLP-based Skill Matcher using spaCy
Provides semantic matching for skills (e.g., "ML" matches "machine learning")
"""

import spacy
import numpy as np
from typing import List, Dict, Tuple

class NLPSkillMatcher:
    def __init__(self, similarity_threshold=0.65):
        """
        Initialize NLP matcher with spaCy
        
        Args:
            similarity_threshold: Minimum similarity score (0-1) to consider a match
        """
        self.similarity_threshold = similarity_threshold
        
        try:
            # Load medium English model (includes word vectors)
            self.nlp = spacy.load("en_core_web_md")
            print("✅ NLP model loaded successfully!")
        except OSError:
            print("❌ spaCy model not found. Run: python -m spacy download en_core_web_md")
            print("⚠️  Falling back to exact string matching...")
            self.nlp = None
        
        # Common skill synonyms (manual mapping for high accuracy)
        self.skill_synonyms = {
            'ml': 'machine learning',
            'ai': 'artificial intelligence',
            'js': 'javascript',
            'ts': 'typescript',
            'py': 'python',
            'k8s': 'kubernetes',
            'dl': 'deep learning',
            'nlp': 'natural language processing',
            'cv': 'computer vision',
            'aws': 'amazon web services',
            'gcp': 'google cloud platform',
            'react.js': 'react',
            'vue.js': 'vue',
            'node.js': 'nodejs',
            'sql server': 'sql',
            'mysql': 'sql',
            'postgresql': 'sql',
            'nosql': 'database',
            'mongodb': 'database',
        }
    
    def normalize_skill(self, skill: str) -> str:
        """Normalize skill name (lowercase, handle synonyms)"""
        skill = skill.lower().strip()
        
        # Check for direct synonym match
        if skill in self.skill_synonyms:
            return self.skill_synonyms[skill]
        
        return skill
    
    def calculate_similarity(self, skill1: str, skill2: str) -> float:
        """
        Calculate semantic similarity between two skills
        
        Returns:
            float: Similarity score (0-1)
        """
        skill1 = self.normalize_skill(skill1)
        skill2 = self.normalize_skill(skill2)
        
        # Exact match
        if skill1 == skill2:
            return 1.0
        
        # If NLP not available, use simple string matching
        if self.nlp is None:
            return 1.0 if skill1 == skill2 else 0.0
        
        # Use spaCy for semantic similarity
        try:
            doc1 = self.nlp(skill1)
            doc2 = self.nlp(skill2)
            
            # Check if documents have vectors
            if doc1.has_vector and doc2.has_vector:
                similarity = doc1.similarity(doc2)
                return max(0.0, min(1.0, similarity))  # Clamp between 0-1
            else:
                return 1.0 if skill1 == skill2 else 0.0
        except Exception as e:
            print(f"⚠️  Error calculating similarity: {e}")
            return 1.0 if skill1 == skill2 else 0.0
    
    def find_matches(self, student_skills: List[str], job_skills: List[str]) -> Dict:
        """
        Find matching skills between student and job using NLP
        
        Args:
            student_skills: List of skills the student has
            job_skills: List of skills the job requires
        
        Returns:
            dict: {
                'matched': [(student_skill, job_skill, similarity), ...],
                'unmatched_job_skills': [skill, ...],
                'unused_student_skills': [skill, ...]
            }
        """
        matched = []
        used_student_skills = set()
        used_job_skills = set()
        
        # For each job skill, find best matching student skill
        for job_skill in job_skills:
            best_match = None
            best_similarity = self.similarity_threshold
            
            for student_skill in student_skills:
                if student_skill in used_student_skills:
                    continue
                
                similarity = self.calculate_similarity(student_skill, job_skill)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = student_skill
            
            if best_match:
                matched.append((best_match, job_skill, best_similarity))
                used_student_skills.add(best_match)
                used_job_skills.add(job_skill)
        
        # Find unmatched skills
        unmatched_job_skills = [s for s in job_skills if s not in used_job_skills]
        unused_student_skills = [s for s in student_skills if s not in used_student_skills]
        
        return {
            'matched': matched,
            'unmatched_job_skills': unmatched_job_skills,
            'unused_student_skills': unused_student_skills
        }
    
    def get_match_quality(self, matched_pairs: List[Tuple]) -> Dict:
        """
        Analyze quality of matches
        
        Returns:
            dict: Statistics about match quality
        """
        if not matched_pairs:
            return {
                'avg_similarity': 0.0,
                'perfect_matches': 0,
                'good_matches': 0,
                'fair_matches': 0
            }
        
        similarities = [sim for _, _, sim in matched_pairs]
        
        return {
            'avg_similarity': np.mean(similarities),
            'perfect_matches': sum(1 for s in similarities if s >= 0.95),
            'good_matches': sum(1 for s in similarities if 0.80 <= s < 0.95),
            'fair_matches': sum(1 for s in similarities if 0.65 <= s < 0.80)
        }


# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing NLP Skill Matcher\n")
    
    matcher = NLPSkillMatcher()
    
    # Test cases
    test_cases = [
        ("python", "python programming"),
        ("machine learning", "ML"),
        ("javascript", "js"),
        ("deep learning", "neural networks"),
        ("react", "react.js"),
        ("aws", "amazon web services"),
        ("kubernetes", "k8s"),
        ("sql", "mysql"),
        ("data science", "data analysis"),
        ("python", "java"),  # Should NOT match
    ]
    
    print("📊 Similarity Test Results:")
    print("-" * 60)
    for skill1, skill2 in test_cases:
        similarity = matcher.calculate_similarity(skill1, skill2)
        match_status = "✅ MATCH" if similarity >= 0.65 else "❌ NO MATCH"
        print(f"{skill1:20} ↔ {skill2:20} | {similarity:.3f} {match_status}")
    
    print("\n" + "=" * 60)
    print("🎯 Full Matching Example:\n")
    
    student_skills = ["python", "ML", "data visualization", "sql", "react.js"]
    job_skills = ["python programming", "machine learning", "tableau", "database", "react"]
    
    print(f"Student Skills: {student_skills}")
    print(f"Job Requirements: {job_skills}\n")
    
    results = matcher.find_matches(student_skills, job_skills)
    
    print("✅ Matched Skills:")
    for student_skill, job_skill, similarity in results['matched']:
        print(f"   {student_skill} → {job_skill} (similarity: {similarity:.3f})")
    
    print(f"\n❌ Missing Skills: {results['unmatched_job_skills']}")
    print(f"💡 Extra Skills: {results['unused_student_skills']}")
    
    quality = matcher.get_match_quality(results['matched'])
    print(f"\n📈 Match Quality:")
    print(f"   Average Similarity: {quality['avg_similarity']:.3f}")
    print(f"   Perfect Matches (≥0.95): {quality['perfect_matches']}")
    print(f"   Good Matches (0.80-0.95): {quality['good_matches']}")
    print(f"   Fair Matches (0.65-0.80): {quality['fair_matches']}")