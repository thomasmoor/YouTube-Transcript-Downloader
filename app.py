from flask import Flask, json, jsonify, redirect, render_template, request, session, make_response, url_for
from flask_cors import CORS, cross_origin
import pytube as pt
import re
from xml.etree.ElementTree import fromstring, ElementTree
from youtube_transcript_api import YouTubeTranscriptApi

#
# This developmet uses PyTube:
# pytube: https://pytube.io/en/latest/api.html#youtube-object
#

app = Flask(__name__)
# Using session to avoid a "Confirm Form Resubmission" pop-up:
# Redirect and pass form values from post to get method
app.secret_key = 'secret'
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

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

def get_transcript(url):

  # Extract the videoid from the url
  video_id=extract_video_id(url)
    
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
@app.route('/transcript', methods=['POST'])
@cross_origin()
def transcript():
  d=json.loads(request.data)
  print("d:")
  print(d)
  url=d['url']
  print(f"transcript url: {url}")
  if url_ok(url):
    transcript=get_transcript(url)
    print(f"transcript len={len(transcript)}")
    return jsonify(transcript)
  return jsonify("Could not get the transcript")
# transcript

# HTML home page
@app.route('/', methods=['GET','POST'])
def slash():
  print(f"slash - got request: {request.method}")

  # Default text
  text='Enter or copy/paste a URL in the box above \nand press "Get Transcript"'

  # Transcript request
  if 'transcript' in request.form:
    url = request.form["url"]
    print(f"Branch: transcript - url: {url}")
    # Get the transcript
    if url_ok(url):
      text=get_transcript(url)
      print(f"transcript len={len(text)}")
      print(text)
    else:
      text="Could not get transcript"
      
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
    session['text'] = text
    return redirect(url_for('slash'))
  
  # Render page
  else:
    print("render index.html")
    text=session.get('text','session get text')
    print(f"render index.html text= {text}")
    return render_template("index.html", text=text)  

if __name__ == '__main__':
  app.run()