// document.getElementById("editor").innerHTML = `Response`; 
const putMsg = (msg) => {
    editor.setValue(`${msg}`)
}

function makeRequest(){
    var formData = new FormData();
    let file = document.getElementById("ocr").getElementsByTagName("input")[0]; 
    console.log(file.files[0]);
    formData.append("file", file.files[0]); //image file 
    formData.append("language", "eng"); // select language
    formData.append("apikey", "1b6eaefe7b88957"); // api key

    // make request
    let xhr = new XMLHttpRequest();
    xhr.onload = () => { 
        if(xhr.status == 200){
            console.log(xhr);
            try{
                let jsonObj = JSON.parse(xhr.response); 
                console.log(jsonObj.ParsedResults[0].ParsedText);
                putMsg(jsonObj.ParsedResults[0].ParsedText);
            }
            catch(e){
                console.log(e);
                putMsg("Error");
            }
        }
        else {
            putMsg("Something went wrong");
        }
    };
    xhr.open("POST", "https://api8.ocr.space/parse/image");
    xhr.send(formData);
}



    let btn = document.getElementById("ocr").getElementsByTagName("input")[0];
    btn.addEventListener('change', makeRequest);
    console.log("main done");


