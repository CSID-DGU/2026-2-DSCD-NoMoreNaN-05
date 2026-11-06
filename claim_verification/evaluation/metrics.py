"""분류 지표. (정답, 예측) 쌍 목록 → 정확도, 라벨별 정밀도·재현율·F1, Macro F1, 혼동행렬.

라벨 목록은 호출하는 쪽이 정한다. 라벨 목록 밖의 값이 나오면 오류다.
Macro F1은 정답에 한 번이라도 나온 라벨만 평균한다. 정답에 없는 라벨까지 넣으면 0이 섞여 값이 낮아진다.
분모가 0이면(예측·정답이 없는 라벨) 정밀도·재현율·F1은 0으로 둔다.
"""

from collections import Counter


def evaluate(pairs: list[tuple[str, str]], labels: tuple[str, ...]) -> dict:
    """pairs: [(gold, pred), ...]."""
    unknown = sorted({x for pair in pairs for x in pair} - set(labels))
    if unknown:
        raise ValueError(f"라벨 목록에 없는 값: {unknown}")
    matrix = {g: {p: 0 for p in labels} for g in labels}
    for gold, pred in pairs:
        matrix[gold][pred] += 1
    gold_counts = Counter(g for g, _ in pairs)
    per_label = {label: _scores(matrix, label, labels) for label in labels}
    present = [label for label in labels if gold_counts[label]]
    total = len(pairs)
    correct = sum(matrix[label][label] for label in labels)
    return {
        "n": total,
        "accuracy": correct / total if total else 0.0,
        "macro_f1": sum(per_label[label]["f1"] for label in present) / len(present) if present else 0.0,
        "labels": per_label,
        "confusion": matrix,
    }


def _scores(matrix: dict, label: str, labels: tuple[str, ...]) -> dict:
    tp = matrix[label][label]
    predicted = sum(matrix[g][label] for g in labels)
    support = sum(matrix[label].values())
    precision = tp / predicted if predicted else 0.0
    recall = tp / support if support else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"support": support, "predicted": predicted, "precision": precision, "recall": recall, "f1": f1}
