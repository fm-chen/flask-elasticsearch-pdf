
    function $(id){ return document.getElementById(id);}//封装的$(id)函数

    $("btn1").onclick = function(){
        var q = $("qt")
        location.href = '/search?' + q
        ;

    }

const divs = document.querySelectorAll('.get-file');


divs.forEach(el => el.addEventListener('click', event => {
  var base64 = event.target.getElementsByTagName("div")[0].innerHTML;
  var byteCharacters = atob(base64);
var byteNumbers = new Array(byteCharacters.length);
for (var i = 0; i < byteCharacters.length; i++) {
  byteNumbers[i] = byteCharacters.charCodeAt(i);
}
var byteArray = new Uint8Array(byteNumbers);
var file = new Blob([byteArray], { type: 'application/pdf;base64' });
var fileURL = URL.createObjectURL(file);
window.open(fileURL);

}));

