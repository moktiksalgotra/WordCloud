# Word Cloud Generator

A full-stack web application that generates beautiful word clouds from text input. Built with React frontend and Python Flask backend.

## Features

- **Text Processing**: Advanced text preprocessing with tokenization, normalization, and stopword removal
- **Customizable Options**: Toggle stopword removal, custom stopword lists, and mask shapes
- **Real-time Generation**: Instant word cloud generation with loading states
- **Responsive Design**: Modern UI built with Tailwind CSS
- **Multiple Mask Shapes**: Circle, heart, and custom image upload support

## Architecture

- **Frontend**: React + Tailwind CSS
- **Backend**: Python Flask + wordcloud + nltk
- **Communication**: RESTful API with JSON payloads and base64 image transfer

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download NLTK data:
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

5. Run the Flask server:
```bash
python app.py
```

The backend will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

- `POST /generate_wordcloud`: Generate word cloud from text input
  - Request body: JSON with `text`, `remove_stopwords`, `custom_stopwords`, `mask_shape`
  - Response: JSON with `image_base64` and `word_frequencies`

## Usage

1. Open the application in your browser
2. Paste or type your text in the input area
3. Configure options (stopword removal, mask shape)
4. Click "Generate Word Cloud"
5. View and download your generated word cloud

## Technologies Used

- **Frontend**: React, Tailwind CSS, Axios
- **Backend**: Flask, wordcloud, nltk, matplotlib, PIL
- **Development**: npm, pip, virtual environments 