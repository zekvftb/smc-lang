# 🎨 SMC Visual Studio Code Extension

Syntax highlighting and language grammar support for the **SMC (Saturday Morning Cartoons)** programming language.

---

## ⚡ 1-Minute Installation

To enable syntax highlighting in your Visual Studio Code:

### Option 1: Symlink or Copy to Extensions Folder (Easiest)
Copy or link this `vscode` folder into your VS Code extensions directory:

**Windows PowerShell:**
```powershell
Copy-Item -Recurse D:\smc_lang\editors\vscode "$HOME\.vscode\extensions\smc-lang"
```

**Mac / Linux:**
```bash
cp -r /path/to/smc_lang/editors/vscode ~/.vscode/extensions/smc-lang
```

### Option 2: Reload VS Code
1. Open VS Code.
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac).
3. Type **"Developer: Reload Window"** and press Enter.

Now, any `.smc` file you open will automatically light up with beautiful, full-color syntax highlighting!
