import csv, importlib.util, json, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("exporter",ROOT/"scripts/export_monthly_csv.py")
exporter=importlib.util.module_from_spec(spec); spec.loader.exec_module(exporter)

class ExportTests(unittest.TestCase):
    def test_model_contract(self):
        self.assertEqual(exporter.MODELS["ENV-20-pH"][1],"ph")
        self.assertEqual(exporter.MODELS["CWT-BL-PH(T)-S"][3],"temperatura_agua_c")
        self.assertEqual(exporter.MODELS["ENV-40-DOX"][52],"oxigeno_disuelto_mg_l")

    def test_sentinels(self):
        self.assertIsNone(exporter.clean("ENV-20-pH","ph",0))
        self.assertIsNone(exporter.clean("ENV-20-pH","ph",14))
        self.assertIsNone(exporter.clean("DS18B20","temperatura_agua_c",-999))
        self.assertIsNone(exporter.clean("ENV-20-EC-K1.0","conductividad_us_cm",0))
        self.assertEqual(exporter.clean("ENV-40-DOX","oxigeno_disuelto_mg_l",0),"0")

    def test_published_contract(self):
        manifest=json.loads((ROOT/"data/manifest.json").read_text())
        self.assertEqual(manifest["schema_version"],1)
        self.assertEqual(len(manifest["stations"]),4)
        for station in manifest["stations"]:
            self.assertTrue(station["months"])
            for month,paths in station["months"].items():
                self.assertGreaterEqual(month,"2025-01")
                for relative in paths:
                    path=ROOT/relative
                    self.assertTrue(path.is_file())
                    with path.open() as handle:
                        rows=list(csv.DictReader(handle))
                    self.assertTrue(rows)
                    self.assertEqual(list(rows[0]),exporter.HEADER)

if __name__=="__main__": unittest.main()
