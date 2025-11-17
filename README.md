# OCR Receipts Parser

This is a Python-based Telegram Bot which receives an image of a receipt and extracts useful information it.
The program uses OCR (Optical Character Recognition) techniques to extract text from an image, which is then parsed, and the important fields are extracted from it.

> It currently only supports receipts in spanish.

## ⬇️ Instalation

First, clone the repository:

```bash
# Clone the repository
git clone https://github.com/2t0rHub/ocr-receipt-parser.git
cd ocr-receipt-parser
```

### Environment variables

Create a `.env` file in the root of the project with your Telegram Bot key.

Content example:

```
TELEGRAM_BOT_KEY=1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ
```

---

### Alternatives

#### 1. 💻 Running locally

I strongly recommend creating a local environment for the dependencies.

```bash

# Create a virtual environment
python -m venv .venv
# Activate the virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

#  Install dependencies
pip install -r requirements.txt
```

#### 2. 🐋 Running as a Docker container

```bash
# Build the Docker image
docker build -t receipt-bot .

# Run it
docker run --name receipt-bot receipt-bot
```

## ⚙️How it works

### OCR

To extract text from an image, I made use of the `easyocr` Python library.
This library extracts the text from a given image, which can be later parsed.

### Useful information parsing

This is the most complicated part by far. To obtain the information from the text, we look for keywords using regular expressions, and follow different strategies to guess where the useful information might be.

There is room for improvement in the techniques I have used, they might be a little primitive, but I thought that trining a LLM for this was not the way to start. Maybe in the future I will.

## Limitations

There are two main limiting factors, and they are the imperfections in the OCR model and the notable differences between every receipt (each one has its own and unique structure, so parsing information from it is quite hard).

Despite all of these, I managed to capture most of the info of a decent-quality image with no problems.

## Contributions

Contributions are welcome! Please open an issue or submit a pull request if you are willing to colaborate.
