'use strict';
// Export the actual map layers. No screenshot, zoom crop or recalculation is used.
function exportImage(url){const img=new Image();img.src=url;return img.decode().then(()=>img);}
async function exportMap(){
  const button=$('export-map'),notice=$('export-status');
  if(!state.ready||button.disabled||state.exporting)return;
  const snapshot={mode:state.mode,period:state.period,lower:state.lower,upper:state.upper,palette:[...state.meta.palette],request:state.request};
  const custom=snapshot.lower!==20||snapshot.upper!==25;
  // Copy the current raster before awaiting assets: later user changes cannot alter this export.
  let raster;
  if(custom){raster=document.createElement('canvas');raster.width=$('dynamic-map').width;raster.height=$('dynamic-map').height;raster.getContext('2d').drawImage($('dynamic-map'),0,0);}
  state.exporting=true;button.disabled=true;notice.textContent='Preparing your PNG…';
  try{
    const [logo,map,overlay]=await Promise.all([exportImage('logo.svg'),custom?Promise.resolve(raster):exportImage(`assets/${snapshot.mode}-${snapshot.period}.webp`),custom?exportImage('assets/map-overlay.png'):Promise.resolve(null)]);
    const canvas=document.createElement('canvas');canvas.width=2400;canvas.height=2700;
    const ctx=canvas.getContext('2d');ctx.fillStyle='#fff';ctx.fillRect(0,0,2400,2700);
    ctx.drawImage(logo,80,56,76,76);ctx.fillStyle='#183044';ctx.font='700 43px system-ui, sans-serif';ctx.fillText('Comfy Days',176,108);
    const days=snapshot.mode==='days',mean=snapshot.period==='mean';
    ctx.font='700 86px system-ui, sans-serif';ctx.fillText(days?'Where are the comfy days?':'How comfy are your days?',80,230);
    ctx.fillStyle='#536a7a';ctx.font='30px system-ui, sans-serif';
    ctx.fillText(`Europe · ${mean?'2020–2024 average':snapshot.period} · Highs ${snapshot.lower}–${snapshot.upper} °C · Rain ≤1 mm/day`,84,290);
    ctx.drawImage(map,80,320,2240,1960);if(overlay)ctx.drawImage(overlay,80,320,2240,1960);
    ctx.textAlign='center';ctx.fillStyle='#183044';ctx.font='600 32px system-ui, sans-serif';
    ctx.fillText(days?(mean?'Comfortable days per year':`Comfortable days in ${snapshot.period}`):'Average daily comfort score',1200,2340);
    const gradient=ctx.createLinearGradient(280,0,2120,0);snapshot.palette.forEach((colour,i)=>gradient.addColorStop(i/(snapshot.palette.length-1),colour));ctx.fillStyle=gradient;ctx.fillRect(280,2370,1840,26);
    const ticks=days?['0','30','60','90','120','150+']:['≤76','82','87','93','98+'];ctx.fillStyle='#536a7a';ctx.font='28px system-ui, sans-serif';ticks.forEach((tick,i)=>ctx.fillText(tick,280+1840*i/(ticks.length-1),2440));
    ctx.font='27px system-ui, sans-serif';ctx.fillText(days?`Highs ${snapshot.lower}–${snapshot.upper} °C AND rain ≤1 mm. ${mean?'Five-year count ÷ 5.':'Actual count for the selected year.'}`:`100 in ${snapshot.lower}–${snapshot.upper} °C; −1 per °C outside; −1 extra if rain >1 mm.`,1200,2500);
    ctx.fillStyle='#73838e';ctx.font='24px system-ui, sans-serif';ctx.fillText('Temperature + daily precipitation · Wind and humidity are not included',1200,2542);
    ctx.font='22px system-ui, sans-serif';ctx.fillText('E-OBS (Cornes et al., 2018) + NOAA CPC / PSL · Natural Earth · Non-commercial research & education',1200,2584);
    ctx.strokeStyle='#e2e8ec';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(80,2610);ctx.lineTo(2320,2610);ctx.stroke();
    ctx.textAlign='left';ctx.fillStyle='#06716a';ctx.font='600 27px system-ui, sans-serif';ctx.fillText('X @buildwithluiz   ·   IG @lfsadigital',80,2660);ctx.textAlign='right';ctx.font='22px system-ui, sans-serif';ctx.fillText(location.host,2320,2660);
    const blob=await new Promise((resolve,reject)=>canvas.toBlob(b=>b?resolve(b):reject(new Error('PNG creation failed.')),'image/png'));
    const url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download=`comfy-days-${days?'days':'score'}-${snapshot.period}-${snapshot.lower}-to-${snapshot.upper}C-rain-1mm.png`;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),60000);
    notice.textContent='PNG downloaded. Ready to post.';
  }catch(e){notice.textContent=`Could not export the map. ${e.message}`;console.error('Map export failed:',e.message);}
  finally{state.exporting=false;button.disabled=!state.ready;}
}
$('export-map').addEventListener('click',exportMap);
