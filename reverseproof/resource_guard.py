"""Sequential local job monitor. Whole-system swap changes are not causal attribution."""
import os,signal,subprocess,time

def guarded(cmd,log,timeout=900):
 import psutil
 baseline=psutil.swap_memory().used;started=time.monotonic();peak=0;low_since=None;reason=None
 with log.open("x") as stream:
  child=subprocess.Popen(cmd,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
  while child.poll() is None:
   try:
    process=psutil.Process(child.pid)
    rss=sum(p.memory_info().rss for p in [process]+process.children(recursive=True));peak=max(peak,rss)
   except psutil.Error:rss=0
   now=time.monotonic();available=psutil.virtual_memory().available;swap=psutil.swap_memory().used-baseline
   low_since=(low_since or now) if available<512*1024**2 else None
   if rss>6*1024**3:reason="process tree RSS above 6 GiB"
   elif swap>1536*1024**2:reason="whole-system swap growth above 1536 MiB (not causal attribution)"
   elif low_since and now-low_since>=5:reason="available memory below 512 MiB for 5 seconds"
   elif now-started>timeout:reason="job timeout"
   if reason:
    try:os.killpg(child.pid,signal.SIGTERM)
    except ProcessLookupError:pass
    try:child.wait(timeout=5)
    except subprocess.TimeoutExpired:
     try:os.killpg(child.pid,signal.SIGKILL)
     except ProcessLookupError:pass
     child.wait()
    break
   time.sleep(.5)
 return {"exit_code":child.returncode,"guard_stop":reason,"peak_process_tree_rss_bytes":peak,"elapsed_seconds":time.monotonic()-started,"system_swap_growth_bytes":psutil.swap_memory().used-baseline,"log":log.name}
