from flask import Flask, render_template, request, redirect
from flask_restful import Resource
import sys
from flask_sqlalchemy import SQLAlchemy
import re


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True



app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db = SQLAlchemy(app)

class Record(db.Model):
    __tablename__ = "record"
    id = db.Column(db.Integer, primary_key=True)
    regex = db.Column(db.String(50), nullable=False)
    text = db.Column(db.String(1024), nullable=False)
    result = db.Column(db.Boolean, nullable=False)


with app.app_context():
    db.drop_all()
    db.create_all()



class MainPageView(Resource):
    def get(self):
        return render_template('index.html')

    def post(self):
        regex = request.form["regex"]
        text = request.form["text"]
        check = True if re.match(regex, text) else False
        id_new = 0
        last_record = Record.query.order_by(Record.id.desc()).first()
        if last_record is not None:
            id_new = last_record.id + 1
        record = Record(
            id = id_new,
        regex=regex,
        text=text,
        result=check
        )
        db.session.add(record)
        db.session.commit()
        id_new += 1
        return redirect(f'/result/{record.id}/')



class HistoryPageView(Resource):
    def get(self):
        history = Record.query.order_by(Record.id.desc()).all()
        return render_template("history.html", history=history)


class ResultPageView(Resource):
    def get(self, id):
        result = Record.query.filter(Record.id==id).first()
        return render_template("result.html", entry=result)

app.add_url_rule('/', view_func = MainPageView.as_view('main'))
app.add_url_rule('/result/<int:id>/', view_func = ResultPageView.as_view('result'))
app.add_url_rule('/history/', view_func = HistoryPageView.as_view('history'))




# don't change the following way to run flask:
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run(host='0.0.0.0', port=3433)
