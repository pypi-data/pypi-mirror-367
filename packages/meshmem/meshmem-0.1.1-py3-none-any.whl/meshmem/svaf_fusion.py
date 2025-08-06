# ==============================================================================
# Mesh Memory Protocol™ SDK – Symbolic–Vector Attention Fusion (SVAF) Engine Module
#
# File:        svaf_fusion.py
# Version:     v0.1.0
# Date:        2025-08-04
# Author:      Consenix Labs Ltd (R&D subsidiary of Consenix Group Ltd)
# Principal Inventor: Hongwei Xu (hongwei@consenix.com)
#
# © 2025 Consenix Group Ltd. All rights reserved.
#
# All code and derivative works are the exclusive intellectual property of
# Consenix Group Ltd (UK), including all enhancements and commercial extensions.
# Use of this code is governed strictly by the Consenix Protocol License.
# Contact: licensing@consenix.com | https://consenix.com/protocol-law
#
# -------------------------------------------------------------------------------
# THIS FILE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
# ==============================================================================

import datetime
import numpy as np
from typing import List, Dict, Any, Tuple

from .cmb import CognitiveMemoryBlock
from .validators.layer_transition import ProtocolLayerTransitionValidator

# ==============================
# Protocol field names (CAT7 schema)
CAT7_FIELDS = [
    "intent", "commitment", "emotion", "motivation", "perspective", "focus", "issue"
]

# Default protocol config values
DEFAULT_CONFIG = {
    "alpha_f": 1.0,          # Field weights; scalar (all fields) or dict (per field)
    "layer_gravity": 1.0,    # Scalar for anchor layer effect
    "temporal_decay": 0.05,  # Recency weighting for anchors
    "lambda_new": 1.0,       # Candidate (new CMB) weight
    "confidence": 1.0,       # Default anchor confidence
    "drift_threshold": 0.5,  # Protocol drift threshold for clarifier
}

class ProtocolComplianceError(Exception):
    """Raised if SVAF fusion or clarifier fails protocol law compliance."""

def field_cosine(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Cosine similarity between two vectors (for semantic alignment)."""
    denom = np.linalg.norm(vec1) * np.linalg.norm(vec2) + 1e-8
    return float(np.dot(vec1, vec2) / denom)

def compute_time_diff_seconds(ts1, ts2) -> float:
    """Compute time difference in seconds between two timestamps (any format)."""
    diff = ts1 - ts2
    if isinstance(diff, datetime.timedelta):
        return diff.total_seconds()
    return float(diff)

# === Protocol-Correct Anchor Scoring (per-field, per-anchor) ===
def compute_anchor_score(
    cmb_new: CognitiveMemoryBlock,
    anchor: CognitiveMemoryBlock,
    field: str,
    config: Dict[str, Any]
) -> float:
    """
    Lawful protocol anchor score for one anchor and one field:
    score = alpha_f * cosine(field_sim) * layer_gravity * recency * confidence
    """
    sim = field_cosine(cmb_new.fields[field], anchor.fields[field])
    layer = anchor.metadata.get("layer", 1)
    gravity = config.get("layer_gravity", DEFAULT_CONFIG["layer_gravity"]) * layer or 1.0
    time_diff = compute_time_diff_seconds(
        cmb_new.metadata.get("timestamp", 0),
        anchor.metadata.get("timestamp", 0)
    )
    recency = np.exp(-config.get("temporal_decay", DEFAULT_CONFIG["temporal_decay"]) * time_diff) or 1.0
    confidence = anchor.metadata.get("confidence", config.get("confidence", DEFAULT_CONFIG["confidence"])) or 1.0
    alpha_f = config.get("alpha_f", DEFAULT_CONFIG["alpha_f"])
    # Field-specific or uniform protocol weight
    alpha = (alpha_f.get(field, 1.0) if isinstance(alpha_f, dict) else alpha_f) or 1.0
    return alpha * sim * gravity * recency * confidence

def compute_anchor_scores(
    cmb_new: CognitiveMemoryBlock,
    anchor_cmbs: List[CognitiveMemoryBlock],
    field: str,
    config: Dict[str, Any]
) -> np.ndarray:
    """
    For a given field, compute anchor scores for all anchors.
    Returns a numpy array of protocol anchor scores.
    """
    return np.array([
        compute_anchor_score(cmb_new, anchor, field, config)
        for anchor in anchor_cmbs
    ])

# === Protocol-Correct Field-Wise Fusion ===
def protocol_field_fusion(
    cmb_new: CognitiveMemoryBlock,
    anchor_cmbs: List[CognitiveMemoryBlock],
    field: str,
    weights: np.ndarray,
    config: Dict[str, Any]
) -> np.ndarray:
    """
    Protocol law: Fuse a field from candidate and anchors via convex weighted sum.
    - Each field's anchor weights come from protocol anchor scores (already include alpha_f).
    - Candidate CMB weight is lambda_new.
    - Output is always normalized.
    """
    anchor_vecs = [a.fields[field] for a in anchor_cmbs]
    lambda_new = config.get("lambda_new", DEFAULT_CONFIG["lambda_new"])
    # Start with candidate vector, weighted
    fused_vector = lambda_new * cmb_new.fields[field]
    # Add anchor vectors, weighted
    for i, anchor_vec in enumerate(anchor_vecs):
        fused_vector += weights[i] * anchor_vec
    total_weight = lambda_new + np.sum(weights)
    fused_vector /= total_weight
    # Protocol: Normalize the result (||v||=1)
    norm = np.linalg.norm(fused_vector)
    if norm == 0:
        raise ValueError(f"Fused vector for field '{field}' has zero norm (protocol violation).")
    return fused_vector / norm

# === Protocol Drift/Clarifier Calculation ===
def compute_field_drifts(
    fused_vectors: Dict[str, np.ndarray],
    cmb_new: CognitiveMemoryBlock
) -> Dict[str, float]:
    """
    For each field, compute 1 - cosine similarity between the fused vector and the candidate vector.
    - Per protocol, lower is better (0 = perfect alignment).
    """
    return {
        f: float(1 - np.dot(fused_vectors[f], cmb_new.fields[f]))
        for f in fused_vectors
    }

def compute_layer_drifts(
    cmb_new: CognitiveMemoryBlock,
    anchor_cmbs: List[CognitiveMemoryBlock]
) -> List[int]:
    """
    Compute absolute protocol layer difference for each anchor (for audit).
    """
    candidate_layer = cmb_new.metadata.get("layer", 1)
    return [
        abs(candidate_layer - a.metadata.get("layer", 1))
        for a in anchor_cmbs
    ]

def derive_fused_layer(
    cmb_new: CognitiveMemoryBlock,
    anchor_cmbs: List[CognitiveMemoryBlock]
) -> int:
    """
    Protocol law: Set the fused CMB's layer to the mode (most common) among candidate and anchors.
    """
    layers = [cmb_new.metadata.get("layer", 1)] + [a.metadata.get("layer", 1) for a in anchor_cmbs]
    return max(set(layers), key=layers.count)

# === Main SVAF Protocol Fusion Engine ===
def svaf_fuse(
    cmb_new: CognitiveMemoryBlock,
    anchor_cmbs: List[CognitiveMemoryBlock],
    config: Dict[str, Any],
    validator: ProtocolLayerTransitionValidator = None,
    fields: List[str] = CAT7_FIELDS
) -> Tuple[CognitiveMemoryBlock, Dict[str, Any], Dict[str, Any]]:
    """
    Symbolic–Vector Attention Fusion (SVAF): Canonical, protocol-lawful fusion.
    - Fuses candidate + anchors, per field, with protocol anchor weighting.
    - All field-wise provenance and audit details are collected.
    - Returns fused CMB, protocol metrics, and full svaf_details.
    """
    fused_vectors = {}         # Dict[field, np.ndarray]: Fused vectors per field.
    anchor_weights_all = {}    # Dict[field, List[float]]: Protocol anchor weights.
    field_context = {}         # Dict[field, Dict]: Full audit provenance per field.

    # --- 1. For each protocol field, score anchors, fuse vectors, collect provenance ---
    for f in fields:
        # Compute protocol anchor scores (per protocol law)
        scores = compute_anchor_scores(cmb_new, anchor_cmbs, f, config)
        sum_scores = np.sum(scores)
        # Normalize anchor weights (for fusion) -- protocol: sum to 1 unless all 0 (then uniform)
        weights = scores / sum_scores if sum_scores != 0 else np.ones(len(scores)) / len(scores)
        anchor_weights_all[f] = weights.tolist()
        # Field-wise fusion (protocol-canonical)
        fused_vectors[f] = protocol_field_fusion(cmb_new, anchor_cmbs, f, weights, config)
        # Audit provenance: anchor id, label, vector, weight
        anchor_context = []
        for anchor, w in zip(anchor_cmbs, weights):
            anchor_id = getattr(anchor, "id", None)
            anchor_label = None
            if hasattr(anchor, "labels") and anchor.labels and f in anchor.labels:
                anchor_label = anchor.labels[f]
            elif hasattr(anchor, "provenance") and anchor.provenance and f in anchor.provenance:
                anchor_label = anchor.provenance[f].get("label")
            anchor_context.append({
                "anchor_id": anchor_id,
                "anchor_label": anchor_label,
                "vector": anchor.fields[f].tolist(),
                "weight": float(w),
            })
        # Protocol majority label for fused field (optional, for audit)
        fused_label = None
        if anchor_context:
            candidates = [ac["anchor_label"] for ac in anchor_context if ac["anchor_label"] is not None]
            if candidates:
                from collections import Counter
                fused_label = Counter(candidates).most_common(1)[0][0]
        field_context[f] = {
            "fused_vector": fused_vectors[f].tolist(),
            "fused_label": fused_label,
            "anchors": anchor_context
        }

    # --- 2. Compose protocol-fused CMB with full audit provenance and layer ---
    fused_layer = derive_fused_layer(cmb_new, anchor_cmbs)
    fused_cmb = CognitiveMemoryBlock(
        fields=fused_vectors,
        metadata={"event": "svaf_fusion", "layer": fused_layer},
        provenance=field_context
    )

    # --- 3. Compute field drifts and protocol-compliant block drift (critical fix here) ---
    field_drifts = compute_field_drifts(fused_vectors, cmb_new)
    fields_list = list(fused_vectors.keys())
    alpha_f = config.get("alpha_f", DEFAULT_CONFIG["alpha_f"])
    # Compute protocol alpha vector (for block drift weighting)
    if isinstance(alpha_f, dict):
        alpha_vec = np.array([alpha_f.get(f, 1.0) for f in fields_list])
    else:
        alpha_vec = np.ones(len(fields_list)) * float(alpha_f)
    drift_vec = np.array([field_drifts[f] for f in fields_list])
    # === CRITICAL FIX: Protocol-canonical block drift is the alpha_f-weighted mean field drift ===
    block_drift = float(np.sum(alpha_vec * drift_vec) / np.sum(alpha_vec))
    # === End fix ===
    layer_drifts = compute_layer_drifts(cmb_new, anchor_cmbs)

    # --- 4. (Optional) Enforce protocol law for cognitive layer transitions ---
    if validator is not None:
        prev_layer_vec = cmb_new.metadata.get("layer")
        fused_layer_vec = fused_cmb.metadata.get("layer")
        event_metadata = {
            "event": "svaf_fusion_layer_transition",
            "cmb_new_id": getattr(cmb_new, "id", None),
            "fused_cmb_id": getattr(fused_cmb, "id", None),
            "anchor_ids": [getattr(a, "id", None) for a in anchor_cmbs]
        }
        validator.check_transition(prev_layer_vec, fused_layer_vec, event_metadata)

    # --- 5. Enforce protocol drift bounds and flag clarifier if needed ---
    drift_threshold = config.get("drift_threshold", DEFAULT_CONFIG["drift_threshold"])
    fuse_status = None
    if block_drift > drift_threshold:
        # This triggers the protocol clarifier (see docs/metrics.md and AAAI-26)
        fuse_status = "review"
        print(
            f"SVAF fusion flagged for review: block drift={block_drift:.3f} exceeds threshold={drift_threshold}. Clarifier will be auto-triggered."
        )
    else:
        fuse_status = "accepted"

    # --- 6. Collect protocol-grade details for audit/event layer ---
    svaf_details = {
        "anchor_weights": anchor_weights_all,      # Anchor weights per field
        "field_context": field_context,            # Per-field provenance (vectors, labels, weights)
        "field_drifts": field_drifts,              # Per-field drift values (for audit)
        "block_drift": block_drift,                # Protocol-weighted block drift (for compliance)
        "layer_drifts": layer_drifts,              # Layer difference to anchors
        "fuse_status": fuse_status,                # "accepted" or "review" for clarifier
    }

    # --- 7. Return protocol outputs; all logging/auditing is handled by caller ---
    return fused_cmb, {"block": block_drift, "fields": field_drifts}, svaf_details
