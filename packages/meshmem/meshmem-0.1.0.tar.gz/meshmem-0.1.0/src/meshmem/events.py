# ==============================================================================
# Mesh Memory Protocol™ SDK – Mesh Memory Evolution Events (Event Ontology) Module
#
# File:        events.py
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

from datetime import datetime

class MeshProtocolEvent:
    """
    Canonical mesh event types for lawful memory evolution.
    """
    CREATE = "create"         # Agent asserts a new VEE-validated CMB (starts a Trail)
    REMIX = "remix"           # Multiple CMBs/Trails fused via SVAF (creates new memory)
    CLARIFY = "clarify"       # Triggered by drift/contradiction; clarifier agents realign
    COLLAPSE = "collapse"     # Trails reduced to canonical state by validator consensus
    CANONIZE = "canonize"     # Trail finalized to immutable cognitive asset

def create_event(event_type, cmb, related_cmb_ids=None, **kwargs):
    """
    Creates a protocol event record for mesh audit/logging.
    """
    return {
        "event_type": event_type,
        "cmb_id": cmb.id,
        "related_cmb_ids": related_cmb_ids or [],
        "timestamp": datetime.now().isoformat(),
        "details": kwargs
    }
