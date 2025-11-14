import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Параметры
FILE_PATH = "WineDataset.xls"
OUT_DIR = "./lab4_outputs"
RANDOM_SEED = 42
TEST_SIZE = 0.30
KS = [3, 5, 7, 9, 11]
N_FEATURES_TO_USE = 3

# 
# Утилы
# 
def ensure_outdir(path):
    """Создать папку вывода, если нет."""
    os.makedirs(path, exist_ok=True)

def try_read_table(path):
    """Попытки читать Excel, затем CSV с разными разделителями."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Файл не найден: {path}")
    # пробуем excel
    try:
        df = pd.read_excel(path)
        return df
    except Exception:
        # пробуем csv
        try:
            df = pd.read_csv(path)
            return df
        except Exception:
            for sep in [',',';','\t','|']:
                try:
                    df = pd.read_csv(path, sep=sep)
                    return df
                except Exception:
                    continue
    raise ValueError("Не удалось прочитать файл как excel или csv.")

def summarize_features(X_df):
    """Возвращает таблицу основных статистик по признакам."""
    stats = {
        "count": X_df.count(),
        "mean": X_df.mean(),
        "std": X_df.std(ddof=0),
        "min": X_df.min(),
        "25%": X_df.quantile(0.25),
        "50%": X_df.quantile(0.5),
        "75%": X_df.quantile(0.75),
        "max": X_df.max()
    }
    return pd.DataFrame(stats)

# 
# k-NN (без sklearn)
# 
def euclidean_distances(A, B):
    """Векторизованное вычисление евклидовых расстояний."""
    AA = np.sum(A*A, axis=1).reshape(-1,1)
    BB = np.sum(B*B, axis=1).reshape(1,-1)
    AB = A.dot(B.T)
    d2 = AA + BB - 2*AB
    d2 = np.maximum(d2, 0.0)
    return np.sqrt(d2)

def knn_predict(X_train, y_train, X_test, k=3):
    """Простая k-NN: majority vote, при ничьей — минимальная метка."""
    if k <= 0:
        raise ValueError("k must be > 0")
    if X_train.shape[0] == 0:
        raise ValueError("Пустой X_train")
    dists = euclidean_distances(X_test, X_train)
    n_test = dists.shape[0]
    preds = np.empty(n_test, dtype=y_train.dtype)
    for i in range(n_test):
        idx = np.argsort(dists[i])[:k]
        neigh = y_train[idx]
        vals, counts = np.unique(neigh, return_counts=True)
        max_count = counts.max()
        candidates = vals[counts == max_count]
        preds[i] = candidates.min()
    return preds

# 
# Метрики и матрица ошибок
# 
def confusion_matrix(y_true, y_pred):
    """Матрица ошибок и список меток."""
    labels = np.unique(np.concatenate([y_true, y_pred]))
    label_index = {lab: idx for idx, lab in enumerate(labels)}
    cm = np.zeros((len(labels), len(labels)), dtype=int)
    for t, p in zip(y_true, y_pred):
        cm[label_index[t], label_index[p]] += 1
    return cm, labels

def compute_metrics_from_cm(cm):
    """Precision/Recall/F1 (macro) и accuracy из cm."""
    tp = np.diag(cm).astype(float)
    support = cm.sum(axis=1).astype(float)
    precision_per_class = np.where(cm.sum(axis=0) == 0, 0.0, tp / cm.sum(axis=0))
    recall_per_class = np.where(support == 0, 0.0, tp / support)
    f1_per_class = np.where((precision_per_class + recall_per_class) == 0, 0.0,
                            2 * precision_per_class * recall_per_class / (precision_per_class + recall_per_class))
    accuracy = tp.sum() / cm.sum() if cm.sum() > 0 else 0.0
    return {
        "accuracy": float(accuracy),
        "precision_macro": float(np.mean(precision_per_class)),
        "recall_macro": float(np.mean(recall_per_class)),
        "f1_macro": float(np.mean(f1_per_class))
    }


def main(file_path=FILE_PATH, out_dir=OUT_DIR):
    ensure_outdir(out_dir)
    print("Загрузка:", file_path)
    df = try_read_table(file_path)
    print("Размер:", df.shape)
    df.columns = [str(c) for c in df.columns]

    # Автопоиск целевой колонки или последней
    possible_targets = [c for c in df.columns if c.lower() in ('target','class','label','y','type')]
    if len(possible_targets) > 0:
        target_col = possible_targets[0]
    else:
        cand = None
        for c in (df.columns[0], df.columns[-1]):
            nunique = df[c].nunique(dropna=True)
            vals = df[c].dropna()
            if nunique <= 20 and (np.all(np.mod(vals.values, 1) == 0) if len(vals)>0 else True):
                cand = c
                break
        target_col = cand if cand is not None else df.columns[-1]

    print("Целевая колонка:", target_col)
    y_series = df[target_col].copy()
    X_df = df.drop(columns=[target_col])

    #  Импутация
    num_cols = X_df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = X_df.select_dtypes(exclude=[np.number]).columns.tolist()

    for c in num_cols:
        if X_df[c].isna().sum() > 0:
            X_df[c] = X_df[c].fillna(X_df[c].mean())

    for c in cat_cols:
        if X_df[c].isna().sum() > 0:
            X_df[c] = X_df[c].fillna(X_df[c].mode().iloc[0] if not X_df[c].mode().empty else "missing")

    #  Кодирование категорий
    if len(cat_cols) > 0:
        total_dummy = sum(X_df[c].nunique() for c in cat_cols)
        if total_dummy <= 50:
            X_df = pd.get_dummies(X_df, columns=cat_cols, drop_first=True)
        else:
            for c in cat_cols:
                X_df[c] = X_df[c].astype('category').cat.codes

    #  Цель в числа (если нужно)
    if y_series.dtype == object or not np.issubdtype(y_series.dtype, np.number):
        y_cat = y_series.astype('category')
        y = y_cat.cat.codes.values
        class_mapping = dict(enumerate(y_cat.cat.categories))
    else:
        y = y_series.values
        class_mapping = None

    #  Стандартизация
    X = X_df.copy()
    X_values = X.values.astype(float)
    means = np.nanmean(X_values, axis=0)
    stds = np.nanstd(X_values, axis=0, ddof=0)
    stds_fixed = np.where(stds == 0, 1.0, stds)
    X_scaled = (X_values - means) / stds_fixed

    #  Статистика
    stats_df = summarize_features(X_df)
    stats_csv = os.path.join(out_dir, "features_stats.csv")
    stats_df.to_csv(stats_csv)
    print("Статистика сохранена:", stats_csv)

    #  3D график (первые 3 признака)
    feature_names = X_df.columns.tolist()
    if len(feature_names) >= 3:
        f1, f2, f3 = feature_names[0], feature_names[1], feature_names[2]
        fig = plt.figure(figsize=(8,6))
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(X_scaled[:,0], X_scaled[:,1], X_scaled[:,2], s=30, alpha=0.9)
        ax.set_xlabel(f1); ax.set_ylabel(f2); ax.set_zlabel(f3)
        ax.set_title("3D (стандартизовано)")
        plt.tight_layout()
        out3d = os.path.join(out_dir, "3d_plot.png")
        plt.savefig(out3d); plt.close()
        print("3D-рисунок:", out3d)
    else:
        print("Меньше 3 признаков — 3D пропущен.")

    #  Разбиение train/test (стратиф.)
    rng = np.random.default_rng(RANDOM_SEED)
    unique_classes, counts = np.unique(y, return_counts=True)
    train_idx = []; test_idx = []
    for cls in unique_classes:
        idxs = np.where(y==cls)[0].tolist()
        rng.shuffle(idxs)
        n_test = max(1, int(len(idxs) * TEST_SIZE))
        test_idx.extend(idxs[:n_test])
        train_idx.extend(idxs[n_test:])
    train_idx = np.array(train_idx, dtype=int)
    test_idx = np.array(test_idx, dtype=int)
    print("Train:", len(train_idx), "Test:", len(test_idx))

    X_train = X_scaled[train_idx]; X_test = X_scaled[test_idx]
    y_train = y[train_idx]; y_test = y[test_idx]

    #  Выбор признаков: случайные и фиксированные (первые)
    n_total_features = X_df.shape[1]
    k_feat = min(N_FEATURES_TO_USE, n_total_features)
    rng2 = np.random.default_rng(RANDOM_SEED + 1)
    rand_idx = rng2.choice(n_total_features, size=k_feat, replace=False).tolist()
    model1_features = [feature_names[i] for i in rand_idx]
    model2_features = feature_names[:k_feat]

    print("Model1 (рандом):", model1_features)
    print("Model2 (фикс.):", model2_features)

    X_train_df = pd.DataFrame(X_train, columns=feature_names)
    X_test_df = pd.DataFrame(X_test, columns=feature_names)

    X1_train = X_train_df[model1_features].values
    X1_test  = X_test_df[model1_features].values
    X2_train = X_train_df[model2_features].values
    X2_test  = X_test_df[model2_features].values

    #  Оценка по разным k
    results = []
    for model_name, Xtr, Xte in [("Model1_random", X1_train, X1_test), ("Model2_fixed", X2_train, X2_test)]:
        for k in KS:
            kk = min(k, len(Xtr))
            y_pred = knn_predict(Xtr, y_train, Xte, k=kk)
            cm, labels = confusion_matrix(y_test, y_pred)
            metrics = compute_metrics_from_cm(cm)
            results.append({
                "model": model_name,
                "k": kk,
                "accuracy": metrics["accuracy"],
                "precision_macro": metrics["precision_macro"],
                "recall_macro": metrics["recall_macro"],
                "f1_macro": metrics["f1_macro"],
                "confusion": cm,
                "labels": labels
            })
            # сохранить матрицу ошибок как картинку
            fig, ax = plt.subplots(figsize=(4,4))
            ax.imshow(cm, interpolation='nearest')
            ax.set_title(f"{model_name} — k={kk}")
            ax.set_xlabel("Predicted"); ax.set_ylabel("True")
            ax.set_xticks(np.arange(len(labels))); ax.set_yticks(np.arange(len(labels)))
            ax.set_xticklabels([str(l) for l in labels], rotation=45)
            ax.set_yticklabels([str(l) for l in labels])
            for i in range(cm.shape[0]):
                for j in range(cm.shape[1]):
                    ax.text(j, i, str(cm[i,j]), ha="center", va="center")
            plt.tight_layout()
            fname = os.path.join(out_dir, f"confusion_{model_name}_k{kk}.png")
            plt.savefig(fname); plt.close()

    #  Сохранение сводки
    summary_rows = []
    for r in results:
        summary_rows.append({
            "model": r["model"],
            "k": r["k"],
            "accuracy": r["accuracy"],
            "precision_macro": r["precision_macro"],
            "recall_macro": r["recall_macro"],
            "f1_macro": r["f1_macro"]
        })
    res_df = pd.DataFrame(summary_rows)
    out_csv = os.path.join(out_dir, "knn_results_summary.csv")
    res_df.to_csv(out_csv, index=False)
    print("Сводка сохранена:", out_csv)
    print(res_df)

    #  Mapping классов (если был)
    if class_mapping is not None:
        mapping_path = os.path.join(out_dir, "class_mapping.txt")
        with open(mapping_path, "w", encoding="utf-8") as f:
            for k, v in class_mapping.items():
                f.write(f"{k} -> {v}\n")
        print("Mapping сохранён:", mapping_path)

    #  Лучший k по accuracy для каждой модели
    bests = res_df.loc[res_df.groupby("model")["accuracy"].idxmax()].reset_index(drop=True)
    print("\nЛучшее k (по accuracy) для каждой модели:")
    print(bests)

if __name__ == "__main__":
    main()
