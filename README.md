# Formula 1 Race Performance Analysis and Result Prediction

This project focuses on analyzing historical Formula 1 race data to gain deeper insights into driver and team performances and to develop predictive models for race outcomes. By leveraging advanced data analysis and machine learning, the project aims to identify the key variables that influence finishing positions.

## 📌 Project Overview
Formula 1 is one of the most data-driven sports in the world, generating vast amounts of information regarding vehicle and driver performance every race weekend. This study examines performance patterns across multiple dimensions—such as seasons, circuits, and individual drivers—to forecast future race results.

## 🛠️ Tools and Technologies
* **Language:** Python (Primary programming language)
* **Data Manipulation:** Pandas & NumPy
* **Machine Learning:** Scikit-learn
* **Visualization:** Matplotlib & Seaborn
* **Environment:** Jupyter Notebook

## 📊 Dataset and Preprocessing
The project initially targeted a full historical dataset (1950–2020), but due to computational intensity and inconsistent formats, the scope was shifted to a more recent and consistent dataset.

* **Current Data Scope:** Formula 1 race data between **2020 and 2024** obtained from Kaggle.
* **Key Features:**
    * `grid`: Starting position.
    * `Driver Average Position`: Average finishing position in the current year.
    * `points`: Total driver points.
    * `wins`: Number of race wins.
* **Preprocessing Steps:** Data was cleaned by removing missing values using `dropna()`, converting numerical formats, and merging tables via common keys.

## 📈 Exploratory Data Analysis (EDA)
The EDA phase focused on the relationship between starting grid position and race performance.
* **Key Insight:** A strong positive relationship was identified; as the grid position increases (worse starting position), the average finishing position also increases.
* **Conclusion:** Starting grid position is a significant predictor of race outcomes.

## 🤖 Predictive Modeling
The project implements various machine learning models to forecast finishing positions:
* **Linear Regression:** Used as a baseline model for prediction.
* **Decision Tree:** To capture non-linear relationships.
* **Random Forest:** Applied for improved accuracy and handling complex dynamics.
* **Evaluation:** Model performance is measured using **Root Mean Square Error (RMSE)** and classification accuracy.

## 👥 Project Team
* **Halil Taha Demir**
* **Sana Dizmari**
* **Dilara Ünal**
* **Ceren Göl**
* **Zeynep Esra Idiz**
* **Kevser Kutlu**

---
*Developed at Ankara Medipol University, Department of Computer Engineering.*