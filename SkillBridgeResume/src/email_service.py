import requests
from datetime import datetime
import os

class EmailService:
    def __init__(self):
        """Initialize SendGrid email service"""
        # PASTE YOUR SENDGRID API KEY HERE
        SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")  # CHANGE THIS
        self.sender_email = "rishikagitta05@gmail.com"  # Can be any email
        self.sender_name = "SkillBridge Team"
    
    def send_recommendations_email(self, user_email, user_name, recommendations, profile, insights):
        """Send job recommendations via SendGrid API"""
        
        # Calculate stats
        avg_prof = sum(profile.values()) / len(profile) if profile else 0
        expert_skills = sum(1 for p in profile.values() if p >= 0.8)
        top_match = recommendations[0]['match_score'] if recommendations else 0
        
        # Create HTML email (same as before)
        html_body = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 600px;
                    margin: 20px auto;
                    background: white;
                    padding: 0;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #1f77b4 0%, #2e7d32 100%);
                    color: white;
                    padding: 30px 20px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                }}
                .content {{
                    padding: 30px 20px;
                }}
                .stats-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr 1fr;
                    gap: 15px;
                    margin: 20px 0;
                }}
                .stat-card {{
                    background: #f0f8ff;
                    padding: 15px;
                    border-radius: 8px;
                    text-align: center;
                    border-left: 4px solid #1f77b4;
                }}
                .stat-value {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #1f77b4;
                    margin: 5px 0;
                }}
                .stat-label {{
                    font-size: 12px;
                    color: #666;
                }}
                .job-card {{
                    background: #fff;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 15px 0;
                }}
                .job-title {{
                    color: #1f77b4;
                    font-size: 18px;
                    font-weight: bold;
                    margin: 0 0 5px 0;
                }}
                .job-company {{
                    color: #666;
                    font-size: 14px;
                    margin: 0 0 10px 0;
                }}
                .match-badge {{
                    display: inline-block;
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: bold;
                    color: white;
                }}
                .match-excellent {{ background: #2e7d32; }}
                .match-good {{ background: #558b2f; }}
                .match-fair {{ background: #f9a825; }}
                .skills-row {{
                    font-size: 13px;
                    color: #555;
                    margin-top: 8px;
                }}
                .cta-button {{
                    display: inline-block;
                    background: #1f77b4;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 25px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .footer {{
                    background: #f5f5f5;
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                    border-top: 1px solid #e0e0e0;
                }}
                .insight-box {{
                    background: #e8f5e9;
                    border-left: 4px solid #2e7d32;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎓 SkillBridge</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px;">Your Personalized Career Recommendations</p>
                </div>
                
                <div class="content">
                    <p>Hi <strong>{user_name}</strong>,</p>
                    
                    <p>Great news! Based on your profile analysis, we've found some excellent job matches for you.</p>
                    
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-value">{top_match:.0f}/100</div>
                            <div class="stat-label">Best Match</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{len(profile)}</div>
                            <div class="stat-label">Total Skills</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{expert_skills}</div>
                            <div class="stat-label">Expert Skills</div>
                        </div>
                    </div>
                    
                    <div class="insight-box">
                        <strong>🎯 Career Path:</strong> {insights['dominant_category']}<br>
                        <strong>📈 Readiness Level:</strong> {insights['readiness_level']}<br>
                        <strong>💡 Avg Proficiency:</strong> {avg_prof:.0%}
                    </div>
                    
                    <h2 style="color: #1f77b4; border-bottom: 2px solid #1f77b4; padding-bottom: 10px;">
                        🏆 Your Top 5 Job Matches
                    </h2>
        """
        
        # Add top 5 jobs
        for i, rec in enumerate(recommendations[:5], 1):
            if rec['match_score'] >= 80:
                badge_class = "match-excellent"
                badge_text = "Excellent Match"
            elif rec['match_score'] >= 60:
                badge_class = "match-good"
                badge_text = "Good Match"
            else:
                badge_class = "match-fair"
                badge_text = "Fair Match"
            
            html_body += f"""
                    <div class="job-card">
                        <div class="job-title">#{i}. {rec['title']}</div>
                        <div class="job-company">🏢 {rec['company']}</div>
                        <span class="match-badge {badge_class}">{rec['match_score']:.0f}/100 - {badge_text}</span>
                        <div class="skills-row">
                            ✅ <strong>{rec['num_matched']}/{rec['num_required']}</strong> skills matched 
                            ({rec['match_percentage']:.0f}% coverage)
                        </div>
            """
            
            if rec['matched_skills']:
                skills_preview = ', '.join(rec['matched_skills'][:5])
                if len(rec['matched_skills']) > 5:
                    skills_preview += f" +{len(rec['matched_skills'])-5} more"
                html_body += f"""
                        <div class="skills-row" style="margin-top: 5px;">
                            🔧 <em>{skills_preview}</em>
                        </div>
                """
            
            html_body += """
                    </div>
            """
        
        html_body += f"""
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="http://localhost:8501" class="cta-button">
                            View Full Analysis & More Jobs →
                        </a>
                    </div>
                    
                    <div style="background: #fff3e0; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <strong>💡 Next Steps:</strong>
                        <ol style="margin: 10px 0; padding-left: 20px;">
                            <li>Review detailed skill gaps in your dashboard</li>
                            <li>Take recommended courses to fill gaps</li>
                            <li>Update your resume with verified skills</li>
                            <li>Start applying to jobs with 70+ match scores</li>
                        </ol>
                    </div>
                </div>
                
                <div class="footer">
                    <p><strong>SkillBridge - AI-Powered Career Matching</strong></p>
                    <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # SendGrid API request
        url = "https://api.sendgrid.com/v3/mail/send"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "personalizations": [
                {
                    "to": [{"email": user_email, "name": user_name}],
                    "subject": f"🎯 Your SkillBridge Job Recommendations - {datetime.now().strftime('%B %d, %Y')}"
                }
            ],
            "from": {
                "email": self.sender_email,
                "name": self.sender_name
            },
            "content": [
                {
                    "type": "text/html",
                    "value": html_body
                }
            ]
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 202:
                return True, "Email sent successfully! Check your inbox."
            else:
                return False, f"SendGrid error: {response.status_code} - {response.text}"
        
        except Exception as e:
            return False, f"Failed to send email: {str(e)}"