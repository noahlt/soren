from flask import Flask, request
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
      "passage": request.args.get('q'),
      "include-passage-references": "false",
      "include-footnotes": "false"
    })
  return r.text

if __name__ == "__main__":
  app.run()
