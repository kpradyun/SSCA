import pygraphviz as pgv
import networkx as nx
import csv
import argparse
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional, List, Set, Any
import sys
import json
from collections import defaultdict
from datetime import datetime

INPUT_FILE = "output.dot"
OUTPUT_STATS_CSV = "function_stats.csv"
OUTPUT_REDUCED_DOT = "reduced_graph.dot"
OUTPUT_JSON = "analysis_results.json"
OUTPUT_DEAD_CODE = "dead_code.txt"
OUTPUT_HOT_PATHS = "hot_paths.txt"
OUTPUT_CLUSTERS = "clusters.json"


class CallGraphAnalyzer:
    def __init__(self, input_file: str, memory_efficient: bool = False):
        self.input_file = input_file
        self.graph: Optional[nx.DiGraph] = None
        self.node_importance: Dict[str, float] = {}
        self.memory_efficient = memory_efficient
        self.analysis_results: Dict[str, Any] = {}

        self.dead_code: Set[str] = set()
        self.entry_points: Set[str] = set()
        self.hot_paths: List[Tuple[List[str], float]] = []
        self.clusters: Dict[int, List[str]] = {}
        self.pagerank_scores: Dict[str, float] = {}

    def load_graph(self) -> nx.DiGraph:
        print(f"Loading graph from {self.input_file}...")

        if not Path(self.input_file).exists():
            raise FileNotFoundError(f"Input file '{self.input_file}' not found")

        try:
            ag = pgv.AGraph(self.input_file)
        except Exception as e:
            raise ValueError(f"Failed to parse DOT file: {e}")

        if len(ag.nodes()) == 0:
            raise ValueError("Input graph contains no nodes")

        G = nx.DiGraph()

        for n in ag.nodes():
            raw_id = str(n)
            label = ag.get_node(n).attr.get("label") or raw_id
            G.add_node(raw_id, raw_id=raw_id, label=label)

        print("Processing edges...")
        seen_edges = set()
        for edge in ag.edges():
            src, dst = str(edge[0]), str(edge[1])
            if src != dst and (src, dst) not in seen_edges:
                G.add_edge(src, dst)
                seen_edges.add((src, dst))

        print(f"Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

        if not nx.is_weakly_connected(G):
            print(
                f"Warning: Graph has {nx.number_weakly_connected_components(G)} disconnected components"
            )

        return G

    def compute_node_importance(self) -> None:
        print("Computing centrality metrics...")

        try:
            betweenness = nx.betweenness_centrality(self.graph, normalized=True)
        except Exception as e:
            print(f"Warning: Betweenness failed: {e}")
            betweenness = {n: 0.0 for n in self.graph.nodes()}

        try:
            self.pagerank_scores = nx.pagerank(self.graph, alpha=0.85)
        except Exception as e:
            print(f"Warning: PageRank failed: {e}")
            self.pagerank_scores = {n: 1 / len(self.graph) for n in self.graph.nodes()}

        max_score = max(betweenness.values()) if betweenness else 1.0
        self.node_importance = {
            n: (v / max_score) * 100 if max_score > 0 else 0.0
            for n, v in betweenness.items()
        }

    def identify_dead_code(self) -> Set[str]:
        print("Identifying dead code...")

        self.entry_points = {n for n in self.graph if self.graph.in_degree(n) == 0}

        reachable = set()
        for entry in self.entry_points:
            reachable.add(entry)
            reachable.update(nx.descendants(self.graph, entry))

        self.dead_code = set(self.graph.nodes()) - reachable

        print(f"Entry points: {len(self.entry_points)}")
        print(f"Dead code functions: {len(self.dead_code)}")

        return self.dead_code

    def detect_hot_paths(self, max_depth: int = 5, top_n: int = 10):
        print("Detecting hot paths...")
        edge_bw = nx.edge_betweenness_centrality(self.graph, normalized=True)

        if not self.entry_points:
            self.identify_dead_code()

        results = []
        for entry in list(self.entry_points)[:10]:
            stack = [(entry, [entry])]
            while stack:
                node, path = stack.pop()

                # score all paths, not only max depth
                results.append((path, self._score_path(path, edge_bw)))

                if len(path) >= max_depth:
                    continue

                for succ in self.graph.successors(node):
                    if succ not in path:
                        stack.append((succ, path + [succ]))

        results.sort(key=lambda x: x[1], reverse=True)
        self.hot_paths = results[:top_n]
        return self.hot_paths

    def _score_path(self, path, edge_bw):
        return sum(
            edge_bw.get((path[i], path[i + 1]), 0)
            for i in range(len(path) - 1)
        )

    def export_hot_paths(self):
        if not self.hot_paths:
            print("No hot paths detected.")
            return

        with open(OUTPUT_HOT_PATHS, "w", encoding="utf-8") as f:
            for i, (path, score) in enumerate(self.hot_paths, 1):
                f.write(f"Hot Path #{i}\n")
                f.write(f"Score: {score:.6f}\n")
                f.write(" -> ".join(path) + "\n\n")

    def identify_clusters(self):
        print("Identifying clusters...")
        undirected = self.graph.to_undirected()
        communities = nx.community.greedy_modularity_communities(undirected)

        self.clusters = defaultdict(list)
        for cid, community in enumerate(communities):
            for node in community:
                self.clusters[cid].append(node)

        return dict(self.clusters)

    def generate_statistics(self):
        print(f"Generating statistics to {OUTPUT_STATS_CSV}...")
        with open(OUTPUT_STATS_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "Function",
                    "In_Degree",
                    "Out_Degree",
                    "Betweenness",
                    "PageRank",
                    "Is_Entry",
                    "Is_Dead",
                ]
            )

            for n in self.graph.nodes():
                writer.writerow(
                    [
                        n,
                        self.graph.in_degree(n),
                        self.graph.out_degree(n),
                        self.node_importance.get(n, 0),
                        self.pagerank_scores.get(n, 0),
                        n in self.entry_points,
                        n in self.dead_code,
                    ]
                )

    def create_reduced_graph(self, threshold: float):
        important = [n for n, v in self.node_importance.items() if v >= threshold]
        if not important:
            important = sorted(
                self.node_importance,
                key=lambda n: self.node_importance[n],
                reverse=True,
            )[: max(1, len(self.graph) // 10)]

        reduced = self.graph.subgraph(important)
        nx.drawing.nx_agraph.write_dot(reduced, OUTPUT_REDUCED_DOT)

    def export_to_json(self):
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "nodes": len(self.graph),
                    "edges": self.graph.number_of_edges(),
                    "dead_code": list(self.dead_code),
                    "hot_paths": [
                        {"path": p, "score": s} for p, s in self.hot_paths
                    ],
                },
                f,
                indent=2,
            )

    def run_analysis(
        self,
        threshold: float,
        enable_dead_code=True,
        enable_hot_paths=True,
        enable_clustering=True,
        export_json=True,
    ):
        self.graph = self.load_graph()
        self.compute_node_importance()

        if enable_dead_code:
            self.identify_dead_code()

        if enable_clustering:
            self.identify_clusters()

        if enable_hot_paths:
            self.detect_hot_paths()
            self.export_hot_paths()

        self.generate_statistics()
        self.create_reduced_graph(threshold)

        if export_json:
            self.export_to_json()

        print("Analysis completed successfully!")
        print("Generated files:")
        print(f"  - {OUTPUT_STATS_CSV}")
        print(f"  - {OUTPUT_REDUCED_DOT}")
        if enable_hot_paths:
            print(f"  - {OUTPUT_HOT_PATHS}")
        if export_json:
            print(f"  - {OUTPUT_JSON}")


def main():
    global OUTPUT_STATS_CSV, OUTPUT_REDUCED_DOT, OUTPUT_JSON
    global OUTPUT_DEAD_CODE, OUTPUT_HOT_PATHS, OUTPUT_CLUSTERS

    parser = argparse.ArgumentParser(
        description="Comprehensive call graph analyzer"
    )

    parser.add_argument("--input", default=INPUT_FILE)
    parser.add_argument("--output-stats", default=OUTPUT_STATS_CSV)
    parser.add_argument("--output-reduced", default=OUTPUT_REDUCED_DOT)
    parser.add_argument("--output-json", default=OUTPUT_JSON)
    parser.add_argument("--threshold", type=float, default=0.0)
    parser.add_argument("--memory-efficient", action="store_true")
    parser.add_argument("--no-dead-code", action="store_true")
    parser.add_argument("--no-hot-paths", action="store_true")
    parser.add_argument("--no-clustering", action="store_true")
    parser.add_argument("--no-json", action="store_true")

    args = parser.parse_args()

    OUTPUT_STATS_CSV = args.output_stats
    OUTPUT_REDUCED_DOT = args.output_reduced
    OUTPUT_JSON = args.output_json

    analyzer = CallGraphAnalyzer(
        args.input, memory_efficient=args.memory_efficient
    )

    analyzer.run_analysis(
        threshold=args.threshold,
        enable_dead_code=not args.no_dead_code,
        enable_hot_paths=not args.no_hot_paths,
        enable_clustering=not args.no_clustering,
        export_json=not args.no_json,
    )


if __name__ == "__main__":
    main()

