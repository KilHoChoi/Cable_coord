print("test")
a = 1;

<<<<<<< Updated upstream
import pandas as pd
import numpy as np
=======
# df1 = pd.read_excel('CableConfig_INP.xlsx',"profile") # profile info
# df1 = df1.dropna(how='all',axis='columns').dropna(how='all')
# df1 = df1.astype(float)

# g1 = 1.0;

## Description 
# Calculate coordinates of cable anchorage of cable-stayed bridge
# assume parabola curve for cable configuration
# 

# import libraries
import math
import sympy as sp

## Data inputs
g1 = 0.020981       # initial roadway grade
g2 = -0.010898      # final roadway grade 
Lc = 960            # length of the vertical curve measured in a horizontal plane, m
STA_PVC = 3567      # station of PVC(Point of Vertical Curvature)
ELE_PVC = 65.371    # elevation of PVC, m
off= 1.18           # offset from pavement to COG

STA_PY1 = 4282      # station of PY1
STA_CAB = 4302      # station of the cable
L2 = 2.029          # dimension of the anchorage at deck, m (refers to fig. )
L3 = 1.975          # dimension of the anchorage at deck, m (refers to fig. )
X_WPTOP = 0         # x-coord. of WPTOP, m (refers to fig. )
Y_WPTOP = 132.263   # y-coord. of WPTOP, m (refers to fig. )
A = 0.01541/2       # Area of the cable, m2
F = 910.8/2         # cable force
w = 0.13796/2       # weight of cable(along the cable)
E = 19300000        # Young's modulus, ton/m2
X2_1 = 3.5          # 1st trial of X2, m
d2 = 0.4            # pylon side anchorage dimension (refers to fig. )
d1 = 0.4            # pylon side anchorage dimension (refers to fig. )
 
## Girder side anchorage coordinates (X_WPA, Y_WPA)
X_WPA = STA_CAB - STA_PY1  
Y_WPA = (g2-g1)/2/Lc*(STA_CAB-STA_PVC)**2+g1*(STA_CAB-STA_PVC)+ELE_PVC-off

alpha_c = math.atan((Y_WPTOP-Y_WPA)/(X_WPTOP-X_WPA))

# Cable equation y = K2*x**2 + K1*x + K0
alpha, x, y, xA, xB, yA = sp.symbols('alpha x y xA xB yA') 
H = F*sp.cos(alpha)
q = w/sp.cos(alpha)

K2 = q/2/H
K0 = yA - sp.tan(alpha)*xA + K2*xA*xB
K1 = sp.tan(alpha) - K2*(xA+xB)
y = K2*x**2 + K1*x + K0 
dy = sp.diff(y,x)

X_WP3 = X_WPA - L2*sp.cos(alpha)
Y_WP3 = Y_WPA - L2*sp.sin(alpha)

for i in range(1,11):
    X_WP3_tmp = X_WP3.subs(alpha, alpha_c)
    Y_WP3_tmp = Y_WP3.subs(alpha, alpha_c)
    
    alpha_tmp = math.atan((Y_WPTOP-Y_WP3_tmp)/(X_WPTOP-X_WP3_tmp))
    
    K2_tmp = K2.subs(alpha, alpha_tmp)
    K1_tmp = K1.subs({alpha: alpha_tmp, xA: X_WP3_tmp, xB: X_WPTOP})
    K0_tmp = K0.subs({alpha: alpha_tmp, xA: X_WP3_tmp, xB: X_WPTOP, yA:Y_WP3_tmp}) 
 
    dy_tmp = 2*K2_tmp*x + K1_tmp
    
    theta_WPTOP = math.atan(dy_tmp.subs(x,X_WPTOP))
    theta_WP3 = math.atan(dy_tmp.subs(x,X_WP3_tmp))
    
    err = abs(theta_WP3-alpha_tmp)
    print(X_WP3_tmp)
    print(Y_WP3_tmp)
    
    # print(theta_WP3)
    # print(err)
    if err < 0.00001: break
    
    alpha_c = theta_WP3


    
    
>>>>>>> Stashed changes

