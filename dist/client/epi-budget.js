'use strict';
class EPIBudget {
 constructor(onChange) {
  this.onChange=onChange; this.region='world'; this.ready=false; this.loading=false; this.error=false;
  this.box=document.getElementById('epi-budget-fieldset');
  this.toggle=document.getElementById('epi-enabled'); this.input=document.getElementById('epi-max');
  this.slider=document.getElementById('epi-max-slider'); this.status=document.getElementById('epi-status');
  const q=new URLSearchParams(location.search),value=Number(q.get('epimax'));
  this.toggle.checked=q.get('epi')==='1';
  if(q.has('epimax')&&Number.isFinite(value)&&value>=0&&value<=100000)this.input.value=value;
  const changed=()=>{this.sync();window.ComfyDays?.ui.refresh();clearTimeout(this.timer);this.timer=setTimeout(onChange,120);};
  this.toggle.addEventListener('change',()=>{this.sync();onChange();});
  this.input.addEventListener('input',changed);
  this.slider.addEventListener('input',()=>{this.input.value=this.slider.value;changed();});
  document.getElementById('epi-retry').onclick=()=>this.load();
  this.sync();
 }
 setRegion(region){this.region=region;this.box.hidden=region!=='usa';this.sync();if(region==='usa'&&!this.ready&&!this.loading&&!this.error)this.load();}
 get state(){return {epi:this.region==='usa'&&this.toggle.checked,budget:this.input.value===''?NaN:Number(this.input.value)};}
 valid(s=this.state){return !s.epi||Number.isFinite(s.budget)&&s.budget>=0&&s.budget<=100000;}
 sync(){this.input.disabled=this.slider.disabled=!this.toggle.checked;this.slider.value=this.input.value;
  this.status.textContent=!this.valid()?'Enter a budget from $0 to $100,000.':this.loading?'Loading regional budgets…':this.error?'Regional budgets unavailable. Unknown cities are kept.':this.ready?'EPI 2026 · 2025 dollars · regional estimate.':'';
  document.getElementById('epi-retry').hidden=!this.error;
 }
 reset(){clearTimeout(this.timer);this.toggle.checked=false;this.input.value=5000;this.sync();}
 async load(){if(this.loading)return;this.loading=true;this.error=false;this.sync();
  try{const r=await fetch('assets/epi-budget.json.gz?v=23');if(!r.ok)throw Error('EPI download failed');
   const data=await new Response(r.body.pipeThrough(new DecompressionStream('gzip'))).json();
   if(data.family_code!=='1p0c'||data.currency!=='USD'||data.price_year!==2025||!data.counties||!data.city_counties)throw Error('Unexpected EPI profile');
   this.data=data;this.ready=true;
  }catch(e){this.error=true;this.ready=false;}finally{this.loading=false;this.sync();this.onChange();}
 }
 record(place){if(!this.ready||place[5]!=='United States')return null;const fips=this.data.city_counties[String(place[0])],row=this.data.counties[fips];
  if(!row)return null;return {fips,name:row[0],state:row[1],monthly:row[2],annual:row[3],components:row.slice(4)};
 }
 assessment(place,s=this.state){if(!s.epi)return {failures:[],missing:[]};const r=this.record(place);
  if(!r)return {failures:[],missing:['EPI regional budget Unknown']};
  return {failures:r.monthly>s.budget?[`Regional budget $${Math.round(r.monthly).toLocaleString('en')} > $${s.budget.toLocaleString('en')}/month`]:[],missing:[]};
 }
 description(s=this.state){return s.epi?[`EPI regional budget ≤$${s.budget.toLocaleString('en')}/mo · 1 adult, no children · 2025 USD`]:[];}
 detailText(place){if(this.region!=='usa')return '';const r=this.record(place);return r?`EPI: $${Math.round(r.monthly).toLocaleString('en')}/month · ${r.name}, ${r.state} · regional estimate, 2025 USD`:'EPI regional budget: Unknown';}
 details(place,add){if(this.region!=='usa'||place[5]!=='United States')return;const r=this.record(place);
  const desc=add('Monthly budget · regional',r?`$${r.monthly.toLocaleString('en',{maximumFractionDigits:0})} USD · ${r.name}, ${r.state}`:'Unknown','EPI','https://www.epi.org/resources/budget/');
  const note=document.createElement('small');note.textContent='1 adult, no children · 2025 dollars · includes taxes. County estimate, not a city or neighborhood price.';desc.append(note);
  if(r){const details=document.createElement('details'),summary=document.createElement('summary'),list=document.createElement('dl');summary.textContent='Budget breakdown';
   ['Housing','Food','Transport','Healthcare','Other necessities','Childcare','Taxes'].forEach((label,i)=>{const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=label;dd.textContent='$'+r.components[i].toLocaleString('en',{maximumFractionDigits:0});list.append(dt,dd);});
   const foot=document.createElement('small');foot.textContent='Published total retained; rounded components may differ slightly.';details.append(summary,list,foot);desc.append(details);
  }
 }
}
window.EPIBudget=EPIBudget;
