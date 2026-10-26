(function(root){
'use strict';
const valid=v=>typeof v==='number'&&Number.isFinite(v)&&v>=0;
function daily(hours){
 if(hours?.length!==24)throw Error('AQI day requires 24 UTC hourly slots');
 if(Array.from(hours).filter(valid).length<22)return NaN;
 let maximum=-Infinity;
 for(let i=0;i<=21;i++)if(valid(hours[i])&&valid(hours[i+1])&&valid(hours[i+2]))maximum=Math.max(maximum,(hours[i]+hours[i+1]+hours[i+2])/3);
 return Number.isFinite(maximum)?maximum:NaN;
}
function penalty(value,limit){if(!Number.isFinite(limit)||limit<0||limit>500)throw Error('Invalid AQI limit');return valid(value)?Math.max(0,(value-limit)/50):0;}
function parse(buffer,{start,n,year}={}){
 if(!(buffer instanceof ArrayBuffer)||buffer.byteLength<32)throw Error('Invalid daily AQI archive');
 const h=new Uint32Array(buffer,0,8),days=h[5]===2024?366:365;
 if(h[0]!==0x41514431||h[1]!==1||!h[3]||h[3]>2048||h[2]+h[3]>85699||h[4]!==days||![2023,2024,2025].includes(h[5])||h[6]!==3||h[7]!==22||buffer.byteLength!==32+h[3]*days*8||start!==undefined&&h[2]!==start||n!==undefined&&h[3]!==n||year!==undefined&&h[5]!==year)throw Error('Daily AQI archive grid/year mismatch');
 const values=new Float64Array(buffer,32);for(const v of values)if(!Number.isNaN(v)&&!valid(v))throw Error('Invalid daily AQI value');
 return {start:h[2],n:h[3],days,year:h[5],values};
}
root.AirQualityDailyCore={daily,penalty,parse};if(typeof module!=='undefined')module.exports=root.AirQualityDailyCore;
})(globalThis);
