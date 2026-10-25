'use strict';
// Progressive verification keeps unverified places out of results. Ranking
// walks climate-sorted candidates in order, so ten confirmed matches are the
// true Top 10; a bounded incomplete scan is explicitly labelled as such.
class AirQualityFilter {
 constructor(owner){this.owner=owner;this.cache=new Map();this.failures=new Set();this.pending=new Map();this.revision=0;this.generation=0;this.limit=40;this.busy=false;this.scan=null;this.pool=[];this.checked=0;this.complete=false;this.passed=0;this.queue=[];this.workers=0;this.controllers=new Set();}
 get signature(){return [this.owner.enabled,this.owner.appliedPeriod,this.owner.maximum,this.revision].join('|');}
 key(lat,lon,period=this.owner.appliedPeriod){return [Number(lat.toFixed(4)),Number(lon.toFixed(4)),period].join('|');}
 summary(e){return this.cache.get(this.key(e.place[2],e.place[3]));}
 allows(e){if(!this.owner.enabled)return true;const s=this.summary(e);return !!s?.aqi?.eligible&&Number.isFinite(s.aqi.median)&&s.aqi.median<=this.owner.maximum;}
 reset(){this.generation++;for(const c of this.controllers)c.abort();this.controllers.clear();for(const job of this.queue)job.reject(new DOMException('Cancelled','AbortError'));this.queue=[];this.pending.clear();this.failures.clear();this.limit=40;this.pool=[];this.scan=null;this.visibleKey=null;this.visibleScan=null;this.busy=false;this.checked=0;this.complete=false;this.passed=0;this.revision++;this.notify();}
 notify(){clearTimeout(this.timer);this.timer=setTimeout(()=>{window.ComfyDays?.discovery?.renderRanking();window.ComfyDays?.cityMap?.refresh();window.ComfyDays?.ui?.refresh();this.status();},50);}
 status(){
  const box=document.getElementById('aq-map-status'),retry=document.getElementById('aq-filter-retry'),more=document.getElementById('aq-filter-more');
  box.hidden=!this.owner.enabled;retry.hidden=!this.owner.enabled||!this.failures.size;more.hidden=!this.owner.enabled||this.busy||this.complete||this.passed>=10;
  if(!this.owner.enabled)return;
  box.textContent=this.busy?`Checking city AQI · ${this.checked} checked · ${this.passed} ranking matches so far. Only verified city points are shown.`:this.failures.size?`Some city AQI checks failed. Results are provisional; retry to complete the ranking. Only verified matches are shown.`:!this.complete&&this.passed<10?`${this.checked} leading candidates checked · ${this.passed} verified matches. Check more cities to continue.`:`AQI filter · median ≤${this.owner.maximum} · ${this.owner.appliedPeriod==='mean'?'2023–2025':this.owner.appliedPeriod}. Only verified city points are shown; climate shading is hidden.`;
 }
 async load(lat,lon,period=this.owner.appliedPeriod){
  const key=this.key(lat,lon,period),cached=this.cache.get(key);if(cached)return cached;
  if(this.pending.has(key))return this.pending.get(key);
  const generation=this.generation;
  const promise=new Promise((resolve,reject)=>{this.queue.push({lat,lon,period,key,generation,resolve,reject});this.pump();});
  this.pending.set(key,promise);
  try{return await promise;}finally{if(this.pending.get(key)===promise)this.pending.delete(key);}
 }
 pump(){while(this.workers<2&&this.queue.length){const job=this.queue.shift();this.workers++;this.run(job).then(job.resolve,job.reject).finally(()=>{this.workers--;this.pump();});}}
 async run(job){
  const {lat,lon,period,key,generation}=job,controller=new AbortController();this.controllers.add(controller);
  try{
   for(let attempt=0;attempt<5;attempt++){
    if(generation!==this.generation)throw new DOMException('Cancelled','AbortError');
    const url=new URL('api/air-quality/v1',location.href);for(const [k,v]of Object.entries({lat:lat.toFixed(4),lon:lon.toFixed(4),period}))url.searchParams.set(k,v);
    const timeout=setTimeout(()=>controller.abort(),145000);let response;
    try{response=await fetch(url,{signal:controller.signal,cache:'no-store'});}finally{clearTimeout(timeout);}
    if(response.status===503&&attempt<4){await new Promise(resolve=>setTimeout(resolve,1000*(attempt+1)));continue;}
    if(!response.ok)throw Error('AQI summary HTTP '+response.status);
    const s=await response.json();
    if(s.version!==1||s.period!==period||!s.aqi||typeof s.aqi.eligible!=='boolean'||!Array.isArray(s.months)||s.months.length!==12||s.latitude!==Number(lat.toFixed(4))||s.longitude!==Number(lon.toFixed(4))||s.aqi.eligible&&(!Number.isFinite(s.aqi.median)||s.aqi.count<=0||s.aqi.count>s.aqi.expected))throw Error('Invalid AQI summary');
    if(generation!==this.generation)throw new DOMException('Cancelled','AbortError');
    this.cache.set(key,s);while(this.cache.size>2000)this.cache.delete(this.cache.keys().next().value);this.failures.delete(key);this.revision++;this.notify();return s;
   }
  }catch(error){if(generation===this.generation){this.failures.add(key);this.revision++;this.notify();}throw error;}
  finally{this.controllers.delete(controller);}
 }
 filterCandidates(rows,context){
  if(!this.owner.enabled)return rows;
  if(this.context!==context){this.context=context;this.generation++;for(const c of this.controllers)c.abort();this.controllers.clear();for(const job of this.queue)job.reject(new DOMException('Cancelled','AbortError'));this.queue=[];this.pending.clear();this.scan=null;this.visibleKey=null;this.visibleScan=null;this.busy=false;this.limit=40;this.failures.clear();}
  this.pool=rows;
  if(!this.scan){this.scan=Symbol('scan');const token=this.scan;this.scanRanking(rows,token).catch(()=>{});}
  this.status();return rows.filter(e=>this.allows(e));
 }
 async scanRanking(rows,token){
  this.busy=true;this.checked=0;this.passed=0;this.complete=false;this.status();
  const spread=document.getElementById('rank-spread').checked,seen=new Set();let inspected=0,finished=true;
  try{for(const e of rows){
   if(token!==this.scan)return;
   if(spread&&seen.has(e.index))continue;
   if(inspected>=this.limit){finished=false;break;}
   inspected++;const key=this.key(e.place[2],e.place[3]);
   if(!this.cache.has(key)&&!this.failures.has(key))try{await this.load(e.place[2],e.place[3]);}catch(error){if(token!==this.scan)return;}
   if(token!==this.scan)return;
   this.checked=inspected;if(this.allows(e)){seen.add(e.index);this.passed++;}
   this.status();if(this.passed>=10)break;
  }}finally{if(token===this.scan){this.busy=false;this.complete=finished;this.status();this.notify();}}
 }
 more(){this.limit+=40;this.scan=null;this.revision++;this.notify();}
 retry(){this.failures.clear();this.scan=null;this.visibleScan=null;this.revision++;this.notify();}
 verifyVisible(rows,key){
  if(!this.owner.enabled)return;
  if(this.visibleKey!==key){this.visibleKey=key;this.visibleLimit=8;this.visibleScan=null;}
  this.visibleRows=rows;
  const more=document.getElementById('aq-view-more');more.hidden=!rows.slice(this.visibleLimit).some(e=>!this.summary(e));
  if(this.visibleScan)return;
  const token=this.visibleScan=Symbol('visible');
  (async()=>{for(const e of rows.slice(0,this.visibleLimit)){
   if(token!==this.visibleScan||!this.owner.enabled)return;
   const k=this.key(e.place[2],e.place[3]);if(this.cache.has(k)||this.failures.has(k))continue;
   try{await this.load(e.place[2],e.place[3]);}catch{}
  }})().catch(()=>{});
 }
 moreVisible(){this.visibleLimit+=8;this.visibleScan=null;this.revision++;this.notify();}
}
window.AirQualityFilter=AirQualityFilter;
