const assert=require('node:assert/strict'),core=require('../site/dist/air-quality-daily-core.js'),climate=require('../site/dist/daily-temperature-core.js');
const hours=Array(24).fill(60);hours[12]=140;assert.equal(core.daily(hours),260/3);hours[11]=hours[13]=140;assert.equal(core.daily(hours),140);
assert.equal(core.daily(Array(24).fill(0)),0);assert.equal(core.daily(Array(24).fill(100)),100);assert.throws(()=>core.daily([1,2]));
const missing=Array(24).fill(60);missing[0]=missing[1]=null;assert.equal(core.daily(missing),60);missing[2]=null;assert(Number.isNaN(core.daily(missing)));
const isolated=Array(24).fill(60);isolated[0]=140;isolated[1]=null;assert.equal(core.daily(isolated),60,'A window must not bridge missing hours');
for(const value of [null,undefined,NaN,-1,Infinity])assert.equal(core.penalty(value,100),0);
for(const [aqi,want]of [[0,0],[100,0],[125,.5],[150,1],[200,2],[300,4]])assert.equal(core.penalty(aqi,100),want);
const p={lower:14,upper:30,lowenabled:true,lowmin:14,lowmax:30,rain0:4,rain1:10,rain2:20,pen1:.5,pen2:1,pen3:1.5,sunenabled:false,sunmin:6,aqenabled:true,aqmax:100};
assert.deepEqual(climate.daily(25,16,0,7,p,150),{score:9,comfortable:false});assert.deepEqual(climate.daily(25,16,0,7,p,100),{score:10,comfortable:true});
assert.deepEqual(climate.daily(25,16,0,7,p,NaN),{score:10,comfortable:true});assert.deepEqual(climate.daily(25,16,0,7,{...p,aqenabled:false},500),{score:10,comfortable:true});
assert.deepEqual(climate.daily(50,-5,25,0,{...p,sunenabled:true},500),{score:0,comfortable:false});
// AQI is applied on the same dates before the daily zero floor and averaging.
const n=1,days=365,c={start:0,n,days,year:2025,monthDays:[31,28,31,30,31,30,31,31,30,31,30,31],temperature:new Float32Array([25]),temperatureIndex:new Uint16Array(days),rain:new Uint16Array(days),sunshine:new Float32Array(days).fill(7*3600)},low={start:0,n,days,year:2025,values:new Float32Array(days).fill(16)},aq={start:0,n,days,year:2025,values:new Float64Array(days).fill(150)};
aq.values[0]=NaN;const actual=climate.calculate(c,low,0,p,aq);assert.equal(actual.aqCount,364);assert.equal(actual.scoreSum,10+364*9);assert.equal(actual.comfortable,1);assert.equal(actual.count,365);assert.throws(()=>climate.calculate(c,low,0,p,{...aq,year:2024}));
const b=new ArrayBuffer(32+365*8);new Uint32Array(b,0,8).set([0x41514431,1,0,1,365,2025,3,22]);new Float64Array(b,32).set(aq.values);assert.equal(core.parse(b,{start:0,n:1,year:2025}).values[1],150);assert.throws(()=>core.parse(b,{year:2024}));assert.throws(()=>core.parse(b.slice(0,-1)));
console.log('PASS: isolated vs sustained peaks, 22-hour requirement, contiguous windows, boundaries/zero, agreed slope, missing-data fallback, daily floor and exact date alignment.');
const legacy=require('./fixtures/daily-temperature-v36.cjs');let seed=90210;const random=()=>((seed=(Math.imul(seed,1664525)+1013904223)>>>0)/4294967296);
for(let i=0;i<10000;i++){const high=random()*90-30,low=high-random()*25,rain=random()*60,sun=random()*24,rules={...p,aqenabled:false,lower:-10+Math.floor(random()*25),upper:25+Math.floor(random()*20),lowmin:-10+Math.floor(random()*25),lowmax:25+Math.floor(random()*20),sunenabled:random()>.5,sunmin:random()*12};assert.deepEqual(climate.daily(high,low,rain,sun,rules,random()*500),legacy.daily(high,low,rain,sun,rules));}
console.log('PASS: 10,000 independent disabled-AQI daily results exactly match the published v36 engine.');
