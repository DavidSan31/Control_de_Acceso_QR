import os
import qrcode

# Función para generar el código QR con el nombre de una persona
def generar_qr(nombre):
    # Crear el objeto QR
    qr = qrcode.QRCode(
        version=1,  # Nivel de complejidad (más grande es más complejo)
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # Nivel de corrección de errores
        box_size=10,  # Tamaño de cada cuadro
        border=4,  # Ancho del borde
    )
    
    # Agregar el texto (en este caso, el nombre de la persona)
    qr.add_data(nombre)
    qr.make(fit=True)
    
    # Crear una imagen del código QR
    img = qr.make_image(fill='black', back_color='white')
    
    # Definir la ruta de la carpeta "Personal CBVF"
    carpeta_destino = "Personal CBVF"
    
    # Verificar si la carpeta existe, si no existe, crearla
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)
        print(f"Carpeta '{carpeta_destino}' creada.")
    
    # Guardar la imagen en la carpeta "Personal CBVF"
    ruta_guardado = os.path.join(carpeta_destino, f'{nombre}.png')
    img.save(ruta_guardado)
    print(f'Código QR generado para {nombre} y guardado en {ruta_guardado}')

# Ejemplo de uso: Generar un código QR con el nombre de una persona
nombre_persona = input("Ingresa el nombre de la persona: ")
generar_qr(nombre_persona)
