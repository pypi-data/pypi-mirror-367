# ==============================================================================
# Mesh Memory Protocol™ SDK – SVAF API Entry Point Module
#
# File:        svaf_api.py
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

from .cmb import CognitiveMemoryBlock

# In future: from meshmemory_core import svaf_fuse
from .svaf_fusion import svaf_fuse   # For now, included in SDK. Move to core later.

def svaf_api(request_payload: dict) -> dict:
    """
    Protocol-facing SVAF API.
    - Accepts a VEE/mesh-generated request payload (see below)
    - Returns a protocol-complete SVAF response, including:
        - Fused CMB, all anchors, event edge(s), SVAF metrics, exception if any.
    - No audit/logging side effects (caller must invoke audit).

    Request payload structure:
    {
        "cmb_new": { ... },          # Candidate CMB node (dict, includes id, fields, metadata, etc.)
        "anchors": [ ... ],          # List of anchor CMB dicts (same structure)
        "config": { ... },           # Protocol config/hyperparams (for SVAF, drift, etc.)
        "request_id": "event-uuid"   # Optional, used as event id
        # Optionally: "raw_input_ref", "raw_input_text"
    }

    Response structure:
    {
        "fused_cmb": { ... },        # Resulting fused CMB dict
        "anchors": [ ... ],          # Repeat anchors (so audit/event has full event context)
        "edges": [
            {
                "from": ["anchor_id1", "anchor_id2", ...],
                "relation": "is_fused_from",
                "event_id": "event-uuid"
            }
        ],
        "svaf_details": { ... },     # Anchor weights, drift, field context, etc.
        "exception": str or None     # Any error or protocol violation details
    }
    """
    try:
        # Parse CMBs from dicts (with id/fields/metadata/edges/labels/provenance)
        cmb_new = CognitiveMemoryBlock.from_dict(request_payload["cmb_new"])
        anchors = [CognitiveMemoryBlock.from_dict(a) for a in request_payload["anchors"]]
        config = request_payload["config"]
        event_id = request_payload.get("request_id")

        # --- Run protocol-lawful SVAF fusion (core is pure/stateless) ---
        fused_cmb, svaf_metrics, svaf_details = svaf_fuse(
            cmb_new, anchors, config, fields=list(cmb_new.fields.keys())
        )

        # --- Prepare protocol edge (all ancestry, event_id for audit) ---
        edge = {
            "from": [a.id for a in anchors],
            "relation": "is_fused_from",
            "event_id": event_id
        }

        response = {
            "fused_cmb": fused_cmb.to_dict(),
            "anchors": [a.to_dict() for a in anchors],
            "edges": [edge],
            "svaf_details": svaf_details,
            "exception": None
        }
    except Exception as ex:
        # On protocol violation or error, package for async audit/log
        response = {
            "fused_cmb": None,
            "anchors": [a.to_dict() for a in anchors] if 'anchors' in locals() else [],
            "edges": [],
            "svaf_details": {},
            "exception": str(ex)
        }
    return response
