```text
 _  __          _   ____  _    ____        ____
| |/ /__ _ _ __| |_|  _ \/ \  |  _ \__   _|___ \
| ' // _` | '__| __| |_) / _ \ | | | \ \ / / __) |
| . \ (_| | |  | |_|  __/ ___ \| |_| |\ V /|__ <
|_|\_\__,_|_|   \__|_| /_/   \_\____/  \_/ |___/
```

> **KartPADv3** — Convierte tu móvil en un Wiimote horizontal para jugar en Dolphin.  
> Sin hardware extra. Sin drivers. Solo tu teléfono y la misma Wi-Fi.

---

## ¿Qué es esto?

KartPADv3 es una herramienta que permite usar un teléfono móvil como mando de Wii para el emulador **Dolphin**, enviando en tiempo real los datos del giroscopio, acelerómetro y botones táctiles a través de red local mediante el **protocolo DSU (cemuhook)**.

Está pensado principalmente para **Mario Kart Wii** pero funciona con cualquier juego de Wii que use Wiimote horizontal.

---

## Instalación y Uso

### En el PC (Windows)

1. Descarga la última versión de **KartPADv3.exe** desde la sección [Releases](../../releases) en GitHub.
2. Ejecuta el programa. Si el Firewall de Windows pide permisos de red, **acéptalos**.
3. Se abrirá una ventana con el **código QR**, la IP del servidor y el estado de la conexión.

### En el Móvil (iOS / Android)

4. Asegúrate de que el **móvil y el PC están en la misma red Wi-Fi**.
5. Escanea el código QR con la cámara del móvil (o escribe la IP manualmente si usas la APK).
6. Si aparece una advertencia de seguridad del certificado, **acéptala** — es un certificado local autofirmado, necesario para acceder al giroscopio en iOS Safari.
7. Elige tu número de jugador (1 a 4) y pon el teléfono en **posición horizontal**.

---

## Configuración en Dolphin

### Opción A — Automática (recomendada)

En la ventana de KartPADv3 pulsa el botón **"🐬 Aplicar Config Dolphin"**.  
El programa escribe automáticamente los archivos `WiimoteNew.ini` y `DSUClient.ini` con la configuración correcta.  
También se aplica de forma automática la primera vez que Dolphin se pone en primer plano.

> Después de aplicar la configuración, **cierra y vuelve a abrir Dolphin** para que cargue los cambios.

### Opción B — Manual

1. Abre Dolphin → **Mandos**.
2. En *Wiimote 1*, elige **"Wiimote emulado"** → Configurar.
3. En el desplegable *Dispositivo*, selecciona **`DSUClient/0/KartPAD`**. Si no aparece, pulsa Actualizar.
4. En la pestaña *Opciones* (esquina inferior derecha), marca **"Mando de Wii en horizontal"** ✓ — obligatorio para que el giro funcione.
5. Para más jugadores: repite con `DSUClient/1/`, `DSUClient/2/`…

---

## Mapeo de controles

| Botón en el móvil | Señal DSU | Acción en MKWii |
|---|---|---|
| **A** | R2 | Acelerar (Wiimote 2) |
| **B** | L2 | Frenar (Wiimote 1) |
| **DRIFT** (trigger izq.) | R1 | Derrapar (Wiimote B) |
| **ITEM** (trigger der.) | Pad N (Up) | Usar objeto / Menú ↑ |
| **TRUCO** | Triangle → Shake | Pirueta |
| **ATRÁS** | X (Square) | Mirar atrás (Wiimote A) |
| **+** | OPTIONS | Pausa |
| **D-Pad** | Pad N/S/W/E | Navegar menús |
| **Inclinar móvil** | IMU Accel/Gyro | Girar (volante) |
| **Agitar móvil** | Accel spike | Pirueta / Truco |

---

## Características del sistema

### Conectividad
- **Puerto unificado HTTPS + WSS** en `:3443`: la web y el WebSocket comparten el mismo puerto TLS, por lo que iOS solo necesita aceptar el certificado **una sola vez**.
- **Servidor HTTP plano** en `:3000` para la APK Android (Capacitor, cleartext).
- **WebSocket WS** en `:8000` para la APK (sin TLS).
- **Detección de IP inteligente**: prioriza la interfaz Wi-Fi/Ethernet real, ignorando adaptadores virtuales (WSL, Hyper-V, VMware, VirtualBox).
- **Reconexión automática con cuenta atrás cancelable**: si se pierde la conexión, el móvil reconecta automáticamente en 8 segundos. El usuario puede cancelarlo tocando el mensaje.

### Mando móvil (interfaz web PWA)
- Compatible con **iOS Safari**, **Android Chrome** y **APK nativa** (Capacitor).
- **HapticEngine en capas**: vibración nativa → Web Audio API (click audible en iOS Safari como fallback) → flash visual CSS.
- **Sensibilidad del volante ajustable** en 5 niveles (zona muerta + umbral).
- **Inversión del volante**: opción para quienes les resulta más natural el giro invertido.
- **Recalibración automática** del punto neutro del volante al cambiar la orientación de pantalla.
- **Modo pantalla completa** y bloqueo de orientación landscape.
- **Modo puntero de menú**: usa el touchpad táctil del móvil para mover el cursor del ratón en el PC.
- **Banner PWA para iOS**: detecta si la app no está instalada en Safari y guía al usuario a "Añadir a inicio".
- **Escáner QR integrado**: la cámara del propio móvil escanea el QR que muestra el PC, sin necesidad de escribir la IP.
- **IP recordada**: la última IP usada se guarda y se propone en el siguiente arranque.

### Launcher de escritorio (Windows)
- Interfaz gráfica con **selección de red**: muestra todas las IPs detectadas y actualiza el QR al seleccionarla.
- **Panel de prueba de mandos en tiempo real** (`📊 Probar Mandos`): muestra volante, estado de agitación y botones pulsados de cada jugador simultáneamente.
- **Aplicación automática de config Dolphin**: detecta cuando Dolphin está en primer plano y aplica la configuración sin intervención del usuario.
- **Guía interactiva de Dolphin** integrada en la ventana.
- **Gradiente animado** en el separador de cabecera y logo con colores por jugador.

### Seguridad
- **Certificado TLS autofirmado** generado localmente en cada instalación (nunca se sube a internet).
- **Protección contra path traversal** en el servidor de archivos estáticos.
- **Sin dependencias de servidores externos**: todo el procesamiento ocurre en red local.
- **Sin credenciales hardcodeadas** ni tokens de API en el código.

---

## Cómo funciona internamente

```
Móvil (Safari / Chrome / APK)
    │  Giroscopio + Acelerómetro + Botones táctiles
    │  WebSocket seguro (WSS :3443) o WS (:8000)
    ▼
PC — KartPADv3.exe
    │  Python: servidor web + MobileGateway (WebSocket)
    │  Protocolo DSU / cemuhook (UDP :26760)
    ▼
Dolphin Emulator
    │  DSUClient recibe los datos
    │  Los mapea a un Wiimote emulado virtual
    ▼
Mario Kart Wii 🏎️
```

- **Servidor web**: sirve la interfaz del mando en el móvil (HTTPS estático + WebSocket en el mismo puerto TLS).
- **MobileGateway**: recibe los mensajes JSON del móvil (botones y datos de movimiento) y los entrega al `ControllerHub`.
- **ControllerHub**: mantiene el estado de hasta 4 mandos simultáneos y lo traduce al formato binario DSU.
- **DSUServer**: empaqueta los datos en paquetes UDP que Dolphin consume como si fuera un mando físico.

---

## Dependencias

```
websockets
qrcode
Pillow
psutil
pywin32      # solo Windows — detección de ventana Dolphin
pyinstaller  # solo para compilar el ejecutable
```

Instala con:
```bash
pip install -r requirements.txt
```

---

## Construir el ejecutable

```powershell
.\build_windows.ps1
```

El script usa PyInstaller y empaqueta todos los activos (icono, certificados, archivos estáticos) en un único `.exe`.

---

## Licencia

MIT — ver [LICENSE](LICENSE).
