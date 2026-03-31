import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 📌 DATA LOAD (dosya aynı klasörde olmalı!)
df = pd.read_csv("data/raw/F1 Races 2020-2024.csv")

# 📌 VERİYİ İNCELE (istersen kapatabilirsin)
print("Columns:", df.columns)

# 📌 CLEANING
df = df.dropna()

# 📌 GRAFİK AYARLARI
plt.figure(figsize=(10,6))

# 📊 SCATTER + ŞEFFAFLIK (üst üste binmeyi azaltır)
sns.scatterplot(
    x="grid",
    y="Driver Average Position (This Year till last race)",
    data=df,
    alpha=0.3
)

# 📈 TREND ÇİZGİSİ (hocaya hava)
sns.regplot(
    x="grid",
    y="Driver Average Position (This Year till last race)",
    data=df,
    scatter=False,
    color="red"
)

# 📌 BAŞLIK VE ETİKETLER
plt.title("Effect of Grid Position on Race Performance", fontsize=14)
plt.xlabel("Starting Grid Position")
plt.ylabel("Average Finishing Position")

# 📌 GRID (görsellik)
plt.grid(True)

# 📌 GRAFİĞİ GÖSTER
plt.show()