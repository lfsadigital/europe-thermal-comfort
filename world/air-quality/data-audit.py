"""Read-only feasibility audit; never starts a bulk import or purchases access."""
import json,urllib.request,urllib.parse,xml.etree.ElementTree as ET
ns={'s':'http://s3.amazonaws.com/doc/2006-03-01/'}
for prefix in ['data/cams_global/','data/cams_global/pm2_5/','data/cams_global/ozone/','data/cams_global/nitrogen_dioxide/']:
 url='https://openmeteo.s3.amazonaws.com/?'+urllib.parse.urlencode({'list-type':2,'prefix':prefix,'delimiter':'/','max-keys':1000})
 try:
  with urllib.request.urlopen(url,timeout=40) as r: root=ET.fromstring(r.read())
  print(json.dumps({'prefix':prefix,'directories':[x.text for x in root.findall('s:CommonPrefixes/s:Prefix',ns)],'files':[{'key':e.find('s:Key',ns).text,'bytes':int(e.find('s:Size',ns).text)} for e in root.findall('s:Contents',ns)],'truncated':root.find('s:IsTruncated',ns).text}),flush=True)
 except Exception as e: print(json.dumps({'prefix':prefix,'error':str(e)}),flush=True)
