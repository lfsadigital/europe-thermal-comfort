import assert from 'node:assert/strict';
import {createService} from './service.mjs';
import {parseQuery,queryURL,calculatePart,encodePart,NODES,CHUNK_SIZE} from './query-core.mjs';
import '../site/dist/climate-result.js';
const p={lower:14,upper:30,lowenabled:true,lowmin:14,lowmax:30,rain0:4,rain1:10,rain2:20,pen1:.5,pen2:1,pen3:1.5,drymax:4,sunenabled:false,sunmin:6};
const url=queryURL('https://example.test/api/climate/v1',41,'mean',p),spec=parseQuery(url);assert.equal(spec.part,41);assert.equal(spec.params.sunmin,6);
const reordered={...p,sunmin:8};assert.equal(parseQuery(queryURL(url,41,'mean',reordered)).key,spec.key);
for(const bad of [{...p,lowenabled:false},{...p,upper:31},{...p,rain0:Infinity},{...p,rain1:-1},{...p,pen3:99},{...p,sunmin:.25},{...p,extra:'https://bad.test'}])assert.throws(()=>parseQuery(queryURL(url,41,'mean',bad)));
for(const part of [-1,42,1.5])assert.throws(()=>parseQuery(queryURL(url,part,'mean',p)));
const start=41*CHUNK_SIZE,n=NODES-start;let loads=0;
const cFor=year=>{const monthDays=[31,year%4===0?29:28,31,30,31,30,31,31,30,31,30,31],days=monthDays.reduce((a,b)=>a+b),size=n*days;return [{start,n,days,year,monthDays,temperature:new Float32Array([25]),temperatureIndex:new Uint16Array(size),rain:new Uint16Array(size),sunshine:new Float32Array(size).fill(7*3600)},{start,n,days,year,values:new Float32Array(size).fill(16)}];};
const result=await calculatePart(spec,async year=>{loads++;return cFor(year);});assert.equal(loads,6);for(let i=0;i<n;i++){assert.equal(result.score[i],10);assert.equal(result.days[i],2192/6);assert.equal(result.coverage[i],2192);assert.equal(result.sunhours[i],7);}const encoded=encodePart(result),parsed=globalThis.ClimateResult.parse(encoded,{start,n});assert.deepEqual(parsed.score,result.score);assert.throws(()=>globalThis.ClimateResult.parse(encoded,{start:0}));assert.throws(()=>globalThis.ClimateResult.parse(encoded.slice(0,-1)));assert.throws(()=>globalThis.ClimateResult.parse(new ArrayBuffer(4)));
const service=createService({fetcher:()=>{throw Error('Should not fetch for invalid request');}});assert.equal((await service.fetch(new Request('https://example.test/?part=0'))).status,400);assert.equal((await service.fetch(new Request(url,{method:'POST'}))).status,405);
console.log('PASS: canonical keys, invalid inputs, six-year annualization, archive alignment, compact roundtrip and truncated responses.');
// Concurrent identical requests share one job, and failures never enter the cache.
const entries=new Map(),jobs=[];let readCount=0;
const cache={async match(k){return entries.get(k.url)?.clone();},async put(k,r){entries.set(k.url,r.clone());}};
const sharedService=createService({cache,maxConcurrent:1,loadYear:async year=>{readCount++;await new Promise(r=>setTimeout(r,1));return cFor(year);}});
const same=()=>new Request(queryURL(url,41,'2025',p));const ctx={waitUntil:p=>jobs.push(p)};
const replies=await Promise.all([sharedService.fetch(same(),ctx),sharedService.fetch(same(),ctx)]);await Promise.all(jobs);assert.equal(readCount,1);assert.deepEqual(replies.map(r=>r.headers.get('X-Climate-Cache')),['miss','pending']);assert.equal(replies[1].status,202);assert.equal((await sharedService.fetch(same(),ctx)).headers.get('X-Climate-Cache'),'hit');assert.equal(readCount,1);
const failed=createService({cache,loadYear:async()=>{throw Error('source outage');}});const failURL=queryURL(url,41,'2024',p);assert.equal((await failed.fetch(new Request(failURL),ctx)).status,502);assert.equal((await failed.fetch(new Request(failURL),ctx)).headers.get('Cache-Control'),'no-store');
const missing=await calculatePart({...spec,period:'2025'},async year=>{const pair=cFor(year);pair[1].values.fill(NaN,0,31);return pair;});assert(Number.isNaN(missing.score[0]));assert.equal(missing.coverage[0],334);
console.log('PASS: in-flight sharing, cache hits, uncached failures and per-month missing-data exclusion.');
// Sites denies the default cache. Initialize a single named cache and shared service set.
const worker=(await import('./worker.mjs')).default;let opens=0;
globalThis.caches={get default(){throw Error('Default cache is forbidden on Sites');},async open(name){assert.equal(name,'comfy-days-results-v1');opens++;return cache;}};
const invalid=new Request('https://comfy.test/api/climate/v1?part=999');const invalidResponses=await Promise.all([worker.fetch(invalid,{},ctx),worker.fetch(invalid,{},ctx)]);assert.deepEqual(invalidResponses.map(r=>r.status),[400,400]);assert.equal(opens,2);
console.log('PASS: Sites named-cache isolation and request-local cache handles under concurrent requests.');
