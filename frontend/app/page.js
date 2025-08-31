'use client';

import { useState, useRef } from 'react';
import { HeroSection } from '../components/HeroSection';
import { TabNavigation } from '../components/TabNavigation';
import { UploadSection } from '../components/UploadSection';
import { UrlSection } from '../components/UrlSection';
import { ResultsSection } from '../components/ResultsSection';
import { FilterSection } from '../components/FilterSection';

export default function VisualProductMatcher() {
  const [activeTab, setActiveTab] = useState('upload');
  const [selectedFile, setSelectedFile] = useState(null);
  const [imageUrl, setImageUrl] = useState('');
  const [results, setResults] = useState([]);
  const [allResults, setAllResults] = useState([]); // Store all results for filtering
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchInitiated, setSearchInitiated] = useState(false);
  const [minSimilarity, setMinSimilarity] = useState(0.0); // Similarity filter
  const [hasSearchResults, setHasSearchResults] = useState(false); // Track if we have search results
  const uploadSectionRef = useRef(null);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001/api';

  // Scroll to upload section
  const scrollToUpload = () => {
    uploadSectionRef.current?.scrollIntoView({ 
      behavior: 'smooth',
      block: 'start'
    });
  };

  // Search by uploaded image
  const handleUploadSearch = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setError('');
    setSearchInitiated(true);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('min_score', minSimilarity.toString());

      const response = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        const searchResults = data.results || [];
        setAllResults(searchResults);
        setResults(searchResults);
        setHasSearchResults(searchResults.length > 0);
      } else {
        setError(data.error || 'Search failed');
      }
    } catch (err) {
      setError('Network error. Please check if the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  // Search by image URL
  const handleUrlSearch = async () => {
    if (!imageUrl.trim()) return;

    setLoading(true);
    setError('');
    setSearchInitiated(true);

    try {
      const response = await fetch(`${API_BASE}/search-url`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          image_url: imageUrl, 
          min_score: minSimilarity 
        }),
      });

      const data = await response.json();

      if (response.ok) {
        const searchResults = data.results || [];
        setAllResults(searchResults);
        setResults(searchResults);
        setHasSearchResults(searchResults.length > 0);
      } else {
        setError(data.error || 'Search failed');
      }
    } catch (err) {
      setError('Network error. Please check if the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  // Browse all products
  const handleBrowseProducts = async () => {
    setLoading(true);
    setError('');
    setSearchInitiated(true);

    try {
      const response = await fetch(`${API_BASE}/products`);
      const data = await response.json();

      if (response.ok) {
        const products = data.products || [];
        setAllResults(products);
        setResults(products);
        setHasSearchResults(false); // Browse doesn't have similarity scores
      } else {
        setError(data.error || 'Failed to load products');
      }
    } catch (err) {
      setError('Network error. Please check if the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  // Filter results by similarity score
  const handleFilter = () => {
    if (!hasSearchResults) return; // Only filter search results with similarity scores
    
    const filtered = allResults.filter(product => {
      const similarity = product.similarity_score || product.similarity || 0;
      return similarity >= minSimilarity;
    });
    setResults(filtered);
  };

  // Reset filter
  const handleFilterReset = () => {
    setMinSimilarity(0.0);
    setResults(allResults);
  };

  // Reset function
  const handleReset = () => {
    setSelectedFile(null);
    setImageUrl('');
    setResults([]);
    setAllResults([]);
    setError('');
    setSearchInitiated(false);
    setMinSimilarity(0.0);
    setHasSearchResults(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Hero Section */}
      <HeroSection onScrollToUpload={scrollToUpload} />

      {/* Main Content */}
      <div ref={uploadSectionRef} className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Tab Navigation */}
        <div className="py-8 lg:py-12">
          <TabNavigation
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            onReset={handleReset}
            onBrowseProducts={handleBrowseProducts}
          />
        </div>

        {/* Content Sections */}
        <div className="max-w-4xl mx-auto mb-8 lg:mb-12">
          {activeTab === 'upload' && (
            <UploadSection
              selectedFile={selectedFile}
              setSelectedFile={setSelectedFile}
              onSearch={handleUploadSearch}
              loading={loading}
              error={error}
            />
          )}

          {activeTab === 'url' && (
            <UrlSection
              imageUrl={imageUrl}
              setImageUrl={setImageUrl}
              onSearch={handleUrlSearch}
              loading={loading}
              error={error}
            />
          )}

          {activeTab === 'browse' && (
            <div className="text-center space-y-4 py-8">
              <h3 className="text-2xl font-bold">Product Catalog</h3>
              <p className="text-muted-foreground">
                {loading ? 'Loading products...' : `Browse through our collection of ${results.length} products`}
              </p>
            </div>
          )}
        </div>

        {/* Filter Section - Only show for search results with similarity scores */}
        {hasSearchResults && searchInitiated && !loading && (
          <div className="max-w-6xl mx-auto mb-8">
            <FilterSection
              minSimilarity={minSimilarity}
              setMinSimilarity={setMinSimilarity}
              onFilter={handleFilter}
              onReset={handleFilterReset}
              loading={false}
              totalResults={allResults.length}
              filteredResults={results.length}
            />
          </div>
        )}

        {/* Results Section */}
        <div className="max-w-7xl mx-auto pb-16">
          <ResultsSection
            results={results}
            loading={loading && searchInitiated}
            activeTab={activeTab}
          />
        </div>
      </div>
    </div>
  );
}
