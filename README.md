# SkillBridge 🎯
### Know Your Skills, Find Your Path

A skill-based student progress and career recommendation system that bridges the gap 
between online certifications and real-world career opportunities.

---

## 📌 About the Project

SkillBridge is an integrated platform that automatically extracts skills from resumes 
and course certificates, evaluates competency levels, and recommends personalized 
career paths — all within a single unified system.

Built as a mini-project for the Bachelor of Engineering in Computer Science and 
Business Systems at BMS Institute of Technology & Management, Bengaluru (VTU), 2024-25.

---

## ✨ Features

- 📄 **Resume Parsing** — Upload a PDF resume; skills, education, and experience are extracted automatically
- 🎓 **Course Management** — Add completed courses with progress, grades, and hours spent
- 🧠 **Skill Proficiency Scoring** — Proficiency computed using a weighted formula:
  `Score = 0.5 × Progress + 0.3 × Grade + 0.2 × Duration`
- 🔍 **Semantic Job Matching** — NLP-powered matching using spaCy embeddings and cosine similarity
- 📊 **Career Recommendations** — Top job roles ranked by a composite match score (0–100)
- 🕳️ **Skill Gap Analysis** — Identifies missing skills and suggests targeted courses
- 📈 **Analytics Dashboard** — Visualizes skill distribution, course progress, and job readiness
- 📧 **Email Notifications** — Sends career insights and recommendations to your inbox via SendGrid

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | Python 3.8+ |
| NLP | spaCy, NLTK |
| Machine Learning | scikit-learn |
| Resume Parsing | PyPDF2, pytesseract (OCR) |
| Database | SQLite (dev) / MySQL (production) |
| Visualization | Plotly, Matplotlib |
| Email Service | SendGrid |
| Authentication | bcrypt |
| Data Processing | pandas, NumPy |

---

## ⚙️ Getting Started

### Prerequisites
- Python 3.8+
- pip
- A SendGrid account (for email features)

### Installation

1. **Clone the repository**
```
   git clone https://github.com/NandithaKale/SkillBridge.git
   cd SkillBridge
```

2. **Install dependencies**
```
   pip install -r requirements.txt
```

3. **Set up environment variables**

   Create a `.env` file in the root directory:
```
   SENDGRID_API_KEY=your_sendgrid_api_key_here
```

4. **Run the application**
```
   streamlit run app.py
```

---

## 🧩 System Architecture

The system follows a 4-layer architecture:

- **Presentation Layer** — Streamlit web dashboard
- **Business Logic Layer** — Python modules: AuthManager, ResumeParser, CareerPredictor, EmailService
- **Data Processing Layer** — NLP engine (spaCy) for semantic skill analysis
- **Persistence Layer** — Relational database storing users, courses, jobs, and recommendations

---

## 📊 How the Matching Works

1. Skills are extracted from resumes and course certificates using NLP
2. Proficiency scores are computed per skill based on progress, grade, and time invested
3. User skills are semantically matched against job requirements (threshold: cosine similarity ≥ 0.65)
4. A composite match score is calculated:
   `MatchScore = 40 × Coverage + 50 × AvgProficiency + 10 × ImportanceScore`
5. Jobs are ranked and displayed with skill gap analysis and learning path suggestions

---

## 👩‍💻 Team

| Name | USN |
|---|---|
| D. Nanditha Kale | 1BY23CB012 |
| Rishika Gitta | 1BY23CB043 |
| Sai Kavyashree S. | 1BY23CB048 |
| Sanjana Athani | 1BY24CB403 |

**Guide:** Dr. Vishwa Kiran S., Professor & Head of Department, CSBS — BMSIT&M

---

## 🔮 Future Scope

- Integration with LinkedIn, GitHub, and digital badge platforms
- Transformer-based embeddings (BERT/GPT) for improved matching
- Expanded skill taxonomy using ESCO / ONET standards
- Mobile application for on-the-go career guidance
- Feedback loops for continuous personalization

---

## 📄 License

This project was developed for academic purposes under VTU, 2024-25.
