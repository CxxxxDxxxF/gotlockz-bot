# GotLockz Bot

A collaborative Discord bot project that reads Fanatics bet slips and posts AI-generated analysis.

## Developer Roles & File Structure
- **Developer 1 (Windows 10):** `/image-processing/`
- **Developer 2 (macOS M4):** `/discord/`
- **Shared Modules:** `/shared/`

## Folder Structure
```
image-processing/
discord/
shared/
```

## Getting Started
1. Clone the repository:
   ```
   git clone https://github.com/CxxxxDxxxF/gotlockz-bot.git
   cd gotlockz-bot
   ```
2. Create a feature branch:
   ```
   git checkout -b feature/<task>-win10   # for Windows dev
   git checkout -b feature/<task>-m4      # for macOS dev
   ```
3. Work only in your assigned folder or `/shared/`.
4. Coordinate before editing another dev’s folder.
5. Push your branch and open a pull request when ready.

> This project is runtime-neutral. No assumptions about Node.js, Python, or other environments are made at this stage.
