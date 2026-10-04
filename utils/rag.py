"""
FAISS-based RAG (Retrieval Augmented Generation) for health guidelines.
Uses local sentence-transformers embeddings - no API keys.
"""

import os
import streamlit as st
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np


@st.cache_resource(show_spinner="Loading AI embedding model...")
def load_embedding_model():
    """Load sentence-transformer model (cached)."""
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


@st.cache_resource(show_spinner="Building knowledge base index...")
def build_faiss_index(texts: list, model):
    """Build FAISS index from texts."""
    embeddings = model.encode(texts, convert_to_numpy=True)
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype("float32"))

    return index, embeddings


def load_text_file(path: str) -> list:
    """Load a text file and split into chunks by blank lines."""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    chunks = [c.strip() for c in content.split("\n\n") if c.strip()]
    return chunks


def search(query: str, chunks: list, model, index, top_k: int = 3) -> list:
    """Search FAISS index for similar chunks."""
    if not chunks:
        return []

    query_embedding = model.encode([query], convert_to_numpy=True).astype("float32")
    distances, indices = index.search(query_embedding, top_k)

    results = []
    for idx, dist in zip(indices[0], distances[0]):
        if idx < len(chunks) and idx >= 0:
            results.append({
                "text": chunks[idx],
                "score": float(dist),
            })
    return results


@st.cache_resource(show_spinner="Loading RAG knowledge base...")
def load_knowledge_base():
    """Load all knowledge base files and build indices."""
    model = load_embedding_model()

    kb = {}

    # Health guidelines
    health_chunks = load_text_file("data/health_guidelines.txt")
    if health_chunks:
        health_index, _ = build_faiss_index(health_chunks, model)
        kb["health"] = {"chunks": health_chunks, "index": health_index}

    # AQI thresholds
    threshold_chunks = load_text_file("data/aqi_thresholds.txt")
    if threshold_chunks:
        threshold_index, _ = build_faiss_index(threshold_chunks, model)
        kb["thresholds"] = {"chunks": threshold_chunks, "index": threshold_index}

    # City zones
    zone_chunks = load_text_file("data/city_zones.txt")
    if zone_chunks:
        zone_index, _ = build_faiss_index(zone_chunks, model)
        kb["zones"] = {"chunks": zone_chunks, "index": zone_index}

    kb["model"] = model
    return kb


def search_health(condition: str, kb: dict) -> list:
    """Search health guidelines for a condition."""
    if "health" not in kb:
        return []
    return search(
        condition,
        kb["health"]["chunks"],
        kb["model"],
        kb["health"]["index"],
        top_k=2,
    )


def search_threshold(aqi: int, kb: dict) -> dict:
    """Find threshold info for an AQI value."""
    if "thresholds" not in kb:
        return {}
    results = search(
        f"AQI {aqi}",
        kb["thresholds"]["chunks"],
        kb["model"],
        kb["thresholds"]["index"],
        top_k=1,
    )
    if not results:
        return {}
    return parse_threshold(results[0]["text"])


def search_zone(zone_name: str, kb: dict) -> dict:
    """Find zone info."""
    if "zones" not in kb:
        return {}
    results = search(
        zone_name,
        kb["zones"]["chunks"],
        kb["model"],
        kb["zones"]["index"],
        top_k=1,
    )
    if not results:
        return {}
    return parse_zone(results[0]["text"])


def parse_threshold(text: str) -> dict:
    """Parse a threshold block into a dict."""
    result = {}
    for line in text.split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            result[key.strip().lower()] = val.strip()
    return result


def parse_zone(text: str) -> dict:
    """Parse a zone block into a dict."""
    result = {}
    for line in text.split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            result[key.strip().lower()] = val.strip()
    return result
