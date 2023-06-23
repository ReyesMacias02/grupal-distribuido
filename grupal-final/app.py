from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    cedula = request.form['cedula']
    # Lógica para verificar la cédula y autenticar al usuario
    return redirect(url_for('cajero'))

@app.route('/cajero')
def cajero():
    return render_template('cajero.html')



if __name__ == '__main__':
    app.run(debug=True)
