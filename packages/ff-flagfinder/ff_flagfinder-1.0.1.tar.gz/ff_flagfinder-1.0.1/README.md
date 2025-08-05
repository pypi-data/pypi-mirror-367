# FF - FlagFinder

**FF - FlagFinder** is a CLI tool to extract CTF-style flags from authenticated pages using cookies, headers, or session files. Ideal for CTF players and pentesters automating post-authentication access.

---

## 🎯 Features

- 🔐 Supports authenticated requests using:
  - Session file (from [LP-LoginParser](https://github.com/Ph4nt01/LP-LoginParser))
  - Custom cookies and headers
- 🎯 Flexible flag detection:
  - Exact flag match
  - Regex pattern match
  - Auto-detect common CTF flag formats
- 📂 Saves response HTML (`debug.html`)
- 📝 Saves detected flag(s) to file

---

## 📦 Installation

### ✅ Install via `pipx` (recommended)

```bash
pipx install ff-flagfinder
````

### Or via pip:

```bash
pip install ff-flagfinder
```

---

## 🚀 Usage Examples

### 🔍 Exact Flag Match

```bash
ff -fu https://target.com/flag -f CTF{example_flag}
```

### 🧠 Regex Pattern Match

```bash
ff -fu https://target.com/flag -f "picoCTF{.*?}" -r
```

### 📦 Using Session File

```bash
ff -fu https://target.com/flag -f FLAG{123} -s session.json
```

### 🍪 With Cookies / Headers

```bash
ff -fu https://target.com/flag -f HTB{.*} \
   -ck sessionid=abc123 \
   -hd "User-Agent: Mozilla/5.0" \
   -r
```

---

## 🛠 Options

|Option|Description|
|---|---|
|`-fu`, `--flagurl`|URL to the page where the flag is located (required)|
|`-f`, `--flag`|Flag or regex pattern to match|
|`-r`, `--regex`|Treat `-f` as a regex pattern|
|`-s`, `--session`|JSON session file (cookies/headers from LP-LoginParser)|
|`-ck`, `--cookie`|Custom cookies (e.g., `sessionid=abc123`)|
|`-hd`, `--header`|Custom headers (e.g., `"User-Agent: Firefox"`)|
|`-o`, `--output`|Output file name (default: `flag.txt`)|

---

## 🔍 Auto-Detected Flag Formats

If no `--flag` is provided, it searches for:

- `CTF{.*?}`
    
- `FLAG{.*?}`
    
- `HTB{.*?}`
    
- `picoCTF{.*?}`
    
- `AKASEC{.*?}`
    

---

## 📁 Output Files

- `debug.html` → full response content
    
- `flag.txt` → extracted flag(s)
    

---

## 📜 License

Licensed under the [MIT License](https://chatgpt.com/g/g-JtV1tF7gf-git-expert-ugithub-gitlabu/c/LICENSE)

---

## 👨‍💻 Author

Built by [Your Name](https://github.com/yourusername)  
🔗 Project repo: [github.com/yourusername/ff-flagfinder](https://github.com/yourusername/ff-flagfinder)

```

Let me know if you want help publishing it to PyPI or writing a GitHub Actions CI/CD for it 🚀
```
