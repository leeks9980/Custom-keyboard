"""Pico connection and discovery functions."""

import json
import time
import serial
import serial.tools.list_ports
from pathlib import Path

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
