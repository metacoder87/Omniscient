import unittest
import os
import glob
import omniscient


class TestOmniscient(unittest.TestCase):

    def test_extract_text(self):
        pdf_path = '../../test_pdfs/test.pdf'
        text = omniscient.extract_text(pdf_path)
        self.assertIsInstance(text, str)

    def test_extract_images(self):
        pdf_path = '../test_pdfs/test.pdf'
        images = omniscient.extract_images(pdf_path)
        self.assertIsInstance(images, list)

    def test_extract_metadata(self):
        pdf_path = '../test_pdfs/test.pdf'
        metadata = omniscient.extract_metadata(pdf_path)
        self.assertIsInstance(metadata, dict)

    def test_folder_contents(self):
        pdf_folder = '../test_pdfs/'
        pdf_files = [os.path.basename(p) for p in glob.glob(
            os.path.join(pdf_folder, '*.pdf'))]
        self.assertGreater(len(pdf_files), 0)
        for pdf_file in pdf_files:
            self.assertTrue(os.path.exists(os.path.join(pdf_folder, pdf_file)))

    def test_extraction(self):
        pdf_folder = '../test_pdfs/'
        for pdf_path in glob.glob(os.path.join(pdf_folder, '*.pdf')):
            # Test text extraction
            text = omniscient.extract_text(pdf_path)
            self.assertIsInstance(text, str)

            # Test image extraction
            images = omniscient.extract_images(pdf_path)
            self.assertIsInstance(images, list)

            # Test metadata extraction
            metadata = omniscient.extract_metadata(pdf_path)
            self.assertIsInstance(metadata, dict)


if __name__ == '__main__':
    unittest.main()
