# GClock v2.3 제작 및 배포 안내

GPT-6.1 Sol을 활용해 제작한 Windows x64 시각 타이머입니다.

프로젝트: https://github.com/nanjjo/GClock

MP3 플레이어는 Irmen de Jong의 **pyminiaudio 1.71**을 사용합니다.
원본: https://github.com/irmen/pyminiaudio (MIT)

이 바인딩에 포함된 네이티브 엔진은 David Reid의 **miniaudio**입니다.
원본: https://github.com/mackron/miniaudio (public domain 또는 MIT-0)

audio_player.py는 이 엔진을 사용해 MP3 디코드, 버퍼 재생과 실시간 PCM 볼륨 조절을 제공합니다. 의존성 라이선스 전문은 THIRD_PARTY_NOTICES.txt에 있습니다.

실행 PC에는 Python 설치가 필요 없습니다. 음악은 별도로 준비하며 EXE 옆 settings.json에 설정이 저장됩니다. Python이 없는 별도 PC에서의 검증은 수행하지 않았습니다.
