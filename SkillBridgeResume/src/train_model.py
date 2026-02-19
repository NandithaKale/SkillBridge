import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

print("="*70)
print("TRAINING MACHINE LEARNING MODEL")
print("="*70)

# Load training data
print("\n📂 Loading training data...")

profiles_df = pd.read_excel('data/training_data/profiles.xlsx')
courses_df = pd.read_excel('data/training_data/courses.xlsx')
matches_df = pd.read_excel('data/training_data/matches.xlsx')

print(f"✓ Loaded {len(profiles_df)} skill profiles")
print(f"✓ Loaded {len(courses_df)} course records")
print(f"✓ Loaded {len(matches_df)} job matches")

# Prepare features for training
print("\n🔧 Preparing training features...")

# Aggregate student metrics
student_features = courses_df.groupby('student_id').agg({
    'progress': 'mean',
    'grade': 'mean',
    'time_spent_hours': 'sum',
    'course_name': 'count'
}).reset_index()

student_features.columns = ['student_id', 'avg_progress', 'avg_grade', 
                            'total_time', 'num_courses']

# Count skills per student
skill_counts = profiles_df.groupby('student_id').size().reset_index(name='num_skills')
student_features = student_features.merge(skill_counts, on='student_id')

# Get max proficiency per student
max_prof = profiles_df.groupby('student_id')['proficiency'].max().reset_index()
max_prof.columns = ['student_id', 'max_proficiency']
student_features = student_features.merge(max_prof, on='student_id')

print(f"✓ Prepared features for {len(student_features)} students")

# Create training dataset for match score prediction
print("\n🎯 Creating training dataset...")

# Get top match for each student
top_matches = matches_df.loc[matches_df.groupby('student_id')['match_score'].idxmax()]

# Merge with features
training_data = student_features.merge(top_matches[['student_id', 'match_score']], 
                                       on='student_id')

# Features and target
X = training_data[['avg_progress', 'avg_grade', 'total_time', 'num_courses', 
                   'num_skills', 'max_proficiency']]
y = training_data['match_score']

print(f"✓ Training dataset shape: {X.shape}")

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"  Training samples: {len(X_train)}")
print(f"  Testing samples: {len(X_test)}")

# Train multiple models
print("\n🚀 Training models...")

# Model 1: Random Forest
print("\n  Training Random Forest...")
rf_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
rf_model.fit(X_train, y_train)
rf_pred = rf_model.predict(X_test)
rf_mse = mean_squared_error(y_test, rf_pred)
rf_r2 = r2_score(y_test, rf_pred)

print(f"    MSE: {rf_mse:.4f}")
print(f"    R² Score: {rf_r2:.4f}")

# Model 2: Gradient Boosting
print("\n  Training Gradient Boosting...")
gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
gb_model.fit(X_train, y_train)
gb_pred = gb_model.predict(X_test)
gb_mse = mean_squared_error(y_test, gb_pred)
gb_r2 = r2_score(y_test, gb_pred)

print(f"    MSE: {gb_mse:.4f}")
print(f"    R² Score: {gb_r2:.4f}")

# Select best model
if rf_r2 > gb_r2:
    best_model = rf_model
    best_model_name = "Random Forest"
    best_r2 = rf_r2
else:
    best_model = gb_model
    best_model_name = "Gradient Boosting"
    best_r2 = gb_r2

print(f"\n✓ Best Model: {best_model_name} (R² = {best_r2:.4f})")

# Save model
print("\n💾 Saving model and metadata...")

os.makedirs('data/models', exist_ok=True)

joblib.dump(best_model, 'data/models/match_predictor.pkl')

# Save feature names
metadata = {
    'feature_names': list(X.columns),
    'model_type': best_model_name,
    'r2_score': best_r2
}
joblib.dump(metadata, 'data/models/metadata.pkl')

# Save skill dictionary
all_skills = profiles_df['skill'].unique().tolist()
joblib.dump(all_skills, 'data/models/skill_list.pkl')

print(f"✓ Model saved to data/models/")

print("\n" + "="*70)
print("✓ MODEL TRAINING COMPLETE!")
print("="*70)