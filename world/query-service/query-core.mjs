import '../site/dist/sunshine-core.js';
import '../site/dist/daily-temperature-core.js';

// The revision is part of every cache key; changing the archive or formula invalidates results.
export const REVISION='era5-2020-2025-bounds-v1';
export const NODES=85699, CHUNK_SIZE=2048, PARTS=Math.ceil(NODES/CHUNK_SIZE);
const fields=['lower','upper','rain0','rain1','rain2','pen1','pen2','pen3','drymax','sunenabled','sunmin','lowenabled','lowmin','lowmax'];
export function parseQuery(url){
 const q=new URL(url).searchParams,part=Number(q.get('part')),period=q.get('period')||'mean';
 if(!q.has('part')||!Number.isInteger(part)||part<0||part>=PARTS||!['mean','2020','2021','2022','2023','2024','2025'].includes(period))throw new Error('Invalid climate part or period');
 let raw;try{raw=JSON.parse(q.get('params'));}catch{throw new Error('Invalid weather rules');}
 if(!raw||typeof raw!=='object'||Object.keys(raw).some(k=>!fields.includes(k)))throw new Error('Invalid weather rules');
 const p=Object.fromEntries(fields.map(k=>[k,raw[k]]));
 if(fields.filter(k=>!['sunenabled','lowenabled'].includes(k)).some(k=>!Number.isFinite(p[k])))throw new Error('Invalid numeric rules');
 if(p.lowenabled!==true||typeof p.sunenabled!=='boolean'||p.lower!==p.lowmin||p.upper!==p.lowmax||!Number.isInteger(p.lower)||!Number.isInteger(p.upper)||p.lower< -30||p.upper>50||p.lower>=p.upper)throw new Error('Invalid temperature limits');
 if(!(0<=p.rain0&&p.rain0<p.rain1&&p.rain1<p.rain2&&p.rain2<=300&&p.drymax===p.rain0)||['rain0','rain1','rain2'].some(k=>Math.abs(p[k]*10-Math.round(p[k]*10))>1e-8))throw new Error('Invalid rain limits');
 if(!(0<=p.pen1&&p.pen1<=p.pen2&&p.pen2<=p.pen3&&p.pen3<=10)||['pen1','pen2','pen3'].some(k=>!Number.isInteger(p[k]*2)))throw new Error('Invalid rain losses');
 if(p.sunmin<0||p.sunmin>24||!Number.isInteger(p.sunmin*2))throw new Error('Invalid sunshine limit');
 if(!p.sunenabled)p.sunmin=6;
 return {part,period,params:p,key:JSON.stringify([REVISION,part,period,...fields.map(k=>p[k])])};
}
export function queryURL(base,part,period,params){const u=new URL(base);u.searchParams.set('part',part);u.searchParams.set('period',period);u.searchParams.set('params',JSON.stringify(params));return u;}
export async function calculatePart({part,period,params},loadYear){
 const start=part*CHUNK_SIZE,n=Math.min(CHUNK_SIZE,NODES-start),score=new Float64Array(n),days=new Float64Array(n),coverage=new Uint16Array(n),sunhours=new Float64Array(n),invalid=new Uint8Array(n);
 const years=period==='mean'?[2020,2021,2022,2023,2024,2025]:[Number(period)];let calendar=0;
 for(const year of years){
  const [c,min]=await loadYear(year,part);
  if(c.start!==start||c.n!==n||c.year!==year||min.start!==start||min.n!==n||min.year!==year)throw new Error('Climate archive cell/year mismatch');
  calendar+=c.days;
  for(let k=0;k<n;k++){const v=globalThis.DailyTemperatureCore.calculate(c,min,k,params);score[k]+=v.scoreSum;days[k]+=v.comfortable;coverage[k]+=v.count;sunhours[k]+=v.sunSecondsSum;if(!v.eligible)invalid[k]=1;}
 }
 for(let k=0;k<n;k++)if(invalid[k]||!coverage[k])score[k]=days[k]=sunhours[k]=NaN;else{score[k]=Math.min(10,Math.max(0,score[k]/coverage[k]));days[k]=days[k]/coverage[k]*calendar/years.length;sunhours[k]=sunhours[k]/coverage[k]/3600;}
 return {start,n,score,days,coverage,sunhours};
}
// All offsets are aligned. Float64 preserves the existing calculation output exactly.
export function encodePart(c){const b=new ArrayBuffer(32+c.n*32),h=new Uint32Array(b,0,8);h.set([0x43445131,1,c.start,c.n]);new Float64Array(b,32,c.n).set(c.score);new Float64Array(b,32+c.n*8,c.n).set(c.days);new Float64Array(b,32+c.n*16,c.n).set(c.sunhours);new Uint16Array(b,32+c.n*24,c.n).set(c.coverage);return b;}
