from flask import Flask, render_template, flash, request, Response, jsonify, redirect, url_for, send_file
from database import app, db, PaisSchema
from paises import Pais
from werkzeug.utils import secure_filename
from random import sample
import os
import io

from sqlalchemy.exc import SQLAlchemyError


pais_schema = PaisSchema()
pais_schema = PaisSchema(many=True)

app.app_context().push()
db.create_all()


@app.route('/')
def home():
    pais = Pais.query.all()
    paisesLeidos = pais_schema.dump(pais)

    return render_template('index.html', pais=pais)

@app.route('/imagen/<int:pais_id>')
def obtener_imagen(pais_id):
    pais = Pais.query.get_or_404(pais_id)
    return send_file(io.BytesIO(pais.bandera_blob), mimetype='image/png')  


@app.route('/paises')
def formulario():
    pais = Pais.query.all()
    paisesLeidos = pais_schema.dump(pais)

    return render_template('add.html', pais=paisesLeidos)


# Method Post
def guardar_archivo(bandera_blob, nombre):
    # La ruta donde se encuentra el archivo actual
    basepath = os.path.dirname(__file__)
    # Nombre original del archivo
    filename = secure_filename(bandera_blob.filename)

    # Capturando extensión del archivo ejemplo: (.png, .jpg, .pdf ...etc)
    extension = os.path.splitext(filename)[1]
    nuevo_nombre_file = "BanderaDe" + nombre + extension

    # upload_path = os.path.join(basepath, 'static/images', nuevo_nombre_file)
    bandera_blob.save(upload_path)

    # Leer el contenido del archivo como bytes
    # with open(upload_path, 'rb') as file:
    blob_data = bandera_blob.read()

    bandera_url = "BanderaDe" + nombre + extension

    return bandera_url, blob_data, nuevo_nombre_file


@app.route('/agregar', methods=['POST'])
def add_pais():
    if request.method == 'POST':
        nombre = request.form['nombre']
        capital = request.form['capital']
        bandera_blob = request.files['bandera']
        habitantes = request.form['habitantes']
        dia_nacional = request.form['diaNacional']

        if nombre and capital and bandera_blob and habitantes and dia_nacional:
            bandera_url, blob_data, nuevo_nombre_file = guardar_archivo(bandera_blob, nombre)

            nuevo_pais = Pais(
                nombre=nombre,
                capital=capital,
                bandera_url=bandera_url,
                bandera_blob=blob_data,
                habitantes=habitantes,
                diaNacional=dia_nacional
            )

            db.session.add(nuevo_pais)
            db.session.commit()

            response = jsonify({
                'nombre': nombre,
                'capital': capital,
                'bandera_url': bandera_url,
                'bandera_blob': nuevo_nombre_file,
                'habitantes': habitantes,
                'diaNacional': dia_nacional
            })

            return redirect(url_for('home'))
        else:
            return notFound()



@app.route('/delete/<id>')
def deletePais(id):
    pais = Pais.query.get(id)
    db.session.delete(pais)
    db.session.commit()

    flash('Pais ' + id + ' eliminado correctamente')
    return redirect(url_for('home'))

# Method Put


@app.route('/editar/<id>', methods=['GET', 'POST'])
def editForm(id):
    pais = Pais.query.get(id)
    return render_template('edit.html', pais=pais)

@app.route('/edit/<id>', methods=['POST'])
def editPais(id):
    pais = Pais.query.get(id)

    # Actualizar los atributos con los valores del formulario
    pais.nombre = request.form.get('nombre')
    pais.capital = request.form.get('capital')
    pais.habitantes = request.form.get('habitantes')
    pais.diaNacional = request.form.get('diaNacional')
    bandera_blob = request.files['bandera']
    if bandera_blob is None or not bandera_blob.filename:
        pass
    else:
        # La ruta donde se encuentra el archivo actual
        basepath = os.path.dirname(__file__)
        # Nombre original del archivo
        filename = secure_filename(bandera_blob.filename)

        # Capturando extensión del archivo ejemplo: (.png, .jpg, .pdf ...etc)
        extension = os.path.splitext(filename)[1]
        nuevo_nombre_file = "BanderaDe" + pais.nombre + extension

        upload_path = os.path.join(basepath, 'static/images', nuevo_nombre_file)
        bandera_blob.save(upload_path)

        # Leer el contenido del archivo como bytes
        with open(upload_path, 'rb') as file:
            blob_data = file.read()

        pais.bandera_url = "BanderaDe" + pais.nombre + extension
        pais.bandera_blob = blob_data



    # Guardar los cambios en la base de datos
    db.session.commit()

    flash('País ' + id + ' actualizado correctamente')
    return redirect(url_for('home'))

    
@app.errorhandler(404)
def notFound(error=None):
    message = {
        'message': 'No encontrado ' + request.url,
        'status': '404 Not Found'
    }
    response = jsonify(message)
    response.status_code = 404
    return response


if __name__ == "__main__":
    app.run(debug=True)
