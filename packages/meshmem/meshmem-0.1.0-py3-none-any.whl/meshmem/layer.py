# ==============================================================================
# Mesh Memory Protocol™ SDK – Canonical layer Module
#
# File:        layer.py
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

# Canonical layer definitions
LAYER_ORIGIN = 0
LAYER_OBSERVATION = 1
LAYER_REFLECTION = 2
LAYER_DIVERGENCE = 3
LAYER_SYNTHESIS = 4
LAYER_SYMBOLIC_DRIVE = 5
LAYER_CONVERGENCE = 6
LAYER_CANON = 7
LAYER_ARCHIVE = 8
LAYER_MYTHIC = 9

LAYER_NAMES = [
    "Origin", "Observation", "Reflection", "Divergence", "Synthesis",
    "Symbolic Drive", "Convergence", "Canon", "Archive", "Mythic"
]

def determine_layer(event_type, context=None, previous_layer=None, fuse_status=None):
    """
    Canonical protocol logic for CMB layer assignment.
    """
    if event_type == "create":
        if context and context.get("is_origin"):
            return 0  # L0: Origin
        else:
            return 1  # L1: Observation

    if event_type == "reflection":
        return 2  # L2: Reflection

    if event_type == "remix":
        # SVAF fusion: usually Synthesis unless drift/clarifier triggers divergence
        if fuse_status == "review":
            return 3  # L3: Divergence
        if fuse_status == "rejected":
            return 3  # L3: Divergence (cognitive conflict)
        return 4      # L4: Synthesis

    if event_type == "clarify":
        # If clarifier moves to consensus or resolves conflict
        return 6  # L6: Convergence

    if event_type == "canonize":
        return 7  # L7: Canon

    if event_type == "archive":
        return 8  # L8: Archive

    if event_type == "mythic":
        return 9  # L9: Mythic

    # Fallback: propagate previous layer, but always check protocol!
    return previous_layer if previous_layer is not None else 1
