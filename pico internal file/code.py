import time
import json
import board
import digitalio
import rotaryio
import usb_hid
import usb_cdc
import microcontroller

from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode


# =========================================================
# 기본 설정
# =========================================================

DEFAULT_SETTINGS = {
    "buttons": [
        {
            "type": "key",
            "value": ["WINDOWS"]
        },
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
        }
    ]
}


# =========================================================
# EC11 로터리 인코더
# A = GP21
# B = GP22
# SW = GP10
# =========================================================

encoder = rotaryio.IncrementalEncoder(
    board.GP21,
    board.GP22
)

encoder_button = digitalio.DigitalInOut(board.GP10)
encoder_button.direction = digitalio.Direction.INPUT
encoder_button.pull = digitalio.Pull.UP


# =========================================================
# USB HID
# =========================================================

consumer = ConsumerControl(usb_hid.devices)
keyboard = Keyboard(usb_hid.devices)


# =========================================================
# 버튼 GPIO
# 순서 고정
#
# buttons[0] -> GP20
# buttons[1] -> GP18
# buttons[2] -> GP1
# buttons[3] -> GP9
# =========================================================

button_pins = [
    board.GP20,
    board.GP18,
    board.GP1,
    board.GP9
]

buttons = []

for pin in button_pins:
    button = digitalio.DigitalInOut(pin)
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.UP
    buttons.append(button)


# =========================================================
# settings.json 로드
# =========================================================

def load_settings():

    try:
        with open("/settings.json", "r") as f:
            settings = json.load(f)

        print("settings.json 로드 완료")
        return settings

    except Exception as e:

        print("settings.json 읽기 실패:", e)

        return DEFAULT_SETTINGS


# =========================================================
# 설정 변환
#
# key:
# {
#     "type": "key",
#     "value": ["CONTROL", "C"]
# }
#
# text:
# {
#     "type": "text",
#     "value": "안녕하세요"
# }
# =========================================================

def convert_commands(settings):

    commands = []

    raw_buttons = settings.get("buttons", [])

    for command in raw_buttons:

        if not isinstance(command, dict):
            commands.append({
                "type": "key",
                "value": []
            })
            continue

        command_type = command.get("type", "key")

        # -----------------------------------------
        # 키 입력
        # -----------------------------------------

        if command_type == "key":

            keys = []

            for key_name in command.get("value", []):

                try:

                    key = getattr(Keycode, key_name)
                    keys.append(key)

                except AttributeError:

                    print(
                        "잘못된 Keycode:",
                        key_name
                    )

            commands.append({
                "type": "key",
                "value": keys
            })

        # -----------------------------------------
        # 문자 입력
        # -----------------------------------------

        elif command_type == "text":

            text = command.get("value", "")

            commands.append({
                "type": "text",
                "value": text
            })

        # -----------------------------------------
        # 잘못된 타입
        # -----------------------------------------

        else:

            print(
                "잘못된 command type:",
                command_type
            )

            commands.append({
                "type": "key",
                "value": []
            })


    # 버튼 수 맞추기

    while len(commands) < len(button_pins):

        commands.append({
            "type": "key",
            "value": []
        })


    return commands


settings = load_settings()
key_commands = convert_commands(settings)


# =========================================================
# PC 설정 프로그램 통신
# =========================================================

serial = usb_cdc.data


def check_pc_command():

    if serial is None:
        return

    if not serial.connected:
        return

    if serial.in_waiting:

        try:

            command = (
                serial.readline()
                .decode("utf-8")
                .strip()
            )

            print("PC 명령:", command)

            # -----------------------------------------
            # PC가 이 포트가 data 포트인지 확인
            # -----------------------------------------

            if command == "PING":

                serial.write(
                    b"PICO_OK\n"
                )

                serial.flush()

            # -----------------------------------------
            # PC에서 재부팅 요청
            # -----------------------------------------

            elif command == "REBOOT":

                serial.write(
                    b"REBOOT_OK\n"
                )

                serial.flush()

                time.sleep(0.2)

                microcontroller.reset()

        except Exception as e:

            print(
                "Serial 명령 처리 오류:",
                e
            )


# =========================================================
# Keycode 관련 함수
# =========================================================

def kc(name):

    """
    Keycode 이름을 안전하게 가져온다.
    """

    try:
        return getattr(Keycode, name)

    except AttributeError:
        return None


# =========================================================
# 한글 두벌식 키 매핑
#
# 한글 자모 -> 실제 키보드
# =========================================================

HANGUL_KEYMAP = {

    # 초성 / 자음
    "ㄱ": ("R", False),
    "ㄲ": ("R", True),
    "ㄴ": ("S", False),
    "ㄷ": ("E", False),
    "ㄸ": ("E", True),
    "ㄹ": ("F", False),
    "ㅁ": ("A", False),
    "ㅂ": ("Q", False),
    "ㅃ": ("Q", True),
    "ㅅ": ("T", False),
    "ㅆ": ("T", True),
    "ㅇ": ("D", False),
    "ㅈ": ("W", False),
    "ㅉ": ("W", True),
    "ㅊ": ("C", False),
    "ㅋ": ("Z", False),
    "ㅌ": ("X", False),
    "ㅍ": ("V", False),
    "ㅎ": ("G", False),

    # 모음
    "ㅏ": ("K", False),
    "ㅐ": ("O", False),
    "ㅑ": ("I", False),
    "ㅒ": ("O", True),
    "ㅓ": ("J", False),
    "ㅔ": ("P", False),
    "ㅕ": ("U", False),
    "ㅖ": ("P", True),
    "ㅗ": ("H", False),
    "ㅘ": None,
    "ㅙ": None,
    "ㅚ": None,
    "ㅛ": ("Y", False),
    "ㅜ": ("N", False),
    "ㅝ": None,
    "ㅞ": None,
    "ㅟ": None,
    "ㅠ": ("B", False),
    "ㅡ": ("M", False),
    "ㅢ": None,
    "ㅣ": ("L", False),
}


# =========================================================
# 한글 음절 분해
#
# 예:
#
# 안
# ↓
# ㅇ + ㅏ + ㄴ
#
# 한
# ↓
# ㅎ + ㅏ + ㄴ
# =========================================================

CHO = [
    "ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ",
    "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ",
    "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ",
    "ㅋ", "ㅌ", "ㅍ", "ㅎ"
]

JUNG = [
    "ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ",
    "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ",
    "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ",
    "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ",
    "ㅣ"
]

JONG = [
    "",
    "ㄱ", "ㄲ", "ㄳ", "ㄴ",
    "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ",
    "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ",
    "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ",
    "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ",
    "ㅌ", "ㅍ", "ㅎ"
]


def decompose_hangul(char):

    code = ord(char)

    # 한글 음절 범위
    if 0xAC00 <= code <= 0xD7A3:

        index = code - 0xAC00

        cho_index = index // 588

        jung_index = (
            (index % 588) // 28
        )

        jong_index = index % 28

        result = [
            CHO[cho_index],
            JUNG[jung_index]
        ]

        if jong_index != 0:
            result.append(
                JONG[jong_index]
            )

        return result

    return None


# =========================================================
# 복합 모음 / 복합 받침 분해
# =========================================================

COMPLEX_JUNG = {

    "ㅘ": ["ㅗ", "ㅏ"],
    "ㅙ": ["ㅗ", "ㅐ"],
    "ㅚ": ["ㅗ", "ㅣ"],

    "ㅝ": ["ㅜ", "ㅓ"],
    "ㅞ": ["ㅜ", "ㅔ"],
    "ㅟ": ["ㅜ", "ㅣ"],

    "ㅢ": ["ㅡ", "ㅣ"]
}


COMPLEX_JONG = {

    "ㄳ": ["ㄱ", "ㅅ"],
    "ㄵ": ["ㄴ", "ㅈ"],
    "ㄶ": ["ㄴ", "ㅎ"],
    "ㄺ": ["ㄹ", "ㄱ"],
    "ㄻ": ["ㄹ", "ㅁ"],
    "ㄼ": ["ㄹ", "ㅂ"],
    "ㄽ": ["ㄹ", "ㅅ"],
    "ㄾ": ["ㄹ", "ㅌ"],
    "ㄿ": ["ㄹ", "ㅍ"],
    "ㅀ": ["ㄹ", "ㅎ"],
    "ㅄ": ["ㅂ", "ㅅ"]
}


def expand_jamo(jamo):

    if jamo in COMPLEX_JUNG:
        return COMPLEX_JUNG[jamo]

    if jamo in COMPLEX_JONG:
        return COMPLEX_JONG[jamo]

    return [jamo]


# =========================================================
# Shift가 필요한 문자 입력
# =========================================================

def press_key_with_shift(key):

    if key is None:
        return

    keyboard.press(
        Keycode.SHIFT,
        key
    )

    keyboard.release_all()

    time.sleep(0.005)


# =========================================================
# 한글 자모 하나 입력
# =========================================================

def type_hangul_jamo(jamo):

    mapping = HANGUL_KEYMAP.get(jamo)

    if mapping is None:
        return

    key_name, use_shift = mapping

    key = kc(key_name)

    if key is None:
        return

    if use_shift:

        press_key_with_shift(key)

    else:

        keyboard.press(key)
        keyboard.release_all()

    time.sleep(0.005)


# =========================================================
# 한글 문자열 입력
# =========================================================

def type_hangul(text):

    for char in text:

        decomposed = decompose_hangul(char)

        if decomposed is not None:

            for jamo in decomposed:

                for expanded in expand_jamo(jamo):

                    type_hangul_jamo(expanded)

        else:

            # 한글 음절이 아닌 경우
            type_ascii_char(char)


# =========================================================
# ASCII 문자 -> Keycode
# =========================================================

ASCII_KEYMAP = {

    "a": ("A", False),
    "b": ("B", False),
    "c": ("C", False),
    "d": ("D", False),
    "e": ("E", False),
    "f": ("F", False),
    "g": ("G", False),
    "h": ("H", False),
    "i": ("I", False),
    "j": ("J", False),
    "k": ("K", False),
    "l": ("L", False),
    "m": ("M", False),
    "n": ("N", False),
    "o": ("O", False),
    "p": ("P", False),
    "q": ("Q", False),
    "r": ("R", False),
    "s": ("S", False),
    "t": ("T", False),
    "u": ("U", False),
    "v": ("V", False),
    "w": ("W", False),
    "x": ("X", False),
    "y": ("Y", False),
    "z": ("Z", False),

    "A": ("A", True),
    "B": ("B", True),
    "C": ("C", True),
    "D": ("D", True),
    "E": ("E", True),
    "F": ("F", True),
    "G": ("G", True),
    "H": ("H", True),
    "I": ("I", True),
    "J": ("J", True),
    "K": ("K", True),
    "L": ("L", True),
    "M": ("M", True),
    "N": ("N", True),
    "O": ("O", True),
    "P": ("P", True),
    "Q": ("Q", True),
    "R": ("R", True),
    "S": ("S", True),
    "T": ("T", True),
    "U": ("U", True),
    "V": ("V", True),
    "W": ("W", True),
    "X": ("X", True),
    "Y": ("Y", True),
    "Z": ("Z", True),

    "1": ("ONE", False),
    "2": ("TWO", False),
    "3": ("THREE", False),
    "4": ("FOUR", False),
    "5": ("FIVE", False),
    "6": ("SIX", False),
    "7": ("SEVEN", False),
    "8": ("EIGHT", False),
    "9": ("NINE", False),
    "0": ("ZERO", False),

    " ": ("SPACE", False),

    "\n": ("ENTER", False),
    "\r": ("ENTER", False),

    "\t": ("TAB", False),

    "-": ("MINUS", False),
    "_": ("MINUS", True),

    "=": ("EQUALS", False),
    "+": ("EQUALS", True),

    "[": ("LEFT_BRACKET", False),
    "{": ("LEFT_BRACKET", True),

    "]": ("RIGHT_BRACKET", False),
    "}": ("RIGHT_BRACKET", True),

    "\\": ("BACKSLASH", False),
    "|": ("BACKSLASH", True),

    ";": ("SEMICOLON", False),
    ":": ("SEMICOLON", True),

    "'": ("QUOTE", False),
    '"': ("QUOTE", True),

    ",": ("COMMA", False),
    "<": ("COMMA", True),

    ".": ("PERIOD", False),
    ">": ("PERIOD", True),

    "/": ("FORWARD_SLASH", False),
    "?": ("FORWARD_SLASH", True),

    "`": ("GRAVE_ACCENT", False),
    "~": ("GRAVE_ACCENT", True),

    "!": ("ONE", True),
    "@": ("TWO", True),
    "#": ("THREE", True),
    "$": ("FOUR", True),
    "%": ("FIVE", True),
    "^": ("SIX", True),
    "&": ("SEVEN", True),
    "*": ("EIGHT", True),
    "(": ("NINE", True),
    ")": ("ZERO", True),
}


def type_ascii_char(char):

    mapping = ASCII_KEYMAP.get(char)

    if mapping is None:
        return False

    key_name, use_shift = mapping

    key = kc(key_name)

    if key is None:
        return False

    if use_shift:

        keyboard.press(
            Keycode.SHIFT,
            key
        )

        keyboard.release_all()

    else:

        keyboard.press(key)
        keyboard.release_all()

    time.sleep(0.005)

    return True


# =========================================================
# 문자 입력
# =========================================================

def type_text(text):

    if not text:
        return

    # -----------------------------------------------------
    # 한글이 포함되어 있는지 확인
    # -----------------------------------------------------

    has_hangul = False

    for char in text:

        if (
            0xAC00 <= ord(char) <= 0xD7A3
        ):

            has_hangul = True
            break


    # -----------------------------------------------------
    # 한글이 있으면 한글 입력 모드로 전환
    #
    # LANG1 = 한/영 키
    # -----------------------------------------------------

    if has_hangul:

        hangul_key = kc("LANG1")

        if hangul_key is not None:

            keyboard.press(hangul_key)
            keyboard.release_all()

            time.sleep(0.05)


    # -----------------------------------------------------
    # 문자 입력
    # -----------------------------------------------------

    for char in text:

        # 한글
        if (
            0xAC00 <= ord(char) <= 0xD7A3
        ):

            decomposed = decompose_hangul(char)

            if decomposed:

                for jamo in decomposed:

                    expanded = expand_jamo(jamo)

                    for item in expanded:

                        type_hangul_jamo(item)

        # ASCII
        else:

            type_ascii_char(char)


    # -----------------------------------------------------
    # 한글 입력 모드 종료
    # -----------------------------------------------------

    if has_hangul:

        hangul_key = kc("LANG1")

        if hangul_key is not None:

            keyboard.press(hangul_key)
            keyboard.release_all()

            time.sleep(0.05)


# =========================================================
# 버튼 명령 실행
# =========================================================

def execute_button_command(command):

    if not command:
        return


    command_type = command.get("type")


    # =====================================================
    # KEY
    # =====================================================

    if command_type == "key":

        keys = command.get(
            "value",
            []
        )

        if keys:

            keyboard.press(*keys)

            keyboard.release_all()


    # =====================================================
    # TEXT
    # =====================================================

    elif command_type == "text":

        text = command.get(
            "value",
            ""
        )

        type_text(text)


# =========================================================
# 초기 상태
# =========================================================

last_encoder_position = encoder.position

last_encoder_button = encoder_button.value

last_button_states = []

for button in buttons:
    last_button_states.append(
        button.value
    )


# =========================================================
# 메인 루프
# =========================================================

print("================================")
print("Pico Controller 시작")
print("================================")

while True:

    # -----------------------------------------------------
    # PC 설정 명령 확인
    # -----------------------------------------------------

    check_pc_command()


    # -----------------------------------------------------
    # EC11
    # -----------------------------------------------------

    current_position = encoder.position

    difference = (
        current_position
        - last_encoder_position
    )

    if difference != 0:

        if difference > 0:

            consumer.send(
                ConsumerControlCode.VOLUME_INCREMENT
            )

        else:

            consumer.send(
                ConsumerControlCode.VOLUME_DECREMENT
            )

        last_encoder_position = current_position


    # -----------------------------------------------------
    # EC11 버튼
    # -----------------------------------------------------

    current_encoder_button = (
        encoder_button.value
    )

    # 눌림
    if (
        last_encoder_button
        and not current_encoder_button
    ):

        consumer.send(
            ConsumerControlCode.MUTE
        )

    last_encoder_button = current_encoder_button


    # -----------------------------------------------------
    # 4개 버튼
    # -----------------------------------------------------

    for i, button in enumerate(buttons):

        current_state = button.value
        last_state = last_button_states[i]

        # 버튼 눌림
        if (
            last_state
            and not current_state
        ):

            print(
                "버튼",
                i,
                "실행:",
                key_commands[i]
            )

            execute_button_command(
                key_commands[i]
            )

        last_button_states[i] = current_state


    # -----------------------------------------------------
    # 짧은 대기
    # -----------------------------------------------------

    time.sleep(0.001)