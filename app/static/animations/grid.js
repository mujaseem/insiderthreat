const gridCanvas = document.getElementById("grid");
const gctx = gridCanvas.getContext("2d");

gridCanvas.width = window.innerWidth;
gridCanvas.height = window.innerHeight;

let offset = 0;

function drawGrid() {

    gctx.clearRect(0,0,gridCanvas.width,gridCanvas.height);

    gctx.strokeStyle = "rgba(59,130,246,0.15)";
    gctx.lineWidth = 1;

    const gridSize = 40;

    offset += 0.2;

    for(let x = 0; x < gridCanvas.width; x += gridSize){
        gctx.beginPath();
        gctx.moveTo(x,0);
        gctx.lineTo(x,gridCanvas.height);
        gctx.stroke();
    }

    for(let y = 0; y < gridCanvas.height; y += gridSize){
        gctx.beginPath();
        gctx.moveTo(0,y + offset);
        gctx.lineTo(gridCanvas.width,y + offset);
        gctx.stroke();
    }

    requestAnimationFrame(drawGrid);
}

drawGrid();