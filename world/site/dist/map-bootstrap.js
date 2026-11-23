import * as maplibregl from './vendor/maplibre-gl.mjs';
window.maplibregl=maplibregl;
try {
  await import('./workspace-ui.js?v=45');
  await import('./geo-map.js?v=42');
  await import('./discovery.js?v=42');
  await import('./epi-budget.js?v=23');
  await import('./city-filters.js?v=42');
  await import('./urban-density.js?v=24');
  await import('./climate-result.js?v=40');
  await import('./monthly-charts.js?v=45');
  await import('./city-map.js?v=40');
  await import('./air-quality.js?v=42');
  await import('./app.js?v=46');
} catch (error) {
  document.getElementById('status').textContent='The interactive map could not start. Enable WebGL and reload, or try another browser.';
  document.getElementById('map-hud').textContent='Map unavailable';
  document.getElementById('export').disabled=true;
  document.getElementById('apply').disabled=true;
  console.error('Comfy Days map startup failed:',error);
}
