import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import rawsnes_obs as m


class Snestests(unittest.TestCase):
    def test_snes_names(self):
        for name in ('Super Nintendo Entertainment System', 'Super Nintendo',
                     'SNES', 'Super Famicom', 'SNES / SFC'):
            with self.subTest(name=name):
                self.assertTrue(m.is_snes({'ConsoleName': name}))
        for name in ('Mega Drive', 'Genesis', 'Nintendo Entertainment System',
                     'Game Boy Advance', 'Nintendo DS', 'Saturn'):
            with self.subTest(name=name):
                self.assertFalse(m.is_snes({'ConsoleName': name}))

    def test_case_variants(self):
        self.assertTrue(m.is_snes({'consoleName': 'super nintendo'}))
        self.assertEqual(m.identity({'AchievementID': 9, 'Date': 'now', 'HardcoreMode': 0}),
                         ('9', 'now', '0'))
        self.assertEqual(m.to_event({'Title': 'Hi', 'Points': 7})['points'], 7)
        self.assertEqual(m.to_event({'Title': 'Hi', 'Points': 'invalid'})['points'], 0)

    def test_badge_url_restrictions(self):
        self.assertEqual(m.badge_url({'BadgeName': '12345'}),
                         'https://retroachievements.org/Badge/12345.png')
        self.assertEqual(m.badge_url({'BadgeURL': 'http://evil.test/Badge/1.png'}), '')
        self.assertEqual(m.badge_url({'BadgeURL': 'https://evil.test/Badge/1.png'}), '')
        self.assertEqual(m.badge_url({'BadgeName': 'x/../../etc'}), '')

    def test_state_event_order(self):
        state = m.State()
        self.assertEqual(state.emit({'title': 'Primeira'})['seq'], 1)
        self.assertEqual(state.emit({'title': 'Segunda'})['seq'], 2)
        self.assertEqual(state.last_unlock, 'Segunda')

    def test_port_unique(self):
        self.assertEqual(m.PORT, 8766)


if __name__ == '__main__':
    unittest.main()
