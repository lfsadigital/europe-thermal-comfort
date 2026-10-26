'use strict';
// Optional daily comfort rule. A single map period drives every weather metric.
class AirQuality {
 constructor(){
  this.root=document.getElementById('air-quality');this.toggle=document.getElementById('aq-enabled');this.maximumInput=document.getElementById('aq-max');this.content=document.getElementById('aq-content');this.status=document.getElementById('aq-status');this.results=document.getElementById('aq-results');this.retry=document.getElementById('aq-retry');this.enabled=false;this.maximum=100;this.id=0;this.location=null;
  const q=new URLSearchParams(location.search);this.toggle.checked=q.get('aqi')==='1';this.maximumInput.value=[50,100,150,200,300,500].includes(Number(q.get('aqmax')))?q.get('aqmax'):'100';this.maximumInput.disabled=!this.toggle.checked;
  this.toggle.addEventListener('change',()=>{this.maximumInput.disabled=!this.toggle.checked;this.previewPeriod();window.ComfyDays?.ui.refresh();});this.maximumInput.addEventListener('change',()=>window.ComfyDays?.ui.refresh());
  document.getElementById('aq-settings').onclick=()=>{window.ComfyDays.ui.open('weather');this.toggle.focus({preventScroll:true});};this.retry.onclick=()=>this.refresh();
 }
 get pending(){return this.toggle.checked!==this.enabled||this.toggle.checked&&Number(this.maximumInput.value)!==this.maximum;}
 apply(p){this.enabled=Boolean(p.aqenabled);this.maximum=p.aqmax;this.toggle.checked=this.enabled;this.maximumInput.value=String(this.maximum);this.maximumInput.disabled=!this.enabled;this.refresh();}
 reset(){this.apply({aqenabled:false,aqmax:100});}
 appendURL(q){if(this.enabled){q.set('aqi','1');q.set('aqmax',this.maximum);}}
 previewPeriod(){const period=this.appliedPeriod,label=period==='recent'?'2023–2025':period==='mean'?'2020–2025':period||'selected';document.getElementById('aq-period-note').textContent=this.toggle.checked&&['mean','2020','2021','2022'].includes(period)?'Apply will switch all weather metrics to 2023–2025.':`Uses the map period: ${label}. AQI supports 2023–2025.`;}
 syncPeriod(period){const changed=period!==this.appliedPeriod;this.appliedPeriod=period;const label=period==='recent'?'2023–2025':period==='mean'?'2020–2025':period;document.getElementById('aq-period-note').textContent=`Uses the map period: ${label}. AQI supports 2023–2025.`;const select=document.getElementById('period');for(const o of select.options)o.disabled=this.enabled&&['mean','2020','2021','2022'].includes(o.value);this.previewPeriod();if(changed&&this.enabled&&this.location)this.refresh();}
 select(node,lat,lon){const key=[node,lat,lon].join('|');if(this.key===key)return;this.key=key;this.location={node,lat,lon};document.getElementById('aq-place').textContent=`Climate cell · ${lat.toFixed(2)}°, ${lon.toFixed(2)}°`;this.refresh();}
 clear(){this.location=null;this.key='';document.getElementById('aq-place').textContent='Select a city or click the map.';this.refresh();}
 description(){return `Daily AQI ≤${this.maximum} · maximum 3-hour mean · −1 point per 50 above limit`;}
 async refresh(){
  const id=++this.id;this.controller?.abort();this.controller=new AbortController();this.root.setAttribute('aria-busy','false');this.content.hidden=!this.enabled;this.results.replaceChildren();this.results.hidden=true;this.retry.hidden=true;
  if(!this.enabled)return;
  if(!this.location||this.location.node<0){this.status.textContent='Select a location to inspect the daily AQI used in its comfort calculation.';return;}
  this.status.textContent='Loading daily AQI for this climate cell…';this.root.setAttribute('aria-busy','true');
  try{const url=new URL('api/aqi/daily/v1',location.href);url.searchParams.set('node',this.location.node);url.searchParams.set('period',this.appliedPeriod);url.searchParams.set('max',this.maximum);const r=await fetch(url,{signal:AbortSignal.any([this.controller.signal,AbortSignal.timeout(45000)])});if(!r.ok)throw Error('Daily AQI unavailable');const d=await r.json();if(id!==this.id)return;if(d.version!==1||d.period!==this.appliedPeriod||d.limit!==this.maximum||!Number.isInteger(d.count)||d.count<0||d.count>d.calendar||!Array.isArray(d.months)||d.months.length!==12)throw Error('Invalid daily AQI summary');this.render(d);
  }catch(e){if(id!==this.id||e.name==='AbortError')return;this.status.textContent='AQI could not load. Missing AQI adds no penalty and does not exclude this location.';this.retry.hidden=false;}
  finally{if(id===this.id)this.root.setAttribute('aria-busy','false');}
 }
 render(d){
  const el=(tag,text)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;return e;},fmt=v=>v===null?'Not available':Number(v).toLocaleString('en',{maximumFractionDigits:1});
  this.status.textContent=`${d.count} / ${d.calendar} days with AQI. ${d.calendar-d.count} days without AQI: no penalty; air quality not verified.`;
  const stats=el('dl');stats.className='aq-stats';for(const [label,value]of [['Days within your AQI limit',`${d.within} / ${d.count}`],['Mean of daily maximum 3-hour AQI',fmt(d.mean)]]){const row=el('div');row.append(el('dt',label),el('dd',value));stats.append(row);}this.results.append(stats,el('p','AQI-only counts. A Comfy Day must also meet your temperature, rain and optional sunshine rules.'));
  const details=el('details'),scroll=el('div'),table=el('table'),head=el('thead'),tr=el('tr');details.append(el('summary','View monthly AQI'));scroll.className='aq-table-scroll';scroll.tabIndex=0;scroll.setAttribute('role','region');scroll.setAttribute('aria-label','Monthly daily AQI table');table.append(el('caption','UTC days · daily maximum of complete 3-hour means · at least 22 valid hourly values'));
  for(const text of ['Month','Mean daily AQI','Days ≤ your limit','Days with AQI','Calendar days']){const th=el('th',text);th.scope='col';tr.append(th);}head.append(tr);table.append(head);const body=el('tbody');d.months.forEach((m,i)=>{const row=el('tr');for(const text of [['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][i],fmt(m.mean),m.within,m.count,m.calendar])row.append(el('td',String(text)));body.append(row);});table.append(body);scroll.append(table);details.append(scroll);this.results.append(details);this.results.hidden=false;
 }
}
window.AirQuality=AirQuality;
