import os
import re
import requests
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import PyPDF2
from docx import Document
import pandas as pd
from bs4 import BeautifulSoup
import io

class FileProcessor:
    """Process various file formats and extract text content."""
    
    def __init__(self):
        self.supported_extensions = {
            '.txt': self._extract_text_txt,
            '.pdf': self._extract_text_pdf,
            '.docx': self._extract_text_docx,
            '.csv': self._extract_text_csv,
            '.xlsx': self._extract_text_excel,
            '.html': self._extract_text_html,
            '.htm': self._extract_text_html
        }
        
        self.max_file_size = 16 * 1024 * 1024  # 16MB
        self.max_url_size = 5 * 1024 * 1024  # 5MB for URLs
    
    def extract_text_from_file(self, file_path: str) -> Dict[str, any]:
        """
        Extract text from a file based on its extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                return {
                    'success': False,
                    'error': f'File size ({file_size} bytes) exceeds maximum allowed size ({self.max_file_size} bytes)'
                }
            
            # Get file extension
            _, ext = os.path.splitext(file_path.lower())
            
            if ext not in self.supported_extensions:
                return {
                    'success': False,
                    'error': f'Unsupported file type: {ext}'
                }
            
            # Extract text using appropriate method
            extractor = self.supported_extensions[ext]
            text = extractor(file_path)
            
            if not text or not text.strip():
                return {
                    'success': False,
                    'error': 'No text content found in file'
                }
            
            return {
                'success': True,
                'text': text,
                'file_size': file_size,
                'file_type': ext,
                'word_count': len(text.split()),
                'character_count': len(text)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error processing file: {str(e)}'
            }
    
    def extract_text_from_url(self, url: str) -> Dict[str, any]:
        """
        Extract text from a web page.
        
        Args:
            url: URL to extract text from
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return {
                    'success': False,
                    'error': 'Invalid URL format'
                }
            
            # Fetch content
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30, stream=True)
            response.raise_for_status()
            
            # Check content size
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > self.max_url_size:
                return {
                    'success': False,
                    'error': f'Content size ({content_length} bytes) exceeds maximum allowed size ({self.max_url_size} bytes)'
                }
            
            # Read content
            content = response.text
            
            # Parse HTML
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            if not text or not text.strip():
                return {
                    'success': False,
                    'error': 'No text content found on the webpage'
                }
            
            return {
                'success': True,
                'text': text,
                'url': url,
                'title': soup.title.string if soup.title else '',
                'word_count': len(text.split()),
                'character_count': len(text)
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Error fetching URL: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error processing URL: {str(e)}'
            }
    
    def _extract_text_txt(self, file_path: str) -> str:
        """Extract text from a plain text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
    
    def _extract_text_pdf(self, file_path: str) -> str:
        """Extract text from a PDF file."""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                
                return text.strip()
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def _extract_text_docx(self, file_path: str) -> str:
        """Extract text from a DOCX file."""
        try:
            doc = Document(file_path)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")
    
    def _extract_text_csv(self, file_path: str) -> str:
        """Extract text from a CSV file."""
        try:
            df = pd.read_csv(file_path)
            
            # Convert DataFrame to text
            text_parts = []
            
            # Add column names
            text_parts.append("Columns: " + ", ".join(df.columns.tolist()))
            text_parts.append("\n")
            
            # Add data
            for index, row in df.iterrows():
                row_text = " ".join(str(value) for value in row.values)
                text_parts.append(row_text)
            
            return " ".join(text_parts)
        except Exception as e:
            raise Exception(f"Error reading CSV: {str(e)}")
    
    def _extract_text_excel(self, file_path: str) -> str:
        """Extract text from an Excel file."""
        try:
            # Read all sheets
            excel_file = pd.ExcelFile(file_path)
            text_parts = []
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                # Add sheet name
                text_parts.append(f"Sheet: {sheet_name}")
                text_parts.append("Columns: " + ", ".join(df.columns.tolist()))
                text_parts.append("\n")
                
                # Add data
                for index, row in df.iterrows():
                    row_text = " ".join(str(value) for value in row.values)
                    text_parts.append(row_text)
                
                text_parts.append("\n")
            
            return " ".join(text_parts)
        except Exception as e:
            raise Exception(f"Error reading Excel: {str(e)}")
    
    def _extract_text_html(self, file_path: str) -> str:
        """Extract text from an HTML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            raise Exception(f"Error reading HTML: {str(e)}")
    
    def batch_process_files(self, file_paths: List[str]) -> List[Dict[str, any]]:
        """
        Process multiple files and extract text from each.
        
        Args:
            file_paths: List of file paths to process
            
        Returns:
            List of dictionaries containing extraction results
        """
        results = []
        
        for file_path in file_paths:
            result = self.extract_text_from_file(file_path)
            result['file_path'] = file_path
            results.append(result)
        
        return results
    
    def validate_file(self, file_path: str) -> Dict[str, any]:
        """
        Validate a file before processing.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing validation results
        """
        try:
            if not os.path.exists(file_path):
                return {
                    'valid': False,
                    'error': 'File does not exist'
                }
            
            if not os.path.isfile(file_path):
                return {
                    'valid': False,
                    'error': 'Path is not a file'
                }
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                return {
                    'valid': False,
                    'error': f'File size ({file_size} bytes) exceeds maximum allowed size ({self.max_file_size} bytes)'
                }
            
            # Check file extension
            _, ext = os.path.splitext(file_path.lower())
            if ext not in self.supported_extensions:
                return {
                    'valid': False,
                    'error': f'Unsupported file type: {ext}'
                }
            
            return {
                'valid': True,
                'file_size': file_size,
                'file_type': ext
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Error validating file: {str(e)}'
            } 