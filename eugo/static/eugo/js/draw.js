var c = document.getElementById("canvas");
fitToContainer(c);
var ctx = c.getContext("2d");
var i = 0;
setInterval(function(){draw(ctx)}, 10);

function draw(ctx){
    var w = canvas.width;
    var h = canvas.height;
    ctx.strokeStyle = "#9f9f9f";
    ctx.beginPath();
    ctx.moveTo(0+i,0+i)
    ctx.lineTo(w-i,h-i)
    ctx.stroke();
    i++;
}

function fitToContainer(canvas){
    // Make it visually fill the positioned parent
    canvas.style.width ='100%';
    canvas.style.height='100%';
    // ...then set the internal size to match
    canvas.width  = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
}