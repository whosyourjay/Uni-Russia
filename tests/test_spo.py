"""Small fixtures for the СПО parser's published/missing distinction."""

import unittest

from lib import html
from parse import spo


PAGE = """
<div id='inst_name'>Тестовый колледж</div>
<a href='material.php?type=2&id=10101'>Тестовая область</a>
<table class='table_ugs'><tr><td>09.00.00 - Информатика</td><td>1</td></tr></table>
<tr N='1.1'><td>1.1. Общая численность студентов, чел.</td><td></td><td>500</td><td>1 000</td><td>3 000</td></tr>
<tr N='1.5.1'><td>Средний балл аттестата студентов, принятых на обучение, балл</td><td></td><td>4,10</td><td>4,00</td><td>3,96</td></tr>
<tr N='1.6.1'><td>Средний балл аттестата студентов, принятых за счет средств бюджета, балл</td><td></td><td>4,20</td><td>4,10</td><td>3,98</td></tr>
<tr N='1.7.1'><td>Средний балл аттестата студентов, принятых по договорам платных услуг, балл</td><td></td><td>3,90</td><td>3,80</td><td>3,92</td></tr>
<tr N='1.8'><td>Имеющих средний балл аттестата не менее 4-х баллов</td><td></td><td>55,00</td><td>50</td><td>47,73</td></tr>
"""


class TestSpo(unittest.TestCase):
    def test_index_links_may_use_single_quotes(self):
        self.assertEqual(html.links("<a href='one'>First</a>"),
                         [("one", "First")])

    def test_funding_is_a_column_not_a_route(self):
        row = spo.parse_page(PAGE, 2023, "7")
        self.assertEqual(row["admitted_gpa"], 4.1)
        self.assertEqual(row["budget_admitted_gpa"], 4.2)
        self.assertEqual(row["paid_admitted_gpa"], 3.9)

    def test_public_page_does_not_turn_enrollment_into_admission_seats(self):
        row = spo.parse_page(PAGE, 2023, "7")
        self.assertEqual(row["current_students"], 500)
        self.assertEqual(row["admitted_students"], "")

    def test_offered_fields_do_not_gain_fake_scores_or_seats(self):
        self.assertEqual(spo.fields(PAGE), [("09.00.00", "Информатика")])


if __name__ == "__main__":
    unittest.main()
