'''
Created on 23 mars 2021

@author: Adrien Lucca
'''
import numpy as np 
import matplotlib.pyplot as plt
import GeoSyn as G 

"""step1"""
        
def line_pattern(line):
    
    pattern = ""
    
    if line[0] == "F" or line[0] == "G" or line[0] == "I" or line[0] == "J" or line[0] == "S" or line[0] == "T" or line[0] == "M" or line[0] == "X" or line[0] == "Y" or line[0] == "Z":

        for i in xrange(len(line)):
            
            try: 
                int(line[i][0])
            except:
                val = line[i][0]
                if val != "." and val != "-" and val != " " and val != "\n":
                    pattern += val
    
    return pattern

def linetype_words_pattern(line):
    
    linetype = None
    words = None
    pattern = None

    if line[0] == "(":
        linetype = "comment"
    elif line[0] == "%":
        linetype = "start or end"
    else:
        pattern = line_pattern(line)
        number_of_words = len(pattern)
        linetype = "words"
        
        if number_of_words > 1:
            words = line.split(" ")
            
        else:
            words = line 
        
        
        
    return linetype, words, pattern

def GG_line(line):
    
    print "GG_line", line
    
    words = linetype_words_pattern(line)[1]
    
    print "words", words
    
    word1 = words[0]
    truncated_line = ""
    for i in xrange(len(words)-1):
        truncated_line += str(words[i+1])+" "
    
    print "word1", word1
    print "trucated_line", truncated_line 
    
    return word1, truncated_line
      
def STEP1_split_GG_lines(fn_in, fn_out):
    
    lines = np.loadtxt(fn_in, dtype=str, delimiter="\n")
    
    f = open(fn_out, "w")
    
    for i in xrange(len(lines)):
    
        line = lines[i]
        
        print ""
        print "debug",line
        
        linetype, words, pattern = linetype_words_pattern(line)
        
        if linetype == "start or end" or linetype == "comment":
            
            f.write(line+"\n")
            print line
        
        elif len(pattern) >= 2:
            if pattern[0:2] == "GG":
                
                word1, new_line = GG_line(line)
                
                f.write(word1+"\n")
                print word1
                
                print "new_line", new_line
                
                linetype, words, pattern = linetype_words_pattern(new_line)
                
                print "pattern", pattern
                
                if len(pattern) == 1:
                    f.write(words+"\n")
                    print words
                else:
                    for word in words:
                        f.write(word+" ")
                        print word,
                    f.write("\n")
                    print""
            else:
                if len(pattern) == 1:
                    f.write(words+"\n")
                    print words
                else:
                    for word in words:
                        f.write(word+" ")
                        print word,
                    f.write("\n")
                    print ""
                    
        else:
            
            if len(pattern) == 1:
                f.write(words+"\n")
                print words
            else:
                for word in words:
                    f.write(word+" ")
                    print word,
                f.write("\n")
                print ""
    
    f.close()
    print fn_out, "written"
    
    return None

"""step2"""

def gcode_current_mode(current_mode, line):
    
    if line[0] == "G":
        return line.split(" ")[0]
        
    else:
        return current_mode

def gcode_current_XYZ(currentXYZ, current_mode, line):
    
    current_mode = gcode_current_mode(current_mode, line)
    words, pattern = linetype_words_pattern(line)[1:3]
    
    words = clean_words(words)
    
    number_of_words = len(pattern)
    
#     print "pattern", pattern 
#     print "number of words", number_of_words
    
    if number_of_words == 1:
        
        letter = words[0]
        value = ""
        for j in xrange(len(words)-1):
            value += str(words[j+1])
        
        value = float(value)
        
#         print "letter", letter 
#         print "value", value
        
        if letter == "X":
            currentXYZ[0] = value
        if letter == "Y":
            currentXYZ[1] = value
        if letter == "Z":
            currentXYZ[2] = value
    
    else:
        
        print "words", words 
        print "len words", len(words)
        for i in xrange(len(words)):
            
            word = words[i]
            
            print "word", word
            
            letter = word[0]
            value = ""
            for j in xrange(len(word)-1):
                value += str(word[j+1])
            
            value = float(value)
            
#             print "letter", letter 
#             print "value", value
            
            if letter == "X":
                currentXYZ[0] = value
            if letter == "Y":
                currentXYZ[1] = value
            if letter == "Z":
                currentXYZ[2] = value
    
    return currentXYZ

def gcode_current_plane(current_plane, current_mode):
    
    if current_mode == "G17":
        current_plane = "XY"
    elif current_mode == "G18":
        current_plane = "ZX"
    elif current_mode == "G19":
        current_plane = "YZ"
    
    return current_plane
        
def linearization_G3toG1(line, previousXYZ, currentXYZ, current_plane, min_arc_len, decimal_places):
    
    print "line", line
    
    initialX, initialY, initialZ = np.array(previousXYZ).astype(float)
    destinationX, destinationY, destinationZ = np.array(currentXYZ).astype(float) 
    
    new_lines = []
    
    words = linetype_words_pattern(line)[1]
    words = clean_words(words)
    
    I = 0
    J = 0 
    K = 0
    F = None
    
    for i in xrange(len(words)):
        
        word = words[i]
        print "word", word
        letter = word[0]
        print "letter", letter
        
        if letter != "G":
            
            value = ""
            for j in xrange(len(word)-1):
                value += str(word[j+1])
            value = float(value)
            
            if letter == "I":
                I = value 
            elif letter == "J":
                J = value 
            elif letter == "K":
                K = value 
            elif letter == "F":
                F = value 
    
    print "IJKF", I, J, K, F

    if current_plane == "XY":
        """G17"""
        
        Zrange = destinationZ - initialZ 
        
        radius = (I**2.+J**2.)**.5 
        current_pos = np.array((initialX, initialY)).astype(float)
        centre = np.array((current_pos[0]+I, current_pos[1]+J)).astype(float)
        destination = np.array((destinationX, destinationY)).astype(float)
        
        print "alpha vals", current_pos[0], centre[0],current_pos[1], centre[1]
        
        alpha = np.arctan2(current_pos[1]-centre[1],current_pos[0]-centre[0])
        beta = np.arctan2(destination[1]-centre[1],destination[0]-centre[0])
        gamma = beta - alpha 
        gamma = np.mod(gamma, 2.*np.pi)
        length = gamma * radius 
        n = int(length/min_arc_len+.5)
        if n < 2:
            n = 2
        
        print "curr posit.", current_pos
        print "destination", destination
        print "center     ", centre
        
        print "alpha", alpha 
        print "beta", beta 
        print "gamma", gamma
        
        print "min_arc_len", min_arc_len 
        print 'length', length
        print "steps", n
        
        for i in xrange(n):
            
            step = i + 1.
            
            print "step", step, "/", n
            
            X = round(np.cos(alpha+step*gamma/float(n))*radius+centre[0], decimal_places)
            Y = round(np.sin(alpha+step*gamma/float(n))*radius+centre[1], decimal_places)
            Z = round(initialZ + step/(float(n)) * Zrange, decimal_places)
            
            if i == 0:
                new_line = "G1 X"+str(X)+" Y"+str(Y)+" Z"+str(Z)
                if F != None:
                    new_line += " F"+str(F)
            else:
                new_line = "X"+str(X)+" Y"+str(Y)+" Z"+str(Z)
            
            new_line += "\n"
            
            new_lines += [new_line]
        
        return new_lines
    
    elif current_plane == "ZX":
        """G18"""
        
        radius = (K**2.+I**2.)**.5 
        current_pos = np.array((initialZ, initialX)).astype(float)
        centre = np.array((current_pos[0]+K, current_pos[1]+I)).astype(float)
        destination = np.array((destinationZ, destinationX)).astype(float)
        
        print "alpha vals", current_pos[0], centre[0],current_pos[1], centre[1]
        
        alpha = np.arctan2(current_pos[1]-centre[1],current_pos[0]-centre[0])
        beta = np.arctan2(destination[1]-centre[1],destination[0]-centre[0])
        gamma = beta - alpha 
        gamma = np.mod(gamma, 2.*np.pi)
        length = gamma * radius 
        n = int(length/min_arc_len+.5)
        if n < 2:
            n = 2
        
        print "curr posit.", current_pos
        print "destination", destination
        print "center     ", centre
        
        print "alpha", alpha 
        print "beta", beta 
        print "gamma", gamma
        
        print "min_arc_len", min_arc_len 
        print 'length', length
        print "steps", n
        
        for i in xrange(n):
            
            step = i + 1.
            
            print "step", step, "/", n
            
            Z = round(np.cos(alpha+step*gamma/float(n))*radius+centre[0], decimal_places)
            X = round(np.sin(alpha+step*gamma/float(n))*radius+centre[1], decimal_places)
            
            if i == 0:
                new_line = "G1 X"+str(X)+" Z"+str(Z)
                if F != None:
                    new_line += " F"+str(F)
            else:
                new_line = "X"+str(X)+" Z"+str(Z)
            
            new_line += "\n"
            
            new_lines += [new_line]
        
        return new_lines
    
    elif current_plane == "YZ":
        
        radius = (J**2.+K**2.)**.5 
        current_pos = np.array((initialY, initialZ)).astype(float)
        centre = np.array((current_pos[0]+J, current_pos[1]+K)).astype(float)
        destination = np.array((destinationY, destinationZ)).astype(float)
        
        print "alpha vals", current_pos[0], centre[0],current_pos[1], centre[1]
        
        alpha = np.arctan2(current_pos[1]-centre[1],current_pos[0]-centre[0])
        beta = np.arctan2(destination[1]-centre[1],destination[0]-centre[0])
        gamma = beta - alpha 
        gamma = np.mod(gamma, 2.*np.pi)
        length = gamma * radius 
        n = int(length/min_arc_len+.5)
        if n < 2:
            n = 2
        
        print "curr posit.", current_pos
        print "destination", destination
        print "center     ", centre
        
        print "alpha", alpha 
        print "beta", beta 
        print "gamma", gamma
        
        print "min_arc_len", min_arc_len 
        print 'length', length
        print "steps", n
        
        for i in xrange(n):
            
            step = i + 1.
            
            print "step", step, "/", n
            
            Y = round(np.cos(alpha+step*gamma/float(n))*radius+centre[0], decimal_places)
            Z = round(np.sin(alpha+step*gamma/float(n))*radius+centre[1], decimal_places)
            
            if i == 0:
                new_line = "G1 Y"+str(Y)+" Z"+str(Z)
                if F != None:
                    new_line += " F"+str(F)
            else:
                new_line = "Y"+str(Y)+" Z"+str(Z)
            
            new_line += "\n"
            
            new_lines += [new_line]
        
        return new_lines
    
    else:
        
        print "error no plane selected!"
        return None

def linearization_G2toG1(line, previousXYZ, currentXYZ, current_plane, min_arc_len, decimal_places):
    
    print "line", line
    
    initialX, initialY, initialZ = np.array(previousXYZ).astype(float)
    destinationX, destinationY, destinationZ = np.array(currentXYZ).astype(float) 
    
    new_lines = []
    
    words = linetype_words_pattern(line)[1]
    words = clean_words(words)
    
    I = 0
    J = 0 
    K = 0
    F = None
    
    for i in xrange(len(words)):
        
        word = words[i]
        print "word", word
        letter = word[0]
        print "letter", letter
        
        if letter != "G":
            
            value = ""
            for j in xrange(len(word)-1):
                value += str(word[j+1])
            value = float(value)
            
            if letter == "I":
                I = value 
            elif letter == "J":
                J = value 
            elif letter == "K":
                K = value 
            elif letter == "F":
                F = value 
    
    print "IJKF", I, J, K, F

    if current_plane == "XY":
        """G17"""
        
        Zrange = destinationZ - initialZ 
        
        radius = (I**2.+J**2.)**.5 
        current_pos = np.array((initialX, initialY)).astype(float)
        centre = np.array((current_pos[0]+I, current_pos[1]+J)).astype(float)
        destination = np.array((destinationX, destinationY)).astype(float)
        
        print "alpha vals", current_pos[0], centre[0],current_pos[1], centre[1]
        
        alpha = np.arctan2(current_pos[1]-centre[1],current_pos[0]-centre[0])
        beta = np.arctan2(destination[1]-centre[1],destination[0]-centre[0])
        gamma = beta - alpha 
        gamma = np.mod(gamma, 2.*np.pi)
        gamma = 2.*np.pi - gamma
        length = gamma * radius 
        n = int(length/min_arc_len+.5)
        if n < 2:
            n = 2
        
        print "curr posit.", current_pos
        print "destination", destination
        print "center     ", centre
        
        print "alpha", alpha 
        print "beta", beta 
        print "gamma", gamma
        
        print "min_arc_len", min_arc_len 
        print 'length', length
        print "steps", n
        
        for i in xrange(n):
            
            step = i + 1.
            
            print "step", step, "/", n
            
            X = round(np.cos(alpha-step*gamma/float(n))*radius+centre[0], decimal_places)
            Y = round(np.sin(alpha-step*gamma/float(n))*radius+centre[1], decimal_places)
            Z = round(initialZ + step/(float(n)) * Zrange, decimal_places)
            
            if i == 0:
                new_line = "G1 X"+str(X)+" Y"+str(Y)+" Z"+str(Z)
                if F != None:
                    new_line += " F"+str(F)
            else:
                new_line = "X"+str(X)+" Y"+str(Y)+" Z"+str(Z)
            
            new_line += "\n"
            
            new_lines += [new_line]
        
        return new_lines
    
    elif current_plane == "ZX":
        """G18"""
        
        radius = (K**2.+I**2.)**.5 
        current_pos = np.array((initialZ, initialX)).astype(float)
        centre = np.array((current_pos[0]+K, current_pos[1]+I)).astype(float)
        destination = np.array((destinationZ, destinationX)).astype(float)
        
        print "alpha vals", current_pos[0], centre[0],current_pos[1], centre[1]
        
        alpha = np.arctan2(current_pos[1]-centre[1],current_pos[0]-centre[0])
        beta = np.arctan2(destination[1]-centre[1],destination[0]-centre[0])
        gamma = beta - alpha 
        gamma = np.mod(gamma, 2.*np.pi)
        gamma = 2.*np.pi - gamma
        length = gamma * radius 
        n = int(length/min_arc_len+.5)
        if n < 2:
            n = 2
        
        print "curr posit.", current_pos
        print "destination", destination
        print "center     ", centre
        
        print "alpha", alpha 
        print "beta", beta 
        print "gamma", gamma
        
        print "min_arc_len", min_arc_len 
        print 'length', length
        print "steps", n
        
        for i in xrange(n):
            
            step = i + 1.
            
            print "step", step, "/", n
            
            Z = round(np.cos(alpha-step*gamma/float(n))*radius+centre[0], decimal_places)
            X = round(np.sin(alpha-step*gamma/float(n))*radius+centre[1], decimal_places)
            
            if i == 0:
                new_line = "G1 X"+str(X)+" Z"+str(Z)
                if F != None:
                    new_line += " F"+str(F)
            else:
                new_line = "X"+str(X)+" Z"+str(Z)
            
            new_line += "\n"
            
            new_lines += [new_line]
        
        return new_lines
    
    elif current_plane == "YZ":
        
        radius = (J**2.+K**2.)**.5 
        current_pos = np.array((initialY, initialZ)).astype(float)
        centre = np.array((current_pos[0]+J, current_pos[1]+K)).astype(float)
        destination = np.array((destinationY, destinationZ)).astype(float)
        
        print "alpha vals", current_pos[0], centre[0],current_pos[1], centre[1]
        
        alpha = np.arctan2(current_pos[1]-centre[1],current_pos[0]-centre[0])
        beta = np.arctan2(destination[1]-centre[1],destination[0]-centre[0])
        gamma = beta - alpha 
        gamma = np.mod(gamma, 2.*np.pi)
        gamma = 2.*np.pi - gamma
        length = gamma * radius 
        n = int(length/min_arc_len+.5)
        if n < 2:
            n = 2
        
        print "curr posit.", current_pos
        print "destination", destination
        print "center     ", centre
        
        print "alpha", alpha 
        print "beta", beta 
        print "gamma", gamma
        
        print "min_arc_len", min_arc_len 
        print 'length', length
        print "steps", n
        
        for i in xrange(n):
            
            step = i + 1.
            
            print "step", step, "/", n
            
            Y = round(np.cos(alpha-step*gamma/float(n))*radius+centre[0], decimal_places)
            Z = round(np.sin(alpha-step*gamma/float(n))*radius+centre[1], decimal_places)
            
            if i == 0:
                new_line = "G1 Y"+str(Y)+" Z"+str(Z)
                if F != None:
                    new_line += " F"+str(F)
            else:
                new_line = "Y"+str(Y)+" Z"+str(Z)
            
            new_line += "\n"
            
            new_lines += [new_line]
        
        return new_lines
    
    else:
        
        print "error no plane selected!"
        return None    
     
def clean_words(words):
    
    print "words to clean", words 
    
    """is it a str or a list?"""
    
    print "words type", type(words)
    
    if type(words) is list:
        
        new_words = []
        for i in xrange(len(words)):
            
            word = words[i]
            
            print "word in list", word
            
            try:
                print "word[0]", word[0]
                new_words += [word]
            except:
                continue
        
        print "new words", new_words 
        
        return new_words
        
    else:
        
        return words
        
def STEP2_linearize_G2G3(fn_in, fn_out, min_arc_len, decimal_places):     
    
    lines = np.loadtxt(fn_in, dtype=str, delimiter="\n")
    
    f = open(fn_out, "w")
    
    current_mode = None
    current_plane = None
    previousXYZ = np.array((None,None,None))   
    currentXYZ = np.array((None,None,None))
    
    for i in xrange(len(lines)):
    
        line = lines[i]
        
        print "debug", line
        
        linetype = linetype_words_pattern(line)[0]
        
        print "linetype", linetype, linetype == "words"
        
        if linetype == "words":
            
            previousXYZ = np.copy(currentXYZ)
            currentXYZ = gcode_current_XYZ(currentXYZ, current_mode, line)
            current_mode = gcode_current_mode(current_mode, line)
            current_plane = gcode_current_plane(current_plane, current_mode)
            
            print "plane", current_plane
            print "prevXYZ", previousXYZ
            print "currXYZ", currentXYZ
            
            if current_mode == "G3":
                
                """linearize G3"""
                print ""
                print "linearize G3"
                new_lines = linearization_G3toG1(line, previousXYZ, currentXYZ, current_plane, min_arc_len, decimal_places)
                
                print "new lines G1", new_lines 
                
                for j in xrange(len(new_lines)):
                    
                    f.write(new_lines[j])
                
            
            elif current_mode == "G2":
                 
                """linearize G2"""
                print ""
                print "linearize G2"
                new_lines = linearization_G2toG1(line, previousXYZ, currentXYZ, current_plane, min_arc_len, decimal_places)
                 
                print "new lines G1", new_lines 
                 
                for j in xrange(len(new_lines)):
                     
                    f.write(new_lines[j])
            
            else:
                
                """write line"""
                print "line to write"
                print line 
                f.write(str(line)+"\n")
        
        else:
                
            """write line"""
            print "line to write"
            print line 
            f.write(str(line)+"\n")      
    
    f.close()
    
    print fn_out, "written"
    return None

"""step3"""

#reconstitution 
def reconstitution_polygon_no_negativeXY(A,AB,AC,AD,BC,BD):
    
    D = A[0], A[1]+AD
    circleAB = G.circle2D(A, AB)
    circleDB = G.circle2D(D, BD)
    
    B1, B2 = G.intersection_circle_circle2D(circleAB, circleDB)
    if B1[0] <=0 or B1[1 <=0]:
        B = B2 
    else:
        B = B1
    
    circleBC = G.circle2D(B, BC)
    circleAC = G.circle2D(A, AC)
    
    C1, C2 = G.intersection_circle_circle2D(circleBC, circleAC)
    if C1[0] <=0 or C1[1 <=0]:
        C = C2 
    else:
        C = C1

    return np.array((A, B, C, D))

def inverse_bilinear(poly_real, point, scale):
    """
    https://www.iquilezles.org/www/articles/ibilinear/ibilinear.htm
    """
    
    a,b,c,d = poly_real
    
    p = np.array(point)
    
    e = b-a 
    f = d-a 
    g = a-b+c-d 
    h = p-a
    
    k2 = np.cross(g,f)
    k1 = np.cross(e,f) + np.cross(h,g)
    k0 = np.cross(h,e)
    
    w = k1**2.-4.*k0*k2 
     
    if w < 0.:
        return -1
    
    w = w**.5
    
    v1 = (-k1 - w)/(2.0*k2)
    u1 = (h[0] - f[0]*v1)/(e[0] + g[0]*v1)

    v2 = (-k1 + w)/(2.0*k2)
    u2 = (h[0] - f[0]*v2)/(e[0] + g[0]*v2)

    u = u1
    v = v1
    
    if v < 0. or v >1. or u <0. or u > 1.:
        u = u2 
        v = v2 
    
    return np.round(np.array((u,v))*scale,3)

def STEP3_correct_linearized_gcode(fn_in, fn_out, real, scale):
    
    a,ab,ac,ad,bc,bd = real
    poly_real = reconstitution_polygon_no_negativeXY(a,ab,ac,ad,bc,bd)
    
    lines = np.loadtxt(fn_in, dtype=str, delimiter="\n")
    
    f = open(fn_out, "w")
    
    current_mode = None
    previousXYZ = np.array((None,None,None))   
    currentXYZ = np.array((None,None,None))
    
    for i in xrange(len(lines)):
    
        line = lines[i]
        
        print "debug", line
        
        linetype, words, pattern = linetype_words_pattern(line)
        
        print "linetype", linetype, linetype == "words"
        
        if linetype == "words":
            
            previousXYZ = np.copy(currentXYZ)
            currentXYZ = gcode_current_XYZ(currentXYZ, current_mode, line)
            current_mode = gcode_current_mode(current_mode, line)
            
            print "prevXYZ", previousXYZ
            print "currXYZ", currentXYZ
            print "current mode", current_mode, len(current_mode)
            
            X, Y, Z = previousXYZ
            F = False
            line_header = False
            
            if current_mode == "G0" or current_mode == "G1":
                
                print line 
                words = clean_words(words)
                
                print words
                
                print "pattern", pattern
                print "len pattern", len(pattern)
                
                if len(pattern) > 1:
                
                    for word in words:
                        
                        if word == "G0" or word == "G1":
                            
                            line_header = word
                        
                        elif word[0] == "X":
                            
                            value = ""
                            for j in xrange(len(word)-1):
                                value += str(word[j+1])
                            X = float(value)
                            
                        elif word[0] == "Y":
                            
                            value = ""
                            for j in xrange(len(word)-1):
                                value += str(word[j+1])
                            Y = float(value)
                        
                        elif word[0] == "Z":
                            
                            print "word[0] is Z, word", word
                            
                            
                            value = ""
                            for j in xrange(len(word)-1):
                                value += str(word[j+1])
                                print "letter", word[j+1]
                            
                            print "value", value
                            Z = float(value)
                            
                        elif word[0] == "F":
                            value = ""
                            for j in xrange(len(word)-1):
                                value += str(word[j+1])
                            F = float(value)
                
                else:
                    
                    if words == "G0" or words == "G1":
                            
                        line_header = words
                    
                    elif words[0] == "X":
                        
                        value = ""
                        for j in xrange(len(words)-1):
                            value += str(words[j+1])
                        X = float(value)
                        
                    elif words[0] == "Y":
                        
                        value = ""
                        for j in xrange(len(words)-1):
                            value += str(words[j+1])
                        Y = float(value)
                    
                    elif words[0] == "Z":

                        value = ""
                        for j in xrange(len(words)-1):
                            value += str(words[j+1])
                        Z = float(value)
                        
                    elif words[0] == "F":
                        value = ""
                        for j in xrange(len(words)-1):
                            value += str(words[j+1])
                        F = float(value)
                    
                
                """now we modify X and Y and we copy the pattern"""
                point = X,Y
                X, Y = inverse_bilinear(poly_real, point, scale)
                
                
                """the new pattern"""
                
                new_line = ""
                
                if line_header != False:
                    new_line += line_header+" "
                
                new_line += "X"+str(X)+" Y"+str(Y)+" Z"+str(Z)
                
                if F != False:
                    new_line += " F"+str(F)
                
                """write line"""
                print "line to write"
                print new_line 
                f.write(str(new_line)+"\n")  
    
            else:
                
                """write line"""
                print "line to write"
                print line 
                f.write(str(line)+"\n")    
                
        else:
                
            """write line"""
            print "line to write"
            print line 
            f.write(str(line)+"\n")    
    
    return None      

"""enter real measurements"""
scale = 60.

A = 0,0
AB = scale
BC = scale
AD = scale
AC = scale*2.**.5
BD = scale*2.**.5

theory = A,AB,AC,AD,BC,BD

#real
a = 0,0
ab = 61.1
bc = 59.5
ad = 59.9
ac = 60.*2.**.5
bd = 61.*2.**.5


real = a,ab,ac,ad,bc,bd

""" """


    
fn_in = "multitest.nc"
fn_out = fn_in+"step1.nc"

#STEP1_split_GG_lines(fn_in, fn_out)

fn_in = fn_out 
fn_out = fn_out+"step2.nc"

min_arc_len = 0.2
decimal_places = 3

#STEP2_linearize_G2G3(fn_in, fn_out, min_arc_len, decimal_places)

fn_in = fn_out 
fn_out = fn_out+"step3.nc"

STEP3_correct_linearized_gcode(fn_in, fn_out, real, scale)
