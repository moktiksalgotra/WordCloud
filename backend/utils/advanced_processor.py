import re
import string
import base64
import io
import json
import time
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import os
import tempfile
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image

# Configure matplotlib for non-interactive use
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.colors as mcolors
from PIL import Image, ImageDraw, ImageFont
import cv2

# Text processing libraries
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk
from textblob import TextBlob
import textstat
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0

# Advanced analytics
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import gensim
from gensim import corpora, models
from gensim.models import LdaModel, CoherenceModel

# Word cloud
from wordcloud import WordCloud, STOPWORDS

# Import WordCloudProcessor
from utils.wordcloud_processor import WordCloudProcessor

def convert_numpy_types(obj):
    """Convert numpy data types to native Python types for JSON serialization."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_types(item) for item in obj)
    else:
        return obj

class AdvancedWordCloudProcessor:
    """Advanced processing for word clouds with additional analytics."""
    
    def __init__(self):
        """Initialize the processor."""
        # Initialize NLTK components
        self._ensure_nltk_resources()
        
        # Initialize the WordCloudProcessor for actual wordcloud generation
        self.wordcloud_processor = WordCloudProcessor()
        
        # Set up stopwords
        self.stop_words = set(stopwords.words('english'))
        
        # Initialize lemmatizer
        self.lemmatizer = WordNetLemmatizer()
        
        # Paths for resources
        self.resources_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')
        os.makedirs(self.resources_path, exist_ok=True)
        
    def _ensure_nltk_resources(self):
        """Ensure required NLTK resources are downloaded."""
        resources = [
            ('punkt', 'tokenizers/punkt'),
            ('stopwords', 'corpora/stopwords'),
            ('wordnet', 'corpora/wordnet')
        ]
        
        for name, path in resources:
            try:
                nltk.data.find(path)
            except LookupError:
                print(f"Downloading NLTK resource: {name}")
                nltk.download(name, quiet=True)
    
    def detect_language(self, text: str) -> str:
        """Detect the language of the text."""
        try:
            return detect(text)
        except Exception as e:
            print(f"DEBUG: Language detection failed: {e}")
            return 'en'
    
    def preprocess_text(self, text: str, remove_stopwords: bool = True, 
                       custom_stopwords: List[str] = None, 
                       lemmatize: bool = True, 
                       remove_numbers: bool = True,
                       min_word_length: int = 2) -> List[str]:
        """
        Advanced text preprocessing with multiple options.
        """
        # Tokenization
        tokens = word_tokenize(text.lower())
        
        # Remove punctuation and numbers
        if remove_numbers:
            tokens = [token for token in tokens 
                     if token not in string.punctuation and not token.isnumeric()]
        else:
            tokens = [token for token in tokens 
                     if token not in string.punctuation]
        
        # Remove short words
        tokens = [token for token in tokens if len(token) >= min_word_length]
        
        # Lemmatization
        if lemmatize:
            tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
        
        # Stopword removal
        if remove_stopwords:
            tokens = [token for token in tokens if token not in self.stop_words]
            
            if custom_stopwords:
                custom_stopwords_set = set(word.lower() for word in custom_stopwords)
                tokens = [token for token in tokens if token not in custom_stopwords_set]
        
        return tokens
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text."""
        try:
            tokens = word_tokenize(text)
            pos_tags = pos_tag(tokens)
            named_entities = ne_chunk(pos_tags)
            
            entities = defaultdict(list)
            for chunk in named_entities:
                if hasattr(chunk, 'label'):
                    entity_type = chunk.label()
                    entity_text = ' '.join(c[0] for c in chunk.leaves())
                    entities[entity_type].append(entity_text)
            
            return dict(entities)
        except Exception as e:
            print(f"DEBUG: Entity extraction failed: {e}")
            return {}
    
    def extract_keywords(self, text: str, top_k: int = 20) -> List[Tuple[str, float]]:
        """Extract keywords using TF-IDF."""
        try:
            # Preprocess text
            processed_text = ' '.join(self.preprocess_text(text, lemmatize=True))
            
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                max_features=top_k,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            tfidf_matrix = vectorizer.fit_transform([processed_text])
            feature_names = vectorizer.get_feature_names_out()
            
            # Get TF-IDF scores
            scores = tfidf_matrix.toarray()[0]
            
            # Create keyword-score pairs
            keywords = list(zip(feature_names, scores))
            keywords.sort(key=lambda x: x[1], reverse=True)
            
            return keywords
        except Exception as e:
            print(f"DEBUG: Keyword extraction failed: {e}")
            return []
    
    def perform_topic_modeling(self, text: str, num_topics: int = 5) -> Dict[str, Any]:
        """Perform topic modeling using LDA."""
        try:
            # Preprocess text
            tokens = self.preprocess_text(text, lemmatize=True)
            
            if len(tokens) < 10:
                return {'topics': [], 'coherence': 0.0, 'num_topics': 0}
            
            # Create dictionary
            dictionary = corpora.Dictionary([tokens])
            
            # Create document-term matrix
            doc_term_matrix = [dictionary.doc2bow(tokens)]
            
            # Train LDA model
            lda_model = LdaModel(
                doc_term_matrix,
                num_topics=num_topics,
                id2word=dictionary,
                passes=15,
                random_state=42
            )
            
            # Extract topics
            topics = []
            for topic_id, topic in lda_model.show_topics(num_topics=num_topics, num_words=10, formatted=False):
                topic_words = [word for word, _ in topic]
                topics.append({
                    'topic_id': topic_id,
                    'words': topic_words
                })
            
            # Calculate coherence
            try:
                coherence_model = CoherenceModel(
                    model=lda_model, 
                    texts=[tokens], 
                    dictionary=dictionary, 
                    coherence='c_v'
                )
                coherence = coherence_model.get_coherence()
            except Exception as e:
                print(f"DEBUG: Coherence calculation failed: {e}")
                coherence = 0.0
            
            return {
                'topics': topics,
                'coherence': coherence,
                'num_topics': len(topics)
            }
        except Exception as e:
            print(f"DEBUG: Topic modeling failed: {e}")
            return {'topics': [], 'coherence': 0.0, 'num_topics': 0}
    
    def analyze_readability(self, text: str) -> Dict[str, float]:
        """Analyze text readability using multiple metrics."""
        try:
            return {
                'flesch_reading_ease': textstat.flesch_reading_ease(text),
                'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text),
                'gunning_fog': textstat.gunning_fog(text),
                'smog_index': textstat.smog_index(text),
                'automated_readability_index': textstat.automated_readability_index(text),
                'coleman_liau_index': textstat.coleman_liau_index(text),
                'linsear_write_formula': textstat.linsear_write_formula(text),
                'dale_chall_readability_score': textstat.dale_chall_readability_score(text),
                'difficult_words': textstat.difficult_words(text),
                'syllable_count': textstat.syllable_count(text),
                'lexicon_count': textstat.lexicon_count(text),
                'sentence_count': textstat.sentence_count(text)
            }
        except Exception as e:
            print(f"DEBUG: Readability analysis failed: {e}")
            return {
                'flesch_reading_ease': 0.0,
                'flesch_kincaid_grade': 0.0,
                'gunning_fog': 0.0,
                'smog_index': 0.0,
                'automated_readability_index': 0.0,
                'coleman_liau_index': 0.0,
                'linsear_write_formula': 0.0,
                'dale_chall_readability_score': 0.0,
                'difficult_words': 0,
                'syllable_count': 0,
                'lexicon_count': 0,
                'sentence_count': 0
            }
    
    def analyze_sentiment_advanced(self, text: str) -> Dict[str, Any]:
        """Advanced sentiment analysis with multiple dimensions."""
        try:
            blob = TextBlob(text)
            
            # Basic sentiment
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Sentiment by sentences
            sentences = sent_tokenize(text)
            sentence_sentiments = []
            
            for sentence in sentences:
                try:
                    sentence_blob = TextBlob(sentence)
                    sentence_sentiments.append({
                        'sentence': sentence,
                        'polarity': sentence_blob.sentiment.polarity,
                        'subjectivity': sentence_blob.sentiment.subjectivity
                    })
                except Exception as e:
                    print(f"DEBUG: Sentence sentiment analysis failed for sentence: {e}")
                    continue
            
            # Sentiment categories
            if polarity > 0.2:
                sentiment_category = 'positive'
            elif polarity < -0.2:
                sentiment_category = 'negative'
            else:
                sentiment_category = 'neutral'
            
            # Subjectivity categories
            if subjectivity > 0.6:
                subjectivity_category = 'subjective'
            elif subjectivity < 0.4:
                subjectivity_category = 'objective'
            else:
                subjectivity_category = 'neutral'
            
            return {
                'polarity': polarity,
                'subjectivity': subjectivity,
                'sentiment_category': sentiment_category,
                'subjectivity_category': subjectivity_category,
                'sentence_sentiments': sentence_sentiments,
                'overall_sentiment': {
                    'positive_sentences': len([s for s in sentence_sentiments if s['polarity'] > 0.1]),
                    'negative_sentences': len([s for s in sentence_sentiments if s['polarity'] < -0.1]),
                    'neutral_sentences': len([s for s in sentence_sentiments if -0.1 <= s['polarity'] <= 0.1])
                }
            }
        except Exception as e:
            print(f"DEBUG: Sentiment analysis failed: {e}")
            return {
                'polarity': 0.0,
                'subjectivity': 0.0,
                'sentiment_category': 'neutral',
                'subjectivity_category': 'neutral',
                'sentence_sentiments': [],
                'overall_sentiment': {
                    'positive_sentences': 0,
                    'negative_sentences': 0,
                    'neutral_sentences': 0
                }
            }
    
    def generate_color_function(self, color_scheme: str, background_color: str = 'white'):
        """Generate color function for word cloud."""
        if color_scheme in self.color_schemes:
            cmap = self.color_schemes[color_scheme]
            
            def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
                # Generate color based on word frequency and position
                color = cmap(random_state.randint(0, 255))
                return f"rgb({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)})"
            
            return color_func
        else:
            # Default rainbow colors
            def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
                colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
                         '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9']
                return random_state.choice(colors)
            
            return color_func
    
    def test_simple_wordcloud(self, text: str) -> str:
        """
        Generate a simple word cloud for testing purposes.
        
        Args:
            text (str): The text to generate a word cloud from
            
        Returns:
            str: Base64-encoded image of the word cloud
        """
        # Create a simple word cloud
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color='white',
            max_words=100,
            stopwords=STOPWORDS,
            min_font_size=10
        ).generate(text)
        
        # Convert to image
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        
        # Save to a bytes buffer
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight')
        plt.close()
        
        # Convert to base64
        img_buffer.seek(0)
        img_b64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        
        return f"data:image/png;base64,{img_b64}"
    
    def generate_advanced_wordcloud(self, text: str, settings: Dict = None) -> Tuple[str, Dict]:
        """
        Generate a word cloud with comprehensive analytics.
        
        Args:
            text (str): The text to process
            settings (Dict): Dictionary of settings for customization
            
        Returns:
            Tuple of (image_base64, analytics_dict)
        """
        if not settings:
            settings = {}
            
        print(f"DEBUG: generate_advanced_wordcloud called with settings: {settings}")
        
        start_time = time.time()
        
        # Process text with all options
        processed_text, tokens, word_freq, sentences = self._process_text(
            text, 
            remove_stopwords=settings.get('remove_stopwords', True),
            custom_stopwords=settings.get('custom_stopwords', []),
            lemmatize=settings.get('lemmatize', True),
            min_word_length=settings.get('min_word_length', 2),
            remove_numbers=settings.get('remove_numbers', True),
            min_frequency=settings.get('min_frequency'),
            max_frequency=settings.get('max_frequency')
        )
        
        # Generate word cloud using the WordCloudProcessor
        # The wordcloud_processor.generate_wordcloud returns 5 values:
        # (image_base64, word_frequencies, word_context, sentiment, top_words)
        
        # Ensure min_frequency and max_frequency are properly typed or None
        min_freq = settings.get('min_frequency')
        max_freq = settings.get('max_frequency')
        
        # Ensure they're integers or None
        if min_freq is not None:
            try:
                min_freq = int(min_freq)
            except (ValueError, TypeError):
                min_freq = None
                
        if max_freq is not None:
            try:
                max_freq = int(max_freq)
            except (ValueError, TypeError):
                max_freq = None
        
        image_base64, wc_word_freq, wc_word_context, wc_sentiment, wc_top_words = self.wordcloud_processor.generate_wordcloud(
            processed_text,
            remove_stopwords=settings.get('remove_stopwords', True),
            custom_stopwords=settings.get('custom_stopwords', []),
            mask_shape=settings.get('mask_shape', 'none'),
            min_frequency=min_freq,
            max_frequency=max_freq,
            width=settings.get('width', 800),
            height=settings.get('height', 600),
            color_scheme=settings.get('color_scheme', 'viridis'),
            background_color=settings.get('background_color', 'white'),
            prefer_horizontal=settings.get('prefer_horizontal', 0.7),
            relative_scaling=settings.get('relative_scaling', 0.5),
            max_words=settings.get('max_words', 200),
            min_font_size=settings.get('min_font_size', 10),
            max_font_size=settings.get('max_font_size', 100)
        )
        
        # Extract word context
        word_context = self._extract_word_context(word_freq, sentences)
        
        # Perform sentiment analysis
        sentiment_analysis = self._analyze_sentiment(text)
        
        # Calculate statistics
        text_statistics = self._calculate_statistics(text, tokens, word_freq)
        text_statistics['text_length'] = len(text)  # Ensure text_length is present
        
        # Extract top words
        print(f"DEBUG: Extracting top words from word_freq: {word_freq}")
        print(f"DEBUG: Type of first frequency value: {type(next(iter(word_freq.values()))).__name__}")
        
        # Convert all frequency values to integers to avoid type comparison issues
        word_freq = {word: int(freq) if isinstance(freq, str) else freq for word, freq in word_freq.items()}
        
        top_words = {word: freq for word, freq in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:50]}
        
        # Compile analytics
        analytics = {
            'word_frequencies': word_freq,
            'word_context': word_context,
            'sentiment_analysis': sentiment_analysis,
            'text_statistics': text_statistics,
            'top_words': top_words,
            'processing_time': round(time.time() - start_time, 2)
        }
        # Add mask_shape to text_statistics for frontend display
        analytics['text_statistics']['mask_shape'] = settings.get('mask_shape', 'none')
        
        return image_base64, analytics
    
    def _process_text(self, text: str, remove_stopwords: bool = True, 
                      custom_stopwords: List[str] = None, lemmatize: bool = True, 
                      min_word_length: int = 2, remove_numbers: bool = True,
                      min_frequency: Optional[int] = None, max_frequency: Optional[int] = None) -> Tuple[str, List[str], Dict[str, int], List[str]]:
        """
        Process text with comprehensive options.
        
        Args:
            text (str): Input text
            remove_stopwords (bool): Whether to remove stopwords
            custom_stopwords (List[str]): Additional stopwords to remove
            lemmatize (bool): Whether to lemmatize words
            min_word_length (int): Minimum length of words to include
            remove_numbers (bool): Whether to remove numbers
            min_frequency (int): Minimum frequency for a word to be included
            max_frequency (int): Maximum frequency for a word to be included
            
        Returns:
            Tuple of (processed_text, tokens, word_freq, sentences)
        """
        # Log input parameters for debugging
        print(f"DEBUG _process_text: min_frequency={min_frequency} (type: {type(min_frequency).__name__}), max_frequency={max_frequency} (type: {type(max_frequency).__name__})")
        
        # Initialize stopwords
        stopwords_set = set(STOPWORDS) if remove_stopwords else set()
        
        # Add custom stopwords
        if custom_stopwords:
            stopwords_set.update(set(word.lower() for word in custom_stopwords))
        
        # Split text into sentences
        sentences = sent_tokenize(text)
        
        # Tokenize and process
        tokens = []
        for sentence in sentences:
            words = word_tokenize(sentence.lower())
            
            # Filter tokens
            for word in words:
                # Remove punctuation and clean
                word = re.sub(r'[^\w\s]', '', word)
                
                # Skip empty words
                if not word:
                    continue
                
                # Skip numbers if requested
                if remove_numbers and word.isdigit():
                    continue
                
                # Skip short words
                if len(word) < min_word_length:
                    continue
                
                # Skip stopwords
                if word.lower() in stopwords_set:
                    continue
                
                # Lemmatize if requested
                if lemmatize:
                    word = self.lemmatizer.lemmatize(word)
                
                tokens.append(word)
        
        # Count word frequencies
        word_freq = Counter(tokens)
        print(f"DEBUG: Word frequency count complete. Found {len(word_freq)} unique words.")
        
        # Apply frequency filters
        if min_frequency is not None or max_frequency is not None:
            print(f"DEBUG: Applying frequency filters: min={min_frequency}, max={max_frequency}")
            filtered_word_freq = {}
            for word, freq in word_freq.items():
                try:
                    include_word = True
                    
                    if min_frequency is not None:
                        try:
                            min_freq_value = int(min_frequency)
                            print(f"DEBUG: Checking word '{word}' with freq {freq} against min_freq {min_freq_value}")
                            # Convert frequency to int for comparison if it's a string
                            freq_value = int(freq) if isinstance(freq, str) else freq
                            if freq_value < min_freq_value:
                                include_word = False
                        except (ValueError, TypeError) as e:
                            print(f"DEBUG: Error converting min_frequency: {e}")
                            # If conversion fails, skip min_frequency check
                            pass
                            
                    if include_word and max_frequency is not None:
                        try:
                            max_freq_value = int(max_frequency)
                            print(f"DEBUG: Checking word '{word}' with freq {freq} against max_freq {max_freq_value}")
                            # Convert frequency to int for comparison if it's a string
                            freq_value = int(freq) if isinstance(freq, str) else freq
                            if freq_value > max_freq_value:
                                include_word = False
                        except (ValueError, TypeError) as e:
                            print(f"DEBUG: Error converting max_frequency: {e}")
                            # If conversion fails, skip max_frequency check
                            pass
                            
                    if include_word:
                        filtered_word_freq[word] = freq
                        
                except (ValueError, TypeError) as e:
                    print(f"DEBUG: Error in frequency filtering for word '{word}': {e}")
                    # If conversion fails, include the word anyway
                    filtered_word_freq[word] = freq
                    
            print(f"DEBUG: After filtering, {len(filtered_word_freq)} words remain")
            word_freq = filtered_word_freq
        
        # Join tokens back into text for word cloud generation
        processed_text = ' '.join(word for word in tokens if word in word_freq)
        
        return processed_text, tokens, dict(word_freq), sentences
    
    def _extract_word_context(self, word_freq: Dict[str, int], sentences: List[str]) -> Dict[str, List[str]]:
        """
        Extract context for top words.
        
        Args:
            word_freq (Dict[str, int]): Word frequency dictionary
            sentences (List[str]): List of sentences from the text
            
        Returns:
            Dict[str, List[str]]: Dictionary mapping words to context snippets
        """
        # Get top 20 words by frequency
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
        top_words = [word for word, _ in top_words]
        
        context_dict = defaultdict(list)
        
        # Find sentences containing each top word
        for word in top_words:
            for sentence in sentences:
                if re.search(r'\b' + re.escape(word) + r'\b', sentence.lower()):
                    # Limit context length
                    if len(sentence) > 200:
                        # Find the position of the word in the sentence
                        match = re.search(r'\b' + re.escape(word) + r'\b', sentence.lower())
                        if match:
                            start_pos = max(0, match.start() - 100)
                            end_pos = min(len(sentence), match.end() + 100)
                            context = sentence[start_pos:end_pos]
                            
                            # Add ellipsis if truncated
                            if start_pos > 0:
                                context = '...' + context
                            if end_pos < len(sentence):
                                context = context + '...'
                                
                            context_dict[word].append(context)
                    else:
                        context_dict[word].append(sentence)
                    
                    # Limit to 3 context snippets per word
                    if len(context_dict[word]) >= 3:
                        break
        
        return dict(context_dict)
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Perform sentiment analysis on the text.
        
        Args:
            text (str): Input text
            
        Returns:
            Dict: Sentiment analysis results
        """
        # Basic sentiment analysis with TextBlob
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Determine sentiment category
        if polarity > 0.2:
            sentiment = "positive"
        elif polarity < -0.2:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        # Analyze sentiment by sentence
        sentences = [str(sentence) for sentence in blob.sentences]
        sentence_sentiments = []
        
        positive_sentences = []
        negative_sentences = []
        neutral_sentences = []
        
        for sentence in blob.sentences:
            sentence_text = str(sentence)
            sentence_polarity = sentence.sentiment.polarity
            sentence_subjectivity = sentence.sentiment.subjectivity
            
            if len(sentence_text) > 5:  # Ignore very short sentences
                s_sentiment = ""
                if sentence_polarity > 0.2:
                    s_sentiment = "positive"
                    positive_sentences.append(sentence_text)
                elif sentence_polarity < -0.2:
                    s_sentiment = "negative"
                    negative_sentences.append(sentence_text)
                else:
                    s_sentiment = "neutral"
                    neutral_sentences.append(sentence_text)
                
                sentence_sentiments.append({
                    'text': sentence_text[:100] + ('...' if len(sentence_text) > 100 else ''),
                    'polarity': round(sentence_polarity, 2),
                    'subjectivity': round(sentence_subjectivity, 2),
                    'sentiment': s_sentiment
                })
                
                # Limit to 5 sentences per category
                if len(sentence_sentiments) >= 15:
                    break
        
        # Sample sentences for each sentiment category
        sentiment_examples = {
            'positive': positive_sentences[:3],
            'negative': negative_sentences[:3],
            'neutral': neutral_sentences[:3]
        }
        
        return {
            'overall_polarity': round(polarity, 2),
            'overall_subjectivity': round(subjectivity, 2),
            'overall_sentiment': sentiment,
            'sentence_breakdown': {
                'positive': len(positive_sentences),
                'negative': len(negative_sentences),
                'neutral': len(neutral_sentences)
            },
            'examples': sentiment_examples,
            'sentence_analysis': sentence_sentiments[:10]  # Limit to 10 sentences in the response
        }
    
    def _calculate_statistics(self, original_text: str, tokens: List[str], word_freq: Dict[str, int]) -> Dict[str, Any]:
        """
        Calculate text statistics.
        
        Args:
            original_text (str): Original input text
            tokens (List[str]): Processed tokens
            word_freq (Dict[str, int]): Word frequency dictionary
            
        Returns:
            Dict: Text statistics
        """
        # Basic statistics
        total_words = len(tokens)
        unique_words = len(word_freq)
        if total_words == 0:
            # Handle edge case of empty text
            avg_word_length = 0
            lexical_diversity = 0
        else:
            avg_word_length = sum(len(word) for word in tokens) / total_words
            lexical_diversity = unique_words / total_words
            
        # Count sentences and calculate average sentence length
        sentences = sent_tokenize(original_text)
        total_sentences = len(sentences)
        if total_sentences == 0:
            avg_sentence_length = 0
        else:
            words_per_sentence = [len(word_tokenize(s)) for s in sentences]
            avg_sentence_length = sum(words_per_sentence) / total_sentences
            
        # Calculate character count
        total_characters = len(original_text)
        alpha_characters = sum(c.isalpha() for c in original_text)
        
        # Frequency distribution
        freq_distribution = {}
        for count in range(1, 11):  # Count words appearing 1-10 times
            freq_distribution[count] = sum(1 for freq in word_freq.values() if freq == count)
        freq_distribution['more'] = sum(1 for freq in word_freq.values() if freq > 10)
        
        return {
            'total_words': total_words,
            'unique_words': unique_words,
            'total_characters': total_characters,
            'alpha_characters': alpha_characters,
            'total_sentences': total_sentences,
            'avg_word_length': round(avg_word_length, 1),
            'avg_sentence_length': round(avg_sentence_length, 1),
            'lexical_diversity': round(lexical_diversity, 2),
            'frequency_distribution': freq_distribution
        } 