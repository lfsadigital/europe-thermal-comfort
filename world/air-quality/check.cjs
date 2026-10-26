const assert=require('node:assert/strict'),fs=require('node:fs'),cp=require('node:child_process');
const core=require('../site/dist/air-quality-core.js'),fixture=require('./fixture.cjs');
// Independent expected classifications, including continuous provider values.
for(const [value,expected]of [[0,0],[50,0],[50.01,1],[100,1],[100.01,2],[150,2],[150.01,3],[200,3],[200.01,4],[300,4],[300.01,5],[500,5],[999,5],[null,-1],[undefined,-1],[-1,-1],[NaN,-1],['50',-1],[Infinity,-1]])assert.equal(core.category(value),expected);
const records=[fixture(2023),fixture(2024),fixture(2025)],all=core.aggregate(records,'mean');
assert.equal(all.aqi.expected,26304);assert.equal(all.months[1].aqi.expected,(28+29+28)*24);assert.equal(all.aqi.median,42);assert.equal(all.pm.mean,8);assert.equal(all.aqi.bands[0],26304);assert(all.aqi.eligible);
let r=fixture(2025,0,0);r.hourly.us_aqi[0]=null;let s=core.aggregate([r],'2025');assert.equal(s.aqi.count,8759);assert.equal(s.aqi.median,0);assert.equal(s.pm.mean,0);assert(s.aqi.eligible);
// A January month passes with 74 missing hours and fails with 75.
r=fixture(2025);r.hourly.us_aqi.fill(null,0,74);s=core.aggregate([r],'2025');assert(s.aqi.eligible);r.hourly.us_aqi[74]=null;s=core.aggregate([r],'2025');assert(!s.aqi.eligible);assert(s.pm.eligible);assert(!s.months[0].aqi.eligible);assert(s.months[1].aqi.eligible);
r=fixture(2025);r.hourly.us_aqi.fill(null,2160,2232);assert(core.aggregate([r],'2025').aqi.eligible);r.hourly.us_aqi[2232]=null;assert(!core.aggregate([r],'2025').aqi.eligible);
// One year's bad month cannot be hidden by two years of complete records.
const mixed=[fixture(2023),fixture(2024),r];assert(!core.aggregate(mixed,'mean').months[3].aqi.eligible);
r=fixture(2025);r.hourly.pm2_5.fill(null);s=core.aggregate([r],'2025');assert(!s.pm.eligible);assert.equal(s.pm.mean,null);assert(s.aqi.eligible);
r=fixture(2025);r.hourly.us_aqi=r.hourly.us_aqi.map((_,i)=>[0,75,125,175,250,700][i%6]);s=core.aggregate([r],'2025');assert.equal(s.aqi.median,150);assert.deepEqual(s.aqi.bands,[1460,1460,1460,1460,1460,1460]);assert.equal(s.aqi.bands.reduce((a,b)=>a+b),s.aqi.count);
for(const mutate of [r=>r.hourly.time.reverse(),r=>r.hourly.time.pop(),r=>r.hourly.us_aqi.pop(),r=>r.hourly.us_aqi[0]=-1,r=>r.hourly.pm2_5[0]='8',r=>r.hourly_units.us_aqi='EAQI',r=>r.utc_offset_seconds=3600,r=>r.latitude=null]){const r=fixture();mutate(r);assert.throws(()=>core.aggregate([r],'2025'));}
assert.throws(()=>core.aggregate([fixture(2024)],'2025'));assert.throws(()=>core.aggregate([fixture(2025)],'mean'));assert.deepEqual(core.yearsFor('2020'),[]);
// Legacy climate/sun/monthly engines remain exact. Daily AQI-off parity is covered by daily-check.cjs against the published v36 fixture.
for(const file of ['climate-core.js','sunshine-core.js','monthly-core.js'])assert.equal(fs.readFileSync(__dirname+'/../site/dist/'+file,'utf8'),cp.execFileSync('git',['show','origin/main:world/site/dist/'+file],{encoding:'utf8'}));
console.log('PASS: AQI boundaries, continuous values, missingness, units, UTC axes, leap years, monthly coverage, distributions, independent PM2.5 and unchanged legacy scientific engines; daily off-state parity is checked separately.');
