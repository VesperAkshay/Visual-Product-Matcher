'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Button } from './ui/button';
import { ArrowDown, Search, Upload, Link, Grid3X3 } from 'lucide-react';

export function HeroSection({ onScrollToUpload }) {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16 pb-8">
      {/* Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute top-1/4 right-1/4 w-72 h-72 lg:w-96 lg:h-96 rounded-full opacity-10"
          style={{
            background: 'radial-gradient(circle, #6366f1 0%, transparent 70%)'
          }}
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.1, 0.15, 0.1]
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        <motion.div
          className="absolute bottom-1/4 left-1/4 w-72 h-72 lg:w-96 lg:h-96 rounded-full opacity-10"
          style={{
            background: 'radial-gradient(circle, #8b5cf6 0%, transparent 70%)'
          }}
          animate={{
            scale: [1.2, 1, 1.2],
            opacity: [0.1, 0.15, 0.1]
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      </div>

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* Left Content */}
          <div className="space-y-6 lg:space-y-8 text-center lg:text-left">
            {/* Badge */}
            <motion.div
              className="inline-flex items-center gap-2 glass px-4 py-2 rounded-full text-sm"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2, ease: "easeOut" }}
            >
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
              <span className="text-muted-foreground">AI-Powered • Real-time • Accurate</span>
            </motion.div>

            {/* Main Heading */}
            <motion.div
              className="space-y-4"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.3, ease: "easeOut" }}
            >
              <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-medium leading-tight">
                <span className="text-foreground">Visual </span>
                <span className="gradient-text">Product</span>
                <br />
                <span className="text-foreground">AI </span>
                <span className="gradient-text">Search</span>
                <br />
                <span className="text-foreground">Made </span>
                <span className="gradient-text">Simple</span>
              </h1>
            </motion.div>

            {/* Description */}
            <motion.p
              className="text-lg lg:text-xl text-muted-foreground leading-relaxed max-w-lg mx-auto lg:mx-0"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.6, ease: "easeOut" }}
            >
              Discover similar products using cutting-edge CLIP AI model with lightning-fast vector similarity search.
            </motion.p>

            {/* CTA Buttons */}
            <motion.div
              className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.8, ease: "easeOut" }}
            >
              <Button
                size="lg"
                onClick={onScrollToUpload}
                className="gradient-primary hover:shadow-xl hover:shadow-blue-500/25 transition-all duration-300 text-base px-8 py-4 h-auto"
              >
                Start Searching
                <ArrowDown className="ml-2 h-5 w-5" />
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="glass border-white/20 hover:bg-white/10 transition-all duration-300 text-base px-8 py-4 h-auto"
              >
                <Search className="mr-2 h-5 w-5" />
                View Demo
              </Button>
            </motion.div>

            {/* Stats */}
            <motion.div
              className="flex items-center justify-center lg:justify-start gap-6 lg:gap-8 pt-6 lg:pt-8"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 1, ease: "easeOut" }}
            >
              <div className="text-center">
                <div className="text-xl lg:text-2xl font-medium gradient-text">CLIP</div>
                <div className="text-xs lg:text-sm text-muted-foreground">AI Model</div>
              </div>
              <div className="text-center">
                <div className="text-xl lg:text-2xl font-medium gradient-text">512D</div>
                <div className="text-xs lg:text-sm text-muted-foreground">Embeddings</div>
              </div>
              <div className="text-center">
                <div className="text-xl lg:text-2xl font-medium gradient-text">100+</div>
                <div className="text-xs lg:text-sm text-muted-foreground">Products</div>
              </div>
            </motion.div>
          </div>

          {/* Right Content - Feature Showcase */}
          <motion.div
            className="relative hidden lg:block"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.4, ease: "easeOut" }}
          >
            <div className="relative">
              {/* Main showcase card */}
              <motion.div
                className="glass-card p-6 lg:p-8 rounded-2xl shadow-2xl"
                animate={{ y: [-10, 10, -10] }}
                transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
              >
                <div className="space-y-6">
                  <div className="text-center">
                    <Search className="h-14 w-14 lg:h-16 lg:w-16 mx-auto text-blue-400 mb-4" />
                    <h3 className="text-lg lg:text-xl font-semibold mb-2">Three Ways to Search</h3>
                  </div>
                  
                  <div className="space-y-4">
                    <motion.div 
                      className="flex items-center gap-3 p-3 rounded-lg glass transition-all duration-300 hover:bg-white/15"
                      whileHover={{ x: 5 }}
                      transition={{ duration: 0.2 }}
                    >
                      <Upload className="h-5 w-5 text-blue-400 flex-shrink-0" />
                      <span className="text-sm">Upload Image File</span>
                    </motion.div>
                    
                    <motion.div 
                      className="flex items-center gap-3 p-3 rounded-lg glass transition-all duration-300 hover:bg-white/15"
                      whileHover={{ x: 5 }}
                      transition={{ duration: 0.2 }}
                    >
                      <Link className="h-5 w-5 text-purple-400 flex-shrink-0" />
                      <span className="text-sm">Use Image URL</span>
                    </motion.div>
                    
                    <motion.div 
                      className="flex items-center gap-3 p-3 rounded-lg glass transition-all duration-300 hover:bg-white/15"
                      whileHover={{ x: 5 }}
                      transition={{ duration: 0.2 }}
                    >
                      <Grid3X3 className="h-5 w-5 text-green-400 flex-shrink-0" />
                      <span className="text-sm">Browse Catalog</span>
                    </motion.div>
                  </div>
                </div>
              </motion.div>

              {/* Floating elements */}
              <motion.div
                className="absolute -top-4 -right-4 glass px-3 py-2 rounded-lg text-sm backdrop-blur-sm"
                animate={{ y: [-5, 5, -5] }}
                transition={{ duration: 4, repeat: Infinity, ease: "easeInOut", delay: 1 }}
              >
                <span className="gradient-text font-medium">AI Processing</span>
              </motion.div>

              <motion.div
                className="absolute -bottom-4 -left-4 glass px-3 py-2 rounded-lg text-sm backdrop-blur-sm"
                animate={{ y: [5, -5, 5] }}
                transition={{ duration: 5, repeat: Infinity, ease: "easeInOut", delay: 2 }}
              >
                <span className="text-green-400 font-medium">✓ Ready to Search</span>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <motion.div
        className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.5, ease: "easeOut" }}
      >
        <motion.div
          animate={{ y: [0, 8, 0] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
          className="cursor-pointer p-2 rounded-full glass hover:bg-white/20 transition-all duration-300"
          onClick={onScrollToUpload}
        >
          <ArrowDown className="h-6 w-6 text-muted-foreground" />
        </motion.div>
      </motion.div>
    </section>
  );
}
