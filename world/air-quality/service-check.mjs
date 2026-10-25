import assert from 'node:assert/strict';
import {createAirQualityService} from '../query-service/air-quality-service.mjs';
import fixture from './fixture.cjs';
const request=(query='lat=38.72&lon=-9.14&period=mean')=>new Request('https://local/api/air-quality/v1?'+query);
const entries=new Map(),cache={async match(key){return entries.get(key.url)?.clone();},async put(key,response){entries.set(key.url,response.clone());}};
let calls=0;
const service=createAirQualityService({cache,fetcher:async url=>{calls++;assert.equal(url.hostname,'air-quality-api.open-meteo.com');assert.equal(url.searchParams.get('domains'),'cams_global');assert.equal(url.searchParams.get('timezone'),'UTC');return new Response(JSON.stringify(fixture(Number(url.searchParams.get('start_date').slice(0,4)))));}});
for(const q of ['lat=&lon=0','lat=91&lon=0','lat=0&lon=-181','lat=NaN&lon=0','lat=1&lon=2&period=2020','lat=1','lon=1'])assert.equal((await service.fetch(request(q))).status,400);
assert.equal((await service.fetch(new Request('https://local/api/air-quality/v1',{method:'POST'}))).status,405);
let response=await service.fetch(request()),data=await response.json();assert.equal(response.status,200);assert.equal(data.aqi.expected,26304);assert.equal(data.aqi.median,42);assert(data.aqi.eligible);assert.equal(calls,3);assert(!JSON.stringify(data).includes('hourly_units'));
await service.fetch(request());assert.equal(calls,3,'Repeated history must use compact cache');await service.fetch(request('lat=38.72000&lon=-9.14000&period=mean'));assert.equal(calls,3,'Canonical coordinates share cache');
response=await service.fetch(request('lat=38.72&lon=-9.14&period=2024'));assert.equal((await response.json()).aqi.expected,8784);assert.equal(calls,4,'Periods must not share entries');
let badCalls=0;const bad=createAirQualityService({cache,fetcher:async()=>{badCalls++;return new Response('Outage',{status:429});}});for(let i=0;i<2;i++){const r=await bad.fetch(request('lat=12&lon=14&period=2025'));assert.equal(r.status,502);assert.equal(r.headers.get('Cache-Control'),'no-store');}assert.equal(badCalls,2,'Source failures must remain retryable');
const malformed=createAirQualityService({fetcher:async()=>{const d=fixture(2025);d.hourly.time.reverse();return Response.json(d);}});assert.equal((await malformed.fetch(request('lat=1&lon=2&period=2025'))).status,502);
const missing=createAirQualityService({fetcher:async()=>{const d=fixture(2025);d.hourly.us_aqi.fill(null,0,100);return Response.json(d);}});data=await (await missing.fetch(request('lat=1&lon=2&period=2025'))).json();assert(!data.aqi.eligible);assert(data.pm.eligible);
// At most two independent request-owned source jobs; no cross-request promise.
const gates=[];const activeJobs=new Map(),concurrent=createAirQualityService({activeJobs,fetcher:()=>new Promise(resolve=>gates.push(()=>resolve(Response.json(fixture(2025)))))});
const a=concurrent.fetch(request('lat=1&lon=2&period=2025')),b=concurrent.fetch(request('lat=3&lon=4&period=2025'));await Promise.resolve();assert.equal(activeJobs.size,2);assert.equal((await concurrent.fetch(request('lat=5&lon=6&period=2025'))).status,503);assert.equal((await concurrent.fetch(request('lat=1&lon=2&period=2025'))).status,503);gates.splice(0).forEach(release=>release());assert.equal((await a).status,200);assert.equal((await b).status,200);assert.equal(activeJobs.size,0);
console.log('PASS: AQI service validation, exact years/leap counts, compact cache, period/coordinate isolation, noncached source failures, missing coverage and bounded request-owned concurrency.');
