const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const elements=new Map(),element=id=>{if(!elements.has(id))elements.set(id,{hidden:true,textContent:'',checked:id==='rank-spread'});return elements.get(id);};
const sandbox={window:{},document:{getElementById:element},setTimeout:()=>1,clearTimeout(){},AbortController,DOMException,URL,location:{href:'https://local/'}};
vm.runInNewContext(fs.readFileSync(__dirname+'/../site/dist/air-quality-filter.js','utf8'),sandbox);const Filter=sandbox.window.AirQualityFilter;
const owner={enabled:true,maximum:100,appliedPeriod:'2025'},filter=new Filter(owner),entry=(id,lat=id,index=id)=>({place:[id,'City',lat,0],index});
const record=(median,eligible=true)=>({aqi:{median,eligible}});
for(const [median,eligible,expected]of [[0,true,true],[50,true,true],[100,true,true],[100.001,true,false],[151,true,false],[80,false,false],[null,true,false]]){filter.cache.set(filter.key(1,0),record(median,eligible));assert.equal(filter.allows(entry(1)),expected);}
assert(!filter.allows(entry(2)));owner.enabled=false;assert(filter.allows(entry(2)));owner.enabled=true;
// Independent expected sequence: bad/missing entries cannot occupy Top 10.
const rows=Array.from({length:30},(_,i)=>entry(i+1)),expected=[1,3,4,6,7,9,10,12,13,15];filter.cache.clear();for(const e of rows)filter.cache.set(filter.key(e.place[2],0),record(e.place[0]%3===2?151:100));
filter.load=async()=>{throw Error('Complete fixture should need no fetch');};filter.scan=Symbol('test');filter.limit=40;(async()=>{
 await filter.scanRanking(rows,filter.scan);assert.equal(filter.passed,10);assert(filter.complete);assert.equal(filter.checked,15);assert.deepEqual(rows.filter(e=>filter.allows(e)).slice(0,10).map(e=>e.place[0]),expected);
 // Missing is excluded and visibly incomplete, not silently assumed clean.
 filter.cache.clear();filter.scan=Symbol('missing');filter.limit=4;await filter.scanRanking(rows,filter.scan);assert(!filter.complete);assert.equal(filter.checked,4);assert.equal(filter.passed,0);filter.status();assert.equal(element('aq-filter-more').hidden,false);
 filter.failures.add('source failure');filter.status();assert.match(element('aq-map-status').textContent,/failed/);assert.equal(element('aq-filter-retry').hidden,false);filter.retry();assert.equal(filter.failures.size,0);
 // A rejected city must not hide a qualifying city sharing its climate cell.
 const duplicate=new Filter(owner),duplicates=[entry(1,1,7),entry(2,2,7),...Array.from({length:12},(_,i)=>entry(i+3,i+3,i+8))];
 for(const e of duplicates)if(e.place[0]!==2)duplicate.cache.set(duplicate.key(e.place[2],0),record(e.place[0]===1?151:50));
 const loaded=[];duplicate.load=async lat=>{loaded.push(lat);duplicate.cache.set(duplicate.key(lat,0),record(50));};duplicate.scan=Symbol('duplicates');await duplicate.scanRanking(duplicates,duplicate.scan);assert.deepEqual(loaded,[2]);assert.equal(duplicate.passed,10);assert(duplicate.allows(duplicates[1]));
 // Exercise a real AbortController timeout, without waiting 145 seconds.
 const timeout=new Filter(owner);sandbox.setTimeout=(callback,ms)=>{if(ms===145000)queueMicrotask(callback);return 1;};sandbox.fetch=async(_url,{signal})=>new Promise((_resolve,reject)=>signal.addEventListener('abort',()=>reject(new DOMException('Timed out','AbortError')),{once:true}));
 const timedKey=timeout.key(1,0);await assert.rejects(timeout.run({lat:1,lon:0,period:'2025',key:timedKey,generation:timeout.generation}),e=>e.name==='AbortError');assert(timeout.failures.has(timedKey));timeout.status();assert.match(element('aq-map-status').textContent,/failed/);assert.equal(element('aq-filter-retry').hidden,false);timeout.retry();assert(!timeout.failures.size);
 // An obsolete generation is intentional cancellation and must not be failure.
 timeout.generation++;await assert.rejects(timeout.run({lat:2,lon:0,period:'2025',key:timeout.key(2,0),generation:timeout.generation-1}),e=>e.name==='AbortError');assert(!timeout.failures.size);
 owner.enabled=false;assert.equal(filter.filterCandidates(rows,'off'),rows);filter.status();assert.equal(element('aq-map-status').hidden,true);
 console.log('PASS: inclusive historical median threshold, zero, missing/invalid exclusion, sorted Top 10 prefix, bounded provisional scans, duplicate-cell representatives, timeout/provisional/retry, intentional cancellation and default-off restoration.');
})().catch(error=>{console.error(error);process.exitCode=1;});
