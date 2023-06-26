from flask import Flask, render_template, request, redirect, url_for,session
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
app = Flask(__name__)
client = MongoClient('mongodb://administrador:asd123@localhost:27017/?authMechanism=DEFAULT&authSource=admin')
db = client.prueba
app.secret_key = 'tu_clave_secreta'
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    # Lógica para verificar la cédula y autenticar al usuario
    cedula = request.form['cedula']
    print(cedula)
    collection = db['clientes']
    
    result = collection.find({"dni": cedula})
    result=list(result)
    #resprint(result)
    if result:
    # Si se encuentra un documento con el campo "idn" igual al valor buscado
    # Realiza alguna operación con el resultado obtenido
         # Si la verificación es exitosa, almacenar los datos en la sesión
        usuario = result[0]
        session['username'] = str(usuario['_id'])
        return redirect(url_for('dashboard'))
    else:
    # Si no se encuentra un documento con el campo "idn" igual al valor buscado
        return 'Documento no encontrado'
   

@app.route('/cajero')
def cajero():
    return render_template('cajero.html')

@app.route('/egreso', methods=['GET'])
def egreso():
    # Lógica para verificar la cédula y autenticar al usuario
    usernid = session.get('username')
    usuario_id = ObjectId(usernid)
    collection = db['clientes']
    print(usuario_id)
    result = collection.find({"_id": usuario_id})
    result=list(result)
    for doc in result:
        mount = doc.get("monto")
    print(mount)
    monto=mount
    if 'resultado_egreso' in session:
        message = session.get('resultado_egreso')
        session.pop('resultado_egreso')
    else:
        message = "null"
    return render_template('egreso.html',monto=monto,message=message)

@app.route('/egreso', methods=['POST'])
def retiro():
    monto = int(request.form['monto'])
    usernid = session.get('username')
    usuario_id = ObjectId(usernid)
    collection = db['Transaction']
    collections = db['clientes']
    fecha_actual = datetime.now()
    fecha_formateada = fecha_actual.strftime("%Y-%m-%d %H:%M:%S")
    sessions = client.start_session()
    with sessions.start_transaction():
        try:
            # Obtener el monto actual del cliente
            cliente = collections.find_one({"_id": usuario_id})
            monto_actual = cliente['monto']

            # Verificar si el monto es suficiente para el egreso
            if monto_actual >= monto:
                # Realizar el egreso en una transacción
                collection.insert_one({"client": usuario_id, "Type": 2, "mount": monto, "date": fecha_formateada})
                # Actualizar el monto del cliente en una transacción
                collections.update_one({"_id": usuario_id}, {"$inc": {"monto": -monto}})

                sessions.commit_transaction()
                resultado = '¡Egreso realizado correctamente!'
            else:
                sessions.abort_transaction()
                resultado = 'Error: El monto actual es insuficiente para el egreso'

        except:
            sessions.abort_transaction()
            resultado = 'Error al realizar el egreso'

    sessions.end_session()
    session['resultado_egreso'] = resultado
    return redirect(url_for('egreso'))

@app.route('/ingreso', methods=['GET'])
def ingreso():
    usernid = session.get('username')
    usuario_id = ObjectId(usernid)
    collection = db['clientes']
    print(usuario_id)
    result = collection.find({"_id": usuario_id})
    result=list(result)
    for doc in result:
        mount = doc.get("monto")
    print(mount)
    monto=mount
    if 'resultado_ingreso' in session:
        message = session.get('resultado_ingreso')
        session.pop('resultado_ingreso')
    else:
        message = "null"
    return render_template('ingreso.html',monto=monto,message=message)

@app.route('/ingreso' ,methods=['POST'])
def guardar():
    monto = request.form['monto']
    print(monto)
    # Actualizar el monto del cliente en la base de datos
    usernid = session.get('username')
    print(usernid)
    usuario_id = ObjectId(usernid)
    collection = db['Transaction']
    collections = db['clientes']
    # Obtener la fecha y hora actual
    fecha_actual = datetime.now()
    # Formatear la fecha al formato deseado
    fecha_formateada = fecha_actual.strftime("%Y-%m-%d %H:%M:%S")
    sessions = client.start_session()  # Iniciar sesión de transacción
    with sessions.start_transaction():
        try:
          
  # Realizar el ingreso en una transacción
            collection.insert_one({"client": usuario_id, "Type": 1, "mount": monto,"date":fecha_formateada})
            # Actualizar el monto del cliente en una transacción
            collections.update_one({"_id": usuario_id}, {"$inc": {"monto": int(monto)}})

            sessions.commit_transaction()  # Confirmar la transacción

            resultado = '¡Monto actualizado correctamente!'
        except:
            session.abort_transaction()  # Hacer rollback en caso de error
            resultado = 'Error al actualizar el monto'

    sessions.end_session()
    session['resultado_ingreso'] = resultado
    return redirect(url_for('ingreso'))

@app.route('/actualizar')
def actualizar():
    return render_template('actualizar.html')

@app.route('/dashboard')
def dashboard():
    # Obtener los datos almacenados en la sesión
    usernid = session.get('username')
    usuario_id = ObjectId(usernid)
    collection = db['Transaction']
    print(usuario_id)
    result = collection.find({"client": usuario_id})
    result=list(result)
    print(result)
    client = db['clientes']
    print(usuario_id)
    mount = client.find({"_id": usuario_id})
    for doc in mount:
        mount = doc.get("monto")
    print(mount)
    monto=mount
    if result:
     
        print(result[0])  # Acceder al primer elemento del cursor
    else:
        print("El cursor está vacío")
    print("este es el dni")
    return render_template('dashboard.html',data=result,monto=monto)
@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username')
    return redirect(url_for('index'))
@app.route('/perfil')
def perfil():

       return render_template('perfil.html')

if __name__ == '__main__':
    app.run(debug=True)
