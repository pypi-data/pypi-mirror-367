# ==============================================================================
# Mesh Memory Protocol™ SDK – Memory Evolution Module
#
# File:        memory_evolution.py
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

import uuid
from datetime import datetime
from .cmb import CognitiveMemoryBlock
from .vee import vee
from .svaf_api import svaf_api
from .clarifier import clarifier_event

# ====== MeshMemory Lawful Event API ======

def create(raw_input, api_key=None, context=None, config=None):
    """
    Lawful onboarding (VEE) event: turns raw input into a protocol-compliant CMB.
    Returns: (CognitiveMemoryBlock, audit_log)
    """
    cmb, audit = vee(raw_input, api_key=api_key, context=context, config=config)
    audit.update({
        'event_type': 'create',
        'cmb_id': cmb.id,
        'timestamp': datetime.now().isoformat(),
    })
    return cmb, audit

def remix(candidate_cmb, anchor_cmbs, config=None, request_id=None):
    """
    Remix protocol event: fuses candidate CMB with anchors using SVAF.
    Returns: (CognitiveMemoryBlock, audit_log)
    """
    config = config or {}
    request_id = request_id or str(uuid.uuid4())
    request_payload = {
        "cmb_new": candidate_cmb.to_dict(),
        "anchors": [a.to_dict() for a in anchor_cmbs],
        "config": config,
        "request_id": request_id,
    }
    response = svaf_api(request_payload)
    if response.get("fused_cmb") is None:
        raise ValueError("Remix failed: response['fused_cmb'] is None. Check upstream logic or API response.")
    fused_cmb = CognitiveMemoryBlock.from_dict(response["fused_cmb"])
    audit = {
        "event_type": "remix",
        "fused_cmb_id": fused_cmb.id,
        "anchors": [a.id for a in anchor_cmbs],
        "edges": response["edges"],
        "svaf_details": response["svaf_details"],
        "timestamp": datetime.now().isoformat(),
        "cmb_field_evolution": extract_field_evolution(response)
    }
    return fused_cmb, audit

def clarify(fused_cmb, drift_scores, config):
    """
    Clarify protocol event: runs protocol clarifier logic.
    Returns: (decision, audit_log)
    """
    decision, clarifier_audit = clarifier_event(fused_cmb, drift_scores, config)
    clarifier_audit.update({
        'event_type': 'clarify',
        'timestamp': datetime.now().isoformat(),
    })
    return decision, clarifier_audit

def collapse(trail_cmbs, config=None):
    """
    Collapse protocol event: collapses a sequence/trail of CMBs to a canonical form.
    (Implemented as SVAF remix for demo/protocol MVP.)
    Returns: (CognitiveMemoryBlock, audit_log)
    """
    config = config or {}
    candidate = trail_cmbs[0]
    anchors = trail_cmbs[1:]
    fused_cmb, audit = remix(candidate, anchors, config, request_id="collapse-" + str(uuid.uuid4()))
    audit['event_type'] = 'collapse'
    return fused_cmb, audit

def canonize(trail_cmbs, config=None):
    """
    Canonize protocol event: finalizes a trail as a protocol-certified, immutable cognitive asset.
    Returns: (CognitiveMemoryBlock, audit_log)
    """
    fused_cmb, audit = collapse(trail_cmbs, config)
    audit.update({
        'event_type': 'canonize',
        'canonical': True,
        'timestamp': datetime.now().isoformat()
    })
    return fused_cmb, audit

# ====== Semantic Field Evolution Extraction ======

def extract_field_evolution(response):
    """
    Traces the evolution path for each CMB field in a protocol remix event.
    Returns: dict {field_name: [{ancestor_id, label, vector, weight}, ... , {fused_label, fused_vector}]}
    """
    field_context = response.get("svaf_details", {}).get("field_context", {})
    evolution = {}
    for field, ctx in field_context.items():
        evolution[field] = [
            {
                "ancestor_id": a.get("anchor_id"),
                "label": a.get("anchor_label"),
                "vector": a.get("vector"),
                "weight": a.get("weight")
            }
            for a in ctx.get("anchors", [])
        ]
        evolution[field].append({
            "fused_label": ctx.get("fused_label"),
            "fused_vector": ctx.get("fused_vector")
        })
    return evolution
