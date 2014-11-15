from flask import Flask, request, g
import requests
import sqlite3
import json

DATABASE = '/Users/noah/soren/database.db'

app = Flask(__name__, static_folder='/Users/noah/soren')

def get_db():
  db = getattr(g, '_database', None)
  if db is None:
    db = g._database = sqlite3.connect(DATABASE)
  db.row_factory = sqlite3.Row # is this the right place for this line?
  return db

@app.teardown_appcontext
def close_connection(exception):
  db = getattr(g, '_database', None)
  if db is not None:
    db.close()

def query_db(query, args=(), one=False):
  cur = get_db().execute(query, args)
  rv = cur.fetchall()
  cur.close()
  return (rv[0] if rv else None) if one else rv

@app.route("/")
def root():
  return app.send_static_file("index.html")

@app.route("/comments.json")
def comments():
  return app.send_static_file("comments.json")

@app.route("/passageQuery")
def passage():
  r = requests.get('http://www.esvapi.org/v2/rest/passageQuery', params={
      "key": "IP",
      "passage": request.args.get('q'),
      "include-passage-references": "false",
      "include-xml-declaration": "true",
      "include-footnotes": "false",
      "include-line-breaks": "false",
      "include-simple-entities": "true",
      "output-format": "crossway-xml-1.0"
    })
  # remove the DOCTYPE which for some reason breaks jQuery parsing
  return r.text.replace('<!DOCTYPE crossway-bible SYSTEM "http://www.gnpcb.org/esv/share/schemas/crossway.base.entities.dtd">', '')

def label(t, *labels):
  '''Given a tuple and a list of objects, produce a '''

@app.route("/commentary", methods=['GET', 'POST'])
def commentary():
  if request.method == 'POST':
    get_db().execute('INSERT INTO commentary VALUES(?, ?, ?, ?)',
                     (request.form["book"], request.form["chapter"], request.form["verse"], request.form["text"]))
    get_db().commit()
    return 'ok'
  elif request.method == 'GET':
    print request.args.get('book')
    results = query_db('select * from commentary')
    return json.dumps([dict(zip(['book', 'chapter', 'verse', 'comment'], r)) for r in results])

if __name__ == "__main__":
  app.run(debug=True)
