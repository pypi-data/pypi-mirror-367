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
import passgent as generate_password

keyword = ["admin", "dashboard", "login", "administrator", "manager"]
year = ["2021", "2022", "2023", "2024", "2025"]
symbols = ["#", "@", "_", "-", "+", "*", "%"]
suffix = ["pass", "123", "admin", "dashboard", "login", "web", "apps"]
password = generate_password(keyword, year, symbols, suffix).generate(10)
print(password)
```

---

## Without args:
```python
import passgent as generate_password

password = generate_password().generate(10)
print(password)
```
---

```

## Output:
``` bash
['Adminmanager#2021', 'Adm1n15tr4t0r%4dm1n4pp5', 'ADMINLOGIN%2023', 'ADMIN@ADMINISTRATORl0g1n', 'ADMIN%Adm1n15tr4t0rp455', 'MANAGER@4dm1n15tr4t0rl0g1n', 'loginADMIN#2024', 'L0g1nDASHBOARDp455', 'adminDASHBOARD123', 'Managerdashboardapps']
```
