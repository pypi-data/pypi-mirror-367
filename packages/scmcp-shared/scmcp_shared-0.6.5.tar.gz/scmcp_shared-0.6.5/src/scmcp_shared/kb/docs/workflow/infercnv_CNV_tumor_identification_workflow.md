## Workflow 1: Inferring Copy Number Variations (CNV) and Identifying Tumor Cells from scRNA-seq Data

### Overview
This workflow outlines the process of inferring large-scale chromosomal copy number variations (CNVs) from single-cell RNA-seq (scRNA-seq) data. The core idea is to identify genomic regions with consistently higher or lower gene expression in a subset of cells compared to a reference set of normal cells. This allows for the identification of potential tumor cells characterized by aneuploidy. The workflow proceeds by calculating a CNV profile for each cell, clustering cells based on these profiles, and then classifying cells as "tumor" or "normal" based on their CNV characteristics.

### Standard Steps
1.  **Data Input**:
    *   **Data Source**: An `AnnData` object containing single-cell gene expression data.
    *   **Data Format**: The object should have a counts matrix (`adata.X` or a layer) and cell metadata (`adata.obs`).
    *   **Data Structure Check**:
        *   `adata.var` must contain gene annotation information, specifically the chromosome, start, and end positions for each gene (e.g., `adata.var['chromosome']`, `adata.var['start']`, `adata.var['end']`).
        *   `adata.obs` must have a column identifying cell types or a reference group annotation (e.g., `adata.obs['cell_type']`).

2.  **External Resources**:
    *   **Database Calls**: No direct database calls are made during the analysis.
    *   **Reference Data**: A pre-defined set of reference (normal) cells is required. These are identified via a categorical annotation in `adata.obs`.
    *   **Tool Dependencies**: `infercnvpy`, `scanpy`, `leidenalg`.

3.  **Core Analysis**:
    *   **CNV Inference**: Use `infercnvpy.tl.infercnv()` to calculate the CNV matrix. This involves averaging gene expression over a sliding window along each chromosome and comparing it to the average of the reference cells.
    *   **CNV-based Clustering**:
        *   Perform dimensionality reduction on the resulting CNV matrix (`infercnvpy.tl.pca`).
        *   Construct a neighborhood graph on the reduced dimensions (`infercnvpy.pp.neighbors`).
        *   Cluster the cells using the Leiden algorithm (`infercnvpy.tl.leiden`).
    *   **CNV Score Calculation**: Compute a summary score for the magnitude of CNV events per cell (`infercnvpy.tl.cnv_score`).

4.  **Result Storage**:
    *   **Data Structure Updates**: The results of each step are added back to the original `AnnData` object.
    *   **Result Location**:
        *   CNV matrix: `adata.obsm['X_cnv']`
        *   PCA on CNV matrix: `adata.obsm['X_cnv_pca']`, `adata.varm['cnv_pca']`
        *   Neighborhood graph: `adata.uns['cnv_neighbors']`
        *   Leiden cluster labels: `adata.obs['cnv_leiden']`
        *   UMAP on CNV matrix: `adata.obsm['X_cnv_umap']`
        *   CNV score: `adata.obs['cnv_score']`
        *   Tumor/Normal status: Manually created column, e.g., `adata.obs['cnv_status']`

5.  **Visualization**:
    *   **Chromosome Heatmap**: `infercnvpy.pl.chromosome_heatmap` visualizes gene expression smoothed across genomic coordinates, grouped by cell annotations. This is the primary tool for observing large-scale CNV patterns.
    *   **UMAP**:
        *   `infercnvpy.pl.umap`: Visualizes the UMAP embedding calculated from the CNV profiles.
        *   `scanpy.pl.umap`: Visualizes the original transcriptomic UMAP, but colored by CNV results (leiden clusters, score, status). This helps relate CNV identity back to the original cell states.

### Technical Details
-   **Key Functions**:
    *   `cnv.tl.infercnv()`: The core function for CNV inference.
    *   `cnv.tl.pca()`, `cnv.pp.neighbors()`, `cnv.tl.leiden()`: Standard functions for dimensionality reduction and clustering, adapted for CNV profiles.
    *   `cnv.tl.umap()`: Computes a UMAP embedding based on the CNV data.
    *   `cnv.tl.cnv_score()`: Calculates a per-cell CNV score.
    *   `cnv.pl.chromosome_heatmap()`: The main visualization tool for inspecting CNV patterns across chromosomes.
    *   `cnv.pl.umap()`: Visualizes the CNV-based UMAP.

-   **Data Object Changes**:
    *   `cnv.tl.infercnv()`: Adds `adata.obsm['X_cnv']` and `adata.uns['cnv']`.
    *   `cnv.tl.pca()`: Adds `adata.obsm['X_cnv_pca']` and `adata.varm['cnv_pca']`.
    *   `cnv.pp.neighbors()`: Adds `adata.uns['cnv_neighbors']`.
    *   `cnv.tl.leiden()`: Adds `adata.obs['cnv_leiden']` (categorical).
    *   `cnv.tl.umap()`: Adds `adata.obsm['X_cnv_umap']`.
    *   `cnv.tl.cnv_score()`: Adds `adata.obs['cnv_score']` (float).
    *   Manual classification: Adds a user-defined column like `adata.obs['cnv_status']`.

-   **Data Object Management**:
    *   A single `AnnData` object is used and progressively updated throughout the entire workflow. No new objects are created, and no switching occurs. Subsetting is used for final visualizations (e.g., plotting heatmaps for only tumor or normal cells).

-   **Result Location**:
    *   All numerical results (CNV matrix, PCA, UMAP) are stored in `adata.obsm`.
    *   All per-cell categorical or continuous results (cluster labels, scores, status) are stored in `adata.obs`.
    *   Algorithm parameters and other metadata are stored in `adata.uns`.

-   **Data Flow Tracking**:
    `AnnData` -> `cnv.tl.infercnv()` -> `adata.obsm['X_cnv']` -> `cnv.tl.pca()` -> `adata.obsm['X_cnv_pca']` -> `cnv.pp.neighbors()` -> `adata.uns['cnv_neighbors']` -> `cnv.tl.leiden()` -> `adata.obs['cnv_leiden']` -> Visualizations & Manual Annotation -> Final classified `AnnData` object.

### Generality Assessment
-   **Dependency Conditions**:
    *   **Species Specificity**: The workflow is dependent on having correct gene annotations for the species of interest, specifically the chromosomal location (`chromosome`, `start`, `end`). It is otherwise species-agnostic.
    *   **Reference Requirement**: A key dependency is the ability to define a reliable set of "normal" reference cells that are assumed to be diploid. The quality of the result is highly dependent on the quality of this reference.

-   **Extensibility**:
    *   **Data Replacement**: The workflow can be applied to any scRNA-seq dataset, provided the gene annotations and a reference cell population are available.
    *   **Parameter Adjustment**:
        *   `window_size` in `cnv.tl.infercnv()`: This key parameter controls the degree of smoothing. A smaller window gives higher resolution but may be noisier; a larger window gives smoother profiles but may obscure smaller CNV events.
        *   Clustering resolution in `cnv.tl.leiden()`: Can be adjusted to yield more or fewer CNV-based clusters.

-   **Applicable Scenarios**:
    *   **Research Purpose**: Identifying tumor cells and subclones from mixed-population single-cell datasets, such as tumor microenvironments. Studying intratumor heterogeneity from a genomic perspective.
    *   **Technical Platform**: Applicable to most gene-expression-based single-cell platforms (e.g., 10x Genomics), but is not suitable for single-cell ATAC-seq or other modalities. It works best on full-length transcript data but is commonly applied to 3' or 5' tagged data as well.

### CODE EXAMPLE
```python
import scanpy as sc
import infercnvpy as cnv

# 1. Data Input: Load AnnData object.
# The object must contain gene locations in .var and cell type annotations in .obs
adata = cnv.datasets.maynard2020_3k()

# 2. Core Analysis: Infer CNVs
# A reference cell type or set of types must be specified.
cnv.tl.infercnv(
    adata,
    reference_key="cell_type",
    reference_cat=[
        "B cell", "Macrophage", "Mast cell", "Monocyte", "NK cell", 
        "Plasma cell", "T cell CD4", "T cell CD8", "T cell regulatory", 
        "mDC", "pDC",
    ],
    window_size=250, # Key parameter for smoothing
)
# Result is stored in adata.obsm['X_cnv']

# 3. Visualization: Plot heatmap to inspect results
# This visualization confirms that epithelial cells show CNV patterns while immune cells do not.
cnv.pl.chromosome_heatmap(adata, groupby="cell_type")

# 4. Core Analysis: Cluster cells based on CNV profile
cnv.tl.pca(adata) # PCA on adata.obsm['X_cnv'] -> adata.obsm['X_cnv_pca']
cnv.pp.neighbors(adata) # Builds graph on CNV PCA -> adata.uns['cnv_neighbors']
cnv.tl.leiden(adata) # Clusters graph -> adata.obs['cnv_leiden']
cnv.tl.umap(adata) # UMAP on CNV PCA -> adata.obsm['X_cnv_umap']
cnv.tl.cnv_score(adata) # Calculate CNV score -> adata.obs['cnv_score']

# 5. Visualization: UMAP of CNV profiles
# Used to identify clusters with distinct CNV profiles, which are candidate tumor clusters.
cnv.pl.umap(
    adata,
    color=["cnv_leiden", "cnv_score", "cell_type"],
    legend_loc="on data",
)

# 6. Result Interpretation: Classify tumor cells
# Based on visualizations, manually define which cnv_leiden clusters are tumors.
# This adds a new column to adata.obs.
adata.obs["cnv_status"] = "normal"
adata.obs.loc[adata.obs["cnv_leiden"].isin(["10", "16", "13"]), "cnv_status"] = "tumor"

# 7. Final Visualization: Confirm classification
# Plot heatmaps for the classified tumor and normal cells separately.
cnv.pl.chromosome_heatmap(adata[adata.obs["cnv_status"] == "tumor", :])
cnv.pl.chromosome_heatmap(adata[adata.obs["cnv_status"] == "normal", :])

```