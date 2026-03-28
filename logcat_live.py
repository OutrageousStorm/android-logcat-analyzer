#!/usr/bin/env python3
"""
logcat_live.py -- Real-time Android logcat analyzer
Streams logcat and highlights crashes, ANRs, errors, and warnings.
Usage: python3 logcat_live.py [--filter app.package] [--save logcat.txt]
"""
import subprocess, sys, re, time
from datetime import datetime

CRASH_PATTERN = re.compile(r'FATAL EXCEPTION|AndroidRuntime.*?FATAL|Process.*?died')
ANR_PATTERN = re.compile(r'ANR|Application Not Responding|skipped \d+ frames')
WARN_PATTERN = re.compile(r'WARNING|OutOfMemoryError|WARN')
ERROR_PATTERN = re.compile(r'\bERROR\b|Exception|FileNotFoundException|SecurityException')

def colorize(text, color):
    colors = {
        'red': '\033[91m', 'yellow': '\033[93m', 'green': '\033[92m',
        'cyan': '\033[96m', 'dim': '\033[2m', 'reset': '\033[0m'
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--filter", help="Filter by package")
    parser.add_argument("--save", help="Save logcat to file")
    args = parser.parse_args()

    print(colorize("\n📊 Logcat Live Analyzer", "cyan"))
    print("Press Ctrl+C to stop\n")

    cmd = "adb logcat -v threadtime"
    if args.filter:
        cmd += f" | grep -i {args.filter}"

    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    crash_count = 0; anr_count = 0; error_count = 0
    logfile = open(args.save, 'w') if args.save else None

    try:
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            
            line = line.rstrip()
            if logfile:
                logfile.write(line + '\n')

            if CRASH_PATTERN.search(line):
                print(colorize(f"[CRASH] {line}", "red"))
                crash_count += 1
            elif ANR_PATTERN.search(line):
                print(colorize(f"[ANR] {line}", "yellow"))
                anr_count += 1
            elif ERROR_PATTERN.search(line):
                print(colorize(f"[ERROR] {line}", "red"))
                error_count += 1
            elif WARN_PATTERN.search(line):
                print(colorize(f"[WARN] {line}", "yellow"))
            elif any(x in line for x in ['D/', 'I/', 'V/']):
                if args.filter or len(sys.argv) > 1:
                    print(colorize(line, "dim"))

    except KeyboardInterrupt:
        pass
    finally:
        proc.terminate()
        if logfile:
            logfile.close()
        print(f"\n{colorize(f'Crashes: {crash_count}  ANRs: {anr_count}  Errors: {error_count}', 'cyan')}")

if __name__ == "__main__":
    main()
