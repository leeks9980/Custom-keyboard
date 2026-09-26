# Raspberry Pi Pico Custom USB Controller

Raspberry Pi Pico와 EC11 로터리 엔코더, 4개의 버튼을 이용한
커스텀 USB HID 컨트롤러입니다.

버튼 기능은 Pico 내부의 settings.json에 저장되며,
Windows 설정 프로그램을 통해 GUI에서 변경할 수 있습니다.

## 주요 기능

- USB HID 기반 커스텀 컨트롤러
- 4개 버튼 사용자 지정
- 키보드 단축키 / 문자열 입력
- EC11 볼륨 조절 및 음소거
- Pico 내부 설정 저장
- Windows GUI 설정 프로그램
- Pico의 현재 설정 자동 불러오기
- 설정 변경 후 Pico 자동 적용
- Windows EXE 배포 지원

## System Architecture


                 ┌─────────────────────────┐
                 │   PC Configuration GUI  │
                 └────────────┬────────────┘
                              │
                         USB Serial
                              │
                              ▼
                 ┌─────────────────────────┐
                 │    Raspberry Pi Pico    │
                 │                         │
                 │  ┌───────────────────┐  │
                 │  │   settings.json   │  │
                 │  └───────────────────┘  │
                 │                         │
                 │  Button Input           │
                 │  EC11 Encoder           │
                 └────────────┬────────────┘
                              │
                           USB HID
                              │
                              ▼
                 ┌─────────────────────────┐
                 │      Host PC            │
                 │  Keyboard / Volume      │
                 └─────────────────────────┘

## Hardware

| Component | Quantity |
|---|---:|
| Raspberry Pi Pico | 1 |
| EC11 Encoder | 1 |
| Push Button | 4 |

### GPIO

| Function | GPIO |
|---|---|
| Button 1 | GP20 |
| Button 2 | GP18 |
| Button 3 | GP1 |
| Button 4 | GP9 |
| Encoder A | GP21 |
| Encoder B | GP22 |
| Encoder SW | GP10 |

## Configuration GUI

[GUI 스크린샷]

설정 프로그램은 Pico에 저장된 settings.json을
자동으로 읽어 현재 설정을 GUI에 표시합니다.

사용자는 버튼을 선택하고 키 입력 또는 문자열을
지정할 수 있습니다.

## Project Structure

```text
Pico-USB-Controller/
├── Pico/
│   ├── boot.py
│   ├── code.py
│   └── settings.json
│
├── PC/
│   ├── control.py
│   ├── config.py
│   ├── dialogs.py
│   ├── main_gui.py
│   ├── pico.py
│   ├── settings.py
│   └── window_style.py
│
└── README.md
