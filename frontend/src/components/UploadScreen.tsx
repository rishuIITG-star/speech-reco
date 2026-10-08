import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, StopCircle, UploadCloud, FileAudio, ArrowRight, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function UploadScreen() {
  const [file, setFile] = useState<File | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [glossary, setGlossary] = useState("");
  
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];
      
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };
      
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        const newFile = new File([blob], "recorded_meeting.webm", { type: 'audio/webm' });
        setFile(newFile);
        stream.getTracks().forEach(track => track.stop());
      };
      
      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } catch (err) {
      console.error("Error accessing microphone", err);
      alert("Could not access microphone.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
    if (timerRef.current) clearInterval(timerRef.current);
  };

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
      }
    };
  }, []);

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60).toString().padStart(2, '0');
    const s = (seconds % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];
      
      const allowedTypes = ['audio/mpeg', 'audio/wav', 'audio/x-wav', 'audio/mp4', 'audio/x-m4a', 'audio/m4a', 'audio/webm'];
      if (!allowedTypes.includes(selectedFile.type) && !selectedFile.name.match(/\.(mp3|wav|m4a|webm)$/i)) {
        alert("Unsupported file format. Please use MP3, WAV, M4A, or WEBM.");
        return;
      }
      
      const maxSize = 500 * 1024 * 1024; // 500MB
      if (selectedFile.size > maxSize) {
        alert("File is too large. Maximum size is 500MB.");
        return;
      }
      
      setFile(selectedFile);
    }
  };

  const handleStart = async () => {
    if (!file) return;
    setLoading(true);
    
    const formData = new FormData();
    formData.append('file', file);
    if (glossary) formData.append('glossary', glossary);

    try {
      const res = await fetch('/api/process', {
        method: 'POST',
        body: formData,
      });
      
      if (!res.ok) throw new Error("Failed to upload");
      const data = await res.json();
      navigate(`/meeting/${data.job_id}`);
    } catch (err) {
      console.error(err);
      alert("Error starting process");
      setLoading(false);
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="max-w-3xl mx-auto mt-10"
    >
      <div className="mb-space-lg text-center">
        <motion.h1 
          initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="font-headline-lg text-headline-lg text-ink-primary mb-2"
        >
          Upload or Record Meeting
        </motion.h1>
        <motion.p 
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}
          className="font-body-md text-ink-secondary"
        >
          Supported formats: MP3, M4A, WAV, WEBM (Max 500MB)
        </motion.p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-space-md mb-space-lg">
        {/* Upload Box */}
        <motion.div 
          whileHover={{ scale: 1.02, backgroundColor: "var(--color-surface-container-low)" }}
          whileTap={{ scale: 0.98 }}
          onClick={() => fileInputRef.current?.click()}
          className="bg-surface-container-lowest rounded-xl p-space-xl shadow-sm border-2 border-dashed border-outline-variant text-center cursor-pointer flex flex-col items-center justify-center transition-colors relative"
        >
          <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" accept="audio/*" />
          <UploadCloud className="w-12 h-12 text-accent-forest mb-4" />
          <h3 className="font-headline-sm text-headline-sm text-ink-primary mb-1">Drag & Drop</h3>
          <p className="font-body-sm text-ink-muted mb-4">or click to browse files</p>
          <button className="px-space-md py-2 rounded-full bg-paper-subtle text-ink-primary font-button-text hover:bg-paper-border transition-colors">
            Select File
          </button>
        </motion.div>

        {/* Record Box */}
        <motion.div 
          className="bg-surface-container-lowest rounded-xl p-space-xl shadow-sm border-2 border-outline-variant text-center flex flex-col items-center justify-center relative overflow-hidden"
          layout
        >
          {isRecording ? (
            <motion.div 
              initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }}
              className="flex flex-col items-center w-full"
            >
              <div className="flex items-end justify-center h-16 gap-1 mb-4 w-full">
                {/* Audio Waveform Animation */}
                {[...Array(12)].map((_, i) => (
                  <motion.div
                    key={i}
                    animate={{ height: ["20%", "100%", "30%", "80%", "20%"] }}
                    transition={{ repeat: Infinity, duration: 1.5, ease: "easeInOut", delay: i * 0.1 }}
                    className="w-2 bg-error rounded-full"
                  />
                ))}
              </div>
              <h3 className="font-headline-sm text-headline-sm text-error mb-1">Recording Live...</h3>
              <p className="font-label-code text-label-code text-ink-primary mb-4 font-bold">{formatTime(recordingTime)}</p>
              <motion.button 
                whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                onClick={stopRecording}
                className="px-space-md py-2 rounded-full bg-error text-surface font-button-text flex items-center gap-2 shadow-lg"
              >
                <StopCircle className="w-4 h-4" /> Stop Recording
              </motion.button>
            </motion.div>
          ) : (
            <motion.div 
              initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              className="flex flex-col items-center"
            >
              <Mic className="w-12 h-12 text-ink-primary mb-4" />
              <h3 className="font-headline-sm text-headline-sm text-ink-primary mb-1">Record Audio</h3>
              <p className="font-body-sm text-ink-muted mb-4">Capture meeting directly</p>
              <motion.button 
                whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                onClick={startRecording}
                className="px-space-md py-2 rounded-full bg-ink-primary text-surface font-button-text flex items-center gap-2 shadow-md"
              >
                <Mic className="w-4 h-4" /> Start
              </motion.button>
            </motion.div>
          )}
        </motion.div>
      </div>

      <AnimatePresence>
        {file && (
          <motion.div 
            initial={{ opacity: 0, y: 10, scale: 0.95 }} 
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="bg-paper-subtle rounded-xl p-space-md mb-space-lg flex items-center justify-between border border-outline-variant/30"
          >
            <div className="flex items-center gap-3">
              <FileAudio className="w-6 h-6 text-accent-forest" />
              <div>
                <p className="font-headline-sm text-ink-primary">{file.name}</p>
                <p className="font-label-code text-ink-muted uppercase tracking-wider">Ready to process</p>
              </div>
            </div>
            <button onClick={() => setFile(null)} className="text-ink-muted hover:text-error transition-colors p-1">
              <X className="w-5 h-5" />
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.div 
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}
        className="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm mb-space-xl"
      >
        <label className="block font-headline-sm text-headline-sm text-ink-primary mb-2">
          Meeting Context (Optional)
        </label>
        <p className="font-body-sm text-ink-muted mb-4">
          Add expected terms, acronyms, and participant names to improve transcription accuracy.
        </p>
        <textarea 
          value={glossary}
          onChange={e => setGlossary(e.target.value)}
          className="w-full bg-surface-container-low border border-outline-variant rounded-lg p-space-md font-body-md text-ink-primary focus:outline-none focus:border-accent-forest transition-all min-h-[120px]"
          placeholder="e.g. Kubernetes, API v1, MFA, SOC2 compliance, Elena Zhao, Marcus Vance..."
        />
      </motion.div>

      <motion.div 
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}
        className="flex justify-end"
      >
        <motion.button 
          whileHover={file && !loading ? { scale: 1.05, paddingRight: "2rem" } : {}}
          whileTap={file && !loading ? { scale: 0.95 } : {}}
          onClick={handleStart}
          disabled={!file || loading}
          className={`relative px-space-xl py-3 rounded-full font-button-text text-button-text transition-all flex items-center gap-2 overflow-hidden ${
            file ? 'bg-ink-primary text-surface shadow-lg' : 'bg-surface-container-high text-ink-muted cursor-not-allowed'
          }`}
        >
          {file && (
            <motion.div 
              className="absolute inset-0 bg-white/10"
              initial={{ x: "-100%" }}
              whileHover={{ x: "100%" }}
              transition={{ duration: 0.5 }}
            />
          )}
          <span>{loading ? 'Starting...' : 'Start Processing'}</span>
          <ArrowRight className="w-4 h-4 relative z-10" />
        </motion.button>
      </motion.div>
    </motion.div>
  );
}

