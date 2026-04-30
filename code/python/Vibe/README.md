# Paddle Ball

A classic arcade paddle-ball game built entirely in Python with `tkinter` — no external game engine required.

---

## How This Was Made

This project was **vibe coded** from scratch with Claude (Anthropic) in a single session.
"Vibe coding" means describing what you want in plain English and iterating with an AI until it exists.
The full arc of this session:

1. Claude wrote the initial game from a description
2. Stuttering → performance pass (timer resolution, z-order, cached color state)
3. Ball passing through paddle corners → collision fix (radius-aware hit zone)
4. 8-bit beep sounds → `winsound` cycling through 3 pitches on every hit
5. Fullscreen text squishing → height-scaling fix for all static screens
6. Background music → Windows MCI (`winmm.dll`) plays the MP3 on game start, stops on loss
7. Volume controls → scroll wheel, M to mute, headphone toggle button, vol indicator
8. PyCharm type warnings → cleaned up font types, float/int mismatches, duplicate fragments
9. This README

---

## Requirements

- Python 3.11+
- Tkinter
- Windows (for beep sounds and MP3 playback via `winsound` / Windows MCI)
- The MP3 file must be in the same folder as `paddle_ball.py`

---

## How to Play

```
python paddle_ball.py
```

Click anywhere to start. Keep the ball from falling off the bottom.
Every hit speeds the ball up. Every 5 hits it gets a bigger boost.

---

## Controls

| Input | Action |
|---|---|
| Mouse | Move paddle |
| ← → arrow keys | Move paddle |
| M | Mute / unmute |
| Scroll wheel | Volume up / down |
| F11 | Toggle fullscreen |
| Escape | Exit fullscreen |
| 🎧 button | Enable / disable music (top-right corner) |
| ⛶ button | Fullscreen (top-right corner) |

---

## Power-ups

Power-ups fall from the top and are collected by the ball.

| Icon | Name | Effect | Duration |
|---|---|---|---|
| `x2` | Split | Duplicates all balls (max 8) | Permanent |
| `+W` | Wide | Widens the paddle | ~10 s |
| `+B` | Big Ball | Enlarges the ball | ~10 s |
| `-W` | Narrow | Shrinks the paddle | ~10 s |

---

## Features

- **Sweep-based collision** — no tunneling at high speed; ball can't clip through paddle corners
- **Reflective wall bouncing** — preserves momentum through walls instead of clamping
- **Particle bursts** — fire-orange explosion on every paddle hit and power-up collect
- **8-bit beep** — three cycling pitches (A4 → C#5 → E5) on each hit, played in a background thread so it never stutters the game
- **Background music** — loops the bundled MP3 via Windows MCI; starts on game start, stops on loss
- **Volume control** — scroll wheel adjusts in 5% steps, M key mutes, 🎧 button disables entirely; a HUD indicator fades after 1.5 s
- **Power-up system** — weighted random spawns, timed effects, visual HUD countdown
- **Fullscreen support** — F11 or button; all positions and font sizes scale with both screen width and height
- **High score** — best streak persists across rounds in the same session
- **60 fps loop** — Windows timer resolution bumped to 1 ms (`timeBeginPeriod`) for smooth scheduling

---

## Project Structure

```
Vibe/
├── paddle_ball.py                              # entire game (~800 lines)
└── 2021-08-30_-_Boss_Time_-_www.FesliyanStudios.com.mp3
```

---

## What Now?

Some ideas if you want to keep going:

- **High score persistence** — save `best` to a file so it survives between sessions
- **Difficulty levels** — a menu choice that sets starting speed and power-up rates
- **More power-ups** — slow-mo, sticky paddle, multi-hit brick targets, shrink ball
- **Brick layer** — add a row of breakable bricks at the top for a Breakout mode
- **Lives system** — start with 3 lives instead of instant game-over
- **Online leaderboard** — POST the score to a simple Flask endpoint
- **Sound effects for power-ups** — different pitch/melody per power-up type
- **Cross-platform audio** — swap Windows MCI for `pygame.mixer` to support Mac/Linux
- **Animated title screen** — bouncing demo ball behind the menu text
- **Replay system** — record inputs and play back the best round

---

*Built with Python, tkinter, and vibes.*
