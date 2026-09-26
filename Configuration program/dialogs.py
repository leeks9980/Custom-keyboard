import json
import tkinter as tk
from tkinter import ttk

from config import DISPLAY_NAMES, KEY_MAP
from window_style import apply_title_bar_style


class DialogMixin:
    """설정/정보 대화창 전용 Mixin."""

    def _style_dialog(self, dialog, title, geometry):
        dialog.title(title)
        dialog.geometry(geometry)
        dialog.configure(bg=self.BG)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        apply_title_bar_style(dialog, self.BG, self.TEXT)

    def _dialog_button(self, parent, text, command, primary=False, width=12):
        bg = self.ACCENT if primary else self.PANEL_2
        active = self.ACCENT_2 if primary else "#30343d"
        fg = "white" if primary else self.TEXT
        return tk.Button(
            parent,
            text=text,
            command=command,
            width=width,
            bg=bg,
            fg=fg,
            activebackground=active,
            activeforeground=fg,
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
        )

    def open_setting_dialog(self, index):
        mode = self.mode_vars[index].get()
        if mode == "key":
            self.open_key_dialog(index)
        else:
            self.open_text_dialog(index)

    def open_key_dialog(self, index):
        dialog = tk.Toplevel(self.root)
        self._style_dialog(dialog, f"버튼 {index + 1} · 키 설정", "500x360")

        body = tk.Frame(dialog, bg=self.BG)
        body.pack(fill="both", expand=True, padx=28, pady=24)

        tk.Label(
            body, text=f"BUTTON {index + 1}", bg=self.BG, fg=self.ACCENT_2,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w")
        tk.Label(
            body, text="키 조합 설정", bg=self.BG, fg=self.TEXT,
            font=("Segoe UI", 17, "bold")
        ).pack(anchor="w", pady=(2, 4))
        tk.Label(
            body, text="원하는 키를 동시에 누르면 해당 조합이 버튼에 저장됩니다.",
            bg=self.BG, fg=self.MUTED, font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(0, 18))

        current = self.settings["buttons"][index].get("value", [])

        current_frame = tk.Frame(
            body, bg=self.PANEL, highlightthickness=1,
            highlightbackground=self.BORDER
        )
        current_frame.pack(fill="x", pady=(0, 18))

        tk.Label(
            current_frame, text="현재 설정", bg=self.PANEL, fg=self.MUTED,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w", padx=14, pady=(10, 2))

        current_label = tk.Label(
            current_frame,
            text=self.format_key_command(current),
            bg=self.PANEL, fg=self.TEXT,
            font=("Segoe UI", 15, "bold"),
            anchor="w",
        )
        current_label.pack(fill="x", padx=14, pady=(0, 12))

        self.capture_index = index
        self.captured_keys = []
        self.pressed_keys = set()

        def start_capture():
            self.capturing = True
            self.captured_keys = []
            self.pressed_keys = set()
            current_label.config(text="키를 눌러주세요...", fg=self.ACCENT_2)
            dialog.bind(
                "<KeyPress>",
                lambda event: self.on_key_press(event, current_label),
            )
            dialog.bind(
                "<KeyRelease>",
                lambda event: self.on_key_release(event, current_label, dialog),
            )
            dialog.focus_force()

        def cancel():
            self.capturing = False
            self.capture_index = None
            dialog.destroy()

        buttons = tk.Frame(body, bg=self.BG)
        buttons.pack(fill="x")

        start = self._dialog_button(buttons, "키 입력 시작", start_capture, primary=True, width=16)
        start.pack(side="left")

        cancel_button = self._dialog_button(buttons, "취소", cancel, width=10)
        cancel_button.pack(side="right")

    def on_key_press(self, event, label):
        if not self.capturing:
            return
        key_name = KEY_MAP.get(event.keysym.lower())
        if key_name is None:
            return
        if key_name not in self.pressed_keys:
            self.pressed_keys.add(key_name)
            self.captured_keys.append(key_name)
            label.config(text=self.format_key_command(self.captured_keys), fg=self.TEXT)

    def on_key_release(self, event, label, dialog):
        if not self.capturing:
            return
        key_name = KEY_MAP.get(event.keysym.lower())
        if key_name is not None:
            self.pressed_keys.discard(key_name)
        if self.captured_keys and not self.pressed_keys:
            self.finish_key_capture(self.capture_index, dialog)

    def finish_key_capture(self, index, dialog):
        self.capturing = False
        if not self.captured_keys:
            return
        self.settings["buttons"][index] = {
            "type": "key",
            "value": list(self.captured_keys),
        }
        self.mode_vars[index].set("key")
        self.refresh_display(index)
        self.capture_index = None
        self.captured_keys = []
        self.pressed_keys = set()
        dialog.destroy()

    def open_text_dialog(self, index):
        dialog = tk.Toplevel(self.root)
        self._style_dialog(dialog, f"버튼 {index + 1} · 문자 설정", "540x390")

        body = tk.Frame(dialog, bg=self.BG)
        body.pack(fill="both", expand=True, padx=28, pady=24)

        tk.Label(
            body, text=f"BUTTON {index + 1}", bg=self.BG, fg=self.ACCENT_2,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w")
        tk.Label(
            body, text="문자 입력 설정", bg=self.BG, fg=self.TEXT,
            font=("Segoe UI", 17, "bold")
        ).pack(anchor="w", pady=(2, 4))
        tk.Label(
            body, text="버튼을 눌렀을 때 입력할 문자를 작성하세요.",
            bg=self.BG, fg=self.MUTED, font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(0, 14))

        text_box = tk.Text(
            body, height=8, wrap="word",
            bg=self.PANEL_2, fg=self.TEXT,
            insertbackground=self.TEXT,
            selectbackground=self.ACCENT,
            relief="flat", bd=0,
            font=("Segoe UI", 10), padx=12, pady=10,
        )
        text_box.pack(fill="both", expand=True, pady=(0, 18))

        current_command = self.settings["buttons"][index]
        if current_command.get("type") == "text":
            current_value = current_command.get("value", "")
            if isinstance(current_value, str):
                text_box.insert("1.0", current_value)

        def save_text():
            value = text_box.get("1.0", "end-1c")
            self.settings["buttons"][index] = {"type": "text", "value": value}
            self.mode_vars[index].set("text")
            self.refresh_display(index)
            dialog.destroy()

        buttons = tk.Frame(body, bg=self.BG)
        buttons.pack(fill="x")
        self._dialog_button(buttons, "저장", save_text, primary=True).pack(side="left")
        self._dialog_button(buttons, "취소", dialog.destroy).pack(side="right")
        text_box.focus_set()

    def show_current_json(self):
        dialog = tk.Toplevel(self.root)
        self._style_dialog(dialog, "현재 설정 JSON", "680x520")

        body = tk.Frame(dialog, bg=self.BG)
        body.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            body, text="CURRENT CONFIGURATION", bg=self.BG, fg=self.ACCENT_2,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w")
        tk.Label(
            body, text="Pico에 적용될 현재 설정", bg=self.BG, fg=self.TEXT,
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", pady=(2, 12))

        text = tk.Text(
            body, wrap="none",
            bg="#111318", fg="#dce2ea",
            insertbackground=self.TEXT,
            selectbackground=self.ACCENT,
            relief="flat", bd=0,
            font=("Consolas", 10),
            padx=14, pady=14,
        )
        text.pack(fill="both", expand=True)

        json_text = json.dumps(self.settings, ensure_ascii=False, indent=4)
        text.insert("1.0", json_text)
        text.config(state="disabled")

        self._dialog_button(body, "닫기", dialog.destroy, primary=True, width=10).pack(
            anchor="e", pady=(12, 0)
        )

    def show_result_dialog(self, title, heading, message, success=True):
        dialog = tk.Toplevel(self.root)
        self._style_dialog(dialog, title, "460x270")

        body = tk.Frame(dialog, bg=self.BG)
        body.pack(fill="both", expand=True, padx=30, pady=28)

        accent = self.ACCENT_2 if success else "#e7a96b"
        symbol = "✓" if success else "!"

        tk.Label(
            body, text=symbol, bg=self.BG, fg=accent,
            font=("Segoe UI", 30, "bold")
        ).pack(anchor="w")
        tk.Label(
            body, text=heading, bg=self.BG, fg=self.TEXT,
            font=("Segoe UI", 17, "bold")
        ).pack(anchor="w", pady=(2, 8))
        tk.Label(
            body, text=message, bg=self.BG, fg=self.MUTED,
            font=("Segoe UI", 9), justify="left", wraplength=390
        ).pack(anchor="w")

        self._dialog_button(body, "확인", dialog.destroy, primary=True, width=10).pack(
            anchor="e", side="bottom"
        )
        dialog.focus_force()
        return dialog
