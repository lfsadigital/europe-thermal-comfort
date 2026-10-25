import AirCore from '../site/dist/air-quality-core.js';

// Cache only compact, validated historical summaries. No source arrays or
// request-owned promises/cache handles are retained across Worker invocations.
export function createAirQualityService({fetcher=fetch,cache=null,activeJobs=new Map()}={}){
 const headers={'Content-Type':'application/json','Cache-Control':'public, max-age=604800','X-Content-Type-Options':'nosniff'};
 const failure=(message,status)=>new Response(JSON.stringify({error:message}),{status,headers:{...headers,'Cache-Control':'no-store',...(status===503?{'Retry-After':'2'}:{})}});
 return {async fetch(request){
  if(request.method!=='GET')return failure('Use GET',405);
  const q=new URL(request.url).searchParams,rawLat=q.get('lat'),rawLon=q.get('lon'),lat=Number(rawLat),lon=Number(rawLon),period=q.get('period')||'mean';
  if(!rawLat?.trim()||!rawLon?.trim()||!Number.isFinite(lat)||!Number.isFinite(lon)||lat< -90||lat>90||lon< -180||lon>180||!AirCore.yearsFor(period).length)return failure('Invalid air-quality location or period',400);
  const latitude=Number(lat.toFixed(4)),longitude=Number(lon.toFixed(4));
  const key=new Request(`https://comfy-air-quality-cache.invalid/cams-global-us-aqi-v1/${latitude}/${longitude}/${period}`);
  const hit=cache&&await cache.match(key);if(hit)return hit;
  // Only timestamps cross invocations; each invocation owns its fetches.
  for(const [k,time]of activeJobs)if(Date.now()-time>150000)activeJobs.delete(k);
  if(activeJobs.has(key.url)||activeJobs.size>=2)return failure('Air-quality checks are busy. Try again shortly.',503);
  activeJobs.set(key.url,Date.now());
  try{
   const records=[];
   for(const year of AirCore.yearsFor(period)){
    const url=new URL('https://air-quality-api.open-meteo.com/v1/air-quality');
    for(const [k,v]of Object.entries({latitude,longitude,start_date:`${year}-01-01`,end_date:`${year}-12-31`,hourly:'us_aqi,pm2_5',domains:'cams_global',timezone:'UTC'}))url.searchParams.set(k,v);
    const r=await fetcher(url,{signal:AbortSignal.timeout(45000)});if(!r.ok)throw Error('Air-quality source HTTP '+r.status);
    records.push(AirCore.validate(await r.json(),year));
   }
   const summary=AirCore.aggregate(records,period);
   const response=new Response(JSON.stringify({version:1,latitude,longitude,...summary}),{headers});
   if(cache)await cache.put(key,response.clone());return response;
  }catch(error){console.error('Air-quality summary unavailable: '+error.message);return failure('Historical air quality is temporarily unavailable.',502);}
  finally{activeJobs.delete(key.url);}
 }};
}
