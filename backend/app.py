import os
import logging
import base64
from datetime import datetime
from flask import Flask, request, jsonify, send_file, current_app, make_response
from flask_cors import CORS
from flask_migrate import Migrate
import redis
from celery import Celery
from werkzeug.utils import secure_filename
from PIL import Image
import io
import nltk
from flask_socketio import SocketIO

# Import models
from models import db, User, WordCloud, Analytics

# Import processors
from utils.advanced_processor import AdvancedWordCloudProcessor
from utils.file_processor import FileProcessor
from utils.wordcloud_processor import WordCloudProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize extensions
migrate = Migrate()

# Initialize processors
advanced_processor = AdvancedWordCloudProcessor()
file_processor = FileProcessor()

# Initialize Celery
celery = Celery(__name__)

# Set NLTK data path
nltk.data.path.append(os.path.join(os.path.dirname(__file__), 'nltk_data'))

# Download NLTK punkt_tab and punkt if not already downloaded
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def create_app(config_name='default'):
    """Application factory pattern."""
    app = Flask(__name__)
    
    # Use absolute path for database to avoid path resolution issues
    base_dir = os.path.abspath(os.path.dirname(__file__))
    instance_dir = os.path.join(base_dir, 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    db_path = os.path.join(instance_dir, 'wordcloud_dev.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['UPLOAD_FOLDER'] = 'uploads'
    
    # Set maximum content length for uploads (16MB)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    # Set maximum text length (1MB for text input)
    app.config['MAX_TEXT_LENGTH'] = 1 * 1024 * 1024
    
    # Add JWT secret key for authentication
    app.config['JWT_SECRET_KEY'] = 'your_super_secret_jwt_key'  # TODO: Change this to a secure value in production
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, origins=["http://localhost:3000", "https://wordcloudapp.onrender.com"])
    
    # Initialize Celery
    celery.conf.update(app.config)
    
    # Create upload directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app

app = create_app()
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:3000", "https://wordcloudapp.onrender.com"])

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy', 
        'message': 'Professional Word Cloud Generator API is running',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0'
    })

# Test endpoint for simple word cloud
@app.route('/api/test_wordcloud', methods=['POST'])
def test_simple_wordcloud():
    """Test endpoint for simple word cloud generation."""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'Text input is required'
            }), 400
        
        # Test simple word cloud
        image_base64 = advanced_processor.test_simple_wordcloud(text)
        
        if image_base64:
            return jsonify({
                'success': True,
                'image_base64': image_base64,
                'message': 'Simple word cloud generated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to generate simple word cloud'
            }), 500
            
    except Exception as e:
        logger.error(f"Error in test word cloud: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# File upload endpoint
@app.route('/api/upload_file', methods=['POST'])
def upload_file():
    """
    Upload and process a file to extract text.
    Supports multiple file formats including TXT, PDF, DOCX, CSV, etc.
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file part in the request'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
            
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Process the file to extract text
            result = file_processor.extract_text_from_file(file_path)
            
            # Delete the uploaded file after processing (cleanup)
            try:
                os.remove(file_path)
            except Exception as e:
                logger.error(f"Error removing uploaded file: {str(e)}")
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'text': result['text'],
                    'file_type': result.get('file_type', 'unknown'),
                    'word_count': result.get('word_count', 0),
                    'character_count': result.get('character_count', 0)
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Failed to extract text from file')
                }), 400
    except Exception as e:
        logger.error(f"Error in file upload: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error processing file: {str(e)}"
        }), 500

# URL processing endpoint
@app.route('/api/process_url', methods=['POST'])
def process_url():
    """
    Extract text from a website URL.
    Uses BeautifulSoup to parse and extract meaningful text.
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'URL is required'
            }), 400
            
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'URL cannot be empty'
            }), 400
            
        # Process the URL to extract text
        result = file_processor.extract_text_from_url(url)
        
        if result['success']:
            return jsonify({
                'success': True,
                'text': result['text'],
                'title': result.get('title', ''),
                'url': result.get('url', url),
                'word_count': result.get('word_count', 0),
                'character_count': result.get('character_count', 0)
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to extract text from URL')
            }), 400
    except Exception as e:
        logger.error(f"Error in URL processing: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error processing URL: {str(e)}"
        }), 500

# Advanced word cloud generation
@app.route('/api/generate_wordcloud', methods=['POST'])
def generate_advanced_wordcloud():
    """
    Generate advanced word cloud with comprehensive analytics.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        # Extract parameters
        text = data.get('text', '').strip()
        settings = data.get('settings', {})
        title = data.get('title', 'Untitled Word Cloud')
        tags = data.get('tags', [])
        
        # Validate input
        if not text:
            return jsonify({
                'success': False,
                'error': 'Text input is required'
            }), 400
        
        if len(text) < 10:
            return jsonify({
                'success': False,
                'error': 'Text must be at least 10 characters long'
            }), 400
        
        if len(text) > current_app.config['MAX_TEXT_LENGTH']:
            return jsonify({
                'success': False,
                'error': f'Text length exceeds maximum allowed ({current_app.config["MAX_TEXT_LENGTH"]} characters)'
            }), 400
            
        # Validate and convert numeric settings
        if 'min_frequency' in settings:
            logger.info(f"Original min_frequency value: {settings['min_frequency']} (type: {type(settings['min_frequency']).__name__})")
            try:
                settings['min_frequency'] = int(settings['min_frequency'])
                logger.info(f"Converted min_frequency value: {settings['min_frequency']} (type: {type(settings['min_frequency']).__name__})")
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid min_frequency value: {settings.get('min_frequency')}, setting to None. Error: {str(e)}")
                settings['min_frequency'] = None
                
        if 'max_frequency' in settings:
            logger.info(f"Original max_frequency value: {settings['max_frequency']} (type: {type(settings['max_frequency']).__name__})")
            try:
                settings['max_frequency'] = int(settings['max_frequency'])
                logger.info(f"Converted max_frequency value: {settings['max_frequency']} (type: {type(settings['max_frequency']).__name__})")
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid max_frequency value: {settings.get('max_frequency')}, setting to None. Error: {str(e)}")
                settings['max_frequency'] = None
        
        # Log all settings for debugging
        logger.info(f"Settings after validation: {settings}")
        
        # No authentication: always set user_id = None
        user_id = None
        
        logger.info(f"Generating advanced word cloud for text of length {len(text)}")
        
        # Generate word cloud with advanced analytics
        image_base64, analytics = advanced_processor.generate_advanced_wordcloud(text, settings)
        
        # Do not save to database with user_id, but you may still save as public or anonymous if needed
        wordcloud_record = None
        # Optionally, you can comment out the following block if you don't want to save at all
        # if user_id:
        #     try:
        #         wordcloud_record = WordCloud(
        #             title=title,
        #             user_id=user_id,
        #             original_text=text,
        #             processed_text=' '.join(analytics['word_frequencies'].keys()),
        #             text_length=len(text),
        #             word_count=analytics['text_statistics']['total_words'],
        #             unique_words=analytics['text_statistics']['unique_words'],
        #             mask_shape=settings.get('mask_shape', 'none'),
        #             color_scheme=settings.get('color_scheme', 'viridis'),
        #             background_color=settings.get('background_color', 'white'),
        #             width=settings.get('width', 800),
        #             height=settings.get('height', 600),
        #             image_base64=image_base64,
        #             is_public=data.get('is_public', False)
        #         )
        #         wordcloud_record.set_settings(settings)
        #         wordcloud_record.set_word_frequencies(analytics['word_frequencies'])
        #         wordcloud_record.set_sentiment_analysis(analytics['sentiment_analysis'])
        #         wordcloud_record.set_tags(tags)
        #         db.session.add(wordcloud_record)
        #         db.session.commit()
        #         analytics_record = Analytics(
        #             user_id=user_id,
        #             action='generate_wordcloud',
        #             feature_used='wordcloud',
        #             text_length=len(text),
        #         )
        #         db.session.add(analytics_record)
        #         db.session.commit()
        #     except Exception as e:
        #         logger.error(f"Error saving word cloud to database: {str(e)}")
        #         # Continue execution despite DB error
        
        # Convert any dictionaries with mixed keys to ensure all keys are strings
        def ensure_str_keys(obj):
            if isinstance(obj, dict):
                return {str(k): ensure_str_keys(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [ensure_str_keys(item) for item in obj]
            else:
                return obj
                
        # Return the word cloud data
        return jsonify({
            'success': True,
            'message': 'Word cloud generated successfully',
            'image_base64': image_base64,
            'word_frequencies': ensure_str_keys(analytics['word_frequencies']),
            'word_context': ensure_str_keys(analytics['word_context']),
            'sentiment_analysis': ensure_str_keys(analytics['sentiment_analysis']),
            'top_words': ensure_str_keys(analytics.get('top_words', {})),
            'text_statistics': ensure_str_keys(analytics['text_statistics']),
            'wordcloud_id': wordcloud_record.id if wordcloud_record else None
        })
        
    except Exception as e:
        import traceback
        logger.error(f"Error in advanced word cloud generation: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

# Export endpoints
@app.route('/api/export/<int:wordcloud_id>', methods=['GET'])
def export_wordcloud(wordcloud_id):
    """Export word cloud in various formats."""
    try:
        format_type = request.args.get('format', 'png')
        dpi = request.args.get('dpi', 300, type=int)
        
        # Get word cloud from database
        wordcloud = WordCloud.query.get(wordcloud_id)
        if not wordcloud:
            return jsonify({
                'success': False,
                'error': 'Word cloud not found'
            }), 404
        
        # Removed: Check if public or user has access
        # if not wordcloud.is_public:
        #     # Add authentication check here
        #     pass
        
        if format_type == 'png':
            # Return PNG image
            import base64
            image_data = base64.b64decode(wordcloud.image_base64)
            return send_file(
                io.BytesIO(image_data),
                mimetype='image/png',
                as_attachment=True,
                download_name=f'wordcloud_{wordcloud_id}.png'
            )
        
        elif format_type == 'json':
            # Return JSON data
            return jsonify({
                'success': True,
                'wordcloud': wordcloud.to_dict()
            })
        
        elif format_type == 'csv':
            # Return CSV data
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Word', 'Frequency'])
            
            word_frequencies = wordcloud.get_word_frequencies()
            for word, freq in sorted(word_frequencies.items(), key=lambda x: x[1], reverse=True):
                writer.writerow([word, freq])
            
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode()),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'wordcloud_{wordcloud_id}.csv'
            )
        
        else:
            return jsonify({
                'success': False,
                'error': 'Unsupported export format'
            }), 400
        
    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Export failed: {str(e)}'
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

@app.route('/mask_preview', methods=['GET'])
def mask_preview():
    """
    Get a preview image for a word cloud shape mask.
    
    Query parameters:
    - mask_shape: Shape name (e.g., 'circle', 'heart', 'star', etc.)
    - width: Width of the preview image (optional, default: 200)
    - height: Height of the preview image (optional, default: 150)
    """
    try:
        # Get shape name from query parameters
        shape_name = request.args.get('mask_shape', 'none')
        
        # Get dimensions from query parameters
        width = int(request.args.get('width', 200))
        height = int(request.args.get('height', 150))
        
        # Validate dimensions
        if width < 50 or width > 1000 or height < 50 or height > 1000:
            return jsonify({
                'success': False,
                'error': 'Invalid dimensions. Width and height must be between 50 and 1000 pixels.'
            }), 400
        
        # Generate preview image
        preview_image_base64 = advanced_processor.wordcloud_processor.get_shape_preview(
            shape_name=shape_name,
            width=width,
            height=height
        )
        
        # Extract the base64 data part and return as image with proper headers
        if ',' in preview_image_base64:
            base64_data = preview_image_base64.split(',')[1]
        else:
            base64_data = preview_image_base64
            
        # Decode the base64 string
        image_data = base64.b64decode(base64_data)
        
        # Return as image with proper headers
        response = make_response(image_data)
        response.headers.set('Content-Type', 'image/png')
        response.headers.set('Cache-Control', 'no-cache')
        response.headers.set('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        logger.error(f"Error generating mask preview: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error generating shape preview'
        }), 500

@app.route('/api/analytics/dashboard', methods=['GET'])
def analytics_dashboard():
    """Placeholder dashboard analytics endpoint."""
    return jsonify({
        'success': True,
        'statistics': {
            'total_users': 42,
            'total_wordclouds': 123,
            'active_sessions': 7
        }
    })

@app.route('/generator', methods=['GET'])
def generator_page():
    """Placeholder generator endpoint."""
    return jsonify({
        'success': True,
        'message': 'Generator endpoint placeholder.'
    })

# Example event handler
@socketio.on('connect')
def handle_connect():
    logger.info('Client connected via WebSocket')

if __name__ == '__main__':
    logger.info("Starting Professional Word Cloud Generator API with WebSocket support...")
    if os.environ.get("RENDER") == "true" or os.environ.get("FLASK_ENV") == "production":
        socketio.run(app, host='0.0.0.0', port=8000, server='eventlet')
    else:
        socketio.run(app, debug=True, host='0.0.0.0', port=8000, allow_unsafe_werkzeug=True) 