[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/Etw90P0Z)
# DIPPID and Pyglet

---
Assignment 1 for the Interactive Techniques and Technologies course (ITT), Universität Regensburg.

Author: Martina Roby Culasso

## Exercise 1 — DIPPID Sender
Simulates an input device by sending accelerometer and button data via the DIPPID protocol over UDP to localhost.

## Exercise 2 — 2D Game
A side-scrolling underwater game built with pyglet, controlled using accelerometer and button data from an M5Stack transmitted via the DIPPID protocol over UDP.

---
Each folder contains an `info.txt` file with a description of the files and relevant notes.

---
## Setup

```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
source .venv/bin/activate # macOS/Linux
pip install -r requirements.txt
```

## How to run

**Exercise 1 — DIPPID Sender:**
```bash
cd dippid_sender
python DIPPID_sender.py
```

**Exercise 2 — 2D Game:**
```bash
cd 2d_game
python game_dippid.py
```
> **Note:** Requires an M5Stack device connected to the same network and sending data via DIPPID on port 5700.