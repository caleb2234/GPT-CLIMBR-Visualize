import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PathwayVisualization from './components/PathwayVisualization';
import './App.css';

function App() {
  const [pathwayData, setPathwayData] = useState(null);
  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch pathway data from Flask backend
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Get pathways
        const pathwaysResponse = await axios.get('http://localhost:5000/api/pathways');
        
        setPathwayData(pathwaysResponse.data);
        
        // Get predictions
        const predictionsResponse = await axios.get('http://localhost:5000/api/predictions');
        setPredictions(predictionsResponse.data.predictions);
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError(err.message);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading CLMBR model results...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center">
        <div className="text-center text-red-600">
          <p>Error loading data: {error}</p>
          <p className="text-sm mt-2">Make sure the Flask backend is running on port 5000</p>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <PathwayVisualization 
        pathwayData={pathwayData} 
        predictions={predictions}
      />
    </div>
  );
}

export default App;