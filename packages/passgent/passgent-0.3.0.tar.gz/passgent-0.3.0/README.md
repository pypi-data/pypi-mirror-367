# passgent

**`passgent`** is a lightweight Python module to generate a password with custom arguments and password amounts.

---

## 🔧 Features

- Generate many password with suffixies and symbol.
- Doesn't require a module.

---

## 📦 Installation

If using locally, just save `passgent.py` in your project directory.

```bash
pip install passgent
```

---

## Code example:
```python
import passgent as g

keywords = ["admin", "dashboard"]
years = ["2024"]
symbols = ["@"]
suffixes = ["123"]

generate=g.setup(keywords, years, symbols, suffixes)
generate=generate.generate(10)
print(generate)
```

---

## Without args:
```python
import passgent as g

generate=g.setup()
generate=generate.generate(10)
print(generate)
```
---

```

## Output:
['Adminmanager#2021', 'Adm1n15tr4t0r%4dm1n4pp5', 'ADMINLOGIN%2023', 'ADMIN@ADMINISTRATORl0g1n', 'ADMIN%Adm1n15tr4t0rp455', 'MANAGER@4dm1n15tr4t0rl0g1n', 'loginADMIN#2024', 'L0g1nDASHBOARDp455', 'adminDASHBOARD123', 'Managerdashboardapps']
```
