# GClock v2.0 — Handoff

작성일: 2026-10-09 (Asia/Seoul)

최종 수정일: 2026-10-10. 고해상도 개선을 추가했다. `display_support.py`와 `windows.manifest`가 System DPI awareness를 설정하고, `dial_renderer.py`가 Pillow 12.3.0으로 다이얼을 현재 물리 픽셀 크기의 2배로 그린 후 LANCZOS로 축소한다. 캐시한 배경/눈금 레이어를 사용한다. 글꼴 tk scaling=dpi/72, 창 크기·슬라이더 폭은 dpi/96으로 배율 적용. 제목의 버전 표기는 사용자 요청대로 v2.0을 유지한다. 100/150/200%를 주입한 UI 검증과 300/600/1200px 렌더링 검증을 추가해 테스트는 총 10개다. 실제 사용자 4K 모니터에서 육안 검증은 수행하지 않았다. System DPI 방식이므로 서로 다른 DPI 모니터로 이동할 때 실시간 재배율은 지원하지 않는다.

## 현재 결과

추가 UI/오디오 변경: MP3 안내 줄을 간결하게 줄이고 무음 오른쪽에 0~100% 볼륨을 배치했다. SettingsStore에 `volume_percent` 정수 필드를 추가(기본100). 미리 듣기 오류를 일으킨 미지원 set_master_volume 호출을 제거했다. AudioPlayer는 signed16 PCM 스트림의 각 샘플에 최신 volume을 곱한다. 기본 시스템 알림음은 Windows 볼륨을 따른다. 시계 아래 MM:SS 라벨은 다이얼 영역 내부의 별도 위젯으로 배치해 같은 gap을 유지한다. 위 상태 문구의 아래 패딩은 글꼴 linespace, 시계의 y 중심은 radius로 설정해 불필요한 상단 빈 공간을 제거했다.

2026-10-10 추가: `settings_store.py`가 EXE와 같은 폴더의 settings.json에 선택 초 수, MP3 경로, 무음·항상 위·색상, 정상 창 크기/위치와 최대화 여부를 JSON으로 저장한다. 크기는 DPI 독립값, 위치는 물리 좌표다. 500ms debounce와 종료 시 저장, 임시 파일+os.replace 원자적 갱신, 필드 검증/손상 시 기본값을 적용한다. 테스트·EXE smoke 모드는 settings_path=False 또는 프로젝트 임시 파일을 사용해 실제 사용자 설정을 변경하지 않는다. 타이머 잔여량·실행 여부와 음악 재생 상태는 복원하지 않는다. 테스트는 총 18개다.

Windows x64용 Python/Tkinter 시각 타이머 개발을 완료했다. 최종 실행 파일은 `dist/GClock.exe`이며 Python 런타임, Tcl/Tk, miniaudio 및 관련 라이브러리를 포함한다. 사용자 PC에는 Python이 필요 없다. 이 프로젝트에서 사용자가 말하는 API는 데스크톱 앱을 의미하며 HTTP 서버는 없다.

## 최종 동작

- 제목: `GClock · 시각 타이머 · v2.0`. 기본 창 560×720, 최소 440×650.
- 0~60분 원형 눈금과 남은 시간에 비례해 줄어드는 색 부채꼴. 초기 시간 25분.
- 다이얼 클릭/드래그, 클릭 후 휠 1분 조절, 왼쪽 세로 슬라이더, 오른쪽 10/30/50분 프리셋.
- 슬라이더 두께 30px, 숫자 14pt. 다이얼과 같은 높이로 함께 크기 변경.
- 프리셋은 다이얼에서 버튼 너비의 1/5 간격. 시계 중심 기준 좌우 공간 대칭.
- 시작/일시정지/재개/초기화. Space: 시작/일시정지, Escape: 초기화.
- 상단 오른쪽 항상 위·색상 선택. 무음은 MP3 안내 문구 뒤.
- MP3 경로 입력/선택, 미리 듣기, 재생 중지. 종료 시 MP3 재생, 빈 경로나 재생 실패 시 기본 알림음.

## 파일 안내

| 파일 | 역할 |
|---|---|
| `gclock.py` | 타이머 상태, Tkinter UI, 입력 처리, 종료 알림, EXE smoke test |
| `audio_player.py` | miniaudio 기반 MP3 재생·중지 및 자원 해제 |
| `display_support.py`, `windows.manifest` | 소스·EXE의 Windows DPI 설정 |
| `dial_renderer.py`, `test_display.py` | 고해상도 렌더러, 해상도·배율 회귀 검증 |
| `requirements.txt` | 실행 의존성 고정 버전 |
| `requirements-build.txt` | 실행 의존성 + PyInstaller 빌드 의존성 |
| `build.bat` | 가상환경·의존성·테스트·EXE 빌드·실행 검증 |
| `run.cmd` | 소스 실행: 로컬 가상환경 우선 사용 |
| `test_gclock.py` | 타이머 계산 테스트 |
| `test_gclock_ui.py` | 크기 변경, 휠, MP3 종료·무음·실패 처리 테스트 |
| `test_audio_player.py` | 버퍼 크기 회귀 테스트, 잘못된 경로 처리 |
| `THIRD_PARTY_NOTICES.txt` | 배포에 포함하는 오픈소스 라이선스 |
| `SPEC.md` | 빈 프로젝트에서 재현하기 위한 제작 설명 |

## 재개 및 빌드

Windows의 Python 3.12 x64와 인터넷 연결이 있는 빌드 PC에서 프로젝트 폴더의 `build.bat`를 실행한다. 실패하면 0이 아닌 종료 코드로 중단한다. 성공하면 `dist/GClock.exe`를 배포한다. 기존 EXE가 실행 중이면 먼저 닫고 재빌드한다.

```powershell
.\build.bat
.\.venv\Scripts\python.exe -m unittest test_gclock.py test_gclock_ui.py test_audio_player.py
```

## 검증 근거

- 고해상도 개선 전 v2.0 배치 빌드와 테스트 8개 통과. 개선 후 배치 빌드에는 해상도·배율 테스트 2개를 추가하여 총 10개를 실행한다.
- 패키징된 EXE의 `--smoke-test` 성공: UI 생성, 시작/초기화, 네이티브 디코더 및 22,050프레임 요청 검증.
- 실제 MP3를 재생하며 창 크기를 반복 변경한 검증에서 264,600프레임 전달 확인.
- 사용자가 MP3가 잘 들린다고 확인했다. 이후 변경은 배치와 제목이었다.
- Python이 없는 별도 PC/VM에서의 검증은 수행하지 않았다. 이전 버전의 제한된 PATH 실행 검증과 최종 버전의 EXE smoke test를 구분한다.

## 유지해야 할 구현 주의점

오디오는 miniaudio 1.71로 교체했다. 출력 버퍼 500ms, 디코더 `frames_to_read=32768`를 함께 유지한다. 44,100Hz에서 500ms는 22,050프레임이므로 기존 16,384 저장 공간은 CFFI 콜백 오류를 일으켰다. 버퍼를 변경할 때 회귀 테스트도 변경한다.

Tkinter `after` ID를 보관하고 종료 시 취소한다. 슬라이더의 비동기 콜백은 이미 설정된 시간과 같은 값이면 무시해, 프로그래밍 방식의 슬라이더 동기화가 실행 중인 타이머를 다시 멈추지 않도록 한다.

## 범위와 남은 제한

- M4A 미지원. 타이머 진행 상태·음악 재생 상태는 복원하지 않으며 선택 시간과 사용자 설정은 저장한다.
- Android 미구현. 이전 Flutter 소스와 `.tools/flutter`는 참고용으로 남아 있으며 현재 빌드에는 쓰이지 않는다.
- PC 절전 중 알림은 울리지 않는다. 재개 후 타이머는 monotonic clock과 Windows 절전 동작의 영향을 받는다.
- 음악은 외부 파일로 별도 복사해야 한다. 앱은 MP3 원본 전체를 메모리에 읽으므로 대형 파일은 메모리·시작 지연에 영향을 준다.
- 사용자 화면 배율·창 비율에 따라 여백과 픽셀 값은 달라질 수 있다. 프리셋 오른쪽의 약 1/5 여백은 기본 창 크기에 맞춘 값이다.
- 코드 서명, 설치 프로그램, 자동 업데이트는 제공하지 않는다.

현재 요청에서 남은 필수 작업은 없다. 위 제한의 확장은 후속 요청으로 진행한다.

## 최신 검증 및 변경

miniaudio 1.71에 없는 장치 볼륨 함수 때문에 미리 듣기가 실패했다. PCM gain wrapper로 수정했으며 기존 500ms/32768프레임 버퍼를 유지했다. 실제 MP3 미리 듣기를 통해 220,500프레임 전달을 확인했다. 볼륨 Scale은 숫자14pt·두께30px로 표시한다. 다이얼 영역은 expand=False와 실제 콘텐츠 높이 계산으로 숫자 아래 빈 공간을 제거한다.

최신 build.bat 실행 성공: 테스트18개 통과, 단일 dist/GClock.exe 재빌드, 패키징된 EXE smoke test 정상 종료. dist/settings.json에 기본 설정을 제공하며 이후 빌드는 기존 JSON을 덮어쓰지 않는다. Python이 없는 별도 PC 검증은 수행하지 않았다.

설정은 EXE 옆 JSON만 사용하고 상대 MP3 경로도 그 폴더 기준이다. 이전 LocalAppData는 런타임에서 읽지 않는다. 파일 선택 시 Entry로 포커스를 옮기고 경로만 바꾼다. 휠은 포커스와 이벤트 대상이 모두 Canvas여야 한다. 단축키는 루트 또는 Canvas에서만 동작한다. 18개 테스트는 MP3 gain/실제 디코더·장치 API autospec, 파일 선택 중 타이머 유지, 다른 위젯 휠 무시, 작업 폴더 독립 설정 경로, compact 레이아웃을 포함한다.


## 최신 볼륨 디자인 및 시계 확대 (이전 볼륨 UI 설명보다 우선)

새 기본 창은560×720으로, 기존460px 폭에서 다이얼 지름이 약25% 커진다. 구버전 JSON에 창 크기가 있으면 layout_version<2일 때 width>=520, height>=720로 한 번 확대하고 layout_version=2를 저장한다. 그 후 사용자 창 크기는 그대로 복원한다. 다른 설정은 유지한다.

volume_control.py의 VolumeBar는110×15 논리 픽셀의 고정 크기 Canvas다. 이전 바의 가로·세로 크기를 약절반으로 줄였다. 숫자·볼륨 라벨 없이 회색 전체 바와 녹색 volume_percent/100 비율의 채움 사각형을 그린다. 클릭·드래그 위치를0~100으로 제한해 IntVar에 저장한다. 변수 trace로 즉시 그림과 오디오 gain 및500ms 설정 저장 예약을 갱신한다. 좌우 화살표/휠은5단위, Home/End는0/100이며 타이머 단축키와 분리한다. Destroy에서 trace를 해제한다. MP3 안내와 무음 체크박스 글꼴은 모두 맑은 고딕11pt, pack(side=left,anchor=center)로 바의 수직 중앙과 맞춘다. 볼륨 바는 expand하지 않는다.

miniaudio PlaybackDevice(buffersize_msec=50, callback_periods=2)로 바꾸어 약100ms의 출력 큐를 목표로 한다. frames_to_read=32768은 디코더 용량이며 그대로 유지한다. 50ms 요청2205프레임을 패키징 smoke test에서도 검증한다. 이전500ms 관련 내용은 과거 CFFI 오류 원인 설명이다. 최종 소리가 들리는 지연은 Windows·오디오 장치의 추가 버퍼에도 영향을 받으므로 물리적으로 정확한100ms라고 보장하지 않는다. 볼륨 gain은 다음 콜백부터 적용하며 장치를 다시 시작하지 않는다.

18개 회귀 테스트에서 색 채움 비율·텍스트 부재·그래픽 중앙 정렬·클릭 후 즉시 볼륨 적용·새 장치 버퍼 인자를 검증한다. 실제 MP3 재생도 확인한다.

최신 검증: 실제 MP3에서 최대 요청2205프레임(50ms), 볼륨 변경 다음 콜백 반영16ms를 관측했다. 이 값은 물리 출력의 청취 지연 측정이 아니다. build.bat의18개 테스트와 최신 패키징 EXE smoke test가 모두 성공했다. 기존 dist/settings.json은 빌드 과정에서 변경하지 않았다.


## 최신 좌우 정렬 보완

이 절의 배치를 이전 패딩 설명보다 우선한다. main의 논리 패딩은(left30,top0,right30,bottom20)이며 DPI 배율을 적용한다. 제목줄과 GClock 사이의 추가 상단 여백을 제거했다. GClock, MP3 안내, 경로 입력칸의 왼쪽 기준선을 통일하고, 마지막 색상 버튼·볼륨 바·찾기 버튼의 오른쪽 끝을 맞춘다. 마지막 색상 버튼의 오른쪽 pack padx는0이다. MP3 안내는 왼쪽, 볼륨 바는 side=right로 먼저 pack하고 무음 체크박스를 그 왼쪽에 side=right로 pack한다. 모두 수직 중앙에 맞춘다. 경로 Entry는 side=left, fill=both, expand=True로 pack해 찾기 버튼과 동일한 높이를 갖는다.

resize_dial의 가용 높이는 main높이에서20*dpiScale 및 다른 자식 높이/패딩을 뺀다. 새 기본 창은560×720으로 이전보다 좌우 여백이20px씩 증가해도 시계 지름을 유지한다. 기존 JSON은 layout_version<2일 때 이전 확대(최소520×720)를 적용하고, layout_version<3일 때 폭만40px 더해 한 번 보정한다. 이후 layout_version=3으로 저장하며 사용자 창 크기를 계속 복원한다. 설정과 음악 파일 경로는 그대로 유지한다.

기존 UI 테스트에서 입력/버튼 높이 일치, 헤더 상단 여백0, 좌우 끝선 일치도 확인한다.


## v2.0 최종 변경 (앞선 레이아웃 치수보다 우선)

GPT-6.1 Sol을 활용해 제작했다. MP3 출처: pyminiaudio1.71 https://github.com/irmen/pyminiaudio (MIT), 그 안의 네이티브 miniaudio https://github.com/mackron/miniaudio (public domain 또는 MIT-0). README와 ABOUT.md에 제작 도구 및 출처를 명시하고 배포할 때 THIRD_PARTY_NOTICES.txt를 제공한다.

제목은 GClock · 시각 타이머 · v2.0이다. 바깥 패딩을(left6,top0,right6,bottom4)*dpiScale로 바꾸어 이전 좌우30px·아래20px의1/5로 줄인다. 새 기본 창은512×704이며 시계 표시 크기는 유지한다. resize_dial은 main높이에서4*dpiScale와 다른 자식 요청높이/패딩을 뺀다. JSON layout_version은4로 저장한다. 이전 레이아웃1/2/3의 기존 보정을 순서대로 적용한 후 version<4에서는 width=max(440,width-48), height=max(650,height-16)으로 한 번 줄인다. 이후 창 크기와 설정은 계속 복원한다.

GitHub 공개 저장소에는 Python 소스, 고정 의존성, 배치, 테스트, 매니페스트, 라이선스, 제작/재현 문서만 등록한다. 개인 settings.json·음악·Flutter 과거 파일·personal-skills·.venv·.tools·빌드 캐시를 올리지 않는다. 실행 파일은 v2.0 릴리스 자산으로 제공한다. 공개 등록은 사용자가 명시적으로 승인했다.

v2.0 검증 완료: 테스트18개·배치 빌드·패키징 EXE smoke test 성공. README/ABOUT에 GPT-6.1 Sol 제작과 오디오 출처를 명시했다. 2026-10-10(Asia/Seoul), 사용자 nanjjo 계정 인증 후 공개 저장소 https://github.com/nanjjo/GClock 에 소스와 문서를 게시했다. 릴리스 https://github.com/nanjjo/GClock/releases/tag/v2.0 에 GClock.exe, Windows x64 배포 ZIP, SHA256SUMS.txt, ABOUT.md, THIRD_PARTY_NOTICES.txt를 업로드했다. 공개/PUBLISHED 상태 및 업로드 EXE의 SHA256이 로컬 빌드와 일치함을 확인했다. 로컬 .build-temp/release에도 ZIP/체크섬이 있다. 프로젝트 내부 .tools/github-cli/runtime/bin/gh.exe를 사용했으며 GH_CONFIG_DIR는 .tools/github-cli/config다. 로그인 정보·기기 인증 코드·개인 설정·음악은 공개 파일에 포함하지 않는다.
