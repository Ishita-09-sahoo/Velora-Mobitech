import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import excelParser from '../utils/excelParser.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function runCppOptimizer(demandBuffer, supplyBuffer) {
  // 1. Parse Excel files
  const employees = excelParser(demandBuffer);
  const vehicles = excelParser(supplyBuffer);

  // 2. Build input data
  const inputData = {
    employees: employees.map(e => ({
      user_id: e.user_id,
      priority_level: parseInt(e.priority_level),
      pickup_lat: parseFloat(e.pickup_lat),
      pickup_lng: parseFloat(e.pickup_lng),
      dest_lat: parseFloat(e.dest_lat),
      dest_lng: parseFloat(e.dest_lng),
      vehicle_preference: e.vehicle_preference,
      sharing_pref: e.sharing_pref
    })),
    vehicles: vehicles.map(v => ({
      vehicle_id: v.vehicle_id,
      capacity: parseInt(v.capacity),
      cost_per_km: parseFloat(v.cost_per_km),
      avg_speed: parseFloat(v.avg_speed),
      current_lat: parseFloat(v.current_lat),
      current_lng: parseFloat(v.current_lng)
    })),
    baseline_rate_per_km: 15.0
  };

  console.log(`📤 Sending ${inputData.employees.length} employees, ${inputData.vehicles.length} vehicles to C++`);

  // 3. C++ executable path
  const cppPath = path.join(__dirname, '..', 'cpp', 'output', 'vrp_solver.exe');
  console.log(`🚀 Spawning: ${cppPath}`);

  return new Promise((resolve, reject) => {
    const cppProcess = spawn(cppPath, [], {
      stdio: ['pipe', 'pipe', 'pipe'],
      timeout: 60000,
      shell: true
    });

    // Send input
    cppProcess.stdin.write(JSON.stringify(inputData));
    cppProcess.stdin.end();

    let stdoutData = '';
    let stderrData = '';

    cppProcess.stdout.on('data', (chunk) => {
      stdoutData += chunk.toString();
    });

    cppProcess.stderr.on('data', (chunk) => {
      stderrData += chunk.toString();
    });

    cppProcess.on('close', (code) => {
      console.log(`✅ C++ exited (code: ${code})`);
      
      if (code === 0 && stdoutData.trim()) {
        try {
          const solution = JSON.parse(stdoutData);
          resolve(solution);
        } catch (parseErr) {
          reject(new Error(`JSON parse failed: ${parseErr.message}`));
        }
      } else {
        reject(new Error(`C++ failed (code ${code}):\n${stderrData}`));
      }
    });

    cppProcess.on('error', (err) => {
      reject(new Error(`Spawn failed: ${err.message}`));
    });
  });
}

export default runCppOptimizer;