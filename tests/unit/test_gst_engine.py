import pytest
from decimal import Decimal

# Assuming a placeholder GST engine function based on constraints
def calculate_gst(amount: Decimal, rate: Decimal, is_interstate: bool):
    gst = amount * (rate / 100)
    if is_interstate:
        return {"igst": gst.quantize(Decimal("0.01")), "cgst": Decimal("0.00"), "sgst": Decimal("0.00"), "total": (amount + gst).quantize(Decimal("0.01"))}
    else:
        half = (gst / 2).quantize(Decimal("0.01"))
        return {"igst": Decimal("0.00"), "cgst": half, "sgst": half, "total": (amount + half + half).quantize(Decimal("0.01"))}

def test_intrastate_cgst_sgst_split_equal():
    res = calculate_gst(Decimal("100.00"), Decimal("18"), False)
    assert res["cgst"] == Decimal("9.00")
    assert res["sgst"] == Decimal("9.00")

def test_interstate_full_igst_applied():
    res = calculate_gst(Decimal("100.00"), Decimal("18"), True)
    assert res["igst"] == Decimal("18.00")

def test_28_pct_gst_on_parts():
    res = calculate_gst(Decimal("1000.00"), Decimal("28"), False)
    assert res["cgst"] == Decimal("140.00")

def test_18_pct_gst_on_labor():
    res = calculate_gst(Decimal("2000.00"), Decimal("18"), False)
    assert res["cgst"] == Decimal("180.00")

def test_total_equals_subtotal_plus_gst():
    res = calculate_gst(Decimal("1000.00"), Decimal("18"), False)
    assert res["total"] == Decimal("1180.00")

def test_zero_gst_on_warranty_item():
    res = calculate_gst(Decimal("1000.00"), Decimal("0"), False)
    assert res["total"] == Decimal("1000.00")

