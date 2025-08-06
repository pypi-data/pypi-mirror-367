# MeshMem SDK

**MeshMem™** is the protocol-native, event-driven SDK for composable, auditable, and lawful cognitive memory in AI and multi-agent systems—built and governed by Consenix Group Ltd.

---

## 🚀 What is MeshMem?

**MeshMem turns any agent, LLM app, or distributed system into a protocol-governed, semantically continuous, and auditable cognitive agent.**
It’s more than an “AI memory” layer—it’s the full, lawful substrate for composable, explainable, and capitalizable mesh cognition.

---

## 🏆 Key Capabilities

* **Field-complete Cognitive Memory Blocks (CMBs):**  
  Structured, protocol-auditable memory with symbolic fields and vectors—not just blobs or chunks.

* **Lawful Memory Evolution:**  
  Every memory change (creation, remix, clarification, canonization) is a protocol event—fully logged, validator/auditor-signed, and auditable.

* **Protocol-grade Semantic Fusion (SVAF):**  
  Field-wise, mathematically rigorous, drift-bounded fusion; no more “just average the embeddings.”

* **Semantic Drift Detection & Clarifier Logic:**  
  Built-in drift detection and clarifier agents maintain mesh-wide semantic continuity.

* **Full Auditability & Regulatory Compliance:**  
  Every event is protocol-logged: who, what, when, why, and how.

* **Composable, Programmable Mesh Memory:**  
  Remix, clarify, and canonize memories into cognitive assets—ready for assetization, staking, and multi-agent collaboration.

---

## 🧑‍💻 Developer Quickstart

**Install from PyPI:**

```bash
pip install meshmem
```

**From source:**

```bash
git clone https://github.com/meshmem/meshmem-sdk.git
cd meshmem-sdk
pip install -e .
```

> See [`examples/`](./examples/) for ready-to-run demos.

---

### ⚡ Minimal Example

```python
from meshmem import create, remix, clarify

raw_input = "List the main compliance and technical risks for Q4."
cmb, audit = create(raw_input, api_key="sk-...")

# Fuse with anchor CMBs
fused_cmb, remix_audit = remix(cmb, [cmb2, cmb3])

# Clarify semantic drift
decision, clarifier_audit = clarify(fused_cmb, drift_scores={"block": remix_audit["svaf_details"]["block_drift"]}, config={...})
```

---

## 📖 Documentation

* [Protocol Overview](./docs/protocol_overview.md)
* [SVAF API Reference](./docs/svaf_api_reference.md)
* [Memory Evolution API Reference](./docs/memory_evolution_api_reference.md)
* [Metrics & Experiments](./docs/metrics.md)
* [Replication & Reproducibility](./docs/replication.md)

---

## 💡 Why MeshMem? (vs. Other “Memory” Tools)

<details>
<summary><strong>MeshMem is protocol-native, mesh-ready, and audit-grade—here’s how it stands apart:</strong> (click to expand)</summary>

### **Feature Comparison Table**

| Feature            | MeshMem (SDK)                                  | LangMem / MemGPT / etc.       |
| ------------------ | ---------------------------------------------- | ----------------------------- |
| Memory Structure   | Protocol-defined CMBs, fields, vectors, labels | “Chunks”, text blobs, vectors |
| Semantic Alignment | Field-wise, drift-bounded SVAF fusion          | Heuristic, vector avg/concat  |
| Drift Detection    | Built-in, protocol-governed, clarifier logic   | Rare or ad hoc                |
| Audit Trail        | Validator-signed, event-driven, forensic       | Minimal or app-level          |
| Governance         | Mesh protocol law, validator circles, RFCs     | None or app-specific          |
| Assetization       | Canonize as programmable assets (MCATs, etc.)  | No, or only as DB records     |
| Compliance         | Native, protocol-signed, explainable           | No protocol, no compliance    |
| Mesh/Inter-agent   | Designed for mesh/collab cognition across orgs | Agent-local or per-app        |

**Bottom Line:**
MeshMem does for AI memory what blockchain did for transactions:
It makes memory lawful, composable, auditable, and programmable—enabling collective intelligence, regulatory compliance, and epistemic assetization.

</details>

---

## ⚡️ Upgrade Path: Open Source → Enterprise

MeshMem is free for non-commercial research, academic, and protocol evaluation.
**For enterprise/commercial deployments, production support, or integration:**

### **SYM.BOT Ltd — Exclusive Enterprise Steward for MeshMem**

[![Enterprise Support: SYM.BOT](https://img.shields.io/badge/Enterprise--Support-SYM.BOT-25D0FF?style=flat-square&logo=datadog&logoColor=white)](https://sym.bot)

* LTS releases, onboarding, and SLAs
* Enterprise integrations, compliance, and security features
* Professional support, consulting, and managed deployments
* Custom features and OEM licensing

📧 [support@sym.bot](mailto:support@sym.bot)  
🌐 [https://sym.bot](https://sym.bot)

*All protocol law and underlying technology remain governed by Consenix Group Ltd.*

---

## 💼 IP, Licensing, and Commercial Use

**MeshMem SDK and protocol are exclusive IP of Consenix Group Ltd.**

* No commercial use, redistribution, or integration permitted without written license.
* See [LICENSE](./LICENSE) and [IP\_NOTICE.md](./IP_NOTICE.md) for details.

All protocol IP, research, and governance inquiries:  
📧 [licensing@consenix.com](mailto:licensing@consenix.com)  
🌐 [https://consenix.com/license](https://consenix.com/license)

---

## 🤝 Contributing

* Bug reports and documentation suggestions are welcome.
* Protocol law changes/features require RFC via Consenix governance.
* All contributions are subject to IP assignment.

See [CONTRIBUTING.md](./CONTRIBUTING.md)

---

© 2025 Consenix Group Ltd. All Rights Reserved.  
MeshMem™, MeshMemory™, CMB™, SVAF™, CAT7™, and SYMBit™ are trademarks of Consenix Group Ltd.

---

**MeshMem: Turn any agent into a protocol-governed, compliant, and composable node of collective intelligence.**

---