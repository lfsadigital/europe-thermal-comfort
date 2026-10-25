// Real public deployment and real CAMS history; no fixtures or request routing.
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('playwright');
const origin='https://comfy.lfsadigital.com';
async function summary(lat,lon,period){
 const url=new URL('/api/air-quality/v1',origin);for(const [k,v]of Object.entries({lat,lon,period}))url.searchParams.set(k,v);
 for(let i=0;i<10;i++){
  const r=await fetch(url,{signal:AbortSignal.timeout(145000)});
  if(r.status===503&&i<9){await new Promise(resolve=>setTimeout(resolve,2000));continue;}
  if(!r.ok)throw Error('Published AQI HTTP '+r.status+': '+await r.text());assert.match(r.headers.get('content-type'),/application\/json/);
  const data=await r.json();assert.equal(data.version,1);assert(data.aqi.eligible);assert(Number.isFinite(data.aqi.median));assert.equal(data.aqi.expected,period==='mean'?26304:period==='2024'?8784:8760);return data;
 }
}
const real=[];
for(const [name,lat,lon,period]of [['Lisbon',38.72,-9.14,'mean'],['New Delhi',28.61,77.21,'2025']]){
 const s=await summary(lat,lon,period);real.push({name,period,medianAQI:s.aqi.median,hours:s.aqi.count,expected:s.aqi.expected,passes100:s.aqi.median<=100});
}
assert(real[0].passes100,'Lisbon reference must qualify at 100');assert(!real[1].passes100,'Polluted reference must be excluded at 100');
assert.equal((await fetch(origin+'/api/air-quality/v1?lat=&lon=0&period=2025')).status,400);
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(origin+'/?region=europe&aqi=1&aqmax=100&aqiyear=2025',{waitUntil:'domcontentloaded',timeout:90000});
 await page.waitForFunction(()=>window.ComfyDays&&!ComfyDays.state.busy,{},{timeout:120000});
 await page.waitForFunction(()=>{const f=ComfyDays.airQuality.filter;return !f.busy&&f.passed>=10&&f.failures.size===0;},{},{timeout:240000});
 await page.waitForTimeout(100);
 const live=await page.evaluate(async()=>{
  const aq=ComfyDays.airQuality;window.__liveOriginal=[ComfyDays.state.scoreValues,ComfyDays.state.dayValues];
  const polluted=await aq.filter.load(28.61,77.21,'2025');
  return {rows:ComfyDays.discovery.rows.map(e=>({name:e.name,aqi:aq.filter.summary(e).aqi.median,score:ComfyDays.state.scoreValues[e.index]})),raster:ComfyDays.navigation.map.getLayoutProperty('climate','visibility'),pollutedMedian:polluted.aqi.median,pollutedAllowed:aq.filter.allows({place:[0,'New Delhi',28.61,77.21]}),markersPass:ComfyDays.cityMap.features.every(f=>aq.filter.allows(ComfyDays.cityMap.entries.get(f.properties.id)))};
 });
 assert.equal(live.rows.length,10);assert(live.rows.every(r=>r.aqi<=100));assert.equal(live.raster,'none');assert(!live.pollutedAllowed);assert(live.markersPass);
 await page.evaluate(()=>ComfyDays.ui.open('weather'));await page.locator('#aq-enabled').uncheck();await page.locator('#apply').click();
 assert(await page.evaluate(()=>ComfyDays.state.scoreValues===window.__liveOriginal[0]&&ComfyDays.state.dayValues===window.__liveOriginal[1]));assert.equal(await page.evaluate(()=>ComfyDays.navigation.map.getLayoutProperty('climate','visibility')),'visible');assert.deepEqual(errors,[]);
 console.log(JSON.stringify({result:'PASS',synthetic:false,origin,source:'Open-Meteo/CAMS global through published Worker',real,browser:live,checks:['published JSON source route','real clean/polluted threshold outcomes','public browser verified Top 10','only qualified map points','climate shading hidden/restored','exact Confi10 array identity','zero page errors']},null,2));
}finally{await browser.close();}
