import React, { useState } from "react";

function FileUpload({ onFileSelect }) {
  const [status, setStatus] = useState("Waiting for file...");
  const [error, setError] = useState(null);

  const handleFile = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setStatus("✓ File selected");
    setError(null);

    if (onFileSelect) {
      onFileSelect(file); // send file to App.jsx
    }
  };

  return (
    <div className="input-field-wrapper">
      <label className="input-label">
        UPLOAD EXCEL FILE
      </label>

      <input
        type="file"
        accept=".xlsx, .xls"
        onChange={handleFile}
      />

      <div style={{ marginTop: "10px", fontSize: "0.8rem" }}>
        {error ? (
          <span style={{ color: "red" }}>❌ {error}</span>
        ) : (
          <span style={{ color: "green" }}>{status}</span>
        )}
      </div>
    </div>
  );
}

export default FileUpload;