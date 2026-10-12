'use strict';
const assert=require('node:assert/strict'),core=require('./sunshine-core.js');
const params={lower:18,upper:26,rain0:1,rain1:10,rain2:20,pen1:.5,pen2:1,pen3:1.5,sunmin:6};
function fixture(year,definitions){const days=year%4===0?366:365,n=definitions.length,temperatures=Float32Array.from([-30,18,22,25,26,28]),count=n*days,ti=new Uint16Array(count),rain=new Uint16Array(count),sun=new Float32Array(count);for(let k=0;k<n;k++)for(let d=0;d<days;d++){const point=typeof definitions[k]==='function'?definitions[k](d):definitions[k];ti[k*days+d]=temperatures.indexOf(point[0]);rain[k*days+d]=point[1];sun[k*days+d]=point[2];}const header=Uint32Array.from([0x53434c4d,1,0,n,days,year,temperatures.length,0,0,0,0,0]),shuffled=new Uint8Array(count*4),raw=new Uint8Array(sun.buffer);for(let byte=0;byte<4;byte++)for(let i=0;i<count;i++)shuffled[byte*count+i]=raw[i*4+byte];const bytes=Buffer.concat([Buffer.from(header.buffer),Buffer.from(temperatures.buffer),Buffer.from(ti.buffer),Buffer.from(rain.buffer),Buffer.from(shuffled)]);return core.parse(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength));}
let checks=0;function result(c,k,p= params){checks++;return core.calculate(c,k,p);}
const c=fixture(2025,[[22,0,28800],[28,120,14400],[-30,210,0],[18,10,21600],[26,10,21600],[25,0,21599.999]]);
let r=result(c,0);assert.equal(r.scoreSum/r.count,10);assert.equal(r.comfortable,365);assert(r.eligible);
r=result(c,1);assert.equal(r.scoreSum/r.count,7);assert.equal(r.comfortable,0);r=result(c,2);assert.equal(r.scoreSum,0);r=result(c,3);assert.equal(r.comfortable,365);r=result(c,4);assert.equal(r.comfortable,365);r=result(c,5);assert.equal(r.comfortable,0);assert(r.scoreSum/r.count<10);
r=result(c,1,{...params,sunmin:0});assert.equal(r.scoreSum/r.count,8);
const leap=fixture(2024,[[22,0,21600]]);assert.equal(result(leap,0).comfortable,366);
const missing=fixture(2025,[day=>[22,0,day<4?NaN:21600]]);r=result(missing,0);assert.equal(r.count,361);assert.equal(r.comfortable,361);assert.equal(r.eligible,false);assert.equal(r.scoreSum,3610);
const fewMissing=fixture(2025,[day=>[22,0,day===0?NaN:21600]]);r=result(fewMissing,0);assert(r.eligible);assert.equal(r.comfortable/r.count*365,365);
assert.throws(()=>core.parse(new ArrayBuffer(48)),/version/);console.log(JSON.stringify({result:'PASS',checks,verified:'daily zero floor; combined penalties; inclusive temperature/rain/sun boundaries; fractional sunshine; disabled minimum; leap year; missing sunshine and monthly eligibility; malformed input'}));
