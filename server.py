from flask import Flask
import requests

app = Flask(__name__, static_folder='/Users/noah/soren')

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
      "passage": "Genesis 1",
      "include-passage-references": "false",
      "include-footnotes": "false"
    })
  print '======='
  print r.text
  return r.text

if __name__ == "__main__":
  app.run()
