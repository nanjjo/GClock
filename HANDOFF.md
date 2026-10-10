# GClock v2.1 — 인수인계

최종 정리: 2026-10-10, Asia/Seoul. GPT-6.1 Sol을 활용해 제작한 Windows x64 시각 타이머다. 사용자가 말한 API는 이 프로젝트에서 데스크톱 앱을 의미하며 HTTP 서버와 Android 앱은 없다.

## 현재 결과

- 타이머0~60분, 기본25분, 클릭·드래그·휠·세로 바 및10/30/50분 프리셋.
- 시작·일시정지·재개·초기화, 항상 위·색상 선택, 고해상도 렌더링.
- MP3 종료 알림·미리 듣기·재생 중지·무음·색 채움 볼륨 바.
- 항상 위 왼쪽에 한국어/English 콤보. 기본한국어, 즉시 전환 및 저장. 타이머와 오디오는 전환 중 유지.
- MP3 경로 입력 글꼴은 기존 Tk 기본 글꼴의2배. 입력칸과 찾기 버튼 높이가 같다.
- 기본512×704, 최소440×650 논리 픽셀. 외부 패딩 좌우6·위0·아래4. 좌우 끝선 정렬 및 무음/볼륨 오른쪽 정렬.
- 설정은 EXE 옆 settings.json 하나, 소스 실행은 모듈 옆 파일. 작업 폴더와 LocalAppData에 의존하지 않는다.

## 파일과 실행

| 파일 | 역할 |
|---|---|
| gclock.py | TimerState, Tk UI, VERSION, 입력·번역·알림·EXE smoke 모드 |
| translations.py | 한국어/영어 앱 문구 |
| audio_player.py | 메모리 MP3 디코드·PCM gain·오디오 장치 자원 관리 |
| volume_control.py | 숫자 없는 색 채움 볼륨 컨트롤 |
| dial_renderer.py | Pillow2배 렌더링, 레이어 캐시, LANCZOS 축소 |
| display_support.py / windows.manifest | System DPI awareness |
| settings_store.py | 검증된 JSON 로드와 원자적 저장 |
| build.bat / run.cmd | Windows 독립 실행 파일 빌드 / 소스 실행 |
| test_*.py | 타이머·오디오·배치·언어·설정 회귀 테스트20개 |
| README / ABOUT / RELEASE_NOTES | 사용·제작 출처·현재 릴리스 설명 |
| SPEC.md | 빈 프로젝트에서 제작하는 독립 사양 |
| THIRD_PARTY_NOTICES.txt | 배포에 포함하는 의존성 라이선스 전문 |

```powershell
.\build.bat
.\run.cmd
.\.venv\Scripts\python.exe -m unittest discover -v
```

빌드 PC에는 Tkinter가 포함된 Python3.12 x64와 최초 의존성 다운로드를 위한 인터넷이 필요하다. 실행 PC에는 Python을 요구하지 않는다. dist/GClock.exe가 Python·Tcl/Tk·Pillow·miniaudio 네이티브 의존성을 포함한다. 배치는 실패 시 nonzero 종료한다. 개인 설정·음악은 배포 ZIP과 Git에 포함하지 않는다.

## 검증 및 게시

검증 상태: v2.1 build.bat 성공. 테스트20개 및 패키징된 EXE smoke test 정상 종료.

언어 추가본은 테스트20개 및 패키징 EXE smoke를 통과했다. 최종 v2.1은 버전/매니페스트를 갱신했고 같은 검증도 배치에서 통과했다. 테스트는96/144/192 DPI 주입,300/600/1200px 이미지, 창 확대/축소, 버퍼/PCM gain, 파일 선택 시 타이머 유지, 다른 컨트롤 휠 무시, 영어 오류·완료·전환 및 재시작 언어 저장을 포함한다. 실제 MP3 재생에서50ms 요청2205프레임과 다음 콜백 gain 반영16ms를 관측한 근거가 있다. 이는 물리적 청취 지연 측정은 아니다.

게시 대상: https://github.com/nanjjo/GClock (공개, 사용자 승인).
릴리스 대상: https://github.com/nanjjo/GClock/releases/tag/v2.1
게시 상태: 2026-10-10(Asia/Seoul), 공개 main 소스 및 v2.1 정식 릴리스 게시 완료. EXE/ZIP/SHA256SUMS/ABOUT/의존성 라이선스 자산이 uploaded 상태이고, EXE와 ZIP의 서버 SHA256이 로컬 파일과 일치함을 확인했다.

v2.0은 이전 게시본이다. 최종 언어 기능은v2.1에 제공한다. 릴리스 자산은 EXE, Windows x64 ZIP, SHA256SUMS, ABOUT, 의존성 라이선스다. ZIP에는 README/SPEC도 넣는다. 최신 게시 결과를 기록하는 HANDOFF는 저장소 루트에서 제공한다. GitHub CLI는 로컬 .tools/github-cli/runtime/bin/gh.exe, 설정은 GH_CONFIG_DIR=.tools/github-cli/config이다. 둘 다 Git에서 제외한다. 로그인은 사용자 계정nanjjo로 완료했으며 토큰은 Windows keyring을 이용한다. 후속 게시 전 인증 상태를 다시 확인한다.

## 이어서 작업할 때 유지할 조건

1. 버전은gclock.VERSION, 매니페스트, README/ABOUT/릴리스 및 ZIP 이름을 함께 갱신한다. layout_version=4는 UI 창 크기 마이그레이션용이며 제품 버전과 다르다.
2. miniaudio1.71에는set_master_volume이 없다. signed16 샘플에 gain을 적용한다. wrapper만next로 초기화하고 원본 stream_memory는 다시 초기화하지 않는다.
3. 출력50ms period2개와 디코더 frames_to_read=32768을 구분한다. 예전500ms/16384 조합은 CFFI 저장 공간 오류를 일으켰다. 새 출력 버퍼가 작아도 디코더 용량을 불필요하게 줄이지 않는다.
4. 슬라이더 비동기 콜백은selected와 같은 값이면 무시한다. 파일 찾기는 Entry로 포커스를 옮기고 경로만 변경한다. 휠은 Canvas 포커스와 이벤트 대상이 모두 Canvas일 때만 시간을 바꾼다.
5. 언어 변경은status_key/detail과 문구만 다시 표시한다. selected/remaining/deadline/오디오는 건드리지 않는다. tick/save/언어 레이아웃 after ID를 종료 시 취소하고 볼륨 변수 trace도 해제한다.
6. settings.json 검증을 유지한다. 정상 창 크기는 DPI 독립값, 위치는 물리 좌표로 저장한다. 앱 종료는실행 중 타이머의 잔여량을 복원하지 않는다.
7. 이전 Flutter 파일·.tools/flutter·개인 스킬 사본은 로컬 참고용이다. 현재 Python 빌드/공개 저장소에 포함하지 않는다.

## 한계

Python이 없는 별도 PC/VM, 실제 사용자의4K 모니터 또는 혼합 DPI 이동 검증은 수행하지 않았다. System DPI 모드로 모니터 사이 실시간 DPI 변경은 지원하지 않는다. M4A·Android·자동 반복·진행 중 타이머의 종료 후 이어하기·설치 프로그램·코드 서명은 없다. 절전 중 알림은 울리지 않는다. 음악 전체를 메모리에 읽으므로 큰 파일은 시작 지연/메모리에 영향을 준다. OS 파일 대화상자 버튼은 OS 언어, 기본 Windows 알림음은 시스템 볼륨을 따른다.

## 제작/오디오 출처 및 개인 스킬

GPT-6.1 Sol 활용 제작. pyminiaudio1.71 https://github.com/irmen/pyminiaudio (MIT), 포함된 네이티브 miniaudio https://github.com/mackron/miniaudio (public domain 또는 MIT-0). 라이선스 전문은 THIRD_PARTY_NOTICES.txt에 보존한다.

사용자 요청에 따라 개인 project-finish-docs 스킬에 GitHub 등록·업데이트·릴리스 게시를 포함했다. 설치 위치는사용자 ~/.codex/skills/project-finish-docs/SKILL.md다. 기존 원격/공개 여부를 재사용하고 미지정 공개 여부나 계정 인증만 필요한 경우 확인한다. 이 프로젝트의 공개 게시 승인을 다른 프로젝트의 공개 승인으로 확장하지 않는다.

개인 마무리 스킬은 설치본 및 로컬 사본 모두 quick_validate에서 유효 판정을 받았다. 검증 도구의 PyYAML은 Git 제외 .tools/skill-validator에만 설치했다. 앱 실행 의존성에는 추가하지 않았다.

이번 마무리 요청의 필수 작업은 완료했다. 개인 스킬 업데이트, 현재 사양/인수인계 정리, 최종20개 테스트 및 EXE 검증, 공개 GitHub 소스와 v2.1 배포 게시를 수행했다. 클린PC·혼합DPI·M4A 등 앞서 명시한 확장은 별도 요청 범위다.
