import '../site/dist/monthly-core.js';
import {REVISION} from './query-core.mjs';
const fields=['temperature','meanTemperature','minimumTemperature','humidity','hotNights','precipitation','sunshine'];
export function createMonthlyService({fetcher=fetch,cache=null,activeJobs=new Map()}={}){
 return {async fetch(request,ctx={waitUntil:()=>{}}){
  const headers={'Content-Type':'application/json','Cache-Control':'public, max-age=604800','Access-Control-Allow-Origin':'*','X-Content-Type-Options':'nosniff'};
  if(request.method!=='GET')return new Response('Method not allowed',{status:405,headers:{...headers,'Cache-Control':'no-store'}});
  const q=new URL(request.url).searchParams,lat=Number(q.get('lat')),lon=Number(q.get('lon')),period=q.get('period')||'mean';
  if(!q.has('lat')||!q.has('lon')||!Number.isFinite(lat)||!Number.isFinite(lon)||lat< -90||lat>90||lon< -180||lon>180||!Number.isInteger(lat*4)||!Number.isInteger(lon*4)||!['mean','2020','2021','2022','2023','2024','2025'].includes(period))return new Response('Invalid climate cell',{status:400,headers:{...headers,'Cache-Control':'no-store'}});
  const key=new Request(`https://comfy-monthly-cache.invalid/${REVISION}/${lat}/${lon}/${period}`),hit=cache&&await cache.match(key);if(hit)return hit;
  for(const [key,started]of activeJobs)if(Date.now()-started>65000)activeJobs.delete(key);
  if(activeJobs.size)return new Response('Monthly records are loading',{status:503,headers:{...headers,'Cache-Control':'no-store','Retry-After':'1'}});
  activeJobs.set(key.url,Date.now());
  try{
   const url=new URL('https://archive-api.open-meteo.com/v1/archive');for(const [k,v]of Object.entries({latitude:lat,longitude:lon,start_date:'2020-01-01',end_date:'2025-12-31',models:'era5',hourly:'temperature_2m',daily:'temperature_2m_max,temperature_2m_mean,temperature_2m_min,relative_humidity_2m_mean,precipitation_sum,sunshine_duration',timezone:'UTC',elevation:'nan',cell_selection:'nearest'}))url.searchParams.set(k,v);
   const r=await fetcher(url,{signal:AbortSignal.timeout(60000)});if(!r.ok)throw Error('Monthly API returned '+r.status);const data=await r.json();if(data.utc_offset_seconds!==0||Math.abs(data.latitude-lat)>1e-6||Math.abs(data.longitude-lon)>1e-6)throw Error('Monthly cell mismatch');
   const records=globalThis.MonthlyCore.fromAPI(data),selected=period==='mean'?records:records.filter(r=>r.year===Number(period)),months=globalThis.MonthlyCore.aggregate(selected,{lower:14,upper:30,lowenabled:true,lowmin:14,lowmax:30,rain0:4,sunenabled:false}).map(m=>Object.fromEntries(['month',...fields].map(k=>[k,m[k]])));
   const response=new Response(JSON.stringify({version:1,latitude:lat,longitude:lon,period,months}),{headers});if(cache)await cache.put(key,response.clone());return response;
  }catch(e){console.error('Monthly climate request failed: '+e.message);return new Response('Monthly records temporarily unavailable',{status:502,headers:{...headers,'Cache-Control':'no-store'}});}
  finally{activeJobs.delete(key.url);}
 }};
}
