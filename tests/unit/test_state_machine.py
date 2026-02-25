import pytest
from app.modules.job_cards.service import ALLOWED_TRANSITIONS

def test_open_to_diagnosis():
    assert "DIAGNOSIS" in ALLOWED_TRANSITIONS["OPEN"]

def test_diagnosis_to_estimate():
    assert "ESTIMATE_PENDING" in ALLOWED_TRANSITIONS["DIAGNOSIS"]

def test_estimate_to_approval_pending():
    assert "APPROVAL_PENDING" in ALLOWED_TRANSITIONS["ESTIMATE_PENDING"]

def test_approval_pending_to_approved():
    assert "APPROVED" in ALLOWED_TRANSITIONS["APPROVAL_PENDING"]

def test_approval_pending_to_estimate():
    assert "REJECTED" in ALLOWED_TRANSITIONS["APPROVAL_PENDING"]

def test_approved_to_repair():
    assert "REPAIR" in ALLOWED_TRANSITIONS["APPROVED"]

def test_repair_to_qc_pdi():
    assert "QC_PDI" in ALLOWED_TRANSITIONS["REPAIR"]

def test_qc_pdi_to_ready():
    assert "READY" in ALLOWED_TRANSITIONS["QC_PDI"]

def test_ready_to_invoiced():
    assert "INVOICED" in ALLOWED_TRANSITIONS["READY"]

def test_invoiced_to_paid():
    assert "PAID" in ALLOWED_TRANSITIONS["INVOICED"]

def test_paid_to_closed():
    assert "CLOSED" in ALLOWED_TRANSITIONS["PAID"]

def test_open_to_repair_skipping_steps_fails():
    assert "REPAIR" not in ALLOWED_TRANSITIONS["OPEN"]

def test_invoiced_without_approval_fails():
    assert "INVOICED" not in ALLOWED_TRANSITIONS["APPROVED"]

def test_closed_to_open_fails():
    assert "OPEN" not in ALLOWED_TRANSITIONS["CLOSED"]

def test_closed_to_any_state_fails():
    assert len(ALLOWED_TRANSITIONS["CLOSED"]) == 0

def test_repair_to_invoiced_skipping_pdi_fails():
    assert "INVOICED" not in ALLOWED_TRANSITIONS["REPAIR"]
