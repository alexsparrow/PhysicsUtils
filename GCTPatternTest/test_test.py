#!/usr/bin/env python
from gct_pat_test import *
from config import *

p = PatternList("OneAboveThreshold",conf)
p += Pattern("NW",
             Taus = 1,
             Jets = 0,
             EPattern = [ v2  , 0   , 0  ,
                          0   , v9 , 0  ,
                          0   , 0   , 0  ]
             )

p += Pattern("N",
             Taus = 1,
             Jets = 0,
             EPattern = [ 0   , v3   , 0  ,
                          0   , v9 , 0  ,
                          0   , 0   , 0  ]
             )

p += Pattern("NE",
             Taus = 1,
             Jets = 0,
             EPattern = [ 0  , 0   , v3  ,
                          0   , v9 , 0  ,
                          0   , 0   , 0  ]
             )

p += Pattern("W",
             Taus = 1,
             Jets = 0,
             EPattern = [ 0  , 0   , 0  ,
                          v3   , v9 , 0  ,
                          0   , 0   , 0  ]
             )

p += Pattern("E",
             Taus = 1,
             Jets = 0,
             EPattern = [ 0  , 0   , 0  ,
                          0   , v9 , v3  ,
                          0   , 0   , 0  ]
             )

p += Pattern("SW",
             Taus = 1,
             Jets = 0,
             EPattern = [ 0  , 0   , 0  ,
                          0   , v9 , 0  ,
                          v3   , 0   , 0  ]
             )

p += Pattern("S",
             Taus = 1,
             Jets = 0,
             EPattern = [ 0  , 0   , 0  ,
                          0   , v9 , 0  ,
                          0   , v3   , 0  ]
             )
p += Pattern("SE",
             Taus = 1,
             Jets = 0,
             EPattern = [ 0  , 0   , 0  ,
                          0   , v9 , 0  ,
                          0   , 0   , v3  ]
             )
p.Compile()

p=PatternList("TwoAboveThreshold",conf)

p += Pattern("NW_N",
	     Taus = 0,
	     Jets = 1,
             EPattern = [ v3 , v3 , 0 ,
			  0  , v9 , 0 ,
			  0  , 0  , 0 ]
	    )
	
p+=Pattern("N_NE",
	   Taus = 0,
           Jets = 1,
	   EPattern = [ 0 , v3 , v3 ,
			0 , v9 , 0 ,
			0 , 0  , 0 ]
	   )

p+=Pattern("NW_W",
	   Taus = 0,
	   Jets = 1,
	   EPattern = [ v3 , 0 , 0 ,
			v3 , v9 , 0 ,
			0  , 0  , 0 ]
)

p+=Pattern("NE_E",
	   Taus = 0,
           Jets = 1,
           EPattern = [ 0 , 0 , v3 ,
			0 , v9 , v3 ,
			0 , 0  , 0 ]
)

p+=Pattern("W_SW",
	   Taus = 0,
	   Jets = 1,
	   EPattern = [ 0 , 0 , 0 ,
			v3 , v9 , 0 ,
			v3 , 0  , 0 ]
)

p+=Pattern("E_SE",
	   Taus = 0,
	   Jets = 1,
	   EPattern = [ 0 , 0 , 0 ,
		        0 , v9 , v3 ,
			0 , 0 , v3 ]
)
