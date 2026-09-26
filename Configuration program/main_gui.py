import tkinter as tk
from tkinter import ttk

from config import BUTTON_PINS, BUTTON_COUNT
from window_style import apply_title_bar_style


class GuiMixin:
    """Pico Configurator 메인 화면 구성 전용 Mixin."""

    BG = "#15171c"
    PANEL = "#202329"
    PANEL_2 = "#272a31"
    BORDER = "#343943"
    TEXT = "#f2f4f7"
    MUTED = "#969daa"
    ACCENT = "#4f8cff"
    ACCENT_2 = "#78a9ff"
    DEVICE = "#555b64"
    DEVICE_EDGE = "#707782"
    KEY = "#17191d"
    KEY_TOP = "#252930"
    KEY_EDGE = "#8d949e"

    def create_gui(self):
        self.root.configure(bg=self.BG)
        self.root.title("Pico Control Center")
        self.root.geometry("1080x720")
        self.root.minsize(980, 650)
        self.root.resizable(True, True)

        self._setup_styles()
        apply_title_bar_style(self.root, self.BG, self.TEXT)

        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------
        header = tk.Frame(self.root, bg=self.BG)
        header.pack(fill="x", padx=28, pady=(22, 12))

        title_box = tk.Frame(header, bg=self.BG)
        title_box.pack(side="left")

        tk.Label(
            title_box,
            text="PICO CONTROL CENTER",
            bg=self.BG,
            fg=self.TEXT,
            font=("Segoe UI", 19, "bold")
        ).pack(anchor="w")

        tk.Label(
            title_box,
            text="USB HID Controller Configuration",
            bg=self.BG,
            fg=self.MUTED,
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(2, 0))

        self.connection_badge = tk.Label(
            header,
            text="●  연결 확인 중",
            bg="#252932",
            fg="#d6d9df",
            padx=14,
            pady=7,
            font=("Segoe UI", 9, "bold")
        )
        self.connection_badge.pack(side="right", pady=3)

        # ----------------------------------------------------
        # Main content
        # ----------------------------------------------------
        content = tk.Frame(self.root, bg=self.BG)
        content.pack(fill="both", expand=True, padx=28, pady=(0, 14))

        # Device preview
        preview_panel = tk.Frame(
            content,
            bg=self.PANEL,
            highlightthickness=1,
            highlightbackground=self.BORDER
        )
        preview_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        preview_header = tk.Frame(preview_panel, bg=self.PANEL)
        preview_header.pack(fill="x", padx=18, pady=(16, 4))

        tk.Label(
            preview_header,
            text="DEVICE",
            bg=self.PANEL,
            fg=self.TEXT,
            font=("Segoe UI", 10, "bold")
        ).pack(side="left")

        tk.Label(
            preview_header,
            text="버튼을 선택하면 오른쪽에서 설정할 수 있습니다.",
            bg=self.PANEL,
            fg=self.MUTED,
            font=("Segoe UI", 8)
        ).pack(side="right")

        self.device_canvas = tk.Canvas(
            preview_panel,
            bg=self.PANEL,
            highlightthickness=0,
            bd=0
        )
        self.device_canvas.pack(fill="both", expand=True, padx=16, pady=(2, 16))
        self.device_canvas.bind("<Configure>", self._on_device_canvas_resize)

        # Settings panel
        settings_panel = tk.Frame(
            content,
            bg=self.PANEL,
            width=340,
            highlightthickness=1,
            highlightbackground=self.BORDER
        )
        settings_panel.pack(side="right", fill="y")
        settings_panel.pack_propagate(False)

        settings_header = tk.Frame(settings_panel, bg=self.PANEL)
        settings_header.pack(fill="x", padx=18, pady=(16, 10))

        tk.Label(
            settings_header,
            text="BUTTONS",
            bg=self.PANEL,
            fg=self.TEXT,
            font=("Segoe UI", 10, "bold")
        ).pack(side="left")

        tk.Label(
            settings_header,
            text="4 FIXED INPUTS",
            bg=self.PANEL,
            fg=self.MUTED,
            font=("Segoe UI", 8, "bold")
        ).pack(side="right")

        self.button_cards = []
        self.mode_vars = []
        self.value_labels = []

        for i in range(BUTTON_COUNT):
            self._create_button_card(settings_panel, i)

        # ----------------------------------------------------
        # Bottom bar
        # ----------------------------------------------------
        bottom = tk.Frame(self.root, bg=self.BG)
        bottom.pack(fill="x", padx=28, pady=(0, 20))

        self.status_label = tk.Label(
            bottom,
            text="Pico 설정을 불러오는 중...",
            bg=self.BG,
            fg=self.MUTED,
            anchor="w",
            font=("Segoe UI", 9)
        )
        self.status_label.pack(side="left", fill="x", expand=True)

        json_button = tk.Button(
            bottom,
            text="JSON 보기",
            command=self.show_current_json,
            bg=self.PANEL_2,
            fg=self.TEXT,
            activebackground="#30343d",
            activeforeground=self.TEXT,
            relief="flat",
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2",
            font=("Segoe UI", 9, "bold")
        )
        json_button.pack(side="right", padx=(8, 0))

        save_button = tk.Button(
            bottom,
            text="저장 및 Pico 적용",
            command=self.save_and_apply,
            bg=self.ACCENT,
            fg="white",
            activebackground=self.ACCENT_2,
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=22,
            pady=9,
            cursor="hand2",
            font=("Segoe UI", 9, "bold")
        )
        save_button.pack(side="right")

        self._draw_device()

    def _setup_styles(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Pico.TCombobox",
            fieldbackground=self.PANEL_2,
            background=self.PANEL_2,
            foreground=self.TEXT,
            bordercolor=self.BORDER,
            lightcolor=self.BORDER,
            darkcolor=self.BORDER,
            arrowcolor=self.MUTED,
            padding=5,
            font=("Segoe UI", 9)
        )
        style.map(
            "Pico.TCombobox",
            fieldbackground=[("readonly", self.PANEL_2)],
            foreground=[("readonly", self.TEXT)]
        )

    def _create_button_card(self, parent, index):
        card = tk.Frame(
            parent,
            bg=self.PANEL_2,
            highlightthickness=1,
            highlightbackground=self.BORDER,
            cursor="hand2"
        )
        card.pack(fill="x", padx=14, pady=5)
        self.button_cards.append(card)

        top = tk.Frame(card, bg=self.PANEL_2)
        top.pack(fill="x", padx=12, pady=(10, 2))

        number = tk.Label(
            top,
            text=f"{index + 1}",
            bg=self.ACCENT if index == 0 else "#3a3f49",
            fg="white",
            width=3,
            pady=3,
            font=("Segoe UI", 9, "bold")
        )
        number.pack(side="left")
        card.number_label = number

        tk.Label(
            top,
            text=f"BUTTON {index + 1}",
            bg=self.PANEL_2,
            fg=self.TEXT,
            font=("Segoe UI", 9, "bold")
        ).pack(side="left", padx=9)

        tk.Label(
            top,
            text=BUTTON_PINS[index],
            bg=self.PANEL_2,
            fg=self.MUTED,
            font=("Consolas", 8)
        ).pack(side="right")

        self._bind_card_click(card, index)

        mode_var = tk.StringVar(value="key")
        self.mode_vars.append(mode_var)

        mode_display = tk.StringVar(value="키 입력")
        mode_box = ttk.Combobox(
            card,
            textvariable=mode_display,
            values=("키 입력", "문자 입력"),
            state="readonly",
            style="Pico.TCombobox",
            width=9
        )
        mode_box.pack(side="left", padx=(12, 6), pady=(6, 10))
        mode_box.bind(
            "<<ComboboxSelected>>",
            lambda event, idx=index, display_var=mode_display:
                self._on_mode_selected(idx, display_var)
        )
        card.mode_display = mode_display
        card.mode_box = mode_box

        value_label = tk.Label(
            card,
            text="불러오는 중...",
            bg=self.PANEL_2,
            fg="#dce0e7",
            anchor="w",
            font=("Segoe UI", 9),
            width=20
        )
        value_label.pack(side="left", fill="x", expand=True, padx=4, pady=(6, 10))
        self.value_labels.append(value_label)
        card.value_label = value_label

        setting_button = tk.Button(
            card,
            text="설정",
            command=lambda idx=index: self.open_setting_dialog(idx),
            bg="#333842",
            fg=self.TEXT,
            activebackground="#414754",
            activeforeground=self.TEXT,
            relief="flat",
            bd=0,
            padx=11,
            pady=5,
            cursor="hand2",
            font=("Segoe UI", 8, "bold")
        )
        setting_button.pack(side="right", padx=(4, 10), pady=(6, 10))
        card.setting_button = setting_button

    def _on_mode_selected(self, index, display_var):
        mode = "text" if display_var.get() == "문자 입력" else "key"
        self.mode_vars[index].set(mode)
        self.on_mode_changed(index)

    def _sync_mode_displays(self):
        for i, mode_var in enumerate(self.mode_vars):
            if i < len(self.button_cards):
                display = "문자 입력" if mode_var.get() == "text" else "키 입력"
                self.button_cards[i].mode_display.set(display)

    def _bind_card_click(self, widget, index):
        widget.bind("<Button-1>", lambda event, idx=index: self.select_button(idx))
        for child in widget.winfo_children():
            child.bind("<Button-1>", lambda event, idx=index: self.select_button(idx))

    def select_button(self, index):
        self.selected_button = index
        self._update_card_selection()
        self._draw_device()

    def _update_card_selection(self):
        selected = getattr(self, "selected_button", 0)
        for i, card in enumerate(self.button_cards):
            if i == selected:
                card.configure(highlightbackground=self.ACCENT, highlightthickness=1)
                card.number_label.configure(bg=self.ACCENT)
            else:
                card.configure(highlightbackground=self.BORDER, highlightthickness=1)
                card.number_label.configure(bg="#3a3f49")

    def _on_device_canvas_resize(self, event):
        self._draw_device()

    def _round_rect(self, canvas, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2 - radius,
            x1, y1 + radius,
        ]
        return canvas.create_polygon(points, smooth=True, splinesteps=16, **kwargs)

    def _draw_keycap(self, canvas, cx, cy, size, index, selected):
        x1 = cx - size / 2
        y1 = cy - size / 2
        x2 = cx + size / 2
        y2 = cy + size / 2

        # shadow / lower body
        self._round_rect(
            canvas,
            x1 + 3,
            y1 + 7,
            x2 + 3,
            y2 + 7,
            9,
            fill="#0d0f12",
            outline="#0d0f12"
        )

        # lower edge
        self._round_rect(
            canvas,
            x1,
            y1 + 5,
            x2,
            y2 + 5,
            9,
            fill="#0f1115",
            outline=self.ACCENT if selected else "#0e1013",
            width=2 if selected else 1
        )

        # top surface
        self._round_rect(
            canvas,
            x1 + 2,
            y1,
            x2 - 2,
            y2 - 3,
            8,
            fill=self.KEY_TOP if selected else self.KEY,
            outline=self.KEY_EDGE if selected else "#555b65",
            width=2 if selected else 1
        )

        # label
        command = ""
        try:
            item = self.settings["buttons"][index]
            if item.get("type") == "key":
                command = self.format_key_command(item.get("value", []))
            else:
                command = item.get("value", "") or "문자"
        except Exception:
            command = ""

        if len(command) > 14:
            command = command[:12] + "…"

        canvas.create_text(
            cx,
            cy - 8,
            text=f"{index + 1}",
            fill="#ffffff",
            font=("Segoe UI", 15, "bold")
        )
        canvas.create_text(
            cx,
            cy + 18,
            text=command,
            fill=self.ACCENT_2 if selected else "#9ba1ab",
            font=("Segoe UI", 8, "bold")
        )

    def _draw_knob(self, canvas, cx, cy, radius):
        canvas.create_oval(
            cx - radius - 3,
            cy - radius - 3,
            cx + radius + 3,
            cy + radius + 3,
            fill="#101216",
            outline="#101216"
        )
        canvas.create_oval(
            cx - radius,
            cy - radius,
            cx + radius,
            cy + radius,
            fill="#1b1d22",
            outline="#707783",
            width=2
        )
        canvas.create_oval(
            cx - radius + 7,
            cy - radius + 7,
            cx + radius - 7,
            cy + radius - 7,
            fill="#292d34",
            outline="#0f1114"
        )

        # knob marker
        canvas.create_line(
            cx,
            cy - radius + 9,
            cx,
            cy - radius + 22,
            fill=self.ACCENT_2,
            width=3
        )

        canvas.create_text(
            cx,
            cy + radius + 23,
            text="VOLUME",
            fill=self.MUTED,
            font=("Segoe UI", 8, "bold")
        )

    def _draw_device(self):
        if not hasattr(self, "device_canvas"):
            return

        canvas = self.device_canvas
        canvas.delete("all")

        w = max(canvas.winfo_width(), 420)
        h = max(canvas.winfo_height(), 360)

        # Device keeps the same broad proportions as the supplied model.
        device_w = min(w - 54, 620)
        device_h = min(h - 70, 360)
        device_w = max(device_w, 400)
        device_h = max(device_h, 260)

        x1 = (w - device_w) / 2
        y1 = (h - device_h) / 2
        x2 = x1 + device_w
        y2 = y1 + device_h

        # subtle ground shadow
        self._round_rect(
            canvas,
            x1 + 8,
            y1 + 10,
            x2 + 8,
            y2 + 10,
            16,
            fill="#0d0f12",
            outline="#0d0f12"
        )

        # enclosure
        self._round_rect(
            canvas,
            x1,
            y1,
            x2,
            y2,
            16,
            fill=self.DEVICE,
            outline=self.DEVICE_EDGE,
            width=2
        )

        # top edge highlight
        canvas.create_line(
            x1 + 18,
            y1 + 8,
            x2 - 18,
            y1 + 8,
            fill="#828892",
            width=1
        )

        # four keys, matching the physical layout in the supplied model
        key_size = min(device_w * 0.18, device_h * 0.30)
        left_x = x1 + device_w * 0.23
        right_x = x1 + device_w * 0.56
        top_y = y1 + device_h * 0.36
        bottom_y = y1 + device_h * 0.69

        positions = [
            (left_x, top_y),
            (right_x, top_y),
            (left_x, bottom_y),
            (right_x, bottom_y),
        ]

        selected = getattr(self, "selected_button", 0)
        for i, (cx, cy) in enumerate(positions):
            tag = f"device_button_{i}"
            self._draw_keycap(canvas, cx, cy, key_size, i, i == selected)
            # 키캡 영역을 클릭하면 해당 버튼을 선택
            items = canvas.find_overlapping(
                cx - key_size / 2 - 5,
                cy - key_size / 2 - 5,
                cx + key_size / 2 + 5,
                cy + key_size / 2 + 5
            )
            for item in items:
                canvas.addtag_withtag(tag, item)
            canvas.tag_bind(
                tag,
                "<Button-1>",
                lambda event, idx=i: self.select_button(idx)
            )

        # rotary knob on the right
        knob_x = x1 + device_w * 0.82
        knob_y = y1 + device_h * 0.50
        knob_radius = min(device_w, device_h) * 0.085
        self._draw_knob(canvas, knob_x, knob_y, knob_radius)

        # device label
        canvas.create_text(
            x1 + 22,
            y2 - 19,
            text="PICO HID CONTROLLER",
            anchor="w",
            fill="#aeb4bd",
            font=("Segoe UI", 8, "bold")
        )

        self._sync_mode_displays()
        self._update_card_selection()

    def update_graphics(self, index=None):
        """설정 변경 후 장치 미리보기를 갱신."""
        self._draw_device()

    def set_connection_state(self, connected):
        if connected:
            self.connection_badge.configure(
                text="●  PICO 연결됨",
                fg="#8fe3a6"
            )
        else:
            self.connection_badge.configure(
                text="●  PICO 미연결",
                fg="#d7a6a6"
            )
