from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

app = Flask(__name__)
client = MongoClient('mongodb://administrador:asd123@server-quito,server-manta,server-guayaquil/?replicaSet=rsfacci')
db = client.prueba
app.secret_key = 'tu_clave_secreta'

@app.route('/')
def index():
    return sign()

@app.route('/login', methods=['POST'])
def login():
    cedula = request.form['cedula']
    collection = db['clientes']
    result = collection.find({"dni": cedula})
    result = list(result)
    if result:
        usuario = result[0]
        session['username'] = str(usuario['_id'])
        return redirect(url_for('dashboard'))
    else:
        return 'Documento no encontrado'

@app.route('/cajero')
def cajero():
    return render_template('cajero.html')

@app.route('/egreso', methods=['GET'])
def egreso():
    usernid = session.get('username')
    usuario_id = ObjectId(usernid)
    collection = db['clientes']
    result = collection.find({"_id": usuario_id})
    result = list(result)
    for doc in result:
        mount = doc.get("monto")
    monto = mount
    if 'resultado_egreso' in session:
        message = session.get('resultado_egreso')
        session.pop('resultado_egreso')
    else:
        message = None
    return render_template('egreso.html', monto=monto, message=message)

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
            cliente = collections.find_one({"_id": usuario_id})
            monto_actual = cliente['monto']
            if monto_actual >= monto:
                collection.insert_one({"client": usuario_id, "Type": 2, "mount": monto, "date": fecha_formateada})
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
    result = collection.find({"_id": usuario_id})
    result = list(result)
    for doc in result:
        mount = doc.get("monto")
    monto = mount
    if 'resultado_ingreso' in session:
        message = session.get('resultado_ingreso')
        session.pop('resultado_ingreso')
    else:
        message = None
    return render_template('ingreso.html', monto=monto, message=message)

@app.route('/ingreso', methods=['POST'])
def guardar():
    monto = request.form['monto']
    usernid = session.get('username')
    usuario_id = ObjectId(usernid)
    collection = db['Transaction']
    collections = db['clientes']
    fecha_actual = datetime.now()
    fecha_formateada = fecha_actual.strftime("%Y-%m-%d %H:%M:%S")
    sessions = client.start_session()
    with sessions.start_transaction():
        try:
            collection.insert_one({"client": usuario_id, "Type": 1, "mount": monto, "date": fecha_formateada})
            collections.update_one({"_id": usuario_id}, {"$inc": {"monto": int(monto)}})
            sessions.commit_transaction()
            resultado = '¡Monto actualizado correctamente!'
        except:
            session.abort_transaction()
            resultado = 'Error al actualizar el monto'
    sessions.end_session()
    session['resultado_ingreso'] = resultado
    return redirect(url_for('ingreso'))

@app.route('/actualizar')
def actualizar():
    return render_template('actualizar.html')

@app.route('/dashboard')
def dashboard():
    usernid = session.get('username')
    usuario_id = ObjectId(usernid)
    collection = db['Transaction']
    result = collection.find({"client": usuario_id})
    result = list(result)
    client = db['clientes']
    mount = client.find({"_id": usuario_id})
    for doc in mount:
        mount = doc.get("monto")
    monto = mount
    return render_template('dashboard.html', data=result, monto=monto)

@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username')
    return redirect(url_for('index'))

@app.route('/perfil')
def perfil():
    usernid = session.get('username')
    usuario_id = ObjectId(usernid)
    collection = db['clientes']
    perfil = collection.find_one({"_id": usuario_id})
    return render_template('perfil.html', perfil=perfil)

@app.route('/sign-in')
def sign():
    return render_template('sign-in.html')

@app.route('/sign-up', methods=['GET'])
def sign_up():
    return render_template('registro.html')

@app.route('/sign-up', methods=['POST'])
def sign_up_post():
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    dni = request.form['dni']
    email = request.form['email']
    direccion = request.form['direccion']
    name = f"{apellido} {nombre}"
    cliente = {
        'name': name,
        'dni': dni,
        'email': email,
        'direccion': direccion,
        'monto': 0
    }
    client = db['clientes']
    client.insert_one(cliente)
    return sign()

if __name__ == '__main__':
    app.run(debug=True)
