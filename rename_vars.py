"""Rename CSS variable names to match Main branch naming convention."""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
FILES = [
    "app.py",
    os.path.join("pages", "1_Dashboard.py"),
    os.path.join("pages", "2_Chat.py"),
    os.path.join("pages", "4_Forecast.py"),
]

RENAMES = [
    ("--cyan:", "--volt:"),
    ("--purple:", "--ice:"),
    ("--pink:", "--ember:"),
    ("var(--cyan)", "var(--volt)"),
    ("var(--purple)", "var(--ice)"),
    ("var(--pink)", "var(--ember)"),
]

for relpath in FILES:
    fpath = os.path.join(BASE, relpath)
    if not os.path.isfile(fpath):
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    for old, new in RENAMES:
        content = content.replace(old, new)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK: {relpath}")

print("Done — CSS variables renamed.")
