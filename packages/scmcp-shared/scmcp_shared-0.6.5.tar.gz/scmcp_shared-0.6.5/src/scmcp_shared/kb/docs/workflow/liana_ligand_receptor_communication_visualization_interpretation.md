## Workflow 3: Ligand-Receptor Interaction Visualization and Interpretation

### Overview
This workflow focuses on the visualization and biological interpretation of ligand-receptor interaction results from single-cell transcriptomics data. It provides comprehensive plotting capabilities to explore cell-cell communication patterns, identify key signaling pathways, and generate publication-quality figures. The workflow is essential for transforming statistical results into biological insights and communicating findings effectively.

### Standard Steps
1. **Data Input**:
   - Ligand-receptor analysis results stored in AnnData object
   - Results DataFrame containing interaction scores and metadata
   - Cell type annotations and expression statistics
   - Optional: Additional metadata for biological context

2. **External Resources**:
   - Plotting libraries (plotnine, matplotlib, networkx)
   - Color palettes and aesthetic themes
   - File I/O capabilities for figure export
   - Optional: Biological pathway databases for interpretation

3. **Preprocessing**:
   - Result filtering based on statistical thresholds
   - Interaction prioritization and ranking
   - Cell type subset selection for focused analysis
   - Score normalization and transformation for visualization

4. **Core Analysis**:
   - Dot plot generation for interaction overview
   - Tile plot creation for detailed expression patterns
   - Circle plot construction for network visualization
   - Custom plot modification and aesthetic enhancement
   - Interactive filtering and parameter tuning

5. **Result Storage**:
   - High-resolution figure files (PDF, PNG, SVG)
   - Plot objects for further modification
   - Filtered interaction DataFrames for downstream analysis
   - Visualization parameters and settings for reproducibility

6. **Visualization Types**:
   - Dot plots: Interaction magnitude vs specificity
   - Tile plots: Ligand/receptor expression patterns
   - Circle plots: Network-level communication patterns
   - Custom plots: User-defined visualizations with plotnine

### Technical Details
- **Key Functions**:
  - `li.pl.dotplot()` - interaction overview with color/size encoding
  - `li.pl.tileplot()` - detailed expression pattern visualization
  - `li.pl.circle_plot()` - network-based interaction display
  - `plotnine` integration - custom plot modification and theming
  - `plot.save()` - figure export functionality

- **Data Object Changes**:
  - Input: AnnData object with ligand-receptor results in `.uns`
  - Processing: Creates plot objects and filtered DataFrames
  - Output: External figure files and plot objects
  - No modification to original data objects

- **Data Object Management**:
  - Multiple plot objects can be created from same results
  - Plot objects support chaining and modification
  - Results can be filtered and subset without modifying original data
  - Different visualization types access same underlying data

- **Result Location**:
  - External files: Saved plots (PDF, PNG, SVG formats)
  - In-memory: plotnine plot objects for further modification
  - Filtered DataFrames: Subset interactions based on criteria
  - Visualization parameters: Stored within plot objects

- **Data Flow Tracking**:
  - Raw results → filtering/subsetting → plot generation → aesthetic modification → export
  - Each visualization type processes data differently for optimal display
  - Interactive filtering allows dynamic exploration of results
  - Plot objects maintain reference to underlying data for consistency

### Generality Assessment
- **Dependency Conditions**:
  - Species: Visualization is species-agnostic
  - Database: No external database dependencies for plotting
  - Tools: liana, plotnine, matplotlib, networkx for specific plot types

- **Extensibility**:
  - Data Replacement: Compatible with any ligand-receptor results
  - Sample Types: All biological contexts with cell type annotations
  - Parameter Adjustment: Color schemes, sizes, thresholds, layouts

- **Applicable Scenarios**:
  - Data Scale: Any size dataset with appropriate filtering
  - Research Purpose: Result presentation, pattern discovery, hypothesis generation
  - Technical Platform: Compatible with all analysis platforms generating ligand-receptor results

### CODE EXAMPLE
```python
# Import required packages
import liana as li
import scanpy as sc
import plotnine as p9

# Load data and run analysis (assuming previous workflows completed)
adata = sc.datasets.pbmc68k_reduced()
li.mt.rank_aggregate(adata, groupby='bulk_labels', expr_prop=0.1)

# 1. Dot Plot - Interaction Overview
dotplot = li.pl.dotplot(adata=adata,
                       colour='magnitude_rank',      # Color by interaction strength
                       size='specificity_rank',     # Size by interaction specificity
                       inverse_colour=True,         # Lower ranks = more intense color
                       inverse_size=True,           # Lower ranks = larger dots
                       source_labels=['CD14+ Monocyte', 'Dendritic'],
                       target_labels=['CD4+/CD45RO+ Memory', 'CD8+ Cytotoxic T'],
                       filter_fun=lambda x: x['specificity_rank'] <= 0.05,
                       figure_size=(10, 8))

# Save dot plot
dotplot.save('ligand_receptor_dotplot.pdf', dpi=300)

# 2. Tile Plot - Detailed Expression Patterns
tileplot = li.pl.tileplot(adata=adata,
                         fill='means',               # Fill with expression means
                         label='props',              # Label with expression proportions
                         label_fun=lambda x: f'{x:.2f}',  # Format labels
                         top_n=10,                   # Show top 10 interactions
                         orderby='magnitude_rank',
                         orderby_ascending=True,
                         source_labels=['CD14+ Monocyte'],
                         target_labels=['CD4+/CD45RO+ Memory'],
                         source_title='Ligand',
                         target_title='Receptor',
                         figure_size=(8, 7))

# 3. Circle Plot - Network Visualization
circle_plot = li.pl.circle_plot(adata,
                               groupby='bulk_labels',
                               score_key='magnitude_rank',
                               inverse_score=True,
                               source_labels=['CD14+ Monocyte', 'Dendritic'],
                               filter_fun=lambda x: x['specificity_rank'] <= 0.05,
                               pivot_mode='counts',    # Count interactions
                               figure_size=(12, 12))

# 4. Custom Plot Modification
custom_plot = (dotplot + 
               # Change theme
               p9.theme_dark() +
               # Modify theme elements
               p9.theme(
                   strip_text=p9.element_text(size=12, face='bold'),
                   axis_text=p9.element_text(size=10),
                   legend_position='right',
                   figure_size=(12, 8)
               ) +
               # Add custom labels
               p9.labs(
                   title='High-Confidence Ligand-Receptor Interactions',
                   colour='Magnitude Rank',
                   size='Specificity Rank'
               ))

# Save custom plot
custom_plot.save('custom_ligand_receptor_plot.pdf', dpi=300)

# 5. Multiple Cell Type Comparison
multi_cell_plot = li.pl.dotplot(adata=adata,
                               colour='lr_means',
                               size='cellphone_pvals',
                               inverse_size=True,
                               source_labels=['CD14+ Monocyte', 'Dendritic', 'CD34+'],
                               target_labels=['CD4+/CD45RO+ Memory', 'CD8+ Cytotoxic T', 'CD56+ NK'],
                               top_n=20,
                               filter_fun=lambda x: x['cellphone_pvals'] <= 0.01,
                               figure_size=(14, 10))

# 6. Export filtered results for further analysis
results = adata.uns['liana_res']
high_confidence_interactions = results[
    (results['magnitude_rank'] <= 0.01) & 
    (results['specificity_rank'] <= 0.01)
]

# Save filtered interactions
high_confidence_interactions.to_csv('high_confidence_interactions.csv', index=False)

print(f"Generated {len(high_confidence_interactions)} high-confidence interactions")
print(f"Top interactions by magnitude rank:")
print(high_confidence_interactions.nsmallest(10, 'magnitude_rank')[['source', 'target', 'ligand_complex', 'receptor_complex']])
```

### Visualization Parameters and Their Interpretation
- **colour**: Represents interaction magnitude/strength (lower ranks = stronger interactions)
- **size**: Represents interaction specificity/confidence (lower ranks = more specific)
- **inverse_colour/inverse_size**: Reverses scale so lower ranks appear more prominent
- **filter_fun**: Allows dynamic filtering based on statistical thresholds
- **top_n**: Limits display to top N interactions for clarity
- **source_labels/target_labels**: Focuses analysis on specific cell type pairs

### Biological Interpretation Guidelines
1. **Dot Plot Interpretation**:
   - Large, darkly colored dots: High-confidence, strong interactions
   - Small, lightly colored dots: Low-confidence or weak interactions
   - Missing dots: Interactions filtered out by expression thresholds

2. **Tile Plot Interpretation**:
   - Color intensity: Expression level of ligand/receptor
   - Numbers: Expression proportion in cell population
   - Pattern recognition: Co-expression patterns across cell types

3. **Circle Plot Interpretation**:
   - Node size: Number of interactions involving that cell type
   - Edge thickness: Strength or number of interactions between cell types
   - Layout: Spatial arrangement of communication patterns

4. **Rank-based Interpretation**:
   - Magnitude rank < 0.01: Top 1% of interactions by strength
   - Specificity rank < 0.01: Top 1% of interactions by specificity
   - Combined filtering: Identifies high-confidence, specific interactions

This visualization workflow transforms statistical ligand-receptor predictions into interpretable biological insights, enabling researchers to identify key signaling pathways, understand cell-type specific communication patterns, and generate publication-ready figures.