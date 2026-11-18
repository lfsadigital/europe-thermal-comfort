'use strict';
class UrbanDensity {
 constructor(){this.data=null;this.pending=null;this.selection=0;}
 async select(place){
  const id=++this.selection,box=document.getElementById('urban-density-value');
  document.getElementById('urban-density-area').textContent='';box.textContent=place?'Loading…':'Unknown';if(!place)return;
  try{
   if(!this.data){
    this.pending??=fetch('assets/urban-density.json.gz?v=24').then(async r=>{if(!r.ok)throw Error('Urban density unavailable');return JSON.parse(await new Response(r.body.pipeThrough(new DecompressionStream('gzip'))).text());}).catch(e=>{this.pending=null;throw e;});
    this.data=await this.pending;
   }
   if(id!==this.selection)return;
   const row=this.data.cities[String(place[0])];
   box.textContent=row?`${Math.round(row[2]).toLocaleString('en')} people / km²`:'Unknown';
   document.getElementById('urban-density-area').textContent=row?`${row[1]} urban centre · 2025 estimate`:'No urban-centre match for this listed city';
  }catch(e){if(id===this.selection){box.textContent='Unavailable';document.getElementById('urban-density-area').textContent='Select this location again to retry';}}
 }
}
window.UrbanDensity=UrbanDensity;
