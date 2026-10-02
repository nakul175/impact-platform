"""Charts in frozen report packages (v0.27): deterministic bar charts of bound OFFICIAL results.

A report section may declare `charts`; each chart names bars by the section's own numeric binding
codes, so every bar is an OFFICIAL result revision of the locked snapshot that the package already
reconciles, and each bar may pin the approved target revision the snapshot locked for the same
indicator and period (official versus target). Nothing is recalculated: bar heights are proportions
of the stored decimal values, labels are the stored displayed values, a value that is not PRESENT
draws no bar (never a zero-height one) and a chart whose bound results differ in unit or display
places is refused at reconciliation.

The chart model is built once (`chart_models`) from the same immutable payloads the HTML, CSV, PDF,
XLSX and DOCX renderers share; `chart_svg` (HTML artifact) and `chart_drawing` (PDF, reportlab
graphics) draw it with integer-quantised geometry so two renders are byte-identical. XLSX and DOCX
carry the chart's data table and a note instead of a picture.
"""

from decimal import ROUND_HALF_UP, Decimal, localcontext
from html import escape

from .domain import DomainError, decimal_value, display

MAX_CHARTS_PER_SECTION = 10
MAX_BARS = 12
# Geometry of the SVG (CSS pixels) and of the PDF drawing (points): fixed, never data-dependent.
SVG = {"width": 640, "height": 320, "left": 56, "right": 16, "top": 40, "bottom": 64}
PDF = {"width": 460, "height": 230, "left": 44, "right": 12, "top": 30, "bottom": 46}
OFFICIAL_FILL = "#203c34"
TARGET_FILL = "#c9a227"
AXIS = "#586d62"
GRID = "#ccd6cf"
CHART_NOTE = (
    "Chart values are the bound official results of the locked snapshot exactly as the tables "
    "show them; the picture is drawn from the stored values and is never a source of numbers."
)


def _display(value, places):
    """A stored decimal shown once at the chart's display places; None when it cannot be shown."""
    if value is None:
        return None
    try:
        return display(decimal_value(value), places)
    except DomainError:
        return None


def chart_models(section, values, targets=None):
    """The charts of one report section as the renderers draw them. `values` maps
    (section_code, binding_code) to the bound OFFICIAL result payload; `targets` maps a pinned
    target revision to its payload. Unknown references raise KeyError: reconciliation refused them
    before a package could be frozen, so a model with one is a defect, never a rendering."""
    targets = targets or {}
    charts = []
    for chart in section.get("charts") or []:
        bars, unit, places = [], None, None
        for series in chart["series"]:
            result = values[(section["section_code"], series["binding_code"])]
            unit = result.get("unit") if unit is None else unit
            places = result.get("display_decimals", 2) if places is None else places
            present = result.get("value_state") == "PRESENT" and result.get("value") is not None
            target = targets[series["target_revision"]] if series.get("target_revision") else None
            target_present = bool(
                target and target.get("value_state") == "PRESENT" and target.get("value") is not None
            )
            bars.append(
                {
                    "binding_code": series["binding_code"],
                    "label": series.get("label") or series["binding_code"],
                    "value": result.get("value") if present else None,
                    "displayed_value": str(result.get("displayed_value", "—")),
                    "value_state": result.get("value_state"),
                    "target_revision": series.get("target_revision"),
                    "target_value": target.get("value") if target_present else None,
                    "target_displayed_value": _display(target.get("value"), places)
                    if target_present
                    else None,
                }
            )
        charts.append(
            {
                "chart_code": chart["chart_code"],
                "title": chart["title"],
                "unit": unit or "",
                "display_decimals": places if places is not None else 2,
                "with_targets": any(bar["target_revision"] for bar in bars),
                "bars": bars,
            }
        )
    return charts


def chart_rows(chart):
    """The chart's data table: label, official value, unit, target (or blank), value state."""
    rows = []
    for bar in chart["bars"]:
        rows.append(
            [
                bar["label"],
                bar["displayed_value"],
                chart["unit"],
                bar["target_displayed_value"] or "",
                bar["value_state"] or "",
            ]
        )
    return rows


def chart_description(chart):
    parts = []
    for bar in chart["bars"]:
        text = bar["label"] + ": " + bar["displayed_value"] + (" " + chart["unit"] if chart["unit"] else "")
        if bar["target_revision"]:
            text += "; target " + (bar["target_displayed_value"] or "not set")
        parts.append(text)
    return (
        "Official values" + (" and targets" if chart["with_targets"] else "") + ". " + "; ".join(parts) + "."
    )


def _layout(chart, box):
    """Pixel geometry of every bar from the stored decimals, quantised to whole units so the output
    never depends on floating-point formatting. Returns (axis_y, bars) where each bar is a list of
    (x, y, width, height, fill, value_text, label) rectangles for official and target values."""
    numbers = []
    for bar in chart["bars"]:
        for key in ["value", "target_value"]:
            if bar[key] is not None:
                numbers.append(decimal_value(bar[key]))
    low = min([Decimal(0), *numbers])
    high = max([Decimal(0), *numbers])
    if high == low:
        high = low + 1
    plot_left = box["left"]
    plot_right = box["width"] - box["right"]
    plot_top = box["top"]
    plot_bottom = box["height"] - box["bottom"]
    plot_width = plot_right - plot_left
    plot_height = plot_bottom - plot_top
    groups = max(len(chart["bars"]), 1)
    lanes = 2 if chart["with_targets"] else 1
    with localcontext() as context:
        context.prec = 60

        def y_of(value):
            raw = Decimal(plot_top) + (high - value) / (high - low) * Decimal(plot_height)
            return int(raw.quantize(Decimal("1"), rounding=ROUND_HALF_UP))

        axis_y = y_of(Decimal(0))
        slot = Decimal(plot_width) / Decimal(groups)
        bar_width = int(
            (slot * Decimal("0.7") / Decimal(lanes)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        )
        bar_width = max(bar_width, 2)
        rects = []
        for index, bar in enumerate(chart["bars"]):
            group_left = int(
                (Decimal(plot_left) + slot * Decimal(index) + slot * Decimal("0.15")).quantize(
                    Decimal("1"), rounding=ROUND_HALF_UP
                )
            )
            centre = int(
                (Decimal(plot_left) + slot * (Decimal(index) + Decimal("0.5"))).quantize(Decimal("1"))
            )
            series = [("value", "displayed_value", OFFICIAL_FILL, "Official")]
            if chart["with_targets"]:
                series.append(("target_value", "target_displayed_value", TARGET_FILL, "Target"))
            drawn = []
            for lane, (value_key, text_key, fill, kind) in enumerate(series):
                x = group_left + lane * bar_width
                if bar[value_key] is None:
                    drawn.append({"x": x, "y": None, "w": bar_width, "h": 0, "fill": fill, "kind": kind})
                    continue
                value = decimal_value(bar[value_key])
                top = y_of(value)
                height = abs(axis_y - top)
                drawn.append(
                    {
                        "x": x,
                        "y": min(top, axis_y),
                        "w": bar_width,
                        "h": height,
                        "fill": fill,
                        "kind": kind,
                        "text": bar[text_key],
                        "negative": value < 0,
                    }
                )
            rects.append(
                {"label": bar["label"], "centre": centre, "series": drawn, "state": bar["value_state"]}
            )
    return axis_y, plot_left, plot_right, plot_top, plot_bottom, rects


def chart_svg(chart):
    """An inline SVG figure (`role="img"` with title and description) of one chart."""
    box = SVG
    axis_y, plot_left, plot_right, plot_top, plot_bottom, groups = _layout(chart, box)
    code = escape(chart["chart_code"])
    out = [
        '<svg class="report-chart" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" '
        'height="%d" role="img" aria-labelledby="chart-%s-title chart-%s-desc">'
        % (box["width"], box["height"], box["width"], box["height"], code, code),
        '<title id="chart-%s-title">%s</title>' % (code, escape(chart["title"])),
        '<desc id="chart-%s-desc">%s</desc>' % (code, escape(chart_description(chart))),
        '<text x="%d" y="22" font-size="16" font-weight="700" fill="%s">%s</text>'
        % (plot_left, OFFICIAL_FILL, escape(chart["title"])),
        '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1"/>'
        % (plot_left, axis_y, plot_right, axis_y, AXIS),
        '<text x="%d" y="%d" font-size="11" fill="%s" text-anchor="end">0</text>'
        % (plot_left - 6, axis_y + 4, AXIS),
    ]
    if chart["unit"]:
        out.append(
            '<text x="%d" y="%d" font-size="11" fill="%s">%s</text>'
            % (plot_left, plot_top - 8, AXIS, escape(chart["unit"]))
        )
    for group in groups:
        for rect in group["series"]:
            if rect["y"] is None:
                out.append(
                    '<text x="%d" y="%d" font-size="11" fill="%s" text-anchor="middle">%s</text>'
                    % (
                        rect["x"] + rect["w"] // 2,
                        axis_y - 6,
                        AXIS,
                        escape("—" if rect["kind"] == "Target" else (group["state"] or "—")),
                    )
                )
                continue
            out.append(
                '<rect x="%d" y="%d" width="%d" height="%d" fill="%s"><title>%s %s</title></rect>'
                % (
                    rect["x"],
                    rect["y"],
                    rect["w"],
                    rect["h"],
                    rect["fill"],
                    rect["kind"],
                    escape(rect["text"]),
                )
            )
            label_y = rect["y"] + rect["h"] + 14 if rect.get("negative") else rect["y"] - 6
            out.append(
                '<text x="%d" y="%d" font-size="11" fill="%s" text-anchor="middle">%s</text>'
                % (rect["x"] + rect["w"] // 2, label_y, OFFICIAL_FILL, escape(rect["text"]))
            )
        out.append(
            '<text x="%d" y="%d" font-size="12" fill="%s" text-anchor="middle">%s</text>'
            % (group["centre"], plot_bottom + 20, OFFICIAL_FILL, escape(group["label"]))
        )
    legend_y = box["height"] - 14
    out.append(
        '<rect x="%d" y="%d" width="12" height="12" fill="%s"/><text x="%d" y="%d" font-size="11" fill="%s">Official</text>'
        % (plot_left, legend_y - 10, OFFICIAL_FILL, plot_left + 16, legend_y, AXIS)
    )
    if chart["with_targets"]:
        out.append(
            '<rect x="%d" y="%d" width="12" height="12" fill="%s"/><text x="%d" y="%d" font-size="11" fill="%s">Target</text>'
            % (plot_left + 90, legend_y - 10, TARGET_FILL, plot_left + 106, legend_y, AXIS)
        )
    out.append("</svg>")
    return "".join(out)


def chart_drawing(chart):
    """The same chart as a reportlab vector drawing (points), for the PDF artifact."""
    from reportlab.graphics.shapes import Drawing, Line, Rect, String
    from reportlab.lib import colors

    box = PDF
    axis_y, plot_left, plot_right, plot_top, plot_bottom, groups = _layout(chart, box)
    height = box["height"]

    def flip(y):  # reportlab's origin is bottom-left
        return height - y

    drawing = Drawing(box["width"], height)
    drawing.add(
        String(
            plot_left,
            flip(13),
            chart["title"],
            fontName="Helvetica-Bold",
            fontSize=11,
            fillColor=colors.HexColor(OFFICIAL_FILL),
        )
    )
    if chart["unit"]:
        drawing.add(
            String(
                plot_left,
                flip(plot_top - 6),
                chart["unit"],
                fontName="Helvetica",
                fontSize=8,
                fillColor=colors.HexColor(AXIS),
            )
        )
    drawing.add(
        Line(
            plot_left,
            flip(axis_y),
            plot_right,
            flip(axis_y),
            strokeColor=colors.HexColor(AXIS),
            strokeWidth=0.75,
        )
    )
    drawing.add(
        String(
            plot_left - 5,
            flip(axis_y + 3),
            "0",
            fontName="Helvetica",
            fontSize=8,
            textAnchor="end",
            fillColor=colors.HexColor(AXIS),
        )
    )
    for group in groups:
        for rect in group["series"]:
            middle = rect["x"] + rect["w"] / 2
            if rect["y"] is None:
                text = "—" if rect["kind"] == "Target" else (group["state"] or "—")
                drawing.add(
                    String(
                        middle,
                        flip(axis_y - 5),
                        text,
                        fontName="Helvetica",
                        fontSize=8,
                        textAnchor="middle",
                        fillColor=colors.HexColor(AXIS),
                    )
                )
                continue
            drawing.add(
                Rect(
                    rect["x"],
                    flip(rect["y"] + rect["h"]),
                    rect["w"],
                    rect["h"],
                    fillColor=colors.HexColor(rect["fill"]),
                    strokeColor=None,
                )
            )
            label_y = rect["y"] + rect["h"] + 10 if rect.get("negative") else rect["y"] - 4
            drawing.add(
                String(
                    middle,
                    flip(label_y),
                    rect["text"],
                    fontName="Helvetica",
                    fontSize=8,
                    textAnchor="middle",
                    fillColor=colors.HexColor(OFFICIAL_FILL),
                )
            )
        drawing.add(
            String(
                group["centre"],
                flip(plot_bottom + 14),
                group["label"],
                fontName="Helvetica",
                fontSize=9,
                textAnchor="middle",
                fillColor=colors.HexColor(OFFICIAL_FILL),
            )
        )
    legend_y = height - 10
    drawing.add(
        Rect(plot_left, flip(legend_y + 8), 9, 9, fillColor=colors.HexColor(OFFICIAL_FILL), strokeColor=None)
    )
    drawing.add(
        String(
            plot_left + 12,
            flip(legend_y + 7),
            "Official",
            fontName="Helvetica",
            fontSize=8,
            fillColor=colors.HexColor(AXIS),
        )
    )
    if chart["with_targets"]:
        drawing.add(
            Rect(
                plot_left + 60,
                flip(legend_y + 8),
                9,
                9,
                fillColor=colors.HexColor(TARGET_FILL),
                strokeColor=None,
            )
        )
        drawing.add(
            String(
                plot_left + 72,
                flip(legend_y + 7),
                "Target",
                fontName="Helvetica",
                fontSize=8,
                fillColor=colors.HexColor(AXIS),
            )
        )
    return drawing
