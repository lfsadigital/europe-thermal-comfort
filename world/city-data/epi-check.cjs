'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),zlib=require('node:zlib'),vm=require('node:vm');
const data=JSON.parse(zlib.gunzipSync(fs.readFileSync(__dirname+'/../site/dist/assets/epi-budget.json.gz')));
assert.equal(data.family_code,'1p0c');assert.equal(data.price_year,2025);assert.equal(data.license,'CC BY-NC-SA 4.0');
assert.equal(Object.keys(data.counties).length,3143);assert.equal(Object.keys(data.city_counties).length,16418);
for(const row of Object.values(data.counties)){assert(row[2]>0);assert(Math.abs(row[2]*12-row[3])<1e-7);assert.equal(row[9],0);assert(Math.abs(row.slice(4).reduce((a,b)=>a+b,0)-row[2])<=2/12+1e-7);}
for(const fips of Object.values(data.city_counties))assert(data.counties[fips]);
const sandbox={window:{},Number,Math};vm.createContext(sandbox);vm.runInContext(fs.readFileSync(__dirname+'/../site/dist/epi-budget.js','utf8'),sandbox);
const epi=Object.create(sandbox.window.EPIBudget.prototype);Object.assign(epi,{ready:true,data,region:'usa'});
const miami=[4164138,'Miami',25.774,-80.193,'Florida','United States'],nyc=[5128581,'New York City',40.71,-74,'New York','United States'];
assert.equal(epi.record(miami).fips,'12086');assert.equal(epi.record(miami).monthly,5047);assert.equal(epi.record(miami).annual,60564);
assert.equal(epi.assessment(miami,{epi:true,budget:5047}).failures.length,0);assert.equal(epi.assessment(miami,{epi:true,budget:5046.99}).failures.length,1);
assert.equal(epi.record(nyc),null);assert.equal(epi.assessment(nyc,{epi:true,budget:0}).missing.length,1);assert.equal(epi.assessment(nyc,{epi:true,budget:0}).failures.length,0);
assert.equal(epi.assessment(miami,{epi:false,budget:0}).failures.length,0);assert.equal(epi.record([...miami.slice(0,5),'France']),null);
assert(!epi.valid({epi:true,budget:NaN}));assert(!epi.valid({epi:true,budget:-1}));assert(epi.valid({epi:true,budget:0}));
console.log('PASS EPI profile, units, all county totals, exact joins, Miami source values, inclusive limit, Unknown retained, foreign city guard');
