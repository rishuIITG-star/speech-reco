import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, Calendar, ArrowRight, FileText, Plus } from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';

export default function DashboardScreen() {
  const [meetings, setMeetings] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchMeetings = async () => {
      setLoading(true);
      try {
        const url = searchQuery.trim() 
          ? `/api/search?q=${encodeURIComponent(searchQuery)}`
          : '/api/history';
          
        const res = await fetch(url);
        
        if (!res.ok) {
          console.error("Error fetching meetings", res.status);
          return;
        }
        
        const data = await res.json();
        setMeetings(data);
      } catch (err) {
        console.error("Error fetching meetings", err);
      } finally {
        setLoading(false);
      }
    };

    const debounceTimer = setTimeout(fetchMeetings, 300);
    return () => clearTimeout(debounceTimer);
  }, [searchQuery]);

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-title-lg font-bold text-ink-primary">Your Meetings</h1>
          <p className="text-ink-muted">Access and search all your past session artifacts.</p>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/upload" className="flex items-center gap-2 px-4 py-2 bg-accent-forest text-surface rounded-full font-label-code font-bold hover:bg-accent-chartreuse hover:text-ink-primary transition-colors">
            <Plus className="w-4 h-4" /> New Meeting
          </Link>
        </div>
      </div>

      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-ink-muted" />
        </div>
        <input
          type="text"
          placeholder="Search by title, summary, or keywords..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-11 pr-4 py-3 rounded-2xl bg-surface-container border border-outline-variant/30 focus:border-accent-forest/50 focus:outline-none transition-colors text-ink-primary placeholder:text-ink-muted"
        />
      </div>

      {loading ? (
        <div className="text-center py-12 text-ink-muted">Loading meetings...</div>
      ) : meetings.length === 0 ? (
        <div className="text-center py-12 p-8 rounded-3xl bg-surface-container border border-outline-variant/30">
          <FileText className="w-12 h-12 mx-auto text-ink-muted/50 mb-4" />
          <h3 className="text-lg font-bold text-ink-primary mb-2">No meetings found</h3>
          <p className="text-ink-muted">
            {searchQuery ? "Try adjusting your search terms." : "You haven't processed any meetings yet."}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {meetings.map((m, i) => (
            <motion.div
              key={m.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              onClick={() => navigate(`/meeting/${m.job_id}`)}
              className="group cursor-pointer p-6 rounded-3xl bg-surface-container border border-outline-variant/30 hover:border-accent-forest/30 hover:shadow-md transition-all flex flex-col h-full"
            >
              <div className="flex justify-between items-start mb-4">
                <h3 className="font-title-sm font-bold text-ink-primary line-clamp-1">{m.title}</h3>
                <span className={`px-2 py-1 rounded-full text-xs font-bold ${
                  m.status === 'done' ? 'bg-accent-forest/10 text-accent-forest' :
                  m.status === 'failed' ? 'bg-red-500/10 text-red-500' :
                  'bg-yellow-500/10 text-yellow-600'
                }`}>
                  {m.status.toUpperCase()}
                </span>
              </div>
              
              <div className="flex items-center gap-4 text-xs text-ink-muted font-label-code mb-4">
                <div className="flex items-center gap-1"><Calendar className="w-3 h-3" /> {new Date(m.created_at).toLocaleDateString()}</div>
              </div>

              <p className="text-sm text-ink-muted line-clamp-3 mb-6 flex-grow">
                {m.summary || "No summary available."}
              </p>

              <div className="flex items-center justify-between text-accent-forest text-sm font-bold mt-auto group-hover:text-accent-chartreuse">
                <span>View Details</span>
                <ArrowRight className="w-4 h-4 transform group-hover:translate-x-1 transition-transform" />
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
