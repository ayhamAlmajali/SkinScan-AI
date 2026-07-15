from __future__ import annotations

import os

import time
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request, url_for
from PIL import Image, UnidentifiedImageError
from werkzeug.utils import secure_filename

try:
    import numpy as np
except ImportError as exc:  # pragma: no cover - environment issue
    raise RuntimeError("NumPy is required for SkinScan AI") from exc

try:
    import keras
    print("Keras Version:", keras.__version__)
    print("Backend:", keras.config.backend())
except ImportError as exc:
    raise RuntimeError("Keras 3 is required for SkinScan AI") from exc

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model" / "SkinScanAI_Model.keras"
import gdown

MODEL_URL = "https://drive.google.com/uc?id=1Tyfnyto2jjf31OSGTXIINyk4tytQVmqY"

if not MODEL_PATH.exists():
    print("Downloading AI model...")
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    gdown.download(
        MODEL_URL,
        str(MODEL_PATH),
        quiet=False,
    )
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp"}
IMAGE_SIZE = (300, 300)
CLASS_NAMES = [
    "Acne",
    "Eczema",
    "Psoriasis",
    "SkinCancer",
    "Unknown_Normal",
    "Vitiligo",
]

DISEASE_INFO = {
    "Acne": {
        "description": "A common inflammatory skin condition caused by blocked pores, excess oil, and bacteria.",
        "symptoms": ["Whiteheads", "Blackheads", "Pimples", "Inflamed bumps"],
        "causes": ["Hormonal changes", "Excess sebum", "Bacteria", "Clogged follicles"],
        "recommendations": ["Use gentle cleansers", "Avoid picking lesions", "Consult a dermatologist for persistent acne"],
    },
    "Eczema": {
        "description": "A chronic condition that weakens the skin barrier and causes dryness and inflammation.",
        "symptoms": ["Dry skin", "Itchiness", "Red patches", "Cracked skin"],
        "causes": ["Genetics", "Allergens", "Irritants", "Immune triggers"],
        "recommendations": ["Moisturize regularly", "Avoid harsh soaps", "Identify personal triggers"],
    },
    "Psoriasis": {
        "description": "An immune-mediated condition that accelerates skin cell growth and produces scaly plaques.",
        "symptoms": ["Thick scales", "Red plaques", "Itching", "Nail changes"],
        "causes": ["Immune system dysregulation", "Family history", "Stress", "Environmental triggers"],
        "recommendations": ["Use prescribed topical therapy", "Keep skin moisturized", "Seek follow-up for flare control"],
    },
    "SkinCancer": {
        "description": "A potentially serious condition that requires prompt medical evaluation of suspicious skin lesions.",
        "symptoms": ["Changing mole", "Irregular border", "Asymmetry", "Non-healing lesion"],
        "causes": ["UV exposure", "Tanning beds", "Genetics", "History of sunburns"],
        "recommendations": ["Schedule urgent dermatology review", "Monitor lesion changes", "Use broad-spectrum sunscreen"],
    },
    "Unknown_Normal": {
        "description": "The image appears closer to normal skin or outside the trained disease patterns.",
        "symptoms": ["No obvious lesion", "Minimal irritation", "Skin texture within normal range"],
        "causes": ["Healthy skin", "Non-target condition", "Insufficient disease features"],
        "recommendations": ["Continue routine skin care", "Re-upload if the photo is unclear", "Consult a clinician if symptoms persist"],
    },
    "Vitiligo": {
        "description": "A pigment-loss condition that creates patchy depigmented areas on the skin.",
        "symptoms": ["White patches", "Loss of pigment", "Symmetry on both sides", "Premature hair whitening"],
        "causes": ["Autoimmune activity", "Genetics", "Oxidative stress", "Triggering skin injury"],
        "recommendations": ["Protect depigmented skin from the sun", "Discuss treatment options with a dermatologist", "Track changes over time"],
    },
}

DISCLAIMER = (
    "This AI system is designed for educational and preliminary screening purposes only. "
    "It is NOT a medical diagnosis. Always consult a qualified dermatologist."
)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["UPLOAD_FOLDER"] = str(UPLOAD_DIR)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "skinscan-ai-secret-key")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)





def load_model_once():
    if not MODEL_PATH.exists():
        return None, f"Deployment weights file not found at {MODEL_PATH}"

    try:
        model = keras.models.load_model(
        MODEL_PATH,
        compile=False,
        safe_mode=False
        )
        return model, None
    except Exception as exc:  
        return None, f"Failed to load deployment weights: {exc}"


MODEL, MODEL_ERROR = load_model_once()


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def preprocess_image(image_path: Path) -> tuple[np.ndarray, tuple[int, int]]:
    try:
        with Image.open(image_path) as image:
            image = image.convert("RGB")
            original_size = image.size
            image = image.resize(IMAGE_SIZE, Image.Resampling.LANCZOS)
            array = np.asarray(image, dtype=np.float32)
            array = np.expand_dims(array, axis=0)
            return array, original_size
    except UnidentifiedImageError as exc:
        raise ValueError("Unsupported image format. Please upload a valid JPG, PNG, WEBP, or BMP image.") from exc


def generate_analysis_summary(disease_name: str, confidence: float) -> str:
    confidence_text = f"high confidence" if confidence >= 80 else "moderate confidence" if confidence >= 50 else "lower confidence"
    return (
        f"Based on the uploaded image, the AI model predicts {disease_name} with {confidence_text}. "
        "This result should be considered as an AI-assisted preliminary assessment and not a medical diagnosis."
    )


def predict_image(image_path: Path) -> dict:
    if MODEL is None:
        raise RuntimeError(MODEL_ERROR or "Model is not available")

    processed_image, original_size = preprocess_image(image_path)
    start_time = time.perf_counter()
    predictions = MODEL.predict(processed_image, verbose=0)
    prediction_ms = round((time.perf_counter() - start_time) * 1000, 2)

    if predictions.ndim != 2 or predictions.shape[0] != 1:
        raise RuntimeError("Unexpected prediction output shape from the model.")

    probabilities = predictions[0].astype(float)
    if probabilities.size != len(CLASS_NAMES):
        raise RuntimeError("Model output classes do not match the configured labels.")

    ranked_indices = np.argsort(probabilities)[::-1]
    all_probabilities = [
        {
            "label": CLASS_NAMES[index],
            "percentage": round(float(probabilities[index]) * 100, 2),
        }
        for index in ranked_indices
    ]
    top_predictions = []
    for index in ranked_indices[:3]:
        probability = float(probabilities[index])
        top_predictions.append(
            {
                "label": CLASS_NAMES[index],
                "probability": round(probability, 4),
                "percentage": round(probability * 100, 2),
                "color": confidence_color(probability * 100),
            }
        )

    best_index = int(ranked_indices[0])
    best_probability = float(probabilities[best_index])
    best_label = CLASS_NAMES[best_index]

    return {
        "predicted_label": best_label,
        "confidence": round(best_probability * 100, 2),
        "confidence_color": confidence_color(best_probability * 100),
        "analysis_summary": generate_analysis_summary(best_label, best_probability * 100),
        "top_predictions": top_predictions,
        "all_probabilities": all_probabilities,
        "prediction_time_ms": prediction_ms,
        "image_resolution": f"{original_size[0]} x {original_size[1]}",
        "disease_info": DISEASE_INFO[best_label],
    }


def confidence_color(confidence_percentage: float) -> str:
    if confidence_percentage > 80:
        return "green"
    if confidence_percentage > 50:
        return "orange"
    return "red"


@app.route("/")
def index():
    return render_template(
        "index.html",
        app_name="SkinScan AI",
        class_names=CLASS_NAMES,
        disease_info=DISEASE_INFO,
        disclaimer=DISCLAIMER,
        model_ready=MODEL is not None,
        model_error=MODEL_ERROR,
    )


@app.route("/analyze", methods=["POST"])
def analyze():
    if MODEL is None:
        return jsonify({"success": False, "error": MODEL_ERROR or "Model is not available."}), 503

    if "image" not in request.files:
        return jsonify({"success": False, "error": "Please upload an image before analyzing."}), 400

    file = request.files["image"]
    if not file or file.filename.strip() == "":
        return jsonify({"success": False, "error": "Please choose a skin image to analyze."}), 400

    if not allowed_file(file.filename):
        return jsonify({"success": False, "error": "Unsupported file type. Use JPG, PNG, WEBP, or BMP."}), 400

    safe_name = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{safe_name}"
    upload_path = UPLOAD_DIR / unique_name
    file.save(upload_path)

    try:
        result = predict_image(upload_path)
    except ValueError as exc:
        if upload_path.exists():
            upload_path.unlink(missing_ok=True)
        return jsonify({"success": False, "error": str(exc)}), 400
    except Exception as exc:
        if upload_path.exists():
            upload_path.unlink(missing_ok=True)
        return jsonify({"success": False, "error": f"Prediction failed: {exc}"}), 500

    return jsonify(
        {
            "success": True,
            "image_url": url_for("static", filename=f"uploads/{unique_name}"),
            "filename": safe_name,
            "result": result,
            "disclaimer": DISCLAIMER,
        }
    )


@app.errorhandler(413)
def too_large(_: Exception):
    return jsonify({"success": False, "error": "Image is too large. Please upload a file smaller than 16 MB."}), 413


@app.errorhandler(500)
def internal_error(_: Exception):
    return jsonify({"success": False, "error": "An unexpected server error occurred. Please try again."}), 500


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=debug_mode)
