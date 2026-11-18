import unittest
from pathlib import Path
from app.analytics import load_aggregate, missing_vehicle_percent, ticket_signal, validation_summary

class AnalyticsTests(unittest.TestCase):
    def setUp(self): self.stats=load_aggregate(Path(__file__).parents[1]/"data"/"demo_tickets.csv")
    def test_demo_csv_uses_schema_and_has_missing_vehicle_numbers(self):
        self.assertGreater(self.stats["ticket_rows"],100)
        self.assertIsNotNone(missing_vehicle_percent(self.stats))
        self.assertGreater(missing_vehicle_percent(self.stats),0)
    def test_signal_is_bounded_and_reports_confidence(self):
        signal=ticket_signal(self.stats,"SAMPLE-A","08:30")
        self.assertGreaterEqual(signal["score"],0); self.assertLessEqual(signal["score"],100)
        self.assertIn(signal["confidence"],{"low","medium","high"})
        self.assertNotIn("occupancy",signal)
    def test_validation_flags_small_or_zero_samples(self):
        result=validation_summary({"routes":{}},"SAMPLE-A")
        self.assertFalse(result["sufficient_sample"])
        self.assertEqual(result["trend"], "No matching samples")
        self.assertIn("held-out",result["note"])
    def test_peak_signal_is_not_lower_than_low_activity_for_demo(self):
        peak=ticket_signal(self.stats,"SAMPLE-A","08:30")
        low=ticket_signal(self.stats,"SAMPLE-A","14:30")
        self.assertGreaterEqual(peak["score"],low["score"])

if __name__=="__main__": unittest.main()
