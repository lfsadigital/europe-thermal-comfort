const assert=require('node:assert/strict'),http=require('node:http'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const {chromium}=require('playwright'),fixture=require('./fixture.cjs');
const root=path.resolve(__dirname,'../site/dist'),meta=JSON.parse(fs.readFileSync(root+'/assets/metadata.json'));
const types={'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.woff2':'font/woff2','.png':'image/png'};
const server=http.createServer((req,res)=>{const p=path.resolve(root,'.'+new URL(req.url,'http://localhost').pathname.replace(/\/$/,'/index.html'));if(!p.startsWith(root+'/')){res.writeHead(403);return res.end();}try{const b=fs.readFileSync(p);res.setHeader('Content-Type',types[path.extname(p)]||'application/octet-stream');res.end(b);}catch{res.writeHead(404);res.end();}});
(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));const url=`http://127.0.0.1:${server.address().port}`;
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 let requests=0,fail=false,missing=false,slow=false;
 await page.route('**/*',async route=>{
  const u=new URL(route.request().url());
  if(u.hostname==='air-quality-api.open-meteo.com'){
   requests++;if(fail)return route.abort();const year=Number(u.searchParams.get('start_date').slice(0,4)),d=fixture(year);
   d.latitude=Number(u.searchParams.get('latitude'));d.longitude=Number(u.searchParams.get('longitude'));
   d.hourly.us_aqi=d.hourly.us_aqi.map((_,i)=>[20,65,110,170,240,340][i%6]);if(missing)d.hourly.us_aqi.fill(null,0,100);
   if(slow)await new Promise(r=>setTimeout(r,500));
   return route.fulfill({json:d}).catch(()=>{});
  }
  if(u.pathname.endsWith('basemap-style.json'))return route.fulfill({json:{version:8,sources:{},layers:[{id:'background',type:'background',paint:{'background-color':'#eef2f8'}}]}});
  if(u.hostname.includes('climate-sunshine')){
   const year=u.pathname.match(/(202[0-5])/),count=year?(year[1]==='2024'||year[1]==='2020'?366:365):2192;
   const a=u.pathname.includes('coverage')?new Uint16Array(meta.nodes).fill(count):u.pathname.includes('hours')?new Float32Array(meta.shape[0]*meta.shape[1]).fill(6):new Float64Array(meta.nodes).fill(u.pathname.includes('days')?180:8);
   return route.fulfill({body:zlib.gzipSync(Buffer.from(a.buffer))});
  }
  if(u.hostname!=='127.0.0.1')return route.abort();
  return route.continue();
 });
 try{
  await page.goto(url);await page.waitForFunction(()=>window.ComfyDays&&!window.ComfyDays.state.busy);assert.equal(requests,0);
  await page.locator('#aq-enabled').check();assert.match(await page.locator('#aq-status').textContent(),/Select a city/);assert.equal(requests,0);
  await page.evaluate(()=>ComfyDays.inspect(38.72,-9.14));await page.locator('#aq-results').waitFor({state:'visible'});assert.equal(requests,3);assert.equal(await page.locator('.aq-distribution li').count(),6);assert.equal(await page.locator('#aq-results tbody tr').count(),12);
  const fingerprint=()=>page.evaluate(()=>{const s=ComfyDays.state;return JSON.stringify({params:s.params,score:Array.from(s.scoreValues).reduce((a,b)=>a+(Number.isFinite(b)?b:0),0),days:Array.from(s.dayValues).reduce((a,b)=>a+(Number.isFinite(b)?b:0),0),ranks:document.getElementById('city-ranking').textContent});});
  const before=await fingerprint();await page.locator('#aq-period').selectOption('2024');await page.waitForFunction(()=>document.getElementById('aq-status').textContent.startsWith('2024 ·'));assert.match(await page.locator('#aq-status').textContent(),/8,784 \/ 8,784/);assert.equal(await fingerprint(),before);
  await page.evaluate(()=>ComfyDays.setRegion('europe'));assert(new URL(page.url()).searchParams.get('aqi')==='1');assert(new URL(page.url()).searchParams.get('aqiyear')==='2024');
  const afterRegion=await fingerprint();await page.locator('#aq-enabled').uncheck();assert.equal(await fingerprint(),afterRegion);assert(await page.locator('#aq-content').isHidden());const count=requests;await page.locator('#aq-enabled').check();await page.locator('#aq-results').waitFor({state:'visible'});assert.equal(requests,count);
  await page.locator('#aq-period').selectOption('mean');await page.locator('#aq-results').waitFor({state:'visible'});
  await page.locator('#aq-results details summary').click();await page.locator('#aq-content>details>summary').click();
  fs.mkdirSync(path.resolve(__dirname,'../../.impeccable/review'),{recursive:true});
  await page.evaluate(()=>{const p=document.createElement('p');p.textContent='QA capture · synthetic hourly records; not real Lisbon data';p.style.cssText='font-size:14px;font-weight:600';document.getElementById('air-quality').prepend(p);});
  for(const [name,width,height]of [['desktop',1440,1000],['mobile',390,844],['compact',320,740],['tablet',768,1024]]){
   await page.setViewportSize({width,height});await page.locator('#air-quality').scrollIntoViewIfNeeded();assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),name+' page overflow');
   for(const selector of ['.aq-toggle','#aq-period','#aq-results summary'])assert((await page.locator(selector).first().boundingBox()).height>=44,selector+' touch target');
   await page.locator('#air-quality').screenshot({path:path.resolve(__dirname,`../../.impeccable/review/${name}.png`)});
  }
  // Keyboard input and persisted opt-in, with the real application bootstrap.
  await page.locator('#aq-enabled').focus();await page.keyboard.press('Space');assert(await page.locator('#aq-content').isHidden());await page.keyboard.press('Space');await page.locator('#aq-results').waitFor({state:'visible'});
  // Stale responses, cancellation, missing data, failure and explicit retry.
  slow=true;await page.evaluate(()=>ComfyDays.inspect(10,20));await page.waitForTimeout(50);await page.evaluate(()=>ComfyDays.inspect(11,21));await page.locator('#aq-results').waitFor({state:'visible'});assert.match(await page.locator('#aq-results').textContent(),/11.00°, 21.00°/);slow=false;
  missing=true;await page.evaluate(()=>ComfyDays.inspect(12,22));await page.locator('#aq-results').waitFor({state:'visible'});assert.match(await page.locator('#aq-status').textContent(),/Insufficient coverage/);assert.match(await page.locator('.aq-stats').textContent(),/Not available/);missing=false;
  fail=true;await page.evaluate(()=>ComfyDays.inspect(13,23));await page.locator('#aq-retry').waitFor({state:'visible'});assert(await page.locator('#aq-results').isHidden());fail=false;await page.locator('#aq-retry').click();await page.locator('#aq-results').waitFor({state:'visible'});
  slow=true;await page.evaluate(()=>ComfyDays.inspect(14,24));await page.locator('#aq-enabled').uncheck();await page.waitForTimeout(600);assert(await page.locator('#aq-content').isHidden());
  assert.deepEqual(errors,[]);console.log(JSON.stringify({result:'PASS',source:'synthetic hourly fixtures; real UI bootstrap, map and integration',viewports:[1440,390,320,768],checks:['off by default/no fetch','explicit opt-in','selected point','full period/leap year','unchanged climate arrays/parameters/ranking','region/URL parity','cache','keyboard','table','touch targets','no page overflow','stale response cancellation','coverage failure','source failure/retry','disable cancellation','no page errors']},null,2));
 }finally{await browser.close();server.close();}
})().catch(e=>{console.error(e);server.close();process.exitCode=1;});
