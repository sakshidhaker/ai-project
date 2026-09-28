"""
STUDENT CODE MAP
============================================================
FILE: backend/pdf_generator.py

PURPOSE:
    Convert validated AI-generated text into a readable PDF.

CONNECTION:
    backend/api/document_api.py
        -> create_pdf()
        -> ReportLab
        -> generated/<filename>.pdf
        -> backend/api/downloads_api.py
        -> browser

IMPORTANT:
    Qwen may return normal text plus fenced code blocks:

        ```python
        def find_largest(numbers):
            # Python comment
            if not numbers:
                return None
        ```

    Normal text can be formatted as headings/bullets. Code must be handled
    separately so Python indentation and '#' comments are preserved.

EDIT HERE:
    Change the styles or page margins when teaching PDF formatting.

BE CAREFUL:
    Never strip a line while it is inside a code block. Python indentation
    is part of the language.
============================================================
"""

# escape() protects normal text before it is used by ReportLab Paragraph.
from html import escape

# Path builds the final output path safely.
from pathlib import Path

# ReportLab supplies the page, text styles, and flowable classes.
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

# Paragraph is for normal text. Preformatted is for code because it preserves
# spaces and line breaks instead of normalizing whitespace like Paragraph does.
from reportlab.platypus import Paragraph, Preformatted, SimpleDocTemplate, Spacer
from reportlab.lib.units import inch

# The project stores generated files in one configured directory.
from backend.config import GENERATED_DIR


def _build_story(text):
    """
    PURPOSE:
        Convert generated AI text into ReportLab flowables.

    CONNECTION:
        create_pdf() calls this before ReportLab builds the PDF.

    FLOW:
        AI text
            -> detect ``` code fence
            -> normal text -> Paragraph
            -> code       -> Preformatted
            -> final story

    IMPORTANT:
        Markdown headings are recognized only OUTSIDE code blocks.
        A Python '# comment' therefore stays a Python comment.
    """
    styles = getSampleStyleSheet()

    # Courier is monospaced so code indentation is easy to understand.
    code_style = ParagraphStyle(
        "StudentCode",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=8.5,
        leading=10.5,
        leftIndent=0,
        rightIndent=0,
        spaceBefore=5,
        spaceAfter=8,
    )

    story = []
    code_lines = []
    in_code = False

    # splitlines() removes only line endings. Leading code spaces remain.
    for raw_line in str(text).splitlines():
        # Remove only a Windows carriage return. Do not remove indentation.
        line = raw_line.rstrip("\r")

        # Check fences BEFORE checking headings. This prevents ```python from
        # becoming a document title when it is the first line.
        if line.strip().startswith("```"):
            if in_code:
                if code_lines:
                    story.append(
                        Preformatted(
                            "\n".join(code_lines),
                            code_style,
                            dedent=0,
                        )
                    )
                    code_lines = []

                story.append(Spacer(1, 0.08 * inch))
                in_code = False
            else:
                # ``` and ```python are control markers and are not printed.
                in_code = True

            continue

        if in_code:
            # CRITICAL: keep the line exactly as generated apart from \r.
            # Python's indentation must survive the PDF conversion.
            code_lines.append(line)
            continue

        # Empty normal-text lines provide visual separation.
        if not line.strip():
            story.append(Spacer(1, 0.10 * inch))
            continue

        # Only normal text is stripped and escaped.
        clean = escape(line.strip())

        # Interpret Markdown-like headings only outside code.
        if line.startswith("### "):
            story.append(Paragraph(clean[4:], styles["Heading3"]))
        elif line.startswith("## "):
            story.append(Paragraph(clean[3:], styles["Heading2"]))
        elif line.startswith("# "):
            story.append(Paragraph(clean[2:], styles["Title"]))
        elif line.startswith(("- ", "* ")):
            story.append(Paragraph("• " + clean[2:], styles["BodyText"]))
        else:
            story.append(Paragraph(clean, styles["BodyText"]))

        story.append(Spacer(1, 0.06 * inch))

    # If the model forgot the closing fence, the remaining content is still
    # treated as code instead of being accidentally formatted as headings.
    if code_lines:
        story.append(
            Preformatted(
                "\n".join(code_lines),
                code_style,
                dedent=0,
            )
        )

    return story


def create_pdf(text, filename):
    """
    PURPOSE:
        Create a PDF from validated AI output.

    CONNECTION:
        backend/api/document_api.py calls this after validator.py passes.

    INPUT:
        text     - generated document text from Qwen.
        filename - unique name selected by document_api.py.

    RETURNS:
        Path to the generated PDF.

    EDIT HERE:
        Change page size, margins, or styles when teaching PDF generation.
    """
    # Make sure the output directory exists.
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)

    path = Path(GENERATED_DIR) / filename

    # Parse the AI output into normal-text and code flowables.
    story = _build_story(text)

    # SimpleDocTemplate handles pagination and writes the PDF structure.
    document = SimpleDocTemplate(
        str(path),
        pagesize=LETTER,
        leftMargin=0.65 * inch,
        rightMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title="AI Creator Engine",
        author="AI Creator Engine",
    )

    # Build the final PDF.
    document.build(story)
    return path
