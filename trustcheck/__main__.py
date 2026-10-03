"""Command line entry point. Inputs and output remain local."""
import argparse
import json
import sys
from pathlib import Path
from .core import run_suite


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result


def read_json(path):
    if path.stat().st_size > 1024 * 1024:
        raise ValueError('Input exceeds 1 MiB limit')
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_object)


def safe(value):
    return ''.join(c if c.isprintable() else ' ' for c in str(value)).replace('|', '\\|').replace('<', '&lt;').replace('>', '&gt;')


def main(argv=None):
    parser = argparse.ArgumentParser(description='Offline GitHub OIDC trust-policy scenario checker (limited subset; not AWS authorization proof).')
    parser.add_argument('--policy', type=Path, required=True)
    parser.add_argument('--scenarios', type=Path, required=True)
    parser.add_argument('--format', choices=['text', 'json', 'markdown'], default='text')
    args = parser.parse_args(argv)
    try:
        results = run_suite(read_json(args.policy), read_json(args.scenarios))
    except (OSError, ValueError, RecursionError) as exc:
        print('Input error: ' + safe(exc), file=sys.stderr)
        return 2
    disclaimer = 'Model results only: no token verification, AWS call, repository protection check or effective-access guarantee.'
    if args.format == 'json':
        print(json.dumps({'schema_version': 1, 'scope': disclaimer, 'results': results}, indent=2))
    else:
        print(disclaimer)
        if args.format == 'markdown':
            print('\n| Scenario | Expected | Model decision | Status | Reason |\n|---|---|---|---|---|')
            for r in results:
                print('| ' + ' | '.join(safe(r[k]) for k in ['name', 'expected', 'decision', 'status', 'reason']) + ' |')
        else:
            for r in results:
                print(f"{r['status']:7} {safe(r['name'])}: expected={r['expected']} model={r['decision']} — {safe(r['reason'])}")
    return 2 if any(r['status'] == 'UNKNOWN' for r in results) else 1 if any(r['status'] == 'FAIL' for r in results) else 0


if __name__ == '__main__':
    sys.exit(main())
