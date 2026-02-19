#!/usr/bin/env python3
"""
SkillBridge System Setup
Generates training data and initializes the career recommendation system
"""

import os
import sys

def main():
    print("=" * 70)
    print("🎓 SkillBridge - Career Recommendation System Setup")
    print("=" * 70)
    print()
    
    # Check if data already exists
    if os.path.exists('data/training_data/jobs.xlsx'):
        print("⚠️  Training data already exists!")
        response = input("Do you want to regenerate the data? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("✅ Using existing data. Setup complete!")
            return
    
    # Import and run data generator
    print("\n📊 Generating diverse training data...")
    print("-" * 70)
    
    from src.data_generator import DataGenerator
    
    generator = DataGenerator(num_students=10000, num_jobs=100)
    generator.generate_all_data()
    
    print("\n" + "=" * 70)
    print("✅ Setup Complete!")
    print("=" * 70)
    print("\n🚀 Next Steps:")
    print("   1. Run the dashboard: streamlit run dashboard/real_time_app.py")
    print("   2. Enter your course information")
    print("   3. Get personalized job recommendations!")
    print()

if __name__ == "__main__":
    main()