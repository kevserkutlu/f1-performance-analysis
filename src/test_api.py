
import requests

BASE_URL = "http://127.0.0.1:5000"

# ─── Yardımcı fonksiyon ────────────────────────────────────────────────────

def print_result(test_name: str, response: requests.Response) -> None:
    status = "✅ PASS" if response.status_code == 200 else "❌ FAIL"
    print(f"\n{status}  [{response.status_code}]  {test_name}")
    try:
        print(f"  → {response.json()}")
    except Exception:
        print(f"  → {response.text[:200]}")


# ─── TEST 1: Ana sayfa ─────────────────────────────────────────────────────

def test_home():
    r = requests.get(f"{BASE_URL}/")
    print_result("GET /  (ana sayfa)", r)
    assert r.status_code == 200
    assert "endpoints" in r.json()


# ─── TEST 2: Sağlık kontrolü ───────────────────────────────────────────────

def test_health():
    r = requests.get(f"{BASE_URL}/health")
    print_result("GET /health", r)
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


# ─── TEST 3: Normal tahmin (tüm alanlar var) ───────────────────────────────

def test_predict_full():
    payload = {
        "grid": 1,
        "driver_form_score": 3.5,
        "weekend_readiness": 2.8,
        "driver_season_momentum": 18.0,
        "last_3_race_avg_finish": 3.0,
        "last_5_race_avg_finish": 4.0,
    }
    r = requests.post(f"{BASE_URL}/predict", json=payload)
    print_result("POST /predict (tam veri)", r)
    assert r.status_code == 200
    pred = r.json()["prediction"]
    assert 1 <= pred <= 20, f"Tahmin aralık dışı: {pred}"


# ─── TEST 4: Minimum veri (sadece grid) ───────────────────────────────────

def test_predict_minimal():
    payload = {"grid": 5}
    r = requests.post(f"{BASE_URL}/predict", json=payload)
    print_result("POST /predict (sadece grid)", r)
    assert r.status_code == 200
    pred = r.json()["prediction"]
    assert 1 <= pred <= 20, f"Tahmin aralık dışı: {pred}"


# ─── TEST 5: grid eksik → 400 hatası bekliyoruz ───────────────────────────

def test_predict_missing_grid():
    payload = {"driver_form_score": 3.5}
    r = requests.post(f"{BASE_URL}/predict", json=payload)
    print_result("POST /predict (grid eksik → 400 beklenir)", r)
    assert r.status_code == 400
    assert "error" in r.json()


# ─── TEST 6: Boş body → 400 hatası bekliyoruz ─────────────────────────────

def test_predict_empty_body():
    r = requests.post(f"{BASE_URL}/predict", json={})
    print_result("POST /predict (boş body → 400 beklenir)", r)
    assert r.status_code == 400


# ─── TEST 7: Birden fazla yarışçı tahmini ─────────────────────────────────

def test_predict_multiple_drivers():
    drivers = [
        {"name": "Verstappen", "grid": 1, "driver_form_score": 2.1, "driver_season_momentum": 22.0},
        {"name": "Hamilton",   "grid": 4, "driver_form_score": 4.5, "driver_season_momentum": 15.0},
        {"name": "Alonso",     "grid": 8, "driver_form_score": 7.0, "driver_season_momentum": 10.0},
    ]
    print("\n--- TEST 7: Çoklu Sürücü Tahmini ---")
    for d in drivers:
        name = d.pop("name")
        r = requests.post(f"{BASE_URL}/predict", json=d)
        pred = r.json().get("prediction", "ERR")
        print(f"  {name:12s}  grid={d['grid']:2d}  →  tahmin: P{pred}")
        assert r.status_code == 200


# ─── ANA ÇALIŞTIRICI ───────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("  F1 Performance API — Dilara'nın Test Paketi 🏎️")
    print("=" * 55)

    tests = [
        test_home,
        test_health,
        test_predict_full,
        test_predict_minimal,
        test_predict_missing_grid,
        test_predict_empty_body,
        test_predict_multiple_drivers,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ⚠️  AssertionError: {e}")
            failed += 1
        except requests.exceptions.ConnectionError:
            print("\n❌ API'ye bağlanılamadı!")
            print("   → Önce 'python api.py' komutunu çalıştır.")
            break

    print("\n" + "=" * 55)
    print(f"  Sonuç: {passed} PASS  |  {failed} FAIL")
    print("=" * 55)