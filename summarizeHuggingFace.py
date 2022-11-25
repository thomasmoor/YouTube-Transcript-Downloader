from flask import Flask, json, jsonify, redirect, render_template, request, session, make_response, url_for
from flask_cors import CORS, cross_origin
from flask_session import Session
import logging
from transformers import pipeline

#
# pip install flask flask-cors flask-session transformers
# pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu116
#

model="facebook/bart-large-cnn"

# Models Cache Files in C:\Users\User\.cache\huggingface\hub

logging.basicConfig(
  filename='summarizerHuggingFace.log',
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

def summarize(text):

  logging.debug(f"summarize - text length:{len(text)}")
  
  if len(text) == 0:
    return ''

  max_chunk=500
  logging.debug(f"summarization - max chunk: {max_chunk}")
  current_chunk=0
  chunks=[]
  lines=text.splitlines(False)
  for line in lines:
    if len(chunks) == current_chunk+1:
      if len(chunks[current_chunk]) + len(line.split(' ')) <= max_chunk:
        chunks[current_chunk].extend(line.split(' '))
      else:
        current_chunk+=1
        chunks.append(line.split(' '))
    else:
      # print(current_chunk)
      chunks.append(line.split(' '))
  logging.debug(f"summarization - Chunks size: {len(chunks)}")
      
  # Aggregate the chunks
  for chunk_id in range(len(chunks)):
    chunks[chunk_id] = ' '.join(chunks[chunk_id])
    
  logging.debug(f"summarization - chunk(0): {chunks[0]}")
  
  # Get summarization
  res=summarizer(chunks,max_length=120,min_length=30,do_sample=False)
  
  # Concatenate the summaries by chunk
  summary=' '.join([summ['summary_text'] for summ in res])
  logging.debug(f"summary: {summary}")
  ratio=len(summary)/len(text)
  logging.debug(f"Compression: {len(summary)} / {len(text)} = {ratio}")

  return summary

# summarize

# API endpoint
@app.route('/getsummaryhuggingface',:wq methods=['GET','POST'])
@cross_origin()
def api():
  logging.debug(f"Got Summary request")
  logging.debug("request.data:")
  # logging.debug(request.data)
  if request.data:
    d=json.loads(request.data)
  else:
    d=request.form
  # logging.debug("d:")
  # logging.debug(d)
  text=d
  logging.debug(f"summarize - text length: {len(text)}")
  summary2=summarize(text)
  logging.debug(f"summary2 len={len(summary2)}")
  summary=summarize(summary2)
  result={
    'summary':  summary,
    'summary2': summary2
  }
  return jsonify(result)
# api

# HTML home page
@app.route('/', methods=['GET','POST'])
def slash():
  logging.debug(f"slash - got request: {request.method}")
  if 'text' in session:
    logging.debug(f"Session - text:   {session['text'][0:30]}")
  else:
    logging.debug(f"Session - text:   Not in Session")
  if 'result' in session:
    logging.debug(f"Session - result: {session['result'][0:30]}")
  else:
    logging.debug(f"Session - result: Not in Session")

  # Request
  if 'summarize' in request.form:

    # Clear the cache
    session.pop('text', None)
    session.pop('result', None)
    
    text = request.form["inputtext"]
    logging.debug(f"branch: summarize - text length: {len(text)}")
    logging.debug(f"branch: summarize - text: {text[0:25]}")
    session['text']=text
    # Summarize
    if text:
      summary2=summarize(text)
      logging.debug(f"branch: summarize - Summary2 length: {len(summary2)}")
      summary=summarize(summary2)
      logging.debug(f"branch: summarize - Summary  length: {len(summary)}")
    else:
      logging.debug("branch: summarize - Could not summarize: no text")
      summary="Could not summarize"
      summary2="Could not summarize"
    logging.debug(f"branch: summarize - summary:  {summary}")
    logging.debug(f"branch: summarize - summary2: {summary2}")
    result = {
      'summary': summary,
      'summary2': summary2
    }
    session['result']=json.dumps(result)
    logging.debug(f"branch: summarize - Session: {session['result'][0:100]}")

  elif 'download' in request.form:
    print("branch - download")
    result=json.loads(session['result'])
    
    s="Overall Summary\n---------------\n"
    s+=result.summary+"\n"
    s+="Summary by Block\n----------------\n"
    s+=resulr.summary2

	# Create a Flask response
    output = make_response(s)
	# Set the headers to indicate that it is downloadable csv data
    output.headers["Content-Disposition"] = "attachment; filename=thomasmoor-markets.csv"
    output.headers["Content-type"] = "text/csv"

  # Redirect to avoid "Form Resubmission" pop-up
  if request.method=='POST':
    logging.debug("branch: redirect")
    logging.debug(f"branch: redirect - Session text:   {session['text'][0:100]}")
    logging.debug(f"branch: redirect - Session result: {session['result'][0:100]}")
    return redirect(url_for('slash'))
  
  # Render page
  else:
    logging.debug("branch: render - index.html")
    if 'result' in session:
      logging.debug("branch: render - result in session")
      j=session['result']
      logging.debug(f" branch: render - result json: {j}")
      if j:
        result=json.loads(session['result'])
      else:
        result={
          'summary': '',
          'summary2': '',
        }
    else:
        result={
          'summary': '',
          'summary2': '',
        }
    if 'text' in session:
      sessiontext=session['text']
    else:
      sessiontext=''
	  
    logging.debug(f"render index.html - sessiontext:")
    logging.debug(sessiontext)
    logging.debug(f"render index.html - result:")
    logging.debug(result)
    return render_template("index.html", result=result,sessiontext=sessiontext)
# slash

summarizer=pipeline('summarization',model=model)

if __name__ == '__main__':
  app.run(debug=True,host='0.0.0.0',port=5104)
