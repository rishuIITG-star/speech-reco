import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ProcessingScreen from './ProcessingScreen';
import ResultsScreen from './ResultsScreen';

export default function MeetingScreen() {
  const { id } = useParams<{ id: string }>();
  const [status, setStatus] = useState<any>(null);
  const [results, setResults] = useState<any>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!id) return;

    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/status/${id}`);
        
        if (!res.ok) return;
        
        const statusData = await res.json();
        setStatus(statusData);
        
        if (statusData.state === 'done') {
          clearInterval(interval);
          const resultsRes = await fetch(`/api/results/${id}`);
          if (resultsRes.ok) {
            const resData = await resultsRes.json();
            setResults(resData);
          } else {
            setStatus({ state: 'failed', error: { message: "Error fetching results" } });
          }
        } else if (statusData.state === 'failed') {
          clearInterval(interval);
        }
      } catch (err) {
        console.error(err);
      }
    }, 1000); // Check every 1 second

    return () => clearInterval(interval);
  }, [id, navigate]);

  if (results) {
    return <ResultsScreen results={results} jobId={id} />;
  }

  return <ProcessingScreen status={status} />;
}
