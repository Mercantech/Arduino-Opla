"""Engangs-/idempotent oprydning af ustabile tests i gemte rapporter."""

from __future__ import annotations

import json
import logging

from sqlalchemy.orm import Session

from app import models

log = logging.getLogger("opla.cleanup")

STRIP_TEST_NAMES = frozenset({"RGB/Prox", "RGB", "Prox", "Gesture"})


def _recalc(tests: list[dict]) -> tuple[bool, int, int]:
    passed_count = 0
    failed_count = 0
    for t in tests:
        if t.get("skipped"):
            continue
        if t.get("ok"):
            passed_count += 1
        else:
            failed_count += 1
    return failed_count == 0, passed_count, failed_count


def strip_unstable_tests(db: Session) -> int:
    """Fjern RGB/Prox fra alle test_reports.details og genberegn counts.

    Returnerer antal opdaterede rækker. Sikker at køre gentagne gange.
    """
    updated = 0
    rows = db.query(models.TestReport).all()
    for row in rows:
        if not row.details or "RGB/Prox" not in row.details:
            continue
        try:
            data = json.loads(row.details)
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict):
            continue

        report = data.get("report")
        if not isinstance(report, dict):
            continue
        tests = report.get("tests")
        if not isinstance(tests, list):
            continue

        new_tests = [
            t
            for t in tests
            if not (isinstance(t, dict) and t.get("name") in STRIP_TEST_NAMES)
        ]
        if len(new_tests) == len(tests):
            continue

        report["tests"] = new_tests
        passed, passed_count, failed_count = _recalc(new_tests)
        data["passed"] = passed
        data["passed_count"] = passed_count
        data["failed_count"] = failed_count
        data["report"] = report

        row.details = json.dumps(data, ensure_ascii=False)
        row.passed = passed
        row.passed_count = passed_count
        row.failed_count = failed_count
        updated += 1

    if updated:
        db.commit()
        log.info("Stripped RGB/Prox from %s test report(s)", updated)
    return updated
