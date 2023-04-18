function ver_mensajes_recibidos(){
    document.querySelector('.mrecibidos').style.display = 'block';
    document.querySelector('.menviados').style.display = 'none';
}

function ver_mensajes_enviados(){
    document.querySelector('.mrecibidos').style.display = 'none';
    document.querySelector('.menviados').style.display = 'block';
}