<div>
  <div id="myDiv">
    <label htmlFor='video'>YouTube Video URL:</label>
    <input type='text' required id='video' size="50" />
    <button onclick="transcribe()">Transcript</button>
    <br/>
    <b>Transcript</b>
    <textarea cols="100" rows="20" id="transcript"></textarea>
    <br/>
    <label htmlFor='Prefix'>Prefix File Name with:</label>
    <input type='text' id='prefix' />
    <button onclick="saveAsFile()">Download</button>
    <br/><br/>
    <button onclick="summarize()">Summarize</button>
    <br/>
    <b>Summary 1</b>
    <textarea cols="100" rows="10" id="summary"></textarea>
    <b>Summary 2</b>
    <textarea cols="100" rows="5" id="summary2"></textarea>
  </div>
</div>

<script type='text/javascript'>
  
  var author=""
  var title=""
  var videoId=""
  
  const api_transcript = 'https://thomasmoor.org/transcribeyt'
  const api_summarize  = 'https://thomasmoor.org/getsummary'

  // append an element to parent
  const appendNode = (parent, elem) => {
    parent.appendChild(elem);
  }  

  // create an element
  const createNode = (elem) => {
    return document.createElement(elem)
  };
  
  async function destroyClickedElement(event){
    document.body.removeChild(event.target)
  }

  function transcribe(){
    
    // console.log("this.video: ")
    // console.log(this.video.value)
    
    document.getElementById('summary').value = ""
    document.getElementById('summary2').value = ""
    
    // post body data
    const enteredData = {
      video: this.video.value
    };
    
    // create request object
    const request = new Request(api_transcript, {
      method: 'POST',
      body: JSON.stringify(enteredData),
      headers: new Headers({
        'Content-Type': 'application/json'
      })
    })
    
    transcript=document.getElementById("transcript")

    // pass request object to `fetch()`
    fetch(request)
      .then(res => res.json())
      .then(res => {
        console.log(res)
        document.getElementById('transcript').value = res.transcript
        author=res.author
        title=res.title
        videoId=res.id
        // console.log("Done.")
      }).catch(err => {
        console.error('Error: ', err)
      });

  } // transcribe()
  
  async function saveAsFile() {
      console.log("saveAsFile")
      var prefix = document.getElementById("prefix").value
      var textToSave = document.getElementById("transcript").value
      console.log("p: "+prefix+" t: "+textToSave)

      var fileNameToSaveAs = prefix+title+" - "+author+" - "+videoId+".txt"
      // var fileNameToSaveAs = "thomasmoor.org.txt"
 
      textToSave = fileNameToSaveAs + '\n\n' + textToSave
      var textToSaveAsBlob = new Blob([textToSave], {type:"text/plain"})
      var textToSaveAsURL = window.URL.createObjectURL(textToSaveAsBlob)

      var downloadLink = document.createElement("a")
      downloadLink.download = fileNameToSaveAs
      downloadLink.innerHTML = "Download File"
      downloadLink.href = textToSaveAsURL
      downloadLink.onclick = destroyClickedElement
      downloadLink.style.display = "none"
      document.body.appendChild(downloadLink)
 
      downloadLink.click()
  } // saveTextAsFile
  
  function summarize(){
    
    // console.log("this.video: ")
    // console.log(this.video.value)
    
    // post body data
    var text=document.getElementById("transcript").value
    // const enteredData = {
    //  text: document.getElementById("transcript").value
    // };
    console.log("To API:"+api_summarize+" transcript length:"+text.length)
    
    // create request object
    const request = new Request(api_summarize, {
      method: 'POST',
      body: JSON.stringify(text),
      headers: new Headers({
        'Content-Type': 'application/json'
      })
    });
    
    // pass request object to `fetch()`
    fetch(request)
      .then(res => res.json())
      .then(res => {
        console.log(res)
        document.getElementById('summary').value = res.summary
        document.getElementById('summary2').value = res.summary2
        // console.log("Done.")
      }).catch(err => {
        console.error('Error: ', err)
      });

  } // transcribe()
  

</script>