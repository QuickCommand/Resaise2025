# QuickCommand (ReSAISE 2025)
*A low-latency, CPU-only NLP→MAVLink pipeline for reliable UAV telepresence.*

This repository provides artifacts for **“QuickCommand: A Low-Latency NLP Pipeline for Reliable UAV Telepresence.”**  
Goal: **< 50 ms** end-to-end (E2E) command execution to **Pixhawk** with **offline/on-device** inference and built-in safety.

---

## ✨ Highlights
- **CPU-only** compact-transformer intent classification.
- **E2E latency target < 50 ms** (NLP + MAVLink + Pixhawk actuation).
- **Confidence gate + fail-safe hover/hold** for uncertain predictions.
- **7 core intents:** `move`, `altitude`, `rotate`, `hover`, `takeoff`, `land`, `emergency_stop`.

---

## 🗂 Repository Layout
