#!/usr/bin/env python3
"""
crash_summary.py -- Parse a saved logcat file and summarize all crashes/errors
Usage: python3 crash_summary.py logcat.txt
       adb logcat -d > logcat.txt && python3 crash_summary.py logcat.txt
"""
import sys, re, collections

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 crash_summary.py <logcat_file>")
        print("  Get logcat: adb logcat -d > logcat.txt")
        sys.exit(1)

    with open(sys.argv[1], errors='ignore') as f:
        lines = f.readlines()

    crashes = []
    errors = collections.Counter()
    warnings = collections.Counter()
    current_crash = None

    for line in lines:
        # Crashes
        if "FATAL EXCEPTION" in line or "AndroidRuntime" in line:
            pkg_m = re.search(r'Process: (\S+)', line)
            current_crash = {'pkg': pkg_m.group(1) if pkg_m else 'unknown', 'trace': [line]}
        elif current_crash and ("at " in line or "Caused by" in line or "Exception" in line):
            current_crash['trace'].append(line.strip())
            if len(current_crash['trace']) > 15:
                crashes.append(current_crash)
                current_crash = None
        elif current_crash and line.strip() == '':
            if current_crash['trace']:
                crashes.append(current_crash)
            current_crash = None

        # Error/Warning counts by tag
        e = re.match(r'.+\s+E\s+(\S+)\s*:', line)
        if e: errors[e.group(1)] += 1
        w = re.match(r'.+\s+W\s+(\S+)\s*:', line)
        if w: warnings[w.group(1)] += 1

    print(f"\n📊 Logcat Summary — {sys.argv[1]}")
    print(f"   Total lines: {len(lines)}")
    print(f"   Crashes:     {len(crashes)}")
    print(f"   Error tags:  {len(errors)}")

    if crashes:
        print(f"\n{'─'*55}")
        print("💥 CRASHES:")
        for i, c in enumerate(crashes[:10]):
            print(f"\n  [{i+1}] {c['pkg']}")
            for t in c['trace'][:5]:
                print(f"      {t[:100]}")

    if errors:
        print(f"\n{'─'*55}")
        print("🔴 Top Error tags:")
        for tag, count in errors.most_common(10):
            print(f"  {count:>5}x  {tag}")

    if warnings:
        print(f"\n{'─'*55}")
        print("⚠️  Top Warning tags:")
        for tag, count in warnings.most_common(10):
            print(f"  {count:>5}x  {tag}")

if __name__ == "__main__":
    main()
