## Workflow 3: Pathway Activity Scoring

### Overview
This workflow describes how to estimate the activity of biological pathways from single-cell RNA-seq data. Similar to TF activity scoring, this method uses enrichment analysis on predefined gene sets that represent specific pathways. This allows for a higher-level biological interpretation of the data, revealing which cellular processes are active in different cell populations.

### Standard Steps
1.  **Data Input**
    -   **Data Source**: An `AnnData` object from local memory.
    -   **Data Format**: A log-normalized gene expression matrix (cells x genes) in `.X`.
    -   **Data Structure Check**: Cell type annotations (e.g., `adata.obs['celltype']`) are required for comparative analysis.

2.  **External Resources**
    -   **Database Calls**: Uses `decoupler` to access various pathway gene set databases. The tutorial provides two examples:
        1.  **PROGENy**: A collection of 14 core signaling pathways with weighted target genes.
        2.  **Hallmark (MSigDB)**: A set of 50 curated, non-redundant gene sets representing major biological processes.
    -   **Reference Data**: A list of pathway-gene interactions, which can be weighted (like PROGENy) or unweighted (like Hallmark).

3.  **Preprocessing**
    -   The pathway gene sets are loaded directly using `decoupler` helper functions (`dc.op.progeny`, `dc.op.hallmark`). The data is already in the required format.

4.  **Core Analysis**
    -   **Method Name**: Pathway activities are calculated using the `decoupler.mt.ulm` function (univariate linear model).
    -   **Comparison Logic**: For gene sets with many features (like Hallmark), `decoupler.tl.rankby_group` can be used to identify the most significantly active pathways ("marker pathways") for each cell type. For smaller, curated sets like PROGENy, direct visualization is often sufficient.

5.  **Result Storage**
    -   **Data Structure Updates**: The main `AnnData` object is updated in place.
    -   **Result Location**: Pathway activity scores are stored in `adata.obsm['score_ulm']`, overwriting any previous results in that key.
    -   **Output Format**: `rankby_group` produces a pandas DataFrame of ranked pathways per cell type.

6.  **Visualization**
    -   **Chart Types**: UMAPs, violin plots, and matrix plots (heatmaps).
    -   **Visualization Tools**: `scanpy.pl.umap`, `scanpy.pl.violin`, `scanpy.pl.matrixplot`.
    -   **Presentation Purpose**:
        -   **UMAP/Violin Plot**: To visualize the activity of a specific pathway across cell types.
        -   **Matrix Plot**: To provide a comprehensive overview of all pathway activities (for small sets like PROGENy) or marker pathways (for large sets like Hallmark) across all cell types.

### Technical Details
-   **Key Functions**:
    -   `decoupler.op.progeny()` / `decoupler.op.hallmark()`: Fetch pathway gene sets.
    -   `decoupler.mt.ulm()`: Runs the pathway activity scoring.
    -   `decoupler.pp.get_obsm()`: Extracts scores into a new `AnnData` object for plotting.
    -   `decoupler.tl.rankby_group()`: Identifies marker pathways.

-   **Data Object Changes**:
    1.  **Initial State**: `adata` with expression data and cell type labels.
    2.  **After `dc.mt.ulm`**: `adata.obsm` is populated with `'score_ulm'` (DataFrame: cells x pathways). **Note**: This is an in-place operation that overwrites existing data in `adata.obsm['score_ulm']`. Each time a new enrichment analysis is run (e.g., first with PROGENy, then with Hallmark), the old results are replaced.
    3.  **For Visualization**: A new `AnnData` object (`score`) is created to isolate the scores for plotting.

-   **Data Object Management**: This workflow highlights the importance of managing the `adata.obsm['score_ulm']` slot. Since it's overwritten with each new analysis, results that need to be preserved should be saved to a different key or variable before running the next analysis.

-   **Result Location**:
    -   Pathway activity scores: `adata.obsm['score_ulm']`.
    -   Ranked marker pathways: A pandas DataFrame from `dc.tl.rankby_group()`.

-   **Data Flow Tracking**:
    `adata` (expression) + `pathway_geneset` (PROGENy or Hallmark) → `dc.mt.ulm` → `adata.obsm['score_ulm']` → `dc.pp.get_obsm` → `score` AnnData object → Visualization and/or ranking.

### Generality Assessment
-   **Dependency Conditions**: The interpretation depends on the chosen gene set collection and is specific to the organism for which the sets were defined (e.g., human).
-   **Extensibility**: Extremely high. Any gene set from MSigDB or other databases can be used. Users can also provide their own custom gene sets to investigate specific biological questions. The enrichment method is also interchangeable.
-   **Applicable Scenarios**: This workflow is broadly useful for gaining a systems-level understanding of single-cell data. It helps move from gene-level observations to insights about the biological processes that are active or dysregulated in different cell populations, making it valuable for studies in immunology, cancer biology, and developmental biology.

### CODE EXAMPLE
```python
# CODE EXAMPLE for Pathway Activity Scoring

import scanpy as sc
import decoupler as dc

# Load pre-processed AnnData object with expression and celltype labels
adata = dc.ds.pbmc3k()

# --- Workflow Example 1: PROGENy Pathways ---

# 1. External Resources
progeny_net = dc.op.progeny(organism="human")

# 2. Core Analysis
# Run ULM, results are stored in adata.obsm['score_ulm']
dc.mt.ulm(data=adata, net=progeny_net)

# 3. Result Handling & Visualization
# Extract scores into a new AnnData object for plotting
progeny_score = dc.pp.get_obsm(adata=adata, key="score_ulm")

# Visualize activity for a specific pathway
sc.pl.violin(progeny_score, keys=["Trail"], groupby="celltype", rotation=90)

# Visualize all 14 PROGENy pathways in a heatmap
sc.pl.matrixplot(
    adata=progeny_score,
    var_names=progeny_score.var_names,
    groupby="celltype",
    dendrogram=True,
    standard_scale="var",
    cmap="RdBu_r",
)


# --- Workflow Example 2: Hallmark Gene Sets ---

# 1. External Resources
hallmark_net = dc.op.hallmark(organism="human")

# 2. Core Analysis
# Run ULM, this will OVERWRITE the previous PROGENy scores in adata.obsm['score_ulm']
dc.mt.ulm(data=adata, net=hallmark_net)

# 3. Result Handling & Visualization
# Extract the new scores
hallmark_score = dc.pp.get_obsm(adata=adata, key="score_ulm")

# Identify marker gene sets for each cell type
ranked_df = dc.tl.rankby_group(adata=hallmark_score, groupby="celltype", method="t-test_overestim_var")
top_hallmarks = (
    ranked_df[ranked_df["stat"] > 0]
    .groupby("group")
    .head(3)
    .drop_duplicates("name")
    .groupby("group")["name"]
    .apply(list)
    .to_dict()
)

# Visualize marker pathways in a heatmap
sc.pl.matrixplot(
    adata=hallmark_score,
    var_names=top_hallmarks,
    groupby="celltype",
    dendrogram=True,
    standard_scale="var",
    cmap="RdBu_r",
)
```