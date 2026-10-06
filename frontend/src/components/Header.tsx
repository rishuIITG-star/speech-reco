import React from 'react';
import { motion } from 'framer-motion';
import { User, Play } from 'lucide-react';

interface HeaderProps {
  stage: 'upload' | 'processing' | 'results';
  setStage: (stage: 'upload' | 'processing' | 'results') => void;
}

export default function Header({ stage, setStage }: HeaderProps) {
  return (
    <motion.header 
      initial={{ y: -100 }} animate={{ y: 0 }} transition={{ type: "spring", stiffness: 300, damping: 30 }}
      className="fixed top-0 w-full z-50 bg-surface/80 backdrop-blur-xl border-b border-outline-variant/30"
    >
      <div className="h-20 max-w-7xl mx-auto px-gutter flex flex-col justify-center">
        <div className="flex items-center justify-between gap-4">
          <motion.div 
            whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
            className="flex items-center gap-space-md cursor-pointer group" onClick={() => setStage('upload')}
          >
            <div className="flex items-baseline gap-2">
              <span className="font-headline-sm text-headline-sm text-ink-primary font-bold tracking-tight group-hover:text-accent-forest transition-colors">Granola AI</span>
              <span className="font-label-code text-label-code text-ink-muted uppercase hidden sm:inline">/ Meeting Intelligence</span>
            </div>
            {stage === 'results' && (
              <motion.div 
                initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
                className="hidden lg:flex items-center gap-2 px-space-sm py-0.5 rounded-full bg-paper-subtle border border-outline-variant/20"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-accent-chartreuse animate-pulse"></span>
                <span className="font-label-code text-label-code text-ink-secondary">Processed: Q3 Product & Engineering Sync</span>
              </motion.div>
            )}
          </motion.div>
          
          {stage === 'results' && (
            <motion.div 
              initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
              className="hidden md:flex items-center gap-space-sm px-space-md py-1.5 rounded-full bg-paper-subtle border border-outline-variant/20 shadow-sm"
            >
              <motion.button 
                whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}
                className="w-6 h-6 flex items-center justify-center rounded-full bg-accent-forest text-white hover:opacity-90 transition-opacity"
              >
                <Play className="w-3 h-3 ml-0.5" />
              </motion.button>
              <div className="w-32 lg:w-44 h-1.5 bg-surface-container-high rounded-full overflow-hidden flex items-center">
                <motion.div 
                  initial={{ width: 0 }} animate={{ width: "70%" }} transition={{ duration: 1.5, ease: "easeOut" }}
                  className="h-full bg-accent-forest rounded-full"
                ></motion.div>
              </div>
              <span className="font-label-code text-label-code text-ink-secondary">34:12 / 48:20</span>
            </motion.div>
          )}

          <div className="flex items-center gap-space-md">
            <div className="hidden sm:flex items-center gap-space-md">
              <a href="#" className="font-label-caps text-label-caps uppercase tracking-wider text-ink-muted hover:text-ink-primary transition-colors">About</a>
            </div>
            <motion.div 
              whileHover={{ scale: 1.1, backgroundColor: "var(--color-primary-fixed)" }}
              className="w-9 h-9 rounded-full bg-surface-container-high border border-outline-variant/30 flex items-center justify-center cursor-pointer transition-colors"
            >
              <User className="w-5 h-5 text-ink-secondary" />
            </motion.div>
          </div>
        </div>
      </div>
    </motion.header>
  );
}
