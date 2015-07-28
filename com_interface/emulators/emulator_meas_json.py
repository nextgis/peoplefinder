# -*- coding: utf-8 -*-
import time
import random

data = """
{
   "scenario" : "",
   "time" : %d,
   "name" : "",
   "meas_rep" : {
      "L1_FPC" : false,
      "DL_MEAS" : {
         "RXQ-SUB" : 0,
         "RXQ-FULL" : 0,
         "RXL-SUB" : -75,
         "RXL-FULL" : -75
      },
      "L1_TA" : 2,
      "NUM_NEIGH" : 0,
      "NR" : 24,
      "L1_MS_PWR" : 33,
      "BS_POWER" : 0,
      "UL_MEAS" : {
         "RXQ-SUB" : 0,
         "RXQ-FULL" : 0,
         "RXL-SUB" : -47,
         "RXL-FULL" : -47
      },
      "NEIGH" : []
   },
   "imsi" : "%d"
}
"""

if __name__ == "__main__":
    i = 0

    while True:
        print data.replace('\n', '') % (long(time.time()), random.randint(10, 99))
        time.sleep(1)
