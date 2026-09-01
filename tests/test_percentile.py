"""Tests for the score-to-percentile walk and the olympiad correction."""

import os
import random
import unittest

from lib import admissions, percentile

# Few draws per run, unseeded, so successive runs cover different scores rather
# than one run covering them all. FUZZ=2000 python3 -m unittest ... to chase a
# failure.
FUZZ = int(os.environ.get("FUZZ", 200))


class TestPercentile(unittest.TestCase):
    def setUp(self):
        self.years = percentile.years()
        if not self.years:
            self.skipTest("cohort-steps.tsv has not been built")

    def test_a_higher_score_never_ranks_lower(self):
        for _ in range(FUZZ):
            year = random.choice(self.years)
            low = random.uniform(0.0, 100.0)
            high = low + random.uniform(0.0, 100.0 - low)
            self.assertLessEqual(percentile.percentile(low, year),
                                 percentile.percentile(high, year))

    def test_every_percentile_stays_on_the_scale(self):
        for _ in range(FUZZ):
            year = random.choice(self.years)
            points = percentile.table()[year]
            found = percentile.percentile(
                random.uniform(points[0][0], points[-1][0]), year
            )
            self.assertGreaterEqual(found, 0.0)
            self.assertLessEqual(found, 100.0)

    def test_outside_policy_depends_on_whether_the_curve_was_carried(self):
        for year in self.years:
            points = percentile.table()[year]
            outside = (percentile.percentile(points[0][0] - 1, year),
                       percentile.percentile(points[-1][0] + 1, year))
            if points.metadata["carried"]:
                self.assertEqual(outside, (points[0][1], points[-1][1]))
            else:
                self.assertEqual(outside, (None, None))

    def test_a_published_step_returns_its_own_percentile(self):
        for year in self.years:
            steps = percentile.table()[year]
            for score, published in random.sample(steps, min(20, len(steps))):
                self.assertAlmostEqual(percentile.percentile(score, year),
                                       published, places=6)


class TestOlympiadCorrection(unittest.TestCase):
    def test_putting_the_hundreds_back_returns_the_published_average(self):
        for _ in range(FUZZ):
            students = random.randint(2, 4000)
            bvi = random.randint(0, students - 1)
            published = round(random.uniform(40.0, 99.0), 1)
            row = {"students": students, "bvi": bvi, "mean_ege": published}
            examined = admissions.mean_excluding_bvi(row)
            restored = (examined * (students - bvi) + 100.0 * bvi) / students
            self.assertAlmostEqual(restored, published, places=3)

    def test_an_all_olympiad_group_keeps_its_published_average(self):
        row = {"students": 12, "bvi": 12, "mean_ege": 100.0}
        self.assertEqual(admissions.mean_excluding_bvi(row), 100.0)


if __name__ == "__main__":
    unittest.main()
