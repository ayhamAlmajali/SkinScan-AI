# SkinScan AI

SkinScan AI is a production-style Flask web application that classifies skin diseases from an uploaded image using a trained TensorFlow / Keras model.

## Features

- Flask backend with a single-load Keras model
- Secure image upload flow with validation and saved uploads
- 300x300 RGB preprocessing with normalization
- JSON prediction API with top-3 probabilities
- Modern responsive medical AI UI with drag-and-drop upload
- Animated loading state, confidence bars, and result cards
- Disease information cards with a medical disclaimer

## Project Structure

```text
SkinScan AI WebSite/
├── app.py
├── requirements.txt
├── model/
│   └── best_model.keras
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── uploads/
├── templates/
│   └── index.html
└── README.md
```

## Model Setup

Place your trained Keras model at:

```text
model/best_model.keras
```

The application expects six classes in this exact order:

1. Acne
2. Eczema
3. Psoriasis
4. SkinCancer
5. Unknown_Normal
6. Vitiligo

## Installation

```bash
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## API

### `POST /analyze`

Form field:

- `image`: uploaded image file

Response includes:

- predicted class
- confidence
- top 3 predictions
- prediction time
- uploaded image URL
- disease information

## Disclaimer

This AI system is designed for educational and preliminary screening purposes only. It is NOT a medical diagnosis. Always consult a qualified dermatologist.
