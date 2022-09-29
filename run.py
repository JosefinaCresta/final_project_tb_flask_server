from api import app, db
from flask_cors import CORS, cross_origin


cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.shell_context_processor
def make_shell_context():
    return {"app": app,
            "db": db
            }

if __name__ == '__main__':
    # LOCAL
    #app.run(debug=True, host="0.0.0.0")

    # REMOTO
    app.run()
    