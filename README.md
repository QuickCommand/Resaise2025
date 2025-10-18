# QuickCommand (ReSAISE 2025)

A low-latency, **CPU-only** NLP → MAVLink pipeline for reliable UAV telepresence. QuickCommand maps natural-language flight commands to Pixhawk control with a strict end-to-end latency target of **< 50 ms**, including NLP inference, MAVLink dispatch, and flight-controller actuation.

---

## Overview

- **Objective:** Natural-language teleoperation of UAVs with real-time safety guarantees.
- **Approach:** Compact transformer intent classification → parameter extraction → MAVLink translation → Pixhawk dispatch.
- **Safety:** Confidence gating with automatic **hover/hold** fallback for uncertain predictions.

---

## Features

- Seven intents: `move`, `altitude`, `rotate`, `hover`, `takeoff`, `land`, `emergency_stop`
- On-device, offline execution (no cloud dependency)
- GUI hooks for live latency monitoring
- Reproducible dataset generation and evaluation scripts

---

## Repository Structure

