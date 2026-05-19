#!/usr/bin/env python3
"""
logcat_stream.py — Real-time logcat stream parser and filter
Merged from android-logcat-parser
"""
import subprocess, sys, re, argparse
from datetime import datetime

LEVELS = {'V': 0, 'D': 1, 'I': 2, 'W': 3, 'E': 4, 'F': 5}
COLORS = {
    'V': '[37m', 'D': '[36m', 'I': '[32m',
    'W': '[33m', 'E': '[31m', 'F': '[35m', 'RESET': '[0m'
}

LINE_RE = re.compile(
    r'(?P<date>\d{2}-\d{2})\s+(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\s+'
    r'(?P<pid>\d+)\s+(?P<tid>\d+)\s+(?P<level>[VDIWEF])\s+'
    r'(?P<tag>[^:]+):\s+(?P<msg>.*)'
)

def parse_line(line):
    m = LINE_RE.match(line)
    return m.groupdict() if m else None

def colorize(entry):
    c = COLORS.get(entry['level'], '')
    r = COLORS['RESET']
    return f"{c}{entry['time']} {entry['level']}/{entry['tag']}: {entry['msg']}{r}"

def stream(min_level='V', tag_filter=None, pkg_filter=None, output_file=None):
    cmd = ['adb', 'logcat', '-v', 'threadtime']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    
    out = open(output_file, 'w') if output_file else None
    min_lvl = LEVELS.get(min_level.upper(), 0)
    
    try:
        for line in proc.stdout:
            entry = parse_line(line.strip())
            if not entry: continue
            if LEVELS.get(entry['level'], 0) < min_lvl: continue
            if tag_filter and tag_filter.lower() not in entry['tag'].lower(): continue
            
            formatted = colorize(entry)
            print(formatted)
            if out:
                out.write(line)
    except KeyboardInterrupt:
        proc.terminate()
        if out: out.close()
        print(f"\nStream stopped.")

def dump_to_json(output='logcat_dump.json'):
    result = subprocess.run(['adb', 'logcat', '-d', '-v', 'threadtime'],
                            capture_output=True, text=True)
    entries = []
    for line in result.stdout.splitlines():
        entry = parse_line(line)
        if entry: entries.append(entry)
    with open(output, 'w') as f:
        json_str = json.dumps(entries, indent=2)
        f.write(json_str)
    print(f"Dumped {len(entries)} log entries to {output}")

if __name__ == '__main__':
    import json
    parser = argparse.ArgumentParser(description='Real-time logcat stream parser')
    parser.add_argument('--level', default='V', help='Minimum log level (V/D/I/W/E/F)')
    parser.add_argument('--tag', help='Filter by tag substring')
    parser.add_argument('--dump', action='store_true', help='Dump full log to JSON and exit')
    parser.add_argument('--out', help='Also write to file')
    args = parser.parse_args()
    
    if args.dump:
        dump_to_json()
    else:
        stream(min_level=args.level, tag_filter=args.tag, output_file=args.out)
