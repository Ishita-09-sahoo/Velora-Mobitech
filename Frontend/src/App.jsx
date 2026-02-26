import React, { useState } from "react";
import "./styles/main.css";
import "./styles/Dashboard.css";
import FileUpload from "./components/FileUpload";
import MapView from "./components/MapView";

function App() {
  const [file, setFile] = useState(null);
  const [isOptimized, setIsOptimized] = useState(false);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleRunOptimization = async () => {
    if (!file) {
      return alert("Please upload file first!");
    }

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const API_URL = import.meta.env.VITE_API_URL;

      const response = await fetch(`${API_URL}/api/optimise`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(`Server Error: ${errText}`);
      }

      const data = await response.json();
      console.log("Optimization response:", data);

      // 3. Map Backend Data to Frontend Format
      const mappedResults = mapBackendDataToFrontend(data);
      setResults(mappedResults);
      setIsOptimized(true);
    } catch (error) {
      console.error("Optimization error:", error);
      alert(`Optimization failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const mapBackendDataToFrontend = (backendData) => {
    const colors = ["#ef4444", "#3b82f6", "#10b981", "#f59e0b", "#8b5cf6"];

    return {
      baselineCost: 0,
      optimizedCost: backendData.vehicles.reduce((sum, v) => sum + v.cost, 0),
      savingsPct: 0,
      savingsAbs: 0,
      baselineTime: "N/A",
      optimizedTime: "N/A",

      assignments: backendData.vehicles.map((v, index) => ({
        id: v.vehicle_id,
        type: "Fleet Vehicle",
        color: colors[index % colors.length],
        capacity: `${v.route.length} stops`,
        routeDesc: `${v.distance_km} km Route`,

        stops: v.route.map((empId, i) => ({
          time: i === 0 ? "Start" : "Stop",
          loc: `Employee ${empId}`,
          type: "pickup",
        })),
      })),

      routes: backendData.vehicles.map((v, index) => ({
        id: v.vehicle_id,
        color: colors[index % colors.length],
        path: [], // map polyline not available yet
      })),
    };
  };

  return (
    <div className="dashboard-container">
      <header className="header">
        <div className="logo">
          <h1>
            VELORA <span className="blue-text">MOBITECH</span>
          </h1>
        </div>

        {isOptimized && results && (
          <div className="header-results">
            <div className="stat-group">
              <div className="header-stat">Base: ₹{results.baselineCost}</div>
              <div className="header-stat">Opt: ₹{results.optimizedCost}</div>
              <div className="header-stat savings-text">
                Save: {results.savingsPct}%
              </div>
            </div>
            <div className="stat-group time-group">
              <div className="header-stat highlight-time">
                Time: {results.optimizedTime}m
              </div>
            </div>
          </div>
        )}
      </header>

      <aside className="sidebar left-panel">
        <div className="input-group">
          <h3>Input Data</h3>
          <div className="inner-div">
            <FileUpload onFileSelect={setFile} />
          </div>
        </div>

        <div className="action-area">
          <button
            className="optimize-btn"
            onClick={handleRunOptimization}
            disabled={loading}
            style={{
              opacity: loading ? 0.7 : 1,
              cursor: loading ? "wait" : "pointer",
            }}
          >
            {loading
              ? "Optimizing..."
              : isOptimized
                ? "Re-Run Optimization"
                : "Run Optimization"}
          </button>
        </div>
      </aside>

      <main className="map-section">
        <MapView
          routes={results ? results.routes : []}
          isOptimized={isOptimized}
        />
      </main>

      {isOptimized && results && (
        <aside className="assignments-sidebar">
          <h3>Assignments ({results.assignments.length})</h3>
          <div className="vehicle-list">
            {results.assignments.map((veh) => (
              <div
                key={veh.id}
                className="vehicle-card"
                style={{ borderLeft: `4px solid ${veh.color}` }}
              >
                <div className="card-header">
                  <span className="veh-id">{veh.id}</span>
                  <span className="capacity-badge">{veh.capacity}</span>
                </div>
                <p className="route-name">{veh.routeDesc}</p>
                <div className="timeline">
                  {veh.stops.map((stop, i) => (
                    <div key={i} className="timeline-item">
                      <span className="time">{stop.time}</span>
                      <span className={`stop-name ${stop.type}`}>
                        {stop.loc}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </aside>
      )}
    </div>
  );
}

export default App;
