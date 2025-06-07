import fitz  # PyMuPDF
import re


class PDFExtractor:
    """PDFExtractor extracts text and hyperlinks from PDF and returns clean Markdown."""

    def __init__(self):
        self.path = ""
        self.text = ""

    def extract_text(self, path: str) -> str:
        """
        Extracts and returns the full Markdown text content from a PDF document.
        Args:
            path (str): The path to the PDF file to be processed.
        Returns:
            str: The concatenated Markdown from all pages of the PDF.
        """
        doc = fitz.open(path)
        markdown = []

        for page_number, page in enumerate(doc, start=1):
            text_spans = page.get_text("dict")["blocks"]
            link_areas = page.get_links()

            page_md = []
            for block in text_spans:
                if block["type"] != 0:
                    continue
                for line in block["lines"]:
                    line_text = ""
                    for span in line["spans"]:
                        span_text = self.clean_text(span["text"])
                        if not span_text:
                            continue

                        span_rect = fitz.Rect(span["bbox"])
                        linked = None

                        for link in link_areas:
                            if link.get("uri") and fitz.Rect(link["from"]).intersects(
                                span_rect
                            ):
                                linked = link["uri"]
                                break

                        if linked:
                            line_text += f"[{span_text}]({linked})"
                        else:
                            line_text += span_text
                    if line_text.strip():
                        page_md.append(line_text.strip())

            formatted = self.convert_text_to_markdown(page_md)
            markdown.append(formatted)

        combined_md = "\n\n---\n\n".join(markdown)
        return self.clean_markdown_links(combined_md)

    def convert_text_to_markdown(self, lines):
        md_lines = []
        for line in lines:
            if not line:
                continue
            if line.isupper() and len(line.split()) < 10:
                md_lines.append(f"### {line}")
            elif re.match(r"^[-•*]\s", line):
                md_lines.append(f"- {line[2:].strip()}")
            else:
                md_lines.append(line)
        return "\n".join(md_lines)

    def clean_text(self, text: str) -> str:
        """
        Keep only alphanumeric characters and basic punctuation: []\@.:/,+- and space.
        Removes all other characters including invisible symbols and weird artifacts.
        """
        allowed_chars = re.compile(r"[^a-zA-Z0-9\s\[\]\\@.:/,+\-•*‣▪●]")
        cleaned = allowed_chars.sub("", text)
        cleaned = re.sub(r"\s+", " ", cleaned)  # Normalize whitespace
        return cleaned.strip()

    def clean_markdown_links(self, text: str) -> str:
        """
        Removes duplicate markdown link artifacts like:
        [Text](url)[ |](url) -> [Text](url)
        """
        pattern = re.compile(r"(\[[^\]]+\]\(([^)]+)\))\[\s*\|\]\(\2\)")
        return pattern.sub(r"\1", text)
