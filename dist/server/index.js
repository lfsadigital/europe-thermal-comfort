var __create = Object.create;
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __getProtoOf = Object.getPrototypeOf;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __commonJS = (cb, mod) => function __require() {
  try {
    return mod || (0, cb[__getOwnPropNames(cb)[0]])((mod = { exports: {} }).exports, mod), mod.exports;
  } catch (e) {
    throw mod = 0, e;
  }
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(
  // If the importer is in node compatibility mode or this is not an ESM
  // file that has been converted to a CommonJS file using a Babel-
  // compatible transform (i.e. "__esModule" has not been set), then set
  // "default" to the CommonJS "module.exports" for node compatibility.
  isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target,
  mod
));

// world/site/dist/air-quality-daily-core.js
var require_air_quality_daily_core = __commonJS({
  "world/site/dist/air-quality-daily-core.js"(exports, module) {
    (function(root) {
      "use strict";
      const valid = (v) => typeof v === "number" && Number.isFinite(v) && v >= 0;
      function daily(hours) {
        if (hours?.length !== 24) throw Error("AQI day requires 24 UTC hourly slots");
        if (Array.from(hours).filter(valid).length < 22) return NaN;
        let maximum = -Infinity;
        for (let i = 0; i <= 21; i++) if (valid(hours[i]) && valid(hours[i + 1]) && valid(hours[i + 2])) maximum = Math.max(maximum, (hours[i] + hours[i + 1] + hours[i + 2]) / 3);
        return Number.isFinite(maximum) ? maximum : NaN;
      }
      function penalty(value, limit) {
        if (!Number.isFinite(limit) || limit < 0 || limit > 500) throw Error("Invalid AQI limit");
        return valid(value) ? Math.max(0, (value - limit) / 50) : 0;
      }
      function parse(buffer, { start, n, year } = {}) {
        if (!(buffer instanceof ArrayBuffer) || buffer.byteLength < 32) throw Error("Invalid daily AQI archive");
        const h = new Uint32Array(buffer, 0, 8), days = h[5] === 2024 ? 366 : 365;
        if (h[0] !== 1095844913 || h[1] !== 1 || !h[3] || h[3] > 2048 || h[2] + h[3] > 85699 || h[4] !== days || ![2023, 2024, 2025].includes(h[5]) || h[6] !== 3 || h[7] !== 22 || buffer.byteLength !== 32 + h[3] * days * 8 || start !== void 0 && h[2] !== start || n !== void 0 && h[3] !== n || year !== void 0 && h[5] !== year) throw Error("Daily AQI archive grid/year mismatch");
        const values = new Float64Array(buffer, 32);
        for (const v of values) if (!Number.isNaN(v) && !valid(v)) throw Error("Invalid daily AQI value");
        return { start: h[2], n: h[3], days, year: h[5], values };
      }
      root.AirQualityDailyCore = { daily, penalty, parse };
      if (typeof module !== "undefined") module.exports = root.AirQualityDailyCore;
    })(globalThis);
  }
});

// world/site/dist/sunshine-core.js
var require_sunshine_core = __commonJS({
  "world/site/dist/sunshine-core.js"(exports, module) {
    (function(root) {
      "use strict";
      function parse(buffer) {
        let offset = 0;
        function take(Type, n2) {
          const result = new Type(buffer.slice(offset, offset + n2 * Type.BYTES_PER_ELEMENT));
          offset += n2 * Type.BYTES_PER_ELEMENT;
          return result;
        }
        const header = take(Uint32Array, 12);
        if (header[0] !== 1396919373 || header[1] !== 1) throw Error("Invalid sunshine data version");
        const [, , start, n, days, year, nt] = header, count = n * days;
        const c = { start, n, days, year, temperature: take(Float32Array, nt), temperatureIndex: take(Uint16Array, count), rain: take(Uint16Array, count) };
        const shuffled = take(Uint8Array, count * 4), raw = new Uint8Array(count * 4);
        for (let byte = 0; byte < 4; byte++) for (let i = 0; i < count; i++) raw[i * 4 + byte] = shuffled[byte * count + i];
        c.sunshine = new Float32Array(raw.buffer);
        c.monthDays = [31, year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
        if (offset !== buffer.byteLength || c.monthDays.reduce((a, b) => a + b, 0) !== days) throw Error("Sunshine data length mismatch");
        return c;
      }
      function calculate(c, k, p) {
        let scoreSum = 0, comfortable = 0, count = 0, sunSecondsSum = 0, eligible = true, month = 0, monthCount = 0, monthEnd = c.monthDays[0];
        const b0 = Math.round(p.rain0 * 10), b1 = Math.round(p.rain1 * 10), b2 = Math.round(p.rain2 * 10);
        for (let day = 0; day < c.days; day++) {
          const i = k * c.days + day, temperature = c.temperature[c.temperatureIndex[i]], rain = c.rain[i], seconds = c.sunshine[i];
          if (Number.isFinite(temperature) && rain !== 65535 && Number.isFinite(seconds) && seconds >= 0) {
            const hours = seconds / 3600, penalty = rain <= b0 ? 0 : rain <= b1 ? p.pen1 : rain <= b2 ? p.pen2 : p.pen3;
            scoreSum += Math.max(0, 10 - 0.5 * Math.max(p.lower - temperature, 0, temperature - p.upper) - penalty - 0.5 * Math.max(0, p.sunmin - hours));
            if (temperature >= p.lower && temperature <= p.upper && rain <= b0 && hours >= p.sunmin) comfortable++;
            count++;
            monthCount++;
            sunSecondsSum += seconds;
          }
          if (day + 1 === monthEnd) {
            if (monthCount < Math.ceil(c.monthDays[month] * 0.9)) eligible = false;
            month++;
            monthCount = 0;
            monthEnd += c.monthDays[month] || 0;
          }
        }
        return { scoreSum, comfortable, count, sunSecondsSum, eligible };
      }
      root.SunshineCore = { parse, calculate };
      if (typeof module !== "undefined") module.exports = root.SunshineCore;
    })(globalThis);
  }
});

// world/site/dist/daily-temperature-core.js
var require_daily_temperature_core = __commonJS({
  "world/site/dist/daily-temperature-core.js"(exports, module) {
    (function(root) {
      "use strict";
      function temperatureLoss(high, low, p) {
        const highLoss = Math.max(p.lower - high, 0, high - p.upper);
        const lowLoss = p.lowenabled ? Math.max(p.lowmin - low, 0, low - p.lowmax) : 0;
        return 0.5 * Math.max(highLoss, lowLoss);
      }
      function daily(high, low, rain, sun, p, aqi = NaN) {
        if (!Number.isFinite(high) || !Number.isFinite(rain) || rain < 0 || p.lowenabled && !Number.isFinite(low) || p.sunenabled && (!Number.isFinite(sun) || sun < 0)) return null;
        const r = Math.round(rain * 10), r0 = Math.round(p.rain0 * 10), r1 = Math.round(p.rain1 * 10), r2 = Math.round(p.rain2 * 10);
        const rainLoss = r <= r0 ? 0 : r <= r1 ? p.pen1 : r <= r2 ? p.pen2 : p.pen3;
        const loss = temperatureLoss(high, low, p), sunLoss = p.sunenabled ? 0.5 * Math.max(0, p.sunmin - sun) : 0;
        const aqKnown = p.aqenabled && typeof aqi === "number" && Number.isFinite(aqi) && aqi >= 0, aqLoss = aqKnown ? Math.max(0, (aqi - p.aqmax) / 50) : 0;
        return { score: Math.max(0, 10 - loss - rainLoss - sunLoss - aqLoss), comfortable: high >= p.lower && high <= p.upper && (!p.lowenabled || low >= p.lowmin && low <= p.lowmax) && r <= r0 && (!p.sunenabled || sun >= p.sunmin) && (!aqKnown || aqi <= p.aqmax) };
      }
      function parseMinimum(buffer) {
        const h = new Uint32Array(buffer.slice(0, 32));
        if (h[0] !== 1296649812 || h[1] !== 1 || h[7] !== h[3] * h[4] || buffer.byteLength !== 32 + h[7] * 4) throw Error("Invalid daily-minimum file");
        return { start: h[2], n: h[3], days: h[4], year: h[5], values: new Float32Array(buffer.slice(32)) };
      }
      function calculate(c, min, k, p, aq = null, monthMask = 4095) {
        if (min.start !== c.start || min.n !== c.n || min.days !== c.days || min.year !== c.year) throw Error("Daily-minimum dates/cells differ from daily maxima");
        if (aq && (aq.start !== c.start || aq.n !== c.n || aq.days !== c.days || aq.year !== c.year)) throw Error("AQI dates/cells differ from climate");
        let aqCount = 0;
        let scoreSum = 0, comfortable = 0, count = 0, sunSecondsSum = 0, eligible = true, month = 0, monthCount = 0, monthEnd = c.monthDays[0];
        for (let day = 0; day < c.days; day++) {
          const i = k * c.days + day, high = c.temperature[c.temperatureIndex[i]], low = min.values[i], rain = c.rain[i], seconds = c.sunshine[i];
          const v = !(monthMask & 1 << month) || rain === 65535 ? null : daily(high, low, rain / 10, seconds / 3600, p, aq?.values[i]);
          if (v) {
            if (p.aqenabled && Number.isFinite(aq?.values[i]) && aq.values[i] >= 0) aqCount++;
            scoreSum += v.score;
            comfortable += Number(v.comfortable);
            count++;
            monthCount++;
            if (Number.isFinite(seconds) && seconds >= 0) sunSecondsSum += seconds;
          }
          if (day + 1 === monthEnd) {
            if (monthMask & 1 << month && monthCount < Math.ceil(c.monthDays[month] * 0.9)) eligible = false;
            month++;
            monthCount = 0;
            monthEnd += c.monthDays[month] || 0;
          }
        }
        return { scoreSum, comfortable, count, sunSecondsSum, eligible, aqCount };
      }
      root.DailyTemperatureCore = { daily, temperatureLoss, parseMinimum, calculate };
      if (typeof module !== "undefined") module.exports = root.DailyTemperatureCore;
    })(globalThis);
  }
});

// world/site/dist/monthly-core.js
var require_monthly_core = __commonJS({
  "world/site/dist/monthly-core.js"(exports, module) {
    (function(root) {
      "use strict";
      function aggregate(records, p) {
        const result = [];
        for (let m = 0; m < 12; m++) {
          let ts = 0, rs = 0, ss = 0, tc = 0, rc = 0, sc = 0, matched = 0, comfortable = 0, calendar = 0, lows = 0, lowCount = 0, humidities = 0, humidityCount = 0, hotNights = 0, lowOK = true, humidityOK = true, means = 0, meanCount = 0, meanOK = true, tempOK = true, rainOK = true, sunOK = true;
          for (const r of records) {
            let offset = r.monthDays.slice(0, m).reduce((a, b) => a + b, 0), n = r.monthDays[m], tCount = 0, rCount = 0, sCount = 0, mc = 0, lc = 0, hc = 0;
            calendar += n;
            for (let d = offset; d < offset + n; d++) {
              const [t, rain, sun, mean, minimum, humidity] = r.days[d], tv = typeof t === "number" && Number.isFinite(t), rv = typeof rain === "number" && Number.isFinite(rain) && rain >= 0, sv = typeof sun === "number" && Number.isFinite(sun) && sun >= 0;
              if (typeof minimum === "number" && Number.isFinite(minimum)) {
                lows += minimum;
                lowCount++;
                lc++;
                if (minimum >= 20) hotNights++;
              }
              if (typeof humidity === "number" && Number.isFinite(humidity) && humidity >= 0 && humidity <= 100) {
                humidities += humidity;
                humidityCount++;
                hc++;
              }
              if (typeof mean === "number" && Number.isFinite(mean)) {
                means += mean;
                meanCount++;
                mc++;
              }
              if (tv) {
                ts += t;
                tc++;
                tCount++;
              }
              if (rv) {
                rs += rain;
                rc++;
                rCount++;
              }
              if (sv) {
                ss += sun;
                sc++;
                sCount++;
              }
              if (tv && rv && (!p.sunenabled || sv) && (!p.lowenabled || typeof minimum === "number" && Number.isFinite(minimum))) {
                matched++;
                if (t >= p.lower && t <= p.upper && Math.round(rain * 10) <= Math.round(p.rain0 * 10) && (!p.sunenabled || sun >= p.sunmin) && (!p.lowenabled || minimum >= p.lowmin && minimum <= p.lowmax)) comfortable++;
              }
            }
            lowOK &&= lc >= Math.ceil(n * 0.9);
            humidityOK &&= hc >= Math.ceil(n * 0.9);
            meanOK &&= mc >= Math.ceil(n * 0.9);
            tempOK &&= tCount >= Math.ceil(n * 0.9);
            rainOK &&= rCount === n;
            sunOK &&= sCount >= Math.ceil(n * 0.9);
          }
          result.push({ month: m, minimumTemperature: lowOK && lowCount ? lows / lowCount : null, humidity: humidityOK && humidityCount ? humidities / humidityCount : null, hotNights: lowOK && lowCount ? hotNights / lowCount * calendar / records.length : null, minimumCount: lowCount, humidityCount, temperature: tempOK && tc ? ts / tc : null, meanTemperature: meanOK && meanCount ? means / meanCount : null, precipitation: rainOK ? rs / records.length : null, sunshine: sunOK && sc ? ss / sc : null, comfortable: matched ? comfortable / matched * calendar / records.length : null, matched, calendar, temperatureCount: tc, rainCount: rc, sunCount: sc });
        }
        return result;
      }
      function fromAPI(data) {
        const d = data.daily, keys = ["temperature_2m_max", "precipitation_sum", "sunshine_duration", "temperature_2m_mean", "temperature_2m_min", "relative_humidity_2m_mean"];
        if (!d || !keys.every((k) => Array.isArray(d[k]) && d[k].length === 2192) || d.time?.length !== 2192) throw Error("Incomplete monthly API dates or arrays");
        if (data.daily_units?.precipitation_sum !== "mm" || data.daily_units?.sunshine_duration !== "s" || data.daily_units?.temperature_2m_max !== "\xB0C" || data.daily_units?.temperature_2m_mean !== "\xB0C" || data.daily_units?.temperature_2m_min !== "\xB0C" || data.daily_units?.relative_humidity_2m_mean !== "%") throw Error("Unexpected monthly climate units");
        const hourly = data.hourly?.temperature_2m;
        if (hourly && (!Array.isArray(hourly) || hourly.length !== 2192 * 24 || data.hourly?.time?.length !== 2192 * 24 || data.hourly_units?.temperature_2m !== "\xB0C")) throw Error("Incomplete hourly temperature records or units");
        const records = [];
        let i = 0;
        for (let year = 2020; year <= 2025; year++) {
          const monthDays = [31, year % 4 === 0 ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31], days = [];
          for (let month = 0; month < 12; month++) for (let day = 1; day <= monthDays[month]; day++, i++) {
            const date = `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
            if (d.time[i] !== date) throw Error("Monthly API dates do not match the archive");
            let high = d.temperature_2m_max[i], low = d.temperature_2m_min[i], mean = d.temperature_2m_mean[i];
            if (hourly) {
              const values = hourly.slice(i * 24, i * 24 + 24);
              for (let h = 0; h < 24; h++) if (data.hourly.time[i * 24 + h] !== date + "T" + String(h).padStart(2, "0") + ":00") throw Error("Hourly temperature dates do not match UTC days");
              if (values.every((v) => typeof v === "number" && Number.isFinite(v))) {
                high = Math.max(...values);
                low = Math.min(...values);
                mean = values.reduce((a, b) => a + b, 0) / 24;
              } else high = low = mean = null;
            }
            days.push([high, d.precipitation_sum[i], typeof d.sunshine_duration[i] === "number" ? d.sunshine_duration[i] / 3600 : null, mean, low, d.relative_humidity_2m_mean[i]]);
          }
          records.push({ year, monthDays, days });
        }
        return records;
      }
      root.MonthlyCore = { aggregate, fromAPI };
      if (typeof module !== "undefined") module.exports = root.MonthlyCore;
    })(globalThis);
  }
});

// world/query-service/aqi-archive.mjs
var import_air_quality_daily_core = __toESM(require_air_quality_daily_core(), 1);

// world/query-service/aqi-dataset.mjs
var AQI_DATASET = { "version": 1, "dataset": "cams-global-max3h-425950138cae91b1", "validation": "passed", "years": [2023, 2024, 2025], "nodes": 85699, "chunk_size": 2048, "method": "max of complete 3-hour windows within UTC day", "minimum_valid_hours": 22, "source": "CAMS global / ECMWF via Open-Meteo AWS", "source_commit": "03d62919c419f1eccad8dcbbcf7f92a2dd7069b4", "license": "CC BY 4.0", "grid_sha256": "aea5570ba747eb6625c47b56e58d16a2f25a3c197fe98d578731e2cad2403cf7", "data_url": "https://github.com/lfsadigital/europe-thermal-comfort/releases/download/comfy-aqi-daily-max3h-v1/", "files": { "aqi-daily-2023-0.gz": { "bytes": 2023370, "sha256": "de743b65ab1522d125f7482ad0afa3f42b85588890c7a350e12d6e2fca7f9f8f" }, "aqi-daily-2023-1.gz": { "bytes": 2242941, "sha256": "d6960d34b7356618bdf62cce9aad6c5f8bd494292e6a376ed8ce3a6f786ecd23" }, "aqi-daily-2023-2.gz": { "bytes": 2445753, "sha256": "e2302fc3d9df8ac9f7f3691cfb5ca0d67b0f03699a9afe4e6c9d5eba8e3a7331" }, "aqi-daily-2023-3.gz": { "bytes": 2550909, "sha256": "ff64390eb95db7270d5affbcfb2c4e4cc18710f6b4be1ac87ca6a4ebb1d8b5b6" }, "aqi-daily-2023-4.gz": { "bytes": 2612531, "sha256": "a46204c73d10832308540eba92511e4f2aa500dc1277448129c616f2d3c2846a" }, "aqi-daily-2023-5.gz": { "bytes": 2657069, "sha256": "66a7e02cc02da562da297876a714b29bef00a7c69d06939b9d66e7ee8b6b0cfa" }, "aqi-daily-2023-6.gz": { "bytes": 2717556, "sha256": "1a61406b48b2db4899b182a3be3c6e53bffc2d033ed941524ac21b8f727bc475" }, "aqi-daily-2023-7.gz": { "bytes": 2790772, "sha256": "9c20c31bcd11f13e4ebf5cd157d641262cc85f93d416fd0e3d2f0fe4f8308328" }, "aqi-daily-2023-8.gz": { "bytes": 2856580, "sha256": "5224a2e2ea6e8fd61e34a5267c3444907028e523eec4c657099aff8eba60726a" }, "aqi-daily-2023-9.gz": { "bytes": 2901183, "sha256": "351abd6909779724d45037181255399fb51ced0efad5152aa38a704eef67d6db" }, "aqi-daily-2023-10.gz": { "bytes": 2923932, "sha256": "223aeefe2b41f47078f997d3a66da10c274e0e9bc262fd597cca151928ec967f" }, "aqi-daily-2023-11.gz": { "bytes": 2933069, "sha256": "993a0e773d0a1c87e4199e6bcaaf47c29056b948f74c477ea3beed6cc9b5b8ca" }, "aqi-daily-2023-12.gz": { "bytes": 2963054, "sha256": "1e82e7daf6765d69a87b5f10c0ce22bbe12821e11a88c9d1d8c9af2d02a45bd9" }, "aqi-daily-2023-13.gz": { "bytes": 3020527, "sha256": "73b268d480c8a18ff0c422d5120695aad150695bb0878e49a4ae246a9c76bc72" }, "aqi-daily-2023-14.gz": { "bytes": 3012739, "sha256": "3ee4f7303f282fb7a2599b0b80a4fc765c0f622c5dcff70418e0a68aa85a7375" }, "aqi-daily-2023-15.gz": { "bytes": 2992297, "sha256": "aa7baf93bdfcc8a18674a2657b9371d49797770af403c61d9e5f763818974b9e" }, "aqi-daily-2023-16.gz": { "bytes": 2945944, "sha256": "5761c12a2e64cd36ae490c5eb48feed7836992f0f3075f132cbb021b4db7b858" }, "aqi-daily-2023-17.gz": { "bytes": 2965202, "sha256": "9a2e773632bc248a80acf0c94009a4d9d5b85f50a45e9db149e36bf473fde810" }, "aqi-daily-2023-18.gz": { "bytes": 3009018, "sha256": "fb1994a7248d721d5b821707b4e52d7d957318609b57324b4c4f2539a1d3de29" }, "aqi-daily-2023-19.gz": { "bytes": 3059231, "sha256": "99dfff4db660825317b743b61e0bcc2a425ae73371be5a3a5d8e857205985000" }, "aqi-daily-2023-20.gz": { "bytes": 3087746, "sha256": "486cbdddaef5ad0a99adcea473bbe3bc687bed6b72cc8049609f47a761916f97" }, "aqi-daily-2023-21.gz": { "bytes": 3099500, "sha256": "fd778929ee82cab191fdc5e6d4051bef9a9497795370b3747be8de3c40310c08" }, "aqi-daily-2023-22.gz": { "bytes": 3076926, "sha256": "c3ba9f0bf7d527b39a7e300857b2730aa29449f2805992918b42c91ca38a7e45" }, "aqi-daily-2023-23.gz": { "bytes": 3043420, "sha256": "2c913d44cb0a93bd55679ad095c9ac215303359ded0da669dbf756d6d7054087" }, "aqi-daily-2023-24.gz": { "bytes": 3035081, "sha256": "d544cd6f347c8338df5131deea0ad3306e4232f495343c6354d8c0ac5680c665" }, "aqi-daily-2023-25.gz": { "bytes": 3035347, "sha256": "2ab7472d6381154656d55a49f9f7e4b643f239800c6cd6c83457b5f16cea283b" }, "aqi-daily-2023-26.gz": { "bytes": 3017368, "sha256": "138dae8f4e23847060d3c583f635622e6ab393b409498f55b3391a59aafe2d3a" }, "aqi-daily-2023-27.gz": { "bytes": 2965652, "sha256": "ec29c6517039a580d3e3592646db401f004fe9ee4e4c798b5adde075b3297291" }, "aqi-daily-2023-28.gz": { "bytes": 2832878, "sha256": "0f120fba33fa3d984343ca209cae9de33e6580d7b86f3b05a68aff4515d2131a" }, "aqi-daily-2023-29.gz": { "bytes": 2760690, "sha256": "05798a99f120f9e644ffb5d1b4a02e25b5902326fb7d771282c8377143c9d4fc" }, "aqi-daily-2023-30.gz": { "bytes": 1841020, "sha256": "a66697bec2cd2234048c4c00f8689f1c55b2e9189e9dac8312d4ff5d0d0251f0" }, "aqi-daily-2023-31.gz": { "bytes": 1709713, "sha256": "e528674f69d689cb7f82d00acdee5b6a8bb1f7cda873cd164b667ee5638c24a8" }, "aqi-daily-2023-32.gz": { "bytes": 1609233, "sha256": "cda1c4c7e5177f40cdb78ad5e07f077e47534e0d2ebc598f2c41037e574bdbf0" }, "aqi-daily-2023-33.gz": { "bytes": 1554322, "sha256": "09f3ba8e0775a265a82a9a5ef209db29581b0e01f17e6dafa14043998ef43864" }, "aqi-daily-2023-34.gz": { "bytes": 1496095, "sha256": "d082a3e3c19ecbaa5a820ca621560a936fae3586b757ae88f5753710e31da4aa" }, "aqi-daily-2023-35.gz": { "bytes": 1415308, "sha256": "6903b4f661ab5ebfd9410223470f49d1c465a9586296b548b55706e8fe2a4650" }, "aqi-daily-2023-36.gz": { "bytes": 1286320, "sha256": "de37c6bdffe06f39ec733418b4ec5054c749ed877f4d1029fa6a8040414bcc68" }, "aqi-daily-2023-37.gz": { "bytes": 1162783, "sha256": "aeff2507d22413b95c032b757a434e96d59c6f58bdb6040927b74e8cacc8f1d1" }, "aqi-daily-2023-38.gz": { "bytes": 972099, "sha256": "925308292700cc889547d59c8f268cfe315d17a9f9f7adb879795dbb160068ba" }, "aqi-daily-2023-39.gz": { "bytes": 677724, "sha256": "56dad405b9db92d62577ebf41b8e191ed9c93682477c4153ce4be5c7caacb1e1" }, "aqi-daily-2023-40.gz": { "bytes": 449959, "sha256": "4cdb9469bceb04a94625f8b788f6c3d7602cf1e41f0181ccf5a18216070a5700" }, "aqi-daily-2023-41.gz": { "bytes": 196741, "sha256": "a99720ad95f42fc46ef396ebd3b05eb6169deafa299f7c1b495b55892be1b98a" }, "aqi-daily-2024-0.gz": { "bytes": 2102821, "sha256": "5c0cb13b90e680f964fb488f7d106d819a00573a826fcacddbd41fbb9a63596a" }, "aqi-daily-2024-1.gz": { "bytes": 2284215, "sha256": "e209f0c1a690a1d0e49e04b59396444f643c6b7ab967707927b33ad597306a1c" }, "aqi-daily-2024-2.gz": { "bytes": 2456744, "sha256": "93b874f96402f9b329ef24ed01fcdd539fd6425eda32bd463f07df8b8726804a" }, "aqi-daily-2024-3.gz": { "bytes": 2540335, "sha256": "48232aa177cbef1f1342bf4d190adf738150366eb1d5413ca80c4848534d0668" }, "aqi-daily-2024-4.gz": { "bytes": 2576621, "sha256": "2edcaad3134c52e8670f9820621738e886284b890b446ebf704ba58452193836" }, "aqi-daily-2024-5.gz": { "bytes": 2623144, "sha256": "d0ac2984202a558d64fea9a9410e36b6d52365ad5a7f70f40e7eeb41963f2d6f" }, "aqi-daily-2024-6.gz": { "bytes": 2679308, "sha256": "729040295e1568ad4166f7e7d83b445d09af5c88da607b2b46efb378a93be2d1" }, "aqi-daily-2024-7.gz": { "bytes": 2763893, "sha256": "93c6beb0ba0506a8a88882d150769ef225b415a058ed7f0b039ef219f6dc2b45" }, "aqi-daily-2024-8.gz": { "bytes": 2825808, "sha256": "ff3581045d25d03c00cd851b34e285e1e637a9293c8b789cd86073ed399581fc" }, "aqi-daily-2024-9.gz": { "bytes": 2873444, "sha256": "c31e05e1155e8b5654050255742fba72a0766d59dacb99cdf4fbb80257ebf227" }, "aqi-daily-2024-10.gz": { "bytes": 2889783, "sha256": "511374ac02976ae91608a57ebcad957014e98f6e7639131db5de085e413e19dd" }, "aqi-daily-2024-11.gz": { "bytes": 2910534, "sha256": "b1f1094c44622e7aea71d548c80040cbcedcc7b0e405e4a28bb48d464f0217b6" }, "aqi-daily-2024-12.gz": { "bytes": 2947933, "sha256": "68c2afc95f69044c59a9b31829a473749fba1c5830be14337290c47ee89b9910" }, "aqi-daily-2024-13.gz": { "bytes": 3014198, "sha256": "8ceb93b9f7c13b47b8fc01b02352c247b2af27726061f2958585a02e7ac490f4" }, "aqi-daily-2024-14.gz": { "bytes": 3018490, "sha256": "51ce0c58b3619d5825f083abbffed70e865a8df6c6f8dc23fd7e7fb029a25052" }, "aqi-daily-2024-15.gz": { "bytes": 2998228, "sha256": "5e49a7686628ab4c5f9a65d383380f33391f654c3b713b4df7819b79abd82180" }, "aqi-daily-2024-16.gz": { "bytes": 2959895, "sha256": "55fbdba21e2dbb74108c864a2d79a74eb49d77066b726d1fd692cd2404805b4a" }, "aqi-daily-2024-17.gz": { "bytes": 2992653, "sha256": "367b98ad04989d31f6ac6e6c4c1145d1f3eb7d7764b9bd79f27acb71f81b2324" }, "aqi-daily-2024-18.gz": { "bytes": 3043278, "sha256": "1bd54804396a9e3f27e938af8f4577afaaf1a52dc1bf1c1a61e10a9d573c70be" }, "aqi-daily-2024-19.gz": { "bytes": 3088036, "sha256": "c2457ca7477f32d9626bb31b00e1639ac7389c559f93a74802da3899b0453f9c" }, "aqi-daily-2024-20.gz": { "bytes": 3107228, "sha256": "4612e3b7c30a5d67040939e39b8a36462038d98799224c4031ac9f10ecd09b48" }, "aqi-daily-2024-21.gz": { "bytes": 3130237, "sha256": "a0db3c5d21c0bb33986855068523aee50d410329f8a0937e3bb168c186ec096b" }, "aqi-daily-2024-22.gz": { "bytes": 3095668, "sha256": "2484304ae83391b4153e36c91b1c6383fa73e49c50fd6d74ebaff95102dba5e6" }, "aqi-daily-2024-23.gz": { "bytes": 3066562, "sha256": "8202a8e4d806856c7f8bc189530ffe9a26a6fae462be3048751b92e080f5a601" }, "aqi-daily-2024-24.gz": { "bytes": 3060838, "sha256": "062cdbe84017b6dbbdcbf4ecc1cd2969ef02babb4d46571765ced8c4f810540a" }, "aqi-daily-2024-25.gz": { "bytes": 3068985, "sha256": "ad96ee47edfc6de00949486f255a1d1b0484a43f201b14f3b6986f4ac6bc0dd9" }, "aqi-daily-2024-26.gz": { "bytes": 3033423, "sha256": "4d6139d409623380b846e64bdf5899472afa2cabf8bffe092c691886e0e8561a" }, "aqi-daily-2024-27.gz": { "bytes": 2918971, "sha256": "1e380f138484c412fc8ed4af46708a88374f426d10591ba91d6a6b7bea97c069" }, "aqi-daily-2024-28.gz": { "bytes": 2778440, "sha256": "fe4e41c5a83e98ee5fb7482c7e07217627690483e62c49ccca4f06feb2cb33b4" }, "aqi-daily-2024-29.gz": { "bytes": 2719909, "sha256": "7a726cf10cd8387024c5a4a9b9553c666eda05755515783376553ac53cd86314" }, "aqi-daily-2024-30.gz": { "bytes": 1954442, "sha256": "031a706a324e46c646c73781fb871093e44d39870d630b8b723bc4dc4b35205c" }, "aqi-daily-2024-31.gz": { "bytes": 1868747, "sha256": "483eeb46b09c35ec39e272de1b52c6854dfae7f7e930919b598f8492febfc106" }, "aqi-daily-2024-32.gz": { "bytes": 1796920, "sha256": "13357e891b5bb40c8959fcf8f9e6d157e3fec56f3786feca48b9f497ec2c4b18" }, "aqi-daily-2024-33.gz": { "bytes": 1763034, "sha256": "d65e9db8254972a2decc84b91fc01e1768bf01ba4d3273add6a1b5855ea4682e" }, "aqi-daily-2024-34.gz": { "bytes": 1708176, "sha256": "37593be18c424204462d7f03b5273475eba2297b7233e824a8461e4cc2dc4eb7" }, "aqi-daily-2024-35.gz": { "bytes": 1631583, "sha256": "52ddcfa6fb707a00d716661ef977e531c12488cbc763835f2f5e3369affcd865" }, "aqi-daily-2024-36.gz": { "bytes": 1490867, "sha256": "0787c230e9d1adfcb8c3825cf98e924d6c40edd307e76c9e124c3b248d01c6bd" }, "aqi-daily-2024-37.gz": { "bytes": 1356192, "sha256": "9be3bebf56de252653cb6c324361ef698740c0df365430406b0dc9a685b95d00" }, "aqi-daily-2024-38.gz": { "bytes": 1167587, "sha256": "77e3dc9bf9c8916d839414f761e77fd0c396b6b95f1a481014117c233ad10aba" }, "aqi-daily-2024-39.gz": { "bytes": 844116, "sha256": "5bf6f86060efdd337b6aa8d5b8e7a61bccc9c5f1b1dc0a06a400603cc864f6fb" }, "aqi-daily-2024-40.gz": { "bytes": 587887, "sha256": "07b837daa72cf789c31859fe5ec43c574ffd13a4b4d312c63b9ce8b2901562e1" }, "aqi-daily-2024-41.gz": { "bytes": 281234, "sha256": "e86fb34dd714f1f9ac8ab5ee32c0ea9beda4d663ca9c57edc82c7933e96259f0" }, "aqi-daily-2025-0.gz": { "bytes": 2130831, "sha256": "fe9778382a4a7d7b3119ef9fdf6dab70d955f9578f644e436451ca435d636663" }, "aqi-daily-2025-1.gz": { "bytes": 2260442, "sha256": "ae700b88a1001f35ddead66ff1c824742e7e12b7c48854f5e94a2e1ab3c6e80b" }, "aqi-daily-2025-2.gz": { "bytes": 2420590, "sha256": "d9aebc064ae89e2d8651dfa97e2abb3956000e5284161ab7f57bfd4f74cd9ad6" }, "aqi-daily-2025-3.gz": { "bytes": 2520868, "sha256": "0a64ea6502a78dd800b43ef5ce7eeae4ec72e96855b0bdc969727b2c71ddee0e" }, "aqi-daily-2025-4.gz": { "bytes": 2570248, "sha256": "4b0dbabade38841d723d1cab204331fd13f35e124adbfc1ff35db0b79bf1548f" }, "aqi-daily-2025-5.gz": { "bytes": 2622504, "sha256": "2c6adc0fc3b67128035f3b5a82aa683ab0ac3897f93c30d547d7c6261617f9b3" }, "aqi-daily-2025-6.gz": { "bytes": 2690015, "sha256": "5567469ad2ea7b69538cb68f7d9b56b767cc0cb5d3f56fd52b4923d150b66f77" }, "aqi-daily-2025-7.gz": { "bytes": 2760671, "sha256": "ff5795f7505e88ae704c566e668950d1dcb8023334ccc16f036ce82b054321d2" }, "aqi-daily-2025-8.gz": { "bytes": 2812619, "sha256": "abe3b147b7843c5a35a3114ced31032586db25ae65dd7e78b06db0d997b3e921" }, "aqi-daily-2025-9.gz": { "bytes": 2854838, "sha256": "d96322cef21ef296940d7985b5388307dd8b5219d20497bfd9d57b173c6d50c6" }, "aqi-daily-2025-10.gz": { "bytes": 2884201, "sha256": "3debe00d548cf99acbb6ce3c821e35ddcb07d02602d398ef8dbbaac1a6d42c09" }, "aqi-daily-2025-11.gz": { "bytes": 2904533, "sha256": "b1ddcf7851227cca57b7d2956b77b8090a1d792c8f2d42ebf357b048c36c03bf" }, "aqi-daily-2025-12.gz": { "bytes": 2921475, "sha256": "cc81faab9b78295bc5ecdde7d1886d0f5975e646d7791880a8f2e20f7be9c3a7" }, "aqi-daily-2025-13.gz": { "bytes": 2993051, "sha256": "37d4d1cd71d80504b349138d261567f08def46d420f460912d848cbb74744b65" }, "aqi-daily-2025-14.gz": { "bytes": 3008479, "sha256": "4742cf78735b0a87ca96e0cc6e45d3d33245d87dcab2bd7a56a312021d490530" }, "aqi-daily-2025-15.gz": { "bytes": 2992109, "sha256": "c5f3e3d102d395e124b9cbdbd2b8bd9df1fc01cf04b32cc28bd099a03260c91a" }, "aqi-daily-2025-16.gz": { "bytes": 2931739, "sha256": "2a4a8f6381aa229915fc0871f28c7b2a97e4e52abfafadd93277fc23c26a2530" }, "aqi-daily-2025-17.gz": { "bytes": 2959034, "sha256": "8ec416ccf905e8f8817e157dad0991424766acf1805ca775565df6d60b699443" }, "aqi-daily-2025-18.gz": { "bytes": 3022825, "sha256": "2c688f02741177c8385682a6b560f336837ef33b96a454d41672c4628f72f667" }, "aqi-daily-2025-19.gz": { "bytes": 3078521, "sha256": "449ec96d6d15e43a9d7ce99cb2672c20bae0a03472087c88b77f28ed95975a06" }, "aqi-daily-2025-20.gz": { "bytes": 3097613, "sha256": "fc9a86a369fc2aea5cc8b79f191eb016989b9b65a2a2967be85e960808ff6cbd" }, "aqi-daily-2025-21.gz": { "bytes": 3112291, "sha256": "ad3443d4084e147589f4411bd29f5c0be09ec7ceba1a5a7b2bd9e8ba7e408585" }, "aqi-daily-2025-22.gz": { "bytes": 3088024, "sha256": "d4ccede848a671d7e7dfccf529c993614aa392545b40e6275102fa279631b851" }, "aqi-daily-2025-23.gz": { "bytes": 3048815, "sha256": "e7891adc8739e89db78e215e997a2da6a8eb2c235f165bf89d25ff6e6d06a151" }, "aqi-daily-2025-24.gz": { "bytes": 3039609, "sha256": "725146ab1b306725241b1996034e117873e752a6226b16ac63a20eaf49ed786b" }, "aqi-daily-2025-25.gz": { "bytes": 3031672, "sha256": "d98fc726783f8c4ce72d8f6d244663ea121066fed7c4dac5fac1dd806150aeaa" }, "aqi-daily-2025-26.gz": { "bytes": 2990561, "sha256": "6a4afa341a8cc9f1c12f9dc87883fdde423fe2e9ac1bf1d26ccf04b6b83e5a19" }, "aqi-daily-2025-27.gz": { "bytes": 2845472, "sha256": "ef7e4fb29ba1a14a9ab66b4ba40dc57ae4c68dc47459f51ea9838f887a46c643" }, "aqi-daily-2025-28.gz": { "bytes": 2713611, "sha256": "2ea24d307dd64fb02f2aa9ab932a18d50e550b460e20a6b1e2e428e9a2436191" }, "aqi-daily-2025-29.gz": { "bytes": 2630522, "sha256": "6c3f193ad568fdea03ba7c0082464a7b47c866ff531675c0f2bdf16f0c90b0b5" }, "aqi-daily-2025-30.gz": { "bytes": 1848109, "sha256": "76f5959b4dcb666ff002cc4f4293bc812aadbf132d89a1e0b300bd7d33f60d2f" }, "aqi-daily-2025-31.gz": { "bytes": 1798018, "sha256": "303e506a83cdd2365bed587be77a1c4c2b771887e72c580acfd2670955d8a6f0" }, "aqi-daily-2025-32.gz": { "bytes": 1771327, "sha256": "154e08a4c12188e5c3903f927d36fa085085a5f8eb792a351fc183d2b80492a8" }, "aqi-daily-2025-33.gz": { "bytes": 1731160, "sha256": "47fa2e0845818ce63eaacfb538d29bd633be427516f4f5808b1d099721bf02c7" }, "aqi-daily-2025-34.gz": { "bytes": 1683484, "sha256": "939d3e0a57929192b3ff26105db1807ee88387a8c6452aa0f3d8bd0e2891d7f2" }, "aqi-daily-2025-35.gz": { "bytes": 1630288, "sha256": "b36db14ef66e9b88ff0a42e47e1f034b31ccf6acc309c9d393ef68c04c280586" }, "aqi-daily-2025-36.gz": { "bytes": 1496795, "sha256": "0b67630f9bff3f03d2e8ae86f2e28e63b18798787f97da684062d362f598f022" }, "aqi-daily-2025-37.gz": { "bytes": 1366645, "sha256": "92086f5605aecd2e76452f46aa92349677a79c1be7667638ef25ecc4d02f0fb2" }, "aqi-daily-2025-38.gz": { "bytes": 1164914, "sha256": "50bd5b53a95be77791ef3b962d126116872ada319730103a5a46ef8de25c2039" }, "aqi-daily-2025-39.gz": { "bytes": 828746, "sha256": "b49b61c0b6de4e21f96ab707a3718ef1c8fc84c39f7e3c59506dccea03f09158" }, "aqi-daily-2025-40.gz": { "bytes": 561471, "sha256": "14823eb59dcef6b695e04b62e7294c2601bdbc097b9161bb4480bee1ec1f769c" }, "aqi-daily-2025-41.gz": { "bytes": 252830, "sha256": "7a1e6c0dcd4e5d25fff50ba831e1a809fedfb9ea4f202cb66c609890f24c0a01" } }, "independent_api_checks": [{ "place": "Lisbon", "start": "2025-01-01", "hours": 168, "maxAQIErrorVsIntegerRoundedAPI": 0.49536895751953125 }, { "place": "Lisbon", "start": "2025-07-01", "hours": 168, "maxAQIErrorVsIntegerRoundedAPI": 0.4968528747558594 }, { "place": "New Delhi", "start": "2025-01-01", "hours": 168, "maxAQIErrorVsIntegerRoundedAPI": 0.5 }, { "place": "New Delhi", "start": "2025-07-01", "hours": 168, "maxAQIErrorVsIntegerRoundedAPI": 0.4970245361328125 }, { "place": "Sydney", "start": "2025-01-01", "hours": 168, "maxAQIErrorVsIntegerRoundedAPI": 0.4953727722167969 }, { "place": "Sydney", "start": "2025-07-01", "hours": 168, "maxAQIErrorVsIntegerRoundedAPI": 0.4958229064941406 }], "source_fingerprint": "425950138cae91b13a79b259ce742eaf0f5dff97511b4bb5c95e0df62f8cae23", "daily_valid_count": 93921747, "daily_expected_count": 93926104 };

// world/query-service/aqi-archive.mjs
async function loadAQIYear(year, part, fetcher = fetch, dataset = AQI_DATASET, cache = null) {
  if (!dataset) throw Error("Daily AQI dataset is not published");
  const name = `aqi-daily-${year}-${part}.gz`, file = dataset.files[name];
  if (!file) throw Error("AQI archive part unavailable");
  const key = new Request("https://comfy-aqi-data.invalid/" + dataset.dataset + "/" + name);
  let r = cache && await cache.match(key), cached = !!r;
  if (!r) r = await fetcher(dataset.data_url + name, { signal: AbortSignal.timeout(3e4), headers: { "User-Agent": "ComfyDays/1.0 (+https://comfy.lfsadigital.com)" } });
  if (!r.ok) throw Error("Daily AQI source HTTP " + r.status);
  const payload = await r.arrayBuffer();
  if (payload.byteLength !== file.bytes) throw Error("Daily AQI archive length mismatch");
  const hash = Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", payload)), (v) => v.toString(16).padStart(2, "0")).join("");
  if (hash !== file.sha256) {
    if (cache && cached) await cache.delete(key);
    throw Error("Daily AQI archive integrity mismatch");
  }
  let parsed;
  try {
    const buffer = await new Response(new Blob([payload]).stream().pipeThrough(new DecompressionStream("gzip"))).arrayBuffer();
    parsed = globalThis.AirQualityDailyCore.parse(buffer, { start: part * 2048, n: Math.min(2048, 85699 - part * 2048), year });
  } catch (error) {
    if (cache && cached) await cache.delete(key);
    throw error;
  }
  if (cache && !cached) await cache.put(key, new Response(payload, { headers: { "Cache-Control": "public, max-age=31536000", "Content-Type": "application/gzip" } }));
  return parsed;
}
function createAQIDailyService({ fetcher = fetch, dataset = AQI_DATASET, loadYear = null, archiveCache = null } = {}) {
  return { async fetch(request) {
    const headers = { "Content-Type": "application/json", "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" };
    const q = new URL(request.url).searchParams, node = Number(q.get("node")), period = q.get("period"), limit = Number(q.get("max") ?? 100), monthMask = q.has("months") ? Number(q.get("months")) : 4095;
    if (request.method !== "GET") return new Response("Method not allowed", { status: 405, headers });
    if (!Number.isInteger(monthMask) || monthMask < 1 || monthMask > 4095 || !q.has("node") || !Number.isInteger(node) || node < 0 || node >= 85699 || !["recent", "2023", "2024", "2025"].includes(period) || !Number.isFinite(limit) || limit < 0 || limit > 500) return new Response("Invalid AQI point or period", { status: 400, headers });
    try {
      const years = period === "recent" ? [2023, 2024, 2025] : [Number(period)], values = [], monthly = Array.from({ length: 12 }, (_, month) => ({ month, sum: 0, count: 0, within: 0, calendar: 0 }));
      for (const year of years) {
        const a = await (loadYear ? loadYear(year, Math.floor(node / 2048)) : loadAQIYear(year, Math.floor(node / 2048), fetcher, dataset, archiveCache)), days = [31, year === 2024 ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
        let day = 0;
        for (let m = 0; m < 12; m++) for (let d = 0; d < days[m]; d++, day++) {
          const v = a.values[(node - a.start) * a.days + day];
          monthly[m].calendar++;
          if (Number.isFinite(v) && v >= 0) {
            if (monthMask & 1 << m) values.push(v);
            monthly[m].sum += v;
            monthly[m].count++;
            monthly[m].within += Number(v <= limit);
          }
        }
      }
      return Response.json({ version: 1, dataset: dataset?.dataset || "test", period, limit, count: values.length, calendar: years.reduce((n, y) => n + [31, y === 2024 ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31].reduce((sum, d, i) => sum + (monthMask & 1 << i ? d : 0), 0), 0), maximum: values.length ? Math.max(...values) : null, mean: values.length ? values.reduce((a, b) => a + b, 0) / values.length : null, within: values.filter((v) => v <= limit).length, months: monthly.map((m) => ({ ...m, mean: m.count ? m.sum / m.count : null })) }, { headers: { ...headers, "Cache-Control": "public, max-age=86400" } });
    } catch (e) {
      console.error("Daily AQI point unavailable: " + e.message);
      return new Response("Daily AQI temporarily unavailable", { status: 502, headers });
    }
  } };
}

// world/query-service/query-core.mjs
var import_sunshine_core = __toESM(require_sunshine_core(), 1);
var import_daily_temperature_core = __toESM(require_daily_temperature_core(), 1);
var REVISION = "era5-cams-daily-max3h-months-v2";
var NODES = 85699;
var CHUNK_SIZE = 2048;
var PARTS = Math.ceil(NODES / CHUNK_SIZE);
var fields = ["lower", "upper", "rain0", "rain1", "rain2", "pen1", "pen2", "pen3", "drymax", "sunenabled", "sunmin", "lowenabled", "lowmin", "lowmax", "aqenabled", "aqmax"];
function parseQuery(url) {
  const q = new URL(url).searchParams, part = Number(q.get("part")), period = q.get("period") || "mean";
  if (!q.has("part") || !Number.isInteger(part) || part < 0 || part >= PARTS || !["mean", "2020", "2021", "2022", "2023", "2024", "2025", "recent"].includes(period)) throw new Error("Invalid climate part or period");
  const monthMask = q.has("months") ? Number(q.get("months")) : 4095;
  if (!Number.isInteger(monthMask) || monthMask < 1 || monthMask > 4095) throw new Error("Invalid month selection");
  let raw;
  try {
    raw = JSON.parse(q.get("params"));
  } catch {
    throw new Error("Invalid weather rules");
  }
  if (!raw || typeof raw !== "object" || Object.keys(raw).some((k) => !fields.includes(k))) throw new Error("Invalid weather rules");
  const p = Object.fromEntries(fields.map((k) => [k, raw[k]]));
  p.aqenabled = raw.aqenabled === void 0 ? false : raw.aqenabled;
  p.aqmax = raw.aqmax === void 0 ? 100 : raw.aqmax;
  if (typeof p.aqenabled !== "boolean" || !Number.isFinite(p.aqmax) || !Number.isInteger(p.aqmax) || p.aqmax < 0 || p.aqmax > 500 || p.aqenabled && !["recent", "2023", "2024", "2025"].includes(period)) throw Error("Invalid AQI rules or period");
  if (!p.aqenabled) p.aqmax = 100;
  if (fields.filter((k) => !["sunenabled", "lowenabled", "aqenabled"].includes(k)).some((k) => !Number.isFinite(p[k]))) throw new Error("Invalid numeric rules");
  if (p.lowenabled !== true || typeof p.sunenabled !== "boolean" || p.lower !== p.lowmin || p.upper !== p.lowmax || !Number.isInteger(p.lower) || !Number.isInteger(p.upper) || p.lower < -30 || p.upper > 50 || p.lower >= p.upper) throw new Error("Invalid temperature limits");
  if (!(0 <= p.rain0 && p.rain0 < p.rain1 && p.rain1 < p.rain2 && p.rain2 <= 300 && p.drymax === p.rain0) || ["rain0", "rain1", "rain2"].some((k) => Math.abs(p[k] * 10 - Math.round(p[k] * 10)) > 1e-8)) throw new Error("Invalid rain limits");
  if (!(0 <= p.pen1 && p.pen1 <= p.pen2 && p.pen2 <= p.pen3 && p.pen3 <= 10) || ["pen1", "pen2", "pen3"].some((k) => !Number.isInteger(p[k] * 2))) throw new Error("Invalid rain losses");
  if (p.sunmin < 0 || p.sunmin > 24 || !Number.isInteger(p.sunmin * 2)) throw new Error("Invalid sunshine limit");
  if (!p.sunenabled) p.sunmin = 6;
  return { part, period, monthMask, params: p, key: JSON.stringify([REVISION, part, period, monthMask, ...fields.map((k) => p[k])]) };
}
async function calculatePart({ part, period, params, monthMask = 4095 }, loadYear) {
  const start = part * CHUNK_SIZE, n = Math.min(CHUNK_SIZE, NODES - start), score = new Float64Array(n), days = new Float64Array(n), coverage = new Uint16Array(n), sunhours = new Float64Array(n), aqCoverage = new Uint16Array(n), invalid = new Uint8Array(n);
  const years = period === "mean" ? [2020, 2021, 2022, 2023, 2024, 2025] : period === "recent" ? [2023, 2024, 2025] : [Number(period)];
  let calendar = 0;
  for (const year of years) {
    const [c, min, aq] = await loadYear(year, part, params.aqenabled);
    if (c.start !== start || c.n !== n || c.year !== year || min.start !== start || min.n !== n || min.year !== year) throw new Error("Climate archive cell/year mismatch");
    calendar += c.monthDays.reduce((total, days2, month) => total + (monthMask & 1 << month ? days2 : 0), 0);
    for (let k = 0; k < n; k++) {
      const v = globalThis.DailyTemperatureCore.calculate(c, min, k, params, aq, monthMask);
      aqCoverage[k] += v.aqCount;
      score[k] += v.scoreSum;
      days[k] += v.comfortable;
      coverage[k] += v.count;
      sunhours[k] += v.sunSecondsSum;
      if (!v.eligible) invalid[k] = 1;
    }
  }
  for (let k = 0; k < n; k++) if (invalid[k] || !coverage[k]) score[k] = days[k] = sunhours[k] = NaN;
  else {
    score[k] = Math.min(10, Math.max(0, score[k] / coverage[k]));
    days[k] = days[k] / coverage[k] * calendar / years.length;
    sunhours[k] = sunhours[k] / coverage[k] / 3600;
  }
  return { start, n, score, days, coverage, sunhours, aqCoverage };
}
function encodePart(c) {
  const b = new ArrayBuffer(32 + c.n * 32), h = new Uint32Array(b, 0, 8);
  h.set([1128550705, 2, c.start, c.n]);
  new Float64Array(b, 32, c.n).set(c.score);
  new Float64Array(b, 32 + c.n * 8, c.n).set(c.days);
  new Float64Array(b, 32 + c.n * 16, c.n).set(c.sunhours);
  new Uint16Array(b, 32 + c.n * 24, c.n).set(c.coverage);
  if (c.aqCoverage) new Uint16Array(b, 32 + c.n * 26, c.n).set(c.aqCoverage);
  return b;
}

// world/query-service/service.mjs
var ORIGIN = "https://comfy-days-climate-sunshine.lfsalmeida92.workers.dev";
function createService({ fetcher = fetch, cache = null, now = () => performance.now(), maxConcurrent = 2, loadYear = null, archiveCache = null, activeJobs = /* @__PURE__ */ new Map(), background = false } = {}) {
  async function load(url, minimum) {
    const response = await fetcher(url, { signal: AbortSignal.timeout(3e4) });
    if (!response.ok) throw Error("Climate source returned " + response.status);
    const buffer = await new Response(response.body.pipeThrough(new DecompressionStream("gzip"))).arrayBuffer();
    return minimum ? globalThis.DailyTemperatureCore.parseMinimum(buffer) : globalThis.SunshineCore.parse(buffer);
  }
  async function compute(spec) {
    return encodePart(await calculatePart(spec, loadYear || ((year, part, aqenabled) => Promise.all([load(`${ORIGIN}/sun-v1/sun-daily-${year}-${part}.gz`, false), load(`${ORIGIN}/minimum-v1/minimum-${year}-${part}.gz`, true), aqenabled ? loadAQIYear(year, part, fetcher, AQI_DATASET, archiveCache).catch((error) => {
      console.error("Daily AQI archive unavailable " + year + "/" + part + ": " + error.message);
      return null;
    }) : null]))));
  }
  return { async fetch(request, ctx = { waitUntil: () => {
  } }) {
    const headers = { "Content-Type": "application/octet-stream", "Cache-Control": "public, max-age=86400", "X-Content-Type-Options": "nosniff", "Access-Control-Allow-Origin": "*", "Access-Control-Expose-Headers": "Server-Timing, X-Climate-Cache, X-Climate-Revision, Retry-After", "X-Climate-Revision": REVISION };
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: { ...headers, "Access-Control-Allow-Methods": "GET, OPTIONS" } });
    if (request.method !== "GET") return new Response("Method not allowed", { status: 405, headers: { ...headers, Allow: "GET, OPTIONS", "Cache-Control": "no-store" } });
    let spec;
    try {
      spec = parseQuery(request.url);
    } catch (e) {
      return new Response(e.message, { status: 400, headers: { ...headers, "Cache-Control": "no-store" } });
    }
    const key = new Request("https://comfy-query-cache.invalid/" + encodeURIComponent(spec.key + "|" + (spec.params.aqenabled ? AQI_DATASET?.dataset : "off"))), t = now(), hit = cache && await cache.match(key);
    if (hit) {
      const h = new Headers(hit.headers);
      h.set("X-Climate-Cache", "hit");
      h.set("Server-Timing", `climate;dur=${(now() - t).toFixed(1)}`);
      return new Response(hit.body, { headers: h });
    }
    for (const [key2, job] of activeJobs) if (now() - job.started > 35e3) activeJobs.delete(key2);
    const pending = () => new Response("Climate calculation in progress", { status: 202, headers: { ...headers, "Cache-Control": "no-store", "Retry-After": "1", "X-Climate-Cache": "pending" } });
    if (activeJobs.has(spec.key) || activeJobs.size >= maxConcurrent) return pending();
    const token = { started: now() };
    activeJobs.set(spec.key, token);
    const work = async () => {
      try {
        const buffer = await compute(spec);
        const parsed = new Uint16Array(buffer, 32 + Math.min(2048, 85699 - spec.part * 2048) * 26, Math.min(2048, 85699 - spec.part * 2048));
        const partial = spec.params.aqenabled && parsed.some((v) => v === 0);
        const response = new Response(buffer, { headers: { ...headers, ...partial ? { "Cache-Control": "public, max-age=30", "X-AQI-Coverage": "partial" } : {}, "X-Climate-Cache": "miss", "Server-Timing": `climate;dur=${(now() - t).toFixed(1)}` } });
        if (cache && !partial) await cache.put(key, response.clone());
        return response;
      } catch (e) {
        console.error("Climate calculation failed: " + e.message);
        return new Response("Climate calculation temporarily unavailable", { status: 502, headers: { ...headers, "Cache-Control": "no-store", "Retry-After": "2" } });
      } finally {
        if (activeJobs.get(spec.key) === token) activeJobs.delete(spec.key);
      }
    };
    if (background) {
      ctx.waitUntil(work());
      return pending();
    }
    return work();
  } };
}

// world/query-service/monthly-service.mjs
var import_monthly_core = __toESM(require_monthly_core(), 1);
var fields2 = ["temperature", "meanTemperature", "minimumTemperature", "humidity", "hotNights", "precipitation", "sunshine"];
function createMonthlyService({ fetcher = fetch, cache = null, activeJobs = /* @__PURE__ */ new Map() } = {}) {
  return { async fetch(request, ctx = { waitUntil: () => {
  } }) {
    const headers = { "Content-Type": "application/json", "Cache-Control": "public, max-age=604800", "Access-Control-Allow-Origin": "*", "X-Content-Type-Options": "nosniff" };
    if (request.method !== "GET") return new Response("Method not allowed", { status: 405, headers: { ...headers, "Cache-Control": "no-store" } });
    const q = new URL(request.url).searchParams, lat = Number(q.get("lat")), lon = Number(q.get("lon")), period = q.get("period") || "mean";
    if (!q.has("lat") || !q.has("lon") || !Number.isFinite(lat) || !Number.isFinite(lon) || lat < -90 || lat > 90 || lon < -180 || lon > 180 || !Number.isInteger(lat * 4) || !Number.isInteger(lon * 4) || !["mean", "2020", "2021", "2022", "2023", "2024", "2025", "recent"].includes(period)) return new Response("Invalid climate cell", { status: 400, headers: { ...headers, "Cache-Control": "no-store" } });
    const key = new Request(`https://comfy-monthly-cache.invalid/${REVISION}/${lat}/${lon}/${period}`), hit = cache && await cache.match(key);
    if (hit) return hit;
    for (const [key2, started] of activeJobs) if (Date.now() - started > 65e3) activeJobs.delete(key2);
    if (activeJobs.size) return new Response("Monthly records are loading", { status: 503, headers: { ...headers, "Cache-Control": "no-store", "Retry-After": "1" } });
    activeJobs.set(key.url, Date.now());
    try {
      const url = new URL("https://archive-api.open-meteo.com/v1/archive");
      for (const [k, v] of Object.entries({ latitude: lat, longitude: lon, start_date: "2020-01-01", end_date: "2025-12-31", models: "era5", hourly: "temperature_2m", daily: "temperature_2m_max,temperature_2m_mean,temperature_2m_min,relative_humidity_2m_mean,precipitation_sum,sunshine_duration", timezone: "UTC", elevation: "nan", cell_selection: "nearest" })) url.searchParams.set(k, v);
      const r = await fetcher(url, { signal: AbortSignal.timeout(6e4) });
      if (!r.ok) throw Error("Monthly API returned " + r.status);
      const data = await r.json();
      if (data.utc_offset_seconds !== 0 || Math.abs(data.latitude - lat) > 1e-6 || Math.abs(data.longitude - lon) > 1e-6) throw Error("Monthly cell mismatch");
      const records = globalThis.MonthlyCore.fromAPI(data), selected = period === "mean" ? records : period === "recent" ? records.filter((r2) => r2.year >= 2023) : records.filter((r2) => r2.year === Number(period)), months = globalThis.MonthlyCore.aggregate(selected, { lower: 14, upper: 30, lowenabled: true, lowmin: 14, lowmax: 30, rain0: 4, sunenabled: false }).map((m) => Object.fromEntries(["month", ...fields2].map((k) => [k, m[k]])));
      const response = new Response(JSON.stringify({ version: 1, latitude: lat, longitude: lon, period, months }), { headers });
      if (cache) await cache.put(key, response.clone());
      return response;
    } catch (e) {
      console.error("Monthly climate request failed: " + e.message);
      return new Response("Monthly records temporarily unavailable", { status: 502, headers: { ...headers, "Cache-Control": "no-store" } });
    } finally {
      activeJobs.delete(key.url);
    }
  } };
}

// world/query-service/worker.mjs
var climateJobs = /* @__PURE__ */ new Map();
var monthlyJobs = /* @__PURE__ */ new Map();
var worker_default = { async fetch(request, env, ctx) {
  const pathname = new URL(request.url).pathname;
  if (pathname === "/api/aqi/daily/v1") {
    const archiveCache = await caches.open("comfy-aqi-archives-v1");
    return createAQIDailyService({ archiveCache }).fetch(request);
  }
  if (pathname === "/api/monthly/v1") {
    const cache = await caches.open("comfy-days-results-v1");
    return createMonthlyService({ cache, activeJobs: monthlyJobs }).fetch(request, ctx);
  }
  if (pathname === "/api/climate/v1") {
    const cache = await caches.open("comfy-days-results-v1");
    return createService({ cache, archiveCache: await caches.open("comfy-aqi-archives-v1"), activeJobs: climateJobs, maxConcurrent: 2, background: true }).fetch(request, ctx);
  }
  return env.ASSETS.fetch(request);
} };
export {
  worker_default as default
};
