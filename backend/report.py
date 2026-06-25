import base64
import io
from datetime import datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    HRFlowable,
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

C_BG        = colors.HexColor("#0f1117")
C_SURFACE   = colors.HexColor("#1a1d2e")
C_BORDER    = colors.HexColor("#2a2d3e")
C_RED       = colors.HexColor("#ff4444")
C_GREEN     = colors.HexColor("#44ff88")
C_ORANGE    = colors.HexColor("#ff9944")
C_TEXT      = colors.HexColor("#e0e0e0")
C_MUTED     = colors.HexColor("#888888")
C_WHITE     = colors.white

PAGE_W, PAGE_H = A4   # 595.27 x 841.89 pt

def _style(name, **kwargs) -> ParagraphStyle:
    base = getSampleStyleSheet()["Normal"]
    return ParagraphStyle(name, parent=base, **kwargs)


TITLE_STYLE   = _style("vv_title",   fontSize=28, textColor=C_WHITE,
                        alignment=TA_CENTER, fontName="Helvetica-Bold", leading=34)
SUB_STYLE     = _style("vv_sub",     fontSize=11, textColor=C_MUTED,
                        alignment=TA_CENTER, fontName="Helvetica", leading=14)
VERDICT_STYLE = _style("vv_verdict", fontSize=22, textColor=C_WHITE,
                        alignment=TA_CENTER, fontName="Helvetica-Bold", leading=28)
BODY_STYLE    = _style("vv_body",    fontSize=9,  textColor=C_TEXT,
                        fontName="Helvetica", leading=13)
BOLD_STYLE    = _style("vv_bold",    fontSize=9,  textColor=C_TEXT,
                        fontName="Helvetica-Bold", leading=13)
SMALL_STYLE   = _style("vv_small",   fontSize=7.5, textColor=C_MUTED,
                        fontName="Helvetica", leading=11)
HEAD2_STYLE   = _style("vv_h2",      fontSize=12, textColor=C_WHITE,
                        fontName="Helvetica-Bold", leading=16)
MONO_STYLE    = _style("vv_mono",    fontSize=8,  textColor=C_TEXT,
                        fontName="Courier", leading=11)


def _hr(color=C_BORDER, width=1):
    return HRFlowable(width="100%", thickness=width, color=color, spaceAfter=4, spaceBefore=4)


def _b64_to_image(b64_str: str, max_width: float, max_height: float) -> Image:
    data = base64.b64decode(b64_str)
    buf  = io.BytesIO(data)
    img  = Image(buf)
    ratio = min(max_width / img.imageWidth, max_height / img.imageHeight)
    img.drawWidth  = img.imageWidth  * ratio
    img.drawHeight = img.imageHeight * ratio
    return img


def _dark_background(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(C_BG)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    canvas.setFillColor(C_SURFACE)
    canvas.rect(0, PAGE_H - 28, PAGE_W, 28, fill=1, stroke=0)

    canvas.setFillColor(C_MUTED)
    canvas.setFont("Helvetica", 7)
    canvas.drawString(18, PAGE_H - 18, "VoiceVault  —  Deepfake Voice Detection Report")
    canvas.drawRightString(PAGE_W - 18, PAGE_H - 18,
                           f"Generated {datetime.now().strftime('%Y-%m-%d  %H:%M')}")

    canvas.setFillColor(C_MUTED)
    canvas.setFont("Helvetica", 7)
    canvas.drawCentredString(PAGE_W / 2, 14, f"Page {doc.page}")

    canvas.restoreState()


def _cover_page(result: dict, filename: str) -> list:
    verdict    = result["verdict"]          # "spoof" | "bonafide"
    confidence = result["confidence"]
    duration   = result["duration"]
    n_chunks   = result["num_chunks"]
    chunks     = result["chunks"]

    is_spoof      = verdict == "spoof"
    verdict_color = C_RED if is_spoof else C_GREEN
    verdict_label = "⚠  FAKE  (AI-Generated Voice)" if is_spoof else "✓  REAL  (Human Voice)"

    spoof_count    = sum(1 for c in chunks if c["label"] == "spoof")
    bonafide_count = n_chunks - spoof_count
    avg_conf       = sum(c["confidence"] for c in chunks) / max(n_chunks, 1)

    story = []
    story.append(Spacer(1, 1.5 * cm))

    story.append(Paragraph("🔒 VoiceVault", TITLE_STYLE))
    story.append(Paragraph("Real-Time Deepfake Voice Detection", SUB_STYLE))
    story.append(Spacer(1, 0.4 * cm))
    story.append(_hr(C_BORDER, 0.5))
    story.append(Spacer(1, 0.6 * cm))

    verdict_para_style = _style(
        "vv_verdict_col", fontSize=22, textColor=verdict_color,
        alignment=TA_CENTER, fontName="Helvetica-Bold", leading=28,
    )
    story.append(Paragraph(verdict_label, verdict_para_style))
    story.append(Spacer(1, 0.3 * cm))

    conf_pct = f"{confidence * 100:.1f}%"
    conf_style = _style("vv_conf", fontSize=14, textColor=verdict_color,
                        alignment=TA_CENTER, fontName="Helvetica", leading=18)
    story.append(Paragraph(f"Confidence: {conf_pct}", conf_style))
    story.append(Spacer(1, 0.8 * cm))
    story.append(_hr(verdict_color, 1.5))
    story.append(Spacer(1, 0.8 * cm))

    meta_data = [
        ["File", filename],
        ["Duration", f"{duration:.2f} s"],
        ["Chunks analysed", str(n_chunks)],
        ["Chunk length", "3.0 s"],
        ["Sample rate", "16,000 Hz"],
        ["Model", "RawNet2 (fine-tuned on ASVspoof 2019 LA)"],
        ["Analysis date", datetime.now().strftime("%d %B %Y, %H:%M")],
    ]
    meta_table = Table(
        [[Paragraph(k, BOLD_STYLE), Paragraph(v, BODY_STYLE)] for k, v in meta_data],
        colWidths=[5 * cm, 11 * cm],
    )
    meta_table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), C_SURFACE),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [C_SURFACE, C_BG]),
        ("TEXTCOLOR",   (0, 0), (-1, -1), C_TEXT),
        ("GRID",        (0, 0), (-1, -1), 0.4, C_BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",(0, 0), (-1, -1), 8),
        ("TOPPADDING",  (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0,0), (-1, -1), 5),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.8 * cm))


    story.append(Paragraph("Per-Chunk Analysis Summary", HEAD2_STYLE))
    story.append(Spacer(1, 0.3 * cm))

    header = ["Chunk", "Start", "End", "Verdict", "Spoof Prob", "Confidence"]
    rows   = [header]
    for c in chunks:
        v_label = "FAKE" if c["label"] == "spoof" else "REAL"
        rows.append([
            str(c["chunk_idx"] + 1),
            f"{c['start_time']:.1f}s",
            f"{c['end_time']:.1f}s",
            v_label,
            f"{c['spoof_prob'] * 100:.1f}%",
            f"{c['confidence'] * 100:.1f}%",
        ])

    col_widths = [2*cm, 2.5*cm, 2.5*cm, 3*cm, 3.5*cm, 3*cm]
    chunk_table = Table(
        [[Paragraph(str(cell), BOLD_STYLE if i == 0 else BODY_STYLE)
          for cell in row]
         for i, row in enumerate(rows)],
        colWidths=col_widths,
    )


    row_styles = [
        ("BACKGROUND",   (0, 0), (-1, 0),  C_BORDER),       # header row
        ("TEXTCOLOR",    (0, 0), (-1, 0),  C_WHITE),
        ("GRID",         (0, 0), (-1, -1), 0.4, C_BORDER),
        ("LEFTPADDING",  (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
    ]
    for i, c in enumerate(chunks, start=1):
        bg = colors.HexColor("#2a0a0a") if c["label"] == "spoof" else colors.HexColor("#0a1f0a")
        row_styles.append(("BACKGROUND", (0, i), (-1, i), bg))
        txt_col = C_RED if c["label"] == "spoof" else C_GREEN
        row_styles.append(("TEXTCOLOR", (3, i), (3, i), txt_col))

    chunk_table.setStyle(TableStyle(row_styles))
    story.append(chunk_table)
    story.append(Spacer(1, 0.6 * cm))


    stats_data = [[
        Paragraph(f"Fake chunks\n{spoof_count} / {n_chunks}", _style(
            "st1", fontSize=11, textColor=C_RED if spoof_count else C_MUTED,
            alignment=TA_CENTER, fontName="Helvetica-Bold", leading=15)),
        Paragraph(f"Real chunks\n{bonafide_count} / {n_chunks}", _style(
            "st2", fontSize=11, textColor=C_GREEN if bonafide_count else C_MUTED,
            alignment=TA_CENTER, fontName="Helvetica-Bold", leading=15)),
        Paragraph(f"Avg confidence\n{avg_conf * 100:.1f}%", _style(
            "st3", fontSize=11, textColor=C_ORANGE,
            alignment=TA_CENTER, fontName="Helvetica-Bold", leading=15)),
    ]]
    stats_table = Table(stats_data, colWidths=[PAGE_W / 3 - 30] * 3)
    stats_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), C_SURFACE),
        ("GRID",         (0, 0), (-1, -1), 0.4, C_BORDER),
        ("TOPPADDING",   (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
    ]))
    story.append(stats_table)
    story.append(PageBreak())
    return story


def _chunk_pages(chunks: list[dict]) -> list:
    story = []
    usable_w = PAGE_W - 3 * cm    # left+right margin
    usable_h = PAGE_H - 6 * cm    # top header + bottom page number

    for c in chunks:
        if not c.get("gradcam_image"):
            continue

        is_spoof  = c["label"] == "spoof"
        col       = C_RED if is_spoof else C_GREEN
        label_txt = "FAKE (AI-Generated)" if is_spoof else "REAL (Human Voice)"

        story.append(Spacer(1, 0.4 * cm))
        hdr_style = _style(
            f"ch_hdr_{c['chunk_idx']}", fontSize=13, textColor=col,
            fontName="Helvetica-Bold", leading=17, alignment=TA_LEFT,
        )
        story.append(Paragraph(
            f"Chunk {c['chunk_idx'] + 1}  —  {c['start_time']:.1f}s → {c['end_time']:.1f}s  "
            f"|  {label_txt}  ({c['confidence'] * 100:.1f}% confidence)",
            hdr_style,
        ))
        story.append(_hr(col, 0.8))
        story.append(Spacer(1, 0.3 * cm))

        img = _b64_to_image(c["gradcam_image"], usable_w, usable_h * 0.80)
        story.append(img)
        story.append(Spacer(1, 0.3 * cm))

        mini = [
            ["Spoof probability", f"{c['spoof_prob'] * 100:.2f}%"],
            ["Confidence",        f"{c['confidence'] * 100:.2f}%"],
            ["Verdict",           label_txt],
        ]
        mini_table = Table(
            [[Paragraph(k, BOLD_STYLE), Paragraph(v, BODY_STYLE)] for k, v in mini],
            colWidths=[5 * cm, 8 * cm],
        )
        mini_table.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, -1), C_SURFACE),
            ("GRID",         (0, 0), (-1, -1), 0.3, C_BORDER),
            ("LEFTPADDING",  (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING",   (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
            ("TEXTCOLOR",    (1, 2), (1, 2),  col),
        ]))
        story.append(mini_table)
        story.append(PageBreak())

    return story

def _methodology_page() -> list:
    story = []
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("How to Read This Report", HEAD2_STYLE))
    story.append(_hr(C_BORDER))
    story.append(Spacer(1, 0.4 * cm))

    sections = [
        ("What is Grad-CAM?",
         "Gradient-weighted Class Activation Mapping (Grad-CAM) is an explainability "
         "technique that highlights which regions of an input drove a neural network's "
         "decision. In VoiceVault, it is applied to the RawNet2 anti-spoofing model to "
         "show which frequency bands and time segments triggered the FAKE verdict."),

        ("How the heatmap works",
         "The spectrogram overlay uses a jet colourmap: blue regions have low activation "
         "(the model was not suspicious here), while red/yellow regions have high activation "
         "(these features strongly influenced the FAKE decision). The frequency saliency bar "
         "on the right shows the average activation at each mel-frequency band, revealing "
         "which parts of the spectrum are most suspicious."),

        ("What to look for in a FAKE voice",
         "AI vocoders typically produce three detectable artefacts: (1) Over-smoothing of "
         "the 4–8 kHz band — neural TTS systems prioritise speech intelligibility in lower "
         "bands and generate unnaturally uniform energy in the high-frequency range. "
         "(2) Periodic phase artefacts at frame boundaries (~every 10 ms), visible as "
         "vertical striping in the temporal saliency curve. "
         "(3) Unnaturally smooth formant transitions — human voices have micro-variations in "
         "pitch and energy that vocoders cannot replicate faithfully."),

        ("Model",
         "RawNet2 — a raw-waveform anti-spoofing model fine-tuned on the ASVspoof 2019 "
         "Logical Access (LA) dataset (~25,000 real and synthetic utterances). The model "
         "achieves AUC > 0.99 on the ASVspoof 2019 LA evaluation set. The dual Grad-CAM "
         "hooks target (a) the SincConv layer for frequency-band attribution and (b) the "
         "final residual block for temporal attribution."),

        ("Confidence score",
         "The per-chunk confidence is the softmax probability of the predicted class. "
         "The overall verdict confidence is a weighted average of spoof probabilities "
         "across all chunks. A threshold of 0.50 is used: above → FAKE, below → REAL."),

        ("Limitations",
         "This system is trained on ASVspoof 2019 data. Performance may vary on voices "
         "generated by models not represented in that dataset, heavily compressed audio "
         "(below 64 kbps), or audio shorter than 1 second. Cross-model generalisation "
         "testing (ElevenLabs, Murf, Resemble.ai) is ongoing."),
    ]

    for title, body in sections:
        story.append(Paragraph(title, BOLD_STYLE))
        story.append(Spacer(1, 0.15 * cm))
        story.append(Paragraph(body, BODY_STYLE))
        story.append(Spacer(1, 0.4 * cm))

    story.append(_hr(C_BORDER))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "VoiceVault  ·  2025–26",
        SMALL_STYLE,
    ))
    return story


def generate_pdf(result: dict, filename: str = "audio.wav") -> bytes:
    buf = io.BytesIO()

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.2 * cm,
        title="VoiceVault Analysis Report",
        author="VoiceVault",
    )

    story = []
    story += _cover_page(result, filename)
    story += _chunk_pages(result.get("chunks", []))
    story += _methodology_page()

    doc.build(story, onFirstPage=_dark_background, onLaterPages=_dark_background)
    buf.seek(0)
    return buf.read()