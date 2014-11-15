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

def test_int(s):
  '''Test to see whether string s contains an int'''
  try:
    int(s)
    return s
  except ValueError:
    return False

def select_commentary(book=None, chapter=None, verse=None):
    wherePhrases = []

    if book:
      # Danger, Will Robinson, danger! SQL injection here:
      wherePhrases.append('book = "%s"' % (book.lower()))

    if chapter and test_int(chapter):
      wherePhrases.append('chapter = ' + chapter)

    if verse and test_int(verse):
      wherePhrases.append('verse = ' + verse)

    whereClause = 'WHERE ' + ' AND '.join(wherePhrases) if len(wherePhrases) > 0 else ''
    return query_db(' '.join(['SELECT * FROM commentary', whereClause]))


@app.route("/commentary", methods=['GET', 'POST'])
def commentary():
  if request.method == 'POST':
    book = request.form["book"].lower()
    chapter = test_int(request.form["chapter"])
    verse = test_int(request.form["verse"])

    if len(select_commentary(book, chapter, verse)) == 0:
      get_db().execute('INSERT INTO commentary VALUES(?, ?, ?, ?)',
                       (book, chapter, verse, request.form["text"]))
      get_db().commit()
      return 'ok'
    else:
      get_db().execute('UPDATE commentary SET book = ?, chapter = ?, verse = ?, text = ? WHERE book = ? AND chapter = ? AND verse = ?',
                       (book, chapter, verse, request.form["text"], book, chapter, verse))
      get_db().commit()
      return 'ok'
  elif request.method == 'GET':
    results = select_commentary(book=request.args.get('book'),
                                chapter=request.args.get('chapter'),
                                verse=request.args.get('verse'))
    return json.dumps([dict(zip(['book', 'chapter', 'verse', 'comment'], r)) for r in results])

if __name__ == "__main__":
  app.run(debug=True)
