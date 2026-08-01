"""
Shared design system for the N100 Analytics dashboard.

This module centralizes all styling so every page looks and behaves
consistently:

    - apply_global_theme()  -> inject the CSS design system (call once,
                                 from app.py, before any page renders)
    - render_sidebar_nav()  -> render the branded sidebar navigation bar
    - page_header()         -> render a consistent gradient page title
                                 + optional subtitle, used instead of
                                 st.title() on every page

Brand palette
-------------
Primary   #6C63FF  (indigo)
Secondary #FF6B9D  (pink)
Accent    #FFB86C  (amber)
Success   #198754
Danger    #DC3545
"""

import streamlit as st

PRIMARY = "#6C63FF"
SECONDARY = "#FF6B9D"
ACCENT = "#FFB86C"
SUCCESS = "#198754"
DANGER = "#DC3545"


def apply_global_theme() -> None:
    """Inject the single, shared CSS design system for the whole app.

    Call this exactly once per run (from app.py). Individual pages should
    NOT define their own inject_css()/st.set_page_config() anymore -
    that responsibility now lives here so every page renders identically.
    """

    st.markdown(
        """
        <style>

        /* =====================================================
           Fonts & base layout
           ===================================================== */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(14px); }
            to   { opacity: 1; transform: translateY(0); }
        }

        @keyframes shimmer {
            0%   { background-position: 0% center; }
            100% { background-position: 200% center; }
        }

        .main .block-container {
            animation: fadeInUp 0.5s ease-out;
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1400px;
        }

        /* =====================================================
           Headings
           ===================================================== */
        h1 {
            background: linear-gradient(90deg, #6C63FF, #FF6B9D, #FFB86C);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: shimmer 6s linear infinite;
            font-weight: 800 !important;
            letter-spacing: -0.5px;
        }

        h2, h3 {
            font-weight: 700 !important;
            border-left: 4px solid #6C63FF;
            padding-left: 0.6rem;
            animation: fadeInUp 0.6s ease-out;
        }

        /* Page subtitle / caption under the main title */
        .n100-page-subtitle {
            color: rgba(120, 120, 140, 0.9);
            font-size: 1rem;
            margin-top: -0.6rem;
            margin-bottom: 1.2rem;
            animation: fadeInUp 0.7s ease-out;
        }

        /* =====================================================
           KPI metric cards
           ===================================================== */
        div[data-testid="stMetric"] {
            background: linear-gradient(135deg, rgba(108,99,255,0.08), rgba(255,107,157,0.08));
            border: 1px solid rgba(108,99,255,0.25);
            border-radius: 16px;
            padding: 1rem 1rem 0.6rem 1rem;
            box-shadow: 0 4px 14px rgba(0,0,0,0.06);
            transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
            animation: fadeInUp 0.7s ease-out;
        }

        div[data-testid="stMetric"]:hover {
            transform: translateY(-6px) scale(1.02);
            box-shadow: 0 10px 24px rgba(108,99,255,0.25);
            border-color: #6C63FF;
        }

        div[data-testid="stMetricLabel"] {
            font-weight: 600;
            opacity: 0.75;
        }

        div[data-testid="stMetricValue"] {
            font-size: 1.6rem !important;
            font-weight: 800 !important;
        }

        /* =====================================================
           Dividers
           ===================================================== */
        hr {
            margin-top: 1.2rem;
            margin-bottom: 1.2rem;
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, #6C63FF, transparent);
            animation: fadeInUp 0.8s ease-out;
        }

        /* =====================================================
           Charts, tables, expanders
           ===================================================== */
        div[data-testid="stDataFrame"],
        div[data-testid="stExpander"] {
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 4px 16px rgba(0,0,0,0.06);
            transition: box-shadow 0.25s ease, transform 0.25s ease;
            animation: fadeInUp 0.8s ease-out;
        }

        /* Plotly charts intentionally have NO entrance animation and NO
           overflow:hidden. Pages like profile.py redraw the same chart
           container many times per second (key changes every frame) to
           build hand-rolled "Play Animation" transitions - a CSS fade-in
           here would restart on every single frame and fight with that,
           making the animation look broken. Keep only a subtle hover. */
        div[data-testid="stPlotlyChart"] {
            border-radius: 16px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.06);
            transition: box-shadow 0.25s ease;
        }

        div[data-testid="stPlotlyChart"]:hover {
            box-shadow: 0 10px 26px rgba(0,0,0,0.12);
        }

        div[data-testid="stDataFrame"]:hover {
            box-shadow: 0 10px 26px rgba(0,0,0,0.12);
            transform: translateY(-3px);
        }

        /* =====================================================
           Inputs (selectbox, multiselect, text input, sliders)
           ===================================================== */
        div[data-testid="stSelectbox"] label,
        div[data-testid="stMultiSelect"] label,
        div[data-testid="stTextInput"] label,
        div[data-testid="stSlider"] label {
            font-weight: 700;
            color: #6C63FF;
        }

        div[data-baseweb="select"] {
            border-radius: 10px !important;
            transition: box-shadow 0.25s ease;
        }

        div[data-baseweb="select"]:hover {
            box-shadow: 0 0 0 2px rgba(108,99,255,0.3);
        }

        /* =====================================================
           Alerts / banners
           ===================================================== */
        div[data-testid="stAlert"] {
            border-radius: 12px;
            animation: fadeInUp 0.6s ease-out;
            transition: transform 0.2s ease;
        }

        div[data-testid="stAlert"]:hover {
            transform: translateY(-2px);
        }

        /* =====================================================
           Buttons
           ===================================================== */
        div[data-testid="stDownloadButton"] button,
        div[data-testid="stButton"] button {
            border-radius: 10px;
            font-weight: 700;
            background: linear-gradient(90deg, #6C63FF, #FF6B9D);
            color: white;
            border: none;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        div[data-testid="stDownloadButton"] button:hover,
        div[data-testid="stButton"] button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 18px rgba(108,99,255,0.35);
            color: white;
        }

        /* =====================================================
           Tabs
           ===================================================== */
        button[data-baseweb="tab"] {
            font-weight: 600;
            border-radius: 10px 10px 0 0 !important;
        }

        div[data-baseweb="tab-highlight"] {
            background-color: #6C63FF !important;
            height: 3px !important;
        }

        /* =====================================================
           Caption / footer text
           ===================================================== */
        .stCaption, [data-testid="stCaptionContainer"] {
            opacity: 0.7;
            animation: fadeInUp 0.9s ease-out;
        }

        /* =====================================================
           Small reusable badges (status pills used across pages)
           ===================================================== */
        .n100-badge-ok {
            background: #198754;
            padding: 5px 12px;
            border-radius: 20px;
            color: white;
            font-size: 13px;
            font-weight: 700;
            display: inline-block;
        }

        .n100-badge-bad {
            background: #DC3545;
            padding: 5px 12px;
            border-radius: 20px;
            color: white;
            font-size: 13px;
            font-weight: 700;
            display: inline-block;
        }

        /* Backwards-compatible aliases for existing per-page markup */
        .report-ok { background:#198754; padding:5px 12px; border-radius:20px; color:white; font-size:13px; font-weight:700; display:inline-block; }
        .report-bad { background:#DC3545; padding:5px 12px; border-radius:20px; color:white; font-size:13px; font-weight:700; display:inline-block; }

        .n100-card, .pdf-card {
            padding: 16px;
            border-radius: 16px;
            border: 1px solid rgba(108,99,255,0.18);
            margin-bottom: 14px;
            box-shadow: 0 3px 12px rgba(0,0,0,0.05);
            transition: transform 0.25s ease, box-shadow 0.25s ease;
            animation: fadeInUp 0.7s ease-out;
        }

        .n100-card:hover, .pdf-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 20px rgba(108,99,255,0.18);
        }

        /* =====================================================
           SIDEBAR — brand header + navigation bar
           ===================================================== */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(108,99,255,0.07), rgba(255,107,157,0.03));
            border-right: 1px solid rgba(108,99,255,0.12);
        }

        section[data-testid="stSidebar"] .block-container {
            padding-top: 1.5rem;
        }

        .n100-brand {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 4px 4px 18px 4px;
            margin-bottom: 6px;
            border-bottom: 1px solid rgba(108,99,255,0.18);
            animation: fadeInUp 0.5s ease-out;
        }

        .n100-brand-logo {
            font-size: 2rem;
            line-height: 1;
            filter: drop-shadow(0 2px 6px rgba(108,99,255,0.35));
        }

        .n100-brand-title {
            font-weight: 800;
            font-size: 1.15rem;
            background: linear-gradient(90deg, #6C63FF, #FF6B9D);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1.2;
        }

        .n100-brand-sub {
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            opacity: 0.6;
        }

        .n100-nav-label {
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            opacity: 0.55;
            margin: 10px 2px 6px 2px;
        }

        /* Restyle the radio group as a pill navigation bar */
        section[data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] {
            gap: 4px;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label {
            background: transparent;
            border: 1px solid transparent;
            border-radius: 12px;
            padding: 10px 12px !important;
            margin-bottom: 2px;
            width: 100%;
            transition: all 0.18s ease;
            cursor: pointer;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
            background: rgba(108,99,255,0.10);
            border-color: rgba(108,99,255,0.25);
            transform: translateX(3px);
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] p {
            font-weight: 600;
            font-size: 0.95rem;
            margin: 0;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label input[type="radio"] {
            accent-color: #6C63FF;
        }

        /* Highlight the selected nav item (modern browsers) */
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {
            background: linear-gradient(90deg, rgba(108,99,255,0.28), rgba(255,107,157,0.16));
            border-color: #6C63FF;
            box-shadow: 0 4px 14px rgba(108,99,255,0.25);
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) p {
            color: #6C63FF;
            font-weight: 800;
        }

        .n100-sidebar-footer {
            margin-top: 24px;
            padding-top: 14px;
            border-top: 1px solid rgba(108,99,255,0.15);
            font-size: 0.72rem;
            opacity: 0.55;
            line-height: 1.4;
            animation: fadeInUp 1s ease-out;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(icon: str, title: str, subtitle: str | None = None) -> None:
    """Render a consistent gradient page title (+ optional subtitle).

    Use this instead of st.title() so every page shares the same look.
    """

    st.title(f"{icon} {title}")
    if subtitle:
        st.markdown(
            f'<div class="n100-page-subtitle">{subtitle}</div>',
            unsafe_allow_html=True,
        )


def render_sidebar_nav(pages: dict) -> str:
    """Render the branded sidebar navigation bar and return the selected page key.

    `pages` maps page_key -> {"label": str, "icon": str}. Order is preserved,
    so the dict's insertion order defines the nav order.
    """

    with st.sidebar:
        st.markdown(
            """
            <div class="n100-brand">
                <div class="n100-brand-logo">📊</div>
                <div>
                    <div class="n100-brand-title">N100 Analytics</div>
                    <div class="n100-brand-sub">Nifty 100 Financial Platform</div>
                </div>
            </div>
            <div class="n100-nav-label">Navigate</div>
            """,
            unsafe_allow_html=True,
        )

        options = list(pages.keys())
        labels = {key: f"{meta['icon']}  {meta['label']}" for key, meta in pages.items()}

        choice_label = st.radio(
            "Navigation",
            options=[labels[key] for key in options],
            label_visibility="collapsed",
            key="n100_nav_radio",
        )

        st.markdown(
            """
            <div class="n100-sidebar-footer">
                Nifty 100 company fundamentals &amp; screening<br/>
                Data refreshed periodically from filings
            </div>
            """,
            unsafe_allow_html=True,
        )

    for key in options:
        if labels[key] == choice_label:
            return key
    return options[0]
