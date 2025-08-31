'use client';

import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Upload, X, Search, Loader2 } from 'lucide-react';

export function UploadSection({ selectedFile, setSelectedFile, onSearch, loading, error }) {
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setDragActive(false);
    const file = event.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedFile(file);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const handleDragEnter = (event) => {
    event.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    setDragActive(false);
  };

  const removeFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
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
          <div
            className={`relative border-2 border-dashed rounded-xl p-8 transition-all duration-300 cursor-pointer ${
              dragActive 
                ? 'border-blue-400 bg-blue-400/10' 
                : selectedFile 
                  ? 'border-green-400 bg-green-400/10' 
                  : 'border-white/20 hover:border-white/40'
            }`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragEnter={handleDragEnter}
            onDragLeave={handleDragLeave}
            onClick={() => !selectedFile && fileInputRef.current?.click()}
          >
            {!selectedFile ? (
              <motion.div
                className="text-center space-y-4"
                initial={{ scale: 0.9 }}
                animate={{ scale: 1 }}
                transition={{ duration: 0.3 }}
              >
                <motion.div
                  animate={{ y: dragActive ? -10 : 0 }}
                  transition={{ duration: 0.2 }}
                  className="mx-auto"
                >
                  <Upload className="h-16 w-16 text-blue-400 mx-auto mb-4" />
                </motion.div>
                
                <div>
                  <h3 className="text-xl font-semibold mb-2">
                    {dragActive ? 'Drop your image here' : 'Upload Product Image'}
                  </h3>
                  <p className="text-muted-foreground mb-4">
                    Drag and drop an image file or click to browse
                  </p>
                  <div className="inline-flex items-center gap-2 text-sm text-muted-foreground bg-white/5 px-3 py-1 rounded-full">
                    <span>Supports JPG, PNG, GIF, WebP (max 16MB)</span>
                  </div>
                </div>
              </motion.div>
            ) : (
              <motion.div
                className="space-y-4"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3 }}
              >
                <div className="relative">
                  <img 
                    src={URL.createObjectURL(selectedFile)} 
                    alt="Preview"
                    className="w-full max-w-md mx-auto rounded-lg shadow-lg"
                  />
                  <Button
                    variant="destructive"
                    size="icon"
                    className="absolute top-2 right-2"
                    onClick={(e) => {
                      e.stopPropagation();
                      removeFile();
                    }}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
                
                <div className="text-center space-y-2">
                  <p className="font-medium">{selectedFile.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </motion.div>
            )}
            
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              accept="image/*"
              onChange={handleFileSelect}
            />
          </div>
        </CardContent>
      </Card>

      {selectedFile && (
        <motion.div
          className="flex justify-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          <Button
            size="lg"
            onClick={onSearch}
            disabled={loading}
            className="gradient-primary hover:shadow-xl hover:shadow-blue-500/25 transition-all duration-300 px-8 py-4 h-auto text-base"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                Analyzing Image...
              </>
            ) : (
              <>
                <Search className="mr-2 h-5 w-5" />
                Find Similar Products
              </>
            )}
          </Button>
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
