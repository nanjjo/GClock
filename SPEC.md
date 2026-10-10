# GClock v2.1 — 빈 프로젝트에서 만드는 독립 제작 사양

작성일: 2026-10-10 (Asia/Seoul). 현재 소스와 대화 없이 이 문서로 동등한 Windows 시각 타이머를 만들 수 있어야 한다. 앱은 Python/Tkinter 데스크톱 프로그램이다. HTTP API·Android 앱을 대신 만들지 않는다. 제작 도구 표기는GPT-6.1 Sol이다.

## 1. 환경과 파일

빌드: Windows x64, Tkinter 포함Python3.12 x64. 실행: Windows x64, Python 설치 불필요. gclock.py를 진입점으로 하고 audio_player.py, volume_control.py, dial_renderer.py, display_support.py, settings_store.py, translations.py로 분리한다. 배치2개, Windows manifest, 테스트5개 모듈, 사용/인수인계/사양/릴리스/제작 안내와 의존성 라이선스 전문을 제공한다.

requirements.txt:

```text
miniaudio==1.71
cffi==2.1.1
pycparser==3.1
Pillow==12.3.0
```

requirements-build.txt는위 파일을-r requirements.txt로 포함하고 pyinstaller==6.16.0, altgraph==0.17.5, packaging==26.3, pefile==2023.2.7, pyinstaller-hooks-contrib==2026.8, pywin32-ctypes==0.2.3, setuptools==84.0.0을 고정한다. 임의 버전 최신화는 별도 요구가 없다면 하지 않는다.

## 2. 타이머 상태

TimerState(clock=time.monotonic)를 만든다. selected=1500 정수초, remaining=1500.0, deadline=None이다. 테스트는clock을 주입한다.

- set_minutes(m):m을0~60으로 제한하고 selected=round(m*60), reset 호출.
- reset:remaining=float(selected), deadline=None.
- start:deadline이None이고remaining>0이면deadline=clock()+remaining.
- tick:정지 시False. 실행 시remaining=max(0,deadline-clock()). 0이 되면deadline=None 및True 반환. 다음 호출부터False이므로 완료는 한 번만 처리한다.
- pause:tick 후deadline=None. 재개는start로 현재 잔여량에 새deadline을 부여한다.

루트after(100,tick)로 갱신한다. UI 시간은ceil(remaining)의MM:SS다. 시간을 조절하면 타이머를 멈추고 새selected로 초기화한다. 언어·볼륨·MP3 경로 변경은 시간을 바꾸지 않는다. 재실행에는 selected의 준비 상태를 복원하며 자동 재생/시작하지 않는다.

## 3. DPI와 기본 화면

Tk 생성 전에SetProcessDPIAware를 호출하고 지원되지 않으면 무시한다. EXE manifest는dpiAware=true, dpiAwareness=System, requestedExecutionLevel=asInvoker, assemblyIdentity.version=2.1.0.0으로 설정한다. GetDpiForSystem이 없으면96을 사용한다. s=dpi/96, Tk scaling=dpi/72. 글꼴은 point 단위로 지정하고 다시s를 곱하지 않는다.

VERSION='2.1'. 창 제목은 GClock · 시각 타이머 · v2.1 또는 영어 GClock · Visual Timer · v2.1이다. 기본512*s ×704*s, 최소440*s ×650*s. 배경#f5f3ed, ttk clam. 기본 맑은 고딕11pt, 버튼padding=round(8*s). main의패딩(left6*s,top0,right6*s,bottom4*s).

상단 헤더 왼쪽GClock23pt bold. 오른쪽그룹은 한국어/English 읽기 전용콤보(width7,11pt), 항상 위 체크박스, 색상3개 순서다. 색상은#df4a42,#3d8769,#447db0. 마지막색상 버튼 오른쪽pack padx=0으로 끝선을 맞춘다. 항상 위는root.attributes('-topmost',bool).

그 아래 상태 문구는윗간격8, 아래11pt 글꼴의linespace. 다음 다이얼영역, 남은 시간, 조작 안내, 초기화/시작, MP3 안내·무음·볼륨, 경로 입력/찾기, 미리 듣기/재생 중지 순서다. controls pady12, MP3 heading pady(12,4), 마지막controls pady(6,0). MP3 안내는왼쪽, 볼륨부터side=right로pack하고 무음을그 왼쪽에 둔다. 글꼴11pt와수직중앙을 맞춘다. Entry와찾기는같은부모, Entry fill=both/expand=True로높이를맞춘다. 기본Entry 폰트의actual(size)를읽고맑은고딕2배point로바꾼다.

## 4. 다이얼 및 주변 배치

다이얼 부모dial_row는fill=x, expand=False. Canvas는부모를채운다. 왼쪽Scale(from60,to0,vertical,resolution1,width30*s,font14pt), 오른쪽별도Frame에10/30/50분버튼(각pady6)을place로둔다. 숫자라벨은Consolas36pt다. 프리셋폭은한국어width4, 영어width6으로조절한다.

Canvas폭W, 높이H, 프리셋요청폭B, 숫자라벨요청높이T라 하자:

```text
gap=B/5
side=max(slider요청폭+gap,B+gap)
r=max(1,min((W-2*side)/2,(H-T-gap)/2))
cx=W/2, cy=r
slider: x=cx-r-gap, y=cy-r, anchor=ne, height=2*r
presets: x=cx+r+gap, y=cy, anchor=w
time: x=cx, y=cy+r+gap, anchor=n
```

숫자아래빈공간을없애기 위해 Canvas 요청높이를wanted=W-2*side+T+gap으로계산한다. available=main현재높이-4*s-다른main pack자식의요청높이/pady합이다. height=max(80,round(min(wanted,available))). 기존요청높이와다를때만configure한다. pady는숫자또는Tcl리스트일수있다. 루트/Canvas Configure와언어전환after_idle에서재계산한다. 언어레이아웃after ID를보관하고교체/종료시취소한다.

다이얼은Pillow로현재물리픽셀지름D의2배크기(2D×2D RGBA)로그린뒤LANCZOS로D×D 축소한다. (D,color)로본체와overlay를캐시한다. 본체사각형은색상, 내부흰원반은고해상도radius*.94. tick은정수minute=0..59에각도-pi/2-minute*tau/60으로반시계방향이다. tick 시작.71r, 끝은5분마다.78r/그외.75r. 숫자는5분마다.86r,0/5/…55. Arial Bold를Windows Fonts/arialbd.ttf에서읽고없으면Pillow기본폰트. 폰트픽셀크기max(16,round(r*.10)). 노브반경.115r. 남은시간원반반경.68r, extent=clamp(remaining/3600*360,0,360), pieslice start=270-extent,end=270. 60분전체는원을채운다. 색부채꼴을그린뒤눈금/숫자/노브overlay 합성한다.

Canvas에는ImageTk.PhotoImage 하나를표시하고참조를보관한다. 그리기키는(layout,color,ceil(remaining))다. 크기/색상은즉시, 타이머그림은초단위로바꾸어4K의불필요한100ms 재렌더링을피한다. 예전저해상도이미지를늘리지않는다.

## 5. 입력과 볼륨 바

Canvas pointer는반경밖을무시하고안쪽클릭/드래그시포커스·wheel누적량초기화. 노브.13r이내는시간을바꾸지않는다. 나머지는angle=atan2(-dx,-dy)%tau, minutes=round(angle/tau*60)이다. root MouseWheel은focus_get()==Canvas와event.widget==Canvas 모두참일때만delta누적, steps=trunc(remainder/120),remainder-=steps*120으로1분씩0~60조절하고break반환한다. 다른컨트롤의휠은시간을변경하지않는다. slider의비동기command는round(value*60)==selected이면무시해프로그래밍동기화가타이머를초기화하지않도록한다.

Space/Escape는이벤트대상이루트또는Canvas일때만toggle/reset이다. MP3 Entry·볼륨·콤보·버튼에서단축키로오작동하지않아야한다. 찾기는Entry포커스와wheel누적량0설정후대화상자를열고선택경로만변경한다.

VolumeBar는110*s ×15*s Canvas. 숫자/볼륨라벨없이회색#d7d8d2 전체바위에녹색#3d8769를W*volume_percent/100까지채운다. 클릭/드래그x/W*100을round후0~100으로제한해IntVar에쓴다. 변수trace는즉시그림과오디오gain 및설정저장예약을갱신한다. 좌우/휠은5단위,Home/End는0/100이며break반환한다. 기본volume100. Destroy에서trace를제거한다.

## 6. MP3 재생

AudioPlayer는device/stream참조와volume0~1 float를보관한다. play(path)는공백/둘러싼큰따옴표제거,expanduser/resolve,실제.mp3 존재를검증한다. 기존재생stop 후파일전체를bytes로읽어디코드한다.

```python
source = miniaudio.stream_memory(file.read_bytes(), frames_to_read=32768)
stream = volume_stream(source)
next(stream)  # wrapper만 초기화; source는 이미 초기화됨
device = miniaudio.PlaybackDevice(buffersize_msec=50, callback_periods=2)
device.start(stream)
```

기본signed16,2채널,44100Hz. miniaudio1.71에는장치set_master_volume이없다. volume_stream은try/finally안에서frames=yield b'' 후source.send(frames)로받은배열을,volume==1이면그대로그외에는array('h',(round(sample*volume) for sample in samples))로yield한다. 매청크의최신volume을읽는다. source StopIteration에는반환하고finally source.close한다. stop은device.close 후wrapper.close,참조None순서다. 디코더/장치오류는정리후RuntimeError로UI에전달한다. 이전500ms period/16384디코더용량은22050프레임요청을못받아CFFI오류가났으므로디코더용량32768을유지한다. 50ms period2개는약100ms 출력큐목표일뿐물리청취지연보장은아니다.

미리듣기는무음과무관한수동재생. 무음체크는현재재생stop 및자동알림억제. 타이머완료시MP3가설정되면재생,없거나재생실패시winsound SystemExclamation/SND_ALIAS|SND_ASYNC. 미리듣기오류는messagebox,자동재생오류는상태에표시한뒤기본음. 상대음악경로는JSON부모기준이며두경로모두공통audio_path를사용한다.

## 7. 언어와 설정

translations.TEXT={'ko':{…},'en':{…}}에같은키를둔다. 기본ko,콤보표시는한국어/English. 제목·항상위·안내·프리셋·Reset/Start/Pause·MP3 at end/Mute/Browse/Preview/Stop audio·파일선택제목/유형·상태/오류를번역한다. 상태는status_key/detail로기억하고언어전환시현재언어로다시표시한다. 전환은텍스트·폭·상태·refresh/레이아웃만갱신하고selected/remaining/deadline/오디오를건드리지않는다. 앱이생성한오디오한국어예외문구도현재언어로바꾼다. 네이티브오류상세와OS파일대화상자버튼은OS언어를유지한다.

SettingsStore(path=None/False/지정경로). frozen은Path(sys.executable).resolve().parent/settings.json, 소스는settings_store.py부모/settings.json. False는저장비활성,테스트지정경로는절대경로로변환. CWD/LocalAppData에서는읽지않는다. UTF-8 JSON 로드시OSError/ValueError는빈기본설정,저장시같은폴더NamedTemporaryFile→json.dump ensure_ascii=False indent2→os.replace→임시파일정리. 쓰기실패는상태에알리고다른폴더로우회하지않는다.

스키마검증은허용필드만보존한다:

| 필드 | 검증/기본값 |
|---|---|
| selected_seconds | 엄격한int0..3600 /1500 |
| volume_percent | int0..100 /100 |
| language | ko 또는en /ko |
| muted,topmost,maximized | 정확한bool /False |
| color | 위3색화이트리스트 /빨강 |
| mp3_path | 문자열길이<=32768 /빈문자열 |
| layout_version | int1..4 /구형1 |
| window | width440..8000,height650..8000,x/y 절댓값<=100000,모두int |

창크기는s로나눈논리값,좌표는물리값. 가상모니터GetSystemMetrics(76..79)와비교해접근가능한제목위치일때복원한다. 최대화는normal창크기를유지한채복원한다. JSON변경은500ms debounce와종료시저장. 진행중remaining/deadline/재생상태는저장하지않는다.

구형window마이그레이션:layout<2는최소520×720,layout<3는폭+40(최대8000),layout<4는width=max(440,width-48),height=max(650,height-16). 순서대로적용하고다음저장에layout_version4. 제품버전2.1과분리한다. 종료는tick/save/layout after 취소→설정저장→오디오stop→root.destroy.

## 8. 빌드와 배포

build.bat는setlocal,cd /d "%~dp0",.build-temp 생성후TEMP/TMP/PYINSTALLER_CONFIG_DIR를프로젝트내부로설정한다. .venv가없으면py -3 또는python -m venv로만든다. ensurepip,고정requirements-build 설치,테스트20개실행,PyInstaller순서이며매단계errorlevel검사와실패exit /b1.

```bat
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onefile --windowed --manifest "%CD%\windows.manifest" --hidden-import _cffi_backend --add-data "%CD%\THIRD_PARTY_NOTICES.txt;." --name GClock --distpath dist --workpath build\python --specpath build gclock.py
start "" /wait "dist\GClock.exe" --smoke-test
```

specpath가build이므로데이터/매니페스트절대경로를사용한다. 라이선스는EXE안에묶고ZIP에도제공한다. run.cmd는프로젝트.venv우선,없으면python,오류시pause. 배포ZIP에는GClock.exe,README/ABOUT/SPEC,THIRD_PARTY_NOTICES만포함한다. 사용자settings.json/음악/토큰/가상환경은제외한다. EXE/ZIP SHA256파일을생성한다.

## 9. 검증 및 GitHub

TimerState의지연완료1회/일시정지/재개,다이얼크기동기화,슬라이더높이/프리셋/숫자간격,휠부분delta/경계/포커스,MP3완료/무음/실패,실제디코더및PCM gain과PlaybackDevice autospec,JSON손상/Unicode/원자성/작업폴더독립/재실행저장,언어전환중타이머/오디오유지,영어파일/오류/완료문구를검증한다. 배율96/144/192 DPI와300/600/1200px 렌더링검증도포함한다. Tk callback 예외는테스트실패다.

EXE smoke는숨긴Tk에서생성/시작/언어전환/Pause문구/deadline유지/초기화/PhotoImage를검증한다. 메모리WAV의stream.send(2205)가4410 samples를반환하는지확인한다. 실제MP3 출력은별도검증이고클린PC/실제4K검증과모의배율검증을구분한다.

이사용자는마무리시GitHub게시까지요청했다. 이프로젝트는공개nanjjo/GClock,기존origin을재사용한다. 최종소스/문서만선별커밋하고fast-forward push한다. v2.1 태그릴리스에EXE/ZIP/체크섬/출처/라이선스를올리고PUBLIC·게시상태·자산·원본EXE와업로드digest일치를확인한다. 기존태그/릴리스를강제덮어쓰지않는다. Git identity는확인된계정noreply또는기존프로젝트설정,credential helper는가능하면호출범위로둔다. 계정로그인은사용자가직접완료하고토큰을공개파일이나문서에넣지않는다.

## 10. 처음부터 구현하는 순서와 한계

빈폴더→의존성/배치/manifest→TimerState/계산테스트→settings schema→오디오/버퍼/gain→DPI/렌더러→UI/배치→입력/볼륨→언어/상태키→알림/자원정리→통합테스트→출처/라이선스/문서→EXE smoke→실제음악→GitHub소스/릴리스검증순서로진행한다.

M4A·Android·자동반복·진행상태복원·설치프로그램·코드서명은범위밖이다. 절전중알림없음,System DPI로혼합DPI 실시간재배율없음,대형MP3 전체메모리읽기제한이있다. Python없는별도PC검증없으면성공이라고주장하지않는다.

제작출처: GPT-6.1 Sol. pyminiaudio1.71 https://github.com/irmen/pyminiaudio (MIT), miniaudio https://github.com/mackron/miniaudio (public domain/MIT-0). 의존성라이선스전문을실제배포에제공한다. Windows글꼴은설치경로에서읽고재배포하지않는다.
