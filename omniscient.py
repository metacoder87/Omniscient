import os
import sys
import glob
import logging
import argparse
import xmltodict
import io
import json

from google.cloud import storage
from io import BytesIO
from pdfminer.high_level import extract_text, extract_pages
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBoxHorizontal, LTImage, LTTextLine
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfdevice import PDFDevice


# Set up argument parser
parser = argparse.ArgumentParser(
    description='Extract text, images, and metadata from PDFs using pdfMiner')
parser.add_argument('pdf_folder', type=str, help='Folder containing PDF files')
args = parser.parse_args()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Set up Google Cloud Storage client
storage_client = storage.Client()

pdf_folder = args.pdf_folder
for pdf_path in glob.glob(os.path.join(pdf_folder, '*.pdf')):
    logging.info(f'Processing {pdf_path}')
    try:
        # Set up PDF parser
        with open(pdf_path, 'rb') as f:
            parser = PDFParser(f)
            document = PDFDocument(parser)
            if not document.is_extractable:
                logging.warning(f'{pdf_path} is not extractable')
                continue
            rsrcmgr = PDFResourceManager()
            laparams = LAParams()

            # Extract text
            with io.StringIO() as output_string:
                try:
                    device = TextConverter(
                        rsrcmgr, output_string, laparams=laparams)
                    interpreter = PDFPageInterpreter(rsrcmgr, device)
                    for page in PDFPage.create_pages(document):
                        interpreter.process_page(page)
                    text = output_string.getvalue()
                    device.close()
                except PDFTextExtractionNotAllowed:
                    text = None
                    logging.warning(
                        f'{pdf_path} does not allow text extraction')

            # Extract images
            images = []
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            for page in PDFPage.create_pages(document):
                interpreter.process_page(page)
                layout = device.get_result()
                for obj in layout:
                    if isinstance(obj, LTImage):
                        try:
                            images.append(obj.stream.get_rawdata())
                        except Exception as e:
                            logging.warning(
                                f'{pdf_path}: Error extracting image: {e}')

            # Extract metadata
            metadata = {}
            catalog = document.catalog
            if 'Metadata' in catalog:
                stream = catalog['Metadata'].resolve().get_data()

                metadata.update(xmltodict.parse(stream))
            for info in document.info:
                if isinstance(info, dict) and 'XMP' in info:
                    try:
                        stream = info['XMP'].get_data()
                        metadata.update(xmltodict.parse(stream))
                    except Exception as e:
                        logging.warning(
                            f'{pdf_path}: Error extracting metadata: {e}')

            # Store parsed data on Google Cloud Storage
            bucket_name = 'my-bucket'
            storage_client = storage.Client()
            bucket = storage_client.bucket(bucket_name)

            # Create a new blob for the parsed data
            blob = bucket.blob(os.path.splitext(os.path.basename(pdf_path))[0] + '.txt')

            # Write the parsed data to the blob
            blob.upload_from_string(parsed_data)

            # Print the URL of the blob
            logging.info(f'Parsed data saved to {blob.public_url}')
    except Exception as e:
        logging.error(f'An error occurred while processing {pdf_path}: {e}')
