// Backend API base URL
const API_BASE_URL = "http://127.0.0.1:8000";

// DOM elements
const imageInput = document.getElementById("image-input");
const imagePreviewContainer = document.getElementById("image-preview-container");
const imagePreview = document.getElementById("image-preview");
const uploadText = document.getElementById("upload-text");
const heightInput = document.getElementById("height-input");
const genderSelect = document.getElementById("gender-select");
const detectBtn = document.getElementById("detect-btn");
const loading = document.getElementById("loading");
const errorMessage = document.getElementById("error-message");
const results = document.getElementById("results");
const recommendedSize = document.getElementById("recommended-size");
const confidence = document.getElementById("confidence");
const measurementsList = document.getElementById("measurements-list");
const fitAdvice = document.getElementById("fit-advice");
const resetBtn = document.getElementById("reset-btn");

// Store selected file
let selectedFile = null;

// =====================================
// EVENT LISTENERS
// =====================================

// Image preview when user selects file
imageInput.addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (!file) return;
  
  selectedFile = file;
  
  // Show preview
  const reader = new FileReader();
  reader.onload = (event) => {
    imagePreview.src = event.target.result;
    imagePreviewContainer.classList.remove("hidden");
    uploadText.textContent = "✅ " + file.name;
  };
  reader.readAsDataURL(file);
});

// Detect button click
detectBtn.addEventListener("click", async () => {
  // Validation
  if (!selectedFile) {
    showError("Please upload a photo first");
    return;
  }
  
  const height = parseFloat(heightInput.value);
  if (!height || height < 100 || height > 220) {
    showError("Please enter a valid height (100-220 cm)");
    return;
  }
  
  // Start processing
  await processSizeDetection(selectedFile, height, genderSelect.value);
});

// Reset button click
resetBtn.addEventListener("click", () => {
  selectedFile = null;
  imageInput.value = "";
  heightInput.value = "";
  imagePreviewContainer.classList.add("hidden");
  uploadText.textContent = "📷 Upload your photo";
  results.classList.add("hidden");
  errorMessage.classList.add("hidden");
});

// =====================================
// API CALLS
// =====================================

async function processSizeDetection(file, height, gender) {
  hideError();
  hideResults();
  showLoading();
  detectBtn.disabled = true;
  
  try {
    // Step 1: Upload image
    const uploadResult = await uploadImage(file);
    
    // Step 2: Get size recommendation
    const sizeResult = await getSizeRecommendation(
      uploadResult.upload_id,
      height,
      gender
    );
    
    // Step 3: Display results
    displayResults(sizeResult);
    
  } catch (error) {
    showError(error.message || "Something went wrong. Please try again.");
  } finally {
    hideLoading();
    detectBtn.disabled = false;
  }
}

async function uploadImage(file) {
  const formData = new FormData();
  formData.append("file", file);
  
  const response = await fetch(`${API_BASE_URL}/api/upload-image`, {
    method: "POST",
    body: formData
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Image upload failed");
  }
  
  return await response.json();
}

async function getSizeRecommendation(uploadId, height, gender) {
  const response = await fetch(`${API_BASE_URL}/api/recommend-size`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      upload_id: uploadId,
      user_height_cm: height,
      user_gender: gender
    })
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Size recommendation failed");
  }
  
  return await response.json();
}

// =====================================
// UI HELPERS
// =====================================

function displayResults(data) {
  recommendedSize.textContent = data.recommended_size;
  
  const confidencePercent = Math.round(data.confidence_score * 100);
  confidence.textContent = `${confidencePercent}% confidence`;
  
  // Build measurements list
  const m = data.measurements_used;
  measurementsList.innerHTML = `
    <div class="measurement-item">
      <span class="measurement-label">Shoulder</span>
      <span class="measurement-value">${m.shoulder_width_cm.toFixed(1)} cm</span>
    </div>
    <div class="measurement-item">
      <span class="measurement-label">Chest (width)</span>
      <span class="measurement-value">${m.chest_width_cm.toFixed(1)} cm</span>
    </div>
    <div class="measurement-item">
      <span class="measurement-label">Hip</span>
      <span class="measurement-value">${m.hip_width_cm.toFixed(1)} cm</span>
    </div>
    <div class="measurement-item">
      <span class="measurement-label">Torso length</span>
      <span class="measurement-value">${m.torso_length_cm.toFixed(1)} cm</span>
    </div>
    <div class="measurement-item">
      <span class="measurement-label">Arm length</span>
      <span class="measurement-value">${m.arm_length_cm.toFixed(1)} cm</span>
    </div>
  `;
  
  // Fit advice
  fitAdvice.textContent = data.fit_advice;
  
  results.classList.remove("hidden");
}

function showLoading() {
  loading.classList.remove("hidden");
}

function hideLoading() {
  loading.classList.add("hidden");
}

function showError(message) {
  errorMessage.textContent = "⚠️ " + message;
  errorMessage.classList.remove("hidden");
}

function hideError() {
  errorMessage.classList.add("hidden");
}

function hideResults() {
  results.classList.add("hidden");
}