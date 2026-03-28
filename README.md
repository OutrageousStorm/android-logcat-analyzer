# 📊 Android Logcat Analyzer

Parse logcat in real-time or from files — extract crashes, ANRs, memory leaks, and generate reports.

## Tools

```bash
python3 logcat_live.py              # Stream + analyze live logcat
python3 logcat_parse.py logcat.txt  # Analyze saved logcat file
python3 crash_detector.py           # Watch for crashes with alerts
```

## Features
- Real-time crash detection
- ANR (Application Not Responding) tracking
- Memory leak detection (low memory warnings)
- Per-app error summaries
- Export to JSON/CSV
- Custom filter rules
