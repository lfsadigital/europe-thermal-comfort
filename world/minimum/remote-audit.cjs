'use strict';
const fs=require('node:fs'),path=require('node:path'),z=require('node:zlib'),assert=require('node:assert/strict'),cp=require('node:child_process');
const Low=require('./daily-temperature-core.js'),Sun=require('../site/dist/sunshine-core.js');
const root=path.resolve(__dirname,'..'),output=path.join(process.env.RUNNER_TEMP,'comfy-minimum-presets');fs.mkdirSync(output,{recursive:true});
const m=JSON.parse(fs.readFileSync(path.join(root,'site/dist/assets/metadata.json')));
// Buffer's byteOffset must be honored, regardless of Node's allocation pool.
const gridBuffer=fs.readFileSync(path.join(root,'site/dist/assets/node-grid.bin'));const nodeGrid=new Int32Array(gridBuffer.buffer,gridBuffer.byteOffset,gridBuffer.length/4);
const nodeToGrid=new Int32Array(m.nodes);nodeToGrid.fill(-1);for(let i=0;i<nodeGrid.length;i++)if(nodeGrid[i]>=0)nodeToGrid[nodeGrid[i]]=i;
const tag=process.argv[2],repo=process.env.GITHUB_REPOSITORY,base=`https://github.com/${repo}/releases/download/${tag}/`,n=m.nodes;
const params={...m.default,lowenabled:true,lowmin:12,lowmax:22,sunenabled:false,sunmin:6},off={...params,lowenabled:false};
const total={score:new Float64Array(n),days:new Float64Array(n),count:new Uint16Array(n),invalid:new Uint8Array(n)},defaults={};let inspected=0;
async function get(url){for(let i=0;i<5;i++){try{const r=await fetch(url);if(!r.ok)throw Error('HTTP '+r.status);return Buffer.from(await r.arrayBuffer());}catch(e){if(i===4)throw e;await new Promise(r=>setTimeout(r,1000*(i+1)));}}}
const ab=b=>b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength);const write=(name,array)=>{fs.writeFileSync(path.join(output,name),z.gzipSync(Buffer.from(array.buffer),{level:6}));return name;};
function finish(label,sums,calendar,years){const score=new Float64Array(n),days=new Float64Array(n);for(let j=0;j<n;j++){if(sums.invalid[j]||!sums.count[j])score[j]=days[j]=NaN;else{score[j]=sums.score[j]/sums.count[j];days[j]=sums.days[j]/sums.count[j]*calendar/years;}}defaults[label]={score:write(`min-score-${label}.gz`,score),days:write(`min-days-${label}.gz`,days),coverage:write(`min-coverage-${label}.gz`,sums.count)};}
(async()=>{for(const year of m.available_years){const sums={score:new Float64Array(n),days:new Float64Array(n),count:new Uint16Array(n),invalid:new Uint8Array(n)},baselineScoreB=fs.readFileSync(path.join(root,`site/dist/assets/score-${year}.bin`)),baselineDaysB=fs.readFileSync(path.join(root,`site/dist/assets/days-${year}.bin`)),baselineScore=new Float32Array(ab(baselineScoreB)),baselineDays=new Float32Array(ab(baselineDaysB));let maxOffScoreError=0,maxOffDaysError=0;
 for(const name of m.sunshine.daily_files[year]){const raw=z.gunzipSync(await get(m.sunshine.data_url+name)),minRaw=z.gunzipSync(await get(base+name.replace('sun-daily-','minimum-'))),c=Sun.parse(ab(raw)),minimum=Low.parseMinimum(ab(minRaw));
  for(let k=0;k<c.n;k++){const j=c.start+k,v=Low.calculate(c,minimum,k,params),u=Low.calculate(c,minimum,k,off);sums.score[j]=v.scoreSum;sums.days[j]=v.comfortable;sums.count[j]=v.count;sums.invalid[j]=!v.eligible;total.score[j]+=v.scoreSum;total.days[j]+=v.comfortable;total.count[j]+=v.count;if(!v.eligible)total.invalid[j]=1;
   // Exact one-cell correspondence to pre-existing off-state map.
   const cell=nodeToGrid[j];assert(cell>=0);assert.equal(Number.isFinite(baselineScore[cell]),Boolean(u.eligible&&u.count),'Default-off coverage at '+year+'/'+j);if(u.eligible&&u.count){maxOffScoreError=Math.max(maxOffScoreError,Math.abs(u.scoreSum/u.count-baselineScore[cell]));maxOffDaysError=Math.max(maxOffDaysError,Math.abs(u.comfortable/u.count*c.days-baselineDays[cell]));}
   assert(v.count<=u.count);assert(v.comfortable<=u.comfortable);assert(v.scoreSum>=0&&v.scoreSum<=v.count*10+1e-7);inspected++;
  }
 }
 assert(maxOffScoreError<.00002,{year,maxOffScoreError});assert(maxOffDaysError<.0002,{year,maxOffDaysError});finish(String(year),sums,m.year_days[year-2020],1);console.log(JSON.stringify({year,offScoreError:maxOffScoreError,offDaysError:maxOffDaysError,inspected}));}
 finish('mean',total,2192,6);const metadata=JSON.parse((await get(base+'minimum-metadata.json')).toString());metadata.defaults=defaults;fs.writeFileSync(path.join(output,'minimum-metadata.json'),JSON.stringify(metadata));fs.writeFileSync(path.join(output,'minimum-javascript-audit.json'),JSON.stringify({passed:true,inspected,params,defaultOff:'all year/cells compared with original maps',missing:'90% matched records in every month',presets:defaults}));cp.execFileSync('gh',['release','upload',tag,...fs.readdirSync(output).map(f=>path.join(output,f)),'--clobber','--repo',repo],{stdio:'inherit'});console.log('AUDIT AND PRESETS READY');})().catch(e=>{console.error(e);process.exitCode=1});
