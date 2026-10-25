(function(root){
'use strict';
function parse(buffer,{nodes=85699,start=null,n=null}={}){
 if(!(buffer instanceof ArrayBuffer)||buffer.byteLength<32)throw Error('Invalid climate response');
 const h=new Uint32Array(buffer,0,8),from=h[2],count=h[3];
 if(h[0]!==0x43445131||h[1]!==1||!count||from+count>nodes||buffer.byteLength!==32+count*32||start!==null&&from!==start||n!==null&&count!==n)throw Error('Climate response grid mismatch');
 const score=new Float64Array(buffer,32,count),days=new Float64Array(buffer,32+count*8,count),sunhours=new Float64Array(buffer,32+count*16,count),coverage=new Uint16Array(buffer,32+count*24,count);
 for(let i=0;i<count;i++)if((!Number.isNaN(score[i])&&(!Number.isFinite(score[i])||score[i]<0||score[i]>10))||(!Number.isNaN(days[i])&&(!Number.isFinite(days[i])||days[i]<0||days[i]>366))||coverage[i]>2192)throw Error('Invalid climate result values');
 return {start:from,n:count,score,days,sunhours,coverage};
}
root.ClimateResult={parse};if(typeof module!=='undefined')module.exports=root.ClimateResult;
})(globalThis);
