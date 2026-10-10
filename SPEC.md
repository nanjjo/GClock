# GClock v2.0 — AI 재현 제작 Spec

작성일: 2026-10-09 (Asia/Seoul). 이 문서만 전달받은 AI가 빈 폴더부터 동등한 Windows 앱을 만드는 것을 목표로 한다. 현재 코드가 없는 상황을 기준으로 읽는다. 제품은 로컬 데스크톱 시각 타이머이며 HTTP API나 Android 앱을 만들지 않는다.

최종 수정: 2026-10-10. 아래 DPI/렌더링 보완을 우선 적용한다. 이전 치수는 100% 배율의 논리적 기준값이다.

## 고해상도 제작 보완

## 설정 저장 제작 보완 (2026-10-10)

최신 볼륨/간격 보완: JSON에 volume_percent(엄격한 정수0~100)를 추가하고 초기100으로 로드한다. AudioPlayer.volume은 0~1 float이며 set_volume은 범위를 제한하고 다음 디코더 청크의 signed16 PCM 샘플에 곱한다. miniaudio 1.71에는 set_master_volume이 없으므로 호출하지 않는다. MP3 안내 줄은 '종료 시 재생할 MP3'로 줄이고 무음 다음에 볼륨 라벨과 수평0~100 Scale을 놓는다. showvalue=True, font14pt, width30*dpiScale로 숫자를 컨트롤 안에 표시한다. Scale의 command에서 오디오 적용·저장 예약. 기본 시스템 알림음은 운영체제 볼륨을 유지한다.

MM:SS 라벨은 dial_row의 자식으로 옮겨 place한다. gap=B/5를 좌우/아래에 통일한다. side=max(slider_reqwidth+gap,B+gap), radius=max(1,min((W-2*side)/2,(H-time_label_reqheight-gap)/2)), cx=W/2,cy=radius. 아래 숫자의 위쪽은 cy+radius+gap. 위 status 아래 패딩은 맑은 고딕11pt font.metrics('linespace')로 구한다. 따라서 시계 위는 글꼴 한 줄 높이, 아래는 옆 조작부와 같은 gap이며 남는 세로 공간은 아래로 간다. 이 공식은 기존 중앙 정렬/간격 공식보다 우선한다.

`settings_store.py`의 기본 경로는 EXE와 같은 폴더의 settings.json이다. sys.frozen이 참이면 Path(sys.executable).resolve().parent, 소스 실행은 Path(__file__).resolve().parent가 기준이다. 작업 폴더와 LocalAppData는 사용하지 않는다. SettingsStore(path=None)는 기본 경로, path=False는 저장 비활성, 지정 경로는 테스트·주입에 사용한다. GClock(root,settings_path=None)에서 생성 전 설정을 로드한다.

JSON 필드: selected_seconds(정수0~3600), color(세 가지 승인된 색상), muted/topmost/maximized(엄격한 bool), mp3_path(문자열, 최대32768), window={width,height,x,y}(모두 정수). width는 440~8000, height는 650~8000, 좌표 절댓값은 100000 이하로 검증한다. 잘못된 필드만 버리고 손상/누락 파일은 빈 기본값으로 처리한다. bool을 시간 정수로 허용하지 않는다.

window width/height는 실제 픽셀을 display_scale로 나눠 저장하고 복원 시 곱한다. x/y는 물리 화면 좌표다. Windows GetSystemMetrics(76~79) 가상 화면 범위에 제목줄 일부가 남는 위치만 복원한다. 최대화 상태는 정상 창 배치와 별도로 저장한다. 복원은 UI 변수와 TimerState.selected를 초기화하며 deadline=None,remaining=selected를 유지한다. 오디오 자동 재생은 없다.

StringVar/BooleanVar trace, 색상·시간 변경, root Configure에서 500ms 저장 예약을 갱신한다. 앱 종료 시 예약을 취소하고 최종 저장한다. 정상 상태에서만 정상 창 크기를 갱신한다. JSON은 UTF-8로 쓰고 같은 폴더의 임시 파일을 os.replace로 교체한다. 저장 권한 오류는 상태 문구로 알리고 앱은 계속 동작한다.

test_settings.py에서 Unicode 경로 왕복/임시 파일 정리, 손상·잘못된 값 기본 처리, 실제 UI 닫기/재생성에 따른 설정 복원 및 실행하지 않는 타이머를 검증한다. 테스트·EXE smoke에서는 실제 사용자 설정 경로를 쓰지 않는다. 전체 테스트는 18개다. 이 보완은 아래의 '저장하지 않는다'는 초기 v2.0 제한보다 우선한다.

## 고해상도 보완 상세

- 실행 의존성 `Pillow==12.3.0` 추가. `dial_renderer.py`, `display_support.py`, `windows.manifest`, `test_display.py` 추가.
- EXE 매니페스트의 WindowsSettings에 dpiAware=true, dpiAwareness=System을 선언하고 PyInstaller에 `--manifest "%CD%\windows.manifest"` 전달한다. 소스 실행은 Tk 생성 전에 user32.SetProcessDPIAware 호출. 이미 매니페스트가 설정했다면 다시 바꾸지 않아도 된다.
- GetDpiForSystem으로 DPI를 읽으며 지원되지 않으면 96 사용. Tk scaling을 dpi/72로 설정한다. 기본 창·최소 창, 메인 패딩, 버튼 패딩, 슬라이더 폭과 시계 간격을 dpi/96으로 곱해 반올림한다. 폰트 포인트 크기는 Tk가 scaling으로 처리하므로 또 곱하지 않는다.
- Canvas는 입력과 최종 이미지 표시용으로 사용한다. 원·눈금·숫자를 저해상도 Canvas 도형으로 직접 그리는 기존 5절 방식 대신 동일한 비율로 Pillow ImageDraw에 렌더링한다. 현재 표시 지름 D마다 2D×2D RGBA 버퍼를 만들고 마지막에 D×D로 LANCZOS 축소한다. 창 확대 시 예전 이미지를 확대하지 말고 새 물리 픽셀 크기에서 재렌더링한다.
- 타이머 계산은 계속 100ms 간격이지만 그림 키의 remaining은 ceil(remaining)으로 바꿔 다이얼을 초 단위로 다시 그린다. 크기 변경·색상 변경은 즉시 반영한다. 높은 해상도에서 불필요한 픽셀 재처리를 줄이기 위한 최적화다.
- 배경 본체/다이얼과 투명 눈금·숫자·노브 overlay를 (D,color)로 캐시한다. 매 갱신에 배경 복사→색 부채꼴→overlay 합성→축소. Pillow 각도는 시계방향이므로 부채꼴 start=270-extent,end=270. 숫자는 픽셀 폰트 크기 max(16,round(high_res_radius*0.10)), Arial Bold를 Windows Fonts/arialbd.ttf에서 로드한다. 없으면 Pillow 기본 폰트로 대체한다. Tk 포인트 단위와 픽셀 단위를 혼용하지 않는다.
- EXE smoke test의 Canvas 객체 60개 이상 조건을 고해상도 PhotoImage 존재/크기 조건으로 변경한다. Pillow 라이선스를 고지 파일에 추가한다.
- 테스트는 기존 8개에 300/600/1200px 렌더링 및 96/144/192 DPI 주입 UI 검증 2개를 추가한다. 원판의 분 단위 부채꼴 방향, 슬라이더 폭, Tk scaling, 버튼 표시를 검증한다. 실제 4K/혼합 DPI 모니터 검증과 모의 배율 검증을 구분한다.
- System DPI awareness는 기본 Windows 배율에서 흐린 자동 확대를 피하기 위한 선택이다. 여러 모니터 사이의 실시간 WM_DPICHANGED 처리는 구현하지 않는다. 이후 PerMonitorV2를 적용한다면 Tk 레이아웃과 글꼴을 DPI 변화마다 갱신하는 코드를 함께 구현해야 한다.

## 1. 결과물과 환경

Python 3.12 x64, Tkinter/ttk Canvas, miniaudio 1.71, PyInstaller 6.16.0을 사용한다. Windows x64에서 빌드하고 `dist/GClock.exe` 하나를 배포한다. 실행 PC에 Python이나 pip 설치를 요구하지 않는다. Tkinter를 포함한 정식 Windows Python 설치본을 빌드에 사용한다.

파일을 `gclock.py`, `audio_player.py`, `requirements.txt`, `requirements-build.txt`, `build.bat`, `run.cmd`, 테스트 세 개, 라이선스 고지로 나눈다. 상태 계산과 오디오는 UI에서 분리한다.

실행 의존성:

```text
miniaudio==1.71
cffi==2.1.1
pycparser==3.1
```

빌드 의존성에는 위 파일을 `-r requirements.txt`로 포함하고 다음을 고정한다.

```text
pyinstaller==6.16.0
altgraph==0.17.5
packaging==26.3
pefile==2023.2.7
pyinstaller-hooks-contrib==2026.8
pywin32-ctypes==0.2.3
setuptools==84.0.0
```

## 2. 타이머 상태를 먼저 구현

`TimerState(clock=time.monotonic)`를 작성한다. 테스트에서는 clock 함수를 주입할 수 있어야 한다.

- `selected`: 초기 1500초(25분). `remaining`: 초기 1500.0초. `deadline`: 초기 None.
- `set_minutes(m)`: m을 0~60으로 제한하고 `round(m*60)`을 selected에 저장한 뒤 reset.
- `start()`: 정지 상태이며 remaining>0이면 deadline=clock()+remaining. 실행 중 재호출은 무시.
- `tick()`: deadline이 없으면 False. 있으면 remaining=max(0,deadline-clock()). 0에 도달하면 deadline=None으로 바꾸고 이 호출에서만 True 반환. 이후 False.
- `pause()`: tick으로 현재 잔여량을 반영한 후 deadline=None.
- `reset()`: remaining=float(selected), deadline=None.

실행 중 시간 설정을 변경하면 타이머를 중지하고 새 시간으로 재설정한다. 완료 후 자동 반복은 없다. 실제 시간의 지연을 누적 차감하지 않고 deadline으로 보정한다. 시스템 날짜·시각 변경이 타이머에 영향을 주지 않도록 monotonic clock을 사용한다.

## 3. UI 구성

제목은 `GClock · 시각 타이머 · v2.0`, 초기 창 560×720, 최소 440×650이다. 배경은 `#f5f3ed`. ttk 테마는 clam. 기본 라벨/버튼은 맑은 고딕 11pt, 버튼 패딩 8. 메인 프레임 좌우 10px·상하 20px.

위에서 아래 순서:

1. 헤더: 왼쪽 GClock(맑은 고딕 23pt bold), 오른쪽 항상 위 체크박스와 색상 버튼 세 개. 항상 위는 `root.attributes('-topmost', bool)`로 반영.
2. 상태 안내 문구: 초기 “당신의 시간을 가볍게”. 위 8px·아래 12px 여백.
3. 가변 높이 다이얼 영역: 전체를 Canvas가 차지하고, 왼쪽 슬라이더와 오른쪽 프리셋을 같은 부모의 별도 위젯으로 위에 배치.
4. 남은 시간 MM:SS: Consolas 36pt, 초는 remaining의 ceil을 표시.
5. 안내: “다이얼 클릭 후 휠 ↑↓: 1분 조절 · 드래그도 가능”.
6. 초기화·시작/일시정지 버튼.
7. MP3 안내 문구 “종료 시 재생할 MP3 (빈칸: 기본 알림음)”와 그 뒤 무음 체크박스.
8. 경로 Entry와 찾기 버튼.
9. 미리 듣기·재생 중지 버튼.

색상은 코랄 `#df4a42`, 그린 `#3d8769`, 블루 `#447db0`. 초기 코랄. 상태·색상·경로는 저장하지 않는다.

## 4. 크기와 위치 계산

Canvas 폭 W, 높이 H, 슬라이더 요청 폭 S, 프리셋 프레임 요청 폭 B를 얻는다. 숫자·폰트의 화면 배율 차이를 고려해 고정 폭 대신 `winfo_reqwidth()`를 사용한다.

```text
side = max(S + 8, B * 1.2)
cx = W / 2
cy = H / 2
radius = max(1, min((W - 2*side)/2, H/2 - 12))
```

슬라이더 오른쪽 끝은 cx-radius-8, 위는 cy-radius, 높이는 2*radius. `place(anchor='ne', x=..., y=..., height=...)`로 배치한다. 슬라이더는 세로 방향, 위쪽 60·아래쪽 0, 분 단위 resolution=1, 트랙 폭 30px, 맑은 고딕 14pt. 슬라이더와 시계 높이가 함께 변해야 한다.

프리셋 왼쪽은 cx+radius+B/5, 세로 중심은 cy이며 `anchor='w'`로 배치한다. 10분·30분·50분 버튼 세 개를 세로로 놓고 버튼 width=4, 각 pady=6. 시계 중심을 기준으로 전체 좌우 공간은 대칭이다. 기본 크기에서는 오른쪽 창 끝과 프리셋 사이 여백이 버튼 폭의 약 1/5이 되도록 위 치수를 사용한다. 폭 대비 높이가 작은 창에서는 시계를 온전히 표시하기 위해 추가 여백이 생길 수 있다.

Canvas Configure 이벤트마다 위치와 다이얼을 다시 계산한다. 배치 키(cx,cy,radius)가 같으면 위젯 재배치를 생략하고, 그림 키(배치,색상,round(remaining,1))가 같으면 다시 그리지 않는다.

## 5. 다이얼 렌더링

Tk Canvas 기본 도형으로 그려 외부 이미지가 필요 없게 한다.

- 중심에서 radius만큼의 사각 본체를 선택 색상으로 채운다.
- 반지름 radius*0.94의 밝은 원형 다이얼(`#fcfcf8`).
- 색 원판 반지름 radius*0.68, 빈 원판 배경 `#eeeee8`.
- 남은 색 면적은 `remaining/3600*360`도. `start=90`, 양의 extent, pieslice로 그리면 12시부터 반시계 방향으로 증가한다. 60분은 원 전체, 30분 반원, 15분 1/4원. 거의 360도이면 arc 대신 원을 그린다.
- 각 분의 각도는 `-pi/2-minute*tau/60`. 0은 위, 15는 왼쪽, 30은 아래, 45는 오른쪽.
- 60개 눈금: 안쪽 radius*0.71, 바깥은 5분 눈금 0.78·일반 0.75. 선 색 `#414943`, 두께 각각 2·1.
- 5분마다 숫자를 radius*0.86 위치에 표시. Arial bold, 크기 max(8,int(radius*0.10)), 색 `#343d37`.
- 중앙 노브 반지름 radius*0.115, 채움 `#e3e7dc`, 테두리 `#ccd1c7` 두께 2.

## 6. 입력과 UI 갱신

Canvas 클릭과 드래그는 Canvas에 키보드 포커스를 주고 휠 잔여량을 초기화한다. 클릭점 dx,dy를 계산한다. 중심 radius*0.13 이내는 시간 변경 없이 포커스만 준다. 그 밖은 `angle=atan2(-dx,-dy)%tau`, minutes=round(angle/tau*60)으로 설정한다.

Windows MouseWheel은 Canvas에 포커스가 있고 event.widget도 Canvas일 때만 시간을 바꾼다. delta를 누적하고 `steps=trunc(accumulated/120)`으로 1분 단위를 계산한다. 사용된 steps*120을 누적량에서 뺀다. 새 시간은 0~60으로 제한한다. 처리 시 'break' 반환. 포커스가 다른 위젯으로 옮겨지면 이 핸들러는 시간 설정을 하지 않는다.

슬라이더 변경은 selected와 새 값이 다를 때만 set_minutes를 호출한다. 프리셋·다이얼이 slider.set()을 호출하면 Tk의 비동기 콜백이 뒤늦게 오므로 같은 값은 무시해야 한다.

Space는 시작/일시정지, Escape는 초기화. 시작 버튼은 남은 시간이 0이면 비활성화하고 실행 중에는 일시정지라고 표시한다. 초기화는 재생 음악도 멈춘다.

100ms마다 root.after로 tick→완료 처리→UI 갱신을 실행한다. after ID를 보관하고 중복 예약·앱 종료 시 취소한다. 실행·정지 상태는 deadline is None 여부로 구분한다.

## 7. MP3 엔진

GitHub 원본: https://github.com/irmen/pyminiaudio (MIT). Windows MCI 재생은 사용하지 않는다.

`AudioPlayer`는 device와 stream 참조를 보관한다. play(path)는 공백·둘러싼 큰따옴표 제거→expanduser→resolve→실제 `.mp3` 파일인지 검사한다. 기존 재생을 stop한 뒤 압축 파일을 bytes로 읽는다.

```python
stream = miniaudio.stream_memory(file.read_bytes(), frames_to_read=32768)
device = miniaudio.PlaybackDevice(buffersize_msec=500)
device.start(stream)
```

기본 형식은 signed16, 2채널, 44,100Hz다. stream_memory가 반환하는 generator는 이미 초기화되어 있으므로 추가 next를 호출하지 않는다. 재생은 오디오 장치의 백그라운드 콜백으로 진행한다. 기본 디코더 저장 공간 16,384보다 500ms 요청량 22,050프레임이 크므로 frames_to_read=32768을 반드시 유지한다. 임의 콜백 wrapper를 추가했다면 wrapper generator 자체의 초기화 요구도 확인한다.

stop은 device.close 후 stream.close, 참조를 None으로 변경한다. 디코드/장치 초기화 오류는 자원을 해제하고 RuntimeError로 UI에 전달한다. 자연 종료 후 남은 참조는 다음 재생·중지·종료 시 해제한다.

미리 듣기는 무음과 무관한 수동 재생이다. 무음 체크 시 재생 중인 음악을 멈추고 자동 종료 알림을 억제한다. 종료 시 경로가 비어 있으면 winsound의 SystemExclamation을 SND_ALIAS|SND_ASYNC로 재생한다. MP3 오류는 상태 문구에 표시하고 기본 알림음으로 대체한다. 미리 듣기 오류는 messagebox로 표시한다.

M4A는 이 버전의 지원 범위에 포함하지 않는다. MP3 파일 자체는 EXE에 묶지 않는다. 압축 파일 전체를 메모리에 올리므로 큰 파일의 시작 지연·메모리 사용은 알려진 제한이다.

## 8. 배치 빌드와 배포

build.bat 시작 시 setlocal, cd /d "%~dp0". 프로젝트 내부 .build-temp를 TEMP/TMP 및 PyInstaller 캐시에 사용한다. .venv가 없으면 py -3 또는 python으로 venv를 만든다. ensurepip, pip install -r requirements-build.txt, unittest 순서로 실행한다. 각 단계 뒤 errorlevel을 검사하고 실패 시 exit /b 1.

PyInstaller 핵심 명령:

```bat
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onefile --windowed --hidden-import _cffi_backend --add-data "%CD%\THIRD_PARTY_NOTICES.txt;." --name GClock --distpath dist --workpath build\python --specpath build gclock.py
```

--specpath가 build이므로 라이선스 데이터 경로는 절대 경로로 전달한다. miniaudio/cffi/Tcl/Tk 네이티브 의존성까지 포함한다. miniaudio·cffi·pycparser의 라이선스 전문을 THIRD_PARTY_NOTICES.txt로 제공하고 EXE 내부에 포함한다.

빌드 후 `start "" /wait "dist\GClock.exe" --smoke-test`를 실행하고 실패 시 nonzero로 종료한다. smoke 모드는 숨긴 Tk 창에서 UI 생성·시작·초기화·다이얼 객체 존재를 확인한다. 메모리에 1초 stereo signed16 44,100Hz WAV를 생성해 miniaudio stream_memory의 send(22050)이 44,100개 샘플을 반환하는지 검증한다. 실제 음악 출력은 이 검증과 별도로 확인한다.

run.cmd는 로컬 .venv Python이 있으면 그것을 사용한다. 없으면 Python으로 실행하며 오류 시 pause한다. 소스 실행 전 requirements.txt를 설치한다. 최종 사용자는 EXE만 실행한다.

## 9. 수용 기준과 검증

- 지연된 tick에도 종료 한 번만 처리. 일시정지 중 시간이 차감되지 않음. reset은 선택 시간 복원.
- 창 확대/축소 시 원판·숫자·노브·슬라이더가 동기화. 슬라이더 높이=2*radius, 프리셋 간격=B/5.
- 휠 부분 delta 누적, 0/60분 한계, 다른 포커스에서 비활성.
- MP3 종료 재생 호출, 무음 억제, 실패 시 기본음, 재생 중지/종료 시 자원 해제.
- 500ms 출력 요청에 대응하는 디코더 버퍼 회귀 테스트.
- 빌드 배치 성공·EXE smoke test 성공. 실제 MP3를 들으면서 창 크기도 바꿔 끊김을 확인.
- Python 없는 별도 Windows PC를 시험하지 않았다면 독립 PC 검증 완료라고 주장하지 않음.

UI·오디오 테스트는 Tk를 생성할 수 있는 Windows 데스크톱 세션에서 실행한다. 필요하면 현재 테스트와 동일한 8개 의미 있는 테스트를 만들고, 새 문제에만 테스트를 추가한다.

## 10. 구현 순서

빈 폴더→환경/의존성 파일→TimerState와 테스트→AudioPlayer와 버퍼 테스트→Canvas/배치→입력·타이머 갱신→MP3 종료 처리→UI 테스트→라이선스→배치/EXE smoke 모드→실제 재생 확인→README/HANDOFF 작성 순서로 진행한다. 사용자 사양 변경은 이 문서의 값보다 우선한다. Android, 설치 프로그램 등을 임의로 확장하지 않는다.

## 최신 동작의 상세 제작법

이 절을 초기 구현 예제보다 우선한다. AudioPlayer.volume_stream(source)는 try/finally로 source.close를 보장한다. `frames=yield b''` 이후 source.send(frames)로 청크를 받아 volume=1이면 원본 배열, 그 외에는 `array('h', (round(sample*volume) for sample in samples))`를 yield한다. 매 청크에서 최신 volume을 읽고 source의 StopIteration에는 반환한다. 원본 stream_memory는 이미 초기화되어 있으므로 next하지 않는다. wrapper만 next로 초기화한 뒤 device.start(wrapper)에 전달한다. device.close 후 wrapper.close 순서로 중지한다. 존재하지 않는 set_master_volume은 사용하지 않는다.

다이얼 부모는 fill=x, expand=False로 pack한다. Canvas 및 루트 Configure에서 resize_dial을 호출한다. B=프리셋 요청폭, gap=B/5, side=max(slider요청폭+gap,B+gap), wanted=Canvas폭-2*side+시간라벨요청높이+gap이다. available=main높이-상하패딩-다른 main 자식의 요청높이 및 pack pady 합이다. pady는 숫자 또는 Tcl 리스트일 수 있다. Canvas height=max(80,round(min(wanted,available)))로 설정하며 현재 요청높이와 다를 때만 configure한다. 시간 숫자 아래에는 안내·조작부가 바로 이어져야 한다. 기존 저장 창 크기는 복원하고 새 기본값은 560×720이다.

볼륨 Scale은 IntVar, showvalue=True, 14pt, width30*dpiScale를 사용하며 별도 퍼센트 라벨은 없다. pointer는 다이얼 반경 밖에서는 무시한다. 중앙 노브는 포커스만 준다. wheel은 focus_get()==canvas이고 event.widget==canvas일 때만 적용한다. Space/Escape는 루트 또는 Canvas 대상일 때만 타이머 단축키로 처리한다. 파일 찾기는 Entry로 포커스를 옮기고 wheel 누적량을 비운 다음 경로만 변경한다. 타이머 selected/deadline을 변경하지 않는다.

SettingsStore 기본 경로는 frozen이면 sys.executable의 절대 부모, 소스이면 모듈의 절대 부모에 settings.json을 붙인다. 지정 테스트 경로도 절대 경로로 변환한다. LocalAppData와 CWD는 읽지 않는다. 상대 음악 경로는 settings.path.parent 기준으로 해석하고 미리 듣기와 종료 알림 모두 같은 audio_path()를 사용한다. EXE 폴더에 쓰기 권한이 없으면 상태 문구로 저장 실패를 알리고 다른 위치로 조용히 우회하지 않는다.

테스트18개: gain 테스트에는 PCM WAV 데이터를 .mp3 확장자 임시 파일로 저장해 콘텐츠 감지 디코더와 PlaybackDevice autospec을 사용한다. 0.5 gain의 샘플 값과 0 gain을 확인해 실제 없는 장치 API가 다시 추가되지 않게 한다. 실제 MP3·오디오 장치 검증은 별도로 수행한다. Tk callback 오류도 테스트 실패로 처리한다. frozen 설정 위치는 sys.executable 주입 후 CWD 변경으로 검증한다. 나머지는 UI 파일 선택 후 selected/deadline 유지, 다른 컨트롤 휠 무시, 상대 음악 경로와 compact 레이아웃을 검증한다.


## 최신 볼륨 디자인 및 시계 확대 (이전 볼륨 UI 설명보다 우선)

새 기본 창은560×720으로, 기존460px 폭에서 다이얼 지름이 약25% 커진다. 구버전 JSON에 창 크기가 있으면 layout_version<2일 때 width>=520, height>=720로 한 번 확대하고 layout_version=2를 저장한다. 그 후 사용자 창 크기는 그대로 복원한다. 다른 설정은 유지한다.

volume_control.py의 VolumeBar는110×15 논리 픽셀의 고정 크기 Canvas다. 이전 바의 가로·세로 크기를 약절반으로 줄였다. 숫자·볼륨 라벨 없이 회색 전체 바와 녹색 volume_percent/100 비율의 채움 사각형을 그린다. 클릭·드래그 위치를0~100으로 제한해 IntVar에 저장한다. 변수 trace로 즉시 그림과 오디오 gain 및500ms 설정 저장 예약을 갱신한다. 좌우 화살표/휠은5단위, Home/End는0/100이며 타이머 단축키와 분리한다. Destroy에서 trace를 해제한다. MP3 안내와 무음 체크박스 글꼴은 모두 맑은 고딕11pt, pack(side=left,anchor=center)로 바의 수직 중앙과 맞춘다. 볼륨 바는 expand하지 않는다.

miniaudio PlaybackDevice(buffersize_msec=50, callback_periods=2)로 바꾸어 약100ms의 출력 큐를 목표로 한다. frames_to_read=32768은 디코더 용량이며 그대로 유지한다. 50ms 요청2205프레임을 패키징 smoke test에서도 검증한다. 이전500ms 관련 내용은 과거 CFFI 오류 원인 설명이다. 최종 소리가 들리는 지연은 Windows·오디오 장치의 추가 버퍼에도 영향을 받으므로 물리적으로 정확한100ms라고 보장하지 않는다. 볼륨 gain은 다음 콜백부터 적용하며 장치를 다시 시작하지 않는다.

18개 회귀 테스트에서 색 채움 비율·텍스트 부재·그래픽 중앙 정렬·클릭 후 즉시 볼륨 적용·새 장치 버퍼 인자를 검증한다. 실제 MP3 재생도 확인한다.


## 최신 좌우 정렬 보완

이 절의 배치를 이전 패딩 설명보다 우선한다. main의 논리 패딩은(left30,top0,right30,bottom20)이며 DPI 배율을 적용한다. 제목줄과 GClock 사이의 추가 상단 여백을 제거했다. GClock, MP3 안내, 경로 입력칸의 왼쪽 기준선을 통일하고, 마지막 색상 버튼·볼륨 바·찾기 버튼의 오른쪽 끝을 맞춘다. 마지막 색상 버튼의 오른쪽 pack padx는0이다. MP3 안내는 왼쪽, 볼륨 바는 side=right로 먼저 pack하고 무음 체크박스를 그 왼쪽에 side=right로 pack한다. 모두 수직 중앙에 맞춘다. 경로 Entry는 side=left, fill=both, expand=True로 pack해 찾기 버튼과 동일한 높이를 갖는다.

resize_dial의 가용 높이는 main높이에서20*dpiScale 및 다른 자식 높이/패딩을 뺀다. 새 기본 창은560×720으로 이전보다 좌우 여백이20px씩 증가해도 시계 지름을 유지한다. 기존 JSON은 layout_version<2일 때 이전 확대(최소520×720)를 적용하고, layout_version<3일 때 폭만40px 더해 한 번 보정한다. 이후 layout_version=3으로 저장하며 사용자 창 크기를 계속 복원한다. 설정과 음악 파일 경로는 그대로 유지한다.

기존 UI 테스트에서 입력/버튼 높이 일치, 헤더 상단 여백0, 좌우 끝선 일치도 확인한다.


## v2.0 최종 변경 (앞선 레이아웃 치수보다 우선)

GPT-6.1 Sol을 활용해 제작했다. MP3 출처: pyminiaudio1.71 https://github.com/irmen/pyminiaudio (MIT), 그 안의 네이티브 miniaudio https://github.com/mackron/miniaudio (public domain 또는 MIT-0). README와 ABOUT.md에 제작 도구 및 출처를 명시하고 배포할 때 THIRD_PARTY_NOTICES.txt를 제공한다.

제목은 GClock · 시각 타이머 · v2.0이다. 바깥 패딩을(left6,top0,right6,bottom4)*dpiScale로 바꾸어 이전 좌우30px·아래20px의1/5로 줄인다. 새 기본 창은512×704이며 시계 표시 크기는 유지한다. resize_dial은 main높이에서4*dpiScale와 다른 자식 요청높이/패딩을 뺀다. JSON layout_version은4로 저장한다. 이전 레이아웃1/2/3의 기존 보정을 순서대로 적용한 후 version<4에서는 width=max(440,width-48), height=max(650,height-16)으로 한 번 줄인다. 이후 창 크기와 설정은 계속 복원한다.

GitHub 공개 저장소에는 Python 소스, 고정 의존성, 배치, 테스트, 매니페스트, 라이선스, 제작/재현 문서만 등록한다. 개인 settings.json·음악·Flutter 과거 파일·personal-skills·.venv·.tools·빌드 캐시를 올리지 않는다. 실행 파일은 v2.0 릴리스 자산으로 제공한다. 공개 등록은 사용자가 명시적으로 승인했다.
