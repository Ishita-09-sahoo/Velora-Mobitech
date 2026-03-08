import React, { useState, useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Polyline,
  Tooltip,
  useMap
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// ---------- ICONS ----------

const vehicleIcon = new L.DivIcon({
  html: "🚗",
  className: "vehicle-icon",
  iconSize: [40, 40]
});

const employeeIcon = new L.DivIcon({
  html: "📍",
  className: "employee-icon",
  iconSize: [30, 30]
});

const factoryIcon = new L.DivIcon({
  html: "🏭",
  className: "factory-icon",
  iconSize: [35, 35]
});

// ---------- AUTO ZOOM COMPONENT ----------

function AutoZoom({ route }) {
  const map = useMap();

  useEffect(() => {
    if (!route || route.path.length === 0) return;

    const bounds = L.latLngBounds(route.path);
    map.fitBounds(bounds, { padding: [60, 60] });

  }, [route, map]);

  return null;
}

// ---------- MAIN MAP ----------

function MapView({ routes, isOptimized }) {

  const [activeRoute, setActiveRoute] = useState(null);

  const defaultCenter = [12.9716, 77.5946];

  const selectedRoute =
    routes && routes.find(r => r.id === activeRoute);

  return (
    <MapContainer
      center={defaultCenter}
      zoom={12}
      style={{ height: "100%", width: "100%", background: "#0f172a" }}
    >

      {/* MAP TILE */}
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {/* AUTO ZOOM */}
      {selectedRoute && <AutoZoom route={selectedRoute} />}

      {/* ROUTES */}
      {isOptimized &&
        routes &&
        routes.map((route, idx) => {

          const isActive = activeRoute === route.id;

          return (
            <React.Fragment key={route.id || idx}>

              {/* ROUTE LINE */}
              <Polyline
                positions={route.path}
                pathOptions={{
                  color: route.color,
                  weight: isActive ? 7 : 4,
                  opacity: isActive ? 1 : 0.35
                }}
                eventHandlers={{
                  click: () => setActiveRoute(route.id)
                }}
              />

              {/* SHOW MARKERS ONLY FOR ACTIVE ROUTE */}
              {isActive &&
                route.points &&
                route.points.map((p, i) => {

                  if (p.type === "vehicle_start") {
                    return (
                      <Marker
                        key={i}
                        position={[p.lat, p.lng]}
                        icon={vehicleIcon}
                      >
                        <Tooltip permanent direction="top">
                          🚗 {route.id}
                        </Tooltip>
                      </Marker>
                    );
                  }

                  if (p.type === "pickup") {

                    const empId = p.label.replace("Employee ", "");

                    return (
                      <Marker
                        key={i}
                        position={[p.lat, p.lng]}
                        icon={employeeIcon}
                      >
                        <Tooltip permanent direction="top">
                          {empId}
                        </Tooltip>
                      </Marker>
                    );
                  }

                  if (p.type === "factory") {
                    return (
                      <Marker
                        key={i}
                        position={[p.lat, p.lng]}
                        icon={factoryIcon}
                      >
                        <Tooltip permanent direction="top">
                          🏭 Factory
                        </Tooltip>
                      </Marker>
                    );
                  }

                  return null;
                })}
            </React.Fragment>
          );
        })}

      {/* DEFAULT MARKER BEFORE OPTIMIZATION */}
      {!isOptimized && (
        <Marker position={defaultCenter}>
          <Tooltip permanent>Velora HQ</Tooltip>
        </Marker>
      )}
    </MapContainer>
  );
}

export default MapView;