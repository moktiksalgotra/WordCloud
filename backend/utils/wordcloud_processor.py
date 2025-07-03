import matplotlib
matplotlib.use('Agg')
import re
import string
import base64
import io
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw
from textblob import TextBlob
import os
from matplotlib.colors import LinearSegmentedColormap
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WordCloudProcessor:
    def __init__(self):
        """Initialize the WordCloud processor with NLTK data."""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        self.stop_words = set(stopwords.words('english'))
        
        # Standard color maps for word clouds
        self.color_maps = {
            'viridis': plt.cm.viridis,
            'plasma': plt.cm.plasma,
            'inferno': plt.cm.inferno,
            'magma': plt.cm.magma,
            'cividis': plt.cm.cividis,
            'rainbow': plt.cm.rainbow,
            'blues': plt.cm.Blues,
            'reds': plt.cm.Reds,
            'greens': plt.cm.Greens,
            'purples': plt.cm.Purples,
            'greys': plt.cm.Greys,
            'spectral': plt.cm.Spectral,
            'coolwarm': plt.cm.coolwarm
        }
        
        # Shape masks
        self.shape_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'shapes')
        os.makedirs(self.shape_dir, exist_ok=True)
        
        # Standard font options
        self.font_options = [
            'arial', 'times new roman', 'courier new', 'georgia', 
            'verdana', 'impact', 'comic sans ms', 'tahoma', 'trebuchet ms'
        ]
    
    def preprocess_text(self, text: str, remove_stopwords: bool = True, 
                       custom_stopwords: List[str] = None) -> List[str]:
        """
        Preprocess text by tokenizing, normalizing, and removing stopwords.
        
        Args:
            text: Raw input text
            remove_stopwords: Whether to remove stopwords
            custom_stopwords: Additional custom stopwords to remove
            
        Returns:
            List of preprocessed tokens
        """
        # Tokenization
        tokens = word_tokenize(text.lower())
        
        # Normalization: remove punctuation and numbers
        tokens = [token for token in tokens 
                 if token not in string.punctuation and not token.isnumeric()]
        
        # Remove single characters (except 'a' and 'i')
        tokens = [token for token in tokens 
                 if len(token) > 1 or token in ['a', 'i']]
        
        # Stopword removal
        if remove_stopwords:
            tokens = [token for token in tokens if token not in self.stop_words]
            
            # Add custom stopwords
            if custom_stopwords:
                custom_stopwords_set = set(word.lower() for word in custom_stopwords)
                tokens = [token for token in tokens if token not in custom_stopwords_set]
        
        return tokens
    
    def count_frequencies(self, tokens: List[str]) -> Dict[str, int]:
        """
        Count word frequencies from preprocessed tokens.
        
        Args:
            tokens: List of preprocessed tokens
            
        Returns:
            Dictionary of word frequencies
        """
        return dict(Counter(tokens))
    
    def create_mask(self, mask_shape: str, width: int = 800, height: int = 600, preview: bool = False) -> Optional[np.ndarray]:
        """
        Create a mask for the word cloud based on the specified shape.
        If preview=True, return a PNG bytes object for preview.
        
        Args:
            mask_shape: Name of the shape ('none', 'circle', 'heart', etc.)
            width: Width of the mask
            height: Height of the mask
            preview: If True, return bytes for direct display
            
        Returns:
            Optional numpy array or bytes object if preview=True
        """
        # Create a mask array
        if mask_shape == 'none':
            # Rectangle: no mask (all white)
            mask = None
            if preview:
                # Return a blank white image
                img = Image.new('L', (width, height), 255)
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                buffer.seek(0)
                return buffer.getvalue()
            return mask
        
        # For shapes with numpy-based generation
        if mask_shape in ['circle', 'diamond', 'star', 'triangle', 'cloud']:
            # Generate the appropriate mask array
            if mask_shape == 'circle':
                x, y = np.ogrid[:height, :width]
                center_y, center_x = height // 2, width // 2
                radius = min(center_x, center_y) * 0.8
                mask = (((x - center_y) ** 2 + (y - center_x) ** 2) < radius ** 2).astype(np.uint8) * 255
            elif mask_shape == 'diamond':
                y, x = np.ogrid[:height, :width]
                center_y, center_x = height // 2, width // 2
                max_dist = min(center_x, center_y) * 0.8
                mask = ((np.abs(y - center_y) + np.abs(x - center_x)) < max_dist).astype(np.uint8) * 255
            elif mask_shape == 'star':
                x = np.linspace(-1, 1, width)
                y = np.linspace(-1, 1, height)
                X, Y = np.meshgrid(x, y)
                R = np.sqrt(X**2 + Y**2)
                Theta = np.arctan2(Y, X)
                mask = (R < 0.5 + 0.3 * np.cos(5 * Theta + np.pi/2)).astype(np.uint8) * 255
            elif mask_shape == 'triangle':
                mask = np.zeros((height, width), dtype=np.uint8)
                h = height - 1
                w = width - 1
                for i in range(height):
                    line_width = int(w * (i/h))
                    start_x = (width - line_width) // 2
                    mask[i, start_x:start_x + line_width] = 255
            elif mask_shape == 'cloud':
                mask = np.zeros((height, width), dtype=np.uint8)
                centers = [
                    (width * 0.3, height * 0.4),
                    (width * 0.5, height * 0.3),
                    (width * 0.7, height * 0.4),
                    (width * 0.4, height * 0.5),
                    (width * 0.6, height * 0.5)
                ]
                for cx, cy in centers:
                    x, y = np.ogrid[:height, :width]
                    radius = min(width, height) * 0.2
                    circle = ((x - cy) ** 2 + (y - cx) ** 2) < radius ** 2
                    mask = np.where(circle, 255, mask)
            if preview:
                img = Image.fromarray(mask)
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                buffer.seek(0)
                return buffer.getvalue()
            return mask
        
        elif mask_shape == 'heart':
            # Create a heart shape using PIL drawing
            mask = Image.new('L', (width, height), 0)
            draw = ImageDraw.Draw(mask)
            
            center_x, center_y = width // 2, height // 2
            size = min(width, height) // 2  # Size for better fit
            
            # Create heart shape using simpler method
            # Draw two circles for the top curves and a triangle for the bottom
            radius = size // 2
            
            # Top left circle
            left_circle_x = center_x - radius
            left_circle_y = center_y - radius // 2
            draw.ellipse([left_circle_x - radius, left_circle_y - radius, 
                         left_circle_x + radius, left_circle_y + radius], fill=255)
            
            # Top right circle
            right_circle_x = center_x + radius
            right_circle_y = center_y - radius // 2
            draw.ellipse([right_circle_x - radius, right_circle_y - radius, 
                         right_circle_x + radius, right_circle_y + radius], fill=255)
            
            # Bottom triangle
            triangle_points = [
                (center_x, center_y + size),  # Bottom point
                (center_x - size * 1.2, center_y - radius // 2),  # Left point
                (center_x + size * 1.2, center_y - radius // 2)  # Right point
            ]
            draw.polygon(triangle_points, fill=255)
            
            if preview:
                buffer = io.BytesIO()
                mask.save(buffer, format='PNG')
                buffer.seek(0)
                return buffer.getvalue()
            
            # For WordCloud: 0=masked, 255=unmasked
            return np.array(mask)
        
        else:
            # Default to no mask
            return None
    
    def extract_word_context(self, text: str, words: List[str]) -> Dict[str, List[str]]:
        """
        For each word, find sentences in the text where it appears.
        Returns a dict: word -> list of sentences containing the word.
        """
        # Split text into sentences (simple split, can be improved)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        word_context = defaultdict(list)
        for sentence in sentences:
            for word in words:
                # Use word boundaries for exact match, case-insensitive
                if re.search(rf'\\b{re.escape(word)}\\b', sentence, re.IGNORECASE):
                    word_context[word].append(sentence.strip())
        return dict(word_context)
    
    def analyze_sentiment(self, text: str) -> dict:
        """
        Analyze sentiment using TextBlob. Returns polarity and subjectivity.
        """
        blob = TextBlob(text)
        return {
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity
        }
    
    def get_top_n_words(self, word_frequencies: Dict[str, int], n: int = 10) -> list:
        """
        Return a list of tuples (word, frequency) for the top N words.
        """
        # Ensure all frequency values are integers
        word_frequencies_converted = {}
        for word, freq in word_frequencies.items():
            if isinstance(freq, str):
                try:
                    word_frequencies_converted[word] = int(freq)
                except (ValueError, TypeError):
                    word_frequencies_converted[word] = 1  # Default to 1 if conversion fails
            else:
                word_frequencies_converted[word] = freq
                
        return sorted(word_frequencies_converted.items(), key=lambda x: x[1], reverse=True)[:n]
    
    def generate_wordcloud(self, text: str, remove_stopwords: bool = True,
                          custom_stopwords: List[str] = None,
                          mask_shape: str = 'none',
                          min_frequency: int = None,
                          max_frequency: int = None,
                          width: int = 800,
                          height: int = 600,
                          color_scheme: str = 'viridis',
                          background_color: str = 'white',
                          prefer_horizontal: float = 0.7,
                          relative_scaling: float = 0.5,
                          max_words: int = 200,
                          min_font_size: int = 10,
                          max_font_size: int = 100) -> Tuple[str, Dict[str, int], Dict[str, List[str]], dict, list]:
        """
        Generate a word cloud from input text.
        Always use a rectangular shape (no mask).
        
        Args:
            text: Raw input text
            remove_stopwords: Whether to remove stopwords
            custom_stopwords: Additional custom stopwords
            mask_shape: Shape for the word cloud ('none', 'circle', 'heart')
            min_frequency: Minimum frequency for a word to appear
            max_frequency: Maximum frequency for a word to appear
            width: Image width
            height: Image height
            color_scheme: Color scheme for the word cloud
            background_color: Background color for the word cloud
            prefer_horizontal: Ratio of horizontal to vertical word placement (0.0 to 1.0)
            relative_scaling: Importance of word frequency for font size (0.0 to 1.0)
            max_words: Maximum number of words in the cloud
            min_font_size: Minimum font size for words
            max_font_size: Maximum font size for words
            
        Returns:
            Tuple of (base64_image_string, word_frequencies, word_context, sentiment, top_words)
        """
        logger.info(f"Starting generate_wordcloud with min_frequency={min_frequency} (type: {type(min_frequency).__name__}), max_frequency={max_frequency} (type: {type(max_frequency).__name__})")
        
        # Preprocess text
        tokens = self.preprocess_text(text, remove_stopwords, custom_stopwords)
        if not tokens:
            raise ValueError("No valid words found after preprocessing")
        
        # Count frequencies
        word_frequencies = self.count_frequencies(tokens)
        logger.info(f"Found {len(word_frequencies)} unique words before frequency filtering")
        
        # Apply frequency thresholds
        if min_frequency is not None:
            logger.info(f"Applying min_frequency filter: {min_frequency}")
            try:
                min_freq_value = int(min_frequency)
                logger.info(f"Converted min_frequency to {min_freq_value}")
                filtered_words = {}
                for w, f in word_frequencies.items():
                    # Ensure both values are integers for comparison
                    word_freq = int(f) if isinstance(f, str) else f
                    if word_freq >= min_freq_value:
                        filtered_words[w] = f
                word_frequencies = filtered_words
                logger.info(f"After min_frequency filter: {len(word_frequencies)} words remain")
            except (ValueError, TypeError) as e:
                # If conversion fails, log the error but continue without filtering
                logger.error(f"Invalid min_frequency value: {min_frequency}, expected an integer. Error: {str(e)}")
                
        if max_frequency is not None:
            logger.info(f"Applying max_frequency filter: {max_frequency}")
            try:
                max_freq_value = int(max_frequency)
                logger.info(f"Converted max_frequency to {max_freq_value}")
                filtered_words = {}
                for w, f in word_frequencies.items():
                    # Ensure both values are integers for comparison
                    word_freq = int(f) if isinstance(f, str) else f
                    if word_freq <= max_freq_value:
                        filtered_words[w] = f
                word_frequencies = filtered_words
                logger.info(f"After max_frequency filter: {len(word_frequencies)} words remain")
            except (ValueError, TypeError) as e:
                # If conversion fails, log the error but continue without filtering
                logger.error(f"Invalid max_frequency value: {max_frequency}, expected an integer. Error: {str(e)}")
        
        if not word_frequencies:
            raise ValueError("No words meet the frequency threshold criteria.")
        
        # Limit the number of words to prevent overcrowding
        max_words = min(len(word_frequencies), max_words)
        
        # Map frontend color scheme names to matplotlib colormap names
        color_map_translation = {
            'reds': 'Reds',
            'blues': 'Blues',
            'greens': 'Greens',
            'purples': 'Purples',
            'greys': 'Greys',
            'spectral': 'Spectral',
            'coolwarm': 'coolwarm',
            'viridis': 'viridis',
            'plasma': 'plasma',
            'inferno': 'inferno',
            'magma': 'magma',
            'cividis': 'cividis',
            'rainbow': 'rainbow',
            # ... add more as needed ...
        }
        mapped_color_scheme = color_map_translation.get(color_scheme.lower(), color_scheme)
        
        # Map frontend background color names to valid color codes
        background_color_translation = {
            'lightred': '#fff0f0',
            'lightgrey': '#f0f0f0',
            'darkgrey': '#333333',
            'lightblue': '#e6f7ff',
            'lightgreen': '#e6fff0',
            'transparent': None,  # WordCloud uses None for transparent
            'white': '#ffffff',
            'black': '#000000',
            # Add more as needed
        }
        mapped_background_color = background_color_translation.get(background_color.lower(), background_color)
        
        # Remove all mask logic, always use None for mask
        wc = WordCloud(
            width=width,
            height=height,
            background_color=mapped_background_color,
            colormap=mapped_color_scheme,
            mask=None,
            stopwords=self.stop_words,
            min_word_length=1,
            min_font_size=min_font_size,
            max_words=max_words,
            max_font_size=max_font_size,
            prefer_horizontal=prefer_horizontal,
            relative_scaling=relative_scaling
        )
        
        # Generate the word cloud
        wc.generate_from_frequencies(word_frequencies)
        
        # Convert to base64
        # Create figure without GUI
        fig = plt.figure(figsize=(10, 8))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        
        # Save to bytes buffer
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', bbox_inches='tight', 
                   pad_inches=0, dpi=150, facecolor='white')
        buffer.seek(0)
        
        # Convert to base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        plt.close(fig)
        
        # Extract context for each word
        word_context = self.extract_word_context(text, list(word_frequencies.keys()))
        
        # Sentiment analysis
        sentiment = self.analyze_sentiment(text)
        
        # Top N words
        top_words = self.get_top_n_words(word_frequencies, n=10)
        
        return image_base64, word_frequencies, word_context, sentiment, top_words 

    def _get_font_path(self, font_family):
        """Get the path to a font file based on the font family name."""
        # This is a simplified version for illustration
        # In a production environment, you would map font family names to actual font file paths
        
        # Default to a system font that's likely to exist
        standard_fonts = {
            'arial': '/Library/Fonts/Arial.ttf',
            'times new roman': '/Library/Fonts/Times New Roman.ttf',
            'courier new': '/Library/Fonts/Courier New.ttf',
            'georgia': '/Library/Fonts/Georgia.ttf',
            'verdana': '/Library/Fonts/Verdana.ttf',
            'impact': '/Library/Fonts/Impact.ttf',
            'comic sans ms': '/Library/Fonts/Comic Sans MS.ttf',
            'tahoma': '/Library/Fonts/Tahoma.ttf',
            'trebuchet ms': '/Library/Fonts/Trebuchet MS.ttf'
        }
        
        # Check if we support this font
        if font_family.lower() in standard_fonts:
            font_path = standard_fonts[font_family.lower()]
            if os.path.exists(font_path):
                return font_path
        
        # If not found or not supported, return None (use default font)
        return None
    
    def get_shape_preview(self, shape_name, width=200, height=150):
        """
        Generate a preview image for a shape.
        
        Args:
            shape_name (str): Name of the shape
            width (int): Width of the preview
            height (int): Height of the preview
            
        Returns:
            base64 string of the preview image
        """
        try:
            logger.info(f"Generating preview for shape: {shape_name}")
            
            # Generate a simple preview based on the shape
            mask = None
            
            if shape_name == 'none':
                # Rectangle preview
                mask = np.ones((height, width), dtype=np.uint8) * 255
            elif shape_name == 'circle':
                x, y = np.ogrid[:height, :width]
                center_y, center_x = height // 2, width // 2
                radius = min(center_x, center_y) * 0.8
                mask = ((x - center_y) ** 2 + (y - center_x) ** 2) < radius ** 2
                mask = 255 * mask.astype(np.uint8)
            elif shape_name == 'heart':
                # Generate a heart shape
                x = np.linspace(-2, 2, width)
                y = np.linspace(-2, 2, height)
                X, Y = np.meshgrid(x, y)
                # Heart curve formula
                mask = ((X**2 + Y**2 - 1)**3 - X**2 * Y**3) < 0
                mask = 255 * mask.astype(np.uint8)
            elif shape_name == 'star':
                # Generate a star shape
                x = np.linspace(-1, 1, width)
                y = np.linspace(-1, 1, height)
                X, Y = np.meshgrid(x, y)
                # Convert to polar coordinates
                R = np.sqrt(X**2 + Y**2)
                Theta = np.arctan2(Y, X)
                # Star formula with 5 points
                mask = R < 0.5 + 0.3 * np.cos(5 * Theta + np.pi/2)
                mask = 255 * mask.astype(np.uint8)
            elif shape_name == 'triangle':
                # Generate a triangle shape
                mask = np.zeros((height, width), dtype=np.uint8)
                h = height - 1
                w = width - 1
                for i in range(height):
                    line_width = int(w * (i/h))
                    start_x = (width - line_width) // 2
                    for j in range(start_x, start_x + line_width):
                        mask[i, j] = 255
            elif shape_name == 'diamond':
                # Generate a diamond shape using numpy operations (faster)
                y, x = np.ogrid[:height, :width]
                center_y, center_x = height // 2, width // 2
                max_dist = min(center_x, center_y)
                
                # Use Manhattan distance for diamond shape
                mask = (np.abs(y - center_y) + np.abs(x - center_x)) < max_dist
                mask = 255 * mask.astype(np.uint8)
            elif shape_name == 'cloud':
                # Generate a simple cloud shape (multiple overlapping circles)
                mask = np.zeros((height, width), dtype=np.uint8)
                
                # Define center points for circles
                centers = [
                    (width * 0.3, height * 0.4),
                    (width * 0.5, height * 0.3),
                    (width * 0.7, height * 0.4),
                    (width * 0.4, height * 0.5),
                    (width * 0.6, height * 0.5)
                ]
                
                # Draw circles to form a cloud shape
                for cx, cy in centers:
                    x, y = np.ogrid[:height, :width]
                    radius = min(width, height) * 0.2
                    circle = ((x - cy) ** 2 + (y - cx) ** 2) < radius ** 2
                    mask += 255 * circle.astype(np.uint8)
                
                # Clip to 0-255
                mask = np.clip(mask, 0, 255)
            else:
                # Default to rectangle
                mask = np.ones((height, width), dtype=np.uint8) * 255
            
            # Convert mask to PIL Image for easier processing
            mask_img = Image.fromarray(mask)
            
            # Save the mask to a bytes buffer
            img_buffer = io.BytesIO()
            mask_img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            # Convert to base64
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
            logger.info(f"Successfully generated preview for shape: {shape_name}")
            
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            logger.error(f"Error generating shape preview for {shape_name}: {str(e)}")
            # Return a transparent image
            img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            return f"data:image/png;base64,{img_base64}" 