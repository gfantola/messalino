import unittest
from datetime import date
from liturgical_calendar import calendar_day,easter,advent

class CalendarTests(unittest.TestCase):
    def test_easter(self):
        for y,m,d in [(2026,4,5),(2027,3,28),(2028,4,16)]:
            self.assertEqual(easter(y),date(y,m,d))
    def test_advent(self):
        self.assertEqual(advent(2026),date(2026,11,29))
        self.assertEqual(calendar_day('2026-11-27')['sunday_cycle'],'A')
        self.assertEqual(calendar_day('2026-11-29')['sunday_cycle'],'B')
        self.assertEqual(calendar_day('2026-11-29')['week'],1)
    def test_ordinary(self):
        self.assertEqual(calendar_day('2026-11-27')['week'],34)
        self.assertEqual(calendar_day('2026-11-22')['title'],'Cristo Re dell’Universo')
    def test_movable(self):
        for day,title in [('2027-02-10','Mercoledì delle Ceneri'),('2027-03-28','Pasqua di Risurrezione'),('2027-05-09','Ascensione del Signore'),('2027-05-16','Pentecoste')]:
            self.assertEqual(calendar_day(day)['title'],title)
    def test_scope(self):
        self.assertFalse(calendar_day('2026-12-08')['complete'])

if __name__=='__main__':
    unittest.main()
