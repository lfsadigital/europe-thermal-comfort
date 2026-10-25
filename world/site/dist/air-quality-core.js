'use strict';
// The provider calculates US AQI. Never infer it from a mean PM2.5 value.
(function(root){
 const bands=Object.freeze([
  {label:'Good',range:'0–50',max:50,color:'#18794e'},
  {label:'Moderate',range:'>50–100',max:100,color:'#947000'},
  {label:'Unhealthy for sensitive groups',range:'>100–150',max:150,color:'#b65300'},
  {label:'Unhealthy',range:'>150–200',max:200,color:'#c53030'},
  {label:'Very unhealthy',range:'>200–300',max:300,color:'#8054a0'},
  {label:'Hazardous',range:'>300',max:Infinity,color:'#7e2344'}
 ].map(Object.freeze));
 const valid=v=>typeof v==='number'&&Number.isFinite(v)&&v>=0;
 const category=v=>valid(v)?bands.findIndex(b=>v<=b.max):-1;
 const yearsFor=period=>period==='mean'?[2023,2024,2025]:['2023','2024','2025'].includes(String(period))?[Number(period)]:[];
 function validate(data,year){
  const h=data?.hourly,units=data?.hourly_units,start=Date.UTC(year,0,1),length=(Date.UTC(year+1,0,1)-start)/3600000;
  if(!yearsFor(String(year)).length||data?.utc_offset_seconds!==0||!Number.isFinite(data?.latitude)||!Number.isFinite(data?.longitude)||units?.us_aqi!=='USAQI'||!['μg/m³','µg/m³'].includes(units?.pm2_5))throw Error('Unexpected air quality metadata');
  if(!Array.isArray(h?.time)||!Array.isArray(h.us_aqi)||!Array.isArray(h.pm2_5)||[h.time,h.us_aqi,h.pm2_5].some(a=>a.length!==length))throw Error('Incomplete air quality time axis');
  for(let i=0;i<length;i++){
   if(h.time[i]!==new Date(start+i*3600000).toISOString().slice(0,16))throw Error('Unexpected air quality timestamp');
   if([h.us_aqi[i],h.pm2_5[i]].some(v=>v!==null&&!valid(v)))throw Error('Invalid air quality value');
  }
  return data;
 }
 function stats(values,expected,eligible){
  const finite=values.filter(valid),count=finite.length,sorted=finite.slice().sort((a,b)=>a-b),mid=Math.floor(count/2);
  return {count,expected,eligible,mean:count?finite.reduce((a,b)=>a+b,0)/count:null,median:count?(count%2?sorted[mid]:(sorted[mid-1]+sorted[mid])/2):null,bands:bands.map((_,i)=>finite.reduce((n,v)=>n+(category(v)===i),0))};
 }
 function aggregate(records,period){
  const years=yearsFor(period);
  if(!years.length||records.length!==years.length)throw Error('Unexpected air quality period');
  records.forEach((r,i)=>validate(r,years[i]));
  const months=Array.from({length:12},(_,month)=>{
   const aqi=[],pm=[],coverage=[];
   years.forEach((year,i)=>{
    const start=(Date.UTC(year,month,1)-Date.UTC(year,0,1))/3600000,expected=(Date.UTC(year,month+1,1)-Date.UTC(year,month,1))/3600000;
    const a=records[i].hourly.us_aqi.slice(start,start+expected),p=records[i].hourly.pm2_5.slice(start,start+expected);
    coverage.push({year,expected,aqi:a.filter(valid).length,pm:p.filter(valid).length});aqi.push(...a);pm.push(...p);
   });
   const expected=coverage.reduce((n,c)=>n+c.expected,0);
   return {month,coverage,aqi:stats(aqi,expected,coverage.every(c=>c.aqi/c.expected>=.9)),pm:stats(pm,expected,coverage.every(c=>c.pm/c.expected>=.9))};
  });
  const expected=months.reduce((n,m)=>n+m.aqi.expected,0);
  return {period,years,months,aqi:stats(records.flatMap(r=>r.hourly.us_aqi),expected,months.every(m=>m.aqi.eligible)),pm:stats(records.flatMap(r=>r.hourly.pm2_5),expected,months.every(m=>m.pm.eligible)),cells:records.map((r,i)=>({year:years[i],latitude:r.latitude,longitude:r.longitude}))};
 }
 const api={bands,valid,category,yearsFor,validate,aggregate};
 if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.AirQualityCore=api;
})(typeof window==='undefined'?globalThis:window);
