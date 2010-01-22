#!/usr/bin/env python
from gct_pat_test import *
from config import *

p1 = PatternList("OneAboveThreshold",conf)
p1 += Pattern("NW",
             Taus = 1,
             Jets = 0,
             EPattern = [ v3  , 0   , 0  ,
                          0   , v9 , 0  ,
                          0   , 0   , 0  ]
             )

p1 += Pattern("N",
             Taus = 1,
             Jets = 0,
             EPattern = [ 0   , v3   , 0  ,
                          0   , v9 , 0  ,
                          0   , 0   , 0  ]
             )

p1 += Pattern("NE",
             Taus = 1,
             Jets = 0,
             EPattern = [ 0  , 0   , v3  ,
                          0   , v9 , 0  ,
                          0   , 0   , 0  ]
             )

p1 += Pattern("W",
             Taus = 1,
             Jets = 0,
             EPattern = [ 0  , 0   , 0  ,
                          v3   , v9 , 0  ,
                          0   , 0   , 0  ]
             )

p1 += Pattern("E",
             Taus = 1,
             Jets = 0,
             EPattern = [ 0  , 0   , 0  ,
                          0   , v9 , v3  ,
                          0   , 0   , 0  ]
             )

p1 += Pattern("SW",
             Taus = 1,
             Jets = 0,
             EPattern = [ 0  , 0   , 0  ,
                          0   , v9 , 0  ,
                          v3   , 0   , 0  ]
             )

p1 += Pattern("S",
             Taus = 1,
             Jets = 0,
             EPattern = [ 0  , 0   , 0  ,
                          0   , v9 , 0  ,
                          0   , v3   , 0  ]
             )
p1 += Pattern("SE",
             Taus = 1,
             Jets = 0,
             EPattern = [ 0  , 0   , 0  ,
                          0   , v9 , 0  ,
                          0   , 0   , v3  ]
             )
p1.Compile()

p2=PatternList("TwoAboveThreshold",conf)

p2 += Pattern("NW_N",
	     Taus = 0,
	     Jets = 1,
             EPattern = [ v3 , v3 , 0 ,
			  0  , v9 , 0 ,
			  0  , 0  , 0 ]
	    )

p2+=Pattern("N_NE",
	   Taus = 0,
           Jets = 1,
	   EPattern = [ 0 , v3 , v3 ,
			0 , v9 , 0 ,
			0 , 0  , 0 ]
	   )

p2+=Pattern("NW_W",
	   Taus = 0,
	   Jets = 1,
	   EPattern = [ v3 , 0 , 0 ,
			v3 , v9 , 0 ,
			0  , 0  , 0 ]
)

p2+=Pattern("NE_E",
	   Taus = 0,
           Jets = 1,
           EPattern = [ 0 , 0 , v3 ,
			0 , v9 , v3 ,
			0 , 0  , 0 ]
)

p2+=Pattern("W_SW",
	   Taus = 0,
	   Jets = 1,
	   EPattern = [ 0 , 0 , 0 ,
			v3 , v9 , 0 ,
			v3 , 0  , 0 ]
)

p2+=Pattern("E_SE",
	   Taus = 0,
	   Jets = 1,
	   EPattern = [ 0 , 0 ,  0 ,
		        0 , v9 , v3 ,
			0 , 0 ,  v3 ]
)

p2+=Pattern("SW_S",
          Taus=0,
          Jets=1,
          EPattern = [ 0 , 0 , 0 ,
                       0 , v9 , 0 ,
                       v3, v3 , 0 ]
)

p2+=Pattern("S_SE",
           Taus=0,
           Jets=1,
           EPattern = [ 0 , 0 , 0 ,
                        0 , v9 , 0 ,
                        0 , v3 , v3 ]
)
p2.Compile()

p3=PatternList("ThreeAboveThreshold",conf)

p3+=Pattern("N_NW_W",
           Taus=0,
           Jets=1,
           EPattern = [ v3 , v3 , 0 ,
                        v3 , v9 , 0 ,
                        0  , 0  , 0 ]
)

p3+=Pattern("N_NE_E",
           Taus=0,
           Jets=1,
           EPattern = [ 0 , v3 , v3 ,
                        0 , v9 , v3 ,
                        0 , 0 , 0 ]
)

p3+=Pattern("W_SW_S",
           Taus=0,
           Jets=1,
           EPattern = [ 0 , 0 , 0,
                        v3 , v9 , 0,
                        v3 , v3 , 0]
)

p3+=Pattern("E_SE_S",
           Taus=0,
           Jets=1,
           EPattern = [ 0 , 0 , 0,
                        0 , v9 , v3 ,
                        0 , v3 , v3 ]
)

p3+=Pattern("NW_W_SW",
           Taus=0,
           Jets=1,
           EPattern = [ v3 , 0 , 0,
                        v3 , v9 , 0,
                        v3 , 0 , 0 ]
)

p3+=Pattern("NW_N_NE",
           Taus=0,
           Jets=1,
           EPattern = [ v3 , v3 , v3,
                        0 , v9 , 0 ,
                        0 , 0  , 0 ]
)

p3+=Pattern("SW_S_SE",
           Taus=0,
           Jets=1,
           EPattern = [ 0 , 0 , 0 ,
                        0 , v9 , 0 ,
                        v3 , v3 , v3 ]
)

p3+=Pattern("NE_E_SE",
           Taus=0,
           Jets=1,
           EPattern = [ 0 , 0 , v3 ,
                        0 , v9 , v3 ,
                        0 , 0  , v3 ]
)

p3.Compile()

master_pattern = p1 + p2 + p3
print master_pattern.patterns
master_pattern.name="master"
master_pattern.Compile()



