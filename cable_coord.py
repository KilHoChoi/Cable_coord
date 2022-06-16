
## Description 
# Calculate coordinates of cable anchorage of cable-stayed bridge
# assume parabola curve for cable configuration
# 

# import libraries
import math
import sympy as sp
import pandas as pd

############################################################################ 
# Read input excel file (in charge of SNYU)
# CableConfig_INP.xlsx 의 값 가져온다 
# 아래 Data inputs 상수들을 Dataframe 값과 연결시킨다.
############################################################################

filename = 'C:/Users/yoosa/Desktop/Github/Tools-test/CableConfig_INP.xlsx'
#파일 경로 복사해서 사용시 \를 /로 수정


profile  = pd.read_excel(filename,sheet_name ='profile')
cable  = pd.read_excel(filename,sheet_name ='Cable')
aaa = min(profile.isna().sum())
bbb = min(cable.isna().sum())

profile  = pd.read_excel(filename,sheet_name ='profile',skiprows = aaa+1)
cable  = pd.read_excel(filename,sheet_name ='Cable',skiprows = bbb+3)




for ii in range(0,len(cable['Cable #'])):
    ## Data inputs
    g1 = profile['g1'][0]       # initial roadway grade
    g2 = profile['g2'][0]      # final roadway grade 
    Lc = profile['Lc'][0]            # length of the vertical curve measured in a horizontal plane, m
    STA_PVC = profile['sta(PVC)'][0]      # station of PVC(Point of Vertical Curvature)
    ELE_PVC = profile['elev(PVC)'][0]    # elevation of PVC, m
    off= 1.18           # offset from pavement to COG
    
    cable_no = cable['Cable #'][ii]
    STA_PY1 = cable['PY1'][0]      # station of PY1
    STA_CAB = cable['Station'][ii]      # station of the cable
    L2 = cable['L2'][ii]         # dimension of the anchorage at deck, m (refers to fig. )
    L3 = cable['L3'][ii]            # dimension of the anchorage at deck, m (refers to fig. )
    X_WPTOP = cable['X(WPTOP)'][ii]           # x-coord. of WPTOP, m (refers to fig. )
    Y_WPTOP = cable['Y(WPTOP)'][ii]   # y-coord. of WPTOP, m (refers to fig. )
    A = cable['A'][ii]       # Area of the cable, m2
    F = cable['F'][ii]         # cable force
    w = cable['W'][ii]/2       # weight of cable(along the cable)
    E = cable['E'][ii]        # Young's modulus, ton/m2
    X2_1 = cable['X2(1)'][ii]          # 1st trial of X2, m
    d2 = cable['d2'][ii]            # pylon side anchorage dimension (refers to fig. )
    d1 = cable['d1'][ii]            # pylon side anchorage dimension (refers to fig. )
     
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

    


