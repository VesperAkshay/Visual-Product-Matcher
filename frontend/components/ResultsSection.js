'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent } from './ui/card';
import { Star, ExternalLink } from 'lucide-react';

export function ResultsSection({ results, loading, activeTab }) {
  if (!results.length && !loading) return null;

  return (
    <motion.div
      className="space-y-8 mt-8"
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
    >
      <div className="text-center space-y-3">
        <motion.h2 
          className="text-3xl lg:text-4xl font-bold"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          {activeTab === 'browse' ? 'Product Catalog' : 'Similar Products Found'}
        </motion.h2>
        {results.length > 0 && (
          <motion.p 
            className="text-muted-foreground text-lg"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            Showing {results.length} {results.length === 1 ? 'result' : 'results'}
          </motion.p>
        )}
      </div>

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 lg:gap-8">
          {[...Array(8)].map((_, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: i * 0.05, ease: "easeOut" }}
            >
              <Card className="glass-card border-white/10 overflow-hidden">
                <div className="skeleton skeleton-image h-48 lg:h-56" />
                <CardContent className="p-4 lg:p-6 space-y-3">
                  <div className="skeleton skeleton-text h-4" />
                  <div className="skeleton skeleton-text short h-3" />
                  <div className="skeleton skeleton-text h-3" />
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 lg:gap-8">
          {results.map((product, index) => (
            <motion.div
              key={product.id || index}
              initial={{ opacity: 0, y: 30, scale: 0.9 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ 
                duration: 0.5, 
                delay: index * 0.05, 
                ease: "easeOut"
              }}
              whileHover={{ y: -8, transition: { duration: 0.2 } }}
              className="group"
            >
              <Card className="glass-card border-white/10 overflow-hidden hover:border-white/30 transition-all duration-300 h-full shadow-lg hover:shadow-2xl">
                <div className="relative overflow-hidden">
                  <img 
                    src={product.image_url?.startsWith('/') 
                      ? `http://localhost:5001${product.image_url}` 
                      : product.image_url
                    } 
                    alt={product.name}
                    className="w-full h-48 lg:h-56 object-cover group-hover:scale-110 transition-transform duration-500 ease-out"
                    onError={(e) => {
                      e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjRjVGNUY1Ii8+CjxwYXRoIGQ9Ik04NyA3NEg2M1Y5OEg4N1Y3NFoiIGZpbGw9IiNDQ0NDQ0MiLz4KPHA+CjwvcGF0aD4KPC9zdmc+';
                    }}
                  />
                  
                  {/* Similarity Badge */}
                  {(product.similarity || product.similarity_score) && (
                    <motion.div 
                      className="absolute top-3 right-3"
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ duration: 0.3, delay: index * 0.05 + 0.2 }}
                    >
                      <div className="glass px-3 py-1.5 rounded-full text-xs font-semibold border border-white/20 backdrop-blur-sm">
                        <span className="text-green-400">
                          {((product.similarity || product.similarity_score) * 100).toFixed(1)}% match
                        </span>
                      </div>
                    </motion.div>
                  )}
                  
                  {/* Hover Overlay */}
                  <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
                    <motion.div
                      initial={{ scale: 0.8, opacity: 0 }}
                      whileHover={{ scale: 1, opacity: 1 }}
                      className="glass px-4 py-2 rounded-lg text-sm font-medium backdrop-blur-sm"
                    >
                      <ExternalLink className="h-4 w-4 inline mr-2" />
                      View Details
                    </motion.div>
                  </div>
                </div>

                <CardContent className="p-4 lg:p-6 space-y-3">
                  {product.category && (
                    <motion.div 
                      className="text-xs text-blue-400 font-medium uppercase tracking-wider"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ duration: 0.3, delay: index * 0.05 + 0.3 }}
                    >
                      {product.category}
                    </motion.div>
                  )}
                  
                  <motion.h3 
                    className="font-semibold text-sm lg:text-base line-clamp-2 group-hover:text-blue-400 transition-colors duration-300"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.3, delay: index * 0.05 + 0.4 }}
                  >
                    {product.name}
                  </motion.h3>
                  
                  {/* Show similarity score in card content for search results */}
                  {(product.similarity || product.similarity_score) && (
                    <motion.div 
                      className="flex items-center gap-2"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.05 + 0.5 }}
                    >
                      <div className="text-xs px-2 py-1 bg-green-500/20 text-green-400 rounded-full font-medium">
                        {((product.similarity || product.similarity_score) * 100).toFixed(1)}% similar
                      </div>
                    </motion.div>
                  )}
                  
                  <motion.div 
                    className="flex items-center justify-between pt-2"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.3, delay: index * 0.05 + 0.6 }}
                  >
                    <span className="text-lg lg:text-xl font-bold text-green-400">
                      ${product.price}
                    </span>
                    
                    {product.rating && (
                      <div className="flex items-center gap-1">
                        <Star className="h-4 w-4 text-yellow-400 fill-current" />
                        <span className="text-sm text-muted-foreground">
                          {product.rating}
                        </span>
                      </div>
                    )}
                  </motion.div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      )}
    </motion.div>
  );
}
