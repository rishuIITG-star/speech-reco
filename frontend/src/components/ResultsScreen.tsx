import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, CalendarPlus, FileText, CheckCircle2, PlayCircle, Activity, Download, Plus, Trash2, Search, PauseCircle } from 'lucide-react';
import WaveSurfer from 'wavesurfer.js';

export default function ResultsScreen({ results, jobId }: { results: any, jobId?: string }) {
  const [activeTab, setActiveTab] = useState('decisions');
  const [actionItems, setActionItems] = useState<any[]>(results?.record?.action_items || []);
  const [decisions, setDecisions] = useState<any[]>(results?.record?.decisions || []);
  const [decisionSearch, setDecisionSearch] = useState('');
  
  // WaveSurfer
  const waveformRef = useRef<HTMLDivElement>(null);
  const wavesurferRef = useRef<WaveSurfer | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);

  const tabs = [
    { id: 'overview', label: 'AI Summary' },
    { id: 'refined', label: 'Refined Transcript' },
    { id: 'minutes', label: 'Minutes' },
    { id: 'decisions', label: 'Decisions' },
    { id: 'action-items', label: 'Action Items' }
  ];

  const record = results?.record || {};
  const refined = results?.refined || { segments: [] };
  const durationStr = record.meta?.duration ? `${(record.meta.duration / 60).toFixed(1)} mins` : 'Unknown';

  const formatTime = (sec: number) => {
    const m = Math.floor(sec / 60).toString().padStart(2, '0');
    const s = Math.floor(sec % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  const handleDownload = () => {
    const content = results?.minutes_md || "No report generated.";
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'Meeting_Report.md';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  useEffect(() => {
    if (waveformRef.current && jobId && !wavesurferRef.current) {
      wavesurferRef.current = WaveSurfer.create({
        container: waveformRef.current,
        waveColor: '#A3B18A',
        progressColor: '#3A5A40',
        cursorColor: '#588157',
        barWidth: 2,
        barGap: 2,
        barRadius: 2,
        height: 64,
        url: `/api/audio/${jobId}`
      });

      wavesurferRef.current.on('play', () => setIsPlaying(true));
      wavesurferRef.current.on('pause', () => setIsPlaying(false));
      wavesurferRef.current.on('timeupdate', (t) => setCurrentTime(t));
    }
    
    return () => {
      if (wavesurferRef.current) {
        wavesurferRef.current.destroy();
        wavesurferRef.current = null;
      }
    };
  }, [jobId]);

  const togglePlay = () => {
    if (wavesurferRef.current) {
      wavesurferRef.current.playPause();
    }
  };

  const playAt = (time: number) => {
    if (wavesurferRef.current) {
      const duration = wavesurferRef.current.getDuration();
      if (duration > 0) {
        wavesurferRef.current.seekTo(time / duration);
        wavesurferRef.current.play();
      }
    }
  };

  // Filtered decisions
  const filteredDecisions = decisions.filter((d: any) => 
    d.text.toLowerCase().includes(decisionSearch.toLowerCase()) || 
    d.evidence.toLowerCase().includes(decisionSearch.toLowerCase())
  );

  const filteredProposals = (record.proposals_not_agreed || []).filter((p: any) => 
    p.text.toLowerCase().includes(decisionSearch.toLowerCase()) || 
    p.evidence.toLowerCase().includes(decisionSearch.toLowerCase())
  );

  return (
    <motion.div 
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      className="pb-20"
    >
      <motion.div 
        initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ duration: 0.6, ease: "easeOut" }}
        className="flex flex-col md:flex-row md:items-end justify-between gap-space-md pb-space-lg mb-space-xl bg-surface-container-low p-space-lg rounded-xl overflow-hidden relative border border-outline-variant/30"
      >
        <div className="absolute -top-24 -right-24 w-64 h-64 bg-secondary-fixed opacity-30 rounded-full blur-3xl mix-blend-multiply"></div>
        
        <div className="space-y-space-xs relative z-10">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-label-caps text-label-caps uppercase text-ink-muted tracking-wider">Protocol Session Artifacts</span>
            <span className="w-1.5 h-1.5 rounded-full bg-accent-chartreuse animate-pulse"></span>
            <span className="font-label-code text-label-code text-accent-forest font-medium">Consensus Verifier v2.4</span>
            {record.meta && (
              <span className="font-label-code text-xs text-ink-muted ml-4 border-l border-outline-variant/30 pl-4">
                ASR: {record.meta.asr_model} | Refiner: {record.meta.refiner_model} | Extractor: {record.meta.extractor_model}
              </span>
            )}
          </div>
          <h1 className="font-headline-lg text-headline-lg text-ink-primary">Deliberation Record & Executive Decisions</h1>
          <p className="font-body-md text-body-md text-ink-secondary max-w-2xl">
            Extracted statements, resolution consensus metrics, and verbatim audio evidence from your processed audio.
          </p>
        </div>
        <div className="flex items-center gap-space-sm flex-wrap relative z-10">
          <motion.div whileHover={{ scale: 1.05 }} className="flex items-center gap-2 px-space-md py-1.5 rounded-full bg-paper-subtle cursor-default shadow-sm border border-outline-variant/20">
            <span className="font-label-code text-label-code text-ink-muted">Action Items:</span>
            <span className="font-label-code text-label-code font-bold text-accent-forest">{actionItems.length}</span>
          </motion.div>
          <motion.div whileHover={{ scale: 1.05 }} className="flex items-center gap-2 px-space-md py-1.5 rounded-full bg-surface-container-highest cursor-default shadow-sm border border-outline-variant/20">
            <span className="font-label-code text-label-code text-ink-muted">Decisions:</span>
            <span className="font-label-code text-label-code font-semibold text-ink-primary">{filteredDecisions.length} / {decisions.length}</span>
          </motion.div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleDownload}
            className="flex items-center gap-2 px-space-md py-1.5 rounded-full bg-accent-forest text-surface cursor-pointer shadow-sm border border-accent-forest/20 font-label-code text-label-code font-bold hover:bg-accent-chartreuse hover:text-ink-primary transition-colors ml-2"
          >
            <Download className="w-4 h-4" /> Download Report
          </motion.button>
        </div>
      </motion.div>

      <div className="mb-space-lg border-b border-surface-container-high overflow-x-auto pb-2">
        <nav className="flex items-center gap-2 py-1 min-w-max">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`relative px-space-lg py-2.5 rounded-full font-button-text text-button-text transition-colors ${
                activeTab === tab.id ? 'text-surface' : 'text-ink-secondary hover:text-ink-primary hover:bg-paper-subtle/50'
              }`}
            >
              {activeTab === tab.id && (
                <motion.div
                  layoutId="active-tab"
                  className="absolute inset-0 bg-ink-primary rounded-full shadow-md"
                  transition={{ type: "spring", stiffness: 400, damping: 30 }}
                />
              )}
              <span className="relative z-10">{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-xl">
        <div className="lg:col-span-8">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 15, filter: "blur(4px)" }}
              animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
              exit={{ opacity: 0, y: -15, filter: "blur(4px)" }}
              transition={{ duration: 0.3 }}
            >
              {activeTab === 'overview' && (
                <section className="bg-surface-container-lowest rounded-xl p-space-xl shadow-sm border border-outline-variant/30 relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-accent-forest to-secondary-fixed"></div>
                  <h2 className="font-headline-md text-headline-md text-ink-primary mb-6 flex items-center gap-3">
                    <Sparkles className="w-6 h-6 text-accent-forest" /> 
                    AI Executive Summary
                  </h2>
                  <p className="font-body-lg text-ink-secondary leading-relaxed mb-6">
                    {record.summary || "No summary available."}
                  </p>
                </section>
              )}

              {activeTab === 'action-items' && (
                <section>
                  <div className="flex items-center justify-between mb-6 border-b border-surface-container-high pb-4">
                    <h2 className="font-headline-md text-headline-md text-ink-primary flex items-center gap-2">
                      Action Items
                      <button 
                        onClick={async () => {
                          try {
                            const res = await fetch(`/api/results/${jobId}/save`, {
                              method: 'POST',
                              headers: { 'Content-Type': 'application/json' },
                              body: JSON.stringify({ action_items: actionItems })
                            });
                            if (res.ok) alert("Saved successfully!");
                            else alert("Failed to save.");
                          } catch (err) {
                            console.error(err);
                          }
                        }}
                        className="ml-4 text-sm px-3 py-1 bg-accent-forest text-surface rounded-full shadow hover:bg-accent-forest/90"
                      >
                        Save Changes
                      </button>
                    </h2>
                    <button 
                      onClick={() => setActionItems([{ task: 'New Action Item', owner: 'Unspecified', deadline: 'Unspecified', completed: false }, ...actionItems])}
                      className="flex items-center gap-2 px-4 py-2 bg-paper-subtle hover:bg-surface-container-high rounded-full font-button-text text-ink-primary border border-outline-variant/30 transition-colors"
                    >
                      <Plus className="w-4 h-4" /> Add Item
                    </button>
                  </div>
                  <div className="space-y-4">
                    {actionItems.map((item: any, idx: number) => (
                      <motion.div 
                        initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: idx * 0.1 }}
                        key={idx} 
                        className={`group bg-surface-container-lowest hover:bg-surface-container-low transition-colors rounded-xl p-space-lg shadow-sm border ${item.completed ? 'border-accent-forest/50 bg-accent-forest/5' : 'border-outline-variant/30'} flex flex-col md:flex-row md:items-start justify-between gap-4`}
                      >
                        <div className="flex gap-4 flex-1">
                          <input 
                            type="checkbox" 
                            checked={item.completed || false}
                            onChange={(e) => {
                              const newItems = [...actionItems];
                              newItems[idx].completed = e.target.checked;
                              setActionItems(newItems);
                            }}
                            className="mt-1 w-5 h-5 rounded border-outline-variant text-accent-forest focus:ring-accent-forest cursor-pointer"
                          />
                          <div className="flex-1 space-y-3">
                            <input 
                              type="text" 
                              value={item.task}
                              onChange={(e) => {
                                const newItems = [...actionItems];
                                newItems[idx].task = e.target.value;
                                setActionItems(newItems);
                              }}
                              className={`w-full bg-transparent border-none p-0 focus:ring-0 font-headline-sm transition-colors ${item.completed ? 'text-ink-muted line-through' : 'text-ink-primary group-hover:text-accent-forest'}`}
                            />
                            <div className="flex items-center gap-3">
                              <span className={`px-2 py-0.5 rounded text-[12px] font-label-code shadow-sm ${item.owner?.toLowerCase() === 'unspecified' ? 'bg-surface-container-high text-ink-muted' : 'bg-primary-fixed text-on-primary-fixed'}`}>
                                Owner: <input type="text" value={item.owner || ''} onChange={e => { const newItems=[...actionItems]; newItems[idx].owner = e.target.value; setActionItems(newItems); }} className="bg-transparent border-none p-0 focus:ring-0 w-24 text-[12px]" />
                              </span>
                              <span className={`px-2 py-0.5 rounded text-[12px] font-label-code shadow-sm ${item.deadline?.toLowerCase() === 'unspecified' ? 'bg-surface-container-high text-ink-muted' : 'bg-secondary-fixed-dim text-on-secondary-fixed'}`}>
                                Due: <input type="text" value={item.deadline || ''} onChange={e => { const newItems=[...actionItems]; newItems[idx].deadline = e.target.value; setActionItems(newItems); }} className="bg-transparent border-none p-0 focus:ring-0 w-24 text-[12px]" />
                              </span>
                              {item.verified && (
                                <span className="flex items-center gap-1 px-2 py-0.5 rounded text-[12px] font-label-code shadow-sm bg-accent-chartreuse/20 text-accent-forest border border-accent-chartreuse/30">
                                  <CheckCircle2 className="w-3 h-3" /> Verified
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <motion.button 
                            whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                            className="shrink-0 px-4 py-2 rounded-full border border-ink-primary text-ink-primary font-button-text hover:bg-ink-primary hover:text-surface transition-all flex items-center gap-2 shadow-sm"
                          >
                            <CalendarPlus className="w-4 h-4" />
                            Calendar
                          </motion.button>
                          <button 
                            onClick={() => {
                              const newItems = [...actionItems];
                              newItems.splice(idx, 1);
                              setActionItems(newItems);
                            }}
                            className="p-2 text-error/70 hover:text-error hover:bg-error/10 rounded-full transition-colors"
                          >
                            <Trash2 className="w-5 h-5" />
                          </button>
                        </div>
                      </motion.div>
                    ))}
                    {actionItems.length === 0 && (
                      <p className="text-ink-secondary">No action items extracted.</p>
                    )}
                  </div>
                </section>
              )}

              {activeTab === 'refined' && (
                <section className="bg-surface-container-lowest rounded-xl p-space-xl shadow-sm border border-outline-variant/30">
                  <div className="flex justify-between items-center mb-6 border-b border-surface-container-high pb-4">
                    <h2 className="font-headline-md text-headline-md text-ink-primary">Refined Transcript</h2>
                  </div>
                  <div className="space-y-6">
                    {refined.segments?.map((m: any, i: number) => (
                      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }} key={m.id || i}>
                        <div className="flex items-center gap-3 mb-1">
                          <span className="font-label-code font-bold text-ink-primary bg-surface-container-high px-2 py-0.5 rounded shadow-sm">{m.speaker || 'Speaker'}</span>
                        </div>
                        <p className="font-body-lg text-ink-secondary leading-relaxed" dangerouslySetInnerHTML={{__html: m.text}}></p>
                      </motion.div>
                    ))}
                  </div>
                </section>
              )}
              
              {activeTab === 'minutes' && (
                <section className="bg-surface-container-lowest rounded-xl p-space-xl shadow-sm border border-outline-variant/30">
                  <h2 className="font-headline-md text-headline-md text-ink-primary mb-6 flex items-center gap-3">
                    <FileText className="w-6 h-6 text-accent-forest" /> Meeting Minutes
                  </h2>
                  <ul className="space-y-6">
                    {(record.minutes || []).map((t: any, i: number) => (
                      <motion.li 
                        initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }}
                        key={i} className="flex flex-col gap-2 text-ink-secondary font-body-lg items-start"
                      >
                        <div className="flex gap-4 items-center">
                          <span className="w-2.5 h-2.5 rounded-full bg-accent-forest shrink-0 shadow-sm"></span>
                          <strong>{t.title}</strong>
                        </div>
                        <ul className="pl-8 list-disc list-inside">
                          {t.points?.map((p: string, pIdx: number) => (
                            <li key={pIdx} dangerouslySetInnerHTML={{__html: p}}></li>
                          ))}
                        </ul>
                      </motion.li>
                    ))}
                    {(!record.minutes || record.minutes.length === 0) && (
                      <p>No minutes extracted.</p>
                    )}
                  </ul>
                </section>
              )}

              {activeTab === 'decisions' && (
                <section>
                    <div className="flex items-center justify-between pb-space-md mb-space-lg border-b border-surface-container-high">
                      <div className="flex items-center gap-space-sm">
                        <span className="w-3 h-3 rounded-full bg-accent-forest shadow-sm"></span>
                        <h2 className="font-headline-md text-headline-md text-ink-primary flex items-center gap-2">
                          Agreed Decisions
                          <button 
                            onClick={async () => {
                              try {
                                const res = await fetch(`/api/results/${jobId}/save`, {
                                  method: 'POST',
                                  headers: { 'Content-Type': 'application/json' },
                                  body: JSON.stringify({ decisions: decisions })
                                });
                                if (res.ok) alert("Saved successfully!");
                                else alert("Failed to save.");
                              } catch (err) {
                                console.error(err);
                              }
                            }}
                            className="ml-4 text-sm px-3 py-1 bg-accent-forest text-surface rounded-full shadow hover:bg-accent-forest/90"
                          >
                            Save Changes
                          </button>
                        </h2>
                        <motion.span 
                          initial={{ scale: 0.8 }} animate={{ scale: 1 }}
                          className="px-space-md py-1 rounded-full bg-paper-subtle font-label-code text-label-code text-accent-forest font-bold border border-outline-variant/20"
                        >
                          {filteredDecisions.length} Confirmed
                        </motion.span>
                      </div>
                      
                      <div className="relative">
                        <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-ink-muted" />
                        <input 
                          type="text" 
                          placeholder="Search decisions..."
                          value={decisionSearch}
                          onChange={(e) => setDecisionSearch(e.target.value)}
                          className="pl-9 pr-4 py-2 bg-surface-container-lowest border border-outline-variant/50 rounded-full font-body-sm focus:outline-none focus:border-accent-forest focus:ring-1 focus:ring-accent-forest transition-all"
                        />
                      </div>
                    </div>
                    
                    <div className="space-y-space-md">
                      {filteredDecisions.map((decision: any, dIdx: number) => (
                        <motion.article 
                          key={dIdx}
                          whileHover={{ y: -4, scale: 1.01 }}
                          className="bg-surface-container-lowest rounded-xl p-space-xl shadow-sm hover:shadow-xl transition-all relative overflow-hidden group cursor-pointer border border-outline-variant/30"
                        >
                          <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-accent-forest"></div>
                          <div className="flex flex-col space-y-space-md pl-space-xs">
                            <div className="flex items-center justify-between flex-wrap gap-space-sm">
                              <div className="flex items-center gap-space-sm">
                                <span className="inline-flex items-center gap-1.5 px-space-sm py-1 rounded-full bg-secondary-fixed text-primary font-label-caps text-label-caps font-semibold shadow-sm">
                                  <CheckCircle2 className="w-3.5 h-3.5" /> Agreed
                                </span>
                                <button type="button" onClick={() => playAt(decision.timestamp || 0)} className="group/play inline-flex items-center gap-1.5 px-space-sm py-1 rounded-full bg-paper-subtle hover:bg-ink-primary hover:text-surface transition-colors text-ink-primary shadow-sm">
                                  <PlayCircle className="w-4 h-4 text-accent-forest group-hover/play:text-surface transition-colors" />
                                  <span className="font-label-code text-label-code font-medium">{formatTime(decision.timestamp || 0)}</span>
                                </button>
                                {decision.verified && (
                                  <span className="inline-flex items-center gap-1.5 px-space-sm py-1 rounded-full bg-accent-chartreuse/20 text-accent-forest font-label-caps text-[10px] font-semibold border border-accent-chartreuse/30 shadow-sm">
                                    <CheckCircle2 className="w-3 h-3" /> Verified Source
                                  </span>
                                )}
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              <input 
                                type="text"
                                value={decision.text}
                                onChange={(e) => {
                                  const newDecisions = [...decisions];
                                  const index = decisions.findIndex(d => d === decision);
                                  if (index !== -1) {
                                    newDecisions[index] = { ...newDecisions[index], text: e.target.value };
                                    setDecisions(newDecisions);
                                  }
                                }}
                                className="w-full bg-transparent border-none p-0 focus:ring-0 font-headline-sm text-headline-sm text-ink-primary font-semibold leading-snug group-hover:text-accent-forest transition-colors"
                              />
                              <button 
                                onClick={() => {
                                  const newDecisions = [...decisions];
                                  const index = decisions.findIndex(d => d === decision);
                                  if (index !== -1) {
                                    newDecisions.splice(index, 1);
                                    setDecisions(newDecisions);
                                  }
                                }}
                                className="p-2 text-error/70 hover:text-error hover:bg-error/10 rounded-full transition-colors shrink-0"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </div>
                            <div className="bg-paper-subtle rounded-lg p-space-lg relative overflow-hidden border border-outline-variant/20">
                              <div className="flex items-start gap-space-sm relative z-10">
                                <blockquote className="font-headline-md italic text-ink-secondary text-[18px] leading-relaxed">
                                  "{decision.evidence}"
                                </blockquote>
                              </div>
                            </div>
                          </div>
                        </motion.article>
                      ))}
                      {filteredDecisions.length === 0 && (
                        <p className="text-ink-secondary text-center py-8">No decisions match your search.</p>
                      )}
                    </div>
                    
                    {filteredProposals.length > 0 && (
                      <div className="mt-12 pt-8 border-t border-surface-container-high">
                        <div className="flex items-center gap-space-sm pb-space-md mb-space-lg">
                          <span className="w-3 h-3 rounded-full bg-ink-muted shadow-sm"></span>
                          <h2 className="font-headline-md text-headline-md text-ink-primary">Discussed but not agreed</h2>
                          <motion.span 
                            initial={{ scale: 0.8 }} animate={{ scale: 1 }}
                            className="px-space-md py-1 rounded-full bg-paper-subtle font-label-code text-label-code text-ink-muted font-bold border border-outline-variant/20"
                          >
                            {filteredProposals.length} Proposals
                          </motion.span>
                        </div>
                        
                        <div className="space-y-space-md">
                          {filteredProposals.map((proposal: any, pIdx: number) => (
                            <motion.article 
                              key={`p-${pIdx}`}
                              whileHover={{ y: -4, scale: 1.01 }}
                              className="bg-surface-container-lowest rounded-xl p-space-xl shadow-sm hover:shadow-xl transition-all relative overflow-hidden group cursor-pointer border border-outline-variant/30 opacity-80 hover:opacity-100"
                            >
                              <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-ink-muted"></div>
                              <div className="flex flex-col space-y-space-md pl-space-xs">
                                <div className="flex items-center justify-between flex-wrap gap-space-sm">
                                  <div className="flex items-center gap-space-sm">
                                    <span className="inline-flex items-center gap-1.5 px-space-sm py-1 rounded-full bg-surface-container-highest text-ink-secondary font-label-caps text-label-caps font-semibold shadow-sm">
                                      Proposal
                                    </span>
                                    <button type="button" onClick={() => playAt(proposal.timestamp || 0)} className="group/play inline-flex items-center gap-1.5 px-space-sm py-1 rounded-full bg-paper-subtle hover:bg-ink-primary hover:text-surface transition-colors text-ink-primary shadow-sm">
                                      <PlayCircle className="w-4 h-4 text-ink-muted group-hover/play:text-surface transition-colors" />
                                      <span className="font-label-code text-label-code font-medium">{formatTime(proposal.timestamp || 0)}</span>
                                    </button>
                                  </div>
                                </div>
                                <h3 className="font-headline-sm text-headline-sm text-ink-primary font-semibold leading-snug">
                                  {proposal.text}
                                </h3>
                                <div className="bg-paper-subtle rounded-lg p-space-lg relative overflow-hidden border border-outline-variant/20">
                                  <div className="flex items-start gap-space-sm relative z-10">
                                    <blockquote className="font-headline-md italic text-ink-secondary text-[18px] leading-relaxed">
                                      "{proposal.evidence}"
                                    </blockquote>
                                  </div>
                                </div>
                              </div>
                            </motion.article>
                          ))}
                        </div>
                      </div>
                    )}
                </section>
              )}
            </motion.div>
          </AnimatePresence>
        </div>
        
        <aside className="lg:col-span-4 space-y-space-lg">
          <motion.div 
            initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }}
            className="bg-surface-container-lowest rounded-xl p-space-lg shadow-md border border-outline-variant/30 space-y-space-md relative overflow-hidden"
          >
            <div className="flex items-center justify-between relative z-10">
              <span className="font-label-caps text-label-caps uppercase text-ink-muted tracking-wider flex items-center gap-2">
                <Activity className="w-4 h-4" /> Audio Verifier
              </span>
              <span className="flex items-center gap-1.5 font-label-code text-label-code text-accent-chartreuse bg-accent-chartreuse/10 px-3 py-1 rounded-full border border-accent-chartreuse/20">
                <span className="w-2 h-2 rounded-full bg-accent-chartreuse animate-ping"></span>
                Processed
              </span>
            </div>
            
            <div className="bg-paper-subtle rounded-lg p-space-md flex flex-col gap-2 relative z-10 border border-outline-variant/50">
              <div className="flex items-center justify-between">
                <span className="font-label-code text-label-code text-ink-primary font-medium flex items-center gap-2">
                  <button onClick={togglePlay} className="p-1 rounded-full bg-accent-forest text-surface hover:scale-110 transition-transform">
                    {isPlaying ? <PauseCircle className="w-4 h-4" /> : <PlayCircle className="w-4 h-4" />}
                  </button>
                  {formatTime(currentTime)} / {durationStr}
                </span>
                <span className="font-label-code text-label-code text-ink-muted flex items-center gap-2">
                  <Activity className="w-3 h-3" /> Audio Player
                </span>
              </div>
              <div id="waveform" ref={waveformRef} className="w-full mt-2 cursor-pointer"></div>
            </div>
          </motion.div>
        </aside>
      </div>
    </motion.div>
  );
}
