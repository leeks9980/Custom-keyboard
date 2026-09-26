import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import json
import time

import serial
import serial.tools.list_ports
from config import BUTTON_PINS, BUTTON_COUNT, DEFAULT_SETTINGS, KEY_MAP, DISPLAY_NAMES
from pico import find_pico_drive, get_all_serial_ports, find_pico_serial
from settings import deep_copy, convert_settings
from dialogs import DialogMixin
from main_gui import GuiMixin


# ============================================================
# 고정 GPIO
# ============================================================

# ============================================================
# Pico를 찾지 못했을 때만 사용하는 기본값
# ============================================================

# ============================================================
# 키 이름 변환
# ============================================================

# ============================================================
# 화면 표시용 이름
# ============================================================

# ============================================================
# 깊은 복사
# ============================================================



# ============================================================
# Pico(CIRCUITPY) 드라이브 찾기
# ============================================================



# ============================================================
# Serial 포트 전체 검색
# ============================================================



# ============================================================
# 메인 GUI
# ============================================================

class PicoConfigurator(GuiMixin, DialogMixin):

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
    # 메인 GUI는 main_gui.py의 GuiMixin에서 구성
    # ========================================================


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

            if hasattr(self, "set_connection_state"):

                self.set_connection_state(False)


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

            if hasattr(self, "set_connection_state"):

                self.set_connection_state(True)


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

            pico_settings = convert_settings(pico_settings, BUTTON_COUNT)


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

            if hasattr(self, "set_connection_state"):

                self.set_connection_state(True)


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

            if hasattr(self, "set_connection_state"):

                self.set_connection_state(False)


            return False


    # ========================================================
    # JSON 형식 변환
    # ========================================================



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



    # ========================================================
    # 키 설정 창
    # ========================================================



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


        if hasattr(self, "update_graphics"):

            self.update_graphics(index)


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



    # ========================================================
    # Pico 재부팅
    # ========================================================

    def reboot_pico(self):

        port = find_pico_serial()


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


            self.show_result_dialog(
                "적용 완료",
                "설정 적용 완료",
                "설정이 Pico에 저장되고 적용되었습니다.",
                success=True
            )

        else:

            self.status_label.config(
                text="설정은 저장되었지만 Pico 재부팅에 실패했습니다."
            )


            self.show_result_dialog(
                "적용 결과",
                "설정 저장 완료",
                "설정 파일은 저장되었습니다.\n하지만 Pico 재부팅에 실패했습니다.",
                success=False
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