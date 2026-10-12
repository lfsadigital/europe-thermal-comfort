// Sunshine data is cached at Cloudflare but must not accumulate in browser disk caches.
export default {async fetch(request,env){
 const headers={'Access-Control-Allow-Origin':'*','Access-Control-Allow-Methods':'GET, HEAD, OPTIONS','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'};
 if(request.method==='OPTIONS')return new Response(null,{status:204,headers});
 if(!['GET','HEAD'].includes(request.method))return new Response('Method not allowed',{status:405,headers});
 const response=await env.ASSETS.fetch(request),merged=new Headers(response.headers);
 for(const [key,value] of Object.entries(headers))merged.set(key,value);
 return new Response(response.body,{status:response.status,headers:merged});
}};
