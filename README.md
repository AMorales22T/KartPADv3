# KartPADv3

KartPADv3 es una herramienta que permite utilizar un telefono movil como mando de Wii para el emulador Dolphin, trasladando el movimiento real del giroscopio y botones tactiles directamente al juego a traves de red local.

## Instalacion y Uso

1. Descarga la ultima version del archivo ejecutable (KartPADv3.exe) desde la seccion de Releases en GitHub.
2. Ejecuta el programa en tu ordenador con Windows. Si el Firewall de Windows solicita permisos, aceptalos para permitir la conexion en red local.
3. Comprueba que tanto el telefono movil como el ordenador estan conectados a la misma red Wi-Fi.
4. Escanea el codigo QR mostrado en la ventana principal del programa utilizando la camara del movil.
5. Se abrira el navegador en el telefono. Si aparece una advertencia de seguridad, continua (es un certificado local necesario para usar el giroscopio).
6. Selecciona el numero de jugador (1 a 4) en la pantalla del movil y pon el dispositivo en posicion horizontal.

## Configuracion en Dolphin

1. Abre el emulador Dolphin y dirigete a la configuracion de Mandos.
2. En el bloque de "Wiimote 1", elige "Wiimote emulado" y pulsa Configurar.
3. En el panel superior izquierdo (Dispositivo), busca y haz clic en "DSUClient/0/KartPAD". Si no aparece, pulsa el boton Actualizar que hay al lado.
4. En la pestaña de opciones (esquina inferior derecha), marca la casilla "Mando de Wii en horizontal". Es obligatorio para que los giros funcionen en Mario Kart.
5. Si deseas jugar con mas personas, repite los pasos seleccionando "DSUClient/1/KartPAD" para el Jugador 2, y asi sucesivamente.

## Como funciona internamente

* Servidor en PC: El ejecutable inicia un pequeño servidor web y un servidor de telemetria UDP (usando el protocolo DSU).
* Deteccion de movimiento: La interfaz web del movil captura los datos del acelerometro y del giroscopio a alta frecuencia utilizando las APIs estandar de los navegadores.
* Transmision WSS: Los datos de inclinacion y botones tactiles se envian en milisegundos mediante WebSockets seguros al ordenador.
* Puente DSU: El programa de Windows procesa y empaqueta estos datos en formato binario para que Dolphin los reconozca como un mando fisico conectado. Todo se procesa en tu red local sin depender de servidores externos.
