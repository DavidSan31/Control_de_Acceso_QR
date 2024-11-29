import cv2
import pandas as pd
from datetime import datetime
import time  # Para utilizar la pausa de 5 segundos
import pygame  # Para manejar sonidos

# Inicializar pygame para manejar sonidos
pygame.mixer.init()

# Cargar el sonido que se reproducirá al registrar un código QR
sonido_registro = pygame.mixer.Sound("registro.mp3")  # Reemplaza con la ruta de tu archivo de sonido

# Crear o cargar el archivo Excel donde se registrarán los códigos QR
def cargar_o_crear_excel():
    try:
        # Intentar cargar el archivo existente
        df = pd.read_excel("registros_qr.xlsx")
    except FileNotFoundError:
        # Si no existe, crear uno nuevo con las columnas necesarias
        df = pd.DataFrame(columns=["Código QR", "Fecha y Hora", "Tipo"])
        df.to_excel("registros_qr.xlsx", index=False)
    return df

# Función para registrar un código QR en el archivo Excel
def registrar_qr(info_qr, tipo):
    df = cargar_o_crear_excel()
    # Obtener la fecha y hora actual
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Añadir una nueva fila con la información del QR, la fecha/hora y el tipo (entrada o salida)
    nueva_fila = pd.DataFrame([[info_qr, fecha_hora, tipo]], columns=["Código QR", "Fecha y Hora", "Tipo"])
    df = pd.concat([df, nueva_fila], ignore_index=True)
    # Guardar el DataFrame actualizado en el archivo Excel
    df.to_excel("registros_qr.xlsx", index=False)
    print(f"{tipo} registrado para el QR: {info_qr} a las {fecha_hora}")

# Inicializar el detector de códigos QR
qrCode = cv2.QRCodeDetector()
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("No se puede abrir la cámara")
    exit()

# Diccionario para llevar el registro del estado de los códigos QR (si ya han sido registrados y su tipo)
codigos_registrados = {}

# Variables para manejar la espera de 5 segundos
esperando_pausa = False
ultimo_codigo_qr = None
tiempo_ultimo_scan = 0  # Variable para controlar el tiempo de espera
codigo_en_vista = False  # Variable para saber si el código está en vista

# Variables para manejar el mensaje de confirmación
mensaje = ""
mensaje_tiempo = 0  # Tiempo en que se mostró el último mensaje de "Entrada" o "Salida"
mensaje_duracion = 3  # Duración del mensaje en segundos

# Coordenadas para el cuadro en el centro de la cámara
alto, ancho = 480, 640  # Tamaño de la imagen (ajustar según resolución de tu cámara)
cuadro_tamano = 300  # Tamaño del cuadro en píxeles
centro_x, centro_y = ancho // 2, alto // 2  # Centro de la cámara
cuadro_inicio_x = centro_x - cuadro_tamano // 2
cuadro_inicio_y = centro_y - cuadro_tamano // 2
cuadro_fin_x = centro_x + cuadro_tamano // 2
cuadro_fin_y = centro_y + cuadro_tamano // 2

while True:
    ret, frame = cap.read()

    if ret:
        # Dibujar el cuadro en el centro de la pantalla
        cv2.rectangle(frame, (cuadro_inicio_x, cuadro_inicio_y), (cuadro_fin_x, cuadro_fin_y), (255, 0, 0), 2)

        ret_qr, decoded_info, points, _ = qrCode.detectAndDecodeMulti(frame)

        # Establecer el color por defecto antes de procesar los códigos QR
        color = (0, 0, 255)  # Color rojo por defecto si no se detecta QR

        if ret_qr:
            for info, point in zip(decoded_info, points):
                if info:
                    # El código QR está visible
                    codigo_en_vista = True

                    # Verificar si el QR está dentro del cuadro
                    if cv2.pointPolygonTest(point, (centro_x, centro_y), False) >= 0:
                        # Si estamos esperando la pausa de 5 segundos, no procesar el QR
                        if esperando_pausa:
                            continue  # Ignorar este escaneo si estamos esperando la pausa

                        # Verificar si el código QR ya ha sido registrado
                        if info not in codigos_registrados:
                            # Registrar como "Entrada"
                            codigos_registrados[info] = "Entrada"
                            registrar_qr(info, "Entrada")
                            color = (0, 255, 0)  # Color verde para ingreso
                            mensaje = "Entrada registrada"  # Mostrar mensaje de "Entrada"
                            # Reproducir sonido
                            sonido_registro.play()
                            # Pausa de 5 segundos
                            esperando_pausa = True
                            ultimo_codigo_qr = info  # Guardar el código QR para no repetirlo
                            tiempo_ultimo_scan = time.time()  # Registrar el tiempo del último escaneo
                        else:
                            # Si ya fue registrado, alternar entre "Entrada" y "Salida"
                            if codigos_registrados[info] == "Entrada":
                                # Registrar como "Salida"
                                codigos_registrados[info] = "Salida"
                                registrar_qr(info, "Salida")
                                color = (0, 0, 255)  # Color rojo para salida
                                mensaje = "Salida registrada"  # Mostrar mensaje de "Salida"
                            else:
                                # Registrar como "Entrada" nuevamente
                                codigos_registrados[info] = "Entrada"
                                registrar_qr(info, "Entrada")
                                color = (0, 255, 0)  # Color verde para entrada
                                mensaje = "Entrada registrada"  # Mostrar mensaje de "Entrada"

                            # Reproducir sonido
                            sonido_registro.play()

                            # Pausa de 5 segundos
                            esperando_pausa = True
                            ultimo_codigo_qr = info  # Guardar el código QR para no repetirlo
                            tiempo_ultimo_scan = time.time()  # Registrar el tiempo del último escaneo

                    # Dibujar el polígono del QR en el marco
                    frame = cv2.polylines(frame, [point.astype(int)], True, color, 8)

        # Verificar si el mensaje debe desaparecer después de 3 segundos
        if mensaje and time.time() - mensaje_tiempo >= mensaje_duracion:
            mensaje = ""  # Eliminar el mensaje después de la duración
            mensaje_tiempo = 0

        # Colocar el texto en la pantalla si hay mensaje
        if mensaje:
            cv2.putText(frame, mensaje, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)

    else:
        print("No se puede recibir el fotograma (¿final de la transmisión?). Saliendo ...")
        break

    # Mostrar la imagen con el código QR detectado y el mensaje
    cv2.imshow('Detector de codigos QR', frame)

    # Salir del bucle si se presiona la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Control de la pausa de 5 segundos
    if esperando_pausa and time.time() - tiempo_ultimo_scan >= 5:
        esperando_pausa = False

# Liberar la cámara y cerrar las ventanas de OpenCV
cap.release()
cv2.destroyAllWindows()
