## Workflow 2: Ligand-Receptor Rank Aggregate Consensus Analysis

### Overview
This workflow implements a consensus approach that integrates predictions from multiple individual ligand-receptor analysis methods using Robust Rank Aggregation (RRA). By combining results from different algorithms, this approach provides more robust and reliable identification of cell-cell communication events. The workflow is particularly valuable for reducing method-specific biases and identifying high-confidence interactions that are consistently predicted across multiple statistical approaches.

### Standard Steps
1. **Data Input**:
   - Single-cell transcriptomics data in AnnData format
   - Processed data with normalized counts (log1p-transformed preferred)
   - Cell type annotations in `adata.obs`
   - Raw counts accessible via `adata.raw.X`

2. **External Resources**:
   - Comprehensive ligand-receptor interaction databases (default: 'consensus')
   - Species-specific resources available
   - Method-specific statistical frameworks and scoring functions

3. **Preprocessing**:
   - Expression proportion filtering (default: 10% minimum expression)
   - Minimum cell count filtering per cell type
   - Data normalization verification and scaling
   - Complex subunit handling (minimum expression approach)

4. **Core Analysis**:
   - Multi-method execution: CellPhoneDB, Connectome, log2FC, NATMI, SingleCellSignalR by default
   - Rank aggregation using RobustRankAggregate (RRA) algorithm
   - Separate aggregation for magnitude and specificity scores
   - Statistical integration across methods with beta distribution-based probability calculation
   - Bonferroni correction for multiple testing

5. **Result Storage**:
   - Results stored in `adata.uns['liana_res']` as comprehensive DataFrame
   - Contains all individual method scores plus aggregated ranks
   - Magnitude and specificity ranks representing consensus across methods
   - Interaction metadata and expression statistics

6. **Visualization**:
   - Consensus dot plots with aggregated rank scores
   - Circle plots for network-level interaction visualization
   - Filtered visualization based on rank thresholds
   - Customizable plot aesthetics with plotnine integration

### Technical Details
- **Key Functions**:
  - `li.mt.rank_aggregate()` - main consensus function
  - `li.mt.show_methods()` - displays available methods
  - `li.pl.dotplot()`, `li.pl.circle_plot()` - visualization functions
  - `li.mt.AggregateClass()` - custom consensus creation

- **Data Object Changes**:
  - Input: AnnData object with cell type annotations
  - Processing: Creates scaled layer and aggregated statistics
  - Output: Adds comprehensive results to `adata.uns['liana_res']`
  - Adds temporary layers: 'scaled' for normalization

- **Data Object Management**:
  - Single AnnData object used throughout analysis
  - Results stored in standardized location (`adata.uns['liana_res']`)
  - Custom consensus objects can be created for method subsets
  - Multiple consensus runs overwrite previous results by default

- **Result Location**:
  - `adata.uns['liana_res']` contains DataFrame with:
    - Standard columns: 'source', 'target', 'ligand_complex', 'receptor_complex'
    - Individual method scores: 'lr_means', 'cellphone_pvals', 'expr_prod', 'scaled_weight', 'lr_logfc', 'spec_weight', 'lrscore'
    - Consensus ranks: 'magnitude_rank', 'specificity_rank'

- **Data Flow Tracking**:
  - Raw data → individual method execution → score normalization → rank aggregation → consensus calculation
  - Each method generates magnitude and specificity scores independently
  - RRA algorithm combines normalized ranks across methods
  - Final consensus represents robust interaction predictions

### Generality Assessment
- **Dependency Conditions**:
  - Species: Default human gene symbols, requires homology mapping for other species
  - Database: Comprehensive ligand-receptor resource with complex support
  - Tools: liana, scanpy, scientific Python stack, plotnine for visualization

- **Extensibility**:
  - Data Replacement: Compatible with any annotated single-cell dataset
  - Sample Types: Tissues, organoids, developmental series, disease samples
  - Parameter Adjustment: Method selection, aggregation strategy, rank thresholds

- **Applicable Scenarios**:
  - Data Scale: Hundreds to millions of cells
  - Research Purpose: High-confidence cell-cell communication, signaling network analysis, biomarker discovery
  - Technical Platform: All major scRNA-seq platforms with cell type annotations

### CODE EXAMPLE
```python
# Import required packages
import liana as li
import scanpy as sc

# Load single-cell data
adata = sc.datasets.pbmc68k_reduced()

# Run rank aggregate consensus analysis
li.mt.rank_aggregate(adata,
                     groupby='bulk_labels',  # Cell type annotation
                     resource_name='consensus',  # Ligand-receptor database
                     expr_prop=0.1,  # 10% minimum expression threshold
                     verbose=True,
                     n_perms=1000,  # Permutations for statistical testing
                     aggregate_method='rra')  # Robust Rank Aggregation

# View consensus results
consensus_results = adata.uns['liana_res']
print(f"Total interactions analyzed: {len(consensus_results)}")
print(f"Consensus columns: {list(consensus_results.columns)}")

# Filter high-confidence interactions (rank <= 0.01)
high_confidence = consensus_results[
    (consensus_results['magnitude_rank'] <= 0.01) & 
    (consensus_results['specificity_rank'] <= 0.01)
]
print(f"High-confidence interactions: {len(high_confidence)}")

# Visualize top consensus interactions
li.pl.dotplot(adata=adata,
              colour='magnitude_rank',
              size='specificity_rank',
              inverse_colour=True,  # Lower ranks = more intense color
              inverse_size=True,    # Lower ranks = larger dots
              source_labels=['CD14+ Monocyte', 'Dendritic', 'CD34+'],
              target_labels=['CD4+/CD45RO+ Memory', 'CD8+ Cytotoxic T', 'CD56+ NK'],
              top_n=15,  # Show top 15 interactions
              orderby='magnitude_rank',
              orderby_ascending=True,
              figure_size=(12, 8))

# Create network circle plot
li.pl.circle_plot(adata,
                  groupby='bulk_labels',
                  score_key='magnitude_rank',
                  inverse_score=True,
                  source_labels=['CD14+ Monocyte'],
                  filter_fun=lambda x: x['specificity_rank'] <= 0.05,
                  pivot_mode='counts',  # Count interactions per cell type pair
                  figure_size=(10, 10))

# Custom consensus with specific methods
from liana.method import logfc, geometric_mean
custom_methods = [logfc, geometric_mean]
custom_consensus = li.mt.AggregateClass(li.mt.aggregate_meta, methods=custom_methods)

# Run custom consensus
custom_consensus(adata,
                 groupby='bulk_labels',
                 expr_prop=0.1,
                 verbose=True,
                 n_perms=None)  # Skip permutations for faster analysis
```

### Key Parameters and Their Biological Significance
- **aggregate_method**: 'rra' (Robust Rank Aggregation) or 'mean' for different integration strategies
- **consensus_opts**: Controls whether to aggregate magnitude, specificity, or both scores
- **expr_prop**: Balances sensitivity and specificity by setting minimum expression requirements
- **n_perms**: Controls statistical power for permutation-based methods
- **return_all_lrs**: Determines whether to include low-expression interactions in analysis

### Rank Aggregation Algorithm Details
The RRA algorithm works by:
1. Normalizing ranks from each method to [0,1] scale
2. Calculating probability of observing each rank under null hypothesis using beta distribution
3. Taking minimum probability across methods for each interaction
4. Applying Bonferroni correction for multiple testing
5. Converting probabilities to final rank scores

This approach identifies interactions that are consistently highly ranked across multiple methods, providing robust predictions less susceptible to individual method biases.