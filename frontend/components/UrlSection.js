'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Link, Search, Loader2, ExternalLink } from 'lucide-react';

export function UrlSection({ imageUrl, setImageUrl, onSearch, loading, error }) {
  const [previewError, setPreviewError] = useState(false);

  const handleUrlChange = (e) => {
    setImageUrl(e.target.value);
    setPreviewError(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && imageUrl.trim() && !loading) {
      onSearch();
    }
  };

  return (
    <motion.div
      className="space-y-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <Card className="glass-card border-white/10">
        <CardContent className="p-8">
          <div className="space-y-6">
            <div className="text-center">
              <Link className="h-16 w-16 text-purple-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Search by Image URL</h3>
              <p className="text-muted-foreground">
                Paste a direct link to an image from the web
              </p>
            </div>

            <div className="space-y-4">
              <div className="relative">
                <input
                  type="url"
                  className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-400/20 transition-all duration-300 pr-12"
                  placeholder="https://example.com/image.jpg"
                  value={imageUrl}
                  onChange={handleUrlChange}
                  onKeyPress={handleKeyPress}
                />
                <ExternalLink className="absolute right-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
              </div>

              <div className="flex justify-center">
                <Button
                  size="lg"
                  onClick={onSearch}
                  disabled={loading || !imageUrl.trim()}
                  className="gradient-primary hover:shadow-xl hover:shadow-purple-500/25 transition-all duration-300 px-8 py-4 h-auto text-base"
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      Fetching Image...
                    </>
                  ) : (
                    <>
                      <Search className="mr-2 h-5 w-5" />
                      Search Similar Products
                    </>
                  )}
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {imageUrl && !previewError && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
        >
          <Card className="glass-card border-white/10">
            <CardContent className="p-6">
              <div className="text-center space-y-4">
                <h4 className="font-medium text-sm text-muted-foreground">Image Preview</h4>
                <div className="relative inline-block">
                  <img 
                    src={imageUrl} 
                    alt="URL Preview"
                    className="max-w-md max-h-64 rounded-lg shadow-lg mx-auto"
                    onError={() => setPreviewError(true)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {previewError && imageUrl && (
        <motion.div
          className="glass border border-yellow-500/20 bg-yellow-500/10 p-4 rounded-lg"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
        >
          <div className="flex items-center gap-2 text-yellow-400">
            <span>⚠️</span>
            <span>Cannot preview this image URL. You can still search with it.</span>
          </div>
        </motion.div>
      )}

      {error && (
        <motion.div
          className="glass border border-red-500/20 bg-red-500/10 p-4 rounded-lg"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
        >
          <div className="flex items-center gap-2 text-red-400">
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
