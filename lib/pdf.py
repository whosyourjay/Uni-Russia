"""Text extraction shared by the PDF parsers."""

import subprocess


def pdf_text(filename):
    """Extract searchable text from an official PDF with Poppler."""
    return subprocess.run(["pdftotext", "-layout", filename, "-"], check=True,
                          capture_output=True, text=True).stdout
