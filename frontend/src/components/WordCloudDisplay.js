import React, { useState, useEffect } from 'react';

const WordCloudDisplay = ({ imageBase64, wordFrequencies, wordContext, sentiment, topWords, stats, onReset }) => {
  const [selectedWord, setSelectedWord] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [animateCloud, setAnimateCloud] = useState(false);

  useEffect(() => {
    if (imageBase64) {
      setAnimateCloud(false);
      setTimeout(() => setAnimateCloud(true), 50);
    }
  }, [imageBase64]);

  const handleDownload = () => {
    if (!imageBase64) return;
    
    const link = document.createElement('a');
    link.href = `data:image/png;base64,${imageBase64}`;
    link.download = 'word-cloud.png';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleCopyImage = async () => {
    try {
      const response = await fetch(`data:image/png;base64,${imageBase64}`);
      const blob = await response.blob();
      await navigator.clipboard.write([
        new window.ClipboardItem({
          'image/png': blob
        })
      ]);
      alert('Image copied to clipboard!');
    } catch (error) {
      console.error('Failed to copy image:', error);
      alert('Failed to copy image to clipboard');
    }
  };

  const handleWordClick = (word) => {
    setSelectedWord(word);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedWord(null);
  };

  // Helper for sentiment summary
  const getSentimentLabel = (polarity) => {
    if (polarity === undefined || polarity === null) return 'Unknown';
    if (polarity > 0.2) return 'Positive';
    if (polarity < -0.2) return 'Negative';
    return 'Neutral';
  };

  // Find max frequency for bar chart scaling
  const maxTopWordFreq = topWords && Array.isArray(topWords) && topWords.length > 0 ? Math.max(...topWords.map(([_, freq]) => freq || 0)) : 1;

  if (!imageBase64) {
    return null;
  }

  return (
    <div className="card max-w-6xl mx-auto bg-white/70 backdrop-blur-md shadow-2xl rounded-2xl border border-gray-200 p-4 transition-all duration-500">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900 drop-shadow-sm">Your Word Cloud</h2>
        <button
          onClick={onReset}
          className="text-gray-500 hover:text-gray-700 text-sm font-medium"
        >
          Generate New
        </button>
      </div>

      {stats && (
        <div className="flex justify-center mb-6 p-4 bg-gray-50 rounded-lg">
          <div className="grid grid-cols-2 gap-8">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary-600">{stats.total_words}</div>
              <div className="text-sm text-gray-600">Unique Words</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-primary-600">{stats.text_length}</div>
              <div className="text-sm text-gray-600">Characters</div>
            </div>
          </div>
        </div>
      )}

      {/* Sentiment Analysis Section */}
      {sentiment && sentiment.polarity !== undefined && sentiment.subjectivity !== undefined && (
        <div className="mb-6 p-4 bg-blue-50 rounded-lg flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <div className="text-lg font-semibold text-blue-800 mb-1">Sentiment Analysis</div>
            <div className="text-sm text-gray-700">
              <span className="font-medium">Polarity:</span> {sentiment.polarity.toFixed(2)} ({getSentimentLabel(sentiment.polarity)})
              <span className="ml-4 font-medium">Subjectivity:</span> {sentiment.subjectivity.toFixed(2)}
            </div>
          </div>
        </div>
      )}

      <div className="flex justify-center mb-6">
        <div className="relative group">
          <img
            src={`data:image/png;base64,${imageBase64}`}
            alt="Generated Word Cloud"
            className={`max-w-full h-auto rounded-xl shadow-xl border border-gray-200 transition-all duration-700 ease-out ${animateCloud ? 'opacity-100 scale-100' : 'opacity-0 scale-95'} group-hover:shadow-2xl group-hover:shadow-blue-200`}
            style={{ boxShadow: animateCloud ? '0 8px 32px 0 rgba(31, 38, 135, 0.18)' : undefined }}
          />
          {/* Parallax/Glow effect on hover */}
          <div className="absolute inset-0 pointer-events-none group-hover:shadow-[0_0_40px_10px_rgba(59,130,246,0.15)] rounded-xl transition-all duration-300" />
          {/* Overlay with animated buttons */}
          <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all duration-300 rounded-xl flex items-center justify-center opacity-0 group-hover:opacity-100">
            <div className="flex space-x-4 animate-fade-in-up">
              <button
                onClick={handleDownload}
                className="bg-white/90 text-gray-800 px-5 py-2 rounded-xl shadow-lg hover:bg-blue-100 hover:text-blue-700 transition-colors duration-200 flex items-center font-semibold backdrop-blur-md"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Download
              </button>
              <button
                onClick={handleCopyImage}
                className="bg-white/90 text-gray-800 px-5 py-2 rounded-xl shadow-lg hover:bg-blue-100 hover:text-blue-700 transition-colors duration-200 flex items-center font-semibold backdrop-blur-md"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                Copy
              </button>
            </div>
          </div>
        </div>
      </div>

      {wordFrequencies && Object.keys(wordFrequencies).length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Word Frequencies</h3>
          <div className="max-h-64 overflow-y-auto animate-fade-in-up">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
              {Object.entries(wordFrequencies)
                .sort(([,a], [,b]) => (b || 0) - (a || 0))
                .slice(0, 20)
                .map(([word, frequency], idx) => (
                  <button
                    key={word}
                    className="flex justify-between items-center p-2 bg-gray-50 rounded-lg hover:bg-blue-100 hover:scale-105 hover:shadow-md transition-all duration-200 w-full text-left group"
                    style={{ transitionDelay: `${idx * 30}ms` }}
                    onClick={() => handleWordClick(word)}
                  >
                    <span className="text-sm font-medium text-gray-700 group-hover:text-blue-700 transition-colors duration-200">{word}</span>
                    <span className="text-xs text-gray-500 bg-white px-2 py-1 rounded-full group-hover:bg-blue-50 transition-colors duration-200">
                      {frequency || 0}
                    </span>
                  </button>
                ))}
            </div>
            {Object.keys(wordFrequencies).length > 20 && (
              <p className="text-sm text-gray-500 mt-2 text-center">
                Showing top 20 words. Total: {Object.keys(wordFrequencies).length} unique words
              </p>
            )}
          </div>
        </div>
      )}

      {/* Modal for word context */}
      {showModal && selectedWord && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
          <div className="bg-white rounded-lg shadow-lg max-w-lg w-full p-6 relative">
            <button
              onClick={closeModal}
              className="absolute top-2 right-2 text-gray-400 hover:text-gray-700 text-2xl font-bold focus:outline-none"
              aria-label="Close"
            >
              &times;
            </button>
            <h4 className="text-xl font-bold mb-2 text-primary-700">{selectedWord}</h4>
            <div className="mb-2 text-gray-700">
              <span className="font-semibold">Frequency:</span> {wordFrequencies && wordFrequencies[selectedWord] ? wordFrequencies[selectedWord] : 0}
            </div>
            <div>
              <span className="font-semibold">Context:</span>
              <ul className="list-disc list-inside mt-2 max-h-48 overflow-y-auto">
                {(wordContext && wordContext[selectedWord] && wordContext[selectedWord].length > 0) ? (
                  wordContext[selectedWord].map((sentence, idx) => (
                    <li key={idx} className="text-gray-600 mb-1">{sentence}</li>
                  ))
                ) : (
                  <li className="text-gray-400">No context found.</li>
                )}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Top Words Bar Chart (move to last) */}
      {topWords && Array.isArray(topWords) && topWords.length > 0 && (
        <div className="mt-8">
          <div className="text-lg font-semibold text-gray-900 mb-2">Top Words</div>
          <div className="space-y-2">
            {topWords.map(([word, freq]) => (
              <div key={word} className="flex items-center">
                <span className="w-24 text-sm text-gray-700 font-medium">{word}</span>
                <div className="flex-1 h-4 bg-primary-100 rounded mr-2 ml-2">
                  <div
                    className="h-4 bg-primary-500 rounded"
                    style={{ width: `${((freq || 0) / maxTopWordFreq) * 100}%` }}
                  ></div>
                </div>
                <span className="text-xs text-gray-600">{freq || 0}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="flex justify-center space-x-4 mt-6">
        <button
          onClick={handleDownload}
          className="btn-primary flex items-center"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Download PNG
        </button>
        
        <button
          onClick={handleCopyImage}
          className="btn-secondary flex items-center"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          Copy to Clipboard
        </button>
      </div>
    </div>
  );
};

export default WordCloudDisplay; 