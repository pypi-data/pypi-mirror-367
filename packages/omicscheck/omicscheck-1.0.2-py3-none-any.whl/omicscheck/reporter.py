from fpdf import FPDF
from pathlib import Path
from datetime import datetime
import json
import csv
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import numpy as np

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "OmicsCheck Report", ln=True, align="C")
        self.set_font("Arial", "", 12)
        self.cell(0, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
        self.ln(10)

    def section_title(self, title):
        self.set_font("Arial", "B", 14)
        self.set_text_color(0, 51, 102)
        self.cell(0, 10, title, ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(5)

    def add_key_value(self, key, value):
        self.set_font("Arial", "", 12)
        self.cell(50, 10, f"{key}:", ln=False)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, str(value), ln=True)

def convert_types(obj):
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    return obj

def generate_pdf_report(gse_id: str, analysis: dict, output_dir: Path, orientation_note: str = "", log2_note: str = "", qa_result: dict = None):
    pdf = PDF()
    pdf.add_page()

    pdf.section_title(f"GEO Series ID: {gse_id}")
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, f"This report summarizes the gene expression matrix and visual analyses performed for GEO dataset {gse_id} using OmicsCheck.")

    if orientation_note:
        pdf.section_title("Orientation Note")
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, orientation_note)

    if log2_note:
        pdf.section_title("Log2 Transformation Suggestion")
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, log2_note)

    pdf.section_title("Summary Statistics")
    for key, value in analysis.items():
        pdf.add_key_value(key.replace('_', ' ').capitalize(), value)

    if qa_result:
        pdf.section_title("Study Quality Evaluation")
        for key, value in qa_result.items():
            pdf.add_key_value(key, value)

    report_path = output_dir / "report.pdf"
    pdf.output(str(report_path))

def export_analysis_files(output_dir: Path, analysis: dict, qa_result: dict):
    combined = {**analysis, **qa_result}
    combined = {k: convert_types(v) for k, v in combined.items()}

    json_path = output_dir / "analysis.json"
    with open(json_path, "w") as f_json:
        json.dump(combined, f_json, indent=4)

    csv_path = output_dir / "analysis.csv"
    with open(csv_path, "w", newline='') as f_csv:
        writer = csv.writer(f_csv)
        writer.writerow(["Metric", "Value"])
        for key, value in combined.items():
            writer.writerow([key, value])

def plot_pca(df: pd.DataFrame, output_dir: Path):
    """
    Generate and save a 3D PCA scatter plot from gene expression matrix.
    """
    if df.shape[1] < 3:
        print("⚠️ Skipping PCA: not enough samples for 3D.")
        return

    # Clean and normalize the data
    df_clean = df.dropna(axis=1, how='any')
    scaled_data = StandardScaler().fit_transform(df_clean.T)

    # Apply 3D PCA
    pca = PCA(n_components=3)
    pca_result = pca.fit_transform(scaled_data)

    # Create the 3D plot
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    ax.scatter(
        pca_result[:, 0], pca_result[:, 1], pca_result[:, 2],
        c='steelblue', s=60, edgecolor='black'
    )

    ax.set_title("3D PCA Plot of Samples", fontsize=14)
    ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)", fontsize=12)
    ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)", fontsize=12)
    ax.set_zlabel(f"PC3 ({pca.explained_variance_ratio_[2]*100:.1f}%)", fontsize=12)

    plt.tight_layout()
    plt.savefig(output_dir / "pca_plot_3d.png", dpi=300)
    plt.close()
