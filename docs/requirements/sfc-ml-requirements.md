---
title: ML-Based SFC System Requirements
tags: [requirements, sfc, ml, rag]
source: email
from: Thamizhanban Arumugaperumal <Thamizhanban.Arumugaperumal@ggsinc.com>
to: Ravi Dharmarajan <Ravi.Dharmarajan@ggsinc.com>
date: 2026-05-27
subject: ML-Based SFC System Requirements and Expectations
status: received — pending decomposition
---

# ML-Based SFC System Requirements

## Context

Part of the **ALH CBT & SFC web application**. AI-assisted features requested for the **SFC (Symptoms Fault Correlation)** module to improve troubleshooting efficiency and user experience.

## Functional Requirements

### Mission Learning

| ID    | Requirement                                                                                                        |
| ----- | ------------------------------------------------------------------------------------------------------------------ |
| SFC-1 | System learns from previously resolved faults, troubleshooting history, and corrective actions                     |
| SFC-2 | Knowledge base stores: past fault cases, symptoms, probable causes, and successful resolutions                     |
| SFC-3 | When similar symptoms occur, system recommends the most relevant troubleshooting path based on historical learning |

## How This Maps to HAL-AI Architecture

| SFC Concept                         | HAL-AI Component                                                      |
| ----------------------------------- | --------------------------------------------------------------------- |
| Knowledge base of past fault cases  | Qdrant vector store — fault documents ingested via ingestion pipeline |
| Learning from resolved faults       | RAG retrieval — similar symptom vectors retrieved from history        |
| Troubleshooting path recommendation | gemma4 grounded answer using retrieved fault cases as context         |
| Symptom input                       | User query via Chainlit UI or FastAPI `/chat` endpoint                |

## Open Questions

- [ ] What is the source format for fault/symptom data? (structured DB export, PDF reports, plain text logs?)
- [ ] Who populates the knowledge base — engineers log resolutions manually, or is it pulled from an existing system?
- [ ] What does "troubleshooting path" look like in output — ranked steps, single recommendation, or decision tree?
- [ ] Is there a feedback loop — can users mark a recommendation as correct/incorrect to improve future results?
- [ ] What is the target system for production — same air-gapped Windows Server, or separate deployment?
- [ ] Are fault records confidential? (affects data handling in the RAG pipeline)

## Related

- [[requirements]] — HAL-AI base system requirements
- [[adr-005-llamaindex-orchestration]] — RAG orchestration layer
- [[adr-002-qdrant-over-chromadb]] — vector store choice


 # emil for refernce : 
 **From:** Thamizhanban Arumugaperumal <[Thamizhanban.Arumugaperumal@ggsinc.com](mailto:Thamizhanban.Arumugaperumal@ggsinc.com)>  
**Sent:** Wednesday, May 27, 2026 7:08:17 pm  
**To:** Ravi Dharmarajan <[Ravi.Dharmarajan@ggsinc.com](mailto:Ravi.Dharmarajan@ggsinc.com)>  
**Subject:** ML-Based SFC System Requirements and Expectations  


As part of the ALH CBT & SFC web application development, we would like to incorporate AI-assisted features in the SFC (Symptoms Fault Correlation) module to improve troubleshooting efficiency and user experience.

  Please consider the following expectations and functionalities while designing the ML-based SFC system:

  Mission Learning:
The system should learn from previously resolved faults, troubleshooting history, and corrective actions.
Past fault cases, symptoms, probable causes, and successful resolutions should be stored in the knowledge base.
When similar symptoms occur in future, the system should intelligently recommend the most relevant troubleshooting path based on historical learning.

Thanks 
Thamizhanban A
