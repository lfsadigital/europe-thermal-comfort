'use strict';
class AirQuality {
 constructor(){
  this.root=document.getElementById('air-quality');this.toggle=document.getElementById('aq-enabled');this.period=document.getElementById('aq-period');this.content=document.getElementById('aq-content');this.status=document.getElementById('aq-status');this.results=document.getElementById('aq-results');this.retry=document.getElementById('aq-retry');
  this.id=0;this.cache=new Map();this.location=null;this.key='';
  const q=new URLSearchParams(location.search);this.toggle.checked=q.get('aqi')==='1';this.period.value=AirQualityCore.yearsFor(q.get('aqiyear')).length?q.get('aqiyear'):'mean';
  this.toggle.addEventListener('change',()=>{this.saveURL();this.refresh();});this.period.addEventListener('change',()=>{this.saveURL();this.refresh();});this.retry.addEventListener('click',()=>this.refresh());this.refresh();
 }
 appendURL(q){if(this.toggle.checked){q.set('aqi','1');if(this.period.value!=='mean')q.set('aqiyear',this.period.value);}}
 saveURL(){const q=new URLSearchParams(location.search);q.delete('aqi');q.delete('aqiyear');this.appendURL(q);history.replaceState(null,'','?'+q);}
 select(lat,lon){const key=JSON.stringify([lat,lon]);this.location={lat,lon};document.getElementById('aq-place').textContent=`Selected point · ${lat.toFixed(2)}°, ${lon.toFixed(2)}°`;if(this.key===key)return;this.key=key;this.refresh();}
 clear(){this.location=null;this.key='';document.getElementById('aq-place').textContent='Select a city or click the map.';this.refresh();}
 message(text){this.status.textContent=text;}
 async refresh(){
  const id=++this.id;this.controller?.abort();this.controller=new AbortController();const controller=this.controller;this.results.hidden=true;this.results.replaceChildren();this.retry.hidden=true;this.root.setAttribute('aria-busy','false');this.content.hidden=!this.toggle.checked;
  if(!this.toggle.checked)return;
  if(!this.location){this.message('Select a city or click the map to explore its air quality history.');return;}
  const {lat,lon}=this.location,period=this.period.value,key=JSON.stringify([lat,lon,period]),cached=this.cache.get(key);
  if(cached){this.cache.delete(key);this.cache.set(key,cached);this.render(cached);return;}
  const years=AirQualityCore.yearsFor(period),records=[];this.root.setAttribute('aria-busy','true');
  try{
   for(const year of years){
    this.message(`Loading air quality · ${year} (${records.length+1} of ${years.length})…`);
    const url=new URL('https://air-quality-api.open-meteo.com/v1/air-quality');
    for(const [k,v]of Object.entries({latitude:lat,longitude:lon,start_date:`${year}-01-01`,end_date:`${year}-12-31`,hourly:'us_aqi,pm2_5',domains:'cams_global',timezone:'UTC'}))url.searchParams.set(k,v);
    let timedOut=false;const timeout=setTimeout(()=>{timedOut=true;controller.abort();},45000);
    try{const response=await fetch(url,{signal:controller.signal,cache:'no-store'});if(!response.ok)throw Error('Air quality request failed');const record=await response.json();if(id!==this.id)return;records.push(AirQualityCore.validate(record,year));}
    finally{clearTimeout(timeout);if(timedOut)throw Error('Air quality request timed out');}
   }
   if(id!==this.id)return;
   const summary=AirQualityCore.aggregate(records,period);this.cache.set(key,summary);while(this.cache.size>12)this.cache.delete(this.cache.keys().next().value);this.render(summary);
  }catch(error){if(id!==this.id)return;this.message('Air quality could not load. Check your connection and try again.');this.retry.hidden=false;}
  finally{if(id===this.id)this.root.setAttribute('aria-busy','false');}
 }
 render(summary){
  const {aqi,pm,months}=summary,fmt=n=>n.toLocaleString('en',{maximumFractionDigits:1}),pct=(n,d)=>d?fmt(n/d*100)+'%':'—';
  this.message(`${summary.period==='mean'?'2023–2025':summary.period} · ${fmt(aqi.count)} / ${fmt(aqi.expected)} hourly AQI values (${pct(aqi.count,aqi.expected)})${aqi.eligible?'':'. Insufficient coverage: at least 90% is required in every month of each year.'}`);
  const el=(tag,text,cls)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e;};
  const stats=el('dl',undefined,'aq-stats');
  for(const [label,value]of [['Median hourly US AQI',aqi.eligible&&aqi.median!==null?fmt(aqi.median):'Not available'],['Mean PM2.5 · µg/m³',pm.eligible&&pm.mean!==null?fmt(pm.mean):'Not available']]){const row=el('div');row.append(el('dt',label),el('dd',value));stats.append(row);}this.results.append(stats);
  this.results.append(el('p',`PM2.5 coverage: ${fmt(pm.count)} / ${fmt(pm.expected)} hours (${pct(pm.count,pm.expected)}).`,'aq-note'));
  const heading=el('h3','Time in each AQI category');this.results.append(heading,el('p','Share of available hourly values. Lower AQI means less air pollution.','aq-note'));
  const list=el('ul',undefined,'aq-distribution');
  AirQualityCore.bands.forEach((band,i)=>{const row=el('li'),label=el('span',band.label),range=el('span',band.range,'aq-range'),share=el('strong',aqi.eligible?pct(aqi.bands[i],aqi.count):'Not available'),track=el('span',undefined,'aq-track'),fill=el('span');label.className='aq-band';label.style.setProperty('--aq-band-color',band.color);fill.style.width=(aqi.eligible&&aqi.count?aqi.bands[i]/aqi.count*100:0)+'%';track.setAttribute('aria-hidden','true');track.append(fill);row.append(label,range,share,track);list.append(row);});this.results.append(list);
  const disclosure=el('details'),caption=el('summary','View monthly values'),scroll=el('div',undefined,'aq-table-scroll'),table=el('table'),head=el('thead'),header=el('tr');
  table.append(el('caption',`${summary.period==='mean'?'2023–2025 pooled months':summary.period} · available hourly model values`));
  for(const label of ['Month','Median US AQI','Good hours · %','PM2.5 · µg/m³','AQI hours','PM2.5 hours']){const cell=el('th',label);cell.scope='col';header.append(cell);}head.append(header);table.append(head);const body=el('tbody');
  months.forEach((m,i)=>{const row=el('tr'),month=el('th',['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][i]);month.scope='row';row.append(month);for(const value of [m.aqi.eligible?fmt(m.aqi.median):'Not available',m.aqi.eligible?pct(m.aqi.bands[0],m.aqi.count):'Not available',m.pm.eligible?fmt(m.pm.mean):'Not available',`${fmt(m.aqi.count)} / ${fmt(m.aqi.expected)}`,`${fmt(m.pm.count)} / ${fmt(m.pm.expected)}`])row.append(el('td',value));body.append(row);});table.append(body);scroll.tabIndex=0;scroll.setAttribute('role','region');scroll.setAttribute('aria-label','Scrollable monthly air quality table');scroll.append(table);disclosure.append(caption,scroll);this.results.append(disclosure);
  const cells=[...new Set(summary.cells.map(c=>`${c.latitude.toFixed(2)}°, ${c.longitude.toFixed(2)}°`))];this.results.append(el('p',`Provider-returned coordinates: ${cells.join('; ')}. UTC hours · ${summary.years.join(', ')}.`,'aq-note'));this.results.hidden=false;
 }
}
window.AirQuality=AirQuality;
