import pytest

from claim_verification.evaluation.metrics import evaluate

LABELS = ("A", "B", "C")


def test_perfect_prediction():
    out = evaluate([("A", "A"), ("B", "B")], LABELS)
    assert out["accuracy"] == 1.0
    assert out["macro_f1"] == 1.0
    assert out["labels"]["C"] == {"support": 0, "predicted": 0, "precision": 0.0, "recall": 0.0, "f1": 0.0}


def test_scores_and_confusion():
    pairs = [("A", "A"), ("A", "B"), ("B", "B"), ("C", "A")]
    out = evaluate(pairs, LABELS)
    assert out["n"] == 4
    assert out["accuracy"] == 0.5
    assert out["confusion"]["A"] == {"A": 1, "B": 1, "C": 0}
    assert out["confusion"]["C"]["A"] == 1
    a = out["labels"]["A"]
    assert (a["support"], a["predicted"], a["precision"], a["recall"]) == (2, 2, 0.5, 0.5)
    b = out["labels"]["B"]
    assert (b["precision"], b["recall"]) == (0.5, 1.0)
    assert b["f1"] == pytest.approx(2 / 3)
    # 정답에 나온 A·B·C 세 라벨 평균. C는 맞힌 게 없어 0.
    assert out["macro_f1"] == pytest.approx((0.5 + 2 / 3 + 0) / 3)


def test_macro_f1_ignores_labels_absent_from_gold():
    out = evaluate([("A", "A"), ("A", "B")], LABELS)
    assert out["macro_f1"] == pytest.approx(out["labels"]["A"]["f1"])


def test_empty_pairs():
    out = evaluate([], LABELS)
    assert (out["n"], out["accuracy"], out["macro_f1"]) == (0, 0.0, 0.0)


def test_unknown_label_is_error():
    with pytest.raises(ValueError, match="라벨 목록에 없는 값"):
        evaluate([("A", "Z")], LABELS)
