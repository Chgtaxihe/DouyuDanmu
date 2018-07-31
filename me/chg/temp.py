import re

p = re.compile(r'"ip":"([0-9\.]+)"')

with open(r'C:\Users\Chgtaxihe\Desktop\1.txt','r') as f:
    str = f.readline()
    ports = p.findall(str)
result = ''
for port in ports:
    result = result + 'ip.addr == '+port +'||'
print(result)