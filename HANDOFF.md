# GClock v2.2 — 인수인계

최종 정리: 2026-10-17, Asia/Seoul. Windows x64용 Python/Tkinter 시각 타이머다. GPT-6.1 Sol 활용 제작. HTTP 서버와 Android 앱은 범위에 없다.

## 현재 결과

- 0~60분 타이머, 기본25분. 다이얼 클릭·드래그·휠·세로 시간 바,10/30/50분 프리셋.
- 시작·일시정지·재개·초기화, 항상 위, 세 가지 색상, 한국어/English 전환과 저장.
- MP3 경로·무음·볼륨·미리 듣기·재생 중지는 **소리 설정** 창에 둔다. 기본 숨김이며 같은 비모달 창을 재사용한다. 설정 중에도 타이머가 진행되고 닫기/X/Escape는 음악을 정지하고 창을 숨긴다.
- 시간이 끝나면 파동3개가 중심에서 반복해서 퍼진다. 무음이나 MP3 실패에도 실행된다. 확인/시계 클릭은 알림을 멈추고 준비 상태로 복귀하며, 다시 시작은 기존 시간으로 즉시 실행한다. 새 프리셋도 알림을 정지한다.
- 기본 창512×560, 최소440×500 논리 픽셀. 설정 창640×200, 최소540×200. 여백 좌우6·위0·아래4이며 DPI에 맞춰 확대한다. MP3 글꼴은 기본 입력 글꼴의2배, 찾기 버튼과 같은 높이, 무음/볼륨은 오른쪽 정렬이다.
- 설정은 EXE 옆 settings.json 하나다. 소스 실행은 모듈 옆 파일이며 CWD에 의존하지 않는다. 재실행에는 선택 시간의 준비 상태를 복원한다.

## 파일과 실행

| 파일 | 역할 |
|---|---|
| gclock.py | TimerState, UI, 설정 창, 종료 파동, 번역 적용, EXE 검사 진입점 |
| translations.py | 한국어/영어 문구 |
| audio_player.py | 메모리 MP3 디코드, PCM 볼륨, 장치/스트림 정리 |
| volume_control.py | 색 채움 볼륨 바 |
| dial_renderer.py | Pillow2배 렌더링과 레이어 캐시 |
| display_support.py / windows.manifest | System DPI 대응 |
| settings_store.py | JSON 검증과 원자적 저장 |
| build.bat / run.cmd | 단일 EXE 빌드 / 소스 실행 |
| verify_executable.py | 실제 EXE 종료 코드·새 검사 보고서 확인 |
| test_*.py | 회귀 테스트25개, 5개 모듈 |
| SPEC.md | 빈 프로젝트에서 재현하는 독립 제작 사양 |
| README / ABOUT / RELEASE_NOTES | 실행·출처·릴리스 안내 |
| THIRD_PARTY_NOTICES.txt | 의존성 라이선스 전문 |

```powershell
.\build.bat
.\run.cmd
.\.venv\Scripts\python.exe -m unittest discover -v
.\.venv\Scripts\python.exe verify_executable.py
```

빌드 PC에는 Tkinter 포함 Python3.12 x64와 최초 의존성 다운로드를 위한 인터넷이 필요하다. 실행 PC는 Python 설치 없이 dist/GClock.exe로 실행한다. Python·Tcl/Tk·Pillow·네이티브 오디오를 포함한다. 빌드 전 실행 중인 기존 EXE를 종료해야 교체할 수 있다.

## 검증과 한계

최종 소스에서 build.bat 성공, 테스트25개 통과, 패키징 EXE 검사 종료 코드0 및 새 보고서의 ok=true, version=2.2를 확인했다. 이후 변경은 문서와 배포 포장뿐이므로 같은 빌드를 사용한다. 로컬 보고서는 Git에서 제외한 .build-temp/executable-smoke.json이다.

타이머·부분 휠/포커스·MP3 디코더/버퍼/볼륨·파일 선택 시 시간 유지·Unicode JSON/손상 복구/작업 폴더 독립·언어 전환/재실행 저장을 검증했다. 설정 창 기본 숨김/재사용/비모달, 무음 종료 파동의 변화/개수 제한/크기 변경/확인/재시작/프리셋/종료 정리, layout4→5 일회성 창 축소를 확인했다. 96/144/192 DPI 주입과300/600/1200px 렌더링 테스트, 앱 영역 캡처로 배치를 검증했다.

Python 없는 별도 PC/VM, 실제 사용자4K 모니터와 혼합 DPI 이동 검증은 수행하지 않았다. System DPI 방식으로 모니터 간 실시간 재배율은 지원하지 않는다. M4A·Android·자동 반복·진행 중 타이머 종료 후 이어하기·설치 프로그램·코드 서명은 없다. 절전 중 알림은 울리지 않는다. MP3 전체를 메모리에 읽으므로 큰 파일은 시작 지연/메모리에 영향을 준다. OS 파일 선택창 버튼과 기본 알림음 볼륨은 운영체제를 따른다. 미해결 필수 구현 작업은 없다.

## 게시

대상은 사용자 승인된 공개 저장소 https://github.com/nanjjo/GClock 이다. 기존 v2.0/v2.1은 유지한다.

v2.2 게시 상태: 업로드 확인 중.

릴리스: https://github.com/nanjjo/GClock/releases/tag/v2.2

자산은 GClock.exe, GClock-v2.2-Windows-x64.zip, SHA256SUMS-v2.2.txt, ABOUT.md, THIRD_PARTY_NOTICES.txt다. ZIP에는 EXE·README·ABOUT·SPEC·라이선스만 넣는다. 최신 게시 결과를 기록하는 HANDOFF는 저장소 루트에서 제공한다. 설정·음악·로그·토큰·가상환경·개인 스킬은 Git/ZIP에서 제외한다.

## 후속 작업에서 유지할 조건

1. 제품 VERSION=2.2와 manifest2.2.0.0, 문서/릴리스 버전을 맞춘다. layout_version=5는 창 크기 마이그레이션용이다. layout<5에만 높이를144 줄이고 최소500을 적용한다.
2. 시간은 monotonic deadline으로 계산한다. 언어·볼륨·음악 설정은 deadline을 바꾸지 않는다. 슬라이더 비동기 콜백은 기존 selected와 같으면 무시한다.
3. 파동은 after(33)에서 Canvas oval만 재사용한다. 매 프레임 Pillow 이미지를 다시 만들지 않는다. 종료·확인·새 시간 선택 시 animation ID를 취소하고 파동 태그를 삭제한다.
4. 소리 설정은 같은 Toplevel을 withdraw/deiconify하고 공유 변수/trace를 중복 생성하지 않는다. 입력 grab을 사용하지 않는다.
5. miniaudio1.71에는 set_master_volume이 없다. signed16 PCM에 gain을 적용한다. wrapper만 next로 초기화하고 이미 초기화된 source는 다시 초기화하지 않는다. 출력50ms×2와 디코더 frames_to_read=32768을 유지한다.
6. 창 매핑은 비동기다. EXE 검사는 Entry 표시를 최대2초 기다리고 finally에서 창/오디오/예약 콜백을 정리한다. 검사 예외는 JSON traceback과 종료 코드1로 전달한다. verify_executable.py는 기존 보고서를 지우고 새 보고서·버전·실제 종료 코드를 확인하며60초 초과에는 자신이 실행한 프로세스 트리만 정리한다. 사용자 실행에는 검사 인수를 붙이지 않는다.
7. 저장 창 크기는 DPI 독립값, 위치는 물리 좌표다. tick/save/layout/animation 예약을 종료 시 취소하고 볼륨 trace도 해제한다.
8. GitHub에는 기존 origin과 인증을 사용한다. force push/기존 릴리스 덮어쓰기를 하지 않는다. CLI와 인증 설정은 Git 제외 .tools/github-cli 아래에 있다. 토큰을 문서에 기록하지 않는다.

## 제작 및 오디오 출처

GPT-6.1 Sol 활용 제작. [pyminiaudio1.71](https://github.com/irmen/pyminiaudio)은 MIT, 포함된 [miniaudio](https://github.com/mackron/miniaudio)는 public domain 또는 MIT-0이다. 배포에 의존성 라이선스 전문을 포함한다. 개인 project-finish-docs 스킬에 따라 마무리는 문서와 승인된 GitHub 게시를 포함한다.
