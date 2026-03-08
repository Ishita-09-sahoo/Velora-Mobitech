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
  const [showEmployeeTable, setShowEmployeeTable] = useState(false);


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
      baselineCost: backendData.total_baseline_cost,
      optimizedCost: backendData.total_optimized_cost,
      savingsPct: backendData.savings_percent,
      savingsAbs: 0,
      employees: backendData.employees || [],

 assignments: backendData.vehicles.map((v, index) => ({

  id: v.vehicle_id,
  type: "Fleet Vehicle",
  color: colors[index % colors.length],
  capacity: `${v.route.length} stops`,
  routeDesc: `${v.distance_km} km Route`,

  stops: [
    ...v.route.map((emp, i) => ({
      time: emp.pickup_time,
      loc: `Employee ${emp.employee_id}`,
      type: "pickup"
    })),

    // add factory drop
    {
      time: v.drop_time,
      loc: "Factory Drop",
      type: "factory"
    }
  ]

})),

routes: backendData.vehicles.map((v, index) => ({
  id: v.vehicle_id,
  color: colors[index % colors.length],
  path: v.route_points.map(p => [p.lat, p.lng]),
  points: v.route_points
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
            
          {isOptimized && results && (
            <button
              className="employee-btn"
              onClick={() => setShowEmployeeTable(true)}
            >
              Employee Assignment
            </button>
          )}

        
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
    
      {showEmployeeTable && results && (
        <div className="employee-modal-overlay">
          <div className="employee-modal">
            <div className="employee-modal-header">
              <h2>Employees Assignment</h2>
              <button
                className="close-modal-btn"
                onClick={() => setShowEmployeeTable(false)}
              >
                ×
              </button>
            </div>

            <div className="employee-table-wrapper">
              <table className="employee-table">
                <thead>
                  <tr>
                    <th>Employee ID</th>
                    <th>Vehicle ID</th>
                    <th>Priority</th>
                    <th>Earliest Pickup</th>
                    <th>Latest Drop</th>
                    <th>Pickup Time</th>
                    <th>Drop Time</th>
                    <th>Time Taken (min)</th>
                    <th>Baseline Time (min)</th>
                  </tr>
                </thead>
                <tbody>
                  {results.employees.length > 0 ? (
                    results.employees.map((emp, index) => (
                      <tr key={`${emp.employee_id}-${index}`}>
                        <td>{emp.employee_id}</td>
                        <td>{emp.vehicle_id}</td>
                        <td>{emp.priority}</td>
                        <td>{emp.earliest_pickup}</td>
                        <td>{emp.latest_drop}</td>
                        <td>{emp.pickup_time}</td>
                        <td>{emp.drop_time}</td>
                        <td>{emp.time_taken_min}</td>
                        <td>{emp.baseline_time_min}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="9" className="no-data-cell">
                        No employee assignment data available
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
