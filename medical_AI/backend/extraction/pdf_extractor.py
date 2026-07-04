# import fitz

# def extract_text_from_pdf(pdf_path):
#     doc = fitz.open(pdf_path)

#     for i, page in enumerate(doc):
#         # Extract text
#         text = page.get_text()
#         # Count images
#         images = page.get_images(full=True)
#         print("Images on page:", len(images))

#     doc.close()

import io

import cv2
import fitz
import numpy as np
import pdfplumber
from paddleocr import PaddleOCR
from PIL import Image

import os

os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"] = "0"

class PDFExtractor:

    def __init__(self):
        self.ocr = None

    ####################################################
    # LOAD OCR MODEL (ONLY ONCE)
    ####################################################
    def get_ocr(self):

        if self.ocr is None:

            print("=" * 80)
            print("Loading PaddleOCR...")
            print("=" * 80)

            self.ocr = PaddleOCR(
                lang="en",
                # use_gpu=False,          # Disable GPU/CUDA if not explicitly available
                enable_mkldnn=False,     # Bypasses the PIR executor conversion bug
                cpu_threads=4,          # Distribute matrix operations to 4 CPU threads
                use_angle_cls=False,    # Disable image alignment checks (saves massive time)
                ocr_version="PP-OCRv4"  # Force standard lightweight OCR engine instead of structural layout parsing
            )

        return self.ocr

    ####################################################
    # METHOD 1 : PyMuPDF
    ####################################################
    def extract_pymupdf(self, pdf_path):

        text = ""

        try:

            doc = fitz.open(pdf_path)

            for page in doc:
                text += page.get_text("text")

            doc.close()

        except Exception as e:

            print("PyMuPDF Error:", e)

        return text.strip()

    ####################################################
    # METHOD 2 : pdfplumber
    ####################################################
    def extract_pdfplumber(self, pdf_path):

        text = ""

        try:

            with pdfplumber.open(pdf_path) as pdf:

                for page in pdf.pages:

                    page_text = page.extract_text()

                    if page_text:
                        text += page_text + "\n"

        except Exception as e:

            print("pdfplumber Error:", e)

        return text.strip()

    ####################################################
    # IMAGE PREPROCESSING
    ####################################################
    def preprocess_image(self, img):

        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        # Remove noise
        gray = cv2.GaussianBlur(gray, (3, 3), 0)

        # Adaptive threshold
        gray = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            11
        )

        # Sharpen image
        kernel = np.array([
            [-1, -1, -1],
            [-1, 9, -1],
            [-1, -1, -1]
        ])

        gray = cv2.filter2D(gray, -1, kernel)

        return gray

    ####################################################
    # METHOD 3 : OCR
    ####################################################
    # def extract_ocr(self, pdf_path):

    #     text = ""

    #     ocr = self.get_ocr()

    #     try:

    #         doc = fitz.open(pdf_path)

    #         for page_number, page in enumerate(doc):

    #             print(f"OCR Processing Page {page_number + 1}")

    #             pix = page.get_pixmap(
    #                 dpi=300,
    #                 alpha=False
    #             )

    #             img = Image.open(
    #                 io.BytesIO(
    #                     pix.tobytes("png")
    #                 )
    #             )

    #             img = np.array(img)

    #             gray = self.preprocess_image(img)

    #             # PaddleOCR 3.x
    #             results = ocr.predict(gray)
    #             # print("=" * 80)
    #             # print(type(results))
    #             # print(results)
    #             # print("=" * 80)

    #             # return ""
    #             for res in results:

    #                 # Uncomment for debugging if needed
    #                 # res.print()

    #                 try:
    #                     data = res.json["res"]

    #                     texts = data.get("rec_texts", [])
    #                     scores = data.get("rec_scores", [])

    #                     for txt, score in zip(texts, scores):

    #                         if score >= 0.60:
    #                             text += txt + "\n"

    #                 except Exception as e:

    #                     print("OCR Result Parsing Error:", e)

    #             text += "\n"

    #         doc.close()

    #     except Exception as e:

    #         print("OCR Error:", e)

    #     return text.strip()
    ####################################################
    # METHOD 3 : OCR
    ####################################################
    def extract_ocr(self, pdf_path):
        text = ""
        ocr = self.get_ocr()

        try:
            doc = fitz.open(pdf_path)

            for page_number, page in enumerate(doc):
                print("Please Wait while we fetch your reports...")
                print(f"OCR Processing Page {page_number + 1}")

                pix = page.get_pixmap(dpi=300, alpha=False)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                img = np.array(img)

                # PaddleOCR 3.x returns a list containing structure predictions
                results = ocr.predict(img)
                
                if not results:
                    continue

                # PaddleOCR 3.x structure pipeline parses components safely:
                for res in results:
                    # Check if 'res' contains a valid layout dictionary
                    if hasattr(res, 'json') and "res" in res.json:
                        data = res.json["res"]
                        
                        # Handle standard region layout structures
                        if "layout" in data:
                            for element in data["layout"]:
                                if "rec_texts" in element:
                                    # Safe extraction matching text line to score threshold
                                    texts = element.get("rec_texts", [])
                                    scores = element.get("rec_scores", [])
                                    for txt, score in zip(texts, scores):
                                        if score >= 0.60:
                                            text += txt + " "
                                text += "\n"
                        
                        # Fallback: Check root-level text lines if layout isn't structured
                        elif "rec_texts" in data:
                            texts = data.get("rec_texts", [])
                            scores = data.get("rec_scores", [])
                            for txt, score in zip(texts, scores):
                                if score >= 0.60:
                                    text += txt + "\n"
                    
                    # Alternative fallback for standard basic paddleocr layouts
                    elif isinstance(res, list):
                        for line in res:
                            if isinstance(line, list) and len(line) > 1:
                                txt, score = line[1][0], line[1][1]
                                if score >= 0.60:
                                    text += txt + "\n"

                text += "\n"

            doc.close()

        except Exception as e:
            print("OCR Error:", e)

        return text.strip() 
    ####################################################
    # CLEAN TEXT
    ####################################################
    def clean_text(self, text):

        text = text.replace("\x00", " ")
        text = text.replace("\t", " ")

        while "  " in text:
            text = text.replace("  ", " ")

        return text.strip()

    ####################################################
    # MAIN METHOD
    ####################################################
    def extract(self, pdf_path):

        # print("=" * 80)
        # print("Trying PyMuPDF...")
        # print("=" * 80)

        text = self.extract_pymupdf(pdf_path)

        print("Characters:", len(text))

        if len(text) > 100:

            # print("Using PyMuPDF")

            return self.clean_text(text)

        # print("=" * 80)
        # print("Trying pdfplumber...")
        # print("=" * 80)

        text = self.extract_pdfplumber(pdf_path)

        print("Characters:", len(text))

        if len(text) > 100:

            # print("Using pdfplumber")

            return self.clean_text(text)

        # print("=" * 80)
        # print("Running OCR...")
        # print("=" * 80)

        text = self.extract_ocr(pdf_path)

        print("Characters:", len(text))

        return self.clean_text(text)