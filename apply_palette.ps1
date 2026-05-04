# Apply Main branch color palette to Final_v1
# Maps: cyan->volt, purple->ice, pink->ember, updates backgrounds/text/fonts

$files = @(
    "app.py",
    "pages\1_Dashboard.py",
    "pages\2_Chat.py",
    "pages\4_Forecast.py",
    "src\components\sidebar.py",
    "src\components\metrics.py",
    "src\pages\charger_optimizer.py",
    "src\tools\chart_tool.py"
)

$replacements = @(
    # === CSS VARIABLE NAMES ===
    @("--cyan:", "--volt:"),
    @("--purple:", "--ember-alt:"),
    @("--pink:", "--ember:"),
    @("var(--cyan)", "var(--volt)"),
    @("var(--purple)", "var(--ice)"),
    @("var(--pink)", "var(--ember)"),

    # === PRIMARY ACCENT: cyan #00D4FF -> volt #CCFF00 ===
    @("#00D4FF", "#CCFF00"),
    @("0,212,255", "204,255,0"),

    # === SECONDARY: purple #7C3AED -> ice #2DD4BF ===
    @("#7C3AED", "#2DD4BF"),
    @("124,58,237", "45,212,191"),

    # === TERTIARY: pink #F72585 -> ember #FF6B35 ===
    @("#F72585", "#FF6B35"),
    @("247,37,133", "255,107,53"),

    # === BACKGROUNDS ===
    @("#08090F", "#08080C"),
    @("#0D1117", "#0E0E14"),
    @("#111827", "#121218"),
    @("#09101A", "#0A0A10"),
    @("#0B0E18", "#0A0A10"),
    @("#0F1623", "#0E0E14"),
    @("#162032", "#14180E"),
    @("#1E3A5F", "#2A3518"),

    # === BORDERS ===
    @("#1A2236", "#1E1E2A"),
    @("#1E293B", "#1E1E2A"),
    @("#243045", "#2A2A38"),
    @("#263348", "#2A2A38"),

    # === TEXT COLORS ===
    @("#F1F5F9", "#EAEAF0"),
    @("#F8FAFC", "#EAEAF0"),
    @("#CBD5E1", "#B0B0C0"),
    @("#E2E8F0", "#B0B0C0"),
    @("#64748B", "#6B6B80"),
    @("#94A3B8", "#6B6B80"),
    @("#475569", "#3A3A4E"),
    @("#334155", "#3A3A4E"),

    # === FONTS ===
    @("@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');", "@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600;700&family=Manrope:wght@300;400;500;600;700;800&display=swap');"),
    @("@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');", "@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600;700&family=Manrope:wght@300;400;500;600;700;800&display=swap');"),
    @("@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');", "@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600;700&family=Manrope:wght@300;400;500;600;700;800&display=swap');"),
    @("@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');", "@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600;700&family=Manrope:wght@300;400;500;600;700;800&display=swap');"),
    @("'Inter', -apple-system, BlinkMacSystemFont, sans-serif", "'Manrope', -apple-system, sans-serif"),
    @("'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif", "'Manrope', -apple-system, sans-serif"),
    @("'Inter',sans-serif", "'Manrope','IBM Plex Mono',sans-serif"),
    @("'Inter', sans-serif", "'Manrope', sans-serif"),
    @("'Inter',sans-serif", "'Manrope',sans-serif"),
    @("font-family:Inter,sans-serif", "font-family:'Manrope','IBM Plex Mono',sans-serif"),

    # === PLOTLY CHART COLORS (Python lists) ===
    @("'#CCFF00','#2DD4BF','#FF6B35','#10B981','#F59E0B'", "'#CCFF00','#2DD4BF','#FF6B35','#10B981','#F59E0B'"),

    # === CSS VARIABLE BLOCK FIXES (rename vars properly) ===
    @("--volt:", "--volt:"),
    @("--ember-alt:", "--ice:"),
    @("--ember:", "--ember:")
)

$base = "c:\Users\nisar\OneDrive\Documents\SEM 2\AI for engineers\EV_project\final_v_1"

foreach ($file in $files) {
    $path = Join-Path $base $file
    if (Test-Path $path) {
        $content = Get-Content $path -Raw -Encoding UTF8
        foreach ($r in $replacements) {
            $content = $content.Replace($r[0], $r[1])
        }
        Set-Content $path $content -NoNewline -Encoding UTF8
        Write-Host "Updated: $file"
    } else {
        Write-Host "SKIP (not found): $file"
    }
}

Write-Host "`nDone! All files updated with Main branch palette."
