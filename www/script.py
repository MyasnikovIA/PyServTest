import sys
import json 
request = sys.stdin.readline()
print(request)
print( type(request))
print(globals())
for a in range(1,10):
    print('<h1>',a,'</h1>',end='')