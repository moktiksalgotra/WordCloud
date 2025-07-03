import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import WordCloudInput from './WordCloudInput';
import WordCloudDisplay from './WordCloudDisplay';
import MultiSourceInput from './MultiSourceInput';
import { CloudIcon, DocumentTextIcon, LinkIcon } from '@heroicons/react/24/outline';

const API_BASE_URL = process.env.REACT_APP_API_URL;

const WordCloudGenerator = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [wordCloudData, setWordCloudData] = useState(null);
  const [error, setError] = useState(null);
  const [inputType, setInputType] = useState('text');
  const [text, setText] = useState('');
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState('');
  const [progress, setProgress] = useState(0);
  const navigate = useNavigate();
  const location = useLocation();

  // Check for ?id=... in the URL
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const wordcloudId = params.get('id');
    if (wordcloudId) {
      // Fetch the word cloud from the backend
      setIsLoading(true);
      setError(null);
      axios.get(`${API_BASE_URL}/api/export/${wordcloudId}?format=json`)
        .then((response) => {
          if (response.data.success && response.data.wordcloud) {
            const wc = response.data.wordcloud;
            setWordCloudData({
              imageBase64: wc.image_base64,
              wordFrequencies: wc.word_frequencies,
              wordContext: wc.word_context,
              sentiment: wc.sentiment_analysis,
              topWords: wc.top_words,
              stats: {
                total_words: wc.word_count,
                unique_words: wc.unique_words,
                ...wc.text_statistics
              },
              title: wc.title,
              created_at: wc.created_at
            });
          } else {
            setError('Word cloud not found.');
          }
        })
        .catch((err) => {
          setError('Failed to load word cloud.');
        })
        .finally(() => setIsLoading(false));
    } else {
      setWordCloudData(null);
    }
  }, [location.search]);

  const handleGenerate = async (inputData) => {
    setIsLoading(true);
    setError(null);
    try {
      // Ensure numeric values are properly converted to integers
      const minFreq = inputData.min_frequency !== undefined && inputData.min_frequency !== '' 
        ? parseInt(inputData.min_frequency, 10) 
        : null;
      const maxFreq = inputData.max_frequency !== undefined && inputData.max_frequency !== '' 
        ? parseInt(inputData.max_frequency, 10) 
        : null;
      // Input validation for minFreq and maxFreq
      if ((minFreq !== null && isNaN(minFreq)) || (maxFreq !== null && isNaN(maxFreq))) {
        setError('Please enter valid numbers for minimum and maximum frequency.');
        setIsLoading(false);
        return;
      }
      
      console.log(`DEBUG: Sending min_frequency=${minFreq}, max_frequency=${maxFreq}`);
      
      const response = await axios.post(`${API_BASE_URL}/api/generate_wordcloud`, {
        text: inputData.text,
        settings: {
          remove_stopwords: inputData.remove_stopwords,
          custom_stopwords: inputData.custom_stopwords,
          mask_shape: inputData.mask_shape || 'none',
          min_frequency: minFreq,
          max_frequency: maxFreq,
          color_scheme: inputData.color_scheme || 'viridis',
          background_color: inputData.background_color || 'white',
          font_family: inputData.font_family || 'arial',
          width: inputData.width || 800,
          height: inputData.height || 600,
          max_words: inputData.max_words || 200,
          min_font_size: inputData.min_font_size || 10,
          max_font_size: inputData.max_font_size || 100,
          relative_scaling: inputData.relative_scaling || 0.5,
          prefer_horizontal: inputData.prefer_horizontal || 0.7,
          collocations: true,
          lemmatize: true,
          remove_numbers: true,
          min_word_length: 2
        },
        title: 'Generated Word Cloud',
        tags: ['generated']
      });
      if (response.data.success) {
        setWordCloudData({
          imageBase64: response.data.image_base64,
          wordFrequencies: response.data.word_frequencies,
          wordContext: response.data.word_context,
          sentiment: response.data.sentiment_analysis,
          topWords: response.data.top_words,
          stats: response.data.text_statistics
        });
      } else {
        setError(response.data.error || 'Failed to generate word cloud');
      }
    } catch (err) {
      console.error('Error generating word cloud:', err);
      setError(err.response?.data?.error || 'An error occurred while generating the word cloud');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setWordCloudData(null);
    setError(null);
    // Remove ?id=... from the URL
    navigate('/generator', { replace: true });
  };

  // File upload handlers
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setFileName(selectedFile.name);
    }
  };

  const handleFileSubmit = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }
    setIsLoading(true);
    setProgress(10);
    const formData = new FormData();
    formData.append('file', file);
    try {
      setProgress(30);
      const response = await axios.post(`${API_BASE_URL}/api/upload_file`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setProgress(100);
      if (response.data.success) {
        setText(response.data.text);
        setError(null);
      } else {
        setError(response.data.error || 'Failed to extract text from file');
      }
    } catch (error) {
      setError('Error uploading file: ' + (error.response?.data?.error || error.message));
    } finally {
      setIsLoading(false);
      setProgress(0);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-10 px-2 sm:px-0">
      <div className="max-w-2xl mx-auto">
        {/* Header Section */}
        <div className="flex flex-col items-center justify-center mb-8">
          <CloudIcon className="w-16 h-16 text-blue-500 mb-2" />
          <h1 className="text-5xl font-extrabold text-gray-900 leading-tight text-center">WordCloud Generator</h1>
          <p className="text-xl text-gray-500 mt-2 font-normal text-center max-w-2xl">Create beautiful, professional word clouds from your text with advanced customization options.</p>
        </div>
        {/* Card Container */}
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <div>
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Choose Your Input Source</h2>
            <div className="flex space-x-2 mb-6">
              <button
                className={`flex items-center px-5 py-2 rounded-full font-medium transition-colors duration-150 border ${inputType === 'text' ? 'bg-blue-50 text-blue-700 border-blue-200 shadow' : 'bg-gray-50 text-gray-500 border-gray-200 hover:bg-blue-50 hover:text-blue-700'} focus:outline-none`}
                onClick={() => setInputType('text')}
              >
                <DocumentTextIcon className="w-5 h-5 mr-2" /> Direct Text
              </button>
              <button
                className={`flex items-center px-5 py-2 rounded-full font-medium transition-colors duration-150 border ${inputType === 'file' ? 'bg-blue-50 text-blue-700 border-blue-200 shadow' : 'bg-gray-50 text-gray-500 border-gray-200 hover:bg-blue-50 hover:text-blue-700'} focus:outline-none`}
                onClick={() => setInputType('file')}
              >
                <CloudIcon className="w-5 h-5 mr-2" /> Upload File
              </button>
            </div>
          </div>
          {/* Input Area */}
          <div className="mb-10">
            {inputType === 'text' && (
              <div>
                <label htmlFor="text-input" className="block text-base font-medium text-gray-700 mb-2">
                  Enter your text
                </label>
                <textarea
                  id="text-input"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="Paste or type your text here... (minimum 10 characters)"
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-400 h-48 resize-none text-base"
                  disabled={isLoading}
                  required
                />
                <p className="mt-1 text-sm text-gray-400">{text.length} characters</p>
              </div>
            )}
            {inputType === 'file' && (
              <div>
                <label className="block text-base font-medium text-gray-700 mb-2">Upload a file</label>
                <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-xl bg-gray-50">
                  <div className="space-y-1 text-center">
                    <CloudIcon className="mx-auto h-12 w-12 text-gray-400" />
                    <div className="flex text-sm text-gray-600 justify-center">
                      <label htmlFor="file-upload" className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500">
                        <span>Upload a file</span>
                        <input
                          id="file-upload"
                          name="file-upload"
                          type="file"
                          className="sr-only"
                          onChange={handleFileChange}
                          accept=".txt,.pdf,.docx,.doc,.csv,.xlsx,.xls,.html,.htm"
                          disabled={isLoading}
                        />
                      </label>
                      <p className="pl-1">or drag and drop</p>
                    </div>
                    <p className="text-xs text-gray-500">Supported formats: TXT, PDF, DOCX, DOC, CSV, XLSX, XLS, HTML</p>
                  </div>
                </div>
                {fileName && (
                  <div className="mt-3 text-sm text-gray-500">Selected file: {fileName}</div>
                )}
                {isLoading && (
                  <div className="mt-4">
                    <div className="relative pt-1">
                      <div className="flex mb-2 items-center justify-between">
                        <div>
                          <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-blue-600 bg-blue-200">Processing</span>
                        </div>
                        <div className="text-right">
                          <span className="text-xs font-semibold inline-block text-blue-600">{progress}%</span>
                        </div>
                      </div>
                      <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-blue-200">
                        <div style={{ width: `${progress}%` }} className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-blue-500"></div>
                      </div>
                    </div>
                  </div>
                )}
                <div className="mt-4">
                  <button
                    onClick={handleFileSubmit}
                    disabled={isLoading || !file}
                    className="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-lg shadow-md transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoading ? 'Processing...' : 'Extract Text & Continue'}
                  </button>
                </div>
              </div>
            )}
          </div>
          {/* Customization Options */}
          <WordCloudInput
            onGenerate={handleGenerate}
            isLoading={isLoading}
            initialText={text}
            onClear={() => setText('')}
          />
          {/* Show WordCloudDisplay when wordCloudData is set */}
          {wordCloudData && (
            <WordCloudDisplay
              imageBase64={wordCloudData.imageBase64}
              wordFrequencies={wordCloudData.wordFrequencies}
              wordContext={wordCloudData.wordContext}
              sentiment={wordCloudData.sentiment}
              topWords={wordCloudData.topWords}
              stats={wordCloudData.stats}
              onReset={handleReset}
              title={wordCloudData.title}
              created_at={wordCloudData.created_at}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default WordCloudGenerator; 