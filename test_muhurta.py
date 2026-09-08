#!/usr/bin/env python3
"""
Unit tests for Muhurta / Vastu date-selection rules (evaluate_muhurta_day).

Unlike test_api.py, these tests are pure-function tests against canned
panchang dicts shaped like compute_panchang()'s output — no live server
or network calls required. Run with:

    uv run python test_muhurta.py
"""

from app import evaluate_muhurta_day

BASE_PANCHANG = {
    "date": "2026-05-06",  # a Wednesday
    "tamil_month": "Chithirai",
    "weekday": {"english": "Wednesday", "tamil": "Budhan"},
    "tithi": {"number": 2, "name": "Dwithiya", "paksha": "Shukla Paksha", "remaining": 50.0},
    "nakshatra": {"number": 4, "name": "Rohini", "remaining": 50.0},
    "karana": {"number": 3, "name": "Kaulava"},
    "amirthathi_yoga": {"number": 1, "name": "Amirtha", "type": "Auspicious"},
    "special_yoga": {"name": "Siddha", "type": "Auspicious"},
}


def _panchang(**overrides):
    data = {k: dict(v) if isinstance(v, dict) else v for k, v in BASE_PANCHANG.items()}
    data.update(overrides)
    return data


def _assert_rejects(result, keyword):
    assert not result["qualifies"], f"expected rejection, got qualifies=True: {result}"
    assert any(keyword.lower() in r.lower() for r in result["reasons"]), (
        f"expected a reason mentioning '{keyword}', got: {result['reasons']}"
    )


def test_general_clean_day_qualifies():
    result = evaluate_muhurta_day(_panchang(), "general")
    assert result["qualifies"] is True
    assert result["reasons"] == []
    print("PASS: general clean day qualifies")


def test_rikta_tithi_rejected():
    for rikta_number in (4, 9, 14, 19, 24, 29):
        panchang = _panchang(tithi={**BASE_PANCHANG["tithi"], "number": rikta_number})
        result = evaluate_muhurta_day(panchang, "general")
        _assert_rejects(result, "rikta")
    print("PASS: all six rikta tithis rejected")


def test_amavasya_rejected_for_griha_pravesam():
    panchang = _panchang(
        tithi={"number": 30, "name": "Pournami/Amavasya", "paksha": "Krishna Paksha"},
        nakshatra={"number": 4, "name": "Rohini"},  # valid Mel Nokku nakshatra otherwise
    )
    result = evaluate_muhurta_day(panchang, "griha_pravesam")
    _assert_rejects(result, "amavasya")
    print("PASS: amavasya rejected for griha_pravesam")


def test_amavasya_allowed_for_general():
    panchang = _panchang(
        tithi={"number": 30, "name": "Pournami/Amavasya", "paksha": "Krishna Paksha"}
    )
    result = evaluate_muhurta_day(panchang, "general")
    assert result["qualifies"] is True, result["reasons"]
    print("PASS: amavasya not excluded for general activity (no rule for it)")


def test_vishti_karana_rejected():
    panchang = _panchang(karana={"number": 7, "name": "Vishti"})
    result = evaluate_muhurta_day(panchang, "general")
    _assert_rejects(result, "vishti")
    print("PASS: Vishti karana rejected")


def test_inauspicious_amirthathi_yoga_rejected():
    panchang = _panchang(amirthathi_yoga={"number": 3, "name": "Marana", "type": "Inauspicious"})
    result = evaluate_muhurta_day(panchang, "general")
    _assert_rejects(result, "amirthathi")
    print("PASS: inauspicious Amirthathi Yoga rejected")


def test_marana_special_yoga_rejected():
    panchang = _panchang(special_yoga={"name": "Marana", "type": "Inauspicious"})
    result = evaluate_muhurta_day(panchang, "general")
    _assert_rejects(result, "marana")
    print("PASS: Marana special yoga rejected")


def test_griha_pravesam_requires_mel_nokku_nakshatra():
    # Bharani is a Keezh Nokku nakshatra, not Mel Nokku -> should fail for griha_pravesam
    panchang = _panchang(nakshatra={"number": 2, "name": "Bharani"})
    result = evaluate_muhurta_day(panchang, "griha_pravesam")
    _assert_rejects(result, "nakshatra")
    print("PASS: griha_pravesam rejects non-Mel-Nokku nakshatra")


def test_griha_pravesam_accepts_mel_nokku_nakshatra():
    panchang = _panchang(nakshatra={"number": 4, "name": "Rohini"})  # Mel Nokku
    result = evaluate_muhurta_day(panchang, "griha_pravesam")
    assert result["qualifies"] is True, result["reasons"]
    print("PASS: griha_pravesam accepts Mel Nokku nakshatra (Rohini)")


def test_bhoomi_pooja_requires_keezh_nokku_nakshatra():
    panchang = _panchang(nakshatra={"number": 4, "name": "Rohini"})  # Mel Nokku, not Keezh
    result = evaluate_muhurta_day(panchang, "bhoomi_pooja")
    _assert_rejects(result, "nakshatra")
    print("PASS: bhoomi_pooja rejects non-Keezh-Nokku nakshatra")


def test_bhoomi_pooja_accepts_keezh_nokku_nakshatra():
    panchang = _panchang(nakshatra={"number": 2, "name": "Bharani"})  # Keezh Nokku
    result = evaluate_muhurta_day(panchang, "bhoomi_pooja")
    assert result["qualifies"] is True, result["reasons"]
    print("PASS: bhoomi_pooja accepts Keezh Nokku nakshatra (Bharani)")


def test_vastu_excludes_tuesday_and_saturday():
    for weekday_name in ("Tuesday", "Saturday"):
        panchang = _panchang(
            nakshatra={"number": 4, "name": "Rohini"},
            weekday={"english": weekday_name, "tamil": ""},
        )
        result = evaluate_muhurta_day(panchang, "griha_pravesam")
        _assert_rejects(
            result, "weekday" if "weekday" in "".join(result["reasons"]).lower() else weekday_name
        )
    print("PASS: griha_pravesam rejects Tuesday and Saturday")


def test_vastu_excludes_aadi_and_margazhi():
    for month in ("Aadi", "Margazhi"):
        panchang = _panchang(nakshatra={"number": 4, "name": "Rohini"}, tamil_month=month)
        result = evaluate_muhurta_day(panchang, "bhoomi_pooja")
        _assert_rejects(result, month)
    print("PASS: bhoomi_pooja rejects Aadi and Margazhi")


def test_multiple_violations_all_reported():
    panchang = _panchang(
        tithi={"number": 4, "name": "Chathurthi", "paksha": "Shukla Paksha"},
        karana={"number": 7, "name": "Vishti"},
        nakshatra={"number": 2, "name": "Bharani"},
    )
    result = evaluate_muhurta_day(panchang, "griha_pravesam")
    assert not result["qualifies"]
    assert len(result["reasons"]) >= 3, result["reasons"]
    print("PASS: multiple simultaneous violations are all reported")


def test_unknown_activity_raises():
    try:
        evaluate_muhurta_day(_panchang(), "housewarming_party")
        raise AssertionError("expected ValueError for unknown activity")
    except ValueError:
        print("PASS: unknown activity raises ValueError")


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for test in tests:
        test()
    print(f"\n✅ All {len(tests)} muhurta rule tests passed!")


if __name__ == "__main__":
    main()
