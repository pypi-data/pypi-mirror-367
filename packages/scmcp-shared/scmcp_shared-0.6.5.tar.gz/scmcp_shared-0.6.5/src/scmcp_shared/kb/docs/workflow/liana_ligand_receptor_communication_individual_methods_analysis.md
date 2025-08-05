## Workflow 1: Individual Ligand-Receptor Analysis Methods

### Overview
This workflow focuses on using individual statistical methods to infer ligand-receptor interactions from single-cell transcriptomics data. Each method applies different assumptions and scoring functions to identify relevant cell-cell communication events between different cell types. This workflow is applicable to any single-cell RNA-seq dataset with annotated cell types and can be used to study intercellular communication in various biological contexts including development, disease, and tissue homeostasis.

### Standard Steps
1. **Data Input**: 
   - Single-cell transcriptomics data in AnnData format
   - Processed data with normalized counts (preferably log1p-transformed)
   - Cell type annotations stored in `adata.obs`
   - Raw counts accessible via `adata.raw.X` or specified layer

2. **External Resources**:
   - Ligand-receptor interaction databases (default: 'consensus' resource from OmniPath)
   - Species-specific resources available ('mouseconsensus' for mouse)
   - Custom resources can be provided as DataFrames

3. **Preprocessing**:
   - Data quality assessment and filtering
   - Expression proportion filtering (default: 10% of cells per cell type)
   - Minimum cell count filtering per cell type
   - Log-transformation verification (assumes natural log-normalized counts)

4. **Core Analysis**:
   - Method selection from available algorithms: CellPhoneDB, Connectome, log2FC, NATMI, SingleCellSignalR, CellChat, Geometric Mean, scSeqComm
   - Parameter configuration including expression proportion thresholds, permutation counts, and resource selection
   - Statistical computation of magnitude and specificity scores for each ligand-receptor pair
   - Cell type pair-wise interaction analysis

5. **Result Storage**:
   - Results stored in `adata.uns[method_name]` as DataFrame
   - Columns include: ligand, receptor, source, target, magnitude scores, specificity scores, expression statistics
   - Complex interactions handled with minimum subunit expression approach

6. **Visualization**:
   - Dot plots for interaction overview (color by magnitude, size by specificity)
   - Tile plots for detailed ligand/receptor expression statistics
   - Filtering capabilities based on statistical thresholds

### Technical Details
- **Key Functions**: 
  - `cellphonedb()`, `connectome()`, `logfc()`, `natmi()`, `singlecellsignalr()`, `cellchat()`, `geometric_mean()`
  - `li.mt.show_methods()` for method overview
  - `method.describe()` for method-specific information

- **Data Object Changes**:
  - Input: AnnData object with `.obs` containing cell type annotations
  - Processing: Creates temporary aggregated statistics per cell type
  - Output: Adds results to `adata.uns` as new key (e.g., 'cpdb_res')
  - No modification to main data matrices or metadata

- **Data Object Management**:
  - Single AnnData object used throughout
  - Results stored as separate DataFrames in `.uns` attribute
  - Multiple method runs create separate entries in `.uns`

- **Result Location**: 
  - `adata.uns['method_key']` contains DataFrame with results
  - Standard columns: 'ligand', 'receptor', 'source', 'target', method-specific scores
  - Additional columns: expression proportions, means, complex information

- **Data Flow Tracking**:
  - Raw expression matrix → cell-type aggregated statistics → ligand-receptor scoring → result DataFrame
  - Intermediate statistics calculated per cell type for each gene
  - Final results filtered by expression proportion and statistical thresholds

### Generality Assessment
- **Dependency Conditions**:
  - Species: Default uses human gene symbols, requires homology conversion for other species
  - Database: Depends on ligand-receptor resource structure (consensus, mouseconsensus, or custom)
  - Tools: Requires liana, scanpy, and associated scientific Python packages

- **Extensibility**:
  - Data Replacement: Compatible with any single-cell RNA-seq dataset with cell type annotations
  - Sample Types: Applicable to tissues, cell cultures, developmental time series, disease samples
  - Parameter Adjustment: Expression proportion (0-1), permutation count, statistical thresholds

- **Applicable Scenarios**:
  - Data Scale: Suitable for datasets ranging from hundreds to millions of cells
  - Research Purpose: Cell-cell communication, signaling pathway analysis, disease mechanism studies
  - Technical Platform: Compatible with data from 10x Genomics, Smart-seq2, Drop-seq, and other scRNA-seq platforms

### CODE EXAMPLE
```python
# Import required packages
import liana as li
import scanpy as sc
from liana.method import cellphonedb, connectome, natmi, logfc

# Load single-cell data
adata = sc.datasets.pbmc68k_reduced()

# Run CellPhoneDB method
cellphonedb(adata,
            groupby='bulk_labels',  # Cell type annotation column
            resource_name='consensus',  # Ligand-receptor database
            expr_prop=0.1,  # Minimum expression proportion (10%)
            verbose=True, 
            key_added='cpdb_res')  # Results storage key

# View results
results_df = adata.uns['cpdb_res']
print(f"Found {len(results_df)} ligand-receptor interactions")
print(f"Columns: {list(results_df.columns)}")

# Filter significant interactions (p-value <= 0.05)
significant_interactions = results_df[results_df['cellphone_pvals'] <= 0.05]
print(f"Significant interactions: {len(significant_interactions)}")

# Visualize top interactions
li.pl.dotplot(adata=adata,
              colour='lr_means',  # Magnitude score
              size='cellphone_pvals',  # Specificity score
              inverse_size=True,  # Smaller p-values = larger dots
              source_labels=['CD14+ Monocyte', 'Dendritic'],
              target_labels=['CD4+/CD45RO+ Memory', 'CD8+ Cytotoxic T'],
              filter_fun=lambda x: x['cellphone_pvals'] <= 0.05,
              uns_key='cpdb_res',
              figure_size=(10, 8))
```

### Key Parameters and Their Biological Significance
- **expr_prop**: Controls false positive rate by requiring sufficient expression in cell populations
- **resource_name**: Determines which ligand-receptor interactions are tested (biological prior knowledge)
- **groupby**: Specifies cell type annotations for interaction analysis
- **n_perms**: Number of permutations for statistical testing (affects specificity score reliability)
- **use_raw**: Whether to use raw counts or normalized data (affects expression magnitude calculations)