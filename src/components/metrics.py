"""
KPI card component with glassmorphism styling and animated counters.
Call render_kpi_cards() from any Streamlit page that needs the top-line metrics.
"""

import streamlit as st
import streamlit.components.v1 as components

_KPI_CSS = """
<style>
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1.1rem;
    margin-bottom: 1.5rem;
}
@media (max-width: 900px) {
    .kpi-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 500px) {
    .kpi-grid { grid-template-columns: 1fr; }
}
.kpi-card {
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 18px;
    padding: 1.4rem 1.5rem 1.2rem;
    position: relative;
    overflow: hidden;
    transition: transform 0.22s ease, box-shadow 0.22s ease;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #2DD4BF, #CCFF00);
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 32px rgba(0, 212, 255, 0.10), 0 4px 16px rgba(0, 0, 0, 0.35);
    border-color: rgba(0, 212, 255, 0.22);
}
.kpi-label {
    color: #6B6B80;
    font-size: 0.66rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.45rem;
}
.kpi-value {
    color: #CCFF00;
    font-size: 1.75rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1.1;
}
.kpi-delta {
    color: #2DD4BF;
    font-size: 0.74rem;
    font-weight: 600;
    margin-top: 0.3rem;
}
@keyframes kpi-count-up {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
.kpi-value {
    animation: kpi-count-up 0.6s ease-out both;
}
</style>
"""

_COUNT_UP_JS = """
<script>
(function() {
    function animateCount(el, target, duration) {
        var start = 0;
        var startTime = null;
        var isFloat = target % 1 !== 0;
        function step(ts) {
            if (!startTime) startTime = ts;
            var progress = Math.min((ts - startTime) / duration, 1);
            var ease = 1 - Math.pow(1 - progress, 3);
            var current = start + (target - start) * ease;
            el.textContent = isFloat
                ? current.toFixed(1) + "%"
                : Math.round(current).toLocaleString();
            if (progress < 1) requestAnimationFrame(step);
            else el.textContent = isFloat
                ? target.toFixed(1) + "%"
                : target.toLocaleString();
        }
        requestAnimationFrame(step);
    }
    document.querySelectorAll('[data-kpi-target]').forEach(function(el) {
        var raw = el.getAttribute('data-kpi-target');
        var target = parseFloat(raw);
        if (!isNaN(target)) animateCount(el, target, 1200);
    });
})();
</script>
"""


def render_kpi_cards(
    total_evs: int,
    yoy_growth: float,
    top_county: str,
    top_make: str,
) -> None:
    """
    Render 4 glassmorphism KPI cards with animated count-up values.

    Args:
        total_evs:   Total EV registration count.
        yoy_growth:  Year-over-year growth percent (e.g. 12.4 for 12.4%).
        top_county:  Name of the leading county.
        top_make:    Most-registered EV manufacturer.
    """
    html = f"""
    {_KPI_CSS}
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-label">Total EVs</div>
            <div class="kpi-value" data-kpi-target="{total_evs}">{total_evs:,}</div>
            <div class="kpi-delta">Washington State</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">YoY Growth</div>
            <div class="kpi-value" data-kpi-target="{yoy_growth}">{yoy_growth:.1f}%</div>
            <div class="kpi-delta">vs prior year</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Top County</div>
            <div class="kpi-value" style="font-size:1.35rem;">{top_county}</div>
            <div class="kpi-delta">leads registrations</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Top Manufacturer</div>
            <div class="kpi-value" style="font-size:1.35rem;">{top_make}</div>
            <div class="kpi-delta">by registration count</div>
        </div>
    </div>
    {_COUNT_UP_JS}
    """
    components.html(html, height=160, scrolling=False)
