const statusElement = document.getElementById("status");
const penButton = document.getElementById("penButton");
const eraserButton = document.getElementById("eraserButton");
const clearButton = document.getElementById("clearButton");
const doneButton = document.getElementById("doneButton");
const brushSizeInput = document.getElementById("brushSize");
const canvasShell = document.getElementById("canvasShell");
const referenceCanvas = document.getElementById("referenceCanvas");
const drawingCanvas = document.getElementById("drawingCanvas");

const referenceContext = referenceCanvas.getContext("2d");
const drawingContext = drawingCanvas.getContext("2d");

let brushMode = "pen";
let drawing = false;
let pointerId = null;
let promptVersion = -1;
let promptImage = null;
let hasLocalChanges = false;

function setStatus(message) {
    statusElement.textContent = message;
}

function setMode(nextMode) {
    brushMode = nextMode;
    penButton.classList.toggle("is-active", nextMode === "pen");
    eraserButton.classList.toggle("is-active", nextMode === "eraser");
}

function resizeCanvases() {
    const bounds = canvasShell.getBoundingClientRect();
    const width = Math.max(1, Math.floor(bounds.width));
    const height = Math.max(420, Math.floor(bounds.height));

    const snapshot = document.createElement("canvas");
    snapshot.width = drawingCanvas.width;
    snapshot.height = drawingCanvas.height;
    snapshot.getContext("2d").drawImage(drawingCanvas, 0, 0);

    referenceCanvas.width = width;
    referenceCanvas.height = height;
    drawingCanvas.width = width;
    drawingCanvas.height = height;

    drawReferenceImage();
    drawingContext.drawImage(snapshot, 0, 0, width, height);
    drawingContext.lineCap = "round";
    drawingContext.lineJoin = "round";
}

function drawReferenceImage() {
    referenceContext.clearRect(0, 0, referenceCanvas.width, referenceCanvas.height);
    if (!promptImage) {
        return;
    }

    const canvasAspect = referenceCanvas.width / referenceCanvas.height;
    const imageAspect = promptImage.width / promptImage.height;
    let drawWidth = referenceCanvas.width;
    let drawHeight = referenceCanvas.height;
    let x = 0;
    let y = 0;

    if (imageAspect > canvasAspect) {
        drawHeight = referenceCanvas.width / imageAspect;
        y = (referenceCanvas.height - drawHeight) / 2;
    } else {
        drawWidth = referenceCanvas.height * imageAspect;
        x = (referenceCanvas.width - drawWidth) / 2;
    }

    referenceContext.fillStyle = "#fffaf2";
    referenceContext.fillRect(0, 0, referenceCanvas.width, referenceCanvas.height);
    referenceContext.drawImage(promptImage, x, y, drawWidth, drawHeight);
}

function pointerPosition(event) {
    const rect = drawingCanvas.getBoundingClientRect();
    return {
        x: (event.clientX - rect.left) * (drawingCanvas.width / rect.width),
        y: (event.clientY - rect.top) * (drawingCanvas.height / rect.height),
    };
}

function beginStroke(event) {
    if (!promptImage) {
        return;
    }
    event.preventDefault();
    drawing = true;
    pointerId = event.pointerId;
    drawingCanvas.setPointerCapture(pointerId);

    const position = pointerPosition(event);
    drawingContext.beginPath();
    drawingContext.moveTo(position.x, position.y);
    drawingContext.lineWidth = Number(brushSizeInput.value);

    if (brushMode === "eraser") {
        drawingContext.globalCompositeOperation = "destination-out";
        drawingContext.strokeStyle = "rgba(0, 0, 0, 1)";
    } else {
        drawingContext.globalCompositeOperation = "source-over";
        drawingContext.strokeStyle = "#141414";
    }
}

function continueStroke(event) {
    if (!drawing || event.pointerId !== pointerId) {
        return;
    }
    event.preventDefault();
    const position = pointerPosition(event);
    drawingContext.lineTo(position.x, position.y);
    drawingContext.stroke();
    hasLocalChanges = true;
}

function endStroke(event) {
    if (!drawing || event.pointerId !== pointerId) {
        return;
    }
    event.preventDefault();
    drawing = false;
    drawingCanvas.releasePointerCapture(pointerId);
    pointerId = null;
    drawingContext.closePath();
}

function clearDrawing() {
    drawingContext.clearRect(0, 0, drawingCanvas.width, drawingCanvas.height);
    hasLocalChanges = false;
}

function exportDrawing() {
    const exportCanvas = document.createElement("canvas");
    exportCanvas.width = referenceCanvas.width;
    exportCanvas.height = referenceCanvas.height;
    const exportContext = exportCanvas.getContext("2d");
    exportContext.drawImage(referenceCanvas, 0, 0);
    exportContext.drawImage(drawingCanvas, 0, 0);
    return exportCanvas.toDataURL("image/png");
}

async function submitDrawing(done) {
    if (!promptImage) {
        setStatus("Waiting for the agent to send a reference image.");
        return;
    }

    const response = await fetch("/api/drawing", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: exportDrawing(), done }),
    });

    if (!response.ok) {
        setStatus("Failed to save the drawing.");
        return;
    }

    hasLocalChanges = false;
    setStatus(done ? "Drawing saved. The agent can retrieve it now." : "Draft saved.");
}

async function loadPromptImage(dataUrl) {
    if (!dataUrl) {
        promptImage = null;
        referenceContext.clearRect(0, 0, referenceCanvas.width, referenceCanvas.height);
        clearDrawing();
        setStatus("Waiting for the agent to send a reference image.");
        return;
    }

    const image = new Image();
    image.src = dataUrl;
    await image.decode();
    promptImage = image;
    clearDrawing();
    drawReferenceImage();
    setStatus("Reference image received. Draw on top of it and press Done when finished.");
}

async function pollState() {
    try {
        const response = await fetch("/api/state", { cache: "no-store" });
        if (!response.ok) {
            throw new Error("State request failed.");
        }

        const state = await response.json();
        if (state.version !== promptVersion) {
            promptVersion = state.version;
            await loadPromptImage(state.promptImage);
        } else if (state.drawingReady && !hasLocalChanges) {
            setStatus("Drawing saved. The agent can retrieve it now.");
        }
    } catch (error) {
        setStatus("Flask UI is running, but state polling failed.");
    }
}

penButton.addEventListener("click", () => setMode("pen"));
eraserButton.addEventListener("click", () => setMode("eraser"));
clearButton.addEventListener("click", clearDrawing);
doneButton.addEventListener("click", () => submitDrawing(true));

drawingCanvas.addEventListener("pointerdown", beginStroke);
drawingCanvas.addEventListener("pointermove", continueStroke);
drawingCanvas.addEventListener("pointerup", endStroke);
drawingCanvas.addEventListener("pointercancel", endStroke);
drawingCanvas.addEventListener("pointerleave", endStroke);

window.addEventListener("resize", resizeCanvases);

resizeCanvases();
setMode("pen");
pollState();
window.setInterval(pollState, 2000);