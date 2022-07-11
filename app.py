from flask import Flask, json, jsonify, redirect, render_template, request, session, make_response, url_for
from flask_cors import CORS, cross_origin
from flask_session import Session
import logging
import pytube as pt
import re
from xml.etree.ElementTree import fromstring, ElementTree
from youtube_transcript_api import YouTubeTranscriptApi

#
# This developmet uses PyTube:
# pytube: https://pytube.io/en/latest/api.html#youtube-object
#

logging.basicConfig(
  filename='transcribeYT.log',
  # encoding='utf-8',
  format='%(asctime)s %(levelname)s:%(message)s',
  level=logging.DEBUG
)
logging.debug("Logging activated")

app = Flask(__name__)
# Using session to avoid a "Confirm Form Resubmission" pop-up:
# Redirect and pass form values from post to get method
app.secret_key = 'secret'
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Use Flask server session to avoid a "Confirm Form Resubmission" pop-up:
# Redirect and pass form values from post to get method
app.config['SECRET_KEY'] = "your_secret_key" 
app.config['SESSION_TYPE'] = 'filesystem' 
app.config['SESSION_PERMANENT']= False
app.config.from_object(__name__)
Session(app)

def download(vid):

    print("vid    "+vid)
    yt=getYT(vid)

    # YouTube object
    print("Video  author: "+yt.author+" title: "+yt.title+" length: "+str(yt.length)+" views: " + str(yt.views)+" rating: "+str(yt.rating))
          
    captions=getCaptions(yt)
        
    return captions


def extract_video_id(v):
    if (v.startswith("https://www.youtube.com/watch?v=")):
        p1 = 32
    elif (v.startswith("https://youtu.be/")):
        p1 = 17
    else:
        p1 = 0
    p2 = v.find("&")
    if (p2 < 0):
        v2 = v[p1:]
    else:
        v2 = v[p1:p2]
    return v2
# extract_video_id

def get_transcript(video_id):

  # Retrieve the transcript with youtube-transcript-api
  transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
  t = transcript_list.find_transcript(['en'])  

  # fetch the actual transcript data
  text=t.fetch()
  lines=[]
  for r in text:
    lines.append(r['text'])
    
  # Merge short lines
  merge_short_lines(lines)
  
  # Print the meta data
  # print(f"video_id: {t.video_id}")
  # print(f"language: {t.language}")
  # print(f"language_code: {t.language_code}")
  # print(f"is_generated: {t.is_generated}")
  # print(f"is_translatable: {t.is_translatable}")
  # print(f"translation_languages: {t.translation_languages}")

  # Build the response
  s=""
  for line in lines:
    s+=line
    if re.match('.*[.!?]$',line):
      s+="\n"
    s+="\n"
  print(s)
  return s

# get_transcript

def get_yt(id):
    url='https://www.youtube.com/watch?v='+id
    print(f'get_yt - url={url}')
    yt=pt.YouTube(url, use_oauth=True, allow_oauth_cache=True)
    print(f'get_yt - author: {yt.author} title: {yt.title}')
    return yt
# get_yt

def merge_short_lines(lines):
    buffer = ''
    for line in lines:
        if line == "":
            yield '\n' + line
            continue

        if len(line+buffer) < 200:
            buffer += ' ' + line
        else:
            yield buffer.strip()
            buffer = line
    yield buffer
# merge_short_lines

def url_ok(url):
  if url=='':
    print(f"Error: url is empty: {url}")
    return False
  return True;
# url_ok

# API endpoint
@app.route('/transcribeyt', methods=['GET','POST'])
@cross_origin()
def transcript():
  logging.debug(f"Got transcript request. request:")
  logging.debug(request)
  logging.debug("request.data:")
  logging.debug(request.data)
  logging.debug("request.form:")
  logging.debug(request.form)
  if request.data:
    d=json.loads(request.data)
  else:
    d=request.form
  logging.debug("d:")
  logging.debug(d)
  url=d['video']
  logging.debug(f"transcript_yt url: {url}")
  if url_ok(url):
    # Extract the video id from the url
    video_id=extract_video_id(url)
    # Get the metadata
    yt=get_yt(video_id)
    # Get the transcript
    transcript=get_transcript(video_id)
    logging.debug(f"transcript len={len(transcript)}")
    ret={
      "author": yt.author,
      "id": video_id,
      "title": yt.title,
      "transcript": transcript,
    }
    return jsonify(ret)
    # js=json.dumps(ret)
    # logging.debug(f"transcribe_yt - i:{video_id} a:{yt.author} t:{yt.title}")
    # return Response(js)
  return jsonify("Could not get the transcript")
# transcript

# HTML home page
@app.route('/', methods=['GET','POST'])
def slash():
  print(f"slash - got request: {request.method}")

  # Transcript request
  if 'transcript' in request.form:
    url = request.form["url"]
    print(f"Branch: transcript - url: {url}")
    # Get the transcript
    if url_ok(url):
      video_id=extract_video_id(url)
      text=get_transcript(video_id)
      print(f"transcript len={len(text)}")
      print(text)
      session['text']=text;
      
  # Download request
  elif 'download' in request.form:
    text=request.form['text']
    print(f"Branch: Download - text len={len(text)}")
    output = make_response(text)
    output.headers["Content-Disposition"] = "attachment; filename=export.txt"
    output.headers["Content-type"] = "text/csv"
    return output

  # Redirect to avoid "Form Resubmission" pop-up
  if request.method=='POST':
    print("branch: redirect")
    return redirect(url_for('slash'))
  
  # Render page
  else:
    print("render index.html")
    text=session.get('text','session get text')
    print(f"render index.html text= {text}")
    return render_template("index.html", text=text)  

if __name__ == '__main__':
  app.run(debug=True,host='0.0.0.0',port=5004)
