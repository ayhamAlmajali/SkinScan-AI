# SkinScan AI

SkinScan AI is an AI-powered web application for preliminary skin disease classification using deep learning. Users can upload a skin image and receive an AI prediction with confidence scores and disease information.

> ⚠️ This system is intended for educational and preliminary screening purposes only. It is **not** a medical diagnosis.

---

## Features

- AI-based skin disease classification
- Flask web application
- Modern responsive user interface
- Drag-and-drop image upload
- Confidence score visualization
- Top-3 prediction probabilities
- Disease description, symptoms, causes, and recommendations
- Fast image preprocessing and inference

---

## Supported Classes

- Acne
- Eczema
- Psoriasis
- Skin Cancer
- Unknown / Normal
- Vitiligo

---

## Project Structure

```
SkinScan-AI/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── model/
│   └── SkinScanAI_Model.keras
│
├── notebooks/
│   └── Train.ipynb
│
├── static/
│   ├── css/
│   ├── js/
│   └── uploads/
│
└── templates/
    └── index.html
```

---

## Model Setup

The trained model is **not included** in this repository because GitHub does not allow files larger than 100 MB.

Download the trained model from:

https://drive.google.com/file/d/1Tyfnyto2jjf31OSGTXIINyk4tytQVmqY/view?usp=sharing

After downloading, place it inside:

```
model/
└── SkinScanAI_Model.keras
```

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Run the Application

```bash
python app.py
```

Then open:

```
http://127.0.0.1:5000
```

---

## Technologies Used

- Python
- Flask
- TensorFlow
- Keras
- EfficientNetV2-B3
- HTML5
- CSS3
- JavaScript
- Pillow (PIL)
- NumPy

---

## Dataset

The dataset was collected from Kaggle and contains labeled skin disease images belonging to six classes.

---

## Disclaimer

This AI system is designed for educational and preliminary screening purposes only.

It is **NOT** a medical diagnosis.

Always consult a qualified dermatologist for professional medical advice.

---

## Author

**Ayham Al-Majali**

Data Science & Artificial Intelligence Student

Mu'tah University

GitHub: https://github.com/ayhamAlmajali
