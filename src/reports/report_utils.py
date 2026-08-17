# src/reports/report_utils.py

import os
import math
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)
from reportlab.pdfbase.pdfmetrics import stringWidth


# ============================================================
# BRAND COLORS
# ============================================================

MIDNIGHT_BLUE = HexColor("#012970")
FUCHSIA_BLUE = HexColor("#6F42C1")
FLAMINGO = HexColor("#F05537")

WHITE = colors.white
BLACK = colors.black
LIGHT_GREY = HexColor("#F5F6F8")
MEDIUM_GREY = HexColor("#D9DDE5")
DARK_GREY = HexColor("#555555")
GREEN = HexColor("#198754")
RED = HexColor("#DC3545")
YELLOW = HexColor("#FFC107")


# ============================================================
# PAGE SIZE
# ============================================================

PAGE_WIDTH, PAGE_HEIGHT = A4


# ============================================================
# OUTPUT DIRECTORIES
# ============================================================

REPORTS_DIR = "reports"
TEARSHEETS_DIR = os.path.join(REPORTS_DIR, "tearsheets")
SECTORS_DIR = os.path.join(REPORTS_DIR, "sectors")


def ensure_report_directories():
    """
    Create all report output directories.
    """

    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(TEARSHEETS_DIR, exist_ok=True)
    os.makedirs(SECTORS_DIR, exist_ok=True)


# ============================================================
# STYLES
# ============================================================

def get_report_styles():
    """
    Return common ReportLab styles used throughout the reports.
    """

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=MIDNIGHT_BLUE,
            alignment=TA_LEFT,
            spaceAfter=8,
        )
    )

    styles.add(
        ParagraphStyle(
            name="ReportSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=13,
            textColor=DARK_GREY,
            spaceAfter=10,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SectionTitle",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=MIDNIGHT_BLUE,
            spaceBefore=8,
            spaceAfter=6,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SubSectionTitle",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=13,
            textColor=FUCHSIA_BLUE,
            spaceBefore=6,
            spaceAfter=4,
        )
    )

    styles.add(
        ParagraphStyle(
            name="Body",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            textColor=BLACK,
            spaceAfter=5,
        )
    )

    styles.add(
        ParagraphStyle(
            name="Small",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=7,
            leading=9,
            textColor=DARK_GREY,
        )
    )

    styles.add(
        ParagraphStyle(
            name="TableHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=7.5,
            leading=9,
            textColor=WHITE,
            alignment=TA_CENTER,
        )
    )

    styles.add(
        ParagraphStyle(
            name="TableCell",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7,
            leading=9,
            textColor=BLACK,
        )
    )

    styles.add(
        ParagraphStyle(
            name="TableCellCenter",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7,
            leading=9,
            textColor=BLACK,
            alignment=TA_CENTER,
        )
    )

    styles.add(
        ParagraphStyle(
            name="TableCellRight",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7,
            leading=9,
            textColor=BLACK,
            alignment=TA_RIGHT,
        )
    )

    styles.add(
        ParagraphStyle(
            name="KPIValue",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=16,
            textColor=MIDNIGHT_BLUE,
            alignment=TA_CENTER,
        )
    )

    styles.add(
        ParagraphStyle(
            name="KPILabel",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7,
            leading=9,
            textColor=DARK_GREY,
            alignment=TA_CENTER,
        )
    )

    styles.add(
        ParagraphStyle(
            name="Pros",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=GREEN,
            leftIndent=8,
            bulletIndent=0,
        )
    )

    styles.add(
        ParagraphStyle(
            name="Cons",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=RED,
            leftIndent=8,
            bulletIndent=0,
        )
    )

    return styles


# ============================================================
# TEXT HELPERS
# ============================================================

def safe_text(value, default="N/A"):
    """
    Safely convert a value to printable text.
    """

    if value is None:
        return default

    try:
        if hasattr(value, "__class__") and str(value) == "nan":
            return default
    except Exception:
        pass

    if isinstance(value, float):
        if math.isnan(value):
            return default

    return str(value)


def format_number(value, decimals=2):
    """
    Format a numeric value safely.
    """

    if value is None:
        return "N/A"

    try:
        if isinstance(value, float) and math.isnan(value):
            return "N/A"

        return f"{float(value):,.{decimals}f}"

    except (ValueError, TypeError):
        return safe_text(value)


def format_percent(value, decimals=2):
    """
    Format a percentage value.
    """

    if value is None:
        return "N/A"

    try:
        if isinstance(value, float) and math.isnan(value):
            return "N/A"

        return f"{float(value):.{decimals}f}%"

    except (ValueError, TypeError):
        return safe_text(value)


def format_ratio(value, decimals=2):
    """
    Format a ratio.
    """

    return format_number(value, decimals)


def clean_filename(name):
    """
    Make a safe filename for Windows/Linux.
    """

    invalid = '<>:"/\\|?*'

    name = safe_text(name, "company")

    for char in invalid:
        name = name.replace(char, "_")

    name = name.strip()

    if not name:
        name = "company"

    return name[:150]


# ============================================================
# PAGE HEADER / FOOTER
# ============================================================

def draw_page_header_footer(
    canvas,
    doc,
    title="Bluestock N100 Financial Analytics",
):
    """
    Draw consistent branded header and footer.
    """

    canvas.saveState()

    # -----------------------------
    # Header
    # -----------------------------

    canvas.setFillColor(MIDNIGHT_BLUE)

    canvas.rect(
        0,
        PAGE_HEIGHT - 12 * mm,
        PAGE_WIDTH,
        12 * mm,
        fill=1,
        stroke=0,
    )

    canvas.setFillColor(WHITE)

    canvas.setFont(
        "Helvetica-Bold",
        8,
    )

    canvas.drawString(
        15 * mm,
        PAGE_HEIGHT - 7.5 * mm,
        title,
    )

    # -----------------------------
    # Footer line
    # -----------------------------

    canvas.setStrokeColor(MEDIUM_GREY)

    canvas.line(
        15 * mm,
        10 * mm,
        PAGE_WIDTH - 15 * mm,
        10 * mm,
    )

    # -----------------------------
    # Footer text
    # -----------------------------

    canvas.setFillColor(DARK_GREY)

    canvas.setFont(
        "Helvetica",
        6.5,
    )

    canvas.drawString(
        15 * mm,
        6 * mm,
        "Bluestock N100 Financial Analytics",
    )

    canvas.drawRightString(
        PAGE_WIDTH - 15 * mm,
        6 * mm,
        f"Page {doc.page}",
    )

    canvas.restoreState()


# ============================================================
# DOCUMENT BUILDER
# ============================================================

def create_document(
    filepath,
    title="Bluestock N100 Financial Analytics",
    pagesize=A4,
):
    """
    Create a standard branded ReportLab document.
    """

    ensure_report_directories()

    return SimpleDocTemplate(
        filepath,
        pagesize=pagesize,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=18 * mm,
        bottomMargin=15 * mm,
        title=title,
        author="Bluestock N100",
        subject="Financial Analytics Report",
    )


# ============================================================
# TITLE BLOCK
# ============================================================

def title_block(
    title,
    subtitle=None,
    styles=None,
):
    """
    Create a branded title block.
    """

    if styles is None:
        styles = get_report_styles()

    elements = []

    elements.append(
        Paragraph(
            safe_text(title),
            styles["ReportTitle"],
        )
    )

    if subtitle:
        elements.append(
            Paragraph(
                safe_text(subtitle),
                styles["ReportSubtitle"],
            )
        )

    elements.append(
        Table(
            [[""]],
            colWidths=[180 * mm],
            rowHeights=[1.5 * mm],
            style=[
                ("BACKGROUND", (0, 0), (-1, -1), FLAMINGO),
                ("BOX", (0, 0), (-1, -1), 0, FLAMINGO),
            ],
        )
    )

    elements.append(Spacer(1, 5 * mm))

    return elements


# ============================================================
# KPI CARD
# ============================================================

def kpi_card(
    label,
    value,
    styles=None,
):
    """
    Create one KPI card.
    """

    if styles is None:
        styles = get_report_styles()

    data = [
        [
            Paragraph(
                safe_text(value),
                styles["KPIValue"],
            )
        ],
        [
            Paragraph(
                safe_text(label),
                styles["KPILabel"],
            )
        ],
    ]

    table = Table(
        data,
        colWidths=[38 * mm],
        rowHeights=[10 * mm, 7 * mm],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    LIGHT_GREY,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.8,
                    MEDIUM_GREY,
                ),
                (
                    "LINEBEFORE",
                    (0, 0),
                    (0, -1),
                    3,
                    FLAMINGO,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
            ]
        )
    )

    return table


# ============================================================
# KPI ROW
# ============================================================

def kpi_row(kpis, styles=None):
    """
    Create a row of KPI cards.

    kpis:
        [
            ("ROE", "18.2%"),
            ("ROCE", "21.4%"),
            ...
        ]
    """

    if styles is None:
        styles = get_report_styles()

    cards = [
        kpi_card(
            label,
            value,
            styles,
        )
        for label, value in kpis
    ]

    table = Table(
        [cards],
        colWidths=[
            43 * mm
            for _ in cards
        ],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
            ]
        )
    )

    return table


# ============================================================
# GENERIC DATA TABLE
# ============================================================

def make_table(
    headers,
    rows,
    col_widths=None,
    styles=None,
    header_color=MIDNIGHT_BLUE,
):
    """
    Create a professionally formatted table.
    """

    if styles is None:
        styles = get_report_styles()

    header_cells = [
        Paragraph(
            safe_text(header),
            styles["TableHeader"],
        )
        for header in headers
    ]

    data = [header_cells]

    for row in rows:

        formatted_row = []

        for value in row:

            formatted_row.append(
                Paragraph(
                    safe_text(value),
                    styles["TableCell"],
                )
            )

        data.append(formatted_row)

    table = Table(
        data,
        colWidths=col_widths,
        repeatRows=1,
        hAlign="LEFT",
    )

    style_commands = [

        (
            "BACKGROUND",
            (0, 0),
            (-1, 0),
            header_color,
        ),

        (
            "TEXTCOLOR",
            (0, 0),
            (-1, 0),
            WHITE,
        ),

        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.4,
            MEDIUM_GREY,
        ),

        (
            "VALIGN",
            (0, 0),
            (-1, -1),
            "MIDDLE",
        ),

        (
            "LEFTPADDING",
            (0, 0),
            (-1, -1),
            4,
        ),

        (
            "RIGHTPADDING",
            (0, 0),
            (-1, -1),
            4,
        ),

        (
            "TOPPADDING",
            (0, 0),
            (-1, -1),
            4,
        ),

        (
            "BOTTOMPADDING",
            (0, 0),
            (-1, -1),
            4,
        ),
    ]

    # Alternating rows
    for row_index in range(1, len(data)):

        if row_index % 2 == 0:

            style_commands.append(
                (
                    "BACKGROUND",
                    (0, row_index),
                    (-1, row_index),
                    HexColor("#FAFAFA"),
                )
            )

    table.setStyle(
        TableStyle(style_commands)
    )

    return table


# ============================================================
# PROS / CONS BOX
# ============================================================

def pros_cons_table(
    pros,
    cons,
    styles=None,
):
    """
    Create side-by-side Pros and Cons sections.
    """

    if styles is None:
        styles = get_report_styles()

    if not isinstance(pros, list):
        pros = [pros]

    if not isinstance(cons, list):
        cons = [cons]

    pros_items = []

    for item in pros:

        pros_items.append(
            Paragraph(
                f"• {safe_text(item)}",
                styles["Pros"],
            )
        )

    cons_items = []

    for item in cons:

        cons_items.append(
            Paragraph(
                f"• {safe_text(item)}",
                styles["Cons"],
            )
        )

    pros_content = [
        Paragraph(
            "PROS",
            ParagraphStyle(
                "ProsHeading",
                parent=styles["SubSectionTitle"],
                textColor=GREEN,
            ),
        )
    ] + pros_items

    cons_content = [
        Paragraph(
            "CONS",
            ParagraphStyle(
                "ConsHeading",
                parent=styles["SubSectionTitle"],
                textColor=RED,
            ),
        )
    ] + cons_items

    table = Table(
        [
            [
                pros_content,
                cons_content,
            ]
        ],
        colWidths=[
            87 * mm,
            87 * mm,
        ],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, 0),
                    HexColor("#F2FFF6"),
                ),
                (
                    "BACKGROUND",
                    (1, 0),
                    (1, 0),
                    HexColor("#FFF4F3"),
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    MEDIUM_GREY,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    MEDIUM_GREY,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    return table


# ============================================================
# SECTION HEADER
# ============================================================

def section_header(
    title,
    styles=None,
):
    """
    Return a section heading.
    """

    if styles is None:
        styles = get_report_styles()

    return Paragraph(
        safe_text(title),
        styles["SectionTitle"],
    )


# ============================================================
# SIMPLE KEY VALUE TABLE
# ============================================================

def key_value_table(
    data,
    styles=None,
):
    """
    Create a two-column key/value table.

    data:
        {
            "Company": "TCS",
            "Year": "2025",
            "ROE": "21.4%"
        }
    """

    if styles is None:
        styles = get_report_styles()

    rows = []

    for key, value in data.items():

        rows.append(
            [
                Paragraph(
                    safe_text(key),
                    styles["TableCell"],
                ),
                Paragraph(
                    safe_text(value),
                    styles["TableCell"],
                ),
            ]
        )

    table = Table(
        rows,
        colWidths=[
            50 * mm,
            125 * mm,
        ],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    LIGHT_GREY,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    MEDIUM_GREY,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold",
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        )
    )

    return table


# ============================================================
# PAGE BREAK
# ============================================================

def new_page():
    """
    Return a ReportLab page break.
    """

    return PageBreak()


# ============================================================
# REPORT DATE
# ============================================================

def report_date():
    """
    Return current date as a readable string.
    """

    return datetime.now().strftime(
        "%d %B %Y"
    )


# ============================================================
# REPORT FOOTNOTE
# ============================================================

def methodology_note(
    text,
    styles=None,
):
    """
    Add a small methodology/disclaimer note.
    """

    if styles is None:
        styles = get_report_styles()

    return Table(
        [
            [
                Paragraph(
                    f"<b>Note:</b> {safe_text(text)}",
                    styles["Small"],
                )
            ]
        ],
        colWidths=[175 * mm],
        style=TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    LIGHT_GREY,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    MEDIUM_GREY,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        ),
    )


# ============================================================
# BUILD REPORT
# ============================================================

def build_report(
    filepath,
    story,
    title="Bluestock N100 Financial Analytics",
):
    """
    Build and save a complete PDF.
    """

    ensure_report_directories()

    doc = create_document(
        filepath=filepath,
        title=title,
    )

    doc.build(
        story,
        onFirstPage=lambda canvas, doc:
            draw_page_header_footer(
                canvas,
                doc,
                title,
            ),
        onLaterPages=lambda canvas, doc:
            draw_page_header_footer(
                canvas,
                doc,
                title,
            ),
    )

    return filepath


# ============================================================
# EXPORTS
# ============================================================

__all__ = [

    "MIDNIGHT_BLUE",
    "FUCHSIA_BLUE",
    "FLAMINGO",

    "WHITE",
    "BLACK",
    "LIGHT_GREY",
    "MEDIUM_GREY",
    "DARK_GREY",
    "GREEN",
    "RED",
    "YELLOW",

    "REPORTS_DIR",
    "TEARSHEETS_DIR",
    "SECTORS_DIR",

    "ensure_report_directories",

    "get_report_styles",

    "safe_text",
    "format_number",
    "format_percent",
    "format_ratio",
    "clean_filename",

    "draw_page_header_footer",

    "create_document",

    "title_block",

    "kpi_card",
    "kpi_row",

    "make_table",

    "pros_cons_table",

    "section_header",

    "key_value_table",

    "new_page",

    "report_date",

    "methodology_note",

    "build_report",
]