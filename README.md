# Static Structural Call-Graph Analysis (SSCA) for C Programs

This repository provides the implementation, datasets, and artifacts for the
**Static Structural Call-Graph Analysis (SSCA)** Strategy—an architectural
analysis workflow for identifying structural bottlenecks, deep call chains,
modular boundaries, and optimization opportunities in C programs.

SSCA integrates static call-graph extraction, graph-theoretic metrics,
centrality scoring, critical-path detection, modularity analysis, and optional
dynamic profiling to support optimization-oriented architectural reasoning.


## 1. Overview

SSCA enables developers and researchers to:

- Identify architecturally influential functions.
- Detect dispatcher nodes, hubs, and coordination points.
- Highlight deep structural call chains and critical paths.
- Extract modular boundaries via community detection.
- Compute structural metrics (betweenness, PageRank, degree).
- Identify dead or unreachable functions using reachability models.
- Combine static structure with dynamic profiling (gprof/PMU).

The methodology is applicable across embedded systems, IoT firmware,
compiler front-ends, real-time systems, and large-scale C architectures.


## 2. Repository Structure
- /src/               # C source programs for analysis
- /graphs/            # Raw and reduced call-graph DOT files
- /analysis/          # Python code for metrics, centrality scoring, CPSA, FMD
- /figures/           # Generated call-graph visualizations
- /paper/             # Manuscript, results, references, and supplementary material
- /temp/              # Files found after running doxygen

## 3. Features

- **Static Call-Graph Extraction** using Doxygen + GraphViz.
- **Structural Metrics** including betweenness, PageRank, and out-degree.
- **Structural Centrality Scoring (SCS)** for prioritizing influential nodes.
- **Critical Path Structural Analysis (CPSA)** to detect deep call chains.
- **Functional Modularity Detection (FMD)** using Louvain clustering.
- **Dead-Code Identification** via reachability from entry points.
- **Static–Dynamic Comparative Interpretation** for profiling-based refinement.


## 4. Getting Started

### Prerequisites

- Python 3.9+
- NetworkX
- PyGraphviz
- Doxygen
- GraphViz
- (Optional) `gprof` for runtime profiling

### Installation
pip install -r requirements.txt

### Running the Analysis
python analysis/run_scca.py --input src/



## 5. Example Outputs

The pipeline generates:

- Full call graph (DOT/PNG)
- Reduced call graph highlighting structural centers
- CSV/JSON reports containing:
  - Structural metrics
  - Critical paths
  - Modular clusters
  - Dead-code listings
- Ranked Structural Centrality Scores (SCS)


## 6. Results Summary

Applied to a representative C program (13 functions, 15 edges), SSCA achieves:

- **15.38% dead-code reduction**
- **Critical path detection of depth 5**
- **32% improvement in prioritization accuracy** compared to PageRank alone
- Clear modular boundaries and dispatcher-centric architectural patterns


## 7. Citation

If you use SSCA or this dataset in academic work, please cite the corresponding
paper (citation block will be added once finalized).
