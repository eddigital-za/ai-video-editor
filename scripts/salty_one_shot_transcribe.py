import os,json,urllib.request,urllib.error
url=os.environ['SALTY_AUDIO_URL']
audio=urllib.request.urlopen(url,timeout=30).read()
boundary='----saltytranscriber'
parts=[]
for name,value in [('model',os.environ.get('OPENAI_TRANSCRIBE_MODEL','whisper-1')),('response_format','verbose_json'),('timestamp_granularities[]','word')]:
 parts.append(('--'+boundary+'\r\nContent-Disposition: form-data; name="'+name+'"\r\n\r\n'+value+'\r\n').encode())
parts.append(('--'+boundary+'\r\nContent-Disposition: form-data; name="file"; filename="voiceover.m4a"\r\nContent-Type: audio/mp4\r\n\r\n').encode()+audio+b'\r\n')
parts.append(('--'+boundary+'--\r\n').encode())
req=urllib.request.Request('https://api.openai.com/v1/audio/transcriptions',data=b''.join(parts),headers={'Authorization':'Bearer '+os.environ['OPENAI_API_KEY'],'Content-Type':'multipart/form-data; boundary='+boundary},method='POST')
try:
 with urllib.request.urlopen(req,timeout=120) as r: response=json.load(r)
 print('SALTY_TRANSCRIPT_JSON='+json.dumps(response,ensure_ascii=False),flush=True)
except urllib.error.HTTPError as e:
 print('TRANSCRIBE_ERROR',e.code,e.read().decode()[:1000],flush=True)
 raise
