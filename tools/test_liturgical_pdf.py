import tempfile
import unittest
from pathlib import Path
from index_liturgical_pdf import matches_heading,inspect_pdf

class PdfIndexTests(unittest.TestCase):
    def test_normalization(self):
        self.assertTrue(matches_heading('I DOMENICA\nDI AVVENTO','I domenica di Avvento'))
        self.assertFalse(matches_heading('II DOMENICA DI AVVENTO','I domenica di Avvento'))
    def test_synthetic_pdf(self):
        import pymupdf
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'sample.pdf'
            with pymupdf.open() as doc:
                doc.new_page().insert_text((72,72),'I DOMENICA DI AVVENTO')
                doc.new_page().insert_text((72,72),'II DOMENICA DI AVVENTO')
                doc.set_toc([[1,'I DOMENICA DI AVVENTO',1]])
                doc.save(path)
            result=inspect_pdf(path,['I DOMENICA DI AVVENTO'])
            item=result['results']['I DOMENICA DI AVVENTO']
            self.assertEqual(item['candidates'],[1])
            self.assertFalse(item['verified'])
            self.assertEqual(result['pages_with_text'],2)

if __name__=='__main__':
    unittest.main()
