import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler
import networkx as nx
import numpy as np


def plot_boxplot(df: pd.DataFrame, out_path: Path):
    """Generate and save a high-quality boxplot of gene expression values per sample."""
    if df.empty or df.shape[0] == 0 or df.shape[1] == 0:
        print("⚠️ Skipping boxplot: Dataframe is empty.")
        return

    plt.figure(figsize=(24, 12))
    sns.boxplot(
        data=df,
        orient='h',
        fliersize=1,
        linewidth=0.6,
        palette='Set3'
    )

    plt.xlabel("Expression Value", fontsize=16)
    plt.ylabel("Samples", fontsize=16)
    plt.xticks(fontsize=12)
    plt.yticks([], [])

    plt.title("Distribution of Expression Values Across Samples", fontsize=20, pad=20)
    plt.grid(True, axis='x', linestyle='--', linewidth=0.5)

    plt.tight_layout()
    plt.savefig(out_path / "boxplot.png", dpi=300)
    plt.close()
def plot_gene_expression_network(df, output_dir, top_n=50, corr_threshold=0.9):
    corr = df.T.corr()
    top_genes = corr.var().sort_values(ascending=False).head(top_n).index
    corr_subset = corr.loc[top_genes, top_genes]

    G = nx.Graph()

    for i, gene1 in enumerate(top_genes):
        for j, gene2 in enumerate(top_genes):
            if i < j and abs(corr_subset.loc[gene1, gene2]) >= corr_threshold:
                G.add_edge(gene1, gene2, weight=corr_subset.loc[gene1, gene2])

    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(14, 12))

    node_sizes = [500 + 5000 * G.degree(n) / max(dict(G.degree()).values()) for n in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color="indigo", alpha=0.8)
    nx.draw_networkx_edges(G, pos, alpha=0.3)
    nx.draw_networkx_labels(G, pos, font_size=8)

    plt.title("Gene Expression Similarity Network", fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_dir / "gene_network.png", dpi=300)
    plt.close()

