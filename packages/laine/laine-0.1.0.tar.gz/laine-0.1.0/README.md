## 🌊 Laine

A CLI tool to download and deobfuscate Comic-Days manga chapters.

### 🪐 Features

- Downloads all pages of a Comic-Days chapter.
- Deobfuscates scrambled image blocks.
- Restores any missing transparency on the right side.
- Saves pages as PNG images inside a ZIP archive.

### 🧩 Requirements

- Python `3.7` or higher

Dependencies are automatically installed with `pip`:

- `requests`
- `beautifulsoup4`
- `pillow`
- `tqdm`
- `lxml`

### 🚀 Installation

```bash
pip install laine
```

> 🔒 Make sure you have Python 3.7+ and pip installed.

### ✨ Usage

Once installed, run the command:

```bash
laine
```

You'll be prompted to enter a valid chapter ID, and the result will be a ZIP archive containing clean, deobfuscated PNG images of the manga chapter.

### ❓ Example

If the chapter URL is:

```md
https://comic-days.com/episode/2550912965469911422
```

You have to use just the ID:

```md
2550912965469911422
```

### 📜 License

This project is available under the [MIT License](LICENSE).

### Disclaimer

This tool is intended for `educational` and `personal use` only. Please respect the terms of service of Comic-Days and any applicable copyright laws.