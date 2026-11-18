// Synthetic complete hourly records for deterministic tests, never shipped.
module.exports=function fixture(year=2025,aqi=42,pm=8){
 const start=Date.UTC(year,0,1),hours=(Date.UTC(year+1,0,1)-start)/3600000;
 return {latitude:38.8,longitude:-9.2,utc_offset_seconds:0,hourly_units:{us_aqi:'USAQI',pm2_5:'μg/m³'},hourly:{time:Array.from({length:hours},(_,i)=>new Date(start+i*3600000).toISOString().slice(0,16)),us_aqi:Array(hours).fill(aqi),pm2_5:Array(hours).fill(pm)}};
};
