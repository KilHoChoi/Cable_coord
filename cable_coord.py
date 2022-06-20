
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

filename = 'CableConfig_INP.xlsx'
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
        
    cable_no = cable['Cable #'][ii]
    STA_PY1 = cable['PY1'][ii]      # station of PY1
    STA_CAB = cable['Station'][ii]      # station of the cable
    L2 = cable['L2'][ii]         # dimension of the anchorage at deck, m (refers to fig. )
    L3 = cable['L3'][ii]            # dimension of the anchorage at deck, m (refers to fig. )
    X_WPTOP = cable['X(WPTOP)'][ii]           # x-coord. of WPTOP, m (refers to fig. )
    Y_WPTOP = cable['Y(WPTOP)'][ii]   # y-coord. of WPTOP, m (refers to fig. )
    A = cable['A'][ii]       # Area of the cable, m2
    F = cable['F'][ii]         # cable force
    w = cable['W'][ii]       # weight of cable(along the cable)
    E = cable['E'][ii]        # Young's modulus, ton/m2
    X2_1 = cable['X2(1)'][ii]          # 1st trial of X2, m
    d2 = cable['d2'][ii]            # pylon side anchorage dimension (refers to fig. )
    d1 = cable['d1'][ii]            # pylon side anchorage dimension (refers to fig. )
    
    off= cable['off'][ii]           # offset from pavement to COG
    B1 = cable['B1'][ii]
    B2 = cable['B2'][ii]
    D1 = cable['D1'][ii]
    D2 = cable['D2'][ii]
    t_shim = cable['t_shim'][ii]
    
    
     
    ## Girder side anchorage coordinates (X_WPA, Y_WPA)
    X_WPA = STA_CAB - STA_PY1  
    Y_WPA = (g2-g1)/2/Lc*(STA_CAB-STA_PVC)**2+g1*(STA_CAB-STA_PVC)+ELE_PVC-off
    
    if X_WPTOP < X_WPA:
        L2 = -L2
        L3 = -L3
    
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
    

    X_WP3 = X_WPA + L2*sp.cos(alpha)
    Y_WP3 = Y_WPA + L2*sp.sin(alpha)

    
    for i in range(1,11):
        X_WP3_tmp = X_WP3.subs(alpha, alpha_c)
        Y_WP3_tmp = Y_WP3.subs(alpha, alpha_c)
        
        alpha_tmp = math.atan((Y_WPTOP-Y_WP3_tmp)/(X_WPTOP-X_WP3_tmp))
        
        K2_tmp = K2.subs(alpha, alpha_tmp)
        K1_tmp = K1.subs({alpha: alpha_tmp, xA: X_WP3_tmp, xB: X_WPTOP})
        K0_tmp = K0.subs({alpha: alpha_tmp, xA: X_WP3_tmp, xB: X_WPTOP, yA:Y_WP3_tmp}) 
     
        dy_tmp = 2*K2_tmp*x + K1_tmp
        
        theta_WPTOP = math.atan(dy_tmp.subs(x,X_WPTOP))
        
        # theta_WP3 = math.atan(dy_tmp.subs(x,X_WP3_tmp))        
        # err = abs(theta_WP3-alpha_c)*180/math.pi
        
        theta_WP3 = math.atan(dy_tmp.subs(x,0))
        err = abs(theta_WP3-alpha_c)*180/math.pi


        # print(theta_WP3*180/math.pi)
        # print(err)

        if err < 0.00001: break
        
        alpha_c = theta_WP3

    y = y.subs({K2:K2_tmp,K1:K1_tmp,K0:K0_tmp})
    dy = sp.diff(y,x)


    # find (x2,y2)
    x2 = X2_1
    for i in range(1,11):
        y2 = y.subs(x,x2)
        m_tan = dy.subs(x,x2)
        A1 = -1/m_tan
        A2 = -A1*x2+y2
        x3 = -(A2-B2)/(A1-B1)
        y3 = A1*x3+A2
        L = math.sqrt((x2-x3)**2+(y2-y3)**2)
        err = abs(L-d2)/L
        
        # print(err)
        if err < 0.00001: break
        
        theta_WP2 =math.atan(m_tan)
        dx2 = (L-d2)*math.sin(theta_WP2)
        x2 = x2 + dx2
        
    x4 = x2-d1*math.sin(theta_WP2)
    y4 = y2+d1*math.cos(theta_WP2)    
    
    # x5, y5
    C1 = m_tan
    C2 = -m_tan*x4+y4
    
    x5 = -(B2-C2)/(B1-C1)
    y5 = C1*x5+C2
    
    #x1, y1 (intersection point of cable curve and outer line of pylon which is given in drawing)
    K2 = K2_tmp
    K1 = K1_tmp
    K0 = K0_tmp
    x1 = -((K1-D1) + math.sqrt((K1-D1)**2-4*K2*(K0-D2)))/(2*K2)
    y1 = D1*x1 + D2
    
    if y1 > y2 :
        x1 = -((K1-D1) - math.sqrt((K1-D1)**2-4*K2*(K0-D2)))/(2*K2)
        y1 = D1*x1 + D2
        
    # Cable length and Elongation
    a_chord = math.atan((Y_WP3_tmp-y2)/(X_WP3_tmp-x2))
    w_cbl = w*math.cos(a_chord)
    L_chord = math.sqrt((X_WP3_tmp-x2)**2+(Y_WP3_tmp-y2)**2)
    
    S_strs = 2*F/w_cbl*math.sinh((w_cbl*L_chord)/(2*F))
    dS =  F**2/(2*E*A*w_cbl)*(math.sinh((w_cbl*L_chord)/F)+w_cbl*L_chord/F)    
    S0 = S_strs - dS + t_shim
    
    # output
    out_X_WPA = X_WPA
    out_Y_WPA = Y_WPA
    out_X_WP3 = X_WP3_tmp
    out_Y_WP3 = Y_WP3_tmp
    out_X_WP4 = X_WP3_tmp + L3*math.cos(theta_WP3)
    out_Y_WP4 = Y_WP3_tmp + L3*math.sin(theta_WP3)
    out_x1 = x1
    out_y1 = y1
    out_x2 = x2
    out_y2 = y2
    out_x3 = x3
    out_y3 = y3
    out_x4 = x4
    out_y4 = y4
    out_x5 = x5
    out_y5 = y5
    out_X_WPTOP = X_WPTOP
    out_Y_WPTOP = Y_WPTOP
    out_thet_WPA = theta_WP3*180/math.pi
    out_thet_WPTOP = math.atan(dy.subs(x,x2))*180/math.pi
    out_chord_len1 = math.sqrt((X_WPA-X_WPTOP)**2+(Y_WPA-Y_WPTOP)**2)
    out_chord_len2 = L_chord
    out_str_len = S_strs
    out_elong = dS
    out_unstr_len = S0
    
    # out_df['X_WPA'][ii] = out_X_WPA


