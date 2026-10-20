import pytest

from app.baseball_pack import SYNTHETIC_LABEL, InvalidSituation, evaluate


def sit(**kw):
    base = {"inning": 1, "outs": 0, "runners": [], "score_diff": 0}
    base.update(kw)
    return base


def test_late_close_game_bunts():
    assert evaluate(sit(inning=8, runners=["first"], score_diff=-1))["recommendation"] == "SACRIFICE_BUNT"


def test_runner_on_third_contact_play():
    assert evaluate(sit(outs=1, runners=["third"]))["recommendation"] == "CONTACT_PLAY"


def test_two_outs_runner_on_first_steals():
    assert evaluate(sit(outs=2, runners=["first"], score_diff=4))["recommendation"] == "STEAL_ATTEMPT"


def test_default_hit_away():
    assert evaluate(sit())["recommendation"] == "HIT_AWAY"


def test_every_outcome_is_labeled_synthetic():
    out = evaluate(sit())
    assert out["synthetic"] is True and out["label"] == SYNTHETIC_LABEL


def test_live_mode_is_blocked_not_guessed():
    out = evaluate(sit(mode="live"))
    assert out["status"] == "BLOCKED" and "recommendation" not in out


def test_receipt_is_deterministic_for_same_input():
    a, b = evaluate(sit()), evaluate(sit())
    assert a["receipt"]["receipt_id"] == b["receipt"]["receipt_id"]


@pytest.mark.parametrize("bad", [
    {"outs": 0, "runners": [], "score_diff": 0},          # missing inning
    sit(outs=3),
    sit(runners=["home"]),
    sit(inning=0),
])
def test_invalid_situations_rejected(bad):
    with pytest.raises(InvalidSituation):
        evaluate(bad)


def test_late_tied_runner_on_second_gets_pinch_runner():
    assert evaluate(sit(inning=9, outs=1, runners=["second"], score_diff=0))["recommendation"] == "PINCH_RUNNER"


def test_pinch_runner_not_used_early():
    assert evaluate(sit(inning=3, outs=1, runners=["second"], score_diff=0))["recommendation"] == "HIT_AWAY"
