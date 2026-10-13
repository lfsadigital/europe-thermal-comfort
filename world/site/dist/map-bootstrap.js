import * as maplibregl from './vendor/maplibre-gl.mjs';
window.maplibregl=maplibregl;
try {
  await import('./geo-map.js?v=15');
  await import('./discovery.js?v=14');
  await import('./city-filters.js?v=15');
  await import('./monthly-charts.js?v=15');
  await import('./city-map.js?v=15');
  await import('./app.js?v=15');
} catch (error) {
  document.getElementById('status').textContent='The interactive map could not start. Enable WebGL and reload, or try another browser.';
  document.getElementById('map-hud').textContent='Map unavailable';
  document.getElementById('export').disabled=true;
  document.getElementById('apply').disabled=true;
  console.error('Comfy Days map startup failed:',error);
}
