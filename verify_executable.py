"""Build-time verification of the actual EXE exit code and a fresh smoke report."""
import json
from pathlib import Path
import subprocess
import sys
from gclock import VERSION


def main():
    base = Path(__file__).resolve().parent
    report_path = base / '.build-temp' / 'executable-smoke.json'
    report_path.parent.mkdir(exist_ok=True)
    report_path.unlink(missing_ok=True)
    process = subprocess.Popen([str(base / 'dist' / 'GClock.exe'), '--smoke-test',
                                '--smoke-report', str(report_path)])
    try:
        code = process.wait(timeout=60)
    except subprocess.TimeoutExpired:
        # Terminate only this verifier's own process tree, never an open user app.
        subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        print('EXE smoke test timed out after 60 seconds.')
        return 1
    try:
        report = json.loads(report_path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        print(f'EXE smoke test failed: exit={code}; no valid fresh report.')
        return 1
    if code != 0 or report.get('ok') is not True or report.get('version') != VERSION:
        print(f'EXE smoke test failed: exit={code}')
        print(report.get('error', 'Unexpected smoke report.'))
        return 1
    print(f'EXE smoke test passed: v{VERSION}, exit=0, fresh report verified.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
