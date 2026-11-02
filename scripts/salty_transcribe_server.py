import os, json, urllib.request, urllib.error, http.server, tempfile
class Handler(http.server.BaseHTTPRequestHandler):
 def do_GET(self):
  if self.path != '/health': self.send_error(404); return
  self.send_response(200); self.end_headers(); self.wfile.write(b'ok')
 def do_POST(self):
  if self.path != '/transcribe': self.send_error(404); return
  if self.headers.get('Authorization') != 'Bearer '+os.environ.get('SALTY_JOB_TOKEN','not-set'):
   self.send_error(403); return
  length=int(self.headers.get('Content-Length','0'))
  if length<1 or length>15000000: self.send_error(413); return
  data=self.rfile.read(length)
  boundary='----saltytranscriber'
  parts=[]
  for name,value in [('model',os.environ.get('OPENAI_TRANSCRIBE_MODEL','whisper-1')),('response_format','verbose_json'),('timestamp_granularities[]','word')]:
   parts.append(('--'+boundary+'\r\nContent-Disposition: form-data; name="'+name+'"\r\n\r\n'+value+'\r\n').encode())
  parts.append(('--'+boundary+'\r\nContent-Disposition: form-data; name="file"; filename="voiceover.m4a"\r\nContent-Type: audio/mp4\r\n\r\n').encode()+data+b'\r\n')
  parts.append(('--'+boundary+'--\r\n').encode())
  req=urllib.request.Request('https://api.openai.com/v1/audio/transcriptions',data=b''.join(parts),headers={'Authorization':'Bearer '+os.environ['OPENAI_API_KEY'],'Content-Type':'multipart/form-data; boundary='+boundary},method='POST')
  try:
   with urllib.request.urlopen(req,timeout=120) as resp: result=resp.read()
   self.send_response(200); self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(result)));self.end_headers();self.wfile.write(result)
  except urllib.error.HTTPError as e:
   msg=e.read(); self.send_response(e.code);self.end_headers();self.wfile.write(msg[:2000])
  except Exception as e: self.send_error(502,str(type(e).__name__))
http.server.HTTPServer(('0.0.0.0',int(os.environ.get('PORT','8080'))),Handler).serve_forever()
