import os
import subprocess

p = subprocess.Popen(["dotnet", "HeroesDecode/heroesdecode.dll", "-p", "replay.StormReplay", "-s"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                 )
stdout, stderr = p.communicate()
p.wait()
out = stdout.decode('cp866')
print(out)
print(stderr)