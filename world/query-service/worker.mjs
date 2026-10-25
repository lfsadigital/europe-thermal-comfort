import {createService} from './service.mjs';
import {createMonthlyService} from './monthly-service.mjs';
import {createAirQualityService} from './air-quality-service.mjs';
// Only plain metadata crosses requests; cache handles and background I/O belong
// to the current invocation. Sites requires an explicitly named cache.
const climateJobs=new Map(),monthlyJobs=new Map(),airJobs=new Map();
export default {async fetch(request,env,ctx){
 const pathname=new URL(request.url).pathname;
 if(pathname==='/api/air-quality/v1'){const cache=await caches.open('comfy-days-results-v1');return createAirQualityService({cache,activeJobs:airJobs}).fetch(request);}
 if(pathname==='/api/monthly/v1'){const cache=await caches.open('comfy-days-results-v1');return createMonthlyService({cache,activeJobs:monthlyJobs}).fetch(request,ctx);}
 if(pathname==='/api/climate/v1'){const cache=await caches.open('comfy-days-results-v1');return createService({cache,activeJobs:climateJobs,maxConcurrent:2,background:true}).fetch(request,ctx);}
 return env.ASSETS.fetch(request);
}};
