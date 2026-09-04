from flask import Flask, render_template
app = Flask(__name__)
import config , models , routes


if __name__=='__main__':
    app.run(debug=True)    