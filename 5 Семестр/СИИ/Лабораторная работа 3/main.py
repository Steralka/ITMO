import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from prettytable import PrettyTable

# ---------- 1) Загрузка ----------
df = pd.read_csv("california_housing_train.csv")

quantiles = df.quantile([0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99])
stats_basic = df.describe().T
stats_full = stats_basic.join(quantiles.T, how="left", rsuffix="_q")

print("Статистика по признакам")
table = PrettyTable()
table.field_names = ["Признак", "count", "mean", "std", "min", "25%", "50%", "75%", "max"]
for name, row in stats_basic.iterrows():
    table.add_row([
        name,
        f"{row['count']:.0f}",
        f"{row['mean']:.2f}",
        f"{row['std']:.2f}",
        f"{row['min']:.2f}",
        f"{row['25%']:.2f}",
        f"{row['50%']:.2f}",
        f"{row['75%']:.2f}",
        f"{row['max']:.2f}"
    ])
print(table)


# ---------- 2) Min–Max нормализация ----------
y_name = "median_house_value"
y = df[y_name].values.astype(float)
X_df = df.drop(columns=[y_name])

X_min = X_df.min()
X_max = X_df.max()
X_norm = (X_df - X_min) / (X_max - X_min)
X_norm = X_norm.fillna(0)

# Пример таблицы нормализации
print("Нормализации")
for col in ["longitude", "latitude", "housing_median_age", "median_income"]:
    t = PrettyTable()
    t.field_names = [f"Признак: {col}", "До нормализации", "После (0–1)"]
    for i in range(5):
        t.add_row([i+1, f"{X_df[col].iloc[i]:.2f}", f"{X_norm[col].iloc[i]:.4f}"])
    print(t)

# ---------- 3) Разделение train/test ----------
rng = np.random.default_rng(42)
idx = np.arange(len(df))
rng.shuffle(idx)
test_ratio = 0.2
test_size = int(len(idx) * test_ratio)
test_idx = idx[:test_size]
train_idx = idx[test_size:]

X = X_norm.values
X_train, X_test = X[train_idx], X[test_idx]
y_train, y_test = y[train_idx], y[test_idx]

# ---------- 4) Реализация OLS ----------
def add_intercept(X):
    return np.hstack([np.ones((X.shape[0], 1)), X])

def ols_fit(X, y):
    return np.linalg.pinv(add_intercept(X)) @ y

def ols_predict(X, beta):
    return add_intercept(X) @ beta

def r2_score(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred)**2)
    ss_tot = np.sum((y_true - y_true.mean())**2)
    return 1 - ss_res / ss_tot if ss_tot != 0 else 0.0

# ---------- 5) Три модели ----------
all_cols = list(X_df.columns)
m1_cols = ["median_income"]
m2_cols = ["longitude", "latitude", "housing_median_age", "median_income"]
m1_idx = [all_cols.index(c) for c in m1_cols]
m2_idx = [all_cols.index(c) for c in m2_cols]

# Модель 3 — все признаки + синтетика
df_eng = df.copy()
df_eng["rooms_per_household"] = df_eng["total_rooms"] / df_eng["households"].replace(0, np.nan)
df_eng["bedrooms_per_room"] = df_eng["total_bedrooms"] / df_eng["total_rooms"].replace(0, np.nan)
df_eng["population_per_household"] = df_eng["population"] / df_eng["households"].replace(0, np.nan)
df_eng = df_eng.fillna(0)

y3 = df_eng[y_name].values.astype(float)
X3_df = df_eng.drop(columns=[y_name])
X3_min = X3_df.min()
X3_max = X3_df.max()
X3_norm = (X3_df - X3_min) / (X3_max - X3_min)
X3_norm = X3_norm.fillna(0)
X3 = X3_norm.values
X3_train, X3_test = X3[train_idx], X3[test_idx]
y3_train, y3_test = y3[train_idx], y3[test_idx]

# ---------- 6) Обучение и оценка ----------
beta1 = ols_fit(X_train[:, m1_idx], y_train)
beta2 = ols_fit(X_train[:, m2_idx], y_train)
beta3 = ols_fit(X3_train, y3_train)

y1_te = ols_predict(X_test[:, m1_idx], beta1)
y2_te = ols_predict(X_test[:, m2_idx], beta2)
y3_te = ols_predict(X3_test, beta3)

r2_1 = r2_score(y_test, y1_te)
r2_2 = r2_score(y_test, y2_te)
r2_3 = r2_score(y3_test, y3_te)

# ---------- 7) Сравнение моделей ----------
print("📈 Сравнение трёх моделей (Min–Max нормализация)")
compare = PrettyTable()
compare.field_names = ["Модель", "Признаки", "R² (test)"]
compare.add_row(["M1", "median_income", f"{r2_1:.4f}"])
compare.add_row(["M2", "geo + age + income", f"{r2_2:.4f}"])
compare.add_row(["M3", "все + синтетика", f"{r2_3:.4f}"])
print(compare)

# ---------- 8) Визуализация результатов ----------

# (a) сравнение R²
plt.figure(figsize=(8,5))
plt.bar(["M1","M2","M3"], [r2_1, r2_2, r2_3], color=["#6fa8dc","#93c47d","#f6b26b"])
plt.title("📊 Сравнение точности моделей (R²)")
plt.ylabel("R² (на тесте)")
for i, v in enumerate([r2_1, r2_2, r2_3]):
    plt.text(i, v+0.005, f"{v:.3f}", ha='center', fontweight='bold')
plt.tight_layout()
plt.show()

# (b) scatter-графики “факт vs предсказание” для всех моделей
y1_true, y2_true, y3_true = y_test, y_test, y3_test
fig, axs = plt.subplots(1, 3, figsize=(16, 5))

models = [
    ("M1: median_income", y1_true, y1_te, "#6fa8dc"),
    ("M2: geo + age + income", y2_true, y2_te, "#93c47d"),
    ("M3: full + engineered", y3_true, y3_te, "#f6b26b")
]

for ax, (title, y_t, y_h, color) in zip(axs, models):
    ax.scatter(y_t, y_h, s=10, color=color, alpha=0.6)
    lims = [min(y_t.min(), y_h.min()), max(y_t.max(), y_h.max())]
    ax.plot(lims, lims, 'r--', lw=1)
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.set_xlabel("Факт")
    ax.set_ylabel("Предсказание")
    ax.grid(alpha=0.3)

plt.suptitle("📈 Сравнение моделей: Факт vs Предсказание", fontsize=14, fontweight='bold')
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()

# (c) распределения остатков (ошибок)
fig, axs = plt.subplots(1, 3, figsize=(16, 4))

residuals = [
    ("M1", y1_true - y1_te, "#6fa8dc"),
    ("M2", y2_true - y2_te, "#93c47d"),
    ("M3", y3_true - y3_te, "#f6b26b")
]

for ax, (name, res, color) in zip(axs, residuals):
    ax.hist(res, bins=40, color=color, edgecolor='black', alpha=0.8)
    ax.set_title(f"Остатки — {name}", fontweight='bold')
    ax.set_xlabel("Ошибка (y - ŷ)")
    ax.set_ylabel("Частота")
    ax.grid(alpha=0.3)

plt.suptitle("📉 Распределения ошибок по моделям", fontsize=14, fontweight='bold')
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()


# ---------- 9) Факт vs Предсказание для лучшей модели ----------
best_model = max([(r2_1, "M1", y_test, y1_te),
                  (r2_2, "M2", y_test, y2_te),
                  (r2_3, "M3", y3_test, y3_te)], key=lambda x: x[0])
_, best_name, y_true, y_hat = best_model

plt.figure(figsize=(6,6))
plt.scatter(y_true, y_hat, s=10, color='teal')
lims = [min(y_true.min(), y_hat.min()), max(y_true.max(), y_hat.max())]
plt.plot(lims, lims, 'r--')
plt.xlabel("Факт")
plt.ylabel("Предсказание")
plt.title(f"Факт vs Предсказание — {best_name}")
plt.tight_layout()
plt.show()

# (c) распределение остатков
residuals = y_true - y_hat
plt.figure(figsize=(8,5))
plt.hist(residuals, bins=40, edgecolor='black', color='salmon')
plt.title(f"Распределение остатков — {best_name}")
plt.xlabel("Остаток (y - ŷ)")
plt.ylabel("Частота")
plt.tight_layout()
plt.show()
