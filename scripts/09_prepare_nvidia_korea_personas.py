#!/usr/bin/env python3
"""NVIDIA Nemotron-Personas-Korea를 비식별 집계 프로필로 변환한다.

원문 페르소나와 이름은 저장하지 않는다. 출력 JSON은 React 정책 실험기의
연령×성별×권역×교육×직업 층화 표본 생성에만 사용한다.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

DATASET = "nvidia/Nemotron-Personas-Korea"
ALIASES = {
    "age": ("age", "age_years", "current_age"),
    "sex": ("sex", "gender", "biological_sex"),
    "region": ("province", "region", "sido", "residence_province"),
    "education": ("education", "education_level", "highest_education"),
    "occupation": ("occupation", "job", "profession", "detailed_occupation"),
}


def pick(row: dict[str, Any], field: str) -> str:
    lowered = {str(key).lower(): value for key, value in row.items()}
    for alias in ALIASES[field]:
        value = lowered.get(alias)
        if value not in (None, ""):
            return str(value).strip()
    return "미상"


def age_group(value: str) -> str:
    digits = "".join(character for character in value if character.isdigit())
    if not digits:
        return "미상"
    age = max(19, min(99, int(digits[:3])))
    if age < 30:
        return "19-29"
    if age < 40:
        return "30-39"
    if age < 50:
        return "40-49"
    if age < 65:
        return "50-64"
    if age < 75:
        return "65-74"
    return "75-99"


def normalize_region(value: str) -> str:
    if any(token in value for token in ("서울", "경기", "인천")):
        return "수도권"
    if any(token in value for token in ("충북", "충남", "대전", "세종")):
        return "충청권"
    if any(token in value for token in ("전북", "전남", "광주")):
        return "호남권"
    if any(token in value for token in ("경북", "경남", "부산", "대구", "울산")):
        return "영남권"
    if any(token in value for token in ("강원", "제주")):
        return "강원·제주"
    return value or "미상"


def rows(limit: int) -> Iterable[dict[str, Any]]:
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise SystemExit("pip install -r requirements-nvidia.txt 를 먼저 실행하십시오.") from exc
    stream = load_dataset(DATASET, split="train", streaming=True)
    for index, row in enumerate(stream):
        if index >= limit:
            break
        yield row


def aggregate(records: Iterable[dict[str, Any]]) -> tuple[Counter[tuple[str, ...]], int]:
    counter: Counter[tuple[str, ...]] = Counter()
    total = 0
    for row in records:
        key = (
            age_group(pick(row, "age")),
            pick(row, "sex"),
            normalize_region(pick(row, "region")),
            pick(row, "education"),
            pick(row, "occupation"),
        )
        counter[key] += 1
        total += 1
    return counter, total


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=100_000, help="스트리밍 집계할 최대 레코드 수")
    parser.add_argument("--output", type=Path, default=Path("public/data/nvidia-korea-profile.json"))
    args = parser.parse_args()
    if args.rows < 100:
        raise SystemExit("--rows는 100 이상이어야 합니다.")
    counts, total = aggregate(rows(args.rows))
    if not total:
        raise SystemExit("데이터셋에서 레코드를 읽지 못했습니다.")
    payload = {
        "schemaVersion": 1,
        "source": "NVIDIA Nemotron-Personas-Korea",
        "dataset": DATASET,
        "license": "CC BY 4.0",
        "sampleSize": total,
        "strata": [
            {
                "ageGroup": key[0], "sex": key[1], "region": key[2],
                "education": key[3], "occupation": key[4], "count": count,
            }
            for key, count in counts.most_common()
        ],
        "limitations": [
            "NVIDIA 데이터는 실제 분포를 참고해 만든 완전 합성 페르소나이다.",
            "데이터 카드가 밝힌 변수 간 독립성 가정 때문에 결합분포 대표성을 보장하지 않는다.",
            "정책효과·여론·행동의 인과 추정에 사용해서는 안 된다.",
            "원문 이름과 자연어 페르소나는 이 집계 파일에 저장하지 않는다.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "records": total, "strata": len(counts)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
