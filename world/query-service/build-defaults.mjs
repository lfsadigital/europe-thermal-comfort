import {mkdir,writeFile} from 'node:fs/promises';
import {gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {publicFetch} from './local-server.mjs';
import {NODES,CHUNK_SIZE,PARTS,REVISION,encodePart} from './query-core.mjs';
const dist=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../site/dist');
const params={lower:14,upper:30,rain0:4,rain1:10,rain2:20,pen1:.5,pen2:1,pen3:1.5,drymax:4,lowenabled:true,lowmin:14,lowmax:30,sunenabled:false,sunmin:6};
const modes={standard:params,sun6:{...params,sunenabled:true}},output={};
for(const mode of Object.keys(modes))output[mode]={start:0,n:NODES,score:new Float64Array(NODES),days:new Float64Array(NODES),coverage:new Uint16Array(NODES),sunhours:new Float64Array(NODES)};
let next=0,downloaded=0,completed=0;const start=performance.now();
async function load(url,min){const r=await publicFetch(url);const raw=await r.arrayBuffer();downloaded+=raw.byteLength;const b=await new Response(new Blob([raw]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();return min?globalThis.DailyTemperatureCore.parseMinimum(b):globalThis.SunshineCore.parse(b);}
async function part(index){const from=index*CHUNK_SIZE,n=Math.min(CHUNK_SIZE,NODES-from),invalid=Object.fromEntries(Object.keys(modes).map(k=>[k,new Uint8Array(n)]));for(let year=2020;year<=2025;year++){
 const [c,min]=await Promise.all([load(`https://comfy-days-climate-sunshine.lfsalmeida92.workers.dev/sun-v1/sun-daily-${year}-${index}.gz`,false),load(`https://comfy-days-climate-sunshine.lfsalmeida92.workers.dev/minimum-v1/minimum-${year}-${index}.gz`,true)]);
 if(c.start!==from||c.n!==n||c.year!==year||min.start!==from||min.n!==n||min.year!==year)throw Error('Builder source alignment mismatch');
 for(let k=0;k<n;k++)for(const [mode,p]of Object.entries(modes)){const v=globalThis.DailyTemperatureCore.calculate(c,min,k,p),out=output[mode],j=from+k;out.score[j]+=v.scoreSum;out.days[j]+=v.comfortable;out.coverage[j]+=v.count;out.sunhours[j]+=v.sunSecondsSum;if(!v.eligible)invalid[mode][k]=1;}
 }
 for(let k=0;k<n;k++)for(const mode of Object.keys(modes)){const out=output[mode],j=from+k,count=out.coverage[j];if(invalid[mode][k]||!count)out.score[j]=out.days[j]=out.sunhours[j]=NaN;else{out.score[j]=Math.min(10,Math.max(0,out.score[j]/count));out.days[j]=out.days[j]/count*2192/6;out.sunhours[j]=out.sunhours[j]/count/3600;}}
 console.log(`Default maps ${++completed}/${PARTS}`);
}
async function run(){while(next<PARTS){const index=next++;await part(index);}}
await Promise.all([run(),run()]);
const manifest={revision:REVISION,nodes:NODES,period:'mean',modes:{},build:{milliseconds:performance.now()-start,downloadedBytes:downloaded}};
await mkdir(path.join(dist,'assets/bounds-v1'),{recursive:true});
for(const [mode,data]of Object.entries(output)){const buffer=Buffer.from(encodePart(data)),gzip=gzipSync(buffer,{level:9}),sha256=createHash('sha256').update(gzip).digest('hex'),file=`assets/bounds-v1/${mode}-${sha256.slice(0,16)}.bin.gz`;await writeFile(path.join(dist,file),gzip);manifest.modes[mode]={params:modes[mode],file,sha256,bytes:gzip.length};}
await writeFile(path.join(dist,'assets/bounds-defaults-v1.json'),JSON.stringify(manifest,null,2)+'\n');console.log(JSON.stringify(manifest.build));
