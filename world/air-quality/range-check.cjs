const assert=require('node:assert/strict'),core=require('../site/dist/air-quality-core.js'),fixture=require('./fixture.cjs');
const records=[fixture(2023,50),fixture(2024,100),fixture(2025,151)];
const combined={...records[0],hourly:Object.fromEntries(['time','us_aqi','pm2_5'].map(k=>[k,records.flatMap(r=>r.hourly[k])]))};
const split=core.fromRange(combined,'mean');assert.deepEqual(split.map(r=>r.hourly.time.length),[8760,8784,8760]);assert.deepEqual(core.aggregate(split,'mean'),core.aggregate(records,'mean'));
assert.deepEqual(core.aggregate(core.fromRange(fixture(2025),'2025'),'2025').aqi.bands,[8760,0,0,0,0,0]);
for(const mutate of [r=>r.hourly.time.pop(),r=>r.hourly.us_aqi.pop(),r=>r.hourly.time[8760]='2024-01-01T01:00',r=>r.hourly.pm2_5[0]=-1,r=>r.hourly_units.us_aqi='EAQI']){const bad=structuredClone(combined);mutate(bad);assert.throws(()=>core.fromRange(bad,'mean'));}
assert.throws(()=>core.fromRange(combined,'2025'));assert.throws(()=>core.fromRange({},'2025'));assert.throws(()=>core.fromRange(combined,'2020'));
console.log('PASS: combined multi-year history preserves exact annual statistics and leap-year axes; malformed/missing data rejected.');
