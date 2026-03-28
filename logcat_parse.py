#!/usr/bin/env python3
"""
logcat_parse.py -- Analyze saved Android logcat file
Usage: python3 logcat_parse.py logcat.txt [--json output.json]
"""
import sys, re, json, argparse
from collections import defaultdict
from datetime import datetime

CRASH = re.compile(r'(FATAL EXCEPTION|FATAL|Process.+?died)')
ANR = re.compile(r'(ANR|Application Not Responding)')
EXCEPTION = re.compile(r'at (.+?)\((.+?)\)')
OOM = re.compile(r'OutOfMemoryError')
NATIVE_CRASH = re.compile(r'signal \d+|Segmentation|SIGSEGV')

def parse_logcat(filename):
    issues = defaultdict(int)
    crashes = []
    current_crash = []
    current_app = None

    with open(filename) as f:
        for line in f:
            line = line.rstrip()

            # Extract package from tags
            pkg_m = re.search(r'(\S+)\s+\d+\s+\d+\s+[A-Z]\s+', line)
            if pkg_m:
                current_app = pkg_m.group(1)

            if CRASH.search(line):
                if current_crash:
                    crashes.append({'app': current_app, 'trace': current_crash})
                    current_crash = []
                current_crash.append(line)
                issues['crash'] += 1
            elif ANR.search(line):
                issues['anr'] += 1
                if current_app:
                    issues[f'anr_{current_app}'] += 1
            elif OOM.search(line):
                issues['oom'] += 1
            elif NATIVE_CRASH.search(line):
                issues['native_crash'] += 1
            elif current_crash:
                current_crash.append(line)
                if len(current_crash) > 100:
                    crashes.append({'app': current_app, 'trace': current_crash})
                    current_crash = []

    return dict(issues), crashes

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("logcat")
    parser.add_argument("--json", help="Export to JSON")
    args = parser.parse_args()

    print(f"\n📊 Logcat Parser")
    print("=" * 40)

    issues, crashes = parse_logcat(args.logcat)

    print(f"\nIssues found:")
    for issue, count in sorted(issues.items(), key=lambda x: -x[1])[:15]:
        print(f"  {issue:<25} {count}")

    if crashes:
        print(f"\nCrashes: {len(crashes)}")
        for i, c in enumerate(crashes[:3]):
            print(f"\n  Crash {i+1}: {c['app']}")
            for line in c['trace'][:5]:
                print(f"    {line[:80]}")

    if args.json:
        with open(args.json, 'w') as f:
            json.dump({'issues': issues, 'crashes_count': len(crashes)}, f, indent=2)
        print(f"\n✅ Saved to {args.json}")

if __name__ == "__main__":
    main()
