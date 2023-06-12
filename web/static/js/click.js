
function $(id){ return document.getElementById(id);}

// JavaScript popup window function
function basicPopup(url) {
    const h = 500;
    const w = 700;
     var y = window.outerHeight / 2 + window.screenY - ( h / 2)
    var x = window.outerWidth / 2 + window.screenX - ( w / 2)
    return window.open(url, 'Add New', 'toolbar=no, location=no, directories=no, status=no, menubar=no, scrollbars=no, resizable=no, copyhistory=no, width=' + w + ', height=' + h + ', top=' + y + ', left=' + x);
}

    $("btn2").onclick = function(){

        basicPopup('/add');
        return false;
    };


const divs = document.querySelectorAll('.get-file');

divs.forEach(el => el.addEventListener('click', event => {
    var filename =  event.target.parentNode.previousSibling.previousSibling.previousSibling.previousSibling.innerHTML;
    location.href = '/download/' + filename;
}));

