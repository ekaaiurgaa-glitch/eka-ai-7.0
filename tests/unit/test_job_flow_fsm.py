import pytest
from app.modules.job_cards.service import ALLOWED_TRANSITIONS

def test_allowed_transitions():
    """ Tests that a valid transition is allowed. """
    assert "DIAGNOSIS" in ALLOWED_TRANSITIONS["OPEN"]
    assert "REPAIR" in ALLOWED_TRANSITIONS["APPROVED"]

def test_disallowed_transitions():
    """ Tests that an invalid transition is not allowed. """
    assert "REPAIR" not in ALLOWED_TRANSITIONS["OPEN"]
    assert "CLOSED" not in ALLOWED_TRANSITIONS["INVOICED"] # Should go to PAID first

def test_no_transitions_from_closed():
    """ Tests that there are no transitions from a CLOSED state. """
    assert len(ALLOWED_TRANSITIONS["CLOSED"]) == 0

# To test the actual service function, we would need to mock the database
# and the `get_job_card` function.
# Example using pytest-mock:
#
# def test_transition_service_success(mocker):
#     mock_db = mocker.Mock()
#     mock_job_card = mocker.Mock()
#     mock_job_card.state = "OPEN"
#     mocker.patch('app.modules.job_cards.service.get_job_card', return_value=mock_job_card)
#
#     from app.modules.job_cards.service import transition_job_card_state
#     transition_job_card_state(mock_db, 1, "DIAGNOSIS", "tenant", "user")
#
#     assert mock_job_card.state == "DIAGNOSIS"
#     mock_db.commit.assert_called_once()

