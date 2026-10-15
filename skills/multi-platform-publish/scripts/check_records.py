#!/usr/bin/env python3
"""Offline consistency checks; does not authenticate or read any platform."""
import argparse
import datetime as dt
import json
from pathlib import Path
import re
import sys

PLATFORMS = {'xiaohongshu', 'wechat_official', 'wechat_channels', 'douyin', 'bilibili'}
STAGES = {'not_started', 'editing', 'submission_unknown', 'submitted_for_review',
          'scheduled', 'backend_published', 'blocked', 'needs_changes'}


def check(plan, result, evidence_root=None):
    errors = []

    def timestamp(value, label):
        if value is None:
            return None
        try:
            # .NET emits seven fractional digits; Python 3.10 accepts at most six.
            normalized = re.sub(r'(\.\d{6})\d+(?=[+-]|Z|$)', r'\1', value)
            parsed = dt.datetime.fromisoformat(normalized.replace('Z', '+00:00'))
            if parsed.utcoffset() is None:
                raise ValueError('timezone missing')
            return parsed
        except (TypeError, AttributeError, ValueError):
            errors.append(label + ': invalid or timezone-free timestamp')
            return None

    def index(doc, label):
        rows = doc.get('entries') if isinstance(doc, dict) else None
        if not isinstance(rows, list) or not rows:
            errors.append(label + ': nonempty entries required')
            return {}
        indexed = {}
        for row in rows:
            if not isinstance(row, dict):
                errors.append(label + ': entry must be an object')
                continue
            key = (row.get('slug') or row.get('content_id'), row.get('version'), row.get('platform'))
            if not all(isinstance(x, str) and x for x in key):
                errors.append(label + ': missing identity')
                continue
            if key[2] not in PLATFORMS:
                errors.append(label + ': unsupported platform ' + key[2])
            if key in indexed:
                errors.append(label + ': duplicate ' + '/'.join(key))
            indexed[key] = row
        return indexed

    plans, results = index(plan, 'plan'), index(result, 'result')
    if plans.keys() != results.keys():
        errors.append('plan/result identity sets differ')
    saved = public = 0
    for key in plans.keys() & results.keys():
        expected, actual = plans[key], results[key]
        label = '/'.join(key)
        wanted_hash = expected.get('asset_sha256') or expected.get('video_sha256')
        actual_hash = actual.get('asset_sha256')
        if not isinstance(wanted_hash, str) or not re.fullmatch(r'[a-fA-F0-9]{64}', wanted_hash):
            errors.append(label + ': invalid planned asset hash')
        if wanted_hash != actual_hash:
            errors.append(label + ': asset hash mismatch')
        wanted_time = timestamp(expected.get('schedule_at'), label + ' plan')
        actual_time = timestamp(actual.get('scheduled_for'), label + ' result')
        if wanted_time != actual_time:
            errors.append(label + ': schedule mismatch')
        attempt = actual.get('submit_attempt')
        if type(attempt) is not int or attempt < 0:
            errors.append(label + ': submit_attempt must be a nonnegative integer')
        stage = actual.get('stage')
        if stage not in STAGES:
            errors.append(label + ': invalid stage')
        evidence = actual.get('evidence', [])
        if not isinstance(evidence, list) or any(not isinstance(x, str) or not x for x in evidence):
            errors.append(label + ': evidence must be a list of nonempty paths')
            evidence = []
        schedule_saved = actual.get('native_schedule_saved', False)
        if type(schedule_saved) is not bool:
            errors.append(label + ': native_schedule_saved must be boolean')
        verified = timestamp(actual.get('backend_verified_at'), label + ' backend')
        if schedule_saved is True:
            saved += 1
            if not wanted_time or not verified or not actual.get('backend_status') or not evidence:
                errors.append(label + ': saved schedule requires planned time and backend evidence')
        if stage == 'scheduled' and schedule_saved is not True:
            errors.append(label + ': scheduled stage lacks saved native schedule')
        if stage == 'backend_published' and (not verified or not actual.get('backend_status') or not evidence):
            errors.append(label + ': backend_published requires backend evidence')
        url = actual.get('public_url')
        if url:
            public += 1
            if not isinstance(url, str) or not url.startswith('https://') or stage != 'backend_published':
                errors.append(label + ': public URL requires HTTPS and backend_published stage')
        if evidence_root is not None:
            root = Path(evidence_root).resolve()
            for path in evidence:
                resolved = (root / path).resolve()
                if Path(path).is_absolute() or not resolved.is_relative_to(root) or not resolved.is_file():
                    errors.append(label + ': missing or outside evidence ' + path)
    return {'ok': not errors, 'planned': len(plans), 'recorded': len(results),
            'native_schedule_saved': saved, 'public_url_count': public, 'errors': errors,
            'verification_limit': 'offline record consistency only; platform facts not independently verified'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', type=Path)
    parser.add_argument('result', type=Path)
    parser.add_argument('--evidence-root', type=Path)
    args = parser.parse_args()
    try:
        report = check(json.loads(args.plan.read_text(encoding='utf-8')),
                       json.loads(args.result.read_text(encoding='utf-8')), args.evidence_root)
    except (OSError, ValueError) as exc:
        report = {'ok': False, 'errors': [str(exc)]}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
