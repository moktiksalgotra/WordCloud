import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Font options for word clouds
const FONT_OPTIONS = [
  { value: 'arial', label: 'Arial (Sans-serif)' },
  { value: 'times new roman', label: 'Times New Roman (Serif)' },
  { value: 'courier new', label: 'Courier New (Monospace)' },
  { value: 'georgia', label: 'Georgia (Serif)' },
  { value: 'verdana', label: 'Verdana (Sans-serif)' },
  { value: 'impact', label: 'Impact (Display)' },
  { value: 'comic sans ms', label: 'Comic Sans MS (Casual)' },
  { value: 'tahoma', label: 'Tahoma (Sans-serif)' },
  { value: 'trebuchet ms', label: 'Trebuchet MS (Sans-serif)' }
];

// Color scheme options with actual color values
const COLOR_SCHEMES = [
  { value: 'viridis', label: 'Viridis (Blue-Green-Yellow)', preview: ['#440154', '#443982', '#31688e', '#21918c', '#35b779', '#8fd744', '#fde725'] },
  { value: 'plasma', label: 'Plasma (Purple-Orange-Yellow)', preview: ['#0d0887', '#5302a3', '#8b0aa5', '#b83289', '#db5c68', '#f48849', '#febc2a'] },
  { value: 'inferno', label: 'Inferno (Black-Red-Yellow)', preview: ['#000004', '#320a5a', '#781c6d', '#bb3754', '#ed6925', '#fbb61a', '#fcffa4'] },
  { value: 'magma', label: 'Magma (Black-Red-White)', preview: ['#000004', '#2c115f', '#711f81', '#b73779', '#f0605d', '#feae76', '#fbfcbf'] },
  { value: 'cividis', label: 'Cividis (Blue-Yellow)', preview: ['#00204c', '#213d6b', '#555b6c', '#7a7a78', '#a59c74', '#d3c064', '#ffe945'] },
  { value: 'rainbow', label: 'Rainbow', preview: ['#6e40aa', '#1f77b4', '#56b4e9', '#3fa34d', '#eaff00', '#ff7f0e', '#e31a1c'] },
  { value: 'blues', label: 'Blues', preview: ['#f7fbff', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#084594'] },
  { value: 'reds', label: 'Reds', preview: ['#fff5f0', '#fee0d2', '#fcbba1', '#fc9272', '#fb6a4a', '#de2d26', '#a50f15'] },
  { value: 'greens', label: 'Greens', preview: ['#f7fcf5', '#e5f5e0', '#c7e9c0', '#a1d99b', '#74c476', '#41ab5d', '#006d2c'] },
  { value: 'purples', label: 'Purples', preview: ['#fcfbfd', '#efedf5', '#dadaeb', '#bcbddc', '#9e9ac8', '#807dba', '#4a1486'] },
  { value: 'greys', label: 'Greys', preview: ['#ffffff', '#f0f0f0', '#d9d9d9', '#bdbdbd', '#969696', '#636363', '#252525'] },
  { value: 'spectral', label: 'Spectral', preview: ['#9e0142', '#d53e4f', '#f46d43', '#fdae61', '#fee08b', '#e6f598', '#3288bd'] },
  { value: 'coolwarm', label: 'Cool-Warm', preview: ['#3b4cc0', '#6789ee', '#9fc3fe', '#dddcdc', '#f6b69b', '#e6745a', '#b40426'] },
  { value: 'custom', label: 'Custom Colors', preview: [] }
];

// Background color choices
const BACKGROUND_COLORS = [
  { value: 'white', label: 'White', color: '#ffffff' },
  { value: 'black', label: 'Black', color: '#000000' },
  { value: 'transparent', label: 'Transparent', color: 'transparent' },
  { value: 'lightgrey', label: 'Light Grey', color: '#f0f0f0' },
  { value: 'darkgrey', label: 'Dark Grey', color: '#333333' },
  { value: 'lightblue', label: 'Light Blue', color: '#e6f7ff' },
  { value: 'lightgreen', label: 'Light Green', color: '#e6fff0' },
  { value: 'lightred', label: 'Light Red', color: '#fff0f0' },
  { value: 'custom', label: 'Custom Color', color: '' }
];

const WordCloudInput = ({ onGenerate, isLoading, initialText = '', onClear }) => {
  const [removeStopwords, setRemoveStopwords] = useState(true);
  const [customStopwords, setCustomStopwords] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [minFreq, setMinFreq] = useState('');
  const [maxFreq, setMaxFreq] = useState('');
  const [maskPreviewUrl, setMaskPreviewUrl] = useState('');
  const [previewError, setPreviewError] = useState(false);
  
  // New customization states
  const [fontFamily, setFontFamily] = useState('arial');
  const [colorScheme, setColorScheme] = useState('viridis');
  const [customColors, setCustomColors] = useState('');
  const [backgroundColor, setBackgroundColor] = useState('white');
  const [customBackgroundColor, setCustomBackgroundColor] = useState('#ffffff');
  const [wordScaling, setWordScaling] = useState(0.5);
  const [maxWords, setMaxWords] = useState(200);
  const [minFontSize, setMinFontSize] = useState(10);
  const [maxFontSize, setMaxFontSize] = useState(100);
  const [dimension, setDimension] = useState({ width: 800, height: 600 });
  const [showColorInfo, setShowColorInfo] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('handleSubmit called, initialText:', initialText);
    if (!initialText.trim()) {
      alert('Please enter some text to generate a word cloud.');
      return;
    }
    const customStopwordsList = customStopwords
      .split(',')
      .map(word => word.trim())
      .filter(word => word.length > 0);
    let colors = colorScheme;
    if (colorScheme === 'custom' && customColors) {
      colors = customColors
        .split(',')
        .map(color => color.trim())
        .filter(color => color.length > 0);
    }
    let bgColor = backgroundColor;
    if (backgroundColor === 'custom') {
      bgColor = customBackgroundColor;
    }
    onGenerate({
      text: initialText.trim(),
      remove_stopwords: removeStopwords,
      custom_stopwords: customStopwordsList,
      min_frequency: minFreq !== '' ? parseInt(minFreq, 10) : null,
      max_frequency: maxFreq !== '' ? parseInt(maxFreq, 10) : null,
      color_scheme: colors,
      background_color: bgColor,
      font_family: fontFamily,
      width: dimension.width,
      height: dimension.height,
      max_words: Number(maxWords),
      min_font_size: Number(minFontSize),
      max_font_size: Number(maxFontSize),
      relative_scaling: Number(wordScaling),
    });
  };

  const handleClear = () => {
    setRemoveStopwords(true);
    setCustomStopwords('');
    setShowAdvanced(false);
    setMinFreq('');
    setMaxFreq('');
    setFontFamily('arial');
    setColorScheme('viridis');
    setCustomColors('');
    setBackgroundColor('white');
    setCustomBackgroundColor('#ffffff');
    setWordScaling(0.5);
    setMaxWords(200);
    setMinFontSize(10);
    setMaxFontSize(100);
    setDimension({ width: 800, height: 600 });
    setShowColorInfo(false);
    if (onClear) onClear();
  };

  const handleDimensionChange = (dim, value) => {
    const numValue = parseInt(value, 10);
    if (!isNaN(numValue)) {
      setDimension(prev => ({
        ...prev,
        [dim]: numValue
      }));
    }
  };

  return (
    <div className="card max-w-4xl mx-auto">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* No text input here; text is provided by parent */}

        {/* Advanced Options Toggle */}
        <div className="flex items-center">
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="text-primary-600 hover:text-primary-700 font-medium text-sm flex items-center"
          >
            {showAdvanced ? 'Hide' : 'Show'} Advanced Options
            <svg
              className={`ml-1 w-4 h-4 transform transition-transform ${showAdvanced ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>

        {/* Advanced Options */}
        {showAdvanced && (
          <div className="space-y-8 p-6 bg-gray-50 rounded-lg">
            {/* Customization Tabs */}
            <div className="border-b border-gray-200">
              <nav className="-mb-px flex space-x-8" aria-label="Tabs">
                <button
                  type="button"
                  className="border-blue-500 text-blue-600 whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm"
                >
                  Customization Options
                </button>
              </nav>
            </div>
          
            {/* Section: Basic Settings */}
            <div className="space-y-4">
              <h3 className="text-base font-medium text-gray-800">Basic Settings</h3>
              
              {/* Stopword Removal */}
              <div className="flex items-center">
                <input
                  id="remove-stopwords"
                  type="checkbox"
                  checked={removeStopwords}
                  onChange={(e) => setRemoveStopwords(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  disabled={isLoading}
                />
                <label htmlFor="remove-stopwords" className="ml-2 block text-sm text-gray-700">
                  Remove common stopwords (the, and, or, etc.)
                </label>
              </div>

              {/* Custom Stopwords */}
              <div>
                <label htmlFor="custom-stopwords" className="block text-sm font-medium text-gray-700 mb-1">
                  Custom stopwords (comma-separated)
                </label>
                <input
                  id="custom-stopwords"
                  type="text"
                  value={customStopwords}
                  onChange={(e) => setCustomStopwords(e.target.value)}
                  placeholder="word1, word2, word3"
                  className="input-field"
                  disabled={isLoading}
                />
              </div>
              
              {/* Frequency Thresholds */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="min-frequency" className="block text-sm font-medium text-gray-700 mb-1">
                    Min Frequency
                  </label>
                  <input
                    id="min-frequency"
                    type="number"
                    min="1"
                    value={minFreq}
                    onChange={e => setMinFreq(e.target.value)}
                    className="input-field"
                    placeholder="e.g. 2"
                    disabled={isLoading}
                  />
                </div>
                <div>
                  <label htmlFor="max-frequency" className="block text-sm font-medium text-gray-700 mb-1">
                    Max Frequency
                  </label>
                  <input
                    id="max-frequency"
                    type="number"
                    min="1"
                    value={maxFreq}
                    onChange={e => setMaxFreq(e.target.value)}
                    className="input-field"
                    placeholder="e.g. 10"
                    disabled={isLoading}
                  />
                </div>
              </div>
            </div>

            {/* Section: Appearance */}
            <div className="space-y-4 pt-4 border-t border-gray-200">
              <h3 className="text-base font-medium text-gray-800">Appearance</h3>
              
              {/* Font Selection */}
              <div>
                <label htmlFor="font-family" className="block text-sm font-medium text-gray-700 mb-1">
                  Font Family
                </label>
                <select
                  id="font-family"
                  value={fontFamily}
                  onChange={(e) => setFontFamily(e.target.value)}
                  className="input-field"
                  disabled={isLoading}
                >
                  {FONT_OPTIONS.map(font => (
                    <option key={font.value} value={font.value}>
                      {font.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Color Scheme */}
              <div>
                <div className="flex justify-between items-center mb-1">
                  <label htmlFor="color-scheme" className="block text-sm font-medium text-gray-700">
                    Color Scheme
                  </label>
                  <button 
                    type="button" 
                    className="text-xs text-blue-600 hover:text-blue-800"
                    onClick={() => setShowColorInfo(!showColorInfo)}
                  >
                    {showColorInfo ? "Hide info" : "What's this?"}
                  </button>
                </div>
                {showColorInfo && (
                  <div className="mb-3 p-3 bg-blue-50 text-xs text-blue-700 rounded-md">
                    Color schemes determine how words are colored based on their frequency or importance.
                    Each scheme provides a gradient of colors that will be applied to your word cloud.
                  </div>
                )}
                
                <select
                  id="color-scheme"
                  value={colorScheme}
                  onChange={(e) => setColorScheme(e.target.value)}
                  className="input-field mb-2"
                  disabled={isLoading}
                >
                  {COLOR_SCHEMES.map(scheme => (
                    <option key={scheme.value} value={scheme.value}>
                      {scheme.label}
                    </option>
                  ))}
                </select>
                
                {/* Color scheme preview */}
                {colorScheme !== 'custom' && (
                  <div className="flex space-x-1 h-4">
                    {COLOR_SCHEMES.find(s => s.value === colorScheme)?.preview.map((color, index) => (
                      <div 
                        key={index} 
                        className="flex-1 h-4 rounded-sm" 
                        style={{backgroundColor: color}} 
                        title={color}
                      />
                    ))}
                  </div>
                )}
                
                {/* Custom colors input */}
                {colorScheme === 'custom' && (
                  <div>
                    <label htmlFor="custom-colors" className="block text-sm font-medium text-gray-700 mt-2 mb-1">
                      Custom Colors (comma-separated hex values)
                    </label>
                    <input
                      id="custom-colors"
                      type="text"
                      value={customColors}
                      onChange={(e) => setCustomColors(e.target.value)}
                      placeholder="#ff0000, #00ff00, #0000ff"
                      className="input-field"
                      disabled={isLoading}
                    />
                    <p className="mt-1 text-xs text-gray-500">
                      Example: #ff0000, #00ff00, #0000ff for red, green, blue gradient
                    </p>
                  </div>
                )}
              </div>

              {/* Background Color */}
              <div>
                <label htmlFor="background-color" className="block text-sm font-medium text-gray-700 mb-1">
                  Background Color
                </label>
                <div className="flex space-x-2">
                  <select
                    id="background-color"
                    value={backgroundColor}
                    onChange={(e) => setBackgroundColor(e.target.value)}
                    className="input-field flex-grow"
                    disabled={isLoading}
                  >
                    {BACKGROUND_COLORS.map(bg => (
                      <option key={bg.value} value={bg.value}>
                        {bg.label}
                      </option>
                    ))}
                  </select>
                  
                  <div className="w-10 h-10 border border-gray-300 rounded flex items-center justify-center">
                    {backgroundColor !== 'custom' ? (
                      <div 
                        className="w-8 h-8 rounded" 
                        style={{
                          backgroundColor: BACKGROUND_COLORS.find(bg => bg.value === backgroundColor)?.color,
                          backgroundImage: backgroundColor === 'transparent' ? 
                            'repeating-conic-gradient(#CCCCCC 0% 25%, white 0% 50%)' : 
                            'none',
                          backgroundSize: '10px 10px'
                        }}
                      />
                    ) : (
                      <div 
                        className="w-8 h-8 rounded" 
                        style={{backgroundColor: customBackgroundColor}}
                      />
                    )}
                  </div>
                </div>

                {backgroundColor === 'custom' && (
                  <div className="mt-2">
                    <label htmlFor="custom-bg-color" className="block text-sm font-medium text-gray-700 mb-1">
                      Custom Background Color
                    </label>
                    <input
                      id="custom-bg-color"
                      type="color"
                      value={customBackgroundColor}
                      onChange={(e) => setCustomBackgroundColor(e.target.value)}
                      className="w-full h-10 p-1 rounded border border-gray-300"
                      disabled={isLoading}
                    />
                  </div>
                )}
              </div>
            </div>

            {/* Section: Layout & Dimensions */}
            <div className="space-y-4 pt-4 border-t border-gray-200">
              <h3 className="text-base font-medium text-gray-800">Dimensions</h3>
              
              {/* Dimensions */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="width" className="block text-sm font-medium text-gray-700 mb-1">
                    Width (px)
                  </label>
                  <input
                    id="width"
                    type="number"
                    min="100"
                    max="3000"
                    value={dimension.width}
                    onChange={(e) => handleDimensionChange('width', e.target.value)}
                    className="input-field"
                    disabled={isLoading}
                  />
                </div>
                <div>
                  <label htmlFor="height" className="block text-sm font-medium text-gray-700 mb-1">
                    Height (px)
                  </label>
                  <input
                    id="height"
                    type="number"
                    min="100"
                    max="3000"
                    value={dimension.height}
                    onChange={(e) => handleDimensionChange('height', e.target.value)}
                    className="input-field"
                    disabled={isLoading}
                  />
                </div>
              </div>
            </div>
            
            {/* Section: Word Sizing */}
            <div className="space-y-4 pt-4 border-t border-gray-200">
              <h3 className="text-base font-medium text-gray-800">Word Sizing</h3>
              
              {/* Max Words */}
              <div>
                <label htmlFor="max-words" className="block text-sm font-medium text-gray-700 mb-1">
                  Maximum Number of Words
                </label>
                <input
                  id="max-words"
                  type="number"
                  min="10"
                  max="1000"
                  value={maxWords}
                  onChange={(e) => setMaxWords(e.target.value)}
                  className="input-field"
                  disabled={isLoading}
                />
              </div>
              
              {/* Font Size Range */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="min-font-size" className="block text-sm font-medium text-gray-700 mb-1">
                    Minimum Font Size (px)
                  </label>
                  <input
                    id="min-font-size"
                    type="number"
                    min="1"
                    max="100"
                    value={minFontSize}
                    onChange={(e) => setMinFontSize(e.target.value)}
                    className="input-field"
                    disabled={isLoading}
                  />
                </div>
                <div>
                  <label htmlFor="max-font-size" className="block text-sm font-medium text-gray-700 mb-1">
                    Maximum Font Size (px)
                  </label>
                  <input
                    id="max-font-size"
                    type="number"
                    min="10"
                    max="300"
                    value={maxFontSize}
                    onChange={(e) => setMaxFontSize(e.target.value)}
                    className="input-field"
                    disabled={isLoading}
                  />
                </div>
              </div>
              
              {/* Word Scaling */}
              <div>
                <label htmlFor="word-scaling" className="block text-sm font-medium text-gray-700 mb-1">
                  Word Size Scaling (0.0 - 1.0)
                </label>
                <div className="flex items-center space-x-2">
                  <input
                    id="word-scaling"
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={wordScaling}
                    onChange={(e) => setWordScaling(e.target.value)}
                    className="w-full"
                    disabled={isLoading}
                  />
                  <span className="text-sm text-gray-700">{wordScaling}</span>
                </div>
                <p className="mt-1 text-xs text-gray-500">
                  Higher values create greater size differences between words based on frequency.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex space-x-4">
          <button
            type="submit"
            disabled={isLoading || initialText.trim().length < 10}
            className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Generating...
              </span>
            ) : (
              'Generate Word Cloud'
            )}
          </button>
          
          <button
            type="button"
            onClick={handleClear}
            disabled={isLoading}
            className="btn-secondary px-6 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Clear
          </button>
        </div>
        {initialText.trim().length > 0 && initialText.trim().length < 10 && (
          <div className="text-red-500 text-sm mt-2">Please enter at least 10 characters to generate a word cloud.</div>
        )}
      </form>
    </div>
  );
};

export default WordCloudInput; 