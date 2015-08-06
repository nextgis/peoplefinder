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
      "L1_TA" : %d,
      "NUM_NEIGH" : 0,
      "NR" : 0,
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
   "imsi" : "%s"
}
"""

if __name__ == "__main__":
    # for i in range(0, 5):
    #     print data.replace('\n', '') % (long(time.time()), str(random.randint(10, 99))
    #     time.sleep(1)

    for imsi in ['250026686759664', '250015890007249', '250993117364821', '250018520598185', '250018527269573', '250026606991248', '250026685233027', '250993192734211', '250997102433501']:
        print data.replace('\n', '') % (long(time.time()), random.randint(0, 3), imsi)
        time.sleep(1)
