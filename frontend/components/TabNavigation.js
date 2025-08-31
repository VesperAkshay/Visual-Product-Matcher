'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Upload, Link, Grid3X3 } from 'lucide-react';

export function TabNavigation({ activeTab, setActiveTab, onReset, onBrowseProducts }) {
  const tabs = [
    {
      id: 'upload',
      label: 'Upload Image',
      icon: Upload,
      description: 'Upload from device'
    },
    {
      id: 'url',
      label: 'Image URL',
      icon: Link,
      description: 'Use web image'
    },
    {
      id: 'browse',
      label: 'Browse All',
      icon: Grid3X3,
      description: 'View catalog'
    }
  ];

  const handleTabClick = (tabId) => {
    setActiveTab(tabId);
    
    if (tabId === 'browse') {
      onBrowseProducts();
    } else {
      onReset();
    }
  };

  return (
    <motion.div
      className="flex justify-center mb-12"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.2 }}
    >
      <div className="glass border border-white/20 rounded-xl p-1 inline-flex">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          
          return (
            <motion.button
              key={tab.id}
              onClick={() => handleTabClick(tab.id)}
              className={`relative px-6 py-3 rounded-lg transition-all duration-300 flex items-center gap-3 ${
                isActive 
                  ? 'text-white' 
                  : 'text-muted-foreground hover:text-white'
              }`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {isActive && (
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg"
                  layoutId="activeTab"
                  transition={{ type: "spring", duration: 0.6 }}
                />
              )}
              
              <div className="relative flex items-center gap-3">
                <Icon className="h-5 w-5" />
                <div className="text-left hidden sm:block">
                  <div className="text-sm font-medium">{tab.label}</div>
                  <div className="text-xs opacity-75">{tab.description}</div>
                </div>
                <div className="text-sm font-medium sm:hidden">{tab.label}</div>
              </div>
            </motion.button>
          );
        })}
      </div>
    </motion.div>
  );
}
