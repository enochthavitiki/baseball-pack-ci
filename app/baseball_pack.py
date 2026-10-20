"""Baseball domain pack with a SYNTHETIC stand-in decision component.

The real protected decision core is not available to the team, so every
outcome produced here is scripted and labeled synthetic. Requests that
would need the real core are returned as BLOCKED instead of guessed.
"""
import hashlib
import json
from datetime import datetime, timezone

SYNTHETIC_LABEL = "SYNTHETIC - scripted stand-in, not the protected decision core"
VALID_BASES = {"first", "second", "third"}


class InvalidSituation(ValueError):
    pass


def validate(situation: dict) -> None:
    required = ("inning", "outs", "runners", "score_diff")
    missing = [k for k in required if k not in situation]
    if missing:
        raise InvalidSituation(f"missing fields: {', '.join(missing)}")
    if not isinstance(situation["inning"], int) or situation["inning"] < 1:
        raise InvalidSituation("inning must be a positive integer")
    if situation["outs"] not in (0, 1, 2):
        raise InvalidSituation("outs must be 0, 1, or 2")
    runners = situation["runners"]
    if not isinstance(runners, list) or not set(runners) <= VALID_BASES:
        raise InvalidSituation("runners must be a list of: first, second, third")
    if not isinstance(situation["score_diff"], int):
        raise InvalidSituation("score_diff must be an integer (positive = batting team ahead)")


def _scripted_call(s: dict) -> tuple[str, str]:
    """Fixed, readable rules. Deliberately simple: this is a stand-in."""
    runners, outs, diff, late = set(s["runners"]), s["outs"], s["score_diff"], s["inning"] >= 7
    if runners == {"first"} and outs == 0 and late and -1 <= diff <= 0:
        return "SACRIFICE_BUNT", "Late, close game: trade an out to move the tying/go-ahead run into scoring position."
    if "third" in runners and outs < 2 and diff <= 0:
        return "CONTACT_PLAY", "Runner on third with less than two outs: put the ball in play to score him."
    if runners == {"second"} and outs < 2 and late and -1 <= diff <= 0:
        return "PINCH_RUNNER", "Tying/go-ahead run on second late: swap in a faster runner to score on a single."
    if runners == {"first"} and outs == 2:
        return "STEAL_ATTEMPT", "Two outs, runner on first: a steal gets a runner into scoring position with little cost."
    return "HIT_AWAY", "No situational edge identified by the scripted rules."


def receipt_for(situation: dict, decision: dict) -> dict:
    payload = json.dumps({"in": situation, "out": decision}, sort_keys=True).encode()
    return {
        "receipt_id": hashlib.sha256(payload).hexdigest()[:16],
        "issued_at": datetime.now(timezone.utc).isoformat(),
    }


def evaluate(situation: dict) -> dict:
    if situation.get("mode") == "live":
        decision = {
            "status": "BLOCKED",
            "reason": "Live decisions require the protected decision core, which is not available.",
            "synthetic": True,
            "label": SYNTHETIC_LABEL,
        }
        return {**decision, "receipt": receipt_for(situation, decision)}

    validate(situation)
    call, why = _scripted_call(situation)
    decision = {
        "status": "OK",
        "recommendation": call,
        "rationale": why,
        "synthetic": True,
        "label": SYNTHETIC_LABEL,
    }
    return {**decision, "receipt": receipt_for(situation, decision)}
