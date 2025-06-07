import fitz  # PyMuPDF


class PDFExtractor:
    """PDFExtractor is a class that extracts text from PDF files."""

    def __init__(self):
        self.path = ""
        self.text = ""

    def extract_text(self, path: str) -> str:
        """
        Extracts and returns the full text content from a PDF document specified by self.path.
        Args:
            path (str): The path to the PDF file to be processed.
        Returns:
            str: The concatenated text from all pages of the PDF.
        """
        self.path = path
        doc = fitz.open(self.path)
        self.text = ""
        for page in doc:
            self.text += page.get_text()
        return self.text
