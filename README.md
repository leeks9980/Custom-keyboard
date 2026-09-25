# Raspberry Pi Pico Custom USB Controller

Raspberry Pi Pico와 EC11 로터리 엔코더, 4개의 버튼을 이용하여 제작한 **커스텀 USB 입력 컨트롤러**입니다.

Pico는 컴퓨터에 USB HID 장치로 인식되며, 버튼을 누르면 키보드 단축키 또는 지정된 문자열을 입력할 수 있습니다.

또한 별도의 PC 설정 프로그램을 통해 Pico 내부의 `settings.json`을 수정하여 버튼 기능을 GUI에서 간편하게 변경할 수 있습니다.

---

## 주요 기능

* Raspberry Pi Pico 기반 USB HID 컨트롤러
* EC11 로터리 엔코더 지원

  * 시계 방향 → 볼륨 증가
  * 반시계 방향 → 볼륨 감소
  * 버튼 → 음소거 토글
* 4개의 물리 버튼 지원
* 버튼별 기능 설정

  * 키보드 단축키
  * 문자열 입력
* Pico 내부 `settings.json`을 이용한 설정 저장
* Windows PC 설정 프로그램 제공
* PC 프로그램 실행 시 Pico의 현재 설정을 자동으로 읽어 GUI에 표시
* 설정 변경 후 Pico 자동 재부팅
* USB HID를 이용하므로 별도의 PC용 드라이버 없이 키보드 입력 장치로 사용 가능

---

## Hardware

### 사용 부품

| 부품                  | 수량 | 설명          |
| ------------------- | -: | ----------- |
| Raspberry Pi Pico   |  1 | 메인 컨트롤러     |
| EC11 Rotary Encoder |  1 | 볼륨 조절 및 음소거 |
| Push Button         |  4 | 사용자 지정 입력   |
| USB Cable           |  1 | PC 연결       |

---

## GPIO 연결

### EC11 Rotary Encoder

| EC11 | Raspberry Pi Pico |
| ---- | ----------------- |
| A    | GP21              |
| B    | GP22              |
| SW   | GP10              |
| GND  | GND               |

### 버튼

각 버튼은 한쪽을 GPIO에 연결하고 다른 쪽을 GND에 연결합니다.

내부 Pull-up 저항을 사용하므로 별도의 외부 저항 없이 사용할 수 있습니다.

| 버튼       | GPIO |
| -------- | ---- |
| Button 1 | GP20 |
| Button 2 | GP18 |
| Button 3 | GP1  |
| Button 4 | GP9  |

GPIO는 현재 프로그램에서 고정되어 있으며 PC 설정 프로그램에서 변경하지 않습니다.

---

## 프로젝트 구조

```text
Pico-USB-Controller/
│
├── Pico/
│   ├── boot.py
│   ├── code.py
│   └── settings.json
│
├── PC/
│   └── pico_configurator.py
│
└── README.md
```

---

# Pico 프로그램

Pico에서는 CircuitPython을 사용합니다.

## `boot.py`

USB CDC 인터페이스를 활성화하여 PC 설정 프로그램과 통신할 수 있도록 합니다.

```python
import usb_cdc

usb_cdc.enable(
    console=True,
    data=True
)
```

`console`과 `data` 두 개의 USB CDC 인터페이스를 활성화합니다.

PC 설정 프로그램은 이 중 `data` 포트를 사용하여 Pico와 통신합니다.

---

# `code.py`

Pico의 메인 프로그램입니다.

주요 역할은 다음과 같습니다.

* `settings.json` 읽기
* EC11 로터리 엔코더 처리
* 버튼 입력 처리
* USB HID 키보드 입력
* USB HID Consumer Control을 이용한 볼륨 제어
* PC 설정 프로그램과 Serial 통신
* PC에서 설정 변경 후 재부팅

---

## 버튼 동작

각 버튼은 `settings.json`에 저장된 설정에 따라 동작합니다.

### 키 입력

예:

```json
{
    "type": "key",
    "value": ["CONTROL", "C"]
}
```

버튼을 누르면:

```text
Ctrl + C
```

가 입력됩니다.

### 문자 입력

예:

```json
{
    "type": "text",
    "value": "안녕하세요"
}
```

버튼을 누르면:

```text
안녕하세요
```

가 입력됩니다.

---

# 설정 파일

Pico의 `settings.json`을 통해 버튼의 동작을 설정합니다.

예시:

```json
{
    "buttons": [
        {
            "type": "key",
            "value": ["CONTROL", "C"]
        },
        {
            "type": "text",
            "value": "안녕하세요"
        },
        {
            "type": "key",
            "value": ["ALT", "TAB"]
        },
        {
            "type": "text",
            "value": "Hello World"
        }
    ]
}
```

## 설정 구조

각 버튼은 다음 구조를 사용합니다.

```json
{
    "type": "key",
    "value": []
}
```

또는

```json
{
    "type": "text",
    "value": ""
}
```

### `type`

버튼 입력 방식을 지정합니다.

| 값      | 설명           |
| ------ | ------------ |
| `key`  | 키보드 키 또는 단축키 |
| `text` | 문자열 입력       |

### `value`

`type`에 따라 저장되는 데이터가 달라집니다.

#### key

배열 형태로 키를 저장합니다.

```json
"value": ["CONTROL", "C"]
```

```json
"value": ["ALT", "TAB"]
```

```json
"value": ["WINDOWS"]
```

#### text

문자열 형태로 저장합니다.

```json
"value": "Hello World"
```

```json
"value": "안녕하세요"
```

---

# PC 설정 프로그램

`PC/pico_configurator.py`는 Windows에서 실행하는 GUI 설정 프로그램입니다.

Python의 Tkinter를 사용하여 제작되었습니다.

## 주요 기능

### 1. Pico 설정 자동 불러오기

프로그램을 실행하면 먼저 PC에 연결된 Pico의 `CIRCUITPY` 드라이브를 찾습니다.

이후:

```text
CIRCUITPY/settings.json
```

을 읽습니다.

Pico에 저장된 설정을 기준으로 GUI를 구성하기 때문에 프로그램을 실행했을 때 현재 사용 중인 설정을 바로 확인할 수 있습니다.

예를 들어 Pico에 다음 설정이 저장되어 있다면:

```json
{
    "buttons": [
        {
            "type": "key",
            "value": ["CONTROL", "C"]
        },
        {
            "type": "text",
            "value": "안녕하세요"
        }
    ]
}
```

GUI에서도:

```text
Button 1 → 키 입력 → Ctrl + C
Button 2 → 문자 입력 → 안녕하세요
```

로 표시됩니다.

---

## 2. 키 입력 설정

`키 입력` 모드에서 `설정` 버튼을 누르면 키 입력 창이 나타납니다.

사용자가 키 조합을 누르면 프로그램이 해당 키를 감지하여 설정합니다.

예:

```text
Ctrl + C
Alt + Tab
Windows
Ctrl + Shift + S
```

등의 조합을 설정할 수 있습니다.

---

## 3. 문자 입력 설정

`문자 입력` 모드에서는 직접 문자열을 입력할 수 있습니다.

예:

```text
Hello World
```

또는

```text
안녕하세요
```

와 같은 문자열을 설정할 수 있습니다.

---

## 4. 설정 저장

`저장 및 Pico 적용` 버튼을 누르면:

```text
GUI 설정
   ↓
settings.json 저장
   ↓
Pico Serial 연결
   ↓
REBOOT 명령
   ↓
Pico 재부팅
   ↓
새로운 settings.json 적용
```

순서로 설정이 적용됩니다.

---

# PC ↔ Pico 통신

PC 설정 프로그램과 Pico는 USB CDC Serial을 이용하여 통신합니다.

설정 프로그램은 연결된 Serial 포트를 모두 검색한 후 Pico에 다음 명령을 전송합니다.

```text
PING
```

Pico가:

```text
PICO_OK
```

를 반환하면 해당 포트를 Pico의 설정용 Serial 포트로 판단합니다.

---

## Pico 재부팅

설정 적용 시 PC에서:

```text
REBOOT
```

명령을 전송합니다.

Pico는:

```text
REBOOT_OK
```

를 전송한 후:

```python
microcontroller.reset()
```

을 실행하여 재부팅합니다.

---

# 설치

## 1. CircuitPython 설치

Raspberry Pi Pico에 CircuitPython을 설치합니다.

CircuitPython 설치 후 Pico의 `CIRCUITPY` 드라이브에 다음 파일을 복사합니다.

```text
Pico/
├── boot.py
├── code.py
└── settings.json
```

또한 `adafruit_hid` 라이브러리가 필요합니다.

---

## 2. PC 프로그램 설치

Windows에서 Python을 설치한 후 `pyserial`을 설치합니다.

```bash
pip install pyserial
```

Tkinter는 일반적인 Windows Python 설치에 포함되어 있습니다.

---

## 3. 프로그램 실행

프로젝트 폴더에서:

```bash
python PC/pico_configurator.py
```

실행합니다.

Pico가 USB로 연결되어 있으면 프로그램이 자동으로 Pico의 현재 설정을 불러옵니다.

---

# 사용 방법

### 초기 설정

1. Pico를 USB로 PC에 연결
2. `CIRCUITPY` 드라이브가 정상적으로 나타나는지 확인
3. `settings.json`이 Pico에 존재하는지 확인
4. `pico_configurator.py` 실행
5. Pico에 저장된 현재 설정이 GUI에 표시되는지 확인

### 버튼 설정 변경

1. 원하는 버튼의 `키 입력` 또는 `문자 입력` 선택
2. `설정` 버튼 클릭
3. 원하는 키 조합 또는 문자열 입력
4. `저장 및 Pico 적용` 클릭
5. Pico가 자동으로 재부팅됨

재부팅 후 새로운 설정이 적용됩니다.

---

# 설정 예시

다음과 같이 설정하면:

```json
{
    "buttons": [
        {
            "type": "key",
            "value": ["CONTROL", "C"]
        },
        {
            "type": "key",
            "value": ["CONTROL", "V"]
        },
        {
            "type": "key",
            "value": ["ALT", "TAB"]
        },
        {
            "type": "text",
            "value": "Hello World"
        }
    ]
}
```

버튼 동작은 다음과 같습니다.

| 버튼 | GPIO | 동작            |
| -- | ---- | ------------- |
| 1  | GP20 | Ctrl + C      |
| 2  | GP18 | Ctrl + V      |
| 3  | GP1  | Alt + Tab     |
| 4  | GP9  | `Hello World` |

---

# 로터리 엔코더

EC11의 회전 방향에 따라 시스템 볼륨을 조절합니다.

```text
시계 방향
    ↓
Volume Up

반시계 방향
    ↓
Volume Down
```

EC11을 누르면:

```text
Mute Toggle
```

기능을 수행합니다.

---

# 설계 특징

## Pico를 설정 저장 장치로 사용

설정값을 PC 프로그램 내부에 저장하지 않고 Pico의:

```text
settings.json
```

에 저장합니다.

따라서 다른 PC에 Pico를 연결해도 동일한 설정 파일을 사용할 수 있습니다.

---

## GUI는 Pico의 현재 상태를 기준으로 동작

PC 프로그램을 실행했을 때 기본 설정을 무조건 표시하지 않습니다.

먼저 Pico의:

```text
settings.json
```

을 읽고 그 내용을 GUI에 표시합니다.

따라서 사용자는 **현재 Pico에 실제로 저장되어 있는 설정을 확인한 후 변경할 수 있습니다.**

---

# 향후 개선 예정

현재 구조를 기반으로 다음 기능을 추가할 수 있습니다.

* 버튼 개수 확장
* 로터리 엔코더 기능 사용자 설정
* 볼륨 이외의 미디어 키 지원
* 매크로 기능
* 여러 키 입력 순차 실행
* 프로파일 기능
* 게임별 설정
* 프로그램별 자동 프로파일 전환
* GUI 디자인 개선
* 설정 백업 및 복원
* 설정 파일 내보내기 / 가져오기
* 다중 Pico 지원

---

# 기술 스택

### Hardware

* Raspberry Pi Pico
* EC11 Rotary Encoder
* Mechanical Push Button

### Firmware

* CircuitPython
* `digitalio`
* `rotaryio`
* `usb_hid`
* `usb_cdc`
* `adafruit_hid`

### PC Software

* Python
* Tkinter
* PySerial
* JSON

---

# License

개인 프로젝트 및 학습 목적으로 제작되었습니다.

필요에 따라 자유롭게 수정 및 확장할 수 있습니다.
