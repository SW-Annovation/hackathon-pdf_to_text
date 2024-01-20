import PyPDF2
import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance, ImageFilter
import io
import re

def extract_text_with_pypdf2(pdf_path): #pypdf2를 이용해 텍스트 추출
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def preprocess_image(image): #OCR 정확도를 올리기 위해 이미지 전처리과정, 정확도 향상이 미비한 것 같아서 제거해도 상관없을듯?
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    image = image.convert('L')
    image = image.point(lambda x: 0 if x < 128 else 255, '1')
    return image

def extract_text_with_ocr(pdf_path): #OCR(광학문자인식)로 텍스트 추출하기
    images = convert_from_path(pdf_path, dpi=300)
    text = ""
    for image in images:
        processed_image = preprocess_image(image)
        text += pytesseract.image_to_string(processed_image, lang='kor+eng', config='--psm 6')
    return text

def is_mostly_standard_characters(text, threshold=0.8): #threshold로 임계값 설정, 한글 영어 등이 80%이상이면 True
    standard_chars = re.findall(r"[가-힣a-zA-Z0-9\s!\"#$%&'()*+,-./:;<=>?@\[\\\]^_`{|}~]", text)
    return (len(standard_chars) / len(text)) >= threshold

def pdf_to_text(pdf_path): #pdf를 text로 변환
    extracted_text = extract_text_with_pypdf2(pdf_path)

    if not is_mostly_standard_characters(extracted_text):
        extracted_text = extract_text_with_ocr(pdf_path)
        extraction_method = "OCR"
    else:
        extraction_method = "PyPDF2"

    return extracted_text, extraction_method

# 사용 예시
pdf_path = 'paper.pdf'
extracted_text, method_used = pdf_to_text(pdf_path)
print(extracted_text)
print()
print(method_used)