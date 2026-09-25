import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import json
import time

import serial
import serial.tools.list_ports


# ============================================================
# 고정 GPIO
# ============================================================

BUTTON_PINS = [
    "GP20",
    "GP18",
    "GP1",
    "GP9"
]


# ============================================================
# Pico를 찾지 못했을 때만 사용하는 기본값
# ============================================================

DEFAULT_SETTINGS = {
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
            "type": "key",
            "value": ["WINDOWS"]
        }
    ]
}


# ============================================================
# 키 이름 변환
# ============================================================

KEY_MAP = {

    # 알파벳
    "a": "A",
    "b": "B",
    "c": "C",
    "d": "D",
    "e": "E",
    "f": "F",
    "g": "G",
    "h": "H",
    "i": "I",
    "j": "J",
    "k": "K",
    "l": "L",
    "m": "M",
    "n": "N",
    "o": "O",
    "p": "P",
    "q": "Q",
    "r": "R",
    "s": "S",
    "t": "T",
    "u": "U",
    "v": "V",
    "w": "W",
    "x": "X",
    "y": "Y",
    "z": "Z",

    # 숫자
    "0": "ZERO",
    "1": "ONE",
    "2": "TWO",
    "3": "THREE",
    "4": "FOUR",
    "5": "FIVE",
    "6": "SIX",
    "7": "SEVEN",
    "8": "EIGHT",
    "9": "NINE",

    # 기능키
    "f1": "F1",
    "f2": "F2",
    "f3": "F3",
    "f4": "F4",
    "f5": "F5",
    "f6": "F6",
    "f7": "F7",
    "f8": "F8",
    "f9": "F9",
    "f10": "F10",
    "f11": "F11",
    "f12": "F12",

    # 특수키
    "space": "SPACE",
    "return": "ENTER",
    "enter": "ENTER",
    "escape": "ESCAPE",
    "esc": "ESCAPE",
    "tab": "TAB",
    "backspace": "BACKSPACE",
    "delete": "DELETE",
    "insert": "INSERT",

    "home": "HOME",
    "end": "END",

    "prior": "PAGE_UP",
    "next": "PAGE_DOWN",

    # 방향키
    "left": "LEFT_ARROW",
    "right": "RIGHT_ARROW",
    "up": "UP_ARROW",
    "down": "DOWN_ARROW",

    # 조합키
    "control_l": "CONTROL",
    "control_r": "CONTROL",

    "shift_l": "SHIFT",
    "shift_r": "SHIFT",

    "alt_l": "ALT",
    "alt_r": "ALT",

    "win_l": "WINDOWS",
    "win_r": "WINDOWS",

    # 기타
    "caps_lock": "CAPS_LOCK",
    "num_lock": "NUM_LOCK",
    "print": "PRINT_SCREEN",
    "scroll_lock": "SCROLL_LOCK",
    "pause": "PAUSE",
    "menu": "MENU"
}


# ============================================================
# 화면 표시용 이름
# ============================================================

DISPLAY_NAMES = {

    "CONTROL": "Ctrl",
    "SHIFT": "Shift",
    "ALT": "Alt",
    "WINDOWS": "Windows",

    "ENTER": "Enter",
    "ESCAPE": "Esc",
    "TAB": "Tab",
    "SPACE": "Space",

    "BACKSPACE": "Backspace",
    "DELETE": "Delete",
    "INSERT": "Insert",

    "HOME": "Home",
    "END": "End",

    "PAGE_UP": "Page Up",
    "PAGE_DOWN": "Page Down",

    "LEFT_ARROW": "←",
    "RIGHT_ARROW": "→",
    "UP_ARROW": "↑",
    "DOWN_ARROW": "↓",

    "CAPS_LOCK": "Caps Lock",
    "NUM_LOCK": "Num Lock",
    "PRINT_SCREEN": "Print Screen",
    "SCROLL_LOCK": "Scroll Lock",
    "PAUSE": "Pause",
    "MENU": "Menu"
}


# ============================================================
# 깊은 복사
# ============================================================

def deep_copy(data):

    return json.loads(
        json.dumps(
            data,
            ensure_ascii=False
        )
    )


# ============================================================
# Pico(CIRCUITPY) 드라이브 찾기
# ============================================================

def find_pico_drive():

    print("\n========== Pico 드라이브 검색 ==========")

    # --------------------------------------------------------
    # 1. boot_out.txt를 이용해서 찾기
    # --------------------------------------------------------

    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":

        drive = Path(f"{letter}:/")

        if not drive.exists():
            continue

        boot_out = drive / "boot_out.txt"

        if not boot_out.exists():
            continue

        try:

            content = boot_out.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            upper_content = content.upper()

            print(
                f"{drive} boot_out.txt 발견"
            )

            if (
                "CIRCUITPY" in upper_content
                or
                "RASPBERRY PI PICO" in upper_content
                or
                "CIRCUITPYTHON" in upper_content
            ):

                print(
                    f"-> Pico 발견: {drive}"
                )

                return drive

        except Exception as e:

            print(
                f"{drive} boot_out.txt 읽기 실패:",
                e
            )


    # --------------------------------------------------------
    # 2. boot_out.txt로 못 찾았을 경우
    #    settings.json이 있는 드라이브 검색
    # --------------------------------------------------------

    print(
        "boot_out.txt로 Pico를 찾지 못했습니다."
    )

    print(
        "settings.json 검색 중..."
    )


    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":

        drive = Path(f"{letter}:/")

        if not drive.exists():
            continue

        settings_file = drive / "settings.json"

        if settings_file.exists():

            print(
                f"-> settings.json 발견: {drive}"
            )

            return drive


    print(
        "Pico 드라이브를 찾지 못했습니다."
    )

    return None


# ============================================================
# Serial 포트 전체 검색
# ============================================================

def get_all_serial_ports():

    ports = []

    try:

        for port in serial.tools.list_ports.comports():

            ports.append(
                port.device
            )

    except Exception as e:

        print(
            "Serial 포트 검색 오류:",
            e
        )


    return ports


# ============================================================
# 메인 GUI
# ============================================================

class PicoConfigurator:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "Raspberry Pi Pico Configurator"
        )

        self.root.geometry(
            "720x650"
        )

        self.root.resizable(
            False,
            False
        )


        # ----------------------------------------------------
        # GUI 객체
        # ----------------------------------------------------

        self.mode_vars = []

        self.value_labels = []


        # ----------------------------------------------------
        # 키 캡처 관련
        # ----------------------------------------------------

        self.capturing = False

        self.capture_index = None

        self.pressed_keys = set()

        self.captured_keys = []


        # ----------------------------------------------------
        # 처음에는 빈 설정
        #
        # 여기서 DEFAULT_SETTINGS를 GUI에 표시하지 않는다.
        #
        # 먼저 Pico의 JSON을 읽는다.
        # ----------------------------------------------------

        self.settings = {
            "buttons": [
                {
                    "type": "key",
                    "value": []
                }
                for _ in BUTTON_PINS
            ]
        }


        # ----------------------------------------------------
        # GUI 생성
        # ----------------------------------------------------

        self.create_gui()


        # ----------------------------------------------------
        # ★ 가장 중요
        #
        # GUI 생성 직후 Pico의 settings.json을 읽는다.
        # ----------------------------------------------------

        self.load_settings_from_pico()


        # ----------------------------------------------------
        # 읽어온 JSON을 화면에 반영
        # ----------------------------------------------------

        self.refresh_all_displays()


    # ========================================================
    # GUI 생성
    # ========================================================

    def create_gui(self):

        title = tk.Label(
            self.root,
            text="Raspberry Pi Pico Configurator",
            font=("Arial", 18, "bold")
        )

        title.pack(
            pady=(15, 5)
        )


        description = tk.Label(
            self.root,
            text="Pico에 현재 저장되어 있는 설정을 표시합니다."
        )

        description.pack(
            pady=(0, 15)
        )


        # ----------------------------------------------------
        # 버튼 설정
        # ----------------------------------------------------

        for i, pin in enumerate(BUTTON_PINS):

            frame = tk.LabelFrame(
                self.root,
                text=f"버튼 {i + 1}  ({pin})",
                padx=10,
                pady=10
            )

            frame.pack(
                fill="x",
                padx=20,
                pady=5
            )


            # ------------------------------------------------
            # 모드
            # ------------------------------------------------

            mode_var = tk.StringVar(
                value="key"
            )

            self.mode_vars.append(
                mode_var
            )


            # ------------------------------------------------
            # 키 입력
            # ------------------------------------------------

            key_radio = tk.Radiobutton(
                frame,
                text="키 입력",
                variable=mode_var,
                value="key",
                command=lambda index=i:
                    self.on_mode_changed(index)
            )

            key_radio.grid(
                row=0,
                column=0,
                padx=5
            )


            # ------------------------------------------------
            # 문자 입력
            # ------------------------------------------------

            text_radio = tk.Radiobutton(
                frame,
                text="문자 입력",
                variable=mode_var,
                value="text",
                command=lambda index=i:
                    self.on_mode_changed(index)
            )

            text_radio.grid(
                row=0,
                column=1,
                padx=5
            )


            # ------------------------------------------------
            # 현재 설정값
            # ------------------------------------------------

            value_label = tk.Label(
                frame,
                text="불러오는 중...",
                width=38,
                anchor="w",
                relief="sunken"
            )

            value_label.grid(
                row=0,
                column=2,
                padx=10
            )


            self.value_labels.append(
                value_label
            )


            # ------------------------------------------------
            # 설정 버튼
            # ------------------------------------------------

            setting_button = tk.Button(
                frame,
                text="설정",
                width=8,
                command=lambda index=i:
                    self.open_setting_dialog(index)
            )

            setting_button.grid(
                row=0,
                column=3,
                padx=5
            )


        # ----------------------------------------------------
        # 상태
        # ----------------------------------------------------

        self.status_label = tk.Label(
            self.root,
            text="Pico 설정을 불러오는 중...",
            anchor="w"
        )

        self.status_label.pack(
            fill="x",
            padx=25,
            pady=(15, 5)
        )


        # ----------------------------------------------------
        # JSON 확인 버튼
        # ----------------------------------------------------

        show_json_button = tk.Button(
            self.root,
            text="현재 설정 JSON 확인",
            width=22,
            command=self.show_current_json
        )

        show_json_button.pack(
            pady=5
        )


        # ----------------------------------------------------
        # 저장 및 적용
        # ----------------------------------------------------

        save_button = tk.Button(
            self.root,
            text="저장 및 Pico 적용",
            font=("Arial", 12, "bold"),
            width=25,
            height=2,
            command=self.save_and_apply
        )

        save_button.pack(
            pady=10
        )


    # ========================================================
    # ★ Pico JSON 읽기
    # ========================================================

    def load_settings_from_pico(self):

        print("\n========================================")
        print("Pico 설정 불러오기 시작")
        print("========================================")


        drive = find_pico_drive()


        if drive is None:

            print(
                "Pico 드라이브를 찾지 못했습니다."
            )


            # Pico가 정말 없는 경우에만 기본값 사용
            self.settings = deep_copy(
                DEFAULT_SETTINGS
            )


            self.status_label.config(
                text="Pico를 찾지 못했습니다. 기본 설정을 표시합니다."
            )


            return False


        settings_file = (
            drive / "settings.json"
        )


        print(
            "읽을 설정 파일:",
            settings_file
        )


        # ----------------------------------------------------
        # settings.json 존재 여부
        # ----------------------------------------------------

        if not settings_file.exists():

            print(
                "Pico에 settings.json이 없습니다."
            )


            self.settings = deep_copy(
                DEFAULT_SETTINGS
            )


            self.status_label.config(
                text="Pico에 settings.json이 없습니다. 기본 설정을 표시합니다."
            )


            return False


        # ----------------------------------------------------
        # JSON 읽기
        # ----------------------------------------------------

        try:

            with open(
                settings_file,
                "r",
                encoding="utf-8"
            ) as f:

                pico_settings = json.load(f)


            print(
                "\n----- Pico에서 읽은 JSON -----"
            )

            print(
                json.dumps(
                    pico_settings,
                    ensure_ascii=False,
                    indent=4
                )
            )

            print(
                "-------------------------------"
            )


            # ------------------------------------------------
            # JSON 구조 검사
            # ------------------------------------------------

            if not isinstance(
                pico_settings,
                dict
            ):

                raise ValueError(
                    "settings.json의 최상위 구조가 객체가 아닙니다."
                )


            if "buttons" not in pico_settings:

                raise ValueError(
                    "settings.json에 buttons가 없습니다."
                )


            if not isinstance(
                pico_settings["buttons"],
                list
            ):

                raise ValueError(
                    "buttons가 배열이 아닙니다."
                )


            # ------------------------------------------------
            # 기존 형식까지 변환
            # ------------------------------------------------

            pico_settings = self.convert_settings(
                pico_settings
            )


            # ------------------------------------------------
            # ★ 여기서 Pico JSON을 그대로 현재 설정으로 사용
            # ------------------------------------------------

            self.settings = pico_settings


            # ------------------------------------------------
            # GUI 모드에 Pico JSON 반영
            # ------------------------------------------------

            for i in range(
                len(BUTTON_PINS)
            ):

                command = (
                    self.settings["buttons"][i]
                )


                command_type = command.get(
                    "type",
                    "key"
                )


                if command_type not in (
                    "key",
                    "text"
                ):

                    command_type = "key"


                self.mode_vars[i].set(
                    command_type
                )


            # ------------------------------------------------
            # 상태
            # ------------------------------------------------

            self.status_label.config(
                text=f"Pico 설정 불러오기 완료: {settings_file}"
            )


            print(
                "\nPico 설정을 GUI에 반영했습니다."
            )


            return True


        except Exception as e:

            print(
                "\nPico settings.json 읽기 실패:"
            )

            print(
                repr(e)
            )


            messagebox.showerror(
                "설정 읽기 오류",
                "Pico의 settings.json을 읽지 못했습니다.\n\n"
                f"{e}"
            )


            # ------------------------------------------------
            # JSON을 읽지 못한 경우
            #
            # 여기서도 바로 기본값으로 덮어쓰지 않는다.
            # 사용자가 확인할 수 있도록 빈 상태 유지.
            # ------------------------------------------------

            self.status_label.config(
                text="Pico의 settings.json을 읽지 못했습니다."
            )


            return False


    # ========================================================
    # JSON 형식 변환
    # ========================================================

    def convert_settings(self, settings):

        converted_buttons = []


        source_buttons = settings.get(
            "buttons",
            []
        )


        for button in source_buttons:

            # ------------------------------------------------
            # 새로운 형식
            #
            # {
            #   "type": "key",
            #   "value": [...]
            # }
            # ------------------------------------------------

            if isinstance(
                button,
                dict
            ):

                button_type = button.get(
                    "type",
                    "key"
                )

                value = button.get(
                    "value"
                )


                if button_type == "text":

                    if not isinstance(
                        value,
                        str
                    ):

                        value = ""


                    converted_buttons.append({

                        "type": "text",

                        "value": value
                    })


                else:

                    if not isinstance(
                        value,
                        list
                    ):

                        value = []


                    converted_buttons.append({

                        "type": "key",

                        "value": value
                    })


            # ------------------------------------------------
            # 예전 형식
            #
            # ["CONTROL", "C"]
            # ------------------------------------------------

            elif isinstance(
                button,
                list
            ):

                converted_buttons.append({

                    "type": "key",

                    "value": button
                })


            else:

                converted_buttons.append({

                    "type": "key",

                    "value": []
                })


        # ----------------------------------------------------
        # 버튼이 4개보다 적으면 빈 버튼 추가
        # ----------------------------------------------------

        while len(converted_buttons) < len(BUTTON_PINS):

            converted_buttons.append({

                "type": "key",

                "value": []
            })


        # ----------------------------------------------------
        # 버튼이 4개보다 많으면 앞의 4개만 사용
        # ----------------------------------------------------

        converted_buttons = converted_buttons[
            :len(BUTTON_PINS)
        ]


        return {
            "buttons": converted_buttons
        }


    # ========================================================
    # 모드 변경
    # ========================================================

    def on_mode_changed(
        self,
        index
    ):

        new_mode = (
            self.mode_vars[index].get()
        )


        # ----------------------------------------------------
        # 중요:
        #
        # 여기서는 JSON의 value를 변경하지 않는다.
        #
        # 단순히 GUI에서 현재 선택한 모드만 변경한다.
        # ----------------------------------------------------

        print(
            f"버튼 {index + 1} GUI 모드 변경:",
            new_mode
        )


        self.refresh_display(
            index
        )


    # ========================================================
    # 설정 창
    # ========================================================

    def open_setting_dialog(
        self,
        index
    ):

        mode = (
            self.mode_vars[index].get()
        )


        if mode == "key":

            self.open_key_dialog(
                index
            )

        else:

            self.open_text_dialog(
                index
            )


    # ========================================================
    # 키 설정 창
    # ========================================================

    def open_key_dialog(
        self,
        index
    ):

        dialog = tk.Toplevel(
            self.root
        )

        dialog.title(
            f"버튼 {index + 1} 키 설정"
        )

        dialog.geometry(
            "420x260"
        )

        dialog.transient(
            self.root
        )

        dialog.grab_set()


        tk.Label(
            dialog,
            text="원하는 키 조합을 눌러주세요.",
            font=("Arial", 12)
        ).pack(
            pady=20
        )


        # ----------------------------------------------------
        # 현재 Pico/GUI 설정값 표시
        # ----------------------------------------------------

        current = (
            self.settings["buttons"][index]
            .get(
                "value",
                []
            )
        )


        current_label = tk.Label(
            dialog,
            text=self.format_key_command(
                current
            ),
            font=("Arial", 14),
            relief="sunken",
            width=28
        )

        current_label.pack(
            pady=10
        )


        self.capture_index = index

        self.captured_keys = []

        self.pressed_keys = set()


        # ----------------------------------------------------
        # 키 입력 시작
        # ----------------------------------------------------

        def start_capture():

            self.capturing = True

            self.captured_keys = []

            self.pressed_keys = set()


            current_label.config(
                text="키를 누르세요..."
            )


            dialog.bind(
                "<KeyPress>",
                lambda event:
                    self.on_key_press(
                        event,
                        current_label
                    )
            )


            dialog.bind(
                "<KeyRelease>",
                lambda event:
                    self.on_key_release(
                        event,
                        current_label,
                        dialog
                    )
            )


            dialog.focus_force()


        # ----------------------------------------------------
        # 취소
        # ----------------------------------------------------

        def cancel():

            self.capturing = False

            self.capture_index = None

            dialog.destroy()


        tk.Button(
            dialog,
            text="키 입력 시작",
            width=15,
            command=start_capture
        ).pack(
            pady=10
        )


        tk.Button(
            dialog,
            text="취소",
            width=15,
            command=cancel
        ).pack(
            pady=5
        )


    # ========================================================
    # 키 누름
    # ========================================================

    def on_key_press(
        self,
        event,
        label
    ):

        if not self.capturing:
            return


        key_name = KEY_MAP.get(
            event.keysym.lower()
        )


        if key_name is None:
            return


        if key_name not in self.pressed_keys:

            self.pressed_keys.add(
                key_name
            )

            self.captured_keys.append(
                key_name
            )


            label.config(
                text=self.format_key_command(
                    self.captured_keys
                )
            )


    # ========================================================
    # 키 떼기
    # ========================================================

    def on_key_release(
        self,
        event,
        label,
        dialog
    ):

        if not self.capturing:
            return


        key_name = KEY_MAP.get(
            event.keysym.lower()
        )


        if key_name is not None:

            self.pressed_keys.discard(
                key_name
            )


        if (
            len(self.captured_keys) > 0
            and
            len(self.pressed_keys) == 0
        ):

            self.finish_key_capture(
                self.capture_index,
                dialog
            )


    # ========================================================
    # 키 설정 완료
    # ========================================================

    def finish_key_capture(
        self,
        index,
        dialog
    ):

        self.capturing = False


        if not self.captured_keys:

            return


        # ----------------------------------------------------
        # 실제 GUI 설정 변경
        # ----------------------------------------------------

        self.settings["buttons"][index] = {

            "type": "key",

            "value": list(
                self.captured_keys
            )
        }


        self.mode_vars[index].set(
            "key"
        )


        self.refresh_display(
            index
        )


        self.capture_index = None

        self.captured_keys = []

        self.pressed_keys = set()


        dialog.destroy()


    # ========================================================
    # 문자 설정 창
    # ========================================================

    def open_text_dialog(
        self,
        index
    ):

        dialog = tk.Toplevel(
            self.root
        )

        dialog.title(
            f"버튼 {index + 1} 문자 설정"
        )

        dialog.geometry(
            "480x320"
        )

        dialog.transient(
            self.root
        )

        dialog.grab_set()


        tk.Label(
            dialog,
            text="버튼을 눌렀을 때 입력할 문자를 작성하세요.",
            font=("Arial", 12)
        ).pack(
            pady=10
        )


        text_box = tk.Text(
            dialog,
            width=50,
            height=9
        )

        text_box.pack(
            padx=15,
            pady=10
        )


        # ----------------------------------------------------
        # ★ 현재 Pico에 저장되어 있던 문자 표시
        # ----------------------------------------------------

        current_command = (
            self.settings["buttons"][index]
        )


        if (
            current_command.get("type")
            == "text"
        ):

            current_value = (
                current_command.get(
                    "value",
                    ""
                )
            )


            if isinstance(
                current_value,
                str
            ):

                text_box.insert(
                    "1.0",
                    current_value
                )


        # ----------------------------------------------------
        # 저장
        # ----------------------------------------------------

        def save_text():

            value = text_box.get(
                "1.0",
                "end-1c"
            )


            self.settings["buttons"][index] = {

                "type": "text",

                "value": value
            }


            self.mode_vars[index].set(
                "text"
            )


            self.refresh_display(
                index
            )


            dialog.destroy()


        button_frame = tk.Frame(
            dialog
        )

        button_frame.pack(
            pady=10
        )


        tk.Button(
            button_frame,
            text="저장",
            width=12,
            command=save_text
        ).pack(
            side="left",
            padx=5
        )


        tk.Button(
            button_frame,
            text="취소",
            width=12,
            command=dialog.destroy
        ).pack(
            side="left",
            padx=5
        )


        text_box.focus_set()


    # ========================================================
    # 키 표시
    # ========================================================

    def format_key_command(
        self,
        keys
    ):

        if not keys:

            return "설정되지 않음"


        names = []


        for key in keys:

            names.append(
                DISPLAY_NAMES.get(
                    key,
                    key
                )
            )


        return " + ".join(
            names
        )


    # ========================================================
    # 현재 설정 표시
    # ========================================================

    def refresh_display(
        self,
        index
    ):

        # ----------------------------------------------------
        # 현재 GUI에서 선택한 모드
        # ----------------------------------------------------

        mode = (
            self.mode_vars[index].get()
        )


        command = (
            self.settings["buttons"][index]
        )


        # ----------------------------------------------------
        # 키 입력 모드
        # ----------------------------------------------------

        if mode == "key":

            # 실제 설정이 key라면 그 값을 표시
            if command.get("type") == "key":

                value = command.get(
                    "value",
                    []
                )

                display = self.format_key_command(
                    value
                )

            else:

                # 다른 타입이라면
                # 현재 저장된 값이 없다는 의미
                display = "설정되지 않음"


        # ----------------------------------------------------
        # 문자 입력 모드
        # ----------------------------------------------------

        else:

            if command.get("type") == "text":

                value = command.get(
                    "value",
                    ""
                )


                if value:

                    display = value.replace(
                        "\n",
                        " ↵ "
                    )


                    if len(display) > 35:

                        display = (
                            display[:32]
                            + "..."
                        )

                else:

                    display = "설정되지 않음"

            else:

                display = "설정되지 않음"


        self.value_labels[index].config(
            text=display
        )


    # ========================================================
    # 전체 표시 갱신
    # ========================================================

    def refresh_all_displays(self):

        for i in range(
            len(BUTTON_PINS)
        ):

            self.refresh_display(
                i
            )


    # ========================================================
    # 현재 JSON 보기
    # ========================================================

    def show_current_json(self):

        dialog = tk.Toplevel(
            self.root
        )

        dialog.title(
            "현재 설정 JSON"
        )

        dialog.geometry(
            "600x500"
        )


        text = tk.Text(
            dialog,
            wrap="none",
            font=("Consolas", 10)
        )

        text.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )


        json_text = json.dumps(
            self.settings,
            ensure_ascii=False,
            indent=4
        )


        text.insert(
            "1.0",
            json_text
        )


        text.config(
            state="disabled"
        )


    # ========================================================
    # JSON 저장
    # ========================================================

    def save_settings(self):

        drive = find_pico_drive()


        if drive is None:

            messagebox.showerror(
                "오류",
                "CIRCUITPY 드라이브를 찾을 수 없습니다."
            )

            return False


        settings_file = (
            drive / "settings.json"
        )


        try:

            with open(
                settings_file,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    self.settings,
                    f,
                    ensure_ascii=False,
                    indent=4
                )


                f.flush()


            print(
                "\n========== JSON 저장 =========="
            )

            print(
                json.dumps(
                    self.settings,
                    ensure_ascii=False,
                    indent=4
                )
            )


            time.sleep(
                0.5
            )


            return True


        except Exception as e:

            messagebox.showerror(
                "저장 오류",
                f"settings.json 저장 실패:\n\n{e}"
            )

            return False


    # ========================================================
    # Pico Serial 찾기
    # ========================================================

    def find_pico_serial(self):

        ports = get_all_serial_ports()


        print(
            "\n검색된 Serial 포트:",
            ports
        )


        for port in ports:

            try:

                print(
                    f"{port} 확인 중..."
                )


                ser = serial.Serial(
                    port=port,
                    baudrate=115200,
                    timeout=0.5,
                    write_timeout=0.5
                )


                time.sleep(
                    0.2
                )


                ser.reset_input_buffer()


                ser.write(
                    b"PING\n"
                )

                ser.flush()


                response = ser.readline()


                ser.close()


                response = (
                    response
                    .decode(
                        "utf-8",
                        errors="ignore"
                    )
                    .strip()
                )


                print(
                    f"{port} 응답:",
                    response
                )


                if response == "PICO_OK":

                    print(
                        "Pico Serial 발견:",
                        port
                    )

                    return port


            except Exception as e:

                print(
                    f"{port} 확인 실패:",
                    e
                )


        return None


    # ========================================================
    # Pico 재부팅
    # ========================================================

    def reboot_pico(self):

        port = self.find_pico_serial()


        if port is None:

            messagebox.showerror(
                "오류",
                "Pico의 설정용 Serial 포트를 찾지 못했습니다."
            )

            return False


        try:

            print(
                "Pico 재부팅:",
                port
            )


            ser = serial.Serial(
                port=port,
                baudrate=115200,
                timeout=1,
                write_timeout=1
            )


            time.sleep(
                0.2
            )


            ser.reset_input_buffer()


            ser.write(
                b"REBOOT\n"
            )

            ser.flush()


            response = ser.readline()


            response = (
                response
                .decode(
                    "utf-8",
                    errors="ignore"
                )
                .strip()
            )


            print(
                "Pico 응답:",
                response
            )


            ser.close()


            return (
                response == "REBOOT_OK"
            )


        except Exception as e:

            print(
                "Pico 재부팅 오류:",
                e
            )

            return False


    # ========================================================
    # 저장 + Pico 적용
    # ========================================================

    def save_and_apply(self):

        # ----------------------------------------------------
        # JSON 저장
        # ----------------------------------------------------

        if not self.save_settings():

            return


        self.status_label.config(
            text="설정 저장 완료. Pico 재부팅 중..."
        )


        self.root.update()


        # ----------------------------------------------------
        # Pico 재부팅
        # ----------------------------------------------------

        success = self.reboot_pico()


        if success:

            self.status_label.config(
                text="설정 저장 및 Pico 적용 완료"
            )


            messagebox.showinfo(
                "완료",
                "설정이 Pico에 저장되고 적용되었습니다."
            )


        else:

            self.status_label.config(
                text="설정은 저장되었지만 Pico 재부팅에 실패했습니다."
            )


            messagebox.showwarning(
                "주의",
                "설정 파일은 저장되었습니다.\n"
                "하지만 Pico 재부팅에 실패했습니다."
            )


# ============================================================
# 실행
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = PicoConfigurator(
        root
    )

    root.mainloop()