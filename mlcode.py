# -------------------------------------------
#  HIGH ACCURACY DIABETES MODEL (XGBOOST)
# -------------------------------------------

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier
import joblib

# -------------------------------
# 1. Load data
# -------------------------------
df = pd.read_csv("diabetes.csv")
print("Dataset Loaded Successfully!")
print(df.head())

# -------------------------------
# 2. Replace invalid zeros with NaN
# -------------------------------
invalid_cols = ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"]

for col in invalid_cols:
    df[col] = df[col].replace(0, np.nan)

# -------------------------------
# 3. Impute missing values
# -------------------------------
imputer = SimpleImputer(strategy="median")
df_filled = pd.DataFrame(imputer.fit_transform(df), columns=df.columns)

# -------------------------------
# 4. X and y
# -------------------------------
X = df_filled.drop("Outcome", axis=1)
y = df_filled["Outcome"]

# -------------------------------
# 5. Fix imbalance
# -------------------------------
sm = SMOTE(random_state=42)
X_resampled, y_resampled = sm.fit_resample(X, y)

# -------------------------------
# 6. Train-test split
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X_resampled, y_resampled, test_size=0.2, random_state=42
)

# -------------------------------
# 7. Scaling
# -------------------------------
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# -------------------------------
# 8. XGBoost Classifier
# -------------------------------
xgb = XGBClassifier(
    objective="binary:logistic",
    eval_metric="logloss"
)

params = {
    "n_estimators": [100, 200, 300],
    "max_depth": [3, 4, 5],
    "learning_rate": [0.01, 0.05, 0.1],
    "subsample": [0.7, 0.8, 1.0],
}

grid = GridSearchCV(xgb, params, cv=3, scoring="accuracy", verbose=1)
grid.fit(X_train_scaled, y_train)

best_model = grid.best_estimator_
print("Best Parameters:", grid.best_params_)

# -------------------------------
# 9. Final accuracy
# -------------------------------
y_pred = best_model.predict(X_test_scaled)
acc = accuracy_score(y_test, y_pred)
print("Final XGBoost Accuracy:", acc)

# -------------------------------
# 10. Save model if above 90%
# -------------------------------
if acc >= 0.90:
    joblib.dump(best_model, "diabetes_best_model.pkl")
    print("High Accuracy Model Saved Successfully!")
else:
    print("Accuracy < 90%. Try more tuning.")

joblib.dump(best_model, "diabetes_best_model.pkl")
print("Model saved as diabetes_best_model.pkl")

print("Final XGBoost Accuracy:", acc)

if acc >= 0.90:
    joblib.dump(best_model, "diabetes_best_model.pkl")
    print("High Accuracy Model Saved Successfully!")
else:
    joblib.dump(best_model, "diabetes_best_model.pkl")
    print("Accuracy < 90%. Model still saved for usage.")
