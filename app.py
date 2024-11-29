from flask import Flask, render_template, request, redirect, url_for
import os
from datetime import datetime
import threading
import webbrowser
import pandas as pd
import xlsxwriter

app = Flask(__name__)

# Función para obtener el nombre del archivo Excel del día
def get_excel_filename():
    fecha_hoy = datetime.now().strftime('%Y%m%d')  # Formato: YYYYMMDD
    nombre_archivo = f'registros/registros_{fecha_hoy}.xlsx'
    return nombre_archivo

# Función para proteger el archivo con contraseña
def proteger_excel_con_contraseña(archivo_excel, contrasena):
    # Usamos xlsxwriter para agregar protección por contraseña
    df = pd.read_excel(archivo_excel)
    with pd.ExcelWriter(archivo_excel, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Registros')
        workbook = writer.book
        # Configuración de la contraseña
        workbook.password = contrasena

# Ruta principal
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Obtener los datos del formulario
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        documento = request.form['documento']
        observaciones = request.form['observaciones']
        accion = request.form['accion']  # "Ingreso" o "Salida"

        # Obtener la fecha y hora actual
        fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Obtener el nombre del archivo Excel para el día de hoy
        archivo_excel = get_excel_filename()

        # Comprobar si el archivo ya existe para el día actual
        if os.path.exists(archivo_excel):
            # Si el archivo existe, lo cargamos
            df = pd.read_excel(archivo_excel)
        else:
            # Si el archivo no existe, lo creamos con las columnas correspondientes
            df = pd.DataFrame(columns=['Nombre', 'Apellido', 'Documento', 'Observaciones', 'Accion', 'Fecha_Hora'])

        # Crear una nueva fila con los datos del formulario
        nueva_fila = pd.DataFrame([{
            'Nombre': nombre,
            'Apellido': apellido,
            'Documento': documento,
            'Observaciones': observaciones,
            'Accion': accion,
            'Fecha_Hora': fecha_hora
        }])

        # Usar pd.concat() para agregar la nueva fila al DataFrame
        df = pd.concat([df, nueva_fila], ignore_index=True)

        # Guardar el DataFrame de nuevo en el archivo Excel
        df.to_excel(archivo_excel, index=False)

        # Proteger el archivo con una contraseña
        proteger_excel_con_contraseña(archivo_excel, '*Bomberos2024#')

        # Redirigir a la página principal después de guardar los datos
        return redirect(url_for('index'))

    return render_template('index.html')

# Función para abrir la página en el navegador
def abrir_navegador():
    webbrowser.open('http://127.0.0.1:5000/')

# Función para iniciar el servidor Flask en segundo plano
def iniciar_servidor():
    app.run(port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    # Asegúrate de que el directorio 'registros' exista para guardar los archivos Excel
    if not os.path.exists('registros'):
        os.makedirs('registros')

    # Iniciar el servidor Flask en un hilo
    thread = threading.Thread(target=iniciar_servidor)
    thread.daemon = True  # Hacer que el hilo termine cuando se cierre la aplicación principal
    thread.start()

    # Abrir el navegador automáticamente
    abrir_navegador()

    # Mantener el script en ejecución para que el servidor continúe corriendo
    # Flask ya gestiona el ciclo de vida del servidor, por lo que no es necesario usar un ciclo infinito
    thread.join()
