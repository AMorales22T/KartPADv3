from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
import webbrowser

from kardpad.config import APP_NAME, RESOURCE_DIR
from kardpad.runtime import KardPadRuntime, RuntimeInfo

try:
    import qrcode
except ImportError:  # pragma: no cover
    qrcode = None

# ── Colour palette ────────────────────────────────────────────────────
BG_DARK    = "#080c18"
BG_CARD    = "#0f1729"
BG_CARD_HL = "#162038"
BORDER     = "#1e2d4a"
ACCENT     = "#06b6d4"    # cyan-500
ACCENT2    = "#22d3ee"    # cyan-400
RED        = "#e74c3c"
GREEN      = "#34d399"    # emerald-400
TEXT_PRI   = "#f0f4ff"
TEXT_SEC   = "#94a3b8"
TEXT_DIM   = "#64748b"

FONT_TITLE = ("Segoe UI", 26, "bold")
FONT_SUB   = ("Segoe UI", 11)
FONT_BODY  = ("Segoe UI", 10)
FONT_MONO  = ("Consolas", 10)
FONT_SMALL = ("Segoe UI", 9)
FONT_BTN   = ("Segoe UI Semibold", 10)


class DesktopLauncher:
    def __init__(self) -> None:
        self.runtime = KardPadRuntime()
        self.info = self.runtime.start()
        self.root = tk.Tk()
        self.root.title(APP_NAME)
        self.root.geometry("1020x760")
        self.root.minsize(920, 680)
        self.root.configure(bg=BG_DARK)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.selected_ip = tk.StringVar(master=self.root, value=self.info.primary_ip)
        self._window_icon = None
        self._header_logo = None
        self._apply_window_icon()

        self._build_ui(self.info)
        self._refresh_selected_ip()

    def run(self) -> None:
        self.root.mainloop()

    # ── UI construction ───────────────────────────────────────────────

    def _build_ui(self, info: RuntimeInfo) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")

        # -- Custom button styles --
        style.configure(
            "Accent.TButton",
            font=FONT_BTN,
            foreground="#ffffff",
            background=ACCENT,
            borderwidth=0,
            padding=(16, 8),
        )
        style.map(
            "Accent.TButton",
            background=[("active", ACCENT2), ("pressed", ACCENT2)],
        )
        style.configure(
            "Secondary.TButton",
            font=FONT_BTN,
            foreground=TEXT_PRI,
            background=BG_CARD_HL,
            borderwidth=1,
            padding=(14, 8),
        )
        style.map(
            "Secondary.TButton",
            background=[("active", BORDER), ("pressed", BORDER)],
        )

        outer = tk.Frame(self.root, bg=BG_DARK, padx=28, pady=20)
        outer.pack(fill="both", expand=True)

        # ── Header ────────────────────────────────────────────────────
        self._build_header(outer)

        # ── Thin accent line ──────────────────────────────────────────
        sep = tk.Canvas(outer, height=2, bg=BG_DARK, highlightthickness=0)
        sep.pack(fill="x", pady=(0, 18))
        sep.bind("<Configure>", lambda e: self._draw_gradient_line(sep, e.width))

        # ── Content: left + right ─────────────────────────────────────
        content = tk.Frame(outer, bg=BG_DARK)
        content.pack(fill="both", expand=True)

        left = tk.Frame(content, bg=BG_DARK)
        left.pack(side="left", fill="both", expand=True, padx=(0, 16))
        right = tk.Frame(content, bg=BG_DARK)
        right.pack(side="right", fill="y")

        self._build_status_card(left, info)
        self._build_steps_card(left)
        self._build_networks_card(left, info)
        self._build_qr_card(right)

        # ── Footer ────────────────────────────────────────────────────
        footer = tk.Frame(outer, bg=BG_DARK)
        footer.pack(fill="x", pady=(14, 0))
        tk.Label(
            footer,
            text="KartPADv3 · Usa tu móvil como mando de Dolphin",
            bg=BG_DARK, fg=TEXT_DIM, font=FONT_SMALL,
        ).pack(side="left")
        tk.Label(
            footer,
            text="github.com/KartPADv3",
            bg=BG_DARK, fg=TEXT_DIM, font=FONT_SMALL,
        ).pack(side="right")

    # ── Header ────────────────────────────────────────────────────────

    def _build_header(self, parent: tk.Widget) -> None:
        header = tk.Frame(parent, bg=BG_DARK)
        header.pack(fill="x", pady=(0, 14))

        header_left = tk.Frame(header, bg=BG_DARK)
        header_left.pack(anchor="w")

        self._header_logo = self._load_logo_image("assets/kartpadv3-icon-256.png", 68)
        if self._header_logo is not None:
            tk.Label(header_left, image=self._header_logo, bg=BG_DARK).pack(
                side="left", padx=(0, 16)
            )

        title_block = tk.Frame(header_left, bg=BG_DARK)
        title_block.pack(side="left")

        title_row = tk.Frame(title_block, bg=BG_DARK)
        title_row.pack(anchor="w")
        tk.Label(
            title_row, text="Kart", bg=BG_DARK, fg=TEXT_PRI, font=FONT_TITLE,
        ).pack(side="left")
        tk.Label(
            title_row, text="PAD", bg=BG_DARK, fg=RED, font=FONT_TITLE,
        ).pack(side="left")
        tk.Label(
            title_row, text="v3", bg=BG_DARK, fg=ACCENT, font=("Segoe UI", 14),
        ).pack(side="left", padx=(4, 0), pady=(10, 0))

        tk.Label(
            title_block,
            text="Servidor listo · Esta ventana sustituye a la terminal y deja todo preparado.",
            bg=BG_DARK, fg=TEXT_SEC, font=FONT_SUB,
        ).pack(anchor="w", pady=(4, 0))

    # ── Status card ───────────────────────────────────────────────────

    def _build_status_card(self, parent: tk.Widget, info: RuntimeInfo) -> None:
        frame = self._card(parent, "⚡  Estado del servidor")
        frame.pack(fill="x", pady=(0, 10))

        self._status_badge(frame, "✅", "Servidor web", f"Activo · puerto {info.http_port}")
        self._status_badge(frame, "🎮", "DSU Dolphin", f"127.0.0.1:{info.dsu_port}")
        tls_text = f"Activo · {info.https_port}/{info.wss_port}" if info.https_enabled else "No disponible"
        tls_icon = "🔒" if info.https_enabled else "⚠️"
        self._status_badge(frame, tls_icon, "HTTPS / WSS", tls_text)

    def _status_badge(self, parent: tk.Widget, icon: str, label: str, value: str) -> None:
        row = tk.Frame(parent, bg=BG_CARD)
        row.pack(fill="x", padx=16, pady=5)

        tk.Label(row, text=icon, bg=BG_CARD, font=("Segoe UI", 13)).pack(
            side="left", padx=(0, 10)
        )

        lbl_frame = tk.Frame(row, bg=BG_CARD)
        lbl_frame.pack(side="left", fill="x", expand=True)
        tk.Label(
            lbl_frame, text=label, bg=BG_CARD, fg=TEXT_SEC,
            anchor="w", font=FONT_BODY,
        ).pack(anchor="w")
        tk.Label(
            lbl_frame, text=value, bg=BG_CARD, fg=TEXT_PRI,
            anchor="w", font=FONT_MONO,
        ).pack(anchor="w")

    # ── Steps card ────────────────────────────────────────────────────

    def _build_steps_card(self, parent: tk.Widget) -> None:
        frame = self._card(parent, "🚀  Uso rápido")
        frame.pack(fill="x", pady=(0, 10))

        steps = [
            ("①", "Abre la cámara del móvil y escanea el QR de la derecha."),
            ("②", "Si el móvil avisa sobre certificado, pulsa \"Continuar\"."),
            ("③", "Elige jugador y usa el móvil como mando de Wii."),
            ("④", "En Dolphin → Configura el dispositivo como DSUClient."),
        ]
        for num, txt in steps:
            row = tk.Frame(frame, bg=BG_CARD)
            row.pack(fill="x", padx=16, pady=3)
            tk.Label(
                row, text=num, bg=BG_CARD, fg=ACCENT,
                font=("Segoe UI", 12), width=3, anchor="w",
            ).pack(side="left")
            tk.Label(
                row, text=txt, bg=BG_CARD, fg=TEXT_PRI,
                anchor="w", justify="left", font=FONT_BODY,
            ).pack(side="left", fill="x", expand=True)

        actions = tk.Frame(frame, bg=BG_CARD)
        actions.pack(fill="x", padx=16, pady=(12, 16))
        ttk.Button(
            actions, text="🌐  Abrir vista local",
            command=self._open_local_preview, style="Accent.TButton",
        ).pack(side="left")
        ttk.Button(
            actions, text="📋  Copiar enlace",
            command=self._copy_selected_url, style="Secondary.TButton",
        ).pack(side="left", padx=(10, 0))
        ttk.Button(
            actions, text="❓  Ayuda Dolphin",
            command=self._show_dolphin_help, style="Secondary.TButton",
        ).pack(side="left", padx=(10, 0))
        ttk.Button(
            actions, text="📊  Probar Mandos",
            command=self._show_controller_test, style="Secondary.TButton",
        ).pack(side="left", padx=(10, 0))

    # ── Networks card ─────────────────────────────────────────────────

    def _build_networks_card(self, parent: tk.Widget, info: RuntimeInfo) -> None:
        frame = self._card(parent, "🌐  Redes detectadas")
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame,
            text="Selecciona la IP que coincida con tu red Wi-Fi. El QR se actualiza.",
            bg=BG_CARD, fg=TEXT_SEC, anchor="w", justify="left", font=FONT_BODY,
        ).pack(fill="x", padx=16, pady=(10, 8))

        for ip in info.local_ips:
            row = tk.Frame(frame, bg=BG_CARD_HL, highlightbackground=BORDER, highlightthickness=1)
            row.pack(fill="x", padx=16, pady=4)
            tk.Radiobutton(
                row, text=ip, variable=self.selected_ip, value=ip,
                command=self._refresh_selected_ip,
                bg=BG_CARD_HL, fg=TEXT_PRI, selectcolor=BG_CARD_HL,
                activebackground=BG_CARD_HL, activeforeground=TEXT_PRI,
                font=FONT_MONO, indicatoron=True,
            ).pack(anchor="w", padx=14, pady=(8, 2))
            tk.Label(
                row, text=info.preferred_browser_url(ip),
                bg=BG_CARD_HL, fg=ACCENT, font=FONT_MONO,
            ).pack(anchor="w", padx=38, pady=(0, 8))

    # ── QR card ───────────────────────────────────────────────────────

    def _build_qr_card(self, parent: tk.Widget) -> None:
        frame = self._card(parent, "📱  QR para el móvil")
        frame.pack(fill="y")

        # QR canvas with a subtle border
        qr_outer = tk.Frame(frame, bg=BORDER, padx=2, pady=2)
        qr_outer.pack(padx=20, pady=(18, 10))
        self.qr_canvas = tk.Canvas(
            qr_outer, width=260, height=260, bg="#ffffff", highlightthickness=0,
        )
        self.qr_canvas.pack()

        self.url_label = tk.Label(
            frame, text="", bg=BG_CARD, fg=ACCENT2,
            justify="center", wraplength=280, font=FONT_MONO,
        )
        self.url_label.pack(padx=20, pady=(4, 6))

        tk.Label(
            frame,
            text="Si el QR no carga, copia el enlace\ny mándalo al móvil.",
            bg=BG_CARD, fg=TEXT_DIM, justify="center",
            wraplength=280, font=FONT_SMALL,
        ).pack(padx=20, pady=(0, 18))

    # ── Helpers ───────────────────────────────────────────────────────

    def _show_dolphin_help(self) -> None:
        """Opens a dedicated help window for Dolphin configuration."""
        help_win = tk.Toplevel(self.root)
        help_win.title("Guía de Configuración en Dolphin")
        help_win.geometry("600x520")
        help_win.configure(bg=BG_DARK)
        help_win.transient(self.root)
        help_win.grab_set()

        pad = 24
        inner = tk.Frame(help_win, bg=BG_DARK, padx=pad, pady=pad)
        inner.pack(fill="both", expand=True)

        tk.Label(inner, text="Configuración de Mandos", bg=BG_DARK, fg=ACCENT, font=FONT_TITLE).pack(anchor="w", pady=(0, 10))
        
        text_bg = BG_CARD
        content = tk.Frame(inner, bg=text_bg, padx=16, pady=16, highlightbackground=BORDER, highlightthickness=1)
        content.pack(fill="both", expand=True)

        guide = [
            ("1. Abre Dolphin", "Ve a la sección de 'Mandos' en la barra superior."),
            ("2. Elige el Wiimote", "En 'Wiimote 1', selecciona 'Wiimote emulado' y pulsa 'Configurar'."),
            ("3. Selecciona el Dispositivo", "En el desplegable 'Dispositivo' (arriba a la izquierda), busca:\nDSUClient/0/KartPAD\n(Si no aparece, pulsa el botón 'Actualizar' al lado)."),
            ("4. Otros Jugadores", "Para el Jugador 2 usa DSUClient/1/, para el Jugador 3 usa DSUClient/2/..."),
            ("5. ¡IMPORTANTE!", "En la pestaña 'Opciones' (abajo a la derecha), marca la casilla:\n[x] Mando de Wii en horizontal\nEsto es vital para que el giro del móvil funcione en Mario Kart."),
        ]

        for title, desc in guide:
            f = tk.Frame(content, bg=text_bg, pady=6)
            f.pack(fill="x")
            tk.Label(f, text=title, bg=text_bg, fg=TEXT_PRI, font=("Segoe UI Semibold", 11)).pack(anchor="w")
            tk.Label(f, text=desc, bg=text_bg, fg=TEXT_SEC, font=FONT_BODY, justify="left", wraplength=500).pack(anchor="w")

        ttk.Button(inner, text="Entendido", command=help_win.destroy, style="Accent.TButton").pack(pady=(20, 0))

    def _show_controller_test(self) -> None:
        """Opens a window to test connected controllers in real-time."""
        test_win = tk.Toplevel(self.root)
        test_win.title("Prueba de Mandos")
        test_win.geometry("640x520")
        test_win.minsize(640, 520)
        test_win.configure(bg=BG_DARK)
        test_win.transient(self.root)
        
        # Keep it always on top so it's a handy widget while configuring Dolphin
        test_win.attributes("-topmost", True)

        header = tk.Frame(test_win, bg=BG_DARK, pady=16)
        header.pack(fill="x")
        tk.Label(header, text="📊 Test de Mandos", bg=BG_DARK, fg=ACCENT, font=FONT_TITLE).pack()
        tk.Label(header, text="Mueve o pulsa botones en el móvil para verlos aquí en tiempo real.", bg=BG_DARK, fg=TEXT_SEC, font=FONT_SUB).pack()

        grid_frame = tk.Frame(test_win, bg=BG_DARK, padx=20, pady=10)
        grid_frame.pack(fill="both", expand=True)

        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)
        grid_frame.rowconfigure(0, weight=1)
        grid_frame.rowconfigure(1, weight=1)

        self.player_widgets = {}

        for player_id in range(1, 5):
            row, col = (player_id - 1) // 2, (player_id - 1) % 2
            card = tk.LabelFrame(
                grid_frame, text=f" Jugador {player_id} ", bg=BG_CARD, fg=TEXT_PRI,
                font=("Segoe UI Semibold", 11), bd=1, padx=12, pady=12
            )
            card.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)

            # Status
            status_lbl = tk.Label(card, text="🔴 Desconectado", bg=BG_CARD, fg=RED, font=FONT_BTN)
            status_lbl.pack(anchor="w", pady=(0, 6))

            # Steering
            tk.Label(card, text="Volante (Giro horizontal):", bg=BG_CARD, fg=TEXT_SEC, font=FONT_SMALL).pack(anchor="w")
            steer_bar = ttk.Progressbar(card, orient="horizontal", length=200, mode="determinate")
            steer_bar.pack(fill="x", pady=(2, 8))

            # Shake
            shake_lbl = tk.Label(card, text="Agitar: Reposo", bg=BG_CARD, fg=TEXT_DIM, font=FONT_BODY)
            shake_lbl.pack(anchor="w", pady=(0, 6))

            # Buttons
            btn_lbl = tk.Label(card, text="Botones: Ninguno", bg=BG_CARD, fg=TEXT_PRI, font=FONT_BODY, wraplength=220)
            btn_lbl.pack(anchor="w")

            self.player_widgets[player_id] = {
                "status": status_lbl,
                "steer": steer_bar,
                "shake": shake_lbl,
                "btns": btn_lbl,
                "card": card
            }

        def _update():
            if not test_win.winfo_exists():
                return
            
            snapshots = self.runtime.hub.snapshots()
            for snapshot in snapshots:
                pid = snapshot.player_id
                widgets = self.player_widgets.get(pid)
                if not widgets:
                    continue

                if snapshot.connected:
                    widgets["status"].config(text="🟢 Conectado", fg=GREEN)
                    widgets["card"].config(bg=BG_CARD_HL)
                    for k, w in widgets.items():
                        if isinstance(w, tk.Label): w.config(bg=BG_CARD_HL)
                    
                    # Steering: accel[0] ranges roughly from -1.0 to +1.0. Map to 0-100.
                    val = (snapshot.accel[0] + 1.0) / 2.0 * 100
                    widgets["steer"]["value"] = max(0, min(100, val))

                    # Shake: gyro[2] (roll) spikes over 20.0 when shaking
                    if abs(snapshot.gyro[2]) > 15.0:
                        widgets["shake"].config(text="🔥 ¡AGITANDO!", fg="#f59e0b")
                    else:
                        widgets["shake"].config(text="Agitar: Reposo", fg=TEXT_DIM)

                    # Buttons
                    btns = ", ".join(sorted(snapshot.buttons)) if snapshot.buttons else "Ninguno"
                    widgets["btns"].config(text=f"Botones: {btns}")
                else:
                    widgets["status"].config(text="🔴 Desconectado", fg=RED)
                    widgets["card"].config(bg=BG_CARD)
                    for k, w in widgets.items():
                        if isinstance(w, tk.Label): w.config(bg=BG_CARD)
                    widgets["steer"]["value"] = 50
                    widgets["shake"].config(text="Agitar: Reposo", fg=TEXT_DIM)
                    widgets["btns"].config(text="Botones: Ninguno")

            test_win.after(40, _update)

        _update()

    def _refresh_selected_ip(self) -> None:
        ip = self.selected_ip.get()
        url = self.info.preferred_browser_url(ip)
        self.url_label.config(text=url)
        self._draw_qr(url)

    def _draw_qr(self, url: str) -> None:
        self.qr_canvas.delete("all")
        if qrcode is None:
            self.qr_canvas.create_text(
                130, 130, text="Instala qrcode\npara ver el QR",
                fill="#111827", font=("Segoe UI", 14),
            )
            return

        qr = qrcode.QRCode(border=2, box_size=8)
        qr.add_data(url)
        qr.make(fit=True)
        matrix = qr.get_matrix()
        size = len(matrix)
        pixel = max(4, min(10, 220 // max(size, 1)))
        total = size * pixel
        offset_x = (260 - total) // 2
        offset_y = (260 - total) // 2

        for y, row in enumerate(matrix):
            for x, cell in enumerate(row):
                color = "#0f172a" if cell else "#ffffff"
                x0 = offset_x + x * pixel
                y0 = offset_y + y * pixel
                self.qr_canvas.create_rectangle(
                    x0, y0, x0 + pixel, y0 + pixel, outline=color, fill=color,
                )

    def _copy_selected_url(self) -> None:
        url = self.info.preferred_browser_url(self.selected_ip.get())
        self.root.clipboard_clear()
        self.root.clipboard_append(url)
        self.root.update()
        messagebox.showinfo(APP_NAME, "Enlace copiado al portapapeles.")

    def _open_local_preview(self) -> None:
        webbrowser.open(self.info.http_url("127.0.0.1"))

    def _card(self, parent: tk.Widget, title: str) -> tk.LabelFrame:
        return tk.LabelFrame(
            parent, text=f"  {title}  ",
            bg=BG_CARD, fg=TEXT_PRI,
            font=("Segoe UI Semibold", 12),
            labelanchor="nw",
            highlightbackground=BORDER,
            highlightthickness=1,
            bd=0,
            padx=0, pady=4,
        )

    def _draw_gradient_line(self, canvas: tk.Canvas, width: int) -> None:
        """Draw a subtle gradient accent line on the canvas."""
        canvas.delete("all")
        steps = max(width, 1)
        for i in range(steps):
            t = i / max(steps - 1, 1)
            # Fade from transparent-ish dark → cyan → dark
            intensity = 1.0 - abs(2 * t - 1)
            r = int(6 + intensity * 0)
            g = int(12 + intensity * 170)
            b = int(24 + intensity * 188)
            color = f"#{r:02x}{g:02x}{b:02x}"
            canvas.create_line(i, 0, i, 2, fill=color)

    def _apply_window_icon(self) -> None:
        icon_ico = RESOURCE_DIR / "assets" / "kartpadv3.ico"
        icon_png = RESOURCE_DIR / "assets" / "kartpadv3-icon-256.png"
        if icon_png.exists():
            try:
                self._window_icon = tk.PhotoImage(file=str(icon_png))
                self.root.iconphoto(True, self._window_icon)
            except tk.TclError:
                self._window_icon = None
        if icon_ico.exists():
            try:
                self.root.iconbitmap(default=str(icon_ico))
            except tk.TclError:
                pass

    def _load_logo_image(self, relative_path: str, size: int) -> tk.PhotoImage | None:
        image_path = RESOURCE_DIR / relative_path
        if not image_path.exists():
            return None
        try:
            image = tk.PhotoImage(file=str(image_path))
        except tk.TclError:
            return None

        shrink = max(1, image.width() // size)
        if shrink > 1:
            image = image.subsample(shrink, shrink)
        return image

    def _on_close(self) -> None:
        self.runtime.stop()
        self.root.destroy()


def main() -> None:
    try:
        launcher = DesktopLauncher()
    except Exception as exc:
        fallback_root = tk.Tk()
        fallback_root.withdraw()
        messagebox.showerror(APP_NAME, f"No se pudo iniciar {APP_NAME}.\n\n{exc}")
        fallback_root.destroy()
        return
    launcher.run()


if __name__ == "__main__":
    main()
