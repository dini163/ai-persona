# 🎭 AI Persona Hub

> **Curated collection of AI character prompts & system personas** from top open-source projects. Browse, search, and copy prompts for OpenClaw, Hermes Agent, Claude, ChatGPT, and more.

[![GitHub Pages](https://img.shields.io/badge/Hosted%20on-GitHub%20Pages-blue)](https://your-username.github.io/character)
[![Characters](https://img.shields.io/badge/Characters-36+-blueviolet)]()
[![Sources](https://img.shields.io/badge/Sources-4-green)]()

---

## 🚀 What Is This?

AI Persona Hub is a beautiful, searchable gallery of curated AI character prompts extracted from leading open-source agent frameworks. Each character card includes:

- **Complete system prompt** — ready to copy and use
- **Category tags** — Engineering, Design, Marketing, Game Dev, and more
- **Compatibility badges** — OpenClaw, Hermes Agent, Claude, ChatGPT, Manual
- **Source attribution** — links back to the original project

## 📦 Sources

Characters are curated from these open-source projects:

| Source | Characters | Focus |
|--------|-----------|-------|
| [🎭 The Agency](https://github.com/msitarzewski/agency-agents) | ~70+ | Engineering, Design, Marketing, Sales, Product |
| [⚔️ 三省六部 Edict](https://github.com/cft0808/edict) | 12 | Ancient Chinese imperial governance system for AI |
| [🎮 Claude Code Game Studios](https://github.com/Donchitos/Claude-Code-Game-Studios) | 49 | Game dev studio hierarchy (Directors → Leads → Specialists) |
| [🦞 ClawCompany](https://github.com/Claw-Company/clawcompany) | 38 | AI company OS (CEO, CTO, CFO, Researcher, Analyst) |

## 🛠️ How to Use

### For OpenClaw / Hermes Agent Users

1. Browse the gallery and find a character you like
2. Click the card to view the full system prompt
3. Click **"Copy Prompt"** to copy to clipboard
4. Paste into your AI assistant's system prompt configuration

### For Manual Use

Copy the prompt and paste it at the beginning of your conversation with any AI model.

## 🏗️ Tech Stack

- **Pure HTML/CSS/JS** — No build tools, no dependencies
- **GitHub Pages** — Free hosting, instant deployment
- **Glassmorphism UI** — Modern dark theme with animated backgrounds
- **Responsive** — Works on mobile, tablet, and desktop

## 📁 Project Structure

```
character/
├── index.html          ← Main gallery page
├── style.css           ← Design system (dark theme + glassmorphism)
├── app.js              ← Interactive logic (search, filter, modal, copy)
├── data/
│   └── characters.json ← All character data
├── images/
│   └── hero-banner.png ← Hero section image
└── README.md           ← This file
```

## 🤝 Contributing

Want to add a character? Edit `data/characters.json` and submit a PR:

```json
{
  "id": "your-character-id",
  "name": "Character Name",
  "emoji": "🎯",
  "category": "Category",
  "source": "source-id",
  "tags": ["Tag1", "Tag2"],
  "description": "Brief description...",
  "prompt": "Full system prompt...",
  "compatible": ["openclaw", "hermes", "claude", "chatgpt", "manual"]
}
```

## 📄 License

All character prompts are from their respective open-source repositories and follow their original licenses (mostly MIT).

---

Made with ❤️ for the AI community
