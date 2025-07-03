import React, { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL;

const MultiSourceInput = ({ onTextExtracted, onError }) => {
  const [inputType, setInputType] = useState('text'); // text, file, url
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState('');
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleInputTypeChange = (type) => {
    setInputType(type);
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setFileName(selectedFile.name);
    }
  };

  const handleTextSubmit = () => {
    if (!text.trim()) {
      onError('Please enter some text');
      return;
    }
    onTextExtracted(text);
  };

  const handleFileSubmit = async () => {
    if (!file) {
      onError('Please select a file');
      return;
    }

    setLoading(true);
    setProgress(10);

    const formData = new FormData();
    formData.append('file', file);

    try {
      setProgress(30);
      const response = await axios.post(`${API_BASE_URL}/api/upload_file`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setProgress(100);

      if (response.data.success) {
        onTextExtracted(response.data.text);
      } else {
        onError(response.data.error || 'Failed to extract text from file');
      }
    } catch (error) {
      onError('Error uploading file: ' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
      setProgress(0);
    }
  };

  const handleUrlSubmit = async () => {
    if (!url.trim()) {
      onError('Please enter a URL');
      return;
    }

    if (!url.match(/^https?:\/\//i)) {
      onError('Please enter a valid URL starting with http:// or https://');
      return;
    }

    setLoading(true);
    setProgress(10);

    try {
      setProgress(30);
      const response = await axios.post(`${API_BASE_URL}/api/process_url`, { url });
      setProgress(100);

      if (response.data.success) {
        onTextExtracted(response.data.text);
      } else {
        onError(response.data.error || 'Failed to extract text from URL');
      }
    } catch (error) {
      onError('Error processing URL: ' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
      setProgress(0);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-100 mb-6">
      <h3 className="text-lg font-medium text-gray-800 mb-4">Choose Your Input Source</h3>
      
      {/* Input Type Selection */}
      <div className="flex mb-6 border-b">
        <button
          className={`px-4 py-2 text-sm font-medium ${inputType === 'text' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
          onClick={() => handleInputTypeChange('text')}
        >
          <div className="flex items-center">
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            Direct Text
          </div>
        </button>
        <button
          className={`px-4 py-2 text-sm font-medium ${inputType === 'file' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
          onClick={() => handleInputTypeChange('file')}
        >
          <div className="flex items-center">
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Upload File
          </div>
        </button>
        <button
          className={`px-4 py-2 text-sm font-medium ${inputType === 'url' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
          onClick={() => handleInputTypeChange('url')}
        >
          <div className="flex items-center">
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            Website URL
          </div>
        </button>
      </div>

      {/* Input Type Content */}
      <div className="mt-4">
        {inputType === 'text' && (
          <div>
            <label htmlFor="text-input" className="block text-sm font-medium text-gray-700 mb-2">
              Enter your text
            </label>
            <textarea
              id="text-input"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste or type your text here... (minimum 10 characters)"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 h-48 resize-none"
              disabled={loading}
              required
            />
            <p className="mt-1 text-sm text-gray-500">
              {text.length} characters
            </p>
            <div className="mt-4">
              <button
                onClick={handleTextSubmit}
                disabled={loading || text.trim().length < 10}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Continue
              </button>
            </div>
          </div>
        )}

        {inputType === 'file' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Upload a file
            </label>
            <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
              <div className="space-y-1 text-center">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
                </svg>
                <div className="flex text-sm text-gray-600">
                  <label htmlFor="file-upload" className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500">
                    <span>Upload a file</span>
                    <input
                      id="file-upload"
                      name="file-upload"
                      type="file"
                      className="sr-only"
                      onChange={handleFileChange}
                      accept=".txt,.pdf,.docx,.doc,.csv,.xlsx,.xls,.html,.htm"
                      disabled={loading}
                    />
                  </label>
                  <p className="pl-1">or drag and drop</p>
                </div>
                <p className="text-xs text-gray-500">
                  Supported formats: TXT, PDF, DOCX, DOC, CSV, XLSX, XLS, HTML
                </p>
              </div>
            </div>
            
            {fileName && (
              <div className="mt-3 text-sm text-gray-500">
                Selected file: {fileName}
              </div>
            )}

            {loading && (
              <div className="mt-4">
                <div className="relative pt-1">
                  <div className="flex mb-2 items-center justify-between">
                    <div>
                      <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-blue-600 bg-blue-200">
                        Processing
                      </span>
                    </div>
                    <div className="text-right">
                      <span className="text-xs font-semibold inline-block text-blue-600">
                        {progress}%
                      </span>
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
                disabled={loading || !file}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Processing...' : 'Extract Text & Continue'}
              </button>
            </div>
          </div>
        )}

        {inputType === 'url' && (
          <div>
            <label htmlFor="url-input" className="block text-sm font-medium text-gray-700 mb-2">
              Enter a website URL
            </label>
            <div className="mt-1 flex rounded-md shadow-sm">
              <input
                type="text"
                id="url-input"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com"
                className="flex-1 min-w-0 block w-full px-3 py-2 rounded-md border border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                disabled={loading}
              />
            </div>
            <p className="mt-1 text-sm text-gray-500">
              Enter a valid URL starting with http:// or https://
            </p>

            {loading && (
              <div className="mt-4">
                <div className="relative pt-1">
                  <div className="flex mb-2 items-center justify-between">
                    <div>
                      <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-blue-600 bg-blue-200">
                        Processing
                      </span>
                    </div>
                    <div className="text-right">
                      <span className="text-xs font-semibold inline-block text-blue-600">
                        {progress}%
                      </span>
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
                onClick={handleUrlSubmit}
                disabled={loading || !url.trim()}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Processing...' : 'Extract Text & Continue'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MultiSourceInput; 