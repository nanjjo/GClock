# GClock v2.0

Windows x64용 60분 시각 타이머입니다. **GPT-6.1 Sol을 활용해 제작**했으며 Python/Tkinter, Pillow와 miniaudio를 사용합니다.

## 실행

[GitHub Releases](https://github.com/nanjjo/GClock/releases)에서 GClock.exe를 내려받아 실행하세요. Python 설치가 필요 없습니다. MP3 파일은 별도로 준비합니다. 소스에서 빌드하면 `dist/GClock.exe`가 생성됩니다.

설정은 **EXE와 같은 폴더의 settings.json**에 자동 저장합니다. 다른 PC로 옮길 때 EXE와 JSON을 함께 복사하면 설정을 유지할 수 있습니다. 실행 폴더에 쓰기 권한이 필요합니다.

## 기능

- 0~60분 타이머: 다이얼 클릭·드래그·휠, 세로 시간 바, 10/30/50분 프리셋.
- 시작·일시정지·재개·초기화. 다이얼 또는 창에 포커스가 있으면 Space/Escape 단축키.
- 창 크기에 맞춰 다이얼과 시간 바 크기 조절. DPI 대응 및 Pillow 고해상도 렌더링.
- 항상 위, 색상 선택, MP3 종료 알림, 미리 듣기, 재생 중지, 무음.
- 작은 녹색 채움 볼륨 바: 클릭·드래그·휠·좌우 화살표로 조절.
- 시간·음악 경로·볼륨·무음·항상 위·색상·창 크기 및 위치 저장. 다음 실행은 준비 상태로 시작.

v2.0의 기본 창은 100% 배율 기준512×704입니다. 바깥 좌우 여백6px, 아래4px, 위0px로 줄였습니다. MP3 입력칸은 찾기 버튼과 같은 높이이고 무음·볼륨은 오른쪽에 정렬합니다. 이전 설정 파일은 한 번 창 크기를 보정한 뒤 계속 복원합니다.

미리 듣기는 무음과 무관하게 수동 재생합니다. 시간을 바꾸면 진행 중인 타이머가 재설정됩니다. MP3 선택과 볼륨 변경은 타이머 시간을 바꾸지 않습니다. 음악 상대 경로는 설정 JSON이 있는 폴더 기준입니다.

## 빌드

빌드 PC에 Tkinter를 포함한 Python 3.12 x64가 필요합니다. 최초 의존성 다운로드에는 인터넷 연결이 필요합니다.

```powershell
.\build.bat
```

배치는 프로젝트 내부 가상환경 생성, 고정 버전 의존성 설치, 테스트18개, PyInstaller 단일 EXE 빌드, 패키징된 EXE smoke test를 수행합니다. 실패하면0이 아닌 코드로 종료합니다. EXE는 Python 런타임·Tcl/Tk·네이티브 오디오 및 이미지 라이브러리를 포함합니다. Python이 없는 별도 PC/VM 검증은 수행하지 않았습니다.

소스 실행은 의존성 설치 후 `run.cmd`를 사용하세요.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -v
```

## 제작 및 MP3 플레이어 출처

- AI 개발 도구: **GPT-6.1 Sol**. 사용자 요구사항에 맞춰 GClock의 UI, 타이머, 설정 및 배포 코드를 제작했습니다.
- Python 오디오 바인딩: [Irmen de Jong의 pyminiaudio](https://github.com/irmen/pyminiaudio), 버전1.71, MIT 라이선스. AudioPlayer는 이 라이브러리를 사용합니다.
- 네이티브 오디오 엔진: [David Reid의 miniaudio](https://github.com/mackron/miniaudio), pyminiaudio에 포함된 엔진. 원본은 public domain 또는 MIT-0 중 선택하는 라이선스입니다.
- 재생 방식: MP3를 메모리에서 디코드하고 signed16 PCM에 볼륨을 적용합니다. 50ms 출력 period 두 개로 약0.1초의 버퍼를 목표로 합니다. 실제 청취 지연은 Windows 및 오디오 장치에 따라 달라집니다.
- 의존성 라이선스 전문은 [THIRD_PARTY_NOTICES.txt](THIRD_PARTY_NOTICES.txt)를 확인하세요.

## 제한 및 문서

M4A와 Android는 지원하지 않습니다. PC 절전 중에는 알림이 울리지 않습니다. System DPI 방식이며 배율이 다른 모니터 사이의 실시간 재배율은 지원하지 않습니다. 음악 파일 전체를 메모리에 읽으므로 큰 파일은 시작 지연과 메모리 사용에 영향을 줍니다. 기본 Windows 알림음의 볼륨은 운영체제에서 조절합니다.

- [HANDOFF.md](HANDOFF.md): 구현 상태, 검증과 작업 재개 방법.
- [SPEC.md](SPEC.md): 다른 AI가 빈 프로젝트에서 같은 앱을 재현하는 제작법.
- [ABOUT.md](ABOUT.md): 제작 및 배포 안내.

개인 설정 JSON, 사용자의 음악 파일, 가상환경과 빌드 임시 파일은 저장소에 포함하지 않습니다.
