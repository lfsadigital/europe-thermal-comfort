// Asset _headers applies CORS and no-store without running code for normal GETs.
// This fallback handles preflight/errors and must not create browser disk caches.
export default {async fetch(request,env,ctx){
 const headers={'Access-Control-Allow-Origin':'*','Access-Control-Allow-Methods':'GET, HEAD, OPTIONS','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'};
 if(request.method==='OPTIONS')return new Response(null,{status:204,headers});
 if(!['GET','HEAD'].includes(request.method))return new Response('Method not allowed',{status:405,headers});
 const name=new URL(request.url).pathname.match(/^\/minimum-v1\/(minimum-202[0-5]-(?:[0-9]|[1-3][0-9]|4[01])|min-(?:score|days|coverage)-(?:mean|202[0-5])|v2-(?:h|l|hs|ls)-(?:score|days|coverage)-(?:mean|202[0-5]))\.gz$/)?.[1];
 if(name){
  const key=new Request('https://comfy-days-climate-sunshine.lfsalmeida92.workers.dev/minimum-v1/'+name+'.gz');
  let response=await caches.default.match(key);
  if(!response){
   const upstream=await fetch('https://github.com/lfsadigital/europe-thermal-comfort/releases/download/comfy-minimum-preview-38659046289/'+name+'.gz',{redirect:'follow'});
   if(!upstream.ok)return new Response('Daily-low data temporarily unavailable',{status:502,headers});
   response=new Response(upstream.body,{headers:{'Content-Type':'application/octet-stream','Cache-Control':'public, max-age=86400','X-Content-Type-Options':'nosniff'}});
   ctx.waitUntil(caches.default.put(key,response.clone()));
  }
  const merged=new Headers(response.headers);for(const [k,v]of Object.entries(headers))merged.set(k,v);
  return new Response(request.method==='HEAD'?null:response.body,{status:200,headers:merged});
 }
 const response=await env.ASSETS.fetch(request),merged=new Headers(response.headers);
 for(const [key,value] of Object.entries(headers))merged.set(key,value);
 return new Response(response.body,{status:response.status,headers:merged});
}};
