# ==============================================================================
# Mesh Memory Protocol™ SDK – Cognitive Memory Block (CMB) Module
#
# File:        cmb.py
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

import numpy as np
import random

def generate_mesh_cmb_id(prefix="cmb", nbytes=3):
    """
    Generates mesh-readable CMB ID like 'cmb_0xF00D01'.
    - nbytes=3 → 6 hex digits
    """
    randhex = f"{random.getrandbits(nbytes * 8):0{nbytes * 2}X}"
    return f"{prefix}_0x{randhex}"

class CognitiveMemoryBlock:
    """
    MeshMemory Protocol: Cognitive Memory Block (CMB)
    Reference: Protocol Overview §CMB, AAAI-26 Section 3.1, docs/protocol_overview.md

    A field-complete, protocol-normalized, immutable memory unit.
    - Each field is a named, normalized vector (e.g., intent, commitment, etc.).
    - Unique ID is assigned at creation (for mesh trails/graph).
    - Edges record ancestry (fusion, collapse, remix) as per mesh protocol law.
    - Metadata may include agent_id, timestamp, validator_id, protocol event info.
    - Provenance (optional): per-field semantic context trace for full auditability.
    - Labels (optional): per-field symbolic label for audit/test/demo.
    """

    def __init__(
        self,
        fields: dict,
        metadata: dict = None,
        provenance: dict = None,
        labels: dict = None,
        edges: list = None,
        id: str = None
    ):
        """
        Initialize a CognitiveMemoryBlock.
        Args:
            fields: dict mapping field names (str) to np.ndarray (protocol-normalized)
            metadata: dict, optional. Agent/timestamp/event metadata.
            provenance: dict, optional. Per-field semantic context.
            labels: dict, optional. Per-field symbolic label.
            edges: list, optional. List of edge dicts: {"from": [...], "relation": "..."}
            id: str, optional. Unique CMB ID (auto-generated if None)
        Raises:
            ValueError if any field vector is zero or normalization fails.
        """
        self.fields = {k: self._normalize(v) for k, v in fields.items()}
        self.metadata = dict(metadata or {})
        if "timestamp" not in self.metadata:
            self.metadata["timestamp"] = datetime.now()
        self.provenance = provenance or {}
        self.labels = labels or {}
        self.edges = edges or []
        self.id = id or generate_mesh_cmb_id()

    def _normalize(self, v):
        """Ensures vector is protocol-normalized (unit norm)."""
        v = np.array(v)
        norm = np.linalg.norm(v)
        if norm == 0:
            raise ValueError("Field vector cannot be zero (protocol violation)")
        return v / norm

    def to_dict(self):
        """
        Serializes the CMB to a dictionary (for audit log, mesh export, or storage).
        Returns:
            dict with all fields, metadata, id, edges, provenance, and labels.
        """
        out = {
            "id": self.id,
            "fields": {k: v.tolist() for k, v in self.fields.items()},
            "metadata": self.metadata,
            "edges": self.edges
        }
        if self.provenance:
            out["provenance"] = self.provenance
        if self.labels:
            out["labels"] = self.labels
        return out

    @staticmethod
    def from_dict(d):
        """
        Instantiates a CMB from a dictionary (e.g., from storage or network).
        Args:
            d: dict with "fields", "metadata", "provenance", "labels", "edges", "id"
        Returns:
            CognitiveMemoryBlock
        """
        provenance = d.get("provenance", {})
        labels = d.get("labels", {})
        edges = d.get("edges", [])
        id = d.get("id")
        return CognitiveMemoryBlock(
            {k: np.array(v) for k, v in d["fields"].items()},
            d.get("metadata", {}),
            provenance=provenance,
            labels=labels,
            edges=edges,
            id=id
        )

    def validate_completeness(self, required_fields):
        """Checks that all required fields are present."""
        missing = [f for f in required_fields if f not in self.fields]
        if missing:
            raise ValueError(f"CMB is missing required fields: {missing}")

    def validate_all_normalized(self, tol=1e-6):
        """Checks all fields are normalized to unit norm (within tolerance)."""
        for k, v in self.fields.items():
            if abs(np.linalg.norm(v) - 1.0) > tol:
                raise ValueError(f"Field '{k}' not protocol-normalized: {v}")

    def get_field_provenance(self, field):
        """Returns the provenance for a field, if present."""
        return self.provenance.get(field)

    def get_field_label(self, field):
        """Returns the symbolic label for a field, if present."""
        return self.labels.get(field)

    def __repr__(self):
        return (
            f"<CognitiveMemoryBlock(id={self.id}, fields={list(self.fields.keys())}, "
            f"metadata={self.metadata}, edges={self.edges}, "
            f"provenance_keys={list(self.provenance.keys())}, "
            f"labels_keys={list(self.labels.keys())})>"
        )
