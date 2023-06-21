from flask import Flask

app = Flask(__name__)

# Configuración para activar el modo de depuración
app.debug = True

# Rutas y lógica de tu aplicación Flask...

@app.route('/')
def hello():
    return '¡Holacxc, Flaskzs z!'

if __name__ == '__main__':
    app.run(debug=True)
