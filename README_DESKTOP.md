# KartPADv3 para escritorio

## Objetivo

`KartPADv3` puede ejecutarse como programa de escritorio en Windows sin abrir terminal.

La app de escritorio:

- inicia el servidor sola
- muestra la IP correcta
- enseña un QR para el movil
- deja Dolphin apuntando a `127.0.0.1:26760`

## Ejecutar en desarrollo

```powershell
python desktop_launcher.py
```

## Generar el `.exe`

1. Instala dependencias:

```powershell
python -m pip install -r requirements.txt
python -m pip install pyinstaller
```

2. Genera el ejecutable:

```powershell
.\build_windows.ps1
```

3. El binario final quedará en:

```text
dist\KartPADv3.exe
```

## Uso para usuario final

1. Abrir `KartPADv3.exe`
2. Escanear el QR con el movil
3. Aceptar el aviso del certificado si aparece
4. Elegir jugador en el movil
5. En Dolphin usar `DSUClient` con `127.0.0.1:26760`
