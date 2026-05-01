from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
import webbrowser

from kardpad.config import APP_NAME
from kardpad.runtime import KardPadRuntime, RuntimeInfo

try:
    import qrcode
except ImportError:  # pragma: no cover
    qrcode = None


class DesktopLauncher:
    def __init__(self) -> None:
        self.runtime = KardPadRuntime()
        self.info = self.runtime.start()
        self.root = tk.Tk()
        self.root.title(APP_NAME)
        self.root.geometry("980x720")
        self.root.minsize(900, 640)
        self.root.configure(bg="#0b1220")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.selected_ip = tk.StringVar(master=self.root, value=self.info.primary_ip)

        self._build_ui(self.info)
        self._refresh_selected_ip()

    def run(self) -> None:
        self.root.mainloop()

    def _build_ui(self, info: RuntimeInfo) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("Accent.TButton", font=("Segoe UI Semibold", 10))

        outer = tk.Frame(self.root, bg="#0b1220", padx=24, pady=24)
        outer.pack(fill="both", expand=True)

        header = tk.Frame(outer, bg="#0b1220")
        header.pack(fill="x", pady=(0, 18))
        tk.Label(header, text=APP_NAME, bg="#0b1220", fg="#f8fafc", font=("Segoe UI Semibold", 24)).pack(anchor="w")
        tk.Label(
            header,
            text="Servidor listo. Esta ventana sustituye a la terminal y deja todo preparado para el movil.",
            bg="#0b1220",
            fg="#93c5fd",
            font=("Segoe UI", 11),
        ).pack(anchor="w", pady=(6, 0))

        content = tk.Frame(outer, bg="#0b1220")
        content.pack(fill="both", expand=True)

        left = tk.Frame(content, bg="#0b1220")
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))
        right = tk.Frame(content, bg="#0b1220")
        right.pack(side="right", fill="y")

        self._build_status_card(left, info)
        self._build_steps_card(left)
        self._build_networks_card(left, info)
        self._build_qr_card(right)

    def _build_status_card(self, parent: tk.Widget, info: RuntimeInfo) -> None:
        frame = self._card(parent, "Estado")
        frame.pack(fill="x", pady=(0, 12))
        self._status_row(frame, "Servidor web", f"Activo en puerto {info.http_port}")
        self._status_row(frame, "DSU para Dolphin", f"127.0.0.1:{info.dsu_port}")
        tls_text = f"Activo en {info.https_port}/{info.wss_port}" if info.https_enabled else "No disponible"
        self._status_row(frame, "HTTPS / WSS", tls_text)

    def _build_steps_card(self, parent: tk.Widget) -> None:
        frame = self._card(parent, "Uso rapido")
        frame.pack(fill="x", pady=(0, 12))
        steps = [
            "1. Abre la camara del movil y escanea el QR.",
            "2. Si el movil avisa sobre certificado, pulsa continuar.",
            "3. Entra en el enlace, elige jugador y usa el movil como mando.",
            "4. En Dolphin configura DSUClient con 127.0.0.1:26760.",
        ]
        for step in steps:
            tk.Label(frame, text=step, bg="#111827", fg="#dbe4f0", anchor="w", justify="left", font=("Segoe UI", 10)).pack(fill="x", padx=14, pady=4)

        actions = tk.Frame(frame, bg="#111827")
        actions.pack(fill="x", padx=14, pady=(10, 14))
        ttk.Button(actions, text="Abrir vista local", command=self._open_local_preview, style="Accent.TButton").pack(side="left")
        ttk.Button(actions, text="Copiar enlace", command=self._copy_selected_url).pack(side="left", padx=8)

    def _build_networks_card(self, parent: tk.Widget, info: RuntimeInfo) -> None:
        frame = self._card(parent, "Redes detectadas")
        frame.pack(fill="both", expand=True)
        tk.Label(
            frame,
            text="Selecciona la IP que use el movil en tu Wi-Fi. El QR y el enlace se actualizan automaticamente.",
            bg="#111827",
            fg="#dbe4f0",
            anchor="w",
            justify="left",
            font=("Segoe UI", 10),
        ).pack(fill="x", padx=14, pady=(10, 12))

        for ip in info.local_ips:
            row = tk.Frame(frame, bg="#1f2937", highlightbackground="#334155", highlightthickness=1)
            row.pack(fill="x", padx=14, pady=6)
            tk.Radiobutton(
                row,
                text=ip,
                variable=self.selected_ip,
                value=ip,
                command=self._refresh_selected_ip,
                bg="#1f2937",
                fg="#f8fafc",
                selectcolor="#1f2937",
                activebackground="#1f2937",
                activeforeground="#f8fafc",
                font=("Consolas", 11),
            ).pack(anchor="w", padx=12, pady=(10, 4))
            tk.Label(
                row,
                text=info.preferred_browser_url(ip),
                bg="#1f2937",
                fg="#93c5fd",
                font=("Consolas", 10),
            ).pack(anchor="w", padx=36, pady=(0, 10))

    def _build_qr_card(self, parent: tk.Widget) -> None:
        frame = self._card(parent, "QR para el movil")
        frame.pack(fill="y")
        self.qr_canvas = tk.Canvas(frame, width=280, height=280, bg="#ffffff", highlightthickness=0)
        self.qr_canvas.pack(padx=18, pady=(18, 12))
        self.url_label = tk.Label(frame, text="", bg="#111827", fg="#f8fafc", justify="center", wraplength=280, font=("Consolas", 10))
        self.url_label.pack(padx=18, pady=(0, 8))
        tk.Label(
            frame,
            text="Si el QR no carga, copia el enlace y mandalo al movil.",
            bg="#111827",
            fg="#94a3b8",
            justify="center",
            wraplength=280,
            font=("Segoe UI", 9),
        ).pack(padx=18, pady=(0, 18))

    def _refresh_selected_ip(self) -> None:
        ip = self.selected_ip.get()
        url = self.info.preferred_browser_url(ip)
        self.url_label.config(text=url)
        self._draw_qr(url)

    def _draw_qr(self, url: str) -> None:
        self.qr_canvas.delete("all")
        if qrcode is None:
            self.qr_canvas.create_text(140, 140, text="Instala qrcode\npara ver el QR", fill="#111827", font=("Segoe UI", 15))
            return

        qr = qrcode.QRCode(border=2, box_size=8)
        qr.add_data(url)
        qr.make(fit=True)
        matrix = qr.get_matrix()
        size = len(matrix)
        pixel = max(4, min(10, 240 // max(size, 1)))
        total = size * pixel
        offset_x = (280 - total) // 2
        offset_y = (280 - total) // 2

        for y, row in enumerate(matrix):
            for x, cell in enumerate(row):
                color = "#000000" if cell else "#ffffff"
                x0 = offset_x + x * pixel
                y0 = offset_y + y * pixel
                self.qr_canvas.create_rectangle(x0, y0, x0 + pixel, y0 + pixel, outline=color, fill=color)

    def _status_row(self, parent: tk.Widget, label: str, value: str) -> None:
        row = tk.Frame(parent, bg="#111827")
        row.pack(fill="x", padx=14, pady=8)
        tk.Label(row, text=label, bg="#111827", fg="#94a3b8", width=18, anchor="w", font=("Segoe UI", 10)).pack(side="left")
        tk.Label(row, text=value, bg="#111827", fg="#f8fafc", anchor="w", font=("Consolas", 10)).pack(side="left")

    def _copy_selected_url(self) -> None:
        url = self.info.preferred_browser_url(self.selected_ip.get())
        self.root.clipboard_clear()
        self.root.clipboard_append(url)
        self.root.update()
        messagebox.showinfo(APP_NAME, "Enlace copiado al portapapeles.")

    def _open_local_preview(self) -> None:
        webbrowser.open(self.info.http_url("127.0.0.1"))

    def _card(self, parent: tk.Widget, title: str) -> tk.LabelFrame:
        return tk.LabelFrame(parent, text=title, bg="#111827", fg="#f8fafc", font=("Segoe UI Semibold", 12))

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
