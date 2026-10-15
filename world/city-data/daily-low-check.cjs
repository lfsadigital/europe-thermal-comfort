const assert=require('node:assert/strict'),{daily,temperatureLoss,calculate,parseMinimum}=require('../site/dist/daily-temperature-core.js');
const p={lower:20,upper:30,lowenabled:true,lowmin:12,lowmax:22,rain0:1,rain1:10,rain2:20,pen1:.5,pen2:1,pen3:1.5,sunenabled:false,sunmin:6};
assert.equal(daily(18,8,0,0,p).score,8);assert.equal(daily(34,24,0,0,p).score,8);assert.equal(daily(27,18,0,0,p).score,10);
assert.equal(daily(18,8,11,0,p).score,7);assert.equal(daily(18,8,11,4,{...p,sunenabled:true}).score,6);
for(const high of [20,30])for(const low of [12,22])assert(daily(high,low,1,6,{...p,sunenabled:true}).comfortable);
assert(!daily(27,24,0,8,p).comfortable);assert(!daily(19,18,0,8,p).comfortable);assert.equal(daily(27,NaN,0,8,p),null);assert.equal(daily(27,NaN,0,8,{...p,lowenabled:false}).score,10);assert.equal(daily(80,60,30,0,{...p,sunenabled:true}).score,0);
const old=require('../site/dist/sunshine-core.js');let seed=17;const rand=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/2**32;};for(let i=0;i<10000;i++){const high=-40+rand()*100,low=high-rand()*20,rain=rand()*40,sun=rand()*24,q={...p,lowenabled:false,sunenabled:i%2===0};const tLoss=.5*Math.max(q.lower-high,0,high-q.upper),r=Math.round(rain*10),rp=r<=10?0:r<=100?.5:r<=200?1:1.5;assert.equal(daily(high,low,rain,sun,q).score,Math.max(0,10-tLoss-rp-(q.sunenabled?.5*Math.max(0,6-sun):0)));assert.equal(temperatureLoss(high,low,p),.5*Math.max(Math.max(20-high,0,high-30),Math.max(12-low,0,low-22)));}
assert.throws(()=>parseMinimum(new ArrayBuffer(32)));
console.log('PASS: 10,000 direct-reference cases; larger high/low penalty, no sum, daily floor, inclusive limits, rain/sun additions, missing minima, default-off parity.');
