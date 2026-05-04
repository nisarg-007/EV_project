"""Apply Main branch color palette to all Final_v1 files."""
import os

BASE = os.path.dirname(os.path.abspath(__file__))

FILES = [
    "app.py",
    os.path.join("pages", "1_Dashboard.py"),
    os.path.join("pages", "2_Chat.py"),
    os.path.join("pages", "4_Forecast.py"),
    os.path.join("src", "components", "sidebar.py"),
    os.path.join("src", "components", "metrics.py"),
    os.path.join("src", "pages", "charger_optimizer.py"),
    os.path.join("src", "tools", "chart_tool.py"),
]

# Order matters — do specific long strings before short substrings
REPLACEMENTS = [
    # Fonts (long strings first)
    ("family=Inter:wght@300;400;500;600;700;800;900", "family=Syne:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600;700&family=Manrope:wght@300;400;500;600;700;800"),
    ("family=Inter:wght@300;400;500;600;700;800", "family=Syne:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600;700&family=Manrope:wght@300;400;500;600;700;800"),
    ("family=Inter:wght@400;600;700;800;900", "family=Syne:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600;700&family=Manrope:wght@300;400;500;600;700;800"),
    ("family=Inter:wght@400;600;700;800", "family=Syne:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600;700&family=Manrope:wght@300;400;500;600;700;800"),
    ("'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif", "'Manrope', -apple-system, sans-serif"),
    ("'Inter', -apple-system, BlinkMacSystemFont, sans-serif", "'Manrope', -apple-system, sans-serif"),
    ("'Inter',-apple-system,sans-serif", "'Manrope',-apple-system,sans-serif"),
    ("'Inter',sans-serif", "'Manrope','IBM Plex Mono',sans-serif"),
    ("'Inter', sans-serif", "'Manrope', 'IBM Plex Mono', sans-serif"),
    ("Inter,sans-serif", "'Manrope','IBM Plex Mono',sans-serif"),

    # Primary accent: cyan -> volt
    ("#00D4FF", "#CCFF00"),
    ("0,212,255", "204,255,0"),

    # Secondary: purple -> ice
    ("#7C3AED", "#2DD4BF"),
    ("124,58,237", "45,212,191"),

    # Tertiary: pink -> ember
    ("#F72585", "#FF6B35"),
    ("247,37,133", "255,107,53"),

    # Backgrounds (specific to general)
    ("#0B0E18", "#0A0A10"),
    ("#0F1623", "#0E0E14"),
    ("#162032", "#14180E"),
    ("#1E3A5F", "#2A3518"),
    ("#08090F", "#08080C"),
    ("#0D1117", "#0E0E14"),
    ("#111827", "#121218"),
    ("#09101A", "#0A0A10"),

    # Borders
    ("#263348", "#2A2A38"),
    ("#243045", "#2A2A38"),
    ("#1A2236", "#1E1E2A"),
    ("#1E293B", "#1E1E2A"),

    # Text
    ("#F8FAFC", "#EAEAF0"),
    ("#F1F5F9", "#EAEAF0"),
    ("#E2E8F0", "#B0B0C0"),
    ("#CBD5E1", "#B0B0C0"),
    ("#94A3B8", "#6B6B80"),
    ("#64748B", "#6B6B80"),
    ("#475569", "#3A3A4E"),
    ("#334155", "#3A3A4E"),
]

for relpath in FILES:
    fpath = os.path.join(BASE, relpath)
    if not os.path.isfile(fpath):
        print(f"SKIP: {relpath}")
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    for old, new in REPLACEMENTS:
        content = content.replace(old, new)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK: {relpath}")

print("\nDone — Main branch palette applied to all Final_v1 files.")
