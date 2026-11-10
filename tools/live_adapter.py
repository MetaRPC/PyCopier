"""Native SDK adapter for an external live acceptance runner. Secrets arrive on stdin."""
import asyncio,sys,json
from pathlib import Path
from dataclasses import asdict
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pycopier import CopierService,Account,StartRequest
async def main():
 v=[sys.stdin.readline().rstrip('\n\r') for _ in range(13)]
 c=CopierService(v[0],user_key=v[1]);op=sys.argv[1]
 try:
  if op=='start':
   def account(i):return Account(type='MT5',user=int(v[i]),password=v[i+1],server=v[i+2],id=v[i+3])
   r=await c.start(StartRequest(master=account(2),slave=account(6),risk_type=v[10],risk_value=v[11],fixed_master_balance=v[12],copy_sl=True,copy_tp=True))
  elif op=='stream':
   async for event in c.stream_trade_logs(sys.argv[2]):print(json.dumps(event.raw),flush=True)
   return
  elif op=='list':r=await c.list()
  elif op=='pause':r=await c.pause(sys.argv[2],sys.argv[3]=='true')
  elif op=='remove':r=await c.remove(sys.argv[2])
  else:raise ValueError('Unknown operation')
  print(json.dumps(asdict(r)))
 finally:await c.close()
if __name__=='__main__':
 try:asyncio.run(main())
 except Exception as e:print(json.dumps({'ok':False,'error':str(e)}));sys.exit(1)
