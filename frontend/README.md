# ⚛️ Visual Product Matcher - Frontend

> **Modern Next.js Application for AI-Powered Visual Search**

A sophisticated React frontend that provides an intuitive interface for visual product similarity search. Built with Next.js 14, featuring drag-and-drop uploads, real-time search, and responsive design.

## ✨ Features

🎨 **Modern UI/UX** - Clean, intuitive design with Tailwind CSS  
📱 **Responsive Design** - Perfect experience on all devices  
🖼️ **Drag & Drop Upload** - Easy image upload with visual feedback  
🔗 **URL Search** - Search using product image URLs  
⚡ **Real-time Results** - Instant similarity search results  
🎯 **Smart Filtering** - Filter by category, price, and more  
🔄 **Tab Navigation** - Organized interface with multiple search modes  
📊 **Results Grid** - Beautiful product gallery with similarity scores  

## 🏗️ Architecture

```
Next.js Application (App Router)
├── 🎨 UI Components
│   ├── Upload Section (Drag & Drop)
│   ├── URL Search Section
│   ├── Filter Section
│   ├── Results Grid
│   └── Tab Navigation
├── 📡 API Integration
│   ├── Backend Communication
│   ├── Error Handling
│   └── Loading States
├── 🎭 State Management
│   ├── Search State
│   ├── Upload State
│   └── Filter State
└── 🎨 Styling
    ├── Tailwind CSS
    ├── Custom Components
    └── Responsive Design
```

## 🚀 Quick Start

### **1. Install Dependencies**
```bash
npm install
```

### **2. Start Development Server**
```bash
npm run dev
```

### **3. Access Application**
- **Development**: http://localhost:3000
- **Backend API**: http://localhost:5000

### **4. Build for Production**
```bash
npm run build
npm start
```

## 📁 Project Structure

```
frontend/
├── 📄 package.json              # Dependencies and scripts
├── 📄 next.config.mjs           # Next.js configuration
├── 📄 tailwind.config.js        # Tailwind CSS configuration
├── 📄 postcss.config.js         # PostCSS configuration
├── 📄 jsconfig.json             # JavaScript configuration
├── 📁 app/                      # Next.js App Router
│   ├── 📄 layout.js            # Root layout component
│   ├── 📄 page.js              # Home page component
│   ├── 📄 globals.css          # Global styles
│   ├── 📄 page.css             # Page-specific styles
│   └── 📄 favicon.ico          # App icon
├── 📁 components/               # React components
│   ├── 📄 HeroSection.js       # Hero/banner section
│   ├── 📄 UploadSection.js     # Image upload interface
│   ├── 📄 UrlSection.js        # URL search interface
│   ├── 📄 FilterSection.js     # Search filters
│   ├── 📄 ResultsSection.js    # Search results display
│   ├── 📄 TabNavigation.js     # Tab switching component
│   └── 📁 ui/                  # Reusable UI components
├── 📁 lib/                      # Utility libraries
│   └── 📄 utils.js             # Helper functions
└── 📁 public/                   # Static assets
    ├── 📄 next.svg             # Next.js logo
    ├── 📄 vercel.svg           # Vercel logo
    └── 📄 *.svg                # Various icons
```

## 🎨 Component Architecture

### **Core Components**

#### **HeroSection.js**
```javascript
// Main banner and introduction
const HeroSection = () => {
  return (
    <section className="hero-gradient text-white py-20">
      <div className="container mx-auto text-center">
        <h1>AI-Powered Visual Product Search</h1>
        <p>Find similar products using advanced AI technology</p>
      </div>
    </section>
  );
};
```

#### **UploadSection.js**  
```javascript
// Drag & drop image upload
const UploadSection = ({ onUpload, isLoading }) => {
  const handleDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) onUpload(file);
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: handleDrop,
    accept: { 'image/*': [] },
    maxSize: 16 * 1024 * 1024 // 16MB
  });

  return (
    <div {...getRootProps()} className="upload-dropzone">
      <input {...getInputProps()} />
      {isDragActive ? 'Drop image here' : 'Drag & drop or click to upload'}
    </div>
  );
};
```

#### **UrlSection.js**
```javascript
// URL-based image search  
const UrlSection = ({ onSearch, isLoading }) => {
  const [url, setUrl] = useState('');
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (url.trim()) onSearch(url.trim());
  };

  return (
    <form onSubmit={handleSubmit} className="url-search-form">
      <input 
        type="url"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="Enter image URL..."
        className="url-input"
      />
      <button type="submit" disabled={isLoading}>
        Search Similar Products
      </button>
    </form>
  );
};
```

#### **ResultsSection.js**
```javascript
// Display search results grid
const ResultsSection = ({ results, isLoading, error }) => {
  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  if (!results.length) return <EmptyState />;

  return (
    <div className="results-grid">
      {results.map((product) => (
        <ProductCard 
          key={product.id}
          product={product}
          showSimilarity={true}
        />
      ))}
    </div>
  );
};
```

### **Utility Components**

#### **TabNavigation.js**
```javascript
// Tab switching interface
const TabNavigation = ({ activeTab, onTabChange }) => {
  const tabs = [
    { id: 'upload', label: 'Upload Image', icon: '📤' },
    { id: 'url', label: 'Search by URL', icon: '🔗' },
    { id: 'browse', label: 'Browse Products', icon: '👁️' }
  ];

  return (
    <div className="tab-navigation">
      {tabs.map(tab => (
        <button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
          className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
        >
          <span className="tab-icon">{tab.icon}</span>
          {tab.label}
        </button>
      ))}
    </div>
  );
};
```

#### **FilterSection.js**
```javascript
// Search filters and options
const FilterSection = ({ filters, onFilterChange }) => {
  return (
    <div className="filter-section">
      <div className="filter-group">
        <label>Category</label>
        <select 
          value={filters.category}
          onChange={(e) => onFilterChange('category', e.target.value)}
        >
          <option value="">All Categories</option>
          <option value="electronics">Electronics</option>
          <option value="clothing">Clothing</option>
          <option value="home">Home & Garden</option>
        </select>
      </div>
      
      <div className="filter-group">
        <label>Similarity Threshold</label>
        <input
          type="range"
          min="0.5"
          max="1.0"
          step="0.1"
          value={filters.threshold}
          onChange={(e) => onFilterChange('threshold', e.target.value)}
        />
      </div>
    </div>
  );
};
```

## 🎨 Styling & Design

### **Tailwind CSS Configuration**
```javascript
// tailwind.config.js
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 2s infinite',
      }
    },
  },
  plugins: [],
}
```

### **Custom CSS Components**
```css
/* globals.css - Custom component styles */

.hero-gradient {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.upload-dropzone {
  @apply border-2 border-dashed border-gray-300 rounded-lg p-8 text-center
         hover:border-primary-500 transition-colors cursor-pointer
         bg-gray-50 hover:bg-gray-100;
}

.upload-dropzone.drag-active {
  @apply border-primary-500 bg-primary-50;
}

.results-grid {
  @apply grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 
         gap-6 mt-8;
}

.product-card {
  @apply bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow
         overflow-hidden border border-gray-200;
}

.similarity-badge {
  @apply absolute top-2 right-2 bg-primary-500 text-white px-2 py-1 
         rounded-full text-xs font-semibold;
}
```

## 📡 API Integration

### **Backend Communication**
```javascript
// lib/api.js - API service functions
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export const api = {
  // Upload image search
  async uploadImageSearch(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE_URL}/api/search/upload`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
    }
    
    return response.json();
  },

  // URL image search
  async urlImageSearch(url, options = {}) {
    const response = await fetch(`${API_BASE_URL}/api/search/url`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        url, 
        top_k: options.limit || 10,
        threshold: options.threshold || 0.7
      }),
    });
    
    if (!response.ok) {
      throw new Error(`Search failed: ${response.statusText}`);
    }
    
    return response.json();
  },

  // Get all products
  async getProducts(filters = {}) {
    const params = new URLSearchParams();
    if (filters.category) params.set('category', filters.category);
    if (filters.limit) params.set('limit', filters.limit);
    if (filters.offset) params.set('offset', filters.offset);
    
    const response = await fetch(`${API_BASE_URL}/api/products?${params}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch products: ${response.statusText}`);
    }
    
    return response.json();
  },

  // Health check
  async healthCheck() {
    const response = await fetch(`${API_BASE_URL}/api/health`);
    return response.ok;
  }
};
```

### **Error Handling**
```javascript
// Custom error handling hook
const useErrorHandler = () => {
  const [error, setError] = useState(null);
  
  const handleError = useCallback((error) => {
    console.error('Application error:', error);
    
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      setError('Unable to connect to server. Please check your connection.');
    } else if (error.message.includes('413')) {
      setError('File too large. Please choose a smaller image.');
    } else if (error.message.includes('415')) {
      setError('Unsupported file type. Please upload a valid image.');
    } else {
      setError(error.message || 'An unexpected error occurred.');
    }
  }, []);
  
  const clearError = useCallback(() => setError(null), []);
  
  return { error, handleError, clearError };
};
```

## 🔧 State Management

### **Search State Hook**
```javascript
// hooks/useSearch.js - Custom search state management
const useSearch = () => {
  const [state, setState] = useState({
    results: [],
    isLoading: false,
    error: null,
    searchType: null, // 'upload' | 'url' | 'browse'
    filters: {
      category: '',
      threshold: 0.7,
      limit: 20
    }
  });

  const searchByUpload = useCallback(async (file) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const response = await api.uploadImageSearch(file);
      setState(prev => ({
        ...prev,
        results: response.data.similar_products,
        isLoading: false,
        searchType: 'upload'
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error.message,
        isLoading: false
      }));
    }
  }, []);

  const searchByUrl = useCallback(async (url) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const response = await api.urlImageSearch(url, state.filters);
      setState(prev => ({
        ...prev,
        results: response.data.similar_products,
        isLoading: false,
        searchType: 'url'
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error.message,
        isLoading: false
      }));
    }
  }, [state.filters]);

  const updateFilters = useCallback((newFilters) => {
    setState(prev => ({
      ...prev,
      filters: { ...prev.filters, ...newFilters }
    }));
  }, []);

  return {
    ...state,
    searchByUpload,
    searchByUrl,
    updateFilters,
    clearResults: () => setState(prev => ({ ...prev, results: [], error: null }))
  };
};
```

### **Upload State Hook**
```javascript
// hooks/useUpload.js - File upload state management
const useUpload = () => {
  const [uploadState, setUploadState] = useState({
    isDragging: false,
    uploadProgress: 0,
    uploadedFile: null,
    previewUrl: null
  });

  const handleDragEnter = useCallback(() => {
    setUploadState(prev => ({ ...prev, isDragging: true }));
  }, []);

  const handleDragLeave = useCallback(() => {
    setUploadState(prev => ({ ...prev, isDragging: false }));
  }, []);

  const handleFileSelect = useCallback((file) => {
    if (file) {
      const previewUrl = URL.createObjectURL(file);
      setUploadState(prev => ({
        ...prev,
        uploadedFile: file,
        previewUrl,
        isDragging: false
      }));
    }
  }, []);

  const clearUpload = useCallback(() => {
    if (uploadState.previewUrl) {
      URL.revokeObjectURL(uploadState.previewUrl);
    }
    setUploadState({
      isDragging: false,
      uploadProgress: 0,
      uploadedFile: null,
      previewUrl: null
    });
  }, [uploadState.previewUrl]);

  return {
    ...uploadState,
    handleDragEnter,
    handleDragLeave,
    handleFileSelect,
    clearUpload
  };
};
```

## 🧪 Testing

### **Component Testing**
```javascript
// __tests__/components/UploadSection.test.js
import { render, screen, fireEvent } from '@testing-library/react';
import UploadSection from '@/components/UploadSection';

describe('UploadSection', () => {
  const mockOnUpload = jest.fn();

  beforeEach(() => {
    mockOnUpload.mockClear();
  });

  test('renders upload dropzone', () => {
    render(<UploadSection onUpload={mockOnUpload} />);
    expect(screen.getByText(/drag & drop/i)).toBeInTheDocument();
  });

  test('handles file selection', () => {
    render(<UploadSection onUpload={mockOnUpload} />);
    
    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
    const input = screen.getByRole('button');
    
    fireEvent.change(input, { target: { files: [file] } });
    expect(mockOnUpload).toHaveBeenCalledWith(file);
  });

  test('shows loading state', () => {
    render(<UploadSection onUpload={mockOnUpload} isLoading={true} />);
    expect(screen.getByText(/uploading/i)).toBeInTheDocument();
  });
});
```

### **API Testing**
```javascript
// __tests__/lib/api.test.js
import { api } from '@/lib/api';

// Mock fetch globally
global.fetch = jest.fn();

describe('API Service', () => {
  afterEach(() => {
    fetch.mockClear();
  });

  test('uploadImageSearch sends FormData', async () => {
    const mockResponse = { data: { similar_products: [] } };
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
    const result = await api.uploadImageSearch(file);

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/search/upload'),
      expect.objectContaining({
        method: 'POST',
        body: expect.any(FormData),
      })
    );
    expect(result).toEqual(mockResponse);
  });

  test('handles API errors properly', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      statusText: 'Internal Server Error',
    });

    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
    
    await expect(api.uploadImageSearch(file))
      .rejects
      .toThrow('Upload failed: Internal Server Error');
  });
});
```

### **Running Tests**
```bash
# Install testing dependencies
npm install --save-dev jest @testing-library/react @testing-library/jest-dom

# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

## 🔧 Configuration

### **Environment Variables**
```bash
# .env.local - Local development configuration
NEXT_PUBLIC_API_URL=http://localhost:5000
NEXT_PUBLIC_APP_NAME="Visual Product Matcher"
NEXT_PUBLIC_MAX_FILE_SIZE=16777216
NEXT_PUBLIC_SUPPORTED_FORMATS="image/jpeg,image/png,image/webp"
```

### **Next.js Configuration**
```javascript
// next.config.mjs
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost', 'example.com'],
    formats: ['image/webp', 'image/avif'],
  },
  
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`,
      },
    ];
  },

  experimental: {
    optimizeCss: true,
  },
};

export default nextConfig;
```

## 🚀 Deployment

### **Build for Production**
```bash
# Build optimized production bundle
npm run build

# Start production server
npm start

# Analyze bundle size
npm run analyze
```

### **Deployment Platforms**

#### **Vercel (Recommended)**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy to Vercel
vercel --prod
```

#### **Netlify**
```bash
# Build command
npm run build

# Publish directory
out/
```

#### **Static Export**
```bash
# Add to next.config.mjs
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  }
};

# Build static files
npm run build
```

### **Environment Configuration**
```bash
# Production environment variables
NEXT_PUBLIC_API_URL=https://your-api-domain.com
NEXT_PUBLIC_APP_NAME="Visual Product Matcher"

# Vercel environment variables
vercel env add NEXT_PUBLIC_API_URL
```

## 📊 Performance Optimization

### **Image Optimization**
```javascript
// components/ProductCard.js - Optimized image loading
import Image from 'next/image';

const ProductCard = ({ product }) => {
  return (
    <div className="product-card">
      <Image
        src={product.image_url}
        alt={product.name}
        width={300}
        height={300}
        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
        priority={false}
        placeholder="blur"
        blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
      />
    </div>
  );
};
```

### **Code Splitting**
```javascript
// Dynamic imports for better performance
import dynamic from 'next/dynamic';

const FilterSection = dynamic(() => import('@/components/FilterSection'), {
  loading: () => <FilterSkeleton />,
});

const ResultsSection = dynamic(() => import('@/components/ResultsSection'), {
  ssr: false,
});
```

### **Bundle Analysis**
```bash
# Install bundle analyzer
npm install --save-dev @next/bundle-analyzer

# Analyze bundle
npm run analyze
```

## 🚨 Troubleshooting

### **Common Issues**

#### **Build Errors**
```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Check Node.js version
node --version  # Should be 18+
```

#### **API Connection Issues**
```bash
# Check API URL configuration
echo $NEXT_PUBLIC_API_URL

# Test API connection
curl http://localhost:5000/api/health

# Check CORS configuration
curl -H "Origin: http://localhost:3000" http://localhost:5000/api/health
```

#### **Styling Issues**
```bash
# Rebuild Tailwind CSS
npm run dev

# Check PostCSS configuration
cat postcss.config.js

# Clear browser cache
# Hard refresh: Ctrl+Shift+R (Windows) / Cmd+Shift+R (Mac)
```

#### **Performance Issues**
```bash
# Check bundle size
npm run build

# Analyze performance
npm run analyze

# Monitor memory usage
# Chrome DevTools > Performance tab
```

## 📚 Additional Resources

- **⚛️ Next.js**: [Framework Documentation](https://nextjs.org/docs)
- **🎨 Tailwind CSS**: [Styling Documentation](https://tailwindcss.com/docs)
- **🧪 Testing**: [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- **📱 React**: [Component Documentation](https://react.dev/)

---

**Built with ⚛️ for modern web experiences**
