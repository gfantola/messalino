import unittest,json
from liturgical_b_lookup import INDEX,lookup_id,lookup_date

class IndexTests(unittest.TestCase):
    def test_integrity(self):
        data=json.loads(INDEX.read_text(encoding='utf-8'))
        entries=data['entries']
        self.assertEqual(len(entries),84)
        self.assertEqual(len({e['id'] for e in entries}),84)
        for e in entries:
            self.assertTrue(1<=e['lectionary_pdf_page']<=558)
            self.assertTrue(1<=e['missal_pdf_page']<=1278)
    def test_dates(self):
        for day,page in [('2026-11-29',13),('2026-12-25',57),('2027-03-28',215),('2027-05-16',283)]:
            self.assertEqual(lookup_date(day)['entry']['lectionary_pdf_page'],page)
        self.assertIsNone(lookup_date('2026-11-22'))
    def test_variants(self):
        self.assertEqual(lookup_id('christmas-night')['entry']['missal_pdf_page'],121)
        self.assertIsNone(lookup_id('missing'))
if __name__=='__main__':
    unittest.main()
