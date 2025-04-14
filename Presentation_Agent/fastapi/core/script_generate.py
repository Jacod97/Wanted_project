import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import preprocess_text, convert_image_to_base64, extract_image_bytes, extract_page_bytes, calculate_image_ratio, preprocess_script
from fastapi import UploadFile
from models import VISION_LLM, PAGE_SCRIPT_LLM
import fitz
from pathlib import Path
import io

PDF_DIR = Path("../data/pdf_temp")
TEXT_DIR = Path("../data/text_temp")

class ScriptGenerator:
    def __init__(self, pdf_file: UploadFile, full_document: str):
        self.pdf_file = pdf_file
        self.full_document = full_document
        self.pdf_data = []
        self.vision_llm = VISION_LLM
        self.page_script_llm = PAGE_SCRIPT_LLM
        self.pdf_bytes = pdf_file.file.read()
        self.docs = fitz.open(stream=self.pdf_bytes, filetype="pdf")
        print(f"[INIT] PDF 로드 완료 ({len(self.docs)} 페이지)")

    def process(self):
        print("[PROCESS] 전체 PDF 처리 시작")
        self._save_data()
        total_pages = len(self.docs)

        for page_idx, page in enumerate(self.docs):
            text = preprocess_text(page.get_text())
            print(f"[TEXT] {text}")
            image_description = self._image_process(page, text)
            script = self.generate_script(page_idx, text, image_description, total_pages)
            script = script.replace("**", "")
            print(f"[{page_idx + 1} PAGE 원본 대본] {script}")

            self.pdf_data.append({
                "page": page_idx + 1,
                "text": text,
                "image_description": image_description,
                "script": script
            })


        print("[PROCESS] 전체 완료")
        return self.pdf_data

    def _save_data(self):
        PDF_DIR.mkdir(parents=True, exist_ok=True)
        TEXT_DIR.mkdir(parents=True, exist_ok=True)

        pdf_bytes = self.pdf_bytes
        pdf_path = PDF_DIR / self.pdf_file.filename
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)

        save_name = Path(self.pdf_file.filename).stem
        text_path = TEXT_DIR / f"{save_name}.txt"
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(self.full_document)

        print("[SAVE] 파일 저장 완료")

    def _image_process(self, page, text):
        images = page.get_images(full=True)
        page_bytes, page_size = extract_page_bytes(page)

        image_description = []

        for img in images:
            xref = img[0]
            img_bytes, img_size = extract_image_bytes(self.docs, xref)
            image_ratio = calculate_image_ratio(img_size, page_size)

            response = self.vision_llm.invoke({
                "text": text,
                "image_base64": convert_image_to_base64(img_bytes),
            })

            if response.is_chart or image_ratio > 0.5:
                image_description.append(response.description)

        print(f"[IMAGE] {len(image_description)}개 중요한 이미지 감지됨")
        return ", ".join(image_description) if image_description else ""

    def generate_script(self, page_idx, text, image_description, total_pages):
        memory_variables = self.page_script_llm.memory.load_memory_variables(inputs={})
        previous_summary = memory_variables.get("history", "")

        inputs = {
            "page": page_idx + 1,
            "total_pages": total_pages,
            "text": text,
            "image_description": image_description,
            "full_doc": self.full_document,
            "previous_summary": previous_summary
        }

        # print(f"[SCRIPT] 페이지 {page_idx + 1} 대본 생성")
        return self.page_script_llm.invoke(inputs)
    

# if __name__ == "__main__":
#     from fastapi import UploadFile

#     pdf_path = Path(r"C:/wanted/Portfolio/LLM/O3.pdf")
#     with open(pdf_path, "rb") as f:
#         file_content = f.read()

#     upload_file = UploadFile(filename="O3.pdf", file=io.BytesIO(file_content))

#     full_document = """
#     이 발표는 AI 발표 자동화 시스템에 대한 소개입니다.
#     각 슬라이드는 기능, 구조, 기술 스택 등을 설명합니다.
#     """

#     generator = ScriptGenerator(pdf_file=upload_file, full_document=full_document)
#     result = generator.process()

#     for page in result:
#         print(f"\n📄 Page {page['page']}")
#         print(f"텍스트: {page['text']}")
#         print(f"이미지 설명: {page['image_description']}")
#         print(f"🗣️ 대본:\n{page['script']}")
#         print("=" * 80)