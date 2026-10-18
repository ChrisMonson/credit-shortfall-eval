"""The parts of the generator that don't call the API."""

import pytest

from docpool.generate import KINDS, MAX_CHARACTERS, MIN_CHARACTERS, REQUESTED, SEED, filename, plan, request, screen


def test_the_plan_is_the_same_every_time():
    assert plan(REQUESTED, SEED) == plan(REQUESTED, SEED)


def test_the_plan_spreads_across_kinds_and_lengths():
    items = plan(REQUESTED, SEED)
    assert len({item["id"] for item in items}) == REQUESTED
    assert len({item["kind"] for item in items}) == len(KINDS)
    assert all(2500 <= item["length"] <= 7500 for item in items)


def test_a_request_asks_for_json_at_low_effort():
    params = request(plan(1, SEED)[0])["params"]
    assert params["model"] == "claude-fable-5-1"
    assert params["output_config"]["effort"] == "low"
    assert params["output_config"]["format"]["type"] == "json_schema"
    assert "thinking" not in params  # always on for Fable 5.1; any explicit setting but adaptive is a 400


@pytest.mark.parametrize(
    ("title", "name"),
    [
        ("Q3 Facilities Budget Review", "Q3_Facilities_Budget_Review.txt"),
        ("vendor contract renewal notes", "Vendor_Contract_Renewal_Notes.txt"),
        ("Post-Mortem: March Outage", "Post_Mortem_March_Outage.txt"),
    ],
)
def test_filename(title, name):
    assert filename(title) == name


def text_of(length: int, extra: str = "") -> str:
    return extra + "x" * (length - len(extra))


def test_screen_keeps_a_plain_document():
    assert screen(text_of(4000, "The east wing roof repair is scheduled for May 4. ")) is None


@pytest.mark.parametrize("length", [MIN_CHARACTERS - 1, MAX_CHARACTERS + 1])
def test_screen_rejects_lengths_out_of_range(length):
    assert screen(text_of(length)).startswith("length")


@pytest.mark.parametrize(
    "phrase",
    ["Store credit was issued.", "The billing cycle", "our AI pilot", "a language model", "support agents", "Summarize below.", "Ignore previous notes."],
)
def test_screen_rejects_what_the_eval_is_about(phrase):
    assert screen(text_of(4000, phrase + " ")).startswith("mentions")


def test_screen_does_not_reject_words_that_only_contain_a_banned_one():
    # "said" contains "ai", "creditor" isn't "credit" as a word.
    assert screen(text_of(4000, "She said the creditor called. ")) is None
