# WDNAS-Client

## About
This module allows users to connect to their local WD NAS and view system info (Storage capacity, Disk temp, volumes etc..)
Its heavily a WIP and is my first public python module

My end goal with this is to link into Home Assistant so I can monitor my WD NAS

## Code

First create the client with the username, password and the host (Be that hostname or IP address)

__Admin account is requred!__

Now call the functions to obtain wanted data - Thats it!

```
import asyncio
from wdnas_client import client

async def main():
    username = input("Username: ").lower()
    password = input("Password: ")
    host = '192.168.86.41'
    
    async with client(username, password, host) as wdNAS:
        print("System Info:", await wdNAS.system_info())
        print("Share Names:", await wdNAS.share_names())
        print("System Status:", await wdNAS.system_status())
        print("Network Info:", await wdNAS.network_info())
        print("Device Info:", await wdNAS.device_info())
        print("System Version:", await wdNAS.system_version())
        print("Latest Version:", await wdNAS.latest_version())
        print("Accounts:", await wdNAS.accounts())
        print("Alerts:", await wdNAS.alerts())

if __name__ == "__main__":
    asyncio.run(main())
```

## Important Info

I have only tested this on my WD NAS which is a wdmycloud mirror running version 2.13.108

Its an old one and so I cannot say if this system works for any newer WD NAS drives
