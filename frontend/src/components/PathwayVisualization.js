import React, { useState } from 'react';
import { ChevronRight, Activity, Pill, Stethoscope, Beaker, AlertCircle, TrendingUp, GitBranch } from 'lucide-react';

const PathwayVisualization = ({ pathwayData, predictions }) => {
  const [selectedPath, setSelectedPath] = useState(0);
  const [hoveredEvent, setHoveredEvent] = useState(null);

  // Color scheme for different code systems
  const codeColors = {
    'SNOMED': '#10B981', // Green
    'RxNorm': '#8B5CF6', // Purple
    'CPT4': '#F59E0B', // Amber
    'LOINC': '#3B82F6', // Blue
    'Unknown': '#6B7280' // Gray
  };

  const getEventIcon = (system) => {
    switch(system) {
      case 'SNOMED': return <Stethoscope className="w-4 h-4" />;
      case 'RxNorm': return <Pill className="w-4 h-4" />;
      case 'CPT4': return <Activity className="w-4 h-4" />;
      case 'LOINC': return <Beaker className="w-4 h-4" />;
      default: return <AlertCircle className="w-4 h-4" />;
    }
  };

  const getEventTypeDisplay = (type) => {
    const typeMap = {
      'condition_occurrence': 'Diagnosis',
      'drug_exposure': 'Medication',
      'procedure_occurrence': 'Procedure',
      'measurement': 'Lab Test',
      'observation': 'Observation'
    };
    return typeMap[type] || type;
  };

  if (!pathwayData || !predictions) {
    return <div>No data available</div>;
  }

  const { initial_patient, pathways, total_paths, paths_with_diagnosis } = pathwayData;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Clinical Pathway Prediction</h1>
          <div className="mt-4 flex justify-center gap-6 text-sm">
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Patient Timeline */}
          <div className="bg-white rounded-2xl shadow-xl p-6">
            <div className="flex items-center mb-4">
              <div className="bg-purple-100 p-2 rounded-lg mr-3">
                <Activity className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-800">Initial Patient State</h2>
                <p className="text-sm text-gray-500">Starting Conditions</p>
              </div>
            </div>

            <div className="space-y-3">
              {initial_patient.map((event, idx) => (
                <div
                  key={idx}
                  className="flex items-center p-3 rounded-lg border-2 transition-all hover:shadow-md"
                  style={{ 
                    borderColor: codeColors[event.system],
                    backgroundColor: `${codeColors[event.system]}10`
                  }}
                >
                  <div 
                    className="p-2 rounded-lg mr-3"
                    style={{ backgroundColor: `${codeColors[event.system]}30` }}
                  >
                    {getEventIcon(event.system)}
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold text-gray-700">

                      {event.name === event.code ?getEventTypeDisplay(event.omop_table) : event.name}

                    </p>
                    <p className="text-xs text-gray-500">{event.code}</p>
                  </div>
                </div>
              ))}
            </div>

            {/* Legend */}
            <div className="mt-6 pt-4 border-t">
              <p className="text-sm font-semibold text-gray-600 mb-2">Code Systems</p>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(codeColors).filter(([key]) => key !== 'Unknown').map(([system, color]) => (
                  <div key={system} className="flex items-center">
                    <div 
                      className="w-3 h-3 rounded-full mr-2"
                      style={{ backgroundColor: color }}
                    />
                    <span className="text-xs text-gray-600">{system}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Branching Paths Visualization */}
          <div className="bg-white rounded-2xl shadow-xl p-6">
            <div className="flex items-center mb-4">
              <div className="bg-blue-100 p-2 rounded-lg mr-3">
                <GitBranch className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-800">Simulated Pathways</h2>
                <p className="text-sm text-gray-500">{pathways.length} Branches Generated</p>
              </div>
            </div>

            <div className="space-y-2 max-h-96 overflow-y-auto">
              {pathways.map((path, pathIdx) => (
                <div
                  key={path.id}
                  className={`p-3 rounded-lg border-2 cursor-pointer transition-all ${
                    selectedPath === pathIdx 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setSelectedPath(pathIdx)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-semibold text-gray-700">{path.id}</span>
                    {path.diagnosis_found && (
                      <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                        Diagnosis
                      </span>
                    )}
                    <ChevronRight className="w-4 h-4 text-gray-400" />
                  </div>
                  <div className="flex gap-1">
                    {path.steps.map((step, stepIdx) => (
                      <div
                        key={stepIdx}
                        className="h-6 flex-1 rounded transition-all hover:opacity-80"
                        style={{ backgroundColor: codeColors[step.system] }}
                        onMouseEnter={() => setHoveredEvent(step)}
                        onMouseLeave={() => setHoveredEvent(null)}
                        title={`${step.code} (${(step.probability * 100).toFixed(1)}%)`}
                      />
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {hoveredEvent && (
              <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                <p className="text-sm font-semibold text-gray-700">
                  {getEventTypeDisplay(hoveredEvent.type)}
                </p>
                <p className="text-xs text-gray-600">{hoveredEvent.token}</p>
                <p className="text-xs text-gray-500">
                  Probability: {(hoveredEvent.probability * 100).toFixed(1)}%
                </p>
              </div>
            )}
          </div>

          {/* Predictions Panel */}
          <div className="bg-white rounded-2xl shadow-xl p-6">
            <div className="flex items-center mb-4">
              <div className="bg-green-100 p-2 rounded-lg mr-3">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-800">Top Predictions</h2>
                <p className="text-sm text-gray-500">Aggregated Probabilities</p>
              </div>
            </div>

            <div className="space-y-3">
              {predictions.map((prediction, idx) => {
                const color = codeColors[prediction.system];
                return (
                  <div key = {idx} className="relative">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-700">
                        {prediction.name}
                      </span>
                      <span className="text-sm font-bold" style={{ color }}>
                        {prediction.probability}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="h-2 rounded-full transition-all duration-500"
                        style={{
                          width: `${Math.min(prediction.probability * 2, 100)}%`,
                          backgroundColor: color
                        }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Selected Path Details */}
        {selectedPath !== null && pathways[selectedPath] && (
          <div className="mt-6 bg-white rounded-2xl shadow-xl p-6">
            <h3 className="text-lg font-bold text-gray-800 mb-4">
              Path Details: {pathways[selectedPath].id}
              {pathways[selectedPath].parent_id && (
                <span className="text-sm font-normal text-gray-500 ml-2">
                  (Parent: {pathways[selectedPath].parent_id})
                </span>
              )}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {pathways[selectedPath].steps.map((step, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-lg border-2"
                  style={{
                    borderColor: codeColors[step.system],
                    backgroundColor: `${codeColors[step.system]}10`
                  }}
                >
                  <div className="flex items-center mb-2">
                    {getEventIcon(step.system)}
                    <span className="ml-2 text-sm font-semibold text-gray-700">Step {idx + 1}</span>
                  </div>
                  <p className="text-sm font-medium text-gray-800">
                    {step.code}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">{step.token}</p>
                  <div className="mt-2 pt-2 border-t border-gray-200">
                    <p className="text-xs text-gray-600">
                      Probability: <span className="font-bold">{(step.probability * 100).toFixed(1)}%</span>
                    </p>
                    <p className="text-xs text-gray-600">
                      Type: <span className="font-bold">{getEventTypeDisplay(step.type)}</span>
                    </p>
                  </div>
                  {step.type === 'condition_occurrence' && (
                    <div className="mt-2">
                      <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                        DIAGNOSIS
                      </span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PathwayVisualization;