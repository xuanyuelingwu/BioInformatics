# CellAgent: AI Agent for Single-Cell Multi-Omics Analysis

<p align="center">
  <strong>An autonomous AI agent specialized in single-cell RNA-seq data analysis, inspired by Stanford's <a href="https://github.com/snap-stanford/biomni">BioMNI</a> framework.</strong>
</p>

---

## Overview

**CellAgent** is a domain-specific AI agent that combines Large Language Model (LLM) reasoning with specialized bioinformatics tools and curated domain knowledge to autonomously analyze single-cell multi-omics data. Built upon the architectural principles of Stanford's BioMNI, CellAgent adapts the general-purpose biomedical agent paradigm to the focused domain of single-cell genomics.

The agent operates through a **ReAct (Reasoning + Acting) loop**: it receives a natural language query, reasons about the appropriate analysis strategy, selects relevant tools and knowledge, generates executable Python code, and iteratively refines its approach based on execution results.

## Key Features

| Feature | Description |
|---------|-------------|
| **ReAct Reasoning Loop** | Autonomous multi-step analysis with iterative reasoning and code execution |
| **39 Specialized Tools** | Covering 8 categories of single-cell analysis (preprocessing, clustering, annotation, DE, trajectory, visualization, integration, gene analysis) |
| **Domain Knowledge Base** | 5 curated knowledge documents covering QC best practices, cell markers, workflow guides, troubleshooting, and multi-omics integration |
| **LLM-Driven Resource Retrieval** | Dynamically selects relevant tools and knowledge for each query |
| **LLM-Assisted Cell Type Annotation** | Uses LLM knowledge to interpret marker genes and predict cell types |
| **Persistent Execution Environment** | Variables persist across analysis steps, maintaining AnnData objects in memory |
| **Interactive Chat Mode** | Follow-up questions and iterative refinement of analysis |
| **Publication-Quality Visualization** | Automated generation of UMAP, dot plots, volcano plots, and more |

## Architecture

CellAgent's architecture follows the BioMNI design pattern with domain-specific adaptations:

```
┌─────────────────────────────────────────────────────────┐
│                      User Query                          │
│  "Analyze this PBMC dataset and annotate cell types"     │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│               Resource Retriever (LLM)                    │
│  Selects relevant tools, knowledge, and libraries         │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│                  ReAct Agent Loop                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────────────┐      │
│  │  THINK   │──▶│  CODE    │──▶│  EXECUTE & OBSERVE│     │
│  │(Reasoning)│  │(Generate)│   │  (Python REPL)    │     │
│  └──────────┘   └──────────┘   └──────────────────┘      │
│       ▲                              │                    │
│       └──────────────────────────────┘                    │
└──────────────────────────────────────────────────────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
   ┌───────────┐ ┌──────────┐ ┌──────────┐
   │   Tools   │ │Knowledge │ │Libraries │
   │ (39 tools)│ │(5 docs)  │ │(scanpy..)│
   └───────────┘ └──────────┘ └──────────┘
```

### Component Comparison with BioMNI

| Component | BioMNI | CellAgent |
|-----------|--------|-----------|
| Agent Core | LangGraph-based A1 agent | ReAct loop with OpenAI API |
| Tool System | 200+ tools across all biomedicine | 39 tools focused on single-cell |
| Knowledge Base | General biomedical know-how | Single-cell specific (QC, markers, workflows) |
| Resource Retrieval | LLM-based tool/data/library selection | LLM-based tool/knowledge/library selection |
| Code Execution | Persistent Python REPL | Persistent Python REPL |
| Data Lake | 11GB biomedical databases | Not needed (uses scanpy datasets) |
| LLM Integration | Multiple providers | OpenAI-compatible API |

## Installation

### Prerequisites

- Python 3.10+
- An OpenAI-compatible API key

### Install from Source

```bash
git clone https://github.com/xuanyuelingwu/BioInformatics.git
cd BioInformatics/CellAgent

# Install core dependencies
pip install -e .

# Install all optional dependencies (recommended)
pip install -e ".[full]"
```

### Required Packages

```bash
pip install openai scanpy anndata numpy pandas matplotlib seaborn scipy scikit-learn
pip install harmonypy leidenalg gseapy scrublet  # optional but recommended
```

## Quick Start

### 1. Agent Mode (Autonomous Analysis)

```python
from cellagent import CellAgent, CellAgentConfig

# Configure
config = CellAgentConfig(
    llm_model="gpt-4.1-mini",
    temperature=0.1,
    max_iterations=20,
    verbose=True,
)

# Initialize
agent = CellAgent(config=config, output_dir="./output")

# Run analysis with natural language
result = agent.run(
    query="Load the PBMC3k dataset, perform QC, normalize, cluster, "
          "and annotate cell types using known PBMC markers.",
)
print(result)
```

### 2. Direct Tool Usage

```python
import scanpy as sc
from cellagent.tools.preprocessing import calculate_qc_metrics, filter_cells_and_genes
from cellagent.tools.clustering import compute_neighbors, run_leiden_clustering, run_umap
from cellagent.tools.annotation import annotate_with_markers

# Load data
adata = sc.datasets.pbmc3k()

# Step-by-step analysis
qc_report = calculate_qc_metrics(adata, output_dir="./output")
filter_report = filter_cells_and_genes(adata, min_genes=200, max_pct_mt=5)

# ... continue with normalization, PCA, clustering, etc.
```

### 3. Interactive Chat Mode

```python
agent = CellAgent(output_dir="./output")

# Initial analysis
agent.run("Load PBMC3k and perform basic preprocessing and clustering.")

# Follow-up questions
agent.chat("What are the marker genes for cluster 0?")
agent.chat("Try resolution 1.0 and re-cluster.")
agent.chat("Annotate cell types using PBMC markers.")
```

### 4. Command Line Interface

```bash
# Single query
cellagent --query "Analyze PBMC3k dataset" --output ./results

# Interactive mode
cellagent --interactive

# With custom data
cellagent --query "Run QC and clustering" --data my_data.h5ad
```

## Tool Catalog

### Preprocessing (8 tools)
| Tool | Description |
|------|-------------|
| `load_h5ad` | Load .h5ad files into AnnData |
| `load_10x_mtx` | Load 10X Genomics Cell Ranger output |
| `calculate_qc_metrics` | Compute QC metrics (genes/cell, UMI, %MT) |
| `filter_cells_and_genes` | Filter low-quality cells and genes |
| `detect_doublets` | Detect doublets using Scrublet |
| `normalize_and_log_transform` | Normalize and log-transform |
| `select_highly_variable_genes` | HVG selection (Seurat v3) |
| `run_pca` | PCA with elbow plot |

### Clustering (6 tools)
| Tool | Description |
|------|-------------|
| `compute_neighbors` | K-nearest neighbor graph |
| `run_umap` | UMAP embedding |
| `run_tsne` | t-SNE embedding |
| `run_leiden_clustering` | Leiden clustering |
| `run_louvain_clustering` | Louvain clustering |
| `evaluate_clustering_quality` | Silhouette score, CH index |

### Annotation (5 tools)
| Tool | Description |
|------|-------------|
| `find_marker_genes` | DEG-based marker gene identification |
| `annotate_with_markers` | Marker gene-based annotation |
| `annotate_with_llm` | LLM-assisted cell type annotation |
| `score_cell_types` | Gene set scoring |
| `compare_annotations` | Compare annotation sets (ARI, NMI) |

### Differential Expression (4 tools)
| Tool | Description |
|------|-------------|
| `differential_expression` | DE analysis (Wilcoxon, t-test) |
| `volcano_plot` | Volcano plot generation |
| `gene_set_enrichment` | GO/KEGG enrichment (Enrichr) |
| `gsea_prerank` | Pre-ranked GSEA |

### Trajectory (4 tools)
| Tool | Description |
|------|-------------|
| `run_diffusion_map` | Diffusion map embedding |
| `compute_pseudotime_dpt` | Diffusion pseudotime |
| `run_paga` | PAGA trajectory topology |
| `identify_trajectory_genes` | Pseudotime-correlated genes |

### Visualization (6 tools)
| Tool | Description |
|------|-------------|
| `plot_umap_colored` | Multi-panel UMAP plots |
| `plot_dotplot` | Marker gene dot plots |
| `plot_heatmap` | Expression heatmaps |
| `plot_stacked_violin` | Stacked violin plots |
| `plot_cell_composition` | Cell type composition bars |
| `generate_analysis_summary` | Comprehensive analysis report |

### Integration (3 tools)
| Tool | Description |
|------|-------------|
| `integrate_harmony` | Harmony batch correction |
| `integrate_bbknn` | BBKNN integration |
| `evaluate_integration` | Integration quality metrics |

### Gene Analysis (3 tools)
| Tool | Description |
|------|-------------|
| `gene_correlation_network` | Gene co-expression network |
| `cell_cycle_scoring` | Cell cycle phase scoring |
| `query_gene_info` | LLM-powered gene information |

## Knowledge Base

CellAgent includes 5 curated knowledge documents:

1. **QC Best Practices** - Filtering thresholds, doublet detection, adaptive QC
2. **Cell Type Markers** - Canonical markers for PBMC, brain, lung, liver (human & mouse)
3. **Workflow Guide** - Step-by-step analysis pipeline with decision points
4. **Troubleshooting** - Solutions for common clustering, annotation, and technical issues
5. **Multi-Omics Integration** - Batch correction strategies, CITE-seq, 10X Multiome

## Project Structure

```
CellAgent/
├── cellagent/
│   ├── __init__.py              # Package entry point
│   ├── config.py                # Configuration management
│   ├── llm.py                   # LLM client factory
│   ├── cli.py                   # Command-line interface
│   ├── agent/
│   │   ├── cell_agent.py        # Core ReAct agent
│   │   └── executor.py          # Persistent code executor
│   ├── tools/
│   │   ├── tool_registry.py     # Tool registration system
│   │   ├── preprocessing.py     # QC, normalization, PCA
│   │   ├── clustering.py        # Neighbors, clustering, UMAP
│   │   ├── annotation.py        # Cell type annotation
│   │   ├── differential.py      # DE analysis, enrichment
│   │   ├── trajectory.py        # Pseudotime, PAGA
│   │   ├── visualization.py     # Plotting tools
│   │   ├── integration.py       # Batch correction
│   │   └── gene_analysis.py     # Gene networks, cell cycle
│   ├── knowledge/
│   │   ├── loader.py            # Knowledge document loader
│   │   ├── qc_best_practices.md
│   │   ├── cell_markers.md
│   │   ├── workflow_guide.md
│   │   ├── troubleshooting.md
│   │   └── multiomics_integration.md
│   └── retriever/
│       └── resource_retriever.py # LLM-driven resource selection
├── tests/
│   └── test_components.py       # Component tests (5/5 passing)
├── examples/
│   ├── quickstart.py            # Agent mode example
│   └── direct_tools.py          # Direct tool usage example
├── pyproject.toml               # Package configuration
├── LICENSE                      # MIT License
└── README.md                    # This file
```

## Design Principles

Following BioMNI's architecture, CellAgent adheres to these design principles:

1. **Declarative Tool Descriptions**: Tool metadata (parameters, types, descriptions) is separated from implementation, enabling LLM-driven tool selection and code generation.

2. **Know-How Driven**: Domain expertise is encoded in Markdown documents that the agent can retrieve and reference during analysis, rather than being hardcoded.

3. **ReAct Reasoning Loop**: The agent iteratively thinks, generates code, executes it, and observes results, allowing it to adapt its strategy based on intermediate findings.

4. **LLM Resource Retrieval**: Instead of loading all tools and knowledge, the agent uses an LLM to dynamically select the most relevant resources for each query.

5. **Persistent Execution**: The Python REPL maintains state across steps, so AnnData objects and intermediate results persist throughout the analysis session.

## Configuration

```python
from cellagent import CellAgentConfig

config = CellAgentConfig(
    # LLM settings
    llm_model="gpt-4.1-mini",      # Model name
    temperature=0.1,                 # Lower = more deterministic
    
    # Agent settings
    max_iterations=50,               # Max ReAct iterations
    use_resource_retriever=True,     # Enable dynamic tool selection
    verbose=True,                    # Print progress
    
    # Paths
    output_path="./output",          # Output directory
)
```

Environment variables:
- `OPENAI_API_KEY`: API key for OpenAI-compatible LLM
- `CELLAGENT_LLM_MODEL`: Override default model
- `CELLAGENT_OUTPUT_PATH`: Override default output path

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments

- **[BioMNI](https://github.com/snap-stanford/biomni)** (Stanford SNAP Lab) - The architectural inspiration for this project
- **[Scanpy](https://scanpy.readthedocs.io/)** - Core single-cell analysis library
- **[AnnData](https://anndata.readthedocs.io/)** - Data structure for annotated data
