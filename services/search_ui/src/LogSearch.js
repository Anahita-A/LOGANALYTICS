import React, { useState, useEffect } from 'react';
import { Search } from 'lucide-react';

const LogSearch = () => {
  const [query, setQuery] = useState('');
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [logLevel, setLogLevel] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [error, setError] = useState(null);

  const searchLogs = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({
        q: query,
        ...(logLevel && { level: logLevel }),
        ...(startTime && { start: startTime }),
        ...(endTime && { end: endTime }),
      });

      const response = await fetch(`http://localhost:5005/api/search?${params}`);
      if (!response.ok) {
        throw new Error('Search failed');
      }
      const data = await response.json();
      setLogs(data.results || []);
    } catch (error) {
      console.error('Search failed:', error);
      setError('Failed to fetch logs. Please try again.');
    }
    setLoading(false);
  };

  const formatData = (data) => {
    try {
      return JSON.stringify(data, null, 2);
    } catch (e) {
      return JSON.stringify(data);
    }
  };

  return (
    <div className="p-4 max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-4">LogScope Search</h1>
        
        <div className="flex gap-4 mb-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search logs..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full p-2 border rounded"
              onKeyPress={(e) => e.key === 'Enter' && searchLogs()}
            />
          </div>
          
          <select
            value={logLevel}
            onChange={(e) => setLogLevel(e.target.value)}
            className="p-2 border rounded"
          >
            <option value="">All Levels</option>
            <option value="info">Info</option>
            <option value="error">Error</option>
          </select>
          
          <button
            onClick={searchLogs}
            className="px-4 py-2 bg-blue-500 text-white rounded flex items-center gap-2 hover:bg-blue-600 disabled:opacity-50"
            disabled={loading}
          >
            <Search size={20} />
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
        
        <div className="flex gap-4 mb-4">
          <input
            type="datetime-local"
            value={startTime}
            onChange={(e) => setStartTime(e.target.value)}
            className="p-2 border rounded"
            placeholder="Start Time"
          />
          <input
            type="datetime-local"
            value={endTime}
            onChange={(e) => setEndTime(e.target.value)}
            className="p-2 border rounded"
            placeholder="End Time"
          />
        </div>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 text-red-700 rounded">
          {error}
        </div>
      )}

      <div className="border rounded-lg overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="p-3 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
              <th className="p-3 text-left text-xs font-medium text-gray-500 uppercase">Level</th>
              <th className="p-3 text-left text-xs font-medium text-gray-500 uppercase">Event</th>
              <th className="p-3 text-left text-xs font-medium text-gray-500 uppercase">Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {logs.map((log, index) => (
              <tr key={index} className={log.level === 'error' ? 'bg-red-50' : 'bg-white'}>
                <td className="p-3 text-sm">
                  {new Date(log.timestamp).toLocaleString()}
                </td>
                <td className="p-3 text-sm">
                  <span className={`px-2 py-1 rounded text-xs ${
                    log.level === 'error' ? 'bg-red-100 text-red-800' : 'bg-blue-100 text-blue-800'
                  }`}>
                    {log.level}
                  </span>
                </td>
                <td className="p-3 text-sm">{log.event}</td>
                <td className="p-3 text-sm font-mono text-xs">
                  <pre className="whitespace-pre-wrap">
                    {formatData(log.data)}
                  </pre>
                </td>
              </tr>
            ))}
            {logs.length === 0 && !loading && (
              <tr>
                <td colSpan="4" className="p-4 text-center text-gray-500">
                  No logs found. Try adjusting your search criteria.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default LogSearch;