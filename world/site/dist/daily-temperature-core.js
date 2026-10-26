(function(root){
'use strict';
function temperatureLoss(high,low,p){
 const highLoss=Math.max(p.lower-high,0,high-p.upper);
 const lowLoss=p.lowenabled?Math.max(p.lowmin-low,0,low-p.lowmax):0;
 return .5*Math.max(highLoss,lowLoss);
}
function daily(high,low,rain,sun,p,aqi=NaN){
 if(!Number.isFinite(high)||!Number.isFinite(rain)||rain<0||p.lowenabled&&!Number.isFinite(low)||p.sunenabled&&(!Number.isFinite(sun)||sun<0))return null;
 const r=Math.round(rain*10),r0=Math.round(p.rain0*10),r1=Math.round(p.rain1*10),r2=Math.round(p.rain2*10);
 const rainLoss=r<=r0?0:r<=r1?p.pen1:r<=r2?p.pen2:p.pen3;
 const loss=temperatureLoss(high,low,p),sunLoss=p.sunenabled?.5*Math.max(0,p.sunmin-sun):0;
 const aqKnown=p.aqenabled&&typeof aqi==='number'&&Number.isFinite(aqi)&&aqi>=0,aqLoss=aqKnown?Math.max(0,(aqi-p.aqmax)/50):0;
 return {score:Math.max(0,10-loss-rainLoss-sunLoss-aqLoss),comfortable:high>=p.lower&&high<=p.upper&&(!p.lowenabled||low>=p.lowmin&&low<=p.lowmax)&&r<=r0&&(!p.sunenabled||sun>=p.sunmin)&&(!aqKnown||aqi<=p.aqmax)};
}
function parseMinimum(buffer){
 const h=new Uint32Array(buffer.slice(0,32));if(h[0]!==0x4d494e54||h[1]!==1||h[7]!==h[3]*h[4]||buffer.byteLength!==32+h[7]*4)throw Error('Invalid daily-minimum file');
 return {start:h[2],n:h[3],days:h[4],year:h[5],values:new Float32Array(buffer.slice(32))};
}
function calculate(c,min,k,p,aq=null){
 if(min.start!==c.start||min.n!==c.n||min.days!==c.days||min.year!==c.year)throw Error('Daily-minimum dates/cells differ from daily maxima');
 if(aq&&(aq.start!==c.start||aq.n!==c.n||aq.days!==c.days||aq.year!==c.year))throw Error('AQI dates/cells differ from climate');
 let aqCount=0;
 let scoreSum=0,comfortable=0,count=0,sunSecondsSum=0,eligible=true,month=0,monthCount=0,monthEnd=c.monthDays[0];
 for(let day=0;day<c.days;day++){
  const i=k*c.days+day,high=c.temperature[c.temperatureIndex[i]],low=min.values[i],rain=c.rain[i],seconds=c.sunshine[i];
  const v=rain===65535?null:daily(high,low,rain/10,seconds/3600,p,aq?.values[i]);
  if(v){if(p.aqenabled&&Number.isFinite(aq?.values[i])&&aq.values[i]>=0)aqCount++;scoreSum+=v.score;comfortable+=Number(v.comfortable);count++;monthCount++;if(Number.isFinite(seconds)&&seconds>=0)sunSecondsSum+=seconds;}
  if(day+1===monthEnd){if(monthCount<Math.ceil(c.monthDays[month]*.9))eligible=false;month++;monthCount=0;monthEnd+=c.monthDays[month]||0;}
 }
 return {scoreSum,comfortable,count,sunSecondsSum,eligible,aqCount};
}
root.DailyTemperatureCore={daily,temperatureLoss,parseMinimum,calculate};if(typeof module!=='undefined')module.exports=root.DailyTemperatureCore;
})(globalThis);
