const config = window.SKINSCAN_CONFIG || {};
const diseaseInfo = config.diseaseInfo || {};

const imageInput = document.getElementById("imageInput");
const browseButton = document.getElementById("browseButton");
const analyzeButton = document.getElementById("analyzeButton");
const dropZone = document.getElementById("dropZone");
const previewImage = document.getElementById("previewImage");
const previewPlaceholder = document.getElementById("previewPlaceholder");
const fileMeta = document.getElementById("fileMeta");
const resultLabel = document.getElementById("resultLabel");
const confidenceBadge = document.getElementById("confidenceBadge");
const confidenceValue = document.getElementById("confidenceValue");
const predictionTime = document.getElementById("predictionTime");
const imageResolution = document.getElementById("imageResolution");
const uploadFilename = document.getElementById("uploadFilename");
const analysisSummary = document.getElementById("analysisSummary");
const topPredictions = document.getElementById("topPredictions");
const infoTitle = document.getElementById("infoTitle");
const infoDescription = document.getElementById("infoDescription");
const infoSymptoms = document.getElementById("infoSymptoms");
const infoCauses = document.getElementById("infoCauses");
const infoRecommendations = document.getElementById("infoRecommendations");
const loadingOverlay = document.getElementById("loadingOverlay");
const toast = document.getElementById("toast");
const loadingText = loadingOverlay.querySelector("p");

let currentFile = null;
let currentPreviewUrl = null;
let loaderTimer = null;
let loaderStep = 0;
const loaderMessages = ["Analyzing image...", "Running AI model...", "Almost done..."];

const baseInfo = {
  title: "Prediction details will appear here",
  description: "The model result will populate this section with a helpful summary, likely symptoms, causes, and general recommendations.",
  symptoms: [],
  causes: [],
  recommendations: [],
};

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => toast.classList.remove("show"), 3200);
}

function setLoading(isLoading) {
  loadingOverlay.classList.toggle("active", isLoading);
  analyzeButton.disabled = isLoading;
  browseButton.disabled = isLoading;

  if (isLoading) {
    loaderStep = 0;
    loadingText.textContent = loaderMessages[0];
    clearInterval(loaderTimer);
    loaderTimer = setInterval(() => {
      loaderStep = (loaderStep + 1) % loaderMessages.length;
      loadingText.textContent = loaderMessages[loaderStep];
    }, 1200);
    return;
  }

  clearInterval(loaderTimer);
  loaderTimer = null;
}

function updateFileMeta(file) {
  if (!file) {
    fileMeta.textContent = "No image selected yet.";
    return;
  }

  const sizeMb = (file.size / (1024 * 1024)).toFixed(2);
  fileMeta.textContent = `${file.name} | ${sizeMb} MB`;
}

function renderPreview(file) {
  if (currentPreviewUrl) {
    URL.revokeObjectURL(currentPreviewUrl);
  }

  currentPreviewUrl = URL.createObjectURL(file);
  previewImage.src = currentPreviewUrl;
  previewImage.style.display = "block";
  previewPlaceholder.style.display = "none";
  currentFile = file;
  updateFileMeta(file);
}

function resetResult() {
  resultLabel.textContent = baseInfo.title;
  confidenceBadge.textContent = "--";
  confidenceBadge.className = "confidence-badge confidence-neutral";
  confidenceValue.textContent = "--";
  predictionTime.textContent = "--";
  imageResolution.textContent = "--";
  uploadFilename.textContent = "--";
  analysisSummary.textContent = "Based on the uploaded image, the AI model will generate an automatic summary after analysis.";
  topPredictions.innerHTML = "";
  renderDiseaseInfo(baseInfo);
}

function renderDiseaseInfo(info) {
  infoTitle.textContent = info.title || baseInfo.title;
  infoDescription.textContent = info.description || baseInfo.description;

  const populateList = (element, items) => {
    element.innerHTML = "";
    if (!items || items.length === 0) {
      const emptyItem = document.createElement("li");
      emptyItem.textContent = "No details available yet.";
      element.appendChild(emptyItem);
      return;
    }

    items.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      element.appendChild(li);
    });
  };

  populateList(infoSymptoms, info.symptoms || []);
  populateList(infoCauses, info.causes || []);
  populateList(infoRecommendations, info.recommendations || []);
}

function confidenceClassFromValue(confidence) {
  if (confidence > 80) return "confidence-green";
  if (confidence > 50) return "confidence-orange";
  return "confidence-red";
}

function progressClassFromValue(confidence) {
  if (confidence > 80) return "progress-green";
  if (confidence > 50) return "progress-orange";
  return "progress-red";
}

function renderTopPredictions(items) {
  topPredictions.innerHTML = "";

  items.forEach((item) => {
    const row = document.createElement("div");
    row.className = "prediction-item";

    const topLine = document.createElement("div");
    topLine.className = "prediction-topline";
    topLine.innerHTML = `<span>${item.label}</span><span>${item.percentage.toFixed(2)}%</span>`;

    const track = document.createElement("div");
    track.className = "progress-track";

    const fill = document.createElement("div");
    fill.className = `progress-fill ${progressClassFromValue(item.percentage)}`;
    fill.style.width = "0%";

    track.appendChild(fill);
    row.appendChild(topLine);
    row.appendChild(track);
    topPredictions.appendChild(row);

    requestAnimationFrame(() => {
      fill.style.width = `${Math.max(item.percentage, 2)}%`;
    });
  });
}

function renderAllProbabilities(items) {
  topPredictions.innerHTML = "";

  items.forEach((item, index) => {
    const row = document.createElement("div");
    row.className = "prediction-item prediction-item-full";
    row.style.animationDelay = `${index * 80}ms`;

    const topLine = document.createElement("div");
    topLine.className = "prediction-topline";
    topLine.innerHTML = `<span>${item.label}</span><span>${item.percentage.toFixed(2)}%</span>`;

    const track = document.createElement("div");
    track.className = "progress-track";

    const fill = document.createElement("div");
    fill.className = `progress-fill ${progressClassFromValue(item.percentage)}`;
    fill.style.width = "0%";

    track.appendChild(fill);
    row.appendChild(topLine);
    row.appendChild(track);
    topPredictions.appendChild(row);

    requestAnimationFrame(() => {
      fill.style.width = `${Math.max(item.percentage, 2)}%`;
    });
  });
}

function applyResult(data) {
  const result = data.result;
  if (data.image_url) {
    previewImage.src = data.image_url;
    previewImage.style.display = "block";
    previewPlaceholder.style.display = "none";
  }

  resultLabel.textContent = result.predicted_label;
  confidenceBadge.textContent = `${result.confidence.toFixed(2)}%`;
  confidenceBadge.className = `confidence-badge ${confidenceClassFromValue(result.confidence)}`;
  confidenceValue.textContent = `${result.confidence.toFixed(2)}%`;
  predictionTime.textContent = `${result.prediction_time_ms.toFixed(2)} ms`;
  imageResolution.textContent = result.image_resolution;
  uploadFilename.textContent = data.filename || "--";
  analysisSummary.textContent = result.analysis_summary || `Based on the uploaded image, the AI model predicts ${result.predicted_label} with ${result.confidence.toFixed(2)}% confidence. This result should be considered as an AI-assisted preliminary assessment and not a medical diagnosis.`;
  renderAllProbabilities(result.all_probabilities || result.top_predictions || []);

  const disease = diseaseInfo[result.predicted_label] || result.disease_info || baseInfo;
  renderDiseaseInfo({
    title: result.predicted_label,
    description: disease.description,
    symptoms: disease.symptoms || [],
    causes: disease.causes || [],
    recommendations: disease.recommendations || [],
  });

  showToast(`Prediction complete: ${result.predicted_label} (${result.confidence.toFixed(2)}%)`);
}

function handleError(message) {
  showToast(message);
}

async function analyzeImage() {
  if (!currentFile) {
    handleError("Please select a skin image before analyzing.");
    return;
  }

  const formData = new FormData();
  formData.append("image", currentFile);

  setLoading(true);
  try {
    const response = await fetch("/analyze", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    if (!response.ok || !data.success) {
      throw new Error(data.error || "Prediction failed.");
    }

    applyResult(data);
  } catch (error) {
    handleError(error.message || "Prediction failed.");
  } finally {
    setLoading(false);
  }
}

function handleFiles(files) {
  const [file] = files;
  if (!file) {
    return;
  }

  if (!file.type.startsWith("image/")) {
    handleError("Unsupported file type. Please upload a valid image.");
    return;
  }

  renderPreview(file);
}

browseButton.addEventListener("click", (event) => {
  event.stopPropagation();
  imageInput.click();
});

analyzeButton.addEventListener("click", (event) => {
  event.stopPropagation();
  analyzeImage();
});
imageInput.addEventListener("change", (event) => handleFiles(event.target.files));

["dragenter", "dragover"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    event.stopPropagation();
    dropZone.classList.add("dragover");
  });
});

["dragleave", "drop"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    event.stopPropagation();
    dropZone.classList.remove("dragover");
  });
});

dropZone.addEventListener("drop", (event) => {
  const { files } = event.dataTransfer;
  if (files && files.length > 0) {
    imageInput.files = files;
    handleFiles(files);
  }
});

dropZone.addEventListener("click", (event) => {
  if (event.target === dropZone) {
    imageInput.click();
  }
});

resetResult();
renderDiseaseInfo(baseInfo);
