from flask import Flask, render_template, request, redirect, url_for,session
from pymongo import MongoClient
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

@app.route('/egreso')
def egreso():
    return render_template('egreso.html')


@app.route('/ingreso')
def ingreso():
    return render_template('ingreso.html')

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
    for doc in result:
        mount = doc.get("mount")
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
    session.pop('username')
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
