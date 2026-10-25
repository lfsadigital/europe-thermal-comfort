// Small read-only real-source probe. No global import, credentials or fixtures.
const assert=require('node:assert/strict'),core=require('../site/dist/air-quality-core.js');
(async()=>{
 const results=[];
 for(const [name,latitude,longitude]of [['Lisbon',38.72,-9.14],['Miami',25.77,-80.19]]){
  const url=new URL('https://air-quality-api.open-meteo.com/v1/air-quality');
  for(const [k,v]of Object.entries({latitude,longitude,start_date:'2025-01-01',end_date:'2025-12-31',hourly:'us_aqi,pm2_5',domains:'cams_global',timezone:'UTC'}))url.searchParams.set(k,v);
  const r=await fetch(url,{signal:AbortSignal.timeout(90000)});assert(r.ok,`${name}: HTTP ${r.status}`);const data=await r.json(),s=core.aggregate([data],'2025');assert(s.aqi.eligible,`${name}: AQI coverage`);assert(s.pm.eligible,`${name}: PM2.5 coverage`);assert.equal(s.aqi.bands.reduce((a,b)=>a+b),s.aqi.count);
  results.push({name,requested:{latitude,longitude},returned:s.cells[0],aqiHours:s.aqi.count,expected:s.aqi.expected,medianAQI:s.aqi.median,meanPM25:s.pm.mean});
 }
 console.log(JSON.stringify({result:'PASS',source:'Open-Meteo / CAMS global',synthetic:false,results},null,2));
})().catch(e=>{console.error(e);process.exitCode=1;});
