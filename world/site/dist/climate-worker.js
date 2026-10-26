importScripts('climate-result.js?v=40');
// Only compact aggregate results reach the browser. Raw archives stay server-side.
let activeId=0,controller,queue=[];
onmessage=async({data:d})=>{
 if(d.type==='priority'){const index=queue.indexOf(d.part);if(index>=0)queue.unshift(...queue.splice(index,1));return;}
 controller?.abort();if(d.type==='cancel'){activeId=d.id;return;}
 const {id,period,params,nodes,endpoint='api/climate/v1',priority=null}=d;activeId=id;controller=new AbortController();const signal=controller.signal;
 const size=2048,parts=Math.ceil(nodes/size),score=new Float64Array(nodes),days=new Float64Array(nodes),coverage=new Uint16Array(nodes),aqCoverage=new Uint16Array(nodes),sunhours=new Float64Array(nodes);score.fill(NaN);days.fill(NaN);sunhours.fill(NaN);queue=Array.from({length:parts},(_,i)=>i);if(priority!==null&&queue.includes(priority))queue.unshift(...queue.splice(queue.indexOf(priority),1));let completed=0;
 async function run(){while(activeId===id&&queue.length){const part=queue.shift(),url=new URL(endpoint,self.location.href);url.searchParams.set('part',part);url.searchParams.set('period',period);url.searchParams.set('params',JSON.stringify(params));let response;
  for(let attempt=0;attempt<240;attempt++){response=await fetch(url,{signal});if(response.status===202||response.status===503){if(attempt===239)throw Error('Map update is taking longer than expected. Please try Apply again.');await new Promise(resolve=>setTimeout(resolve,1000));if(signal.aborted)throw new DOMException('Canceled','AbortError');continue;}if(response.ok||response.status<500||attempt>=2)break;await new Promise(resolve=>setTimeout(resolve,500));}
  if(!response.ok)throw Error('Map update unavailable. Please try Apply again.');
  const c=ClimateResult.parse(await response.arrayBuffer(),{nodes,start:part*size,n:Math.min(size,nodes-part*size)});if(id!==activeId)return;
  score.set(c.score,c.start);days.set(c.days,c.start);coverage.set(c.coverage,c.start);aqCoverage.set(c.aqCoverage,c.start);sunhours.set(c.sunhours,c.start);
  postMessage({id,partial:true,...c,progress:++completed/parts});
 }}
 try{await Promise.all(Array.from({length:4},run));if(activeId===id)postMessage({id,score,days,coverage,aqCoverage,sunhours},[score.buffer,days.buffer,coverage.buffer,aqCoverage.buffer,sunhours.buffer]);}
 catch(e){if(activeId===id){controller.abort();if(e.name!=='AbortError')postMessage({id,error:e.message});}}
};
