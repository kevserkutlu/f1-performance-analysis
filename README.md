# Formula 1 Race Performance Analysis and Result Prediction

[cite_start]This project focuses on analyzing historical Formula 1 race data to gain deeper insights into driver and team performances and to develop predictive models for race outcomes[cite: 8, 66]. [cite_start]By leveraging advanced data analysis and machine learning, the project aims to identify the key variables that influence finishing positions[cite: 9, 21].

## 📌 Project Overview
[cite_start]Formula 1 is one of the most data-driven sports in the world, generating vast amounts of information regarding vehicle and driver performance every race weekend[cite: 17, 73]. [cite_start]This study examines performance patterns across multiple dimensions—such as seasons, circuits, and individual drivers—to forecast future race results[cite: 9, 11].

## 🛠️ Tools and Technologies
* [cite_start]**Language:** Python (Primary programming language) 
* [cite_start]**Data Manipulation:** Pandas & NumPy 
* [cite_start]**Machine Learning:** Scikit-learn 
* [cite_start]**Visualization:** Matplotlib & Seaborn 
* [cite_start]**Environment:** Jupyter Notebook 

## 📊 Dataset and Preprocessing
[cite_start]The project initially targeted a full historical dataset (1950–2020), but due to computational intensity and inconsistent formats, the scope was shifted to a more recent and consistent dataset[cite: 97, 103].

* [cite_start]**Current Data Scope:** Formula 1 race data between **2020 and 2024** obtained from Kaggle[cite: 66, 78].
* [cite_start]**Key Features:** [cite: 80]
    * `grid`: Starting position.
    * `Driver Average Position`: Average finishing position in the current year.
    * `points`: Total driver points.
    * `wins`: Number of race wins.
* [cite_start]**Preprocessing Steps:** Data was cleaned by removing missing values using `dropna()`, converting numerical formats, and merging tables via common keys[cite: 81, 85].

## 📈 Exploratory Data Analysis (EDA)
[cite_start]The EDA phase focused on the relationship between starting grid position and race performance[cite: 86, 87].
* [cite_start]**Key Insight:** A strong positive relationship was identified; as the grid position increases (worse starting position), the average finishing position also increases[cite: 91, 92].
* [cite_start]**Conclusion:** Starting grid position is a significant predictor of race outcomes[cite: 69, 95].

## 🤖 Predictive Modeling
[cite_start]The project implements various machine learning models to forecast finishing positions: [cite: 43, 107]
* [cite_start]**Linear Regression:** Used as a baseline model for prediction[cite: 44, 109].
* [cite_start]**Decision Tree:** To capture non-linear relationships[cite: 45].
* [cite_start]**Random Forest:** Applied for improved accuracy and handling complex dynamics[cite: 46, 110].
* [cite_start]**Evaluation:** Model performance is measured using **Root Mean Square Error (RMSE)** and classification accuracy[cite: 47, 111].

## 👥 Project Team
* [cite_start]**Halil Taha Demir** [cite: 2, 62]
* [cite_start]**Sana Dizmari** [cite: 3, 62]
* [cite_start]**Dilara Ünal** [cite: 4, 62]
* [cite_start]**Ceren Göl** [cite: 5, 62]
* [cite_start]**Zeynep Esra Idiz** [cite: 6, 62]
* [cite_start]**Kevser Kutlu** [cite: 62]

---
[cite_start]*Developed at Ankara Medipol University, Department of Computer Engineering.* [cite: 7, 63]