import React, { useState, useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Polyline,
  Tooltip,
  useMap,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// ---------- ICONS ----------
const vehicleIcon = new L.DivIcon({
  html: "🚗",
  className: "vehicle-icon",
  iconSize: [36, 36],
});

const employeeIcon = new L.DivIcon({
  html: "📍",
  className: "employee-icon",
  iconSize: [28, 28],
});

const factoryIcon = new L.DivIcon({
  html: "🏭",
  className: "factory-icon",
  iconSize: [34, 34],
});

// ---------- AUTO FIT ALL ROUTES ----------
function FitAllRoutes({ routes, isOptimized }) {
  const map = useMap();

  useEffect(() => {
    map.invalidateSize();

    if (!isOptimized || !routes || routes.length === 0) return;

    const allPoints = routes
      .filter((route) => route.path && route.path.length > 0)
      .flatMap((route) => route.path);

    if (allPoints.length > 0) {
      const bounds = L.latLngBounds(allPoints);
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [routes, isOptimized, map]);

  return null;
}

// ---------- MAIN MAP ----------
function MapView({ routes, isOptimized }) {
  const [activeRoute, setActiveRoute] = useState(null);

  const defaultCenter = [12.9716, 77.5946];

  useEffect(() => {
    if (routes && routes.length > 0) {
      const firstRouteWithPath = routes.find((r) => r.path && r.path.length > 0);
      if (firstRouteWithPath) {
        setActiveRoute(firstRouteWithPath.id);
      }
    }
  }, [routes]);

  return (
    <div className="map-shell">
      <MapContainer
        center={defaultCenter}
        zoom={12}
        className="leaflet-container custom-map"
        zoomControl={true}
      >
        {/* Lighter map tiles for better route visibility */}
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; OpenStreetMap contributors &copy; CARTO'
        />

        <FitAllRoutes routes={routes} isOptimized={isOptimized} />

        {/* ROUTES */}
        {isOptimized &&
          routes &&
          routes.map((route, idx) => {
            const isActive = activeRoute === route.id;

            return (
              <React.Fragment key={route.id || idx}>
                {route.path && route.path.length > 0 && (
                  <Polyline
                    positions={route.path}
                    pathOptions={{
                      color: route.color,
                      weight: isActive ? 7 : 5,
                      opacity: isActive ? 1 : 0.55,
                    }}
                    eventHandlers={{
                      click: () => setActiveRoute(route.id),
                    }}
                  />
                )}

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
                      return (
                        <Marker
                          key={i}
                          position={[p.lat, p.lng]}
                          icon={employeeIcon}
                        >
                          <Tooltip permanent direction="top">
                            {p.label}
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
                            Factory
                          </Tooltip>
                        </Marker>
                      );
                    }

                    return null;
                  })}
              </React.Fragment>
            );
          })}

        {/* BEFORE OPTIMIZATION */}
        {!isOptimized && (
          <Marker position={defaultCenter} icon={factoryIcon}>
            <Tooltip permanent direction="top">
              Velora HQ
            </Tooltip>
          </Marker>
        )}
      </MapContainer>
    </div>
  );
}

export default MapView;