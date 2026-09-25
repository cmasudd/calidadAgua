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
        self.assertEqual(exporter.MODELS["A01NYUB"][22],"distancia_agua_m")
        self.assertEqual(exporter.MODELS["LIQ-136"][23],"profundidad_m")
        self.assertEqual(exporter.MODELS["SHT40"],{3:"temperatura_aire_c",6:"humedad_aire_pct"})

    def test_sentinels(self):
        self.assertIsNone(exporter.clean("ENV-20-pH","ph",0))
        self.assertIsNone(exporter.clean("ENV-20-pH","ph",14))
        self.assertIsNone(exporter.clean("DS18B20","temperatura_agua_c",-999))
        self.assertIsNone(exporter.clean("ENV-20-EC-K1.0","conductividad_us_cm",0))
        self.assertEqual(exporter.clean("ENV-40-DOX","oxigeno_disuelto_mg_l",0),"0")
        self.assertEqual(exporter.clean("A01NYUB","distancia_agua_m",0),"0")
        self.assertIsNone(exporter.clean("SHT40","humedad_aire_pct",101))
        self.assertIsNone(exporter.clean("DS3231","temperatura_sistema_c",237.5))

    def test_published_contract(self):
        manifest=json.loads((ROOT/"data/manifest.json").read_text())
        self.assertEqual(manifest["schema_version"],1)
        self.assertEqual({s["code"] for s in manifest["stations"]},{"AGUA-01","AGUA-02","AGUA-03","URA-01","LVAG-02","LVAG-03","LVAG-04","LVAG-05"})
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
                    self.assertTrue(set(rows[0]).issubset(exporter.HEADER))
                    self.assertIn("fecha",rows[0])
            if station["code"].startswith("LVAG"):
                self.assertIn("profundidad_m",station["variables"])
                current=ROOT/station["months"][max(station["months"])][0]
                with current.open() as handle:
                    rows=list(csv.DictReader(handle))
                self.assertTrue(any(row["profundidad_m"] for row in rows))
                self.assertTrue(any(row["distancia_agua_m"] for row in rows))

if __name__=="__main__": unittest.main()
