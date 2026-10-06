import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Cpu, Check, AlertCircle, RefreshCw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface ProcessingScreenProps {
  status: any;
}

export default function ProcessingScreen({ status }: ProcessingScreenProps) {
  const navigate = useNavigate();
  let step = 1;
  const isFailed = status?.state === 'failed';
  
  if (status && !isFailed) {
    const stage = status.stage;
    if (['refining'].includes(stage)) step = 2;
    if (['extracting', 'rendering', 'done'].includes(stage)) step = 3;
    if (stage === 'done') step = 4;
  }

  const steps = [
    { id: 1, title: 'Transcribing', desc: 'Running Whisper large-v3 with VAD chunking' },
    { id: 2, title: 'Refining', desc: 'LLM-1 fixing terms without changing meaning' },
    { id: 3, title: 'Documenting', desc: 'LLM-2 extracting minutes and decisions' }
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 1.05 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="max-w-2xl mx-auto mt-20"
    >
      <div className="text-center mb-space-2xl">
        <motion.div 
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 4, ease: "linear" }}
          className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-surface-container-low shadow-inner mb-6 border border-outline-variant/30"
        >
          <motion.div
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ repeat: Infinity, duration: 2, ease: "easeInOut" }}
          >
            <Cpu className="w-10 h-10 text-accent-forest" />
          </motion.div>
        </motion.div>
        <motion.h2 
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
          className="font-headline-lg text-headline-lg text-ink-primary mb-2"
        >
          Analyzing Meeting
        </motion.h2>
        <motion.p 
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}
          className="font-body-md text-ink-secondary"
        >
          This might take a few minutes depending on the meeting length.
        </motion.p>
      </div>

      {isFailed && (
        <motion.div 
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
          className="mb-space-2xl bg-error/10 border border-error/20 rounded-xl p-space-lg flex flex-col items-center text-center"
        >
          <AlertCircle className="w-8 h-8 text-error mb-2" />
          <h3 className="font-headline-sm text-error mb-1">Processing Failed {status.error?.code ? `(${status.error.code})` : ''}</h3>
          <p className="font-body-sm text-error/80 mb-4">{status.error?.message || "An unknown error occurred"}</p>
          <button 
            onClick={() => navigate('/')}
            className="flex items-center gap-2 px-4 py-2 bg-error text-white rounded-lg hover:bg-error/90 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Upload New Audio</span>
          </button>
        </motion.div>
      )}

      <div className={`space-y-space-md relative before:absolute before:inset-0 before:ml-8 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-outline-variant before:to-transparent ${isFailed ? 'opacity-50 pointer-events-none' : ''}`}>
        {steps.map((s, idx) => (
          <motion.div 
            initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: idx * 0.2 }}
            key={s.id} 
            className={`relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active`}
          >
            <div className={`flex items-center justify-center w-10 h-10 rounded-full border-4 border-surface shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 shadow-sm transition-colors duration-500 ${step > s.id ? 'bg-accent-forest text-surface' : step === s.id ? 'bg-secondary-fixed text-primary' : 'bg-surface-container-high text-ink-muted'}`}>
              {step > s.id ? (
                <Check className="w-5 h-5" />
              ) : (
                <span className="font-label-code text-label-code">{s.id}</span>
              )}
            </div>
            
            <div className={`w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-space-md rounded-xl transition-all duration-500 border ${step === s.id ? 'bg-surface-container-lowest shadow-md border-accent-forest/30 scale-105' : 'bg-transparent border-transparent opacity-60'}`}>
              <div className="flex items-center justify-between mb-1">
                <h4 className="font-headline-sm text-headline-sm text-ink-primary">{s.title}</h4>
                {step === s.id && (
                  <div className="flex gap-1.5">
                    <motion.span animate={{ scale: [1, 1.5, 1], opacity: [0.5, 1, 0.5] }} transition={{ repeat: Infinity, duration: 1, delay: 0 }} className="w-1.5 h-1.5 rounded-full bg-accent-forest"></motion.span>
                    <motion.span animate={{ scale: [1, 1.5, 1], opacity: [0.5, 1, 0.5] }} transition={{ repeat: Infinity, duration: 1, delay: 0.2 }} className="w-1.5 h-1.5 rounded-full bg-accent-forest"></motion.span>
                    <motion.span animate={{ scale: [1, 1.5, 1], opacity: [0.5, 1, 0.5] }} transition={{ repeat: Infinity, duration: 1, delay: 0.4 }} className="w-1.5 h-1.5 rounded-full bg-accent-forest"></motion.span>
                  </div>
                )}
              </div>
              <p className="font-body-sm text-ink-muted">{s.desc}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
