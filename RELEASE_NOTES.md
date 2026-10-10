# GClock v2.0

Windows x64용 시각 타이머입니다. **GPT-6.1 Sol을 활용해 제작**했습니다.

- 좌우·아래 여백을 이전의1/5로 축소: 좌우6px, 아래4px.
- 고해상도 다이얼, 10/30/50분 프리셋, 클릭·드래그·휠 시간 조절.
- MP3 종료 알림과 미리 듣기, 무음, 작은 색 채움 볼륨 바.
- EXE 옆 settings.json에 시간·음악 경로·볼륨과 창 설정 저장.
- 50ms 오디오 period 두 개를 사용해 빠른 볼륨 반응 제공.

MP3 플레이어: [pyminiaudio1.71](https://github.com/irmen/pyminiaudio) (MIT), 네이티브 엔진 [miniaudio](https://github.com/mackron/miniaudio) (public domain 또는 MIT-0). 제작/출처 안내는 ABOUT.md, 의존성 라이선스는 THIRD_PARTY_NOTICES.txt에 있습니다.

GClock.exe 또는 GClock-v2.0-Windows-x64.zip을 내려받아 실행하세요. Python 설치는 필요 없습니다. 음악은 별도로 준비하며 설정 파일은 실행 시 자동 생성됩니다. ZIP에는 실행 파일·README·제작 및 라이선스 안내가 포함됩니다. 개인 설정과 음악은 포함하지 않습니다.

검증: 테스트18개, v2.0 배치 빌드, 패키징된 EXE smoke test 통과. Python이 없는 별도 PC/VM 검증은 수행하지 않았습니다. M4A·Android는 지원하지 않습니다.
