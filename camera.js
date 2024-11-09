const videoElement = document.getElementById('videoElement');
const captureButton = document.getElementById('captureButton');
const canvas = document.getElementById('canvas');
const capturedImage = document.getElementById('capturedImage');

// Check if the browser supports getUserMedia
if ('mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices) {
    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
        .then(stream => {
            videoElement.srcObject = stream;
        })
        .catch(error => {
            console.error("Error accessing the camera:", error);
        });
} else {
    console.error("getUserMedia is not supported in this browser");
}

captureButton.addEventListener('click', () => {
    // Set canvas dimensions to match the video feed
    canvas.width = videoElement.videoWidth;
    canvas.height = videoElement.videoHeight;

    // Draw the current video frame on the canvas
    canvas.getContext('2d').drawImage(videoElement, 0, 0, canvas.width, canvas.height);

    // Convert the canvas content to a data URL and set it as the image source
    capturedImage.src = canvas.toDataURL('image/png');
    capturedImage.style.display = 'block';
});