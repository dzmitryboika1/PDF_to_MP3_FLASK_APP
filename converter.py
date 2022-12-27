import PyPDF2
from pathlib import Path
from gtts import gTTS
from googletrans import Translator


def define_language(text):
    """Defines language received text and return it"""
    translator = Translator()
    language = translator.detect(text).lang
    return language


def pdf_to_mp3(pdf_file_path, output_dir_path):
    """Extract text from pdf file and convert it to mp3 file. Return output audiofile path or None in case if passed
    incorrect file path or file is not pdf."""
    if Path(pdf_file_path).is_file() and Path(pdf_file_path).suffix == '.pdf':
        with open(pdf_file_path, 'rb') as pdf:
            reader = PyPDF2.PdfFileReader(pdf, strict=False)
            all_pages = [page.extract_text() for page in reader.pages]
        text_from_pdf = ''.join(all_pages).replace('\n', '')  # line breaks are deleted to sound without long pauses

        output_audio = gTTS(text=text_from_pdf, lang=define_language(text_from_pdf))
        mp3_file_name = f'{Path(pdf_file_path).stem}.mp3'
        output_audio.save(f'{output_dir_path}/{mp3_file_name}')

        return mp3_file_name
