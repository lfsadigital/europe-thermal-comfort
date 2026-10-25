importScripts('monthly-core.js?v=26');
let active=0,controller,cellCache=new Map();
const fields=['temperature','meanTemperature','minimumTemperature','humidity','hotNights','precipitation','sunshine'];
async function directMonths(latitude,longitude,period,params,signal){
 const url=new URL('https://archive-api.open-meteo.com/v1/archive');for(const [k,v]of Object.entries({latitude,longitude,start_date:'2020-01-01',end_date:'2025-12-31',models:'era5',hourly:'temperature_2m',daily:'temperature_2m_max,temperature_2m_mean,temperature_2m_min,relative_humidity_2m_mean,precipitation_sum,sunshine_duration',timezone:'UTC',elevation:'nan',cell_selection:'nearest'}))url.searchParams.set(k,v);
 const response=await fetch(url,{cache:'no-store',signal});if(!response.ok)throw Error('Monthly climate source unavailable');const data=await response.json();if(data.utc_offset_seconds!==0||Math.abs(data.latitude-latitude)>1e-6||Math.abs(data.longitude-longitude)>1e-6)throw Error('Monthly climate cell mismatch');const records=MonthlyCore.fromAPI(data),selected=period==='mean'?records:records.filter(r=>r.year===Number(period));return MonthlyCore.aggregate(selected,params).map(m=>Object.fromEntries(['month',...fields].map(k=>[k,m[k]])));
}
onmessage=async({data:{id,node,period,params,latitude,longitude}})=>{
 active=id;controller?.abort();controller=new AbortController();const signal=controller.signal,key=JSON.stringify([node,period,latitude,longitude]);
 try{let months=cellCache.get(key);if(!months){const url=new URL('api/monthly/v1',self.location.href);url.searchParams.set('lat',latitude);url.searchParams.set('lon',longitude);url.searchParams.set('period',period);
  try{const response=await fetch(url,{signal:AbortSignal.any([signal,AbortSignal.timeout(4000)])});if(!response.ok)throw Error('Monthly climate service unavailable');const data=await response.json();if(data.version!==1||data.latitude!==latitude||data.longitude!==longitude||data.period!==period||!Array.isArray(data.months)||data.months.length!==12||data.months.some((m,i)=>m.month!==i||fields.some(k=>m[k]!==null&&!Number.isFinite(m[k]))))throw Error('Invalid monthly climate response');months=data.months;}
  catch(e){if(signal.aborted)throw e;months=await directMonths(latitude,longitude,period,params,signal);}
  if(id!==active)return;cellCache.set(key,months);while(cellCache.size>12)cellCache.delete(cellCache.keys().next().value);}
 postMessage({id,node,period,months});
 }catch(e){if(id===active&&e.name!=='AbortError')postMessage({id,error:e.message});}
};
