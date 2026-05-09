#!/usr/bin/env python3
"""
generate_docs.py — Generate technical-foundations.tex and learning-resources.tex
for each of the 13 repos in the multi-root workspace.

Purpose:
    Produce two LaTeX documents per repository:
    1. technical-foundations.tex — theoretical and architectural basis
    2. learning-resources.tex   — curated Coursera/Pluralsight/ACG/GitHub resources

Usage:
    python3 generate_docs.py
    # Then compile: cd <repo>/docs && pdflatex <file>.tex

Dependencies:
    Python ≥ 3.9, no external packages required.
"""

from __future__ import annotations

import os
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

BASE = Path("/home/yann/Documents/Github")

# ─────────────────────────────────────────────────────────────────────────────
# LaTeX preamble shared across all documents
# ─────────────────────────────────────────────────────────────────────────────

PREAMBLE = r"""\documentclass[11pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[english]{babel}
\usepackage{lmodern}
\usepackage{microtype}
\usepackage{geometry}
\geometry{margin=2.5cm}
\usepackage{hyperref}
\hypersetup{
    colorlinks=true,
    linkcolor=blue!70!black,
    urlcolor=blue!70!black,
    citecolor=blue!70!black
}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{enumitem}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{fancyhdr}
\usepackage{graphicx}
\usepackage{listings}

\definecolor{codegray}{rgb}{0.95,0.95,0.95}
\definecolor{doctum}{rgb}{0.10,0.30,0.60}

\lstset{
  backgroundcolor=\color{codegray},
  basicstyle=\small\ttfamily,
  breaklines=true,
  frame=single,
  rulecolor=\color{gray!40},
  xleftmargin=1em,
  framexleftmargin=0.5em
}

\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\textcolor{doctum}{\small\textbf{Doctum Consilium}}}
\fancyhead[R]{\small\nouppercase{\leftmark}}
\fancyfoot[C]{\thepage}

\titleformat{\section}{\large\bfseries\color{doctum}}{}{0em}{}[\titlerule]
\titleformat{\subsection}{\normalsize\bfseries\color{doctum!80}}{}{0em}{}
"""

# ─────────────────────────────────────────────────────────────────────────────
# Per-repo content definitions
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class RepoDoc:
    name: str
    title: str
    subtitle: str
    description: str
    # --- technical doc ---
    tech_overview: str
    tech_architecture: str
    tech_key_concepts: List[str]
    tech_data_flow: str
    tech_dependencies: str
    tech_design_decisions: str
    # --- learning doc ---
    learn_prereqs: str
    learn_coursera: List[Dict]
    learn_pluralsight: List[Dict]
    learn_acg: List[Dict]
    learn_github: List[Dict]
    learn_books: List[Dict]


REPOS: List[RepoDoc] = [

# ─────────────────────────────────────────────
RepoDoc(
    name="doctum-trading-platform",
    title="Doctum Trading Platform",
    subtitle="Reinforcement Learning Trading System with LLM-Driven Decision Layer",
    description=(
        "Multi-service trading platform integrating a Reinforcement Learning agent, "
        "real-time dashboard, NinjaTrader 8 bridge, and Kubernetes deployment on OVH VPS."
    ),
    tech_overview=r"""
The platform implements an end-to-end automated trading pipeline:
market data is ingested from Binance and Alpaca, processed by a
Reinforcement Learning agent, enriched by an LLM reasoning layer via LiteLLM,
and executed through NinjaTrader~8 or Alpaca REST API.

The system is decomposed into three independently deployable microservices:
\begin{itemize}
  \item \textbf{rl-agent} (FastAPI, Python): core decision engine.
  \item \textbf{realtime-api} (FastAPI, Python): WebSocket bridge and dashboard backend.
  \item \textbf{realtime-web} (Vite/React, nginx): operator dashboard frontend.
\end{itemize}
All services are containerised with Docker and orchestrated on k3s via Kubernetes manifests.
""",
    tech_architecture=r"""
\begin{verbatim}
NinjaTrader 8 ──► realtime-api ──► rl-agent ──► LiteLLM Gateway
     ▲               │                │               │
     │           Redis PubSub     Simulation      Claude/GPT-4
     └── orders ◄────┘           Engine (PnL)
\end{verbatim}
The \textbf{rl-agent} exposes three REST endpoints:
\texttt{/decide} (heuristic-only), \texttt{/decide/llm} (LLM-enriched),
and \texttt{/risk-guard} (circuit-breaker policy).
Risk management is enforced at two levels: position-level drawdown limits
and a portfolio-level risk guard that can halt trading when daily loss
thresholds are exceeded.
""",
    tech_key_concepts=[
        r"Reinforcement Learning: Q-learning and policy gradient foundations; "
          r"state-action-reward-state (SARS) tuples; discount factor $\gamma$; "
          r"Bellman equation $Q(s,a) = r + \gamma \max_{a'} Q(s',a')$.",
        r"Signal Aggregation: weighted ensemble of technical signals (RSI, MACD, "
          r"volume), LLM semantic signals, and news heuristics. Aggregate score "
          r"$S = \sum_i w_i \cdot c_i \cdot s_i$ where $w_i$ is signal weight, "
          r"$c_i$ confidence, $s_i$ directional score $\in [-1,1]$.",
        r"Simulation Engine: mark-to-market PnL, slippage modelling, "
          r"Binance maker/taker bps fee model (2~bps maker, 5~bps taker).",
        r"LLM Integration: structured JSON prompting; fallback chain "
          r"(external LLM → local heuristic) controlled by env flag "
          r"\texttt{RL\_AGENT\_EXTERNAL\_LLM\_FALLBACK\_TO\_DEFAULT}.",
        r"Risk Guard: daily drawdown circuit-breaker; per-symbol exposure cap; "
          r"NT8 bridge message validation and deduplication.",
    ],
    tech_data_flow=r"""
Market tick → NT8 bridge → \texttt{/decide/llm} → LiteLLM Gateway →
LLM response (JSON) → signal fusion → action \{buy/sell/hold\} →
Alpaca executor or NT8 order →
Simulation Engine (PnL update) → Redis PubSub → Dashboard.
""",
    tech_dependencies=r"""
\begin{tabular}{ll}
\toprule
\textbf{Component} & \textbf{Technology} \\
\midrule
RL agent & FastAPI 0.110, Python 3.11 \\
LLM gateway & LiteLLM $\geq$ 1.40 \\
Broker API & Alpaca-trade-api, Binance REST \\
Message bus & Redis Pub/Sub \\
Persistence & PostgreSQL 15 (trade logs) \\
Container runtime & Docker 25, k3s v1.29 \\
CI/CD & GitHub Actions, AWS ECR \\
Monitoring & Prometheus + Grafana (planned) \\
\bottomrule
\end{tabular}
""",
    tech_design_decisions=r"""
\begin{itemize}
  \item \textbf{Microservice decomposition}: each service scales and redeploys
    independently; rl-agent can be replaced with a new model without touching the dashboard.
  \item \textbf{ECR image tags as version identifiers} (e.g.\ \texttt{2026-05-08}):
    simple date-based rollback without a dedicated semver registry.
  \item \textbf{LLM as an optional enrichment layer}: the system degrades gracefully
    to heuristic signals when the external LLM is unavailable.
  \item \textbf{Bps fee model}: accurate Binance fee simulation prevents over-optimistic
    backtesting; maker~2~bps, taker~5~bps configurable via env.
\end{itemize}
""",
    learn_prereqs=r"""
Python intermediate (decorators, async, dataclasses), basic REST API concepts,
Docker fundamentals, Git version control, basic probability and statistics.
""",
    learn_coursera=[
        {"title": "Machine Learning Specialization", "provider": "DeepLearning.AI / Stanford",
         "url": "https://www.coursera.org/specializations/machine-learning-introduction",
         "why": "Foundational RL, supervised and unsupervised learning by Andrew Ng."},
        {"title": "Deep Learning Specialization", "provider": "DeepLearning.AI",
         "url": "https://www.coursera.org/specializations/deep-learning",
         "why": "Neural network architectures used in DRL agents."},
        {"title": "Practical Reinforcement Learning", "provider": "HSE University",
         "url": "https://www.coursera.org/learn/practical-rl",
         "why": "Hands-on Q-learning, DQN, policy gradients with OpenAI Gym."},
        {"title": "Python for Financial Analysis and Algorithmic Trading",
         "provider": "Udemy (Jose Portilla)",
         "url": "https://www.udemy.com/course/python-for-finance-and-trading-algorithms/",
         "why": "Backtesting, technical indicators, Zipline/Quantopian patterns."},
    ],
    learn_pluralsight=[
        {"title": "Building Microservices with FastAPI", "provider": "Pluralsight",
         "url": "https://www.pluralsight.com/courses/building-microservices-fastapi",
         "why": "FastAPI patterns used throughout the platform."},
        {"title": "Docker and Kubernetes: The Big Picture", "provider": "Pluralsight",
         "url": "https://www.pluralsight.com/courses/docker-kubernetes-big-picture",
         "why": "Core k3s/k8s concepts for deployment."},
        {"title": "Kubernetes for Developers", "provider": "Pluralsight",
         "url": "https://www.pluralsight.com/paths/kubernetes-for-developers",
         "why": "Manifests, deployments, secrets, rolling updates."},
    ],
    learn_acg=[
        {"title": "AWS Certified Solutions Architect – Associate", "provider": "A Cloud Guru",
         "url": "https://acloudguru.com/course/aws-certified-solutions-architect-associate",
         "why": "ECR, IAM, VPC essentials used for image registry and secrets."},
        {"title": "Introduction to Kubernetes", "provider": "A Cloud Guru",
         "url": "https://acloudguru.com/course/introduction-to-kubernetes",
         "why": "k3s is a lightweight Kubernetes; same concepts apply."},
    ],
    learn_github=[
        {"title": "openai/gym", "url": "https://github.com/openai/gym",
         "why": "Reference RL environment interface; compatible with custom trading envs."},
        {"title": "AI4Finance-Foundation/FinRL", "url": "https://github.com/AI4Finance-Foundation/FinRL",
         "why": "Full RL trading framework; study its environment and agent structure."},
        {"title": "microsoft/qlib", "url": "https://github.com/microsoft/qlib",
         "why": "Quantitative investment platform; signal engineering patterns."},
        {"title": "tiangolo/fastapi", "url": "https://github.com/tiangolo/fastapi",
         "why": "Source and examples for the web framework used by rl-agent."},
        {"title": "BerriAI/litellm", "url": "https://github.com/BerriAI/litellm",
         "why": "LiteLLM gateway source — understand proxy routing and model fallbacks."},
    ],
    learn_books=[
        {"title": "Reinforcement Learning: An Introduction", "authors": "Sutton \\& Barto, 2nd ed.",
         "url": "http://incompleteideas.net/book/the-book-2nd.html",
         "why": "Definitive reference for RL theory including Q-learning and policy gradients."},
        {"title": "Advances in Financial Machine Learning", "authors": "Marcos Lopez de Prado",
         "url": "https://www.wiley.com/en-us/Advances+in+Financial+Machine+Learning-p-9781119482086",
         "why": "State-of-the-art ML techniques for quantitative finance."},
    ],
),

# ─────────────────────────────────────────────
RepoDoc(
    name="market_insights",
    title="Market Insights",
    subtitle="Real-Time Market Intelligence Pipeline with NLP and RAG",
    description=(
        "Market data ingestion, NLP summarisation, and Retrieval-Augmented Generation "
        "pipeline powered by Apache Airflow, Python, and Docker."
    ),
    tech_overview=r"""
Market Insights is a data engineering and NLP pipeline that collects financial
news and price data, extracts key insights via extractive summarisation and
LLM-augmented RAG, and serves structured signals to downstream consumers.

The pipeline is orchestrated by Apache Airflow and runs on a containerised
stack (Docker Compose). Raw data from multiple connectors (Yahoo Finance,
Alpaca, economic calendars) is stored in a vector database for semantic search.
""",
    tech_architecture=r"""
\begin{verbatim}
Connectors (Yahoo/Alpaca/News) ──► Airflow DAGs ──► NLP Pipeline
          │                                              │
          ▼                                        Vector DB (FAISS)
      PostgreSQL                                        │
          │                                        RAG Query ──► LLM
          └──────────────────────────── REST API ◄──────┘
\end{verbatim}
""",
    tech_key_concepts=[
        r"Apache Airflow: directed acyclic graph (DAG) scheduling; "
          r"task dependencies, XCom for inter-task communication, "
          r"operator types (PythonOperator, BashOperator, HttpSensor).",
        r"Extractive Summarisation: TF-IDF sentence scoring; "
          r"token frequency weighted by inverse document frequency; "
          r"$\text{score}(s) = \sum_{t \in s} \text{tf}(t) \cdot \text{idf}(t)$.",
        r"Vector Embeddings: sentence-transformers for semantic encoding; "
          r"FAISS approximate nearest-neighbour (ANN) search; "
          r"cosine similarity $\cos\theta = \frac{u \cdot v}{|u||v|}$.",
        r"RAG (Retrieval-Augmented Generation): relevant context retrieved from "
          r"vector store is injected into the LLM prompt to ground responses "
          r"in factual financial data.",
        r"Data Quality: price integrity tests (OHLCV consistency), "
          r"connector health checks, deduplication by hash.",
    ],
    tech_data_flow=r"""
Airflow DAG (scheduled) → Connector fetch → HTML strip + NLP clean →
Embedding generation → FAISS upsert →
On-demand RAG query → LLM enrichment → REST response.
""",
    tech_dependencies=r"""
\begin{tabular}{ll}
\toprule
\textbf{Component} & \textbf{Technology} \\
\midrule
Orchestration & Apache Airflow 2.x \\
NLP & sentence-transformers, spaCy \\
Vector store & FAISS (CPU) \\
LLM proxy & LiteLLM \\
Data sources & Yahoo Finance, Alpaca News API \\
Database & PostgreSQL \\
Container & Docker Compose \\
\bottomrule
\end{tabular}
""",
    tech_design_decisions=r"""
\begin{itemize}
  \item Airflow chosen over cron for retries, visibility, and dependency management.
  \item FAISS (CPU) preferred over managed vector DBs to avoid cloud egress costs.
  \item Extractive summarisation is language-model-free and deterministic —
    useful for offline/low-latency paths.
\end{itemize}
""",
    learn_prereqs="Python intermediate, SQL basics, basic NLP concepts, Docker fundamentals.",
    learn_coursera=[
        {"title": "Natural Language Processing Specialization", "provider": "DeepLearning.AI",
         "url": "https://www.coursera.org/specializations/natural-language-processing",
         "why": "Tokenisation, embeddings, seq2seq models used in the NLP pipeline."},
        {"title": "Data Engineering with Google Cloud", "provider": "Google",
         "url": "https://www.coursera.org/professional-certificates/gcp-data-engineering",
         "why": "Pipeline patterns, batch vs streaming — Airflow parallels."},
        {"title": "IBM Data Engineering Professional Certificate", "provider": "IBM",
         "url": "https://www.coursera.org/professional-certificates/ibm-data-engineer",
         "why": "SQL, ETL, Airflow, Kafka fundamentals."},
    ],
    learn_pluralsight=[
        {"title": "Apache Airflow: The Hands-On Guide", "provider": "Pluralsight",
         "url": "https://www.pluralsight.com/courses/apache-airflow-hands-on",
         "why": "DAG authoring, scheduling, XCom, sensors."},
        {"title": "Applied Natural Language Processing in Python", "provider": "Pluralsight",
         "url": "https://www.pluralsight.com/courses/python-natural-language-processing",
         "why": "Text preprocessing, TF-IDF, embeddings."},
    ],
    learn_acg=[
        {"title": "AWS Data Analytics Specialty", "provider": "A Cloud Guru",
         "url": "https://acloudguru.com/course/aws-certified-data-analytics-specialty",
         "why": "Data pipeline patterns applicable to this architecture."},
    ],
    learn_github=[
        {"title": "apache/airflow", "url": "https://github.com/apache/airflow",
         "why": "Source, examples, and DAG best practices."},
        {"title": "facebookresearch/faiss", "url": "https://github.com/facebookresearch/faiss",
         "why": "Vector index internals; understand IVF, HNSW index types."},
        {"title": "UKPLab/sentence-transformers", "url": "https://github.com/UKPLab/sentence-transformers",
         "why": "Embedding models used for semantic search."},
        {"title": "langchain-ai/langchain", "url": "https://github.com/langchain-ai/langchain",
         "why": "RAG pipeline patterns and retriever abstractions."},
    ],
    learn_books=[
        {"title": "Designing Data-Intensive Applications", "authors": "Martin Kleppmann",
         "url": "https://dataintensive.net/", "why": "Foundational for pipeline reliability and data consistency."},
        {"title": "Natural Language Processing with Transformers", "authors": "Lewis Tunstall et al.",
         "url": "https://www.oreilly.com/library/view/natural-language-processing/9781098136789/",
         "why": "Transformer models, fine-tuning, embeddings."},
    ],
),

# ─────────────────────────────────────────────
RepoDoc(
    name="medvision-ai",
    title="MedVision AI",
    subtitle="Medical Image AI Pipeline — Brain MRI Classification and Segmentation",
    description=(
        "Deep learning pipeline for brain MRI analysis using transfer learning, "
        "DVC data versioning, MLflow experiment tracking, and Docker deployment."
    ),
    tech_overview=r"""
MedVision AI implements a reproducible medical image analysis pipeline that:
\begin{enumerate}
  \item Preprocesses and versions MRI datasets with DVC.
  \item Trains classification and segmentation models (DenseNet121, ResNet50, Swin-V2)
    using PyTorch with transfer learning from ImageNet weights.
  \item Tracks experiments, metrics, and artefacts with MLflow.
  \item Serves inference via a FastAPI REST endpoint.
\end{enumerate}
The pipeline targets brain tumour classification (glioma, meningioma, pituitary, no-tumour)
and is designed for extensibility to segmentation tasks (BraTS-compatible datasets).
""",
    tech_architecture=r"""
\begin{verbatim}
Raw MRI dataset (NIfTI/DICOM)
    │
    ▼
DVC pipeline (preprocess → train → evaluate)
    │                        │
    ▼                        ▼
Versioned artefacts     MLflow Tracking
    │                   (metrics, params, models)
    ▼
FastAPI inference endpoint
    │
    ▼
DICOM-SR / JSON prediction output
\end{verbatim}
""",
    tech_key_concepts=[
        r"Transfer Learning: fine-tuning ImageNet-pretrained CNNs on medical images; "
          r"frozen backbone layers + trainable classification head; "
          r"prevents overfitting on limited medical datasets.",
        r"DenseNet121 architecture: dense connectivity $x_l = H_l([x_0, x_1, \ldots, x_{l-1}])$; "
          r"feature reuse; proven on CheXNet (chest X-ray diagnosis).",
        r"Data Augmentation: horizontal flip, rotation $\pm 10°$, colour jitter; "
          r"critical for medical image generalisation given dataset scarcity.",
        r"Class Imbalance: weighted sampling, macro-F1 as primary metric "
          r"rather than accuracy to avoid misleading results on imbalanced classes.",
        r"Reproducibility: DVC pins dataset versions + pipeline stages; "
          r"seeds fixed across NumPy/PyTorch/CUDA for deterministic training.",
        r"MLflow: automatic logging of hyperparameters, per-epoch metrics, "
          r"confusion matrices, and model artifacts for experiment comparison.",
    ],
    tech_data_flow=r"""
DICOM/NIfTI → DVC preprocess stage (resize, normalise) →
PyTorch DataLoader (augmentation) →
Transfer learning model → loss + metrics →
MLflow log → checkpoint save →
FastAPI inference (\texttt{POST /predict}).
""",
    tech_dependencies=r"""
\begin{tabular}{ll}
\toprule
\textbf{Component} & \textbf{Technology} \\
\midrule
Deep learning & PyTorch $\geq$ 2.0, torchvision \\
Model zoo & DenseNet121, ResNet50, Swin-V2-S \\
Data versioning & DVC 3.x \\
Experiment tracking & MLflow 2.x \\
Metrics & scikit-learn (F1, precision, recall, AUC) \\
Serving & FastAPI \\
\bottomrule
\end{tabular}
""",
    tech_design_decisions=r"""
\begin{itemize}
  \item DVC chosen over Git LFS for large dataset versioning with remote storage support.
  \item Macro-F1 as primary metric: clinically relevant — all classes matter equally.
  \item Three backbone options tested (DenseNet121, ResNet50, Swin-V2-S) to compare
    CNN vs.\ Vision Transformer performance on the same dataset.
\end{itemize}
""",
    learn_prereqs="Python, linear algebra (matrices, eigenvalues), calculus (gradients), basic statistics.",
    learn_coursera=[
        {"title": "AI for Medicine Specialization", "provider": "DeepLearning.AI",
         "url": "https://www.coursera.org/specializations/ai-for-medicine",
         "why": "Medical image analysis, diagnostic AI, treatment effect estimation — directly applicable."},
        {"title": "Deep Learning Specialization", "provider": "DeepLearning.AI",
         "url": "https://www.coursera.org/specializations/deep-learning",
         "why": "CNN architecture theory, optimisation, regularisation."},
        {"title": "Practical Data Science on AWS", "provider": "DeepLearning.AI / AWS",
         "url": "https://www.coursera.org/specializations/practical-data-science",
         "why": "MLOps, experiment tracking, model deployment patterns."},
    ],
    learn_pluralsight=[
        {"title": "PyTorch: Getting Started", "provider": "Pluralsight",
         "url": "https://www.pluralsight.com/courses/pytorch-getting-started",
         "why": "Tensors, autograd, DataLoader — foundations for this project."},
        {"title": "MLflow for ML Experiment Tracking", "provider": "Pluralsight",
         "url": "https://www.pluralsight.com/courses/mlflow-ml-experiment-tracking",
         "why": "Direct tool match."},
    ],
    learn_acg=[
        {"title": "Machine Learning on AWS", "provider": "A Cloud Guru",
         "url": "https://acloudguru.com/course/machine-learning-on-aws",
         "why": "SageMaker patterns for scalable model training."},
    ],
    learn_github=[
        {"title": "Project-MONAI/MONAI", "url": "https://github.com/Project-MONAI/MONAI",
         "why": "Medical image deep learning framework; transforms, datasets, metrics."},
        {"title": "mlflow/mlflow", "url": "https://github.com/mlflow/mlflow",
         "why": "Experiment tracking tool used in this project."},
        {"title": "iterative/dvc", "url": "https://github.com/iterative/dvc",
         "why": "Data version control; pipeline stages, remote storage."},
        {"title": "pytorch/vision", "url": "https://github.com/pytorch/vision",
         "why": "DenseNet, ResNet, Swin-V2 implementations."},
    ],
    learn_books=[
        {"title": "Deep Learning for Medical Image Analysis", "authors": "Zhou et al.",
         "url": "https://www.elsevier.com/books/deep-learning-for-medical-image-analysis/zhou/978-0-12-810408-8",
         "why": "Segmentation, classification, and detection in radiology."},
        {"title": "Programming PyTorch for Deep Learning", "authors": "Ian Pointer",
         "url": "https://www.oreilly.com/library/view/programming-pytorch-for/9781492045342/",
         "why": "Practical PyTorch patterns for transfer learning."},
    ],
),

# ─────────────────────────────────────────────
RepoDoc(
    name="k3s-fromOVHVps",
    title="k3s on OVH VPS",
    subtitle="Lightweight Kubernetes Cluster — Manifests, Playbooks and Secret Management",
    description=(
        "k3s cluster provisioning and operations on an OVH VPS: "
        "Kubernetes manifests, Helm-free deployment playbooks, "
        "ECR pull secret automation, and Traefik ingress configuration."
    ),
    tech_overview=r"""
This repository manages the infrastructure-as-code for a production k3s
(lightweight Kubernetes) cluster hosted on an OVH VPS.
It covers the full operational lifecycle: cluster provisioning, namespace
isolation, Kubernetes manifest management, Traefik ingress with TLS,
and automated AWS ECR pull secret rotation.

The cluster hosts multiple services from the Doctum Consilium project:
trading platform, portfolio, market screener, and LiteLLM gateway.
""",
    tech_architecture=r"""
\begin{verbatim}
OVH VPS (Ubuntu 22.04)
└── k3s (single-node)
    ├── traefik (ingress + TLS via Let's Encrypt)
    ├── doctum-trading namespace
    │   ├── rl-agent, realtime-api, realtime-web
    │   ├── PostgreSQL, Redis
    │   └── ecr-registry-secret (rotated every 11h)
    ├── portfolio namespace
    └── gateway namespace (LiteLLM)
\end{verbatim}
ECR tokens have a 12-hour TTL. A rotation script recreates
\texttt{ecr-registry-secret} before expiry to prevent \texttt{ImagePullBackOff}.
""",
    tech_key_concepts=[
        r"k3s: production-grade Kubernetes for resource-constrained environments; "
          r"bundles containerd, CoreDNS, Traefik, and local-path-provisioner.",
        r"Kubernetes objects: Deployment, Service, Ingress, ConfigMap, Secret, "
          r"StatefulSet, PersistentVolumeClaim, PriorityClass.",
        r"Secret lifecycle: k8s Secrets are base64-encoded (not encrypted at rest "
          r"by default); ECR Docker registry secrets store \texttt{.dockerconfigjson}; "
          r"rotation is mandatory every 12h for AWS ECR.",
        r"Traefik v2 ingress: IngressRoute CRD, TLS termination with cert-manager "
          r"or Let's Encrypt ACME challenge.",
        r"Rolling updates: \texttt{RollingUpdate} strategy with "
          r"\texttt{maxUnavailable=0} ensures zero-downtime deployments.",
        r"Namespace isolation: resource quotas, NetworkPolicy, "
          r"separate ServiceAccounts per namespace.",
    ],
    tech_data_flow=r"""
\texttt{kubectl apply -f manifest.yaml} →
k3s API server → controller manager →
kubelet on node → containerd pull (ECR) →
Pod Running → Traefik route active → HTTPS traffic.
""",
    tech_dependencies=r"""
\begin{tabular}{ll}
\toprule
\textbf{Component} & \textbf{Technology} \\
\midrule
Kubernetes distribution & k3s v1.29 \\
Container registry & AWS ECR (eu-west-3) \\
Ingress & Traefik v2 \\
TLS & Let's Encrypt (ACME) \\
Container runtime & containerd \\
Host OS & Ubuntu 22.04 LTS \\
IaC & Bash scripts + rendered YAML manifests \\
\bottomrule
\end{tabular}
""",
    tech_design_decisions=r"""
\begin{itemize}
  \item k3s chosen over full k8s: single binary, low RAM footprint ($< 512$~MB),
    ideal for a single-node OVH VPS.
  \item Rendered manifests (not Helm): simpler auditability, no templating engine
    dependency, version-controlled YAML as the source of truth.
  \item Date-based image tags: straightforward rollback without a semver registry.
\end{itemize}
""",
    learn_prereqs="Linux sysadmin basics, networking (TCP/IP, DNS, TLS), Docker fundamentals, basic YAML.",
    learn_coursera=[
        {"title": "Google Kubernetes Engine (GKE) Fundamentals", "provider": "Google Cloud",
         "url": "https://www.coursera.org/learn/google-kubernetes-engine",
         "why": "Core k8s concepts directly applicable to k3s."},
        {"title": "Site Reliability Engineering: Measuring and Managing Reliability",
         "provider": "Google SRE", "url": "https://www.coursera.org/learn/site-reliability-engineering-slos",
         "why": "SLO/SLA thinking for operating production clusters."},
    ],
    learn_pluralsight=[
        {"title": "Kubernetes for Developers: Core Concepts", "provider": "Pluralsight",
         "url": "https://www.pluralsight.com/courses/kubernetes-developers-core-concepts",
         "why": "Pods, Deployments, Services, Ingress — all used in this repo."},
        {"title": "Managing Kubernetes Controllers and Deployments", "provider": "Pluralsight",
         "url": "https://www.pluralsight.com/courses/managing-kubernetes-controllers-deployments",
         "why": "Rolling updates, StatefulSets, DaemonSets."},
    ],
    learn_acg=[
        {"title": "Kubernetes Deep Dive", "provider": "A Cloud Guru",
         "url": "https://acloudguru.com/course/kubernetes-deep-dive",
         "why": "Advanced scheduling, RBAC, networking — production-grade k8s."},
        {"title": "AWS Certified Solutions Architect – Associate", "provider": "A Cloud Guru",
         "url": "https://acloudguru.com/course/aws-certified-solutions-architect-associate",
         "why": "ECR, IAM roles for image pull secrets."},
    ],
    learn_github=[
        {"title": "k3s-io/k3s", "url": "https://github.com/k3s-io/k3s",
         "why": "k3s source; read issues for known limitations on single-node deployments."},
        {"title": "traefik/traefik", "url": "https://github.com/traefik/traefik",
         "why": "Ingress controller; middleware, routers, TLS configuration."},
        {"title": "kelseyhightower/kubernetes-the-hard-way",
         "url": "https://github.com/kelseyhightower/kubernetes-the-hard-way",
         "why": "Understand what k3s automates; foundational knowledge."},
    ],
    learn_books=[
        {"title": "Kubernetes in Action", "authors": "Marko Luksa, 2nd ed.",
         "url": "https://www.manning.com/books/kubernetes-in-action-second-edition",
         "why": "Comprehensive k8s reference — architecture, internals, operations."},
        {"title": "The DevOps Handbook", "authors": "Kim, Humble, Debois, Willis",
         "url": "https://itrevolution.com/product/the-devops-handbook/",
         "why": "CI/CD, deployment pipelines, and operational excellence."},
    ],
),

# ─────────────────────────────────────────────
RepoDoc(
    name="tradejournal",
    title="Trade Journal",
    subtitle="AI-Powered Trading Journal with REST API and Analytics Dashboard",
    description=(
        "Trading journal application with FastAPI backend, React dashboard, "
        "AI trade analysis service, and PostgreSQL persistence."
    ),
    tech_overview=r"""
Trade Journal provides a structured record of all executed trades enriched
with AI-powered analysis. The system ingests NT8 trade logs, stores them in
PostgreSQL, and offers an AI service that identifies patterns, calculates
statistics, and generates textual summaries via an LLM.

The architecture follows a three-tier pattern:
\begin{enumerate}
  \item \textbf{API layer}: FastAPI REST endpoints for CRUD operations on trades.
  \item \textbf{AI service}: Python service calling an LLM (via LiteLLM) to generate
    trade analysis, pattern recognition, and improvement suggestions.
  \item \textbf{Dashboard}: React frontend for visualisation and journalling UI.
\end{enumerate}
""",
    tech_architecture=r"""
\begin{verbatim}
NT8 trade export (CSV/SQL)
    │
    ▼
FastAPI API ──► PostgreSQL
    │                │
    ▼                ▼
AI Service ──► LiteLLM ──► LLM (Claude/GPT-4)
    │
    ▼
React Dashboard (charts, stats, AI summaries)
\end{verbatim}
""",
    tech_key_concepts=[
        r"REST API design: resource-based URLs, HTTP verbs (GET/POST/PUT/DELETE), "
          r"Pydantic schema validation, OpenAPI/Swagger auto-generation.",
        r"SQL query patterns: window functions for running PnL, "
          r"GROUP BY for per-symbol/per-day aggregates, "
          r"CTE for complex multi-step calculations.",
        r"LLM-based analysis: system prompt engineering for trading analysis; "
          r"structured output (JSON) for machine-parseable insight extraction.",
        r"MCP (Model Context Protocol): tool-based LLM integration pattern "
          r"for database query execution from within LLM reasoning.",
    ],
    tech_data_flow=r"""
NT8 export → \texttt{convert\_trade\_logs\_to\_sql.py} →
PostgreSQL → FastAPI \texttt{/trades} →
AI service \texttt{/analyse} → LiteLLM prompt →
LLM response → structured JSON → Dashboard chart.
""",
    tech_dependencies=r"""
\begin{tabular}{ll}
\toprule
\textbf{Component} & \textbf{Technology} \\
\midrule
Backend API & FastAPI, SQLAlchemy, Pydantic \\
Database & PostgreSQL 15 \\
AI service & LiteLLM, Python 3.11 \\
Frontend & React, Chart.js / Recharts \\
Container & Docker Compose \\
\bottomrule
\end{tabular}
""",
    tech_design_decisions=r"""
\begin{itemize}
  \item Separate AI microservice: LLM calls are expensive and latency-variable;
    isolating them prevents API timeouts from blocking CRUD operations.
  \item MCP protocol: enables the LLM to query the database directly for
    context-aware analysis without pre-loading all data into the prompt.
\end{itemize}
""",
    learn_prereqs="Python, SQL (joins, aggregates), React basics, REST API concepts.",
    learn_coursera=[
        {"title": "Full Stack Development with React", "provider": "Meta",
         "url": "https://www.coursera.org/professional-certificates/meta-full-stack-developer",
         "why": "React, REST integration, state management."},
        {"title": "Databases and SQL for Data Science", "provider": "IBM",
         "url": "https://www.coursera.org/learn/sql-data-science",
         "why": "SQL patterns used extensively for trade analytics."},
    ],
    learn_pluralsight=[
        {"title": "Building Web APIs with FastAPI", "provider": "Pluralsight",
         "url": "https://www.pluralsight.com/courses/building-web-apis-fastapi",
         "why": "Direct framework match."},
        {"title": "React: The Big Picture", "provider": "Pluralsight",
         "url": "https://www.pluralsight.com/courses/react-big-picture",
         "why": "Component model, hooks, state — used in dashboard."},
    ],
    learn_acg=[
        {"title": "Introduction to Cloud Computing", "provider": "A Cloud Guru",
         "url": "https://acloudguru.com/course/introduction-to-cloud-computing",
         "why": "Cloud-native deployment patterns used for this service."},
    ],
    learn_github=[
        {"title": "tiangolo/full-stack-fastapi-template",
         "url": "https://github.com/tiangolo/full-stack-fastapi-template",
         "why": "Official FastAPI + React project template; patterns to adopt."},
        {"title": "modelcontextprotocol/python-sdk",
         "url": "https://github.com/modelcontextprotocol/python-sdk",
         "why": "MCP SDK used in the AI service for database tool integration."},
    ],
    learn_books=[
        {"title": "FastAPI: Modern Python Web Development", "authors": "Bill Lubanovic",
         "url": "https://www.oreilly.com/library/view/fastapi/9781098135492/",
         "why": "Async FastAPI patterns, SQLAlchemy integration."},
    ],
),

# ─────────────────────────────────────────────
RepoDoc(
    name="litellm-gateway-vps",
    title="LiteLLM Gateway on VPS",
    subtitle="Multi-Provider LLM API Gateway with Apache Reverse Proxy",
    description=(
        "Self-hosted LiteLLM proxy gateway routing LLM requests to multiple providers "
        "(Claude, GPT-4, Mistral) via Apache HTTPS reverse proxy on OVH VPS."
    ),
    tech_overview=r"""
LiteLLM Gateway provides a unified OpenAI-compatible REST API that routes
requests to multiple LLM providers. All platform services (rl-agent, AI service,
market insights) use a single endpoint, allowing model switching without code changes.

The gateway runs as a Docker container behind an Apache HTTPS reverse proxy
with Let's Encrypt TLS certificates, and is also deployed as a k8s service
in the Doctum cluster.
""",
    tech_architecture=r"""
\begin{verbatim}
Clients (rl-agent, ai-service, market-insights)
    │ HTTPS POST /chat/completions
    ▼
Apache httpd (TLS termination)
    │ HTTP proxy_pass
    ▼
LiteLLM container (port 4000)
    ├── route: claude-3-5-sonnet → Anthropic API
    ├── route: gpt-4o → OpenAI API
    └── route: mistral-large → Mistral API
\end{verbatim}
""",
    tech_key_concepts=[
        r"API proxying: LiteLLM translates OpenAI-format requests to "
          r"provider-specific formats; unified \texttt{/chat/completions} interface.",
        r"Bearer token auth: \texttt{Authorization: Bearer sk-...} header; "
          r"virtual keys per service for rate limiting and audit.",
        r"Apache \texttt{mod\_proxy}: \texttt{ProxyPass}, \texttt{ProxyPassReverse}; "
          r"TLS termination with \texttt{mod\_ssl}.",
        r"Rate limiting and cost control: LiteLLM budget manager; "
          r"per-key spend limits; fallback model chains.",
    ],
    tech_data_flow=r"""
Client POST → Apache TLS → LiteLLM \texttt{/chat/completions} →
provider routing → API call → response transform → client.
""",
    tech_dependencies=r"""
\begin{tabular}{ll}
\toprule
\textbf{Component} & \textbf{Technology} \\
\midrule
LLM proxy & LiteLLM $\geq$ 1.40 \\
Reverse proxy & Apache httpd 2.4 \\
TLS & Let's Encrypt / certbot \\
Container & Docker, Docker Compose \\
k8s deployment & k3s Deployment + Service + Ingress \\
\bottomrule
\end{tabular}
""",
    tech_design_decisions=r"""
\begin{itemize}
  \item Single gateway endpoint: service code never imports provider SDKs directly;
    switching from Claude to GPT-4 requires one config change.
  \item Apache chosen over nginx: existing OVH VPS Apache installation;
    \texttt{mod\_proxy} is mature and well-documented.
\end{itemize}
""",
    learn_prereqs="HTTP/HTTPS basics, REST APIs, Docker, Linux system administration.",
    learn_coursera=[
        {"title": "Google Cloud Fundamentals: Core Infrastructure", "provider": "Google",
         "url": "https://www.coursera.org/learn/gcp-fundamentals",
         "why": "Cloud networking, load balancing, reverse proxy patterns."},
    ],
    learn_pluralsight=[
        {"title": "Linux Foundation: Networking Fundamentals", "provider": "Pluralsight",
         "url": "https://www.pluralsight.com/courses/linux-networking-fundamentals",
         "why": "Apache proxy configuration, TCP/IP, TLS."},
    ],
    learn_acg=[
        {"title": "AWS Certified Cloud Practitioner", "provider": "A Cloud Guru",
         "url": "https://acloudguru.com/course/aws-certified-cloud-practitioner",
         "why": "Cloud fundamentals; IAM for API key management."},
    ],
    learn_github=[
        {"title": "BerriAI/litellm", "url": "https://github.com/BerriAI/litellm",
         "why": "LiteLLM source; config syntax, virtual keys, budget management."},
    ],
    learn_books=[
        {"title": "The Linux Command Line", "authors": "William Shotts",
         "url": "https://linuxcommand.org/tlcl.php",
         "why": "System administration skills needed for VPS operations."},
    ],
),

# ─────────────────────────────────────────────
RepoDoc(
    name="market_screener",
    title="Market Screener",
    subtitle="Multi-Source Stock Screener with Airflow Pipeline and AI Analysis",
    description=(
        "Automated stock screener with intraday and nightly Airflow pipelines, "
        "FastAPI backend, Yahoo Finance and Alpaca connectors, and AI-powered analysis."
    ),
    tech_overview=r"""
Market Screener automates the identification of trading opportunities by
running configurable screening rules across a universe of instruments.
Two Airflow pipelines run on distinct schedules: intraday (real-time signals)
and nightly (batch scoring and database refresh).

The backend exposes a REST API for queried results, and the AI analysis
module generates natural-language summaries of screener output.
""",
    tech_architecture=r"""
\begin{verbatim}
Airflow Scheduler
├── Intraday DAG  → Yahoo Finance / Alpaca fetch
│                 → Apply screening rules
│                 → Write to PostgreSQL
└── Nightly DAG   → Historical scoring
                  → AI analysis (LiteLLM)
                  → Dashboard refresh

FastAPI backend ──► PostgreSQL ──► React frontend
\end{verbatim}
""",
    tech_key_concepts=[
        r"Technical indicators: RSI $= 100 - \frac{100}{1 + RS}$ where $RS = \frac{\text{avg gain}}{\text{avg loss}}$; "
          r"MACD $= \text{EMA}_{12} - \text{EMA}_{26}$; "
          r"Bollinger Bands $= \mu \pm 2\sigma$ over rolling window.",
        r"Airflow DAG design: idempotent tasks, catchup=False for live data, "
          r"task retries with exponential backoff.",
        r"Database schema: time-series table with (symbol, timestamp, OHLCV, indicators); "
          r"partitioned by date for query performance.",
        r"Screening rules: configurable filter chains; "
          r"e.g.\ RSI $< 30$ AND price $>$ 50-day MA AND volume spike.",
    ],
    tech_data_flow=r"""
Airflow DAG trigger → Yahoo Finance REST → OHLCV normalisation →
Technical indicator calculation → Screening rule application →
PostgreSQL upsert → FastAPI read → React display.
""",
    tech_dependencies=r"""
\begin{tabular}{ll}
\toprule
\textbf{Component} & \textbf{Technology} \\
\midrule
Orchestration & Apache Airflow 2.x \\
Data sources & yfinance, Alpaca Market Data API \\
Indicators & pandas-ta, TA-Lib \\
Database & PostgreSQL \\
API & FastAPI \\
AI analysis & LiteLLM \\
\bottomrule
\end{tabular}
""",
    tech_design_decisions=r"""
\begin{itemize}
  \item Two separate DAGs (intraday vs.\ nightly) to isolate latency-sensitive
    real-time paths from batch operations.
  \item yfinance as primary source (free); Alpaca as fallback for real-time data
    requiring an API key.
\end{itemize}
""",
    learn_prereqs="Python, pandas, SQL, basic technical analysis knowledge.",
    learn_coursera=[
        {"title": "Introduction to Portfolio Construction and Analysis with Python",
         "provider": "EDHEC Business School",
         "url": "https://www.coursera.org/learn/introduction-portfolio-construction-python",
         "why": "Portfolio statistics, risk metrics, technical analysis in Python."},
        {"title": "Financial Engineering and Risk Management", "provider": "Columbia University",
         "url": "https://www.coursera.org/specializations/financialengineering",
         "why": "Quantitative finance foundations for screener rule design."},
    ],
    learn_pluralsight=[
        {"title": "Data Analysis with pandas", "provider": "Pluralsight",
         "url": "https://www.pluralsight.com/courses/data-analysis-pandas",
         "why": "DataFrame operations used extensively for indicator calculation."},
    ],
    learn_acg=[],
    learn_github=[
        {"title": "twopirllc/pandas-ta", "url": "https://github.com/twopirllc/pandas-ta",
         "why": "Technical analysis library used for indicator calculation."},
        {"title": "ranaroussi/yfinance", "url": "https://github.com/ranaroussi/yfinance",
         "why": "Yahoo Finance connector used as primary data source."},
    ],
    learn_books=[
        {"title": "Python for Finance", "authors": "Yves Hilpisch, 2nd ed.",
         "url": "https://www.oreilly.com/library/view/python-for-finance/9781492024323/",
         "why": "Pandas, NumPy, data visualisation for financial data."},
    ],
),

# ─────────────────────────────────────────────
RepoDoc(
    name="NT8Bridge-Multi",
    title="NT8 Bridge Multi",
    subtitle="NinjaTrader 8 WebSocket Bridge for Multi-Account Execution",
    description=(
        "C# NinjaTrader 8 AddOn that bridges NT8 order execution to external "
        "systems via WebSocket, supporting multi-account signal distribution."
    ),
    tech_overview=r"""
NT8Bridge-Multi implements a NinjaTrader~8 AddOn (C\#/.NET) that exposes
a WebSocket server within the NT8 process. External Python clients connect
to receive real-time market events (ticks, bars, order fills) and send
order instructions back to NT8 for execution.

This enables the rl-agent to control NT8 trading accounts programmatically
without screen automation.
""",
    tech_architecture=r"""
\begin{verbatim}
NinjaTrader 8 process
└── NT8WebSocketBridgeAddOn (C#)
    ├── WebSocket server (port 6789)
    │   ├── Publish: ticks, bars, fills, account state
    │   └── Subscribe: order commands (buy/sell/cancel)
    └── NT8 API (NinjaTrader.Core)

Python client (rl-agent / doctum-trading)
    └── websockets library → JSON messages
\end{verbatim}
""",
    tech_key_concepts=[
        r"NinjaTrader AddOn API: \texttt{NinjaTrader.NinjaScript.AddOnBase}; "
          r"event callbacks \texttt{OnConnectionStatusUpdate}, \texttt{OnExecutionUpdate}.",
        r"WebSocket protocol (RFC 6455): full-duplex TCP channel; "
          r"frame types (text, binary, ping/pong, close); "
          r"message framing and masking.",
        r"Multi-account routing: each connected client can target a specific "
          r"NT8 account by name; the bridge dispatches orders accordingly.",
        r"Thread safety: NT8 callbacks execute on the NT8 dispatcher thread; "
          r"WebSocket sends must be marshalled to avoid cross-thread exceptions.",
        r"Message schema: JSON envelopes with \texttt{type}, \texttt{account}, "
          r"\texttt{symbol}, \texttt{action}, \texttt{qty} fields.",
    ],
    tech_data_flow=r"""
NT8 bar/tick event → AddOn callback →
JSON serialise → WebSocket broadcast →
Python client receive → parse →
rl-agent decision → JSON order command →
WebSocket send → AddOn receive →
NT8 \texttt{SubmitOrderManaged()} call.
""",
    tech_dependencies=r"""
\begin{tabular}{ll}
\toprule
\textbf{Component} & \textbf{Technology} \\
\midrule
NT8 AddOn & C\# .NET 4.8, NinjaTrader.Core \\
WebSocket server & \texttt{System.Net.WebSockets} \\
Python client & \texttt{websockets} library \\
Protocol & JSON over WebSocket (ws://) \\
Platform & Windows 10/11 (NT8 requirement) \\
\bottomrule
\end{tabular}
""",
    tech_design_decisions=r"""
\begin{itemize}
  \item WebSocket over named pipes: simpler cross-process and cross-machine communication.
  \item JSON over binary protocol: human-readable for debugging; low latency
    acceptable for swing/day trading (not HFT).
  \item Publisher/Subscriber pattern: the bridge publishes all events;
    clients filter by symbol or account.
\end{itemize}
""",
    learn_prereqs="C# .NET basics, event-driven programming, TCP networking, JSON serialisation.",
    learn_coursera=[
        {"title": "C# Programming for Unity Game Development", "provider": "University of Colorado",
         "url": "https://www.coursera.org/specializations/programming-unity-game-development",
         "why": "C# fundamentals, events, delegates — patterns used in NT8 AddOn."},
    ],
    learn_pluralsight=[
        {"title": "C# Fundamentals", "provider": "Pluralsight",
         "url": "https://www.pluralsight.com/courses/csharp-fundamentals-dev",
         "why": "C# language features: async/await, events, generics."},
        {"title": "Asynchronous Programming in C#", "provider": "Pluralsight",
         "url": "https://www.pluralsight.com/courses/asynchronous-programming-dotnet",
         "why": "Thread marshalling, Task, async patterns critical for NT8 integration."},
    ],
    learn_acg=[],
    learn_github=[
        {"title": "NinjaTrader/NinjaTrader8API", "url": "https://ninjatrader.com/support/helpGuides/nt8/",
         "why": "Official NT8 AddOn API documentation and examples."},
        {"title": "sta/websocket-sharp", "url": "https://github.com/sta/websocket-sharp",
         "why": "Popular C# WebSocket library; alternative implementation reference."},
    ],
    learn_books=[
        {"title": "Pro C# 10 with .NET 6", "authors": "Andrew Troelsen, Phil Japikse",
         "url": "https://link.springer.com/book/10.1007/978-1-4842-7869-7",
         "why": "Comprehensive C# reference including networking and async patterns."},
    ],
),

# ─────────────────────────────────────────────
RepoDoc(
    name="text-to-3d-studio",
    title="Text-to-3D Studio",
    subtitle="Text and Image to 3D Scene Generation with Web and Electron UI",
    description=(
        "End-to-end 3D scene generation from text prompts and images using "
        "Shap-E, HunyuanDiT, and HuggingFace Space providers, "
        "with web and Electron UI, exportable artefacts (GLB, JSON)."
    ),
    tech_overview=r"""
Text-to-3D Studio provides a unified pipeline for generating 3D assets from
natural language descriptions or reference images. It abstracts multiple
generation backends behind a common provider interface and exposes the
pipeline via a FastAPI REST API consumed by both a web frontend and an
Electron desktop application.

Key design constraints:
\begin{itemize}
  \item A downloaded model must be immediately usable (\texttt{runtime\_ready=true}).
  \item Generation must produce verifiable exportable artefacts (\texttt{scene.json}, \texttt{scene.glb}).
  \item Download progress must be visible in the UI.
  \item Errors must be explicit and actionable.
\end{itemize}
""",
    tech_architecture=r"""
\begin{verbatim}
Text/Image prompt
    │
    ▼
FastAPI  ──► Provider Registry
(app/)       ├── ShapEProvider   (local GPU)
             ├── HunyuanProvider (local GPU)
             ├── HFSpaceProvider (API)
             └── CloudProvider   (API)
    │
    ▼
scene.glb + scene.json (artefacts)
    │
    ├── Web frontend (Vite/React)
    └── Electron desktop app
\end{verbatim}
""",
    tech_key_concepts=[
        r"Shap-E (OpenAI): implicit neural representation (NeRF/SDF) conditioned on "
          r"text/image; two-stage: latent generation then rendering to 3D mesh.",
        r"NeRF (Neural Radiance Fields): volumetric scene representation; "
          r"$F_\Theta: (\mathbf{x}, \mathbf{d}) \to (\mathbf{c}, \sigma)$; "
          r"differentiable volume rendering.",
        r"GLB format: binary glTF 2.0 container; PBR materials, animations, "
          r"vertex buffers — standard for 3D web and real-time engines.",
        r"Provider pattern: abstract base class \texttt{Base3DProvider}; "
          r"runtime dispatch via \texttt{ProviderRegistry}; "
          r"enables hot-swap of backends without API changes.",
        r"GPU guard: runtime check for CUDA availability; "
          r"graceful CPU fallback with performance warning.",
        r"Electron + web dual target: shared React components; "
          r"IPC bridge for native file system access in Electron.",
    ],
    tech_data_flow=r"""
\texttt{POST /generate} (text + image) →
GPU guard check → provider dispatch →
model inference (latent $\to$ mesh) →
trimesh export to GLB →
\texttt{scene.json} metadata write →
SSE progress stream to UI →
\texttt{GET /artefacts/\{id\}} download.
""",
    tech_dependencies=r"""
\begin{tabular}{ll}
\toprule
\textbf{Component} & \textbf{Technology} \\
\midrule
3D generation & Shap-E (OpenAI), HunyuanDiT \\
3D mesh & trimesh, PyMeshLab \\
Deep learning & PyTorch $\geq$ 2.0 \\
Backend API & FastAPI \\
Frontend & React (Vite), Three.js \\
Desktop & Electron \\
Export formats & GLB (glTF 2.0), JSON \\
\bottomrule
\end{tabular}
""",
    tech_design_decisions=r"""
\begin{itemize}
  \item Provider registry pattern: decouples API from model; adding a new backend
    requires only a new class implementing \texttt{Base3DProvider.generate()}.
  \item GLB as primary export: widest tool support (Blender, Three.js, Unity, Unreal).
  \item SSE for progress: lightweight server-sent events avoid WebSocket complexity
    for one-directional progress reporting.
\end{itemize}
""",
    learn_prereqs="Python, PyTorch basics, 3D graphics fundamentals (vertices, meshes), React basics.",
    learn_coursera=[
        {"title": "Deep Learning Specialization", "provider": "DeepLearning.AI",
         "url": "https://www.coursera.org/specializations/deep-learning",
         "why": "Neural networks, CNNs, generative models — foundations for 3D generation."},
        {"title": "Computer Vision Basics", "provider": "University at Buffalo",
         "url": "https://www.coursera.org/learn/computer-vision-basics",
         "why": "Image representations, 3D from 2D, camera models."},
    ],
    learn_pluralsight=[
        {"title": "3D Graphics Fundamentals", "provider": "Pluralsight",
         "url": "https://www.pluralsight.com/courses/3d-graphics-fundamentals",
         "why": "Meshes, materials, rendering pipelines — essential for GLB output."},
        {"title": "Building Desktop Apps with Electron", "provider": "Pluralsight",
         "url": "https://www.pluralsight.com/courses/electron-building-cross-platform-desktop-apps",
         "why": "Electron architecture, IPC, native file access."},
    ],
    learn_acg=[],
    learn_github=[
        {"title": "openai/shap-e", "url": "https://github.com/openai/shap-e",
         "why": "Primary generation backend; understand NeRF-to-mesh pipeline."},
        {"title": "mikedh/trimesh", "url": "https://github.com/mikedh/trimesh",
         "why": "Mesh processing and GLB export library."},
        {"title": "mrdoob/three.js", "url": "https://github.com/mrdoob/three.js",
         "why": "3D rendering in the web frontend; GLB loader patterns."},
        {"title": "tencent/HunyuanDiT", "url": "https://github.com/Tencent/HunyuanDiT",
         "why": "Alternative generation backend in the provider registry."},
    ],
    learn_books=[
        {"title": "Computer Graphics: Principles and Practice", "authors": "Hughes et al., 3rd ed.",
         "url": "https://www.cs.brandeis.edu/~cs155/CG3e.html",
         "why": "Foundational 3D geometry, rendering, transformations."},
    ],
),

# ─────────────────────────────────────────────
RepoDoc(
    name="guardrails-kit",
    title="Guardrails Kit",
    subtitle="Multi-Repo AI Assistant Policy and Engineering Standards Framework",
    description=(
        "Canonical guardrails, templates, and agents for 13 downstream repositories. "
        "Ensures consistent code documentation, secret management, and deployment standards "
        "across GitHub Copilot, Claude Code, and Gemini CLI."
    ),
    tech_overview=r"""
Guardrails Kit is a meta-repository that defines and enforces engineering standards
across an entire GitHub organisation. It provides:
\begin{itemize}
  \item Policy documents in \texttt{.guardrails/rules/}
  \item AI assistant configuration templates (Copilot, Claude, Gemini)
  \item A Bash/PowerShell validator script for CI enforcement
  \item GitHub Actions workflow for automated gate checks
  \item Installation scripts for downstream repos
\end{itemize}
The multi-AI design ensures that whether a contributor uses GitHub Copilot,
Claude Code, or Gemini CLI, the same guardrails are applied.
""",
    tech_architecture=r"""
\begin{verbatim}
guardrails-kit (canonical source)
├── templates/
│   ├── copilot-instructions.template.md  → .github/copilot-instructions.md
│   ├── CLAUDE.template.md                → CLAUDE.md
│   └── GEMINI.template.md                → GEMINI.md
├── .guardrails/
│   ├── rules/*.md         (policy documents)
│   └── bin/validate_guardrails.sh
└── scripts/
    ├── install_into_repo.sh   (Ubuntu/macOS)
    └── install_into_repo.ps1  (Windows)

Downstream repos (×13)
├── .github/copilot-instructions.md
├── CLAUDE.md
├── GEMINI.md
└── .github/agents/ecr-secrets-agent.agent.md
\end{verbatim}
""",
    tech_key_concepts=[
        r"Infrastructure-as-Policy: treating engineering standards as versioned, "
          r"testable artefacts rather than wiki pages.",
        r"AI assistant instruction files: \texttt{.github/copilot-instructions.md} "
          r"is loaded by GitHub Copilot; \texttt{CLAUDE.md} by Claude Code; "
          r"\texttt{GEMINI.md} by Gemini CLI at session start.",
        r"CI gate pattern: \texttt{validate\_guardrails.sh} checks required docs, "
          r"doc-update rules, and optional lint/test/build commands as a pre-merge gate.",
        r"Template propagation: \texttt{install\_into\_repo.sh} substitutes "
          r"\texttt{\{\{PROJECT\_NAME\}\}} placeholder and copies files; "
          r"idempotent with \texttt{--force} flag.",
        r"Platform compatibility: all scripts provide Ubuntu (Bash), "
          r"Windows (PowerShell), and macOS (zsh/bash) variants.",
    ],
    tech_data_flow=r"""
guardrails-kit template update →
\texttt{scripts/install\_into\_repo.sh /path/to/repo} →
file copy + placeholder substitution →
\texttt{git add + commit} in target repo →
GitHub Actions \texttt{Guardrails} check passes.
""",
    tech_dependencies=r"""
\begin{tabular}{ll}
\toprule
\textbf{Component} & \textbf{Technology} \\
\midrule
Shell scripting & Bash 5, PowerShell 7 \\
CI & GitHub Actions \\
AI assistants & GitHub Copilot, Claude Code, Gemini CLI \\
Markdown & CommonMark (instruction files) \\
LaTeX & pdflatex (documentation) \\
\bottomrule
\end{tabular}
""",
    tech_design_decisions=r"""
\begin{itemize}
  \item Single source of truth: all 13 repos pull standards from one place;
    a policy change propagates to all repos in one \texttt{install} pass.
  \item Three AI file targets: avoids vendor lock-in; contributors can use
    whichever AI assistant they prefer without losing guardrail enforcement.
  \item Validator checks staged files: integrates cleanly with pre-commit hooks
    and GitHub Actions \texttt{on: pull\_request} trigger.
\end{itemize}
""",
    learn_prereqs="Bash scripting, Git, YAML/Markdown, GitHub Actions basics.",
    learn_coursera=[
        {"title": "DevOps on AWS Specialization", "provider": "Amazon Web Services",
         "url": "https://www.coursera.org/specializations/aws-devops",
         "why": "CI/CD pipelines, infrastructure-as-code, deployment automation."},
    ],
    learn_pluralsight=[
        {"title": "GitHub Actions: The Big Picture", "provider": "Pluralsight",
         "url": "https://www.pluralsight.com/courses/github-actions-big-picture",
         "why": "Workflow syntax, secrets, job dependencies — used in guardrails CI."},
        {"title": "Shell Scripting with Bash", "provider": "Pluralsight",
         "url": "https://www.pluralsight.com/courses/bash-shell-scripting",
         "why": "Advanced Bash: heredocs, associative arrays, subshells."},
    ],
    learn_acg=[
        {"title": "DevOps Essentials", "provider": "A Cloud Guru",
         "url": "https://acloudguru.com/course/devops-essentials",
         "why": "CI/CD, IaC, GitOps — all relevant to guardrails propagation."},
    ],
    learn_github=[
        {"title": "github/super-linter", "url": "https://github.com/github/super-linter",
         "why": "Multi-language linting in GitHub Actions — extend guardrails CI."},
        {"title": "pre-commit/pre-commit", "url": "https://github.com/pre-commit/pre-commit",
         "why": "Pre-commit hook framework; integrate validate_guardrails.sh as a hook."},
    ],
    learn_books=[
        {"title": "The Phoenix Project", "authors": "Kim, Behr, Spafford",
         "url": "https://itrevolution.com/product/the-phoenix-project/",
         "why": "DevOps culture and principles behind guardrails thinking."},
    ],
),

# ─────────────────────────────────────────────
RepoDoc(
    name="streetfighter-enhanced_syno",
    title="Street Fighter Enhanced (Synology)",
    subtitle="Browser-Based Street Fighter Game — Cocos2d-HTML5",
    description=(
        "Enhanced browser port of a Street Fighter game built with Cocos2d-HTML5 "
        "framework, featuring sprite animation, physics, and Synology NAS deployment."
    ),
    tech_overview=r"""
A browser-based 2D fighting game implemented with Cocos2d-HTML5 v3.
The game features sprite-sheet animation, collision detection, physics
simulation, and a multi-layer canvas rendering architecture.
It is containerised with Docker and served as a static web application.
""",
    tech_architecture=r"""
\begin{verbatim}
Browser (Canvas2D / WebGL)
└── Cocos2d-HTML5 runtime
    ├── Scene graph (Layer tree)
    │   ├── BackgroundLayer
    │   ├── AnimationLayer (fighters)
    │   └── StatusLayer (health bars)
    ├── Fighter.js      (state machine)
    ├── FighterPhysics.js (gravity, collision)
    └── Projectile.js   (hadouken physics)
\end{verbatim}
""",
    tech_key_concepts=[
        r"Sprite sheet animation: texture atlas (plist) maps named frames to "
          r"UV coordinates; \texttt{cc.AnimationCache} manages frame sequences.",
        r"Scene graph: hierarchical node tree; each node has position, scale, "
          r"rotation, opacity; parent transforms propagate to children.",
        r"Finite state machine (FSM): fighter states "
          r"(idle, walking, jumping, attacking, stunned, KO); "
          r"transitions triggered by input or collision events.",
        r"AABB collision detection: axis-aligned bounding box overlap; "
          r"$\text{overlap} = \text{rect}_A.\text{intersects}(\text{rect}_B)$.",
        r"Game loop: \texttt{cc.scheduler} drives \texttt{update(dt)} at 60~fps; "
          r"delta-time normalised physics for frame-rate independence.",
    ],
    tech_data_flow=r"""
Input event (keyboard/touch) →
Fighter FSM transition →
Physics update (gravity, velocity integration) →
Collision detection →
Animation frame selection →
Canvas render.
""",
    tech_dependencies=r"""
\begin{tabular}{ll}
\toprule
\textbf{Component} & \textbf{Technology} \\
\midrule
Game framework & Cocos2d-HTML5 v3 \\
Rendering & Canvas2D / WebGL \\
Asset format & PNG sprite sheets + plist atlases \\
Server & nginx (Docker) \\
\bottomrule
\end{tabular}
""",
    tech_design_decisions=r"""
\begin{itemize}
  \item Cocos2d-HTML5 chosen for its mature sprite/animation API
    and cross-browser Canvas/WebGL abstraction.
  \item Static file serving via nginx: no backend required,
    minimal operational overhead on Synology NAS.
\end{itemize}
""",
    learn_prereqs="JavaScript ES5/ES6, HTML/CSS, basic game loop concepts.",
    learn_coursera=[
        {"title": "HTML, CSS, and Javascript for Web Developers", "provider": "Johns Hopkins",
         "url": "https://www.coursera.org/learn/html-css-javascript-for-web-developers",
         "why": "Core web skills for browser-based game development."},
    ],
    learn_pluralsight=[
        {"title": "JavaScript: Getting Started", "provider": "Pluralsight",
         "url": "https://www.pluralsight.com/courses/javascript-getting-started",
         "why": "ES6 classes, closures, prototype chain — used throughout the game code."},
    ],
    learn_acg=[],
    learn_github=[
        {"title": "cocos2d/cocos2d-html5", "url": "https://github.com/cocos2d/cocos2d-html5",
         "why": "Framework source; scene graph, animation, physics internals."},
        {"title": "GDquest/godot-2d-game-creation-course", "url": "https://github.com/GDquest/godot-2d-game-creation-course",
         "why": "Modern 2D game development patterns (FSM, physics, animation) in a different engine."},
    ],
    learn_books=[
        {"title": "Learning Cocos2d-x Game Development", "authors": "Siddharth Shekar",
         "url": "https://www.packtpub.com/product/learning-cocos2d-x-game-development/9781784399849",
         "why": "Cocos2d architecture, scene graph, animations."},
    ],
),

# ─────────────────────────────────────────────
RepoDoc(
    name="doctumconsilium-html5-css3-portfolio",
    title="Doctum Consilium Portfolio",
    subtitle="HTML5/CSS3 Portfolio with FastAPI Backend and Docker Deployment",
    description=(
        "Professional portfolio website with responsive HTML5/CSS3 frontend, "
        "FastAPI backend contact form, and Docker/OVH VPS deployment."
    ),
    tech_overview=r"""
A production-grade portfolio website demonstrating modern HTML5/CSS3
design, responsive layout, and a Python FastAPI backend for form handling.
Deployed on OVH VPS behind Apache with HTTPS.
""",
    tech_architecture=r"""
\begin{verbatim}
Browser
└── HTML5 / CSS3 / Vanilla JS (index.html)
    └── fetch() POST /contact
        └── FastAPI (app/main.py)
            └── Email via SMTP (env vars)
\end{verbatim}
""",
    tech_key_concepts=[
        r"CSS Grid and Flexbox: two-dimensional layout (Grid) vs. one-dimensional (Flexbox); "
          r"responsive design with \texttt{media queries}.",
        r"Semantic HTML5: \texttt{<header>}, \texttt{<main>}, \texttt{<section>}, "
          r"\texttt{<article>}, \texttt{<footer>} for accessibility and SEO.",
        r"FastAPI CORS: \texttt{CORSMiddleware} for cross-origin form submission from browser.",
        r"SMTP email: \texttt{smtplib} with TLS; credentials from environment variables "
          r"(never hardcoded).",
        r"Docker multi-stage: separate builder and runtime stages to minimise image size.",
    ],
    tech_data_flow=r"""
User fills contact form →
JS \texttt{fetch()} POST /contact →
FastAPI validates (Pydantic) →
SMTP send email →
JSON response → JS display confirmation.
""",
    tech_dependencies=r"""
\begin{tabular}{ll}
\toprule
\textbf{Component} & \textbf{Technology} \\
\midrule
Frontend & HTML5, CSS3, Vanilla JS \\
Backend & FastAPI, Python-multipart \\
Email & smtplib (SMTP TLS) \\
Deployment & Docker, Apache reverse proxy \\
\bottomrule
\end{tabular}
""",
    tech_design_decisions=r"""
\begin{itemize}
  \item Vanilla JS (no framework): portfolio page has minimal interactivity;
    zero dependency overhead, faster initial load.
  \item FastAPI for contact form: lightweight, async, automatic OpenAPI docs.
\end{itemize}
""",
    learn_prereqs="HTML, CSS, JavaScript basics.",
    learn_coursera=[
        {"title": "HTML and CSS in Depth", "provider": "Meta",
         "url": "https://www.coursera.org/learn/html-and-css-in-depth",
         "why": "Grid, Flexbox, responsive design patterns used throughout this project."},
    ],
    learn_pluralsight=[
        {"title": "CSS Flexbox Fundamentals", "provider": "Pluralsight",
         "url": "https://www.pluralsight.com/courses/css-flexbox-fundamentals-2",
         "why": "Layout model used for the portfolio sections."},
    ],
    learn_acg=[],
    learn_github=[
        {"title": "h5bp/html5-boilerplate", "url": "https://github.com/h5bp/html5-boilerplate",
         "why": "Best practices for HTML5 project structure and meta tags."},
        {"title": "tiangolo/fastapi", "url": "https://github.com/tiangolo/fastapi",
         "why": "Backend framework source and examples."},
    ],
    learn_books=[
        {"title": "CSS: The Definitive Guide", "authors": "Eric Meyer, Estelle Weyl, 5th ed.",
         "url": "https://www.oreilly.com/library/view/css-the-definitive/9781098117603/",
         "why": "Comprehensive CSS reference including Grid, Flexbox, and animations."},
    ],
),

# ─────────────────────────────────────────────
RepoDoc(
    name="site_en_construction",
    title="Site en Construction",
    subtitle="Maintenance Page for doctumconsilium.com",
    description=(
        "Simple HTML/CSS maintenance page deployed on OVH VPS with "
        "Apache toggle script for enabling/disabling maintenance mode."
    ),
    tech_overview=r"""
A minimal maintenance landing page for doctumconsilium.com.
The \texttt{toggle-maintenance.sh} script enables or disables the
maintenance redirect by swapping Apache virtual host configurations.
""",
    tech_architecture=r"""
\begin{verbatim}
Apache httpd
├── production.conf  (active → portfolio)
└── maintenance.conf (active → maintenance page)

toggle-maintenance.sh
├── disable production vhost
├── enable maintenance vhost
└── apache2ctl graceful
\end{verbatim}
""",
    tech_key_concepts=[
        r"Apache virtual hosts: \texttt{a2ensite}/\texttt{a2dissite} toggle; "
          r"graceful reload preserves in-flight connections.",
        r"HTTP 503 Service Unavailable: \texttt{Retry-After} header for crawler hints.",
        r"CSS animations: keyframe-based spinner; CSS custom properties (variables).",
    ],
    tech_data_flow=r"""
\texttt{./toggle-maintenance.sh enable} →
\texttt{a2dissite} portfolio →
\texttt{a2ensite} maintenance →
\texttt{apache2ctl graceful} →
all HTTP requests → 503 + maintenance page.
""",
    tech_dependencies=r"""
\begin{tabular}{ll}
\toprule
\textbf{Component} & \textbf{Technology} \\
\midrule
Web server & Apache httpd 2.4 \\
Toggle script & Bash \\
Frontend & HTML5, CSS3 \\
\bottomrule
\end{tabular}
""",
    tech_design_decisions=r"""
\begin{itemize}
  \item Static HTML: no backend needed; maintenance page must remain up even if
    all application services are down.
  \item Bash toggle script: zero-dependency, runnable via SSH in any emergency.
\end{itemize}
""",
    learn_prereqs="HTML/CSS basics, Apache basics, Linux command line.",
    learn_coursera=[
        {"title": "Linux Fundamentals", "provider": "LearnQuest",
         "url": "https://www.coursera.org/learn/linux-fundamentals",
         "why": "Apache management, file permissions, shell scripting."},
    ],
    learn_pluralsight=[
        {"title": "Web Server Administration with Apache", "provider": "Pluralsight",
         "url": "https://www.pluralsight.com/courses/linux-web-server",
         "why": "Virtual hosts, modules, TLS configuration."},
    ],
    learn_acg=[],
    learn_github=[
        {"title": "h5bp/server-configs-apache", "url": "https://github.com/h5bp/server-configs-apache",
         "why": "Best practice Apache config: security headers, caching, compression."},
    ],
    learn_books=[
        {"title": "Apache HTTP Server Documentation", "authors": "Apache Software Foundation",
         "url": "https://httpd.apache.org/docs/2.4/", "why": "Official authoritative reference."},
    ],
),

# ─────────────────────────────────────────────
RepoDoc(
  name="doctum-gaming-lab",
  title="Doctum Gaming Lab",
  subtitle="Full-Stack Game Platform — Backend API and Frontend Experience",
  description=(
    "Full-stack gaming platform with backend services, frontend application, "
    "containerized development workflow, and project documentation."
  ),
  tech_overview=r"""
Doctum Gaming Lab is a full-stack game-oriented project that combines
backend APIs and frontend interfaces. The repository emphasizes rapid
iteration with Docker, clear API boundaries, and consistent project guardrails.
""",
  tech_architecture=r"""
\begin{verbatim}
Frontend (web UI) <──HTTP/JSON──> Backend (API)
     │                                │
     └──────────── Docker Compose ────┘
\end{verbatim}
""",
  tech_key_concepts=[
    r"Frontend/backend separation for maintainable feature delivery.",
    r"Containerized local development for reproducible environments.",
    r"Documentation-first workflow for onboarding and consistent execution.",
  ],
  tech_data_flow=r"""
Client action → frontend request → backend handler → response payload → UI update.
""",
  tech_dependencies=r"""
\begin{tabular}{ll}
	oprule
	extbf{Component} & \textbf{Technology} \\
\midrule
Backend & Python + FastAPI (project stack) \\
Frontend & JavaScript application \\
Runtime & Docker Compose \\
\bottomrule
\end{tabular}
""",
  tech_design_decisions=r"""
\begin{itemize}
  \item Keep services decoupled to simplify parallel frontend/backend work.
  \item Use containerized workflows to reduce environment drift.
\end{itemize}
""",
  learn_prereqs="Python basics, JavaScript basics, HTTP fundamentals, Docker basics.",
  learn_coursera=[
    {"title": "Full-Stack Web Development", "provider": "Coursera",
     "url": "https://www.coursera.org/specializations/full-stack-mobile-app-development",
     "why": "Covers frontend/backend integration patterns."},
  ],
  learn_pluralsight=[
    {"title": "Building Web APIs with FastAPI", "provider": "Pluralsight",
     "url": "https://www.pluralsight.com/courses/fastapi-building-web-apis",
     "why": "API patterns aligned with backend service design."},
  ],
  learn_acg=[],
  learn_github=[
    {"title": "tiangolo/fastapi", "url": "https://github.com/tiangolo/fastapi",
     "why": "Reference implementation and patterns for FastAPI."},
  ],
  learn_books=[
    {"title": "Designing Web APIs", "authors": "Brenda Jin et al.",
     "url": "https://www.oreilly.com/library/view/designing-web-apis/9781492026914/",
     "why": "API design principles for robust service interfaces."},
  ],
),

# ─────────────────────────────────────────────
RepoDoc(
  name="doctum-arena",
  title="Doctum Arena",
  subtitle="Competitive Gaming Platform — Service and Interface Architecture",
  description=(
    "Full-stack arena project with backend application services, frontend client, "
    "and Docker-based orchestration for local and deployment workflows."
  ),
  tech_overview=r"""
Doctum Arena organizes game platform capabilities around a backend API and
frontend client. The repository structure supports iterative feature releases,
operational consistency, and shared guardrails-based standards.
""",
  tech_architecture=r"""
\begin{verbatim}
User Browser ──► Frontend App ──► Backend API ──► Service Logic
    ▲                │                │
    └────────────────┴──── Docker Compose ─────┘
\end{verbatim}
""",
  tech_key_concepts=[
    r"Service-oriented backend endpoints for game platform capabilities.",
    r"Frontend modularity for faster UI iteration and testing.",
    r"Operational reproducibility through containerized commands.",
  ],
  tech_data_flow=r"""
User input → UI event → API request → backend processing → JSON response → UI render.
""",
  tech_dependencies=r"""
\begin{tabular}{ll}
	oprule
	extbf{Component} & \textbf{Technology} \\
\midrule
Backend & Python service stack \\
Frontend & JavaScript/TypeScript app \\
Orchestration & Docker Compose \\
\bottomrule
\end{tabular}
""",
  tech_design_decisions=r"""
\begin{itemize}
  \item Keep repository structure explicit (backend/frontend/docs) for clarity.
  \item Favor simple local orchestration to reduce onboarding friction.
\end{itemize}
""",
  learn_prereqs="API basics, frontend fundamentals, Docker and Git essentials.",
  learn_coursera=[
    {"title": "Web Applications for Everybody", "provider": "University of Michigan",
     "url": "https://www.coursera.org/specializations/web-applications",
     "why": "Practical web architecture and deployment fundamentals."},
  ],
  learn_pluralsight=[
    {"title": "Docker for Developers", "provider": "Pluralsight",
     "url": "https://www.pluralsight.com/courses/docker-developers",
     "why": "Container workflows aligned with this repo."},
  ],
  learn_acg=[],
  learn_github=[
    {"title": "docker/awesome-compose", "url": "https://github.com/docker/awesome-compose",
     "why": "Reference compose patterns for multi-service apps."},
  ],
  learn_books=[
    {"title": "Web API Design", "authors": "Brian Mulloy",
     "url": "https://cloud.google.com/blog/products/api-management/api-design-best-practices",
     "why": "Concise API best practices for service contracts."},
  ],
),

# ─────────────────────────────────────────────
RepoDoc(
  name="doctum-ai-ide-mvp",
  title="Doctum AI IDE MVP",
  subtitle="AI-Enabled IDE Gateway and Extension Integration",
  description=(
    "MVP for AI-assisted development workflows integrating gateway services, "
    "editor extensions, and Dockerized runtime components."
  ),
  tech_overview=r"""
Doctum AI IDE MVP focuses on integrating AI gateway capabilities into
developer tooling. The repository combines extension artifacts, gateway code,
and operational scripts to provide an end-to-end assistant workflow.
""",
  tech_architecture=r"""
\begin{verbatim}
Editor Extension ──► Gateway Service ──► Model/Provider APIs
     │                    │
     └────── Config + Scripts + Docker ──────┘
\end{verbatim}
""",
  tech_key_concepts=[
    r"Gateway abstraction for model/provider interoperability.",
    r"Extension-driven developer UX for in-editor assistance.",
    r"Scripted startup and reproducible local execution.",
  ],
  tech_data_flow=r"""
Editor prompt → extension request → gateway routing → provider response → IDE output.
""",
  tech_dependencies=r"""
\begin{tabular}{ll}
	oprule
	extbf{Component} & \textbf{Technology} \\
\midrule
Gateway & Python/Node service layer \\
IDE Integration & Extension artifacts \\
Runtime & Docker Compose + shell scripts \\
\bottomrule
\end{tabular}
""",
  tech_design_decisions=r"""
\begin{itemize}
  \item Separate gateway logic from editor integration for portability.
  \item Keep startup scripts explicit for Linux and Windows operators.
\end{itemize}
""",
  learn_prereqs="HTTP APIs, authentication basics, editor extension concepts, Docker.",
  learn_coursera=[
    {"title": "API Design and Fundamentals of Google Cloud's Apigee API Platform",
     "provider": "Google Cloud",
     "url": "https://www.coursera.org/learn/api-design-apigee-gcp",
     "why": "Strong API gateway design foundations."},
  ],
  learn_pluralsight=[
    {"title": "Building VS Code Extensions", "provider": "Pluralsight",
     "url": "https://www.pluralsight.com/courses/building-visual-studio-code-extensions",
     "why": "Relevant patterns for IDE extension architecture."},
  ],
  learn_acg=[],
  learn_github=[
    {"title": "microsoft/vscode-extension-samples", "url": "https://github.com/microsoft/vscode-extension-samples",
     "why": "Practical extension examples and patterns."},
  ],
  learn_books=[
    {"title": "Designing APIs with Swagger and OpenAPI", "authors": "Joshua S. Ponelat et al.",
     "url": "https://www.manning.com/books/designing-apis-with-swagger-and-openapi",
     "why": "API contracts and tooling design best practices."},
  ],
),

# ─────────────────────────────────────────────
RepoDoc(
  name="doctum-code-agent",
  title="Doctum Code Agent",
  subtitle="Programmable Code-Agent Runtime and Tooling",
  description=(
    "Code-agent runtime repository with agent orchestration logic, tool bindings, "
    "and Python-based execution environment."
  ),
  tech_overview=r"""
Doctum Code Agent provides a programmable runtime for code-execution agents.
It centralizes agent orchestration, tool interfaces, and dependency management
to support automated coding workflows.
""",
  tech_architecture=r"""
\begin{verbatim}
Client Request ──► Agent Runtime ──► Tool Layer ──► Execution Output
             │
             └──── Config + Requirements
\end{verbatim}
""",
  tech_key_concepts=[
    r"Agent loop design: plan, act, observe, and report.",
    r"Tool abstraction layer for controlled capability exposure.",
    r"Dependency pinning and reproducible Python environment setup.",
  ],
  tech_data_flow=r"""
Task input → agent planner → tool invocation(s) → result aggregation → final response.
""",
  tech_dependencies=r"""
\begin{tabular}{ll}
	oprule
	extbf{Component} & \textbf{Technology} \\
\midrule
Runtime & Python 3.x \\
Agent core & Custom orchestration modules \\
Packaging & requirements.txt \\
\bottomrule
\end{tabular}
""",
  tech_design_decisions=r"""
\begin{itemize}
  \item Keep orchestration explicit to simplify debugging and traceability.
  \item Isolate tool interfaces to maintain safe extensibility.
\end{itemize}
""",
  learn_prereqs="Python intermediate, CLI workflows, software architecture basics.",
  learn_coursera=[
    {"title": "Software Design and Architecture", "provider": "University of Alberta",
     "url": "https://www.coursera.org/specializations/software-design-architecture",
     "why": "Architecture principles for robust agent runtimes."},
  ],
  learn_pluralsight=[
    {"title": "Python 3 Fundamentals", "provider": "Pluralsight",
     "url": "https://www.pluralsight.com/courses/python-3-fundamentals",
     "why": "Core Python features used by the runtime."},
  ],
  learn_acg=[],
  learn_github=[
    {"title": "langchain-ai/langchain", "url": "https://github.com/langchain-ai/langchain",
     "why": "Agent and tool-calling abstractions for comparison and inspiration."},
  ],
  learn_books=[
    {"title": "Architecture Patterns with Python", "authors": "Harry Percival and Bob Gregory",
     "url": "https://www.oreilly.com/library/view/architecture-patterns-with/9781492052197/",
     "why": "Pragmatic architecture patterns for maintainable Python systems."},
  ],
),

]


# ─────────────────────────────────────────────────────────────────────────────
# LaTeX generation functions
# ─────────────────────────────────────────────────────────────────────────────

def escape_latex(text: str) -> str:
    """Escape characters that are special in LaTeX body text."""
    # Don't escape if the text is already raw LaTeX
    return text


def build_technical_doc(repo: RepoDoc) -> str:
    """Build the full content of technical-foundations.tex for a repo."""
    item = "\\item"
    concepts_items = "\n".join(
        f"  {item} {c}" for c in repo.tech_key_concepts
    )
    return rf"""{PREAMBLE}

\begin{{document}}

\title{{
  \textcolor{{doctum}}{{\Large\textbf{{{repo.title}}}}} \\[0.5em]
  \large {repo.subtitle} \\[0.3em]
  \normalsize Technical Foundations and Architecture
}}
\author{{Doctum Consilium \\ \small\textit{{Generated 2026-05-08}}}}
\date{{}}
\maketitle
\thispagestyle{{fancy}}

\begin{{abstract}}
{repo.description}
This document covers the theoretical foundations, architectural decisions,
and key technical concepts required to understand, contribute to, and
maintain this repository.
\end{{abstract}}

\tableofcontents
\newpage

\section{{Overview}}
{repo.tech_overview}

\section{{Architecture}}
{repo.tech_architecture}

\section{{Key Technical Concepts}}
\begin{{itemize}}[leftmargin=1.5em]
{concepts_items}
\end{{itemize}}

\section{{Data Flow}}
{repo.tech_data_flow}

\section{{Technology Stack}}
{repo.tech_dependencies}

\section{{Design Decisions}}
{repo.tech_design_decisions}

\section{{Repository Structure}}
\begin{{lstlisting}}[language=bash,caption={{Top-level directory layout}}]
{repo.name}/
  .github/
    copilot-instructions.md   # GitHub Copilot guardrails
    agents/
      ecr-secrets-agent.agent.md  # ECR secret rotation runbook
  CLAUDE.md                   # Claude Code guardrails
  GEMINI.md                   # Gemini CLI guardrails
  INFRASTRUCTURE.md           # Operational runbook
  ROADMAP.md                  # Execution log and roadmap
  README.md                   # Project overview
\end{{lstlisting}}

\section{{Contributing}}
\begin{{enumerate}}
  \item Read \texttt{{README.md}}, \texttt{{INFRASTRUCTURE.md}}, and \texttt{{ROADMAP.md}} before any task.
  \item Follow the Code Documentation Standard: every public function must have
    a docstring (Google-style for Python, JSDoc for TypeScript, XML for C\#).
  \item Run the guardrails validator before committing:
    \begin{{lstlisting}}[language=bash]
git add -A && ./.guardrails/bin/validate_guardrails.sh
    \end{{lstlisting}}
  \item For deployment or destructive operations, always use a named tmux session:
    \begin{{lstlisting}}[language=bash]
tmux new-session -A -s deploy-{repo.name}
    \end{{lstlisting}}
\end{{enumerate}}

\end{{document}}
"""


def fmt_course_table(courses: List[Dict], caption: str) -> str:
    if not courses:
        return "\\textit{{No specific {} courses identified.}}\n".format(caption)
    rows = []
    for c in courses:
        row = "  {} & \\href{{{}}}{{\\texttt{{link}}}} & {} \\\\".format(c['title'], c['url'], c['why'])
        rows.append(row)
    rows_text = "\n".join(rows)
    return """\\begin{{longtable}}{{p{{6cm}} p{{1.5cm}} p{{7cm}}}}
\\toprule
\\textbf{{Course}} & \\textbf{{Link}} & \\textbf{{Why relevant}} \\\\
\\midrule
\\endhead
{}
\\bottomrule
\\caption{{{}}}
\\end{{longtable}}
""".format(rows_text, caption)


def build_learning_doc(repo: RepoDoc) -> str:
    """Build the full content of learning-resources.tex for a repo."""
    github_items = "\n".join(
        "  \\item \\href{{{}}}{{\\textbf{{{}}}}} — {}".format(r['url'], r['title'], r['why'])
        for r in repo.learn_github
    )
    books_items = "\n".join(
        "  \\item \\href{{{}}}{{\\textit{{{}}}}} — {}. {}".format(b['url'], b['title'], b['authors'], b['why'])
        for b in repo.learn_books
    )
    github_items_display = github_items if github_items else "  \\item No specific training repositories identified."
    books_items_display = books_items if books_items else "  \\item No specific books identified."
    
    return """{preamble}

\\begin{{document}}

\\title{{
  \\textcolor{{doctum}}{{\\Large\\textbf{{{title}}}}} \\\\[0.5em]
  \\large {subtitle} \\\\[0.3em]
  \\normalsize Learning Resources and Contributor Onboarding
}}
\\author{{Doctum Consilium \\\\ \\small\\textit{{Generated 2026-05-08}}}}
\\date{{}}
\\maketitle
\\thispagestyle{{fancy}}

\\begin{{abstract}}
This document provides a curated list of courses (Coursera, Pluralsight, A Cloud Guru),
training repositories, and reference books to help contributors ramp up on the
technologies used in \\textbf{{{title}}}.
Resources are selected for quality, relevance, and practical applicability.
\\end{{abstract}}

\\tableofcontents
\\newpage

\\section{{Prerequisites}}
Before starting the courses below, ensure you are comfortable with:
{prereqs}

\\section{{Coursera Courses}}
{coursera}

\\section{{Pluralsight Courses}}
{pluralsight}

\\section{{A Cloud Guru Courses}}
{acg}

\\section{{GitHub Training Repositories}}
\\begin{{itemize}}[leftmargin=1.5em]
{github}
\\end{{itemize}}

\\section{{Reference Books}}
\\begin{{itemize}}[leftmargin=1.5em]
{books}
\\end{{itemize}}

\\section{{Suggested Learning Path}}
\\begin{{enumerate}}
  \\item Complete prerequisites (1--2 weeks).
  \\item Work through the Coursera specialisation most relevant to the repo's domain (4--8 weeks).
  \\item Clone the repository, read \\texttt{{README.md}} and \\texttt{{INFRASTRUCTURE.md}}.
  \\item Run the service locally following the \\textbf{{Local Run}} section of \\texttt{{INFRASTRUCTURE.md}}.
  \\item Study the Pluralsight courses for the specific tools used (2--4 weeks, parallel).
  \\item Contribute a small fix or documentation improvement as a first PR.
  \\item Study the GitHub training repositories for advanced patterns.
\\end{{enumerate}}

\\section{{Free Resources}}
\\begin{{itemize}}
  \\item \\href{{https://docs.python.org/3/tutorial/}}{{\\textbf{{Python Official Tutorial}}}} — free, authoritative.
  \\item \\href{{https://kubernetes.io/docs/tutorials/}}{{\\textbf{{Kubernetes Interactive Tutorials}}}} — browser-based k8s labs.
  \\item \\href{{https://fastapi.tiangolo.com/tutorial/}}{{\\textbf{{FastAPI Tutorial}}}} — official, comprehensive.
  \\item \\href{{https://pytorch.org/tutorials/}}{{\\textbf{{PyTorch Tutorials}}}} — official, covers all levels.
  \\item \\href{{https://www.deeplearning.ai/short-courses/}}{{\\textbf{{DeepLearning.AI Short Courses}}}} — free, recent AI topics.
\\end{{itemize}}

\\end{{document}}
""".format(
        preamble=PREAMBLE,
        title=repo.title,
        subtitle=repo.subtitle,
        prereqs=repo.learn_prereqs,
        coursera=fmt_course_table(repo.learn_coursera, "Coursera"),
        pluralsight=fmt_course_table(repo.learn_pluralsight, "Pluralsight"),
        acg=fmt_course_table(repo.learn_acg, "A Cloud Guru"),
        github=github_items_display,
        books=books_items_display
    )


# ─────────────────────────────────────────────────────────────────────────────
# Main: write files
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    """Generate .tex files for all repos, creating docs/ directories as needed."""
    for repo in REPOS:
        repo_dir = BASE / repo.name
        if not repo_dir.exists():
            print(f"SKIP (not found): {repo.name}")
            continue

        docs_dir = repo_dir / "docs"
        docs_dir.mkdir(exist_ok=True)

        tech_path = docs_dir / "technical-foundations.tex"
        learn_path = docs_dir / "learning-resources.tex"

        tech_path.write_text(build_technical_doc(repo), encoding="utf-8")
        learn_path.write_text(build_learning_doc(repo), encoding="utf-8")

        print(f"WRITTEN: {repo.name}/docs/technical-foundations.tex")
        print(f"WRITTEN: {repo.name}/docs/learning-resources.tex")


if __name__ == "__main__":
    main()
