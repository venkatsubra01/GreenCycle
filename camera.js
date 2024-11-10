let model;
let video;
let canvas;
let bottleInfoEntity;

// Load the MobileNet model
async function loadModel() {
    model = await mobilenet.load();
    console.log('MobileNet model loaded');
}

// Set up the video stream
async function setupCamera() {
    video = document.getElementById('video');
    const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    video.srcObject = stream;
    return new Promise((resolve) => {
        video.onloadedmetadata = () => {
            resolve(video);
        };
    });
}

// Predict the content of the image
async function predict() {
    canvas = document.getElementById('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);

    const imgData = canvas.getContext('2d').getImageData(0, 0, canvas.width, canvas.height);
    const predictions = await model.classify(imgData);
    console.log(predictions);

    // Check if any prediction is related to a bottle
    const bottlePrediction = predictions.find(p => p.className.toLowerCase().includes('bottle'));
    
    if (bottlePrediction) {
        updateBottleInfo(bottlePrediction.className, bottlePrediction.probability);
    } else {
        updateBottleInfo('No bottle detected', 0);
    }
}

// Update the AR text with bottle information
function updateBottleInfo(label, probability) {
    bottleInfoEntity = document.getElementById('bottleInfo');
    bottleInfoEntity.setAttribute('text', {
        value: `${label}\nConfidence: ${(probability * 100).toFixed(2)}%`
    });
}

// Main function to run the AR bottle recognition
async function run() {
    await loadModel();
    await setupCamera();
    bottleInfoEntity = document.getElementById('bottleInfo');

    video.play();

    // Predict every 3 seconds
    setInterval(predict, 3000);
}

// Start the application
run();