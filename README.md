# QuickCommand (ReSAISE 2025)

**QuickCommand** is a low-latency, **CPU-only** NLP → MAVLink pipeline for reliable UAV telepresence.  
It maps natural-language commands (e.g., *“move right three meters”*, *“rotate left 90 degrees”*, *“emergency stop”*) to Pixhawk control under a strict **< 50 ms** end-to-end (E2E) latency budget, with a **confidence gate** and **hover/hold** safety fallback.

---

## 1) Overview

- **Objective:** Natural-language teleoperation of UAVs with real-time safety guarantees.  
- **Approach:** Compact-transformer intent classification → parameter extraction → MAVLink translation → Pixhawk dispatch.  
- **Safety:** Low-confidence predictions automatically trigger **hover/hold**.

---

## 2) Core Command Set (Table I in the paper)

| Class            | Example Utterance                   |
|------------------|-------------------------------------|
| Move (lateral)   | “Move right three meters”           |
| Move (vertical)  | “Go up two meters”                  |
| Rotate (yaw)     | “Rotate left ninety degrees”        |
| Hover            | “Hover here for five seconds”       |
| Takeoff          | “Take off now”                      |
| Land             | “Land gently”                       |
| Emergency Stop   | “Abort mission immediately”         |

---

## 3) Latency Budget & System Targets (Abstract)

- **NLP inference:** ~**15 ms** (budgeted under **20 ms**)  
- **MAVLink dispatch:** ~**12 ms**  
- **Pixhawk actuation:** ~**6 ms**  
- **E2E target:** **< 50 ms** (met by Quantized-BERT and the rule-based baseline)

---

## 4) Results (Table II): Latency & Accuracy (CPU-only)

Median (and 95th) latencies in milliseconds:

| Model              | Inf. Med | Inf. 95% | Trans. Med | Trans. 95% | E2E Med | E2E 95% | Acc. |
|--------------------|----------|----------|------------|------------|---------|---------|------|
| Regex-only         | 1        | 1        | 12         | 12         | 19      | 19      | 100% |
| **Quantized-BERT** | **1**    | **1**    | **12**     | **12**     | **19**  | **19**  | **100%** |
| MobileBERT         | 231      | 231      | 12         | 12         | 249     | 249     | 100% |
| DistilBERT         | 225      | 226      | 12         | 12         | 243     | 244     | 100% |
| ALBERT             | 239      | 240      | 12         | 12         | 257     | 258     | 100% |
| ELECTRA-Small      | 204      | 206      | 12         | 12         | 222     | 224     | 0%   |

**Key takeaway:** Among transformers, **Quantized-BERT** is the only model that satisfies **both** the timing and accuracy requirements for real-time telepresence on CPU.

---

## 5) Comparison with Prior Work (Table III)

| System                            | Latency (ms) | Accuracy |
|-----------------------------------|--------------|----------|
| Contreras et al.                  | 150*         | 96%      |
| Oneață & Cucu (ASR-only)          | 200*         | 90%      |
| Simões et al. (direct audio→cmd)  | 21*          | 99%      |
| **QuickCommand (Quantized-BERT)** | **19**       | **100%** |

\* Refer to original works for exact scope; QuickCommand reports **CPU-only, on-device** latencies including dispatch and actuation.

---

## 6) System Design (Figure 2 in the paper)

**Pipeline stages:**
1. **NLP Preprocessing** (normalize, extract parameters)
2. **Compact Transformer Inference** (7 intents + confidence)
3. **Command Classification** (thresholded; hover fallback)
4. **MAVLink Translation** (standard messages)
5. **Pixhawk Dispatch** (serial/telemetry, on-device)

**MAVLink mapping:**

| Intent                        | MAVLink Command(s)                                                                 |
|------------------------------|-------------------------------------------------------------------------------------|
| move / altitude              | `SET_POSITION_TARGET_LOCAL_NED`                                                     |
| rotate (yaw)                 | `SET_ATTITUDE_TARGET`                                                               |
| takeoff / land               | `MAV_CMD_NAV_TAKEOFF` / `MAV_CMD_NAV_LAND` *(via `COMMAND_LONG`)*                  |
| hover / uncertain (fallback) | zero-velocity hold via `SET_POSITION_TARGET_LOCAL_NED`                              |
| emergency_stop               | switch mode to **HOLD** with zero velocity                                          |

---

## 7) Dataset & Evaluation Protocol

- **7,000** synthetic utterances (**1,000/class**), **80/10/10** split.  
- ASR-style noise: insertions/deletions/substitutions at **10–20%**.  
- Latency measured at **(1) NLP**, **(2) translation**, and **(3) end-to-end**.  
- CPU-only inference reported; dispatch and actuation measured in the loop.

---

## 8) Repository Structure

```text
Resaise2025/
├─ README.md
├─ environment.yml
├─ LICENSE
├─ scripts/
│  ├─ generate_dataset.py          # dataset generator (ready)
│  ├─ test_pipeline.py             # mock E2E latency demo (ready)
│  └─ dump_system_info.py          # system info capture (ready)
├─ quickcommand/
│  ├─ models/
│  │  ├─ quantized_bert/           # (ready) best CPU-latency model from the paper
│  │  ├─ mobilebert/               # (soon)
│  │  ├─ distilbert/               # (soon)
│  │  ├─ tinybert/                 # (soon)
│  │  ├─ albert/                   # (soon)
│  │  └─ electra_small/            # (soon)
│  ├─ nlp/
│  │  └─ preprocessor.py           # (ready) normalization + parameter parsing
│  ├─ mavlink/
│  │  └─ translator.py             # (ready) intent → MAVLink messages
│  └─ gui/                         # (soon) live latency monitor
├─ data/
│  ├─ dataset.jsonl                # created by scripts/generate_dataset.py
│  └─ samples/                     # (soon) small example snippets
└─ reports/
   ├─ latency_summary.json         # mirrors paper’s table
   └─ system_info_local.json       # produced by dump_system_info.py

## 9) Models Evaluated

| Model            | Status | Notes |
|------------------|--------|-------|
| **Quantized-BERT** | Ready  | Meets **< 50 ms** E2E (CPU-only) and **100% accuracy** (paper). Best latency/accuracy trade-off. |
| MobileBERT       | Soon   | High accuracy; CPU inference ~231 ms median. |
| DistilBERT       | Soon   | High accuracy; CPU inference ~225 ms median. |
| TinyBERT         | Soon   | High accuracy; CPU inference >200 ms median. |
| ALBERT           | Soon   | High accuracy; CPU inference ~239 ms median. |
| ELECTRA-Small    | Soon   | Fast-ish but failed accuracy threshold (0%). |
| Regex baseline   | N/A    | Rule-based reference; meets latency, limited generality. |

## 10) Reproducibility & Experimental Environments

### Platforms

| Platform         | Purpose                               | CPU                          | GPU                         | Python | Notes                                                  |
|------------------|----------------------------------------|------------------------------|-----------------------------|--------|--------------------------------------------------------|
| **HPC Node**     | Training & baseline evaluation         | AMD EPYC 9634 (96 cores)     | NVIDIA L40S *(training only)* | 3.10   | Paper reports **CPU-only** inference timings           |
| **Local Machine**| On-device verification & Pixhawk tests | <your CPU model>             | —                           | 3.10   | Pixhawk 2.4.8 via MAVLink 2.0 (915 MHz telemetry)     |

### Software Stack

| Component                  | Version |
|---------------------------|---------|
| Ubuntu                    | 22.04   |
| PyTorch                   | 2.0     |
| Hugging Face Transformers | 4.42.0  |
| NumPy                     | 1.26    |
| pymavlink                 | 3.x     |

### Local Run Directories (examples)

```text
drone_qbert_local
drone_mobilebert_local
drone_distilbert_local
drone_tinybert_local
drone_albert_local
drone_electra-small_local

## 11) Reproduce in 5 Minutes

Follow these steps to replicate the pipeline or verify the latency results on your own system.

### Step 1 – Create and activate the environment
```bash
conda env create -f environment.yml
conda activate quickcommand

## 12) Key Findings

- **Real-time performance:** QuickCommand achieves a **median 19 ms** end-to-end latency on CPU, staying well below the **50 ms** safety threshold required for telepresence control loops.  
- **Model selection:** Among six compact transformers, **Quantized-BERT** uniquely satisfies both latency (< 20 ms NLP inference) and **100 % accuracy**.  
- **Reliability & safety:** A confidence threshold of **0.5** automatically redirects uncertain predictions to a **hover/hold** command, ensuring zero unsafe actions.  
- **Efficiency:** Full command execution—including NLP inference, MAVLink translation, and Pixhawk actuation—fits within a 19 ms median budget on CPU-only hardware.  
- **Deployment readiness:** Operates entirely **offline and on-device**—no GPU or cloud dependency—making it practical for field or edge UAV missions.  
- **Reproducibility:** Includes a 7-class, 7 000-sample dataset generator (**80/10/10** split) and scripts to regenerate experiments and latency tables exactly as reported in the paper.

## 13) Citation

If you use or reference **QuickCommand**, please cite the following paper:

```bibtex
@inproceedings{ElHadedy2025QuickCommand,
  title     = {QuickCommand: A Low-Latency NLP Pipeline for Reliable UAV Telepresence},
  author    = {Mohamed El-Hadedy and Wen-Mei W. Hwu},
  booktitle = {Proceedings of the Workshop on Reliable and Secure AI for Software Engineering (ReSAISE) 2025},
  year      = {2025}
}
## 14) License

This project is released under the **MIT License**. See the [LICENSE](./LICENSE) file for details.


## 15) Contact

For questions, collaborations, or academic use:

**Dr. Mohamed El-Hadedy**  
Department of Electrical and Computer Engineering  
California State Polytechnic University, Pomona (CPP)  
mealy@cpp.edu


## 16) Acknowledgments

<p>
  <img src="https://img.shields.io/badge/U.S.%20Navy%20NEEC-N001742310002-0a3d62?style=for-the-badge" alt="NEEC N001742310002" />
  <img src="https://img.shields.io/badge/ONR-Summer%20Faculty%20Research%20Program-1e90ff?style=for-the-badge" alt="ONR SFRP" />
  <img src="https://img.shields.io/badge/AFRL-FA8650--24--2--2403-2d3436?style=for-the-badge" alt="AFRL FA8650-24-2-2403" />
</p>

**This work was supported by:**
- **U.S. Navy Naval Engineering Education Consortium (NEEC)** — Grant **N001742310002**  
- **Office of Naval Research (ONR)** — Summer Faculty Research Program (SFRP)  
- **Air Force Research Laboratory (AFRL)** — Agreement **FA8650-24-2-2403**

> The views and conclusions contained herein are those of the authors and do not necessarily reflect the official policies or endorsements of the U.S. Government.

