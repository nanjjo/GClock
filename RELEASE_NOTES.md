# GClock v2.2

- MP3 경로·무음·볼륨·미리 듣기·재생 중지를 별도 소리 설정 창으로 이동했습니다. 기본 화면에서는 숨깁니다.
- 비모달 설정 창에서 타이머를 유지하며 변경하고 자동 저장합니다. 창을 닫으면 음악 재생이 멈춥니다.
- 시간이 끝나면 선택 색의 파동이 중심에서 계속 퍼집니다. 무음 상태에서도 표시됩니다.
- 확인/다이얼 클릭으로 알림을 종료하거나, 다시 시작으로 같은 시간을 바로 시작합니다.
- 기본 창을512×560으로 줄였고 기존 창 설정은 한 번 높이를 보정합니다.
- 한국어/English와 고해상도 대응, EXE 옆 JSON 설정을 유지합니다.

Windows x64 단일 EXE는 Python 설치 없이 실행합니다. GPT-6.1 Sol 활용 제작.
MP3 재생 출처: [pyminiaudio](https://github.com/irmen/pyminiaudio) (MIT), [miniaudio](https://github.com/mackron/miniaudio) (public domain/MIT-0).

GClock.exe 또는 GClock-v2.2-Windows-x64.zip을 내려받아 실행하세요. 설정과 음악은 포함하지 않습니다. ZIP에는 사용/재현 사양과 출처/라이선스를 넣었습니다. 최신 인수인계는 저장소의 HANDOFF.md를 확인하세요.

테스트25개와 패키징 EXE 검사를 통과했습니다. 설정 창 표시 대기와 JSON 결과/종료 코드 검증을 보완해 자동 검사 오류 팝업을 방지했습니다. Python 없는 별도 PC 검증은 수행하지 않았습니다.
