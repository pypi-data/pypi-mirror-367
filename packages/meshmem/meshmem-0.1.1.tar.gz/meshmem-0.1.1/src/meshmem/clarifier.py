# ==============================================================================
# Mesh Memory Protocol™ SDK – Clarifier Agent/Event Module
#
# File:        clarifier.py
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
# ------------------------------------------------------------------------------
# THIS FILE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
# ==============================================================================

def clarifier_event(fused_cmb, drift_scores, config):
    """
    Canonical Clarifier Event for MeshMemory Protocol.
    Determines protocol-lawful outcome for a fused memory event
    based on block drift, and returns normalized decision with audit details.

    Args:
        fused_cmb: CognitiveMemoryBlock (result of fusion/remix)
        drift_scores: dict with at least 'block' (float), and optionally per-field scores
        config: dict, must include protocol thresholds:
            - 'drift_threshold': float, required for acceptance
            - 'clarifier_band': float, upper bound for auto-reject
            - (optional: 'timestamp', other audit metadata)
    Returns:
        decision: str ('accepted', 'review', or 'rejected')
        audit: dict with clarifier decision, drift, thresholds, timestamp, etc.

    Protocol References:
        - Protocol Overview §Clarifier, AAAI-26 Section 3.7
        - docs/protocol_overview.md, docs/metrics.md
    """
    block_drift = drift_scores.get("block")
    threshold = config.get("drift_threshold", 0.25)
    upper = config.get("clarifier_band", 0.5)
    timestamp = config.get("timestamp")

    # Lawful protocol decision logic (3-state Kanban)
    if block_drift is None:
        raise ValueError("clarifier_event: drift_scores must include 'block' drift value.")

    if block_drift > upper:
        decision = "rejected"   # Lawful stop
    elif block_drift > threshold:
        decision = "review"     # Needs cognitive/agent intervention
    else:
        decision = "accepted"   # Lawful, proceed

    audit = {
        "clarifier_decision": decision,
        "block_drift": block_drift,
        "drift_threshold": threshold,
        "clarifier_band": upper,
        "timestamp": timestamp,
        "fused_cmb_id": getattr(fused_cmb, "id", None),
        "kanban_status": decision,   # Optional: duplicate for Kanban UI/flow
        "recommended_action": {
            "accepted": "Proceed with next cognitive step.",
            "review": "Review this memory for possible clarification or realignment.",
            "rejected": "Protocol violation. Revise or abandon this memory."
        }[decision]
    }
    # Include per-field drifts, etc. as desired
    if "fields" in drift_scores:
        audit["field_drifts"] = drift_scores["fields"]

    return decision, audit
