import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import fixture from './fixture.cjs';
const require=createRequire(import.meta.url),{chromium}=require('playwright');
const here=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(here,'../site/dist'),out=path.resolve(here,'../../.impeccable/review');
const mime={'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.woff2':'font/woff2','.png':'image/png'};
let sourceCalls=0,failedPoint=null,slow=false;
const grade=(lat,lon)=>[50,100,151][Math.abs(Math.round(lon*100))%3];
async function upstream(url){
 sourceCalls++;const lat=Number(url.searchParams.get('latitude')),lon=Number(url.searchParams.get('longitude'));
 if(failedPoint&&Math.abs(failedPoint[0]-lat)<.0001&&Math.abs(failedPoint[1]-lon)<.0001)return {status:502,body:'Fixture source outage'};
 await new Promise(r=>setTimeout(r,slow?200:5));
 const first=Number(url.searchParams.get('start_date').slice(0,4)),last=Number(url.searchParams.get('end_date').slice(0,4)),records=[];
 for(let year=first;year<=last;year++){const d=fixture(year,grade(lat,lon));d.latitude=lat;d.longitude=lon;if(lat===12.5)d.hourly.us_aqi.fill(null,0,100);records.push(d);}
 return {json:{...records[0],hourly:Object.fromEntries(['time','us_aqi','pm2_5'].map(k=>[k,records.flatMap(r=>r.hourly[k])]))}};
}
const server=http.createServer(async(req,res)=>{
 try{const u=new URL(req.url,'http://localhost');
 const file=path.resolve(root,'.'+(u.pathname==='/'?'/index.html':u.pathname));if(!file.startsWith(root+'/'))throw Error('Path');const data=fs.readFileSync(file);res.setHeader('Content-Type',mime[path.extname(file)]||'application/octet-stream');res.end(data);
 }catch{res.writeHead(404);res.end();}
});
await new Promise(r=>server.listen(0,'127.0.0.1',r));const base=`http://127.0.0.1:${server.address().port}`;
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'}),errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.route('**/*',async route=>{const u=new URL(route.request().url());if(u.hostname==='air-quality-api.open-meteo.com'){const data=await upstream(u);return route.fulfill({...data,headers:{'Access-Control-Allow-Origin':'*','Content-Type':'application/json'}}).catch(()=>{});}if(u.pathname.endsWith('basemap-style.json'))return route.fulfill({json:{version:8,sources:{},layers:[{id:'background',type:'background',paint:{'background-color':'#eef2f8'}}]}});if(u.hostname!=='127.0.0.1')return route.abort();return route.continue();});
const ready=()=>page.waitForFunction(()=>window.ComfyDays&&!ComfyDays.state.busy);
const settled=()=>page.waitForFunction(()=>{const f=ComfyDays.airQuality.filter;return !f.busy&&(f.passed>=10||f.complete||f.checked>=f.limit);},{},{timeout:90000});
const settings=async({enabled=true,max,period}={})=>{await page.evaluate(()=>ComfyDays.ui.open('weather'));await page.locator('#aq-enabled').setChecked(enabled);if(max)await page.locator('#aq-max').selectOption(String(max));if(period)await page.locator('#aq-period').selectOption(period);await page.locator('#apply').click();};
try{
 await page.goto(base);await ready();await page.evaluate(()=>ComfyDays.airQuality.filter.minimumInterval=0);assert.equal(sourceCalls,0);assert(!await page.locator('#aq-enabled').isChecked());
 const baseline=await page.evaluate(()=>{window.__originalArrays=[ComfyDays.state.scoreValues,ComfyDays.state.dayValues];window.__originalParams=JSON.stringify(ComfyDays.state.params);return ComfyDays.discovery.rows.map(e=>e.place[0]);});
 await page.evaluate(()=>ComfyDays.ui.open('weather'));await page.locator('#aq-enabled').check();await page.locator('#aq-max').selectOption('100');assert.equal(sourceCalls,0,'Draft AQI must not query');assert.equal(await page.evaluate(()=>ComfyDays.navigation.map.getLayoutProperty('climate','visibility')),'visible');await page.locator('#apply').click();await settled();await page.waitForTimeout(100);
 assert.equal(await page.evaluate(()=>ComfyDays.navigation.map.getLayoutProperty('climate','visibility')),'none');
 assert(await page.evaluate(()=>ComfyDays.discovery.rows.length===10&&ComfyDays.discovery.rows.every(e=>ComfyDays.airQuality.filter.allows(e))));
 assert(await page.evaluate(()=>ComfyDays.cityMap.features.every(f=>ComfyDays.airQuality.filter.allows(ComfyDays.cityMap.entries.get(f.properties.id)))));
 assert(await page.evaluate(()=>ComfyDays.state.scoreValues===window.__originalArrays[0]&&ComfyDays.state.dayValues===window.__originalArrays[1]&&Object.entries(ComfyDays.state.params).every(([k,v])=>JSON.parse(window.__originalParams)[k]===v)));
 assert.equal(new URL(page.url()).searchParams.get('aqmax'),'100');
 const checked=await page.evaluate(()=>ComfyDays.airQuality.filter.checked);assert(checked>=10&&checked<=40);
 // Inclusive ceiling: fixture cities at exactly 100 pass; 151 never passes.
 const values=await page.evaluate(()=>ComfyDays.discovery.rows.map(e=>ComfyDays.airQuality.filter.summary(e).aqi.median));assert(values.every(v=>v<=100));assert(values.includes(100));
 await settings({max:500});await settled();await page.waitForTimeout(100);assert.deepEqual(await page.evaluate(()=>ComfyDays.discovery.rows.map(e=>e.place[0])),baseline,'Relaxed ceiling must recover original top cities');
 await settings({max:50});await settled();await page.waitForTimeout(100);if(await page.locator('#aq-filter-more').isVisible()){await page.locator('#aq-filter-more').click();await settled();}assert(await page.evaluate(()=>ComfyDays.discovery.rows.every(e=>ComfyDays.airQuality.filter.summary(e).aqi.median===50)));
 // Search/inspection can still show an excluded point's unchanged climate.
 await page.evaluate(()=>ComfyDays.inspect(12.5,22));await page.locator('#aq-results').waitFor({state:'visible'});assert.match(await page.locator('#aq-status').textContent(),/Insufficient coverage/);assert.match(await page.locator('#aq-results').textContent(),/insufficient historical coverage/);assert(!await page.evaluate(()=>ComfyDays.airQuality.filter.allows({place:[0,'Missing',12.5,22]})));
 fs.mkdirSync(out,{recursive:true});await page.evaluate(()=>{const p=document.createElement('p');p.textContent='QA · synthetic pollution source; real climate preset and filter/backend';p.style.cssText='font-size:14px;padding:12px 24px';document.querySelector('.workspace').prepend(p);});
 for(const [name,width,height]of [['desktop',1440,1000],['mobile',390,844],['compact',320,740],['tablet',768,1024]]){
  await page.setViewportSize({width,height});await page.evaluate(()=>ComfyDays.ui.open('weather'));await page.locator('#aq-max').scrollIntoViewIfNeeded();assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert((await page.locator('#aq-max').boundingBox()).height>=44);assert((await page.locator('#apply').boundingBox()).height>=44);await page.screenshot({path:path.join(out,`aq-filter-${name}.png`)});await page.locator('#apply').click();
 }
 // Cold-period source failure cannot silently admit a high-ranked candidate.
 failedPoint=await page.evaluate(()=>{const e=ComfyDays.discovery.candidates().sort((a,b)=>ComfyDays.state.scoreValues[b.index]-ComfyDays.state.scoreValues[a.index]||ComfyDays.state.dayValues[b.index]-ComfyDays.state.dayValues[a.index]||b.population-a.population)[0];return[e.place[2],e.place[3]];});
 await settings({max:500,period:'2024'});await settled();await page.locator('#aq-filter-retry').waitFor({state:'visible'});assert.match(await page.locator('#aq-map-status').textContent(),/failed/);assert(await page.evaluate(()=>ComfyDays.discovery.rows.every(e=>ComfyDays.airQuality.filter.allows(e))));failedPoint=null;await page.locator('#aq-filter-retry').click();await settled();await page.waitForFunction(()=>ComfyDays.airQuality.filter.failures.size===0);
 // Changes during pending requests cannot restore an obsolete filter.
 slow=true;await settings({period:'2023'});await settings({enabled:false});assert.equal(await page.evaluate(()=>ComfyDays.navigation.map.getLayoutProperty('climate','visibility')),'visible');await page.waitForTimeout(500);assert(!await page.locator('#aq-enabled').isChecked());assert.deepEqual(await page.evaluate(()=>ComfyDays.discovery.rows.map(e=>e.place[0])),baseline);slow=false;
 await page.goto(base+'/?aqi=1&aqmax=50&aqiyear=2025');await ready();await page.evaluate(()=>{ComfyDays.airQuality.filter.minimumInterval=0;ComfyDays.airQuality.filter.nextSourceAt=0;});await settled();assert.equal(await page.locator('#aq-max').inputValue(),'50');assert.equal(await page.locator('#aq-period').inputValue(),'2025');assert(await page.evaluate(()=>ComfyDays.discovery.rows.every(e=>ComfyDays.airQuality.filter.allows(e))));
 await page.evaluate(()=>ComfyDays.ui.open('weather'));await page.locator('#reset').click();await ready();assert(!await page.locator('#aq-enabled').isChecked());assert(await page.locator('#aq-max').isDisabled());assert(!new URL(page.url()).searchParams.has('aqmax'));assert.equal(await page.evaluate(()=>ComfyDays.navigation.map.getLayoutProperty('climate','visibility')),'visible');assert.deepEqual(errors,[]);
 console.log(JSON.stringify({result:'PASS',pipeline:'browser → synthetic public API → real validated aggregation → map/ranking filter (quota delay disabled only for fixtures)',viewports:[1440,768,390,320],checks:['off=no requests','draft/apply','inclusive ceiling','recomputed Top 10','unverified and missing excluded','map contains only confirmed matching points','climate shading restored on disable','exact Confi10 array identity and parameters','relaxed limit restores original ranking','independent period/URL','source error/retry','stale requests cannot restore old filter','44px controls/no overflow','Reset','zero page errors'],sourceCalls},null,2));
}finally{await browser.close();server.close();}
