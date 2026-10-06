import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ProcessingScreen from './ProcessingScreen';
import ResultsScreen from './ResultsScreen';

export default function MeetingScreen() {
  const { id } = useParams<{ id: string }>();
  const [status, setStatus] = useState<any>(null);
  const [results, setResults] = useState<any>(null);
  const navigate = useNavigate();

  const [streamedSegments, setStreamedSegments] = useState<any[]>([]);

  useEffect(() => {
    if (!id) return;

    const eventSource = new EventSource(`/api/status/${id}/stream`);

    eventSource.addEventListener('status', async (e) => {
      try {
        const statusData = JSON.parse(e.data);
        setStatus(statusData);
        
        if (statusData.state === 'done') {
          eventSource.close();
          const resultsRes = await fetch(`/api/results/${id}`);
          if (resultsRes.ok) {
            const resData = await resultsRes.json();
            setResults(resData);
          } else {
            setStatus({ state: 'failed', error: { message: "Error fetching results" } });
          }
        } else if (statusData.state === 'failed') {
          eventSource.close();
        }
      } catch (err) {
        console.error(err);
      }
    });

    eventSource.addEventListener('segment', (e) => {
      try {
        const segData = JSON.parse(e.data);
        setStreamedSegments(prev => [...prev, segData]);
      } catch (err) {
        console.error(err);
      }
    });

    eventSource.onerror = (e) => {
      console.error('SSE Error:', e);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [id]);

  if (results) {
    return <ResultsScreen results={results} jobId={id} />;
  }

  return <ProcessingScreen status={status} streamedSegments={streamedSegments} />;
}
