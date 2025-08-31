'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent } from './ui/card';
import { Slider } from './ui/slider';
import { Filter, RefreshCw } from 'lucide-react';

export function FilterSection({ 
  minSimilarity, 
  setMinSimilarity, 
  onFilter, 
  onReset, 
  loading,
  totalResults,
  filteredResults 
}) {
  const quickFilters = [
    { label: 'Any', value: 0.0 },
    { label: '50%+', value: 0.5 },
    { label: '70%+', value: 0.7 },
    { label: '90%+', value: 0.9 }
  ];

  const handleQuickFilter = (value) => {
    setMinSimilarity(value);
    // Auto-apply the filter
    setTimeout(onFilter, 100);
  };

  return (
    <motion.div
      className="mb-8"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
    >
      <Card className="glass-card border-white/10">
        <CardContent className="p-4 lg:p-6">
          <div className="flex flex-col xl:flex-row items-start xl:items-center gap-6">
            {/* Filter Icon and Title */}
            <div className="flex items-center gap-3 min-w-0">
              <Filter className="h-5 w-5 text-blue-400 flex-shrink-0" />
              <h3 className="font-semibold text-white text-lg">Similarity Filter</h3>
            </div>

            {/* Similarity Slider */}
            <div className="flex-1 space-y-4 w-full xl:w-auto">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Minimum Similarity</span>
                <span className="font-mono text-blue-400 text-base font-semibold">
                  {(minSimilarity * 100).toFixed(1)}%
                </span>
              </div>
              
              {/* Quick Filter Buttons */}
              <div className="flex flex-wrap gap-2 mb-3">
                {quickFilters.map((filter) => (
                  <motion.button
                    key={filter.label}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleQuickFilter(filter.value)}
                    className={`px-3 py-1.5 text-sm rounded-full font-medium transition-all duration-200 ${
                      Math.abs(minSimilarity - filter.value) < 0.01
                        ? 'bg-blue-600 text-white shadow-lg'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600 hover:text-white'
                    }`}
                  >
                    {filter.label}
                  </motion.button>
                ))}
              </div>
              
              <Slider
                value={[minSimilarity]}
                onValueChange={(value) => setMinSimilarity(value[0])}
                min={0}
                max={1}
                step={0.01}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>0%</span>
                <span>50%</span>
                <span>100%</span>
              </div>
            </div>

            {/* Results Count */}
            {totalResults > 0 && (
              <div className="text-sm text-muted-foreground min-w-0 xl:text-center">
                <div className="font-semibold text-white text-lg">{filteredResults}</div>
                <div>of {totalResults} results</div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-3 w-full xl:w-auto">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={onFilter}
                disabled={loading}
                className="flex-1 xl:flex-none px-6 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-all duration-200 text-sm shadow-lg hover:shadow-xl"
              >
                {loading ? (
                  <div className="flex items-center justify-center gap-2">
                    <RefreshCw className="h-4 w-4 animate-spin" />
                    Filtering...
                  </div>
                ) : (
                  'Apply Filter'
                )}
              </motion.button>
              
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={onReset}
                className="flex-1 xl:flex-none px-6 py-2.5 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-medium transition-all duration-200 text-sm shadow-lg hover:shadow-xl"
              >
                Reset
              </motion.button>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
