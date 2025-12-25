Static Structural Call-Graph Analysis (SSCA) for C Programs

This repository provides the full implementation, datasets, and supporting material for the Static Structural Call-Graph Analysis (SSCA) Strategy—an architectural analysis methodology designed to uncover structural bottlenecks, deep call chains, modular boundaries, and optimization opportunities in C programs. The workflow integrates static analysis, graph-theoretic metrics, centrality scoring, critical-path detection, and optional dynamic profiling.

1. Overview

SSCA is a structured technique for analyzing the architecture of C codebases using call-graph–driven insights. It enables developers and researchers to:

Detect architecturally influential functions

Identify dispatcher nodes, hubs, and coordination points

Discover modular boundaries via community detection

Highlight deep structural call chains

Quantify structural complexity with graph metrics

Locate and remove unreachable (dead) functions

Combine static and dynamic performance signals for prioritization

The methodology is applicable to embedded systems, IoT firmware, compilers, real-time systems, and any C-based architecture requiring optimization or refactoring.

2. Repository Structure
/src/               # C source programs for analysis
/graphs/            # Raw and reduced call-graph DOT files
/analysis/          # Python code for metrics, centrality scoring, CPSA, FMD
/figures/           # Generated call-graph visualizations
/paper/             # Manuscript, results, references, and supplementary material

3. Features

Static Call-Graph Extraction: Doxygen + GraphViz–based pipeline

Structural Metrics: Betweenness, PageRank, degree measures

Structural Centrality Scoring (SCS): A normalized model combining multiple metrics

Critical Path Structural Analysis (CPSA): Deep-chain detection

Functional Modularity Detection (FMD): Louvain-based module extraction

Dead-Code Detection: Reachability analysis from entry points

Static–Dynamic Comparative Framework: Integration with gprof or PMU data

4. Getting Started
Prerequisites

Python 3.9+

NetworkX

PyGraphviz

Doxygen

GraphViz

(Optional) gprof for runtime profiling

Installation
pip install -r requirements.txt

Run Analysis
python analysis/run_scca.py --input src/

5. Example Outputs

Complete call graph (DOT + PNG)

Reduced call graph highlighting central structures

CSV/JSON reports containing:

Centrality metrics

Critical paths

Modular clusters

Dead-code list

Structural Centrality Score rankings

6. Results Summary

Applied to a representative C program (13 functions, 15 edges), SSCA:

Reduced dead code by 15.38%

Identified a structural critical path of depth 5

Improved prioritization accuracy by 32% compared to PageRank alone

Revealed clear modular boundaries and dispatcher-centric architecture

7. Citation

If you use SSCA or the associated dataset in academic work, please cite the paper (add BibTeX or citation once finalized).
