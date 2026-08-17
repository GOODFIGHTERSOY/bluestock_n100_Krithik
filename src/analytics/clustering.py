# src/analytics/clustering.py

import os
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


# ============================================================
# PATHS
# ============================================================

INPUT_FILE = "output/financial_ratios.csv"

OUTPUT_DIR = "output"

CLUSTERED_FILE = os.path.join(
    OUTPUT_DIR,
    "clustered_companies.csv"
)

ELBOW_FILE = os.path.join(
    OUTPUT_DIR,
    "kmeans_elbow_plot.png"
)

CORRELATION_FILE = os.path.join(
    OUTPUT_DIR,
    "correlation_heatmap.png"
)


# ============================================================
# FEATURES
# ============================================================

FEATURES = [
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "return_on_equity_pct",
    "roce_calculated",
    "debt_to_equity",
    "interest_coverage",
    "asset_turnover",
    "free_cash_flow",
    "cfo_quality_score",
    "capex_intensity",
    "fcf_conversion",
]


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    df = pd.read_csv(
        INPUT_FILE
    )

    print(
        f"Loaded {len(df)} financial records."
    )

    return df


# ============================================================
# PREPARE LATEST COMPANY DATA
# ============================================================

def prepare_latest_data(df):

    # Make sure year is numeric

    if "year" in df.columns:

        df["year"] = pd.to_numeric(
            df["year"],
            errors="coerce"
        )

        # Keep the latest financial record
        # for each company.

        df = (
            df
            .sort_values("year")
            .drop_duplicates(
                "company_id",
                keep="last"
            )
        )

    return df.reset_index(
        drop=True
    )


# ============================================================
# PREPARE FEATURES
# ============================================================

def prepare_features(df):

    available_features = [
        column
        for column in FEATURES
        if column in df.columns
    ]

    missing_features = [
        column
        for column in FEATURES
        if column not in df.columns
    ]

    print()
    print("Features used:")

    for feature in available_features:
        print(f"  ✓ {feature}")

    if missing_features:

        print()
        print("Missing features:")

        for feature in missing_features:
            print(f"  - {feature}")

    if len(available_features) < 2:

        raise ValueError(
            "Not enough clustering features "
            "are available."
        )

    # Convert features to numeric

    X = df[
        available_features
    ].apply(
        pd.to_numeric,
        errors="coerce"
    )

    # Replace infinite values

    X = X.replace(
        [float("inf"), float("-inf")],
        pd.NA
    )

    # Median imputation

    X = X.fillna(
        X.median()
    )

    # Any columns that are still completely empty

    X = X.fillna(0)

    return X, available_features


# ============================================================
# STANDARD SCALER
# ============================================================

def scale_features(X):

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(
        X
    )

    return X_scaled, scaler


# ============================================================
# ELBOW METHOD
# ============================================================

def generate_elbow_plot(
    X_scaled,
    max_k=10
):

    print()
    print("Generating elbow plot...")

    inertias = []

    k_values = range(
        2,
        max_k + 1
    )

    for k in k_values:

        model = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=10
        )

        model.fit(
            X_scaled
        )

        inertias.append(
            model.inertia_
        )

    plt.figure(
        figsize=(9, 6)
    )

    plt.plot(
        list(k_values),
        inertias,
        marker="o"
    )

    plt.xlabel(
        "Number of Clusters (K)"
    )

    plt.ylabel(
        "Within-Cluster Sum of Squares"
    )

    plt.title(
        "KMeans Elbow Method"
    )

    plt.xticks(
        list(k_values)
    )

    plt.grid(
        alpha=0.3
    )

    plt.tight_layout()

    plt.savefig(
        ELBOW_FILE,
        dpi=200
    )

    plt.close()

    print(
        f"Elbow plot saved: {ELBOW_FILE}"
    )


# ============================================================
# KMEANS
# ============================================================

def run_kmeans(
    X_scaled,
    n_clusters=5
):

    print()
    print(
        f"Running KMeans with "
        f"{n_clusters} clusters..."
    )

    model = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init=10
    )

    labels = model.fit_predict(
        X_scaled
    )

    return model, labels


# ============================================================
# CORRELATION HEATMAP
# ============================================================

def generate_correlation_heatmap(
    X,
    feature_names
):

    print()
    print(
        "Generating correlation heatmap..."
    )

    correlation = X[
        feature_names
    ].corr()

    plt.figure(
        figsize=(12, 9)
    )

    plt.imshow(
        correlation,
        aspect="auto"
    )

    plt.colorbar(
        label="Correlation"
    )

    plt.xticks(
        range(
            len(feature_names)
        ),
        feature_names,
        rotation=75,
        ha="right"
    )

    plt.yticks(
        range(
            len(feature_names)
        ),
        feature_names
    )

    plt.title(
        "Financial Feature Correlation Matrix"
    )

    plt.tight_layout()

    plt.savefig(
        CORRELATION_FILE,
        dpi=200,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Correlation heatmap saved: "
        f"{CORRELATION_FILE}"
    )


# ============================================================
# CLUSTER SUMMARY
# ============================================================

def generate_cluster_summary(
    df,
    feature_names
):

    print()
    print(
        "Cluster Summary"
    )

    summary = (
        df
        .groupby("cluster_label")[
            feature_names
        ]
        .mean()
        .round(2)
    )

    summary_file = os.path.join(
        OUTPUT_DIR,
        "cluster_summary.csv"
    )

    summary.to_csv(
        summary_file
    )

    print(summary)

    print()
    print(
        f"Cluster summary saved: "
        f"{summary_file}"
    )

    return summary


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_clustering():

    print("=" * 70)
    print(
        "Bluestock N100 KMeans Clustering"
    )
    print("=" * 70)

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    df = load_data()

    # --------------------------------------------------------
    # Latest company record
    # --------------------------------------------------------

    df = prepare_latest_data(
        df
    )

    print(
        f"Companies available for clustering: "
        f"{len(df)}"
    )

    # --------------------------------------------------------
    # Features
    # --------------------------------------------------------

    X, feature_names = prepare_features(
        df
    )

    # --------------------------------------------------------
    # Correlation matrix
    # --------------------------------------------------------

    generate_correlation_heatmap(
        X,
        feature_names
    )

    # --------------------------------------------------------
    # Scale
    # --------------------------------------------------------

    X_scaled, scaler = scale_features(
        X
    )

    print(
        "Features standardized using "
        "StandardScaler."
    )

    # --------------------------------------------------------
    # Elbow
    # --------------------------------------------------------

    generate_elbow_plot(
        X_scaled
    )

    # --------------------------------------------------------
    # KMeans
    # --------------------------------------------------------

    model, labels = run_kmeans(
        X_scaled,
        n_clusters=5
    )

    # --------------------------------------------------------
    # Assign labels
    # --------------------------------------------------------

    df["cluster_label"] = labels

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    df.to_csv(
        CLUSTERED_FILE,
        index=False
    )

    print()
    print(
        f"Clustered data saved: "
        f"{CLUSTERED_FILE}"
    )

    # --------------------------------------------------------
    # Cluster counts
    # --------------------------------------------------------

    print()
    print(
        "Cluster distribution:"
    )

    print(
        df[
            "cluster_label"
        ]
        .value_counts()
        .sort_index()
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    generate_cluster_summary(
        df,
        feature_names
    )

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "D36-D37 clustering completed successfully"
    )
    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    run_clustering()