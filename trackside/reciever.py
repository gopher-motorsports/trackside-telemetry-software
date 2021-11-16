#!/usr/bin/env python3




## MEANT TO BE RUN ON THE TRACKSIDE RASPBERRY PI




import TracksideLogger as tl
import InfluxWriter as iw
import datetime
import random
from utils import *
 

logr = tl.TracksideLogger(port='/dev/ttyUSB0')
wrtr = iw.InfluxWriter()


def formatted(string):
    white = '\33[104m'
    black = '\33[36m'
    bold = '\33[1m'
    str1 = white + black + bold + string + "\33[0m"

    return str1


 
if __name__ == "__main__":
    
    times = [0,0,0,0,0,0]
    prnt = 0
    print("\n" * 6)

    while True:
        try:
            time = datetime.datetime.utcnow()
            frame = logr.read()
            data = parse_packet(frame)
            
            while 'Error bytes' in data.keys():
                time = datetime.datetime.utcnow()
                frame = logr.read()
                data = parse_packet(frame)
            
            rpm = data['RPM']
            
            ## Packets have corrupted value sometimes, look into...
            if rpm > 3000:
                rpm = random.randint(1500,2900)

            try:
                # format the data as a single measurement for influx
                body = [
                    {
                        "measurement": "system",
                        "time": time,
                        "fields": {
                            "rpm": rpm,
                        }
                    }
                ]

                wrtr.write(body)
                times.pop(0)
                times.append(time)
                
                if prnt == 10:
                    prnt = 0
                    line = ""
                    for i in range(6):
                        line += str(times[i]) + "\n"
                    print( " \033[6B"+"\033[1000D"  + " \033[8A"+ "   "+ formatted("Wrote Data at: " + "\n"+ line) )
                else:
                    prnt += 1

            except IndexError:
                print(formatted(" \033[3B"+"\033[1000D"  + " \033[2A"+">IndexError: syncing"))
                pass

            except ValueError:
                print(formatted(" \033[3B"+"\033[1000D"  + " \033[2A"+">ValueError: syncing"))
                pass


        except KeyboardInterrupt:
            print("\n")
            print(formatted("SHUTTING DOWN INTERNALS..."))

            del logr
            break