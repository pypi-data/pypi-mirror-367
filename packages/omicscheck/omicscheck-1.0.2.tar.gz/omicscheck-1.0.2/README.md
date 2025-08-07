
# OmicsCheck: Intelligent Quality Assessment for Gene Expression Data

**OmicsCheck** is a cutting-edge, automated tool designed to evaluate the quality of gene expression datasets from GEO (Gene Expression Omnibus). It intelligently analyzes raw expression matrices and generates professional PDF reports, visual summaries, and interpretable quality metrics – enabling researchers to screen studies before conducting downstream analysis.

---

##  Features

-  **Download and parse** GEO Series Matrix files automatically.
-  **Auto-orientation** of matrices (genes × samples vs. samples × genes).
-  **Log2 transformation suggestions** based on data distribution.
-  **Data filtering** for the most variable genes (top-N).
-  **QA Score Evaluation** using multi-criteria assessment.
-  **PCA and Heatmap visualization** of gene-level variability.
-  **PDF report generation** with visual plots and summary stats.
-  **Exports analysis files** in `.json` and `.csv` formats.

---

##  Installation

```bash
pip install omicscheck
```

> Requires Python 3.8+

---

##  Usage

```bash
omicscheck run GSE12345
```

This will:

1. Download the matrix file for `GSE12345`
2. Parse and analyze the data
3. Evaluate quality and suggest improvements
4. Generate visual plots
5. Create a full PDF report at: `~/Desktop/OmicsCheck/GSE12345/report.pdf`

---

##  Quality Evaluation Logic

OmicsCheck uses a composite QA Score based on:

- Matrix completeness
- Distribution characteristics
- Gene variance
- Sample PCA spread

Each dataset receives a final **Rating**: `Excellent`, `Good`, `Moderate`, or `Poor`

---

##  Output Files

- `report.pdf`: Professional scientific report
- `analysis.json`: Full results in machine-readable format
- `analysis.csv`: Simplified metrics table
- `boxplot.png`, `heatmap.png`, `pca_plot.png`: Generated plots

---

##  Example Output

Example report: `docs/report_example.pdf`

---

# OmicsCheck

A smart pre-download screening tool for high-quality omics datasets.

[![PyPI version](https://img.shields.io/pypi/v/OmicsCheck.svg)](https://pypi.org/project/OmicsCheck/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
[![DOI](https://img.shields.io/badge/DOI-10.21203/rs.3.rs--7297713--v1-blue)](https://doi.org/10.21203/rs.3.rs-7297713/v1)

---

##  Citation

> Ahmed Yassin. *OmicsCheck Enables Improved Selection of High-Quality Gene Expression Datasets: A Pre-download Screening Tool with Biological Impact Assessment*.  
> Research Square (2025).  
> [https://doi.org/10.21203/rs.3.rs-7297713/v1](https://doi.org/10.21203/rs.3.rs-7297713/v1)


---

##  Contributing

We welcome contributions! Fork the repo and submit a pull request.

---

##  Contact

Lead Developer: [AHMED YASSIN || Computational Biologist]  
Email: [Ahmedyassin300@outlook.com]  
Project Page: [https://github.com/AHMEDY3DGENOME/OmicsCheck]

---

© 2025 OmicsCheck Team. All rights reserved.