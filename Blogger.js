<div>
  <div id="myDiv">
    <label htmlFor='video'>YouTube Video URL:</label>
    <input type='text' required id='video' />
    <!-- label htmlFor='category'>Category:</label>
    <input type='text' id='category' /-->
    <button onclick="exec()">Transcript</button>
    <br/>
    <button onclick="saveAsFile()">Download</button>
    <br/>
    <textarea cols="100" rows="20" id="text"></textarea>
  </div>
</div>

<script type='text/javascript'>
  // create an element
  const createNode = (elem) => {
    return document.createElement(elem);
  };

  // append an element to parent
  const appendNode = (parent, elem) => {
    parent.appendChild(elem);
  }
  
  function exec(){
    
    // console.log("this.video: ")
    // console.log(this.video.value)
    
    const api = 'https://thomasmoor.org/transcribeyt';

    // post body data
    const enteredData = {
      video: this.video.value
    };
    
    // create request object
    const request = new Request(api, {
      method: 'POST',
      body: JSON.stringify(enteredData),
      headers: new Headers({
        'Content-Type': 'application/json'
      })
    });
    
    text=document.getElementById("text");

    // pass request object to `fetch()`
    fetch(request)
      .then(res => res.json())
      .then(res => {
        console.log(res);
        document.getElementById('text').value = res.transcript;
        // console.log("Done.");
      }).catch(err => {
        console.error('Error: ', err);
      });

  } // exec()
  
  async function saveAsFile() {
      console.log("saveAsFile")
      var prefix = ""; // document.getElementById("category").value;
      var textToSave = document.getElementById("text").value;
      console.log("p: "+prefix+" t: "+textToSave)

      // var fileNameToSaveAs = prefix+title+" - "+author+" - "+videoId+".txt";
      var fileNameToSaveAs = "thomasmoor.org.txt";
 
      textToSave = fileNameToSaveAs + '\n\n' + textToSave
      var textToSaveAsBlob = new Blob([textToSave], {type:"text/plain"});
      var textToSaveAsURL = window.URL.createObjectURL(textToSaveAsBlob);

      var downloadLink = document.createElement("a");
      downloadLink.download = fileNameToSaveAs;
      downloadLink.innerHTML = "Download File";
      downloadLink.href = textToSaveAsURL;
      downloadLink.onclick = destroyClickedElement;
      downloadLink.style.display = "none";
      document.body.appendChild(downloadLink);
 
      downloadLink.click();
  } // saveTextAsFile
  
  async function destroyClickedElement(event){
    document.body.removeChild(event.target);
  }
  
</script>