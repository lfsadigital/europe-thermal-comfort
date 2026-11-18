import assert from 'node:assert/strict';
import {parseQuery,calculatePart} from './query-core.mjs';
import {createAQIDailyService} from './aqi-archive.mjs';
const p={lower:14,upper:30,rain0:4,rain1:10,rain2:20,pen1:.5,pen2:1,pen3:1.5,drymax:4,sunenabled:false,sunmin:6,lowenabled:true,lowmin:14,lowmax:30,aqenabled:true,aqmax:100};
const days=366,n=2048,monthDays=[31,29,31,30,31,30,31,31,30,31,30,31],size=days*n;
const climate={start:0,n,year:2024,days,monthDays,temperature:new Float32Array([25,35]),temperatureIndex:new Uint16Array(size),rain:new Uint16Array(size),sunshine:new Float32Array(size).fill(21600)};
const low={start:0,n,year:2024,days,values:new Float32Array(size).fill(16)};
const aq={start:0,n,year:2024,days,values:new Float64Array(size).fill(50)};
for(let k=0;k<n;k++){for(let day=152;day<days;day++){climate.temperatureIndex[k*days+day]=1;aq.values[k*days+day]=150;}}
const janMay=31;const query=new URL('https://example.test/api?part=0&period=2024');query.searchParams.set('params',JSON.stringify(p));query.searchParams.set('months',janMay);const spec=parseQuery(query);
const selected=await calculatePart(spec,async()=>[climate,low,aq]);assert.equal(selected.coverage[0],152);assert.equal(selected.days[0],152);assert.equal(selected.score[0],10);assert.equal(selected.aqCoverage[0],152);
for(let day=152;day<183;day++)climate.rain[day]=65535;
const stillEligible=await calculatePart(spec,async()=>[climate,low,aq]);assert.equal(stillEligible.coverage[0],152);assert.equal(stillEligible.score[0],10);
const full=await calculatePart({...spec,monthMask:4095},async()=>[climate,low,aq]);assert.equal(full.coverage[0],335);assert(Number.isNaN(full.score[0]));assert.equal(full.coverage[1],366);assert.equal(full.days[1],152);assert(full.score[1]<10);
const svc=createAQIDailyService({loadYear:async()=>aq});const response=await svc.fetch(new Request('https://example.test/api?node=0&period=2024&max=100&months=31'));const d=await response.json();assert.equal(d.count,152);assert.equal(d.calendar,152);assert.equal(d.within,152);assert.equal(d.mean,50);
query.searchParams.set('months','0');assert.throws(()=>parseQuery(query),/month/);
console.log('PASS: selected months, leap year, score, comfortable days, coverage, AQI and validation');
