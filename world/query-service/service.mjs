import {loadAQIYear} from './aqi-archive.mjs';
import {AQI_DATASET} from './aqi-dataset.mjs';
import {REVISION,parseQuery,calculatePart,encodePart} from './query-core.mjs';
const ORIGIN='https://comfy-days-climate-sunshine.lfsalmeida92.workers.dev';
// Share only plain job metadata across requests. A Worker must never await another
// request's Promise: each owner either finishes inline or is retained by waitUntil.
export function createService({fetcher=fetch,cache=null,now=()=>performance.now(),maxConcurrent=2,loadYear=null,archiveCache=null,activeJobs=new Map(),background=false}={}){
 async function load(url,minimum){const response=await fetcher(url,{signal:AbortSignal.timeout(30000)});if(!response.ok)throw Error('Climate source returned '+response.status);const buffer=await new Response(response.body.pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();return minimum?globalThis.DailyTemperatureCore.parseMinimum(buffer):globalThis.SunshineCore.parse(buffer);}
 async function compute(spec){return encodePart(await calculatePart(spec,loadYear||((year,part,aqenabled)=>Promise.all([load(`${ORIGIN}/sun-v1/sun-daily-${year}-${part}.gz`,false),load(`${ORIGIN}/minimum-v1/minimum-${year}-${part}.gz`,true),aqenabled?loadAQIYear(year,part,fetcher,AQI_DATASET,archiveCache).catch(()=>null):null]))));}
 return {async fetch(request,ctx={waitUntil:()=>{}}){
  const headers={'Content-Type':'application/octet-stream','Cache-Control':'public, max-age=86400','X-Content-Type-Options':'nosniff','Access-Control-Allow-Origin':'*','Access-Control-Expose-Headers':'Server-Timing, X-Climate-Cache, X-Climate-Revision, Retry-After','X-Climate-Revision':REVISION};
  if(request.method==='OPTIONS')return new Response(null,{status:204,headers:{...headers,'Access-Control-Allow-Methods':'GET, OPTIONS'}});
  if(request.method!=='GET')return new Response('Method not allowed',{status:405,headers:{...headers,Allow:'GET, OPTIONS','Cache-Control':'no-store'}});
  let spec;try{spec=parseQuery(request.url);}catch(e){return new Response(e.message,{status:400,headers:{...headers,'Cache-Control':'no-store'}});}
  const key=new Request('https://comfy-query-cache.invalid/'+encodeURIComponent(spec.key+'|'+(spec.params.aqenabled?AQI_DATASET?.dataset:'off'))),t=now(),hit=cache&&await cache.match(key);
  if(hit){const h=new Headers(hit.headers);h.set('X-Climate-Cache','hit');h.set('Server-Timing',`climate;dur=${(now()-t).toFixed(1)}`);return new Response(hit.body,{headers:h});}
  for(const [key,job]of activeJobs)if(now()-job.started>35000)activeJobs.delete(key);
  const pending=()=>new Response('Climate calculation in progress',{status:202,headers:{...headers,'Cache-Control':'no-store','Retry-After':'1','X-Climate-Cache':'pending'}});
  if(activeJobs.has(spec.key)||activeJobs.size>=maxConcurrent)return pending();
  const token={started:now()};activeJobs.set(spec.key,token);
  const work=async()=>{try{const buffer=await compute(spec);const parsed=new Uint16Array(buffer,32+Math.min(2048,85699-spec.part*2048)*26,Math.min(2048,85699-spec.part*2048));const partial=spec.params.aqenabled&&parsed.some(v=>v===0);const response=new Response(buffer,{headers:{...headers,...(partial?{'Cache-Control':'public, max-age=30','X-AQI-Coverage':'partial'}:{}),'X-Climate-Cache':'miss','Server-Timing':`climate;dur=${(now()-t).toFixed(1)}`}});if(cache&&!partial)await cache.put(key,response.clone());return response;}
   catch(e){console.error('Climate calculation failed: '+e.message);return new Response('Climate calculation temporarily unavailable',{status:502,headers:{...headers,'Cache-Control':'no-store','Retry-After':'2'}});}
   finally{if(activeJobs.get(spec.key)===token)activeJobs.delete(spec.key);}};
  if(background){ctx.waitUntil(work());return pending();}
  return work();
 }};
}
