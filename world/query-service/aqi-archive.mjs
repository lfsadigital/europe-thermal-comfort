import '../site/dist/air-quality-daily-core.js';
import {AQI_DATASET} from './aqi-dataset.mjs';
export async function loadAQIYear(year,part,fetcher=fetch,dataset=AQI_DATASET,cache=null){
 if(!dataset)throw Error('Daily AQI dataset is not published');
 const name=`aqi-daily-${year}-${part}.gz`,file=dataset.files[name];if(!file)throw Error('AQI archive part unavailable');
 const key=new Request('https://comfy-aqi-data.invalid/'+dataset.dataset+'/'+name);let r=cache&&await cache.match(key),cached=!!r;if(!r)r=await fetcher(dataset.data_url+name,{signal:AbortSignal.timeout(30000),headers:{'User-Agent':'ComfyDays/1.0 (+https://comfy.lfsadigital.com)'}});if(!r.ok)throw Error('Daily AQI source HTTP '+r.status);const payload=await r.arrayBuffer();
 if(payload.byteLength!==file.bytes)throw Error('Daily AQI archive length mismatch');
 const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',payload)),v=>v.toString(16).padStart(2,'0')).join('');if(hash!==file.sha256){if(cache&&cached)await cache.delete(key);throw Error('Daily AQI archive integrity mismatch');}
 let parsed;try{const buffer=await new Response(new Blob([payload]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();parsed=globalThis.AirQualityDailyCore.parse(buffer,{start:part*2048,n:Math.min(2048,85699-part*2048),year});}catch(error){if(cache&&cached)await cache.delete(key);throw error;}if(cache&&!cached)await cache.put(key,new Response(payload,{headers:{'Cache-Control':'public, max-age=31536000','Content-Type':'application/gzip'}}));return parsed;
}
export function createAQIDailyService({fetcher=fetch,dataset=AQI_DATASET,loadYear=null,archiveCache=null}={}){return {async fetch(request){
 const headers={'Content-Type':'application/json','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'};const q=new URL(request.url).searchParams,node=Number(q.get('node')),period=q.get('period'),limit=Number(q.get('max')??100);
 if(request.method!=='GET')return new Response('Method not allowed',{status:405,headers});
 if(!q.has('node')||!Number.isInteger(node)||node<0||node>=85699||!['recent','2023','2024','2025'].includes(period)||!Number.isFinite(limit)||limit<0||limit>500)return new Response('Invalid AQI point or period',{status:400,headers});
 try{const years=period==='recent'?[2023,2024,2025]:[Number(period)],values=[],monthly=Array.from({length:12},(_,month)=>({month,sum:0,count:0,within:0,calendar:0}));
  for(const year of years){const a=await (loadYear?loadYear(year,Math.floor(node/2048)):loadAQIYear(year,Math.floor(node/2048),fetcher,dataset,archiveCache)),days=[31,year===2024?29:28,31,30,31,30,31,31,30,31,30,31];let day=0;for(let m=0;m<12;m++)for(let d=0;d<days[m];d++,day++){const v=a.values[(node-a.start)*a.days+day];monthly[m].calendar++;if(Number.isFinite(v)&&v>=0){values.push(v);monthly[m].sum+=v;monthly[m].count++;monthly[m].within+=Number(v<=limit);}}}
  return Response.json({version:1,dataset:dataset?.dataset||'test',period,limit,count:values.length,calendar:years.reduce((n,y)=>n+(y===2024?366:365),0),maximum:values.length?Math.max(...values):null,mean:values.length?values.reduce((a,b)=>a+b,0)/values.length:null,within:values.filter(v=>v<=limit).length,months:monthly.map(m=>({...m,mean:m.count?m.sum/m.count:null}))},{headers:{...headers,'Cache-Control':'public, max-age=86400'}});
 }catch(e){console.error('Daily AQI point unavailable: '+e.message);return new Response('Daily AQI temporarily unavailable',{status:502,headers});}
}};}
