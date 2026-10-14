'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),{launch}=require('./browser-runtime.cjs');
(async()=>{const b=await launch();try{
 const p=await b.newPage({viewport:{width:1440,height:1000},acceptDownloads:true}),errors=[],requests=[];
 p.on('pageerror',e=>errors.push(e.message));p.on('request',r=>requests.push(r.url()));
 const base=process.env.COMFY_TEST_URL||'http://127.0.0.1:8777/';
 await p.goto(base+'?nomads=1&nomadmin=3&cost=1&budget=2500&colors=all');
 await p.waitForFunction(()=>window.ComfyDays&&!ComfyDays.state.busy&&ComfyDays.cityFilters.ready);
 const arrays=()=>p.evaluate(()=>({score:Array.from(ComfyDays.state.scoreValues),days:Array.from(ComfyDays.state.dayValues)})),before=await arrays();
 assert.equal(await p.locator('#nomads-enabled,#cost-enabled').count(),0);
 assert(!new URL(p.url()).searchParams.has('nomads'));assert(!new URL(p.url()).searchParams.has('cost'));
 assert(!requests.some(u=>u.includes('nomads-cities')||u.includes('nomads.com')));
 const old=await p.request.get(base+'assets/nomads-cities.json');assert(!old.ok());
 await p.evaluate(()=>ComfyDays.inspect(25.76,-80.19));assert(!/Nomad|monthly cost/i.test(await p.locator('#city-context-values').innerText()));
 await p.evaluate(()=>ComfyDays.ui.open('city'));await p.check('#crime-enabled');await p.selectOption('#crime-geography','city');await p.selectOption('#crime-year','2024');
 assert.deepEqual(await arrays(),before);assert(await p.evaluate(()=>ComfyDays.cityFilters.cityHomicide.get('4164138|2024').count===28));
 await p.selectOption('#rank-population','1000000');assert.deepEqual(await arrays(),before);
 await p.click('#city-filter-reset');await p.evaluate(()=>ComfyDays.ui.close());
 for(const region of ['europe','usa','world']){await p.click('[data-region="'+region+'"]');assert.deepEqual(await arrays(),before);}
 for(const metric of ['score','days']){await p.click('[data-view="'+metric+'"]');const dl=p.waitForEvent('download');await p.click('#export');await(await dl).saveAs('../share/current-'+metric+'.png');const bytes=fs.readFileSync('../share/current-'+metric+'.png');assert.equal(bytes.readUInt32BE(16),2400);assert.equal(bytes.readUInt32BE(20),1800);assert(!/nomads|budget/i.test(JSON.stringify(await p.evaluate(()=>ComfyDays.lastExport))));}
 await p.setViewportSize({width:360,height:800});await p.evaluate(()=>ComfyDays.ui.open('city'));assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.deepEqual(errors,[]);
 const result={result:'PASS',url:base,checks:['Nomads controls removed','no Nomads network requests','legacy flags removed','public snapshot unavailable','context removed','climate arrays unchanged under city filters and all tabs','municipal homicide retained','two PNG exports without retired filters','mobile no overflow'],errors};
 fs.writeFileSync('../site/docs/license-update-browser'+(process.env.COMFY_TEST_URL?'-public':'')+'.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
}finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1});
