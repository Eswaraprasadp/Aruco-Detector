"""
Author: Eswara prasad
Domain: Signal Processing and ML
Sub-domain: Image processing
Functions: getRectangles, printIds, findId, validateBits, validatePadding, percentageOfBlackAndWhite,
           returnRoi, removeBlackCells, binaryToDecimal, bitwise_not, xnor
Global variables: img, gray, thresh, thresh_inv, rects  

"""

import cv2
import numpy as np

 ## Function Name: getRectangles
 ## Output: Returns a list of rectangles bouded by contours
 ## Logic: Contours with countour area >= limitArea are bounded by rectangles and coordinates of rectangles are returned
 ## Example call: rectangles = getRectangles()

def getRectangles():
    rects = []
    contours, heirarchy = cv2.findContours(thresh_inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    limitArea = 50
    for c in contours:
        if(cv2.contourArea(c) >= limitArea): # We consider only contours with area greater than limit area
            x, y, w, h = cv2.boundingRect(c)
            rects.append([x, y, w, h])
            
    return rects

 ## Function Name: printIds
 ## Input: Rectangle (coordinates of rectangle)
 ## Output: Prints IDs of valid ArUco markers (returned by findId) on the screen and in detected image.
 ## Logic: Calls validateBorders and findId to find whether the rectangle is an valid ArUco marker.
 ## Example call: printIds(rectangles)
    
def printIds(rects):
    ids = []
    for rect in rects:
        x, y, w, h = rect      
        if(validatePadding(rect) == False): #If borders (black padding layer) of the rectangle are invalid (is not black enough) for it to be a ArUco marker, then it proceedes to the next rectangle in rects
            continue
        
        id, valid = findId(rect)  
        
        if(valid): #If the id is valid then writing it in output image
            ids.append(id)
            
            fontSize = 0.9
            dx = 30   # dx is distance from start of the text to the left corner of marker
            dy = 10   # dy is space between the text and the marker           
                                
            if(y > 30 and w < 120):
                dx = 0  # If width is < 120 then we write the image at the top left corner ie. reduce dx
           
            elif(y < 30 and w >= 120): 
                fontSize = 0.8 # If the the marker is at the top of the image then we reduce the font size and space between text and marker
                dy = 2
            
            elif(y < 30 and w < 120):
                fontSize = 0.8 # If the the marker is at the top of the image and it is small then,
                               # we reduce the font size and space between text and marker and orient it in top left
                dx = 0
                dy = 2
                
            cv2.rectangle(img, (x, y), (x+ w, y+ h), (0, 255, 0), 4) #Enclose the marker with green border
            cv2.putText(img, "ID : %d" % id, (x + dx, y - dy), cv2.FONT_HERSHEY_TRIPLEX, fontSize, (255, 0, 0), 1, cv2.LINE_AA)
            # We Write the ID in blue color
   
    # If there are more than one ID, then printing them with commas in between and an 'and' at last      
    if(len(ids) > 1):
        print("ArUco IDs: ", end = ' ')
        for id in ids[:-1]:
            print(id, end = ', ')
        print("and ", ids[-1], " detected.")
        print("Output Image is in output folder.")
    
    elif(len(ids) == 1):
        print("ArUco ID: ", ids[0], " detected.")
        print("Output Image is in output folder.")
        
    else:
        print("No ArUcos detected.")

## Function Name: findId
 ## Input: Rectangle (coordinates of rectangle)
 ## Output: Returns ID of the marker and True, if it is a valid ID, else -1 and False
 ## Logic: Finds data encoded by each 5x5 grid by percentage of black and white. Then validates the bits by passing to validateBits
 ## Example call: id, valid = findId(rectangle)

def findId(rect):
    bits = []
    databits = []   
    aruco = removeBlackPadding(rect) # aruco is region with padding removed 

    for i in range(5):
        for j in range(5):
            # Find the percentage of black and white in each 5x5 grid. The grid is from i/5 of width to (i+1)/5 of width and j/5 to (j+1)/5 of height
            black, white = percentageOfBlackAndWhite(aruco, i/5, (i+1)/5, j/5, (j+1)/5)
            grid = returnRoi(aruco, i/5 , (i+1)/5 , j/5 , (j+1)/5, returnRect = True)
            
            x, y, w, h = grid            
            gridArea = w * h
            limitArea = 25
            
            if(black >= 85):
                bits.append(0)
            elif(white >= 85):
                bits.append(1)
            elif(gridArea <= limitArea):  
                bits.append(0 if (black >= white) else 1)  
            
            # If the grid area is too small, then the pixels may not be clear.
            # So assuming the grid color is black or white, depending on whichever is greater.
    
    if(validateBits(bits) == False):
        return -1, False
    # If the bits do not follow the hamming code return a False flag
    
    data1 = bits[5:10] # ie. Column 2 of aruco marker
    data2 = bits[15:20] # ie. Column 4 of aruco marker
    
    # Add bits to databtis in alternating fashion
    databits = [None]*(len(data1) + len(data2))
    databits[0::2] = data1
    databits[1::2] = data2
    
    # Find the ID of converting the databits to decimal.
    id = binaryToDecimal(databits)
    
    # If the ID is valid, return the ID and True flag
    if(id >= 0 and id <= 1023):
        return id, True
    
    # Else, return ID and False flag.
    return id, False

 ## Function Name: validateBits
 ## Input: List of bits arranged columnwise
 ## Output: Boolean representing validity of the bits
 ## Logic: Divides bits into parity and data bits and checks the validity by modified hamming code
 ## Example call: valid = validateBits(bits)
    
def validateBits(bits):
    
    parity2 = bits[0: 5]    # ie. Column 1 of aruco marker
    data1 = bits[5: 10]     # ie. Column 2 of aruco marker
    parity3 = bits[10: 15]  # ie. Column 3 of aruco marker
    data2 = bits[15: 20]    # ie. Column 4 of aruco marker
    parity1 = bits[20: 25]  # ie. Column 5 of aruco marker 
    
    # According to the modified hamming code,
    # 1) the parity 2 bits should be inverted of data 1,
    # 2) the parity 3 should be the same as data 2 bits and
    # 3) parity 1 bit in each row should be XOR of parity 2 and parity 3 bits in that row
    
    if(parity3 == data2 and data1 == bitwise_not(parity2) and parity1 == xnor(parity2, parity3)):
        return True
    
    # If the pattern follows hamming code, then return True else False
    return False

 ## Function Name: validatePadding

 ## Input: Rectangle (coordinates of rectangle)

 ## Output: Boolean representing validity of the extra layer of black padding

 ## Logic: Finds percentage of white pixels in the padding area. 
 ##       Returns false if it is greater than limit percentage (7% for normal rectangles and 20% for small rectangles)

 ## Example call: valid = validateBorders(detectedRectangle)
    
def validatePadding(rect):
    
    # Find the percentages of the left, right, top and bottom parts of padding seperately
    blackLeft, whiteLeft = percentageOfBlackAndWhite(rect, 0, 1/7, 0, 1)
    blackRight, whiteRight = percentageOfBlackAndWhite(rect, 6/7, 1, 0, 1)
    blackTop, whiteTop = percentageOfBlackAndWhite(rect, 0, 1, 0, 1/7)
    blackBottom, whiteBottom = percentageOfBlackAndWhite(rect, 0, 1, 6/7, 1)
    
    # Put the percentages of white alone in a list.
    whitePercentages = [whiteLeft, whiteRight, whiteTop, whiteBottom]
    
    # Find the rectangle area
    x, y, w, h = rect
    rectArea = w * h
    
    # Iterate through each part of padding
    # If the percentage of white pixels is greater than a limit, then mark it invalid, ie. return False
    
    for white in whitePercentages:
        if(white >= 7 and rectArea >= 200):
            return False
        elif(white >= 20 and rectArea >= 150):
            return False
        # If the area of the part is too small, then pixels may not be clear, so we increase the tolerable white value
   
    # If all the 4 parts have percentage of white less than the tolerable value, return True 
    return True  

 ## Function Name: percentageOfBlackAndWhite
 
 ## Input: Rectangle, fractions of x and y relative to width and height respectively

 ##        x1 = Distance of Left of required region from Left of image relative to the width.
 ##        Similarly x2 for right, y1 for top, y2 for bottom

 ## Output: Percentage of black and white pixels

 ## Logic: Percentage of white pixels is calculated by counting non zero parts of thresh divided by the total no. of pixels.
 ##        Percentage of black pixels is 100 - (Percentage of white)

 ## Example call: black, white = percentageOfBlackAndWhite(rect, 1/7, 2/7, 4/7, 5/7)
    
def percentageOfBlackAndWhite(rect, x1, x2, y1, y2):
   
    boundaryFraction = 0.03
    # boundaryFraction accounts for removing the outer (border) area when a rectangle is passed.
    
    x1 += boundaryFraction
    x2 -= boundaryFraction
    y1 += boundaryFraction
    y2 -= boundaryFraction
    # Removing the boundary area from each part
    # This ensures more accuracy of the percentage of black and white in the rectangle or grid
    
    roi, height, width = returnRoi(rect, x1, x2, y1, y2)

    whitePixels = cv2.countNonZero(roi)
    # Count the number of non-zero pixels(ie. white pixels) in thresh.
    
    noOfPixels = height*width
    # Find the total number of pixels
    try:
        white = (whitePixels/noOfPixels) * 100  # Represents percentage of white pixels
                             
    except:
        white = 50                              # In exceptional cases if the number of pixels is 0, then white is assumed to be 50.
    
    black = 100 - white                         # Represents percentage of black pixels
    black = float("%0.2f" % black)              # Format the percentages to two decimal places
    white = float("%0.2f" % white)

    return black, white
    # Return the number of percentage of black and white.

 ## Function Name: returnRoi
 
 ## Input: Rectangle,
 ##        Fractions of x and y relative to width and height respectively,
 ##        boolean returnRect (to return either region of image or coordinates of rectangle)

 ##        x1 = Distance of Left of required region from Left of image relative to the width.
 ##        Similarly x2 for right, y1 for top, y2 for bottom
 
 ## Output: Either region of image or coordinates of the rectangle

 ## Logic: Translates from the frame of the rectangle to the image 

 ## Example call: roi = returnRoi(rect, 3/5, 4/5, 1/6, 4/6)
 ##               partOfRect = returnRoi(rect, 3/5, 4/5, 1/6, 4/6, returnRect = True)
     
def returnRoi(rect, x1, x2, y1, y2, returnRect = False):
    x, y, w, h = rect
    x1 = x + int(x1 * w) # Since x1 represents fraction of distance from left end to the width,
                         # we multiply width and translate it by x (Left corner of the image)
    x2 = x + int(x2 * w) # Proceeding similarly for x2, y1 and y2
    y1 = y + int(y1 * h)
    y2 = y + int(y2 * h)
    
    if(returnRect): # If the coordinates are required then return the calculated coordinates
        return [x1, y1, x2 - x1, y2 - y1]
   
    # Else return the Region Of Image, Width and Height
    # x2 - x1 = Width, y2 - y1 = Height
    return thresh[y1 : y2, x1: x2], x2 - x1, y2 - y1

 ## Function Name: removeBlackPadding
 ## Input: Rectangle
 ## Output: Rectangle with its black padding layer (1/7 of initial rectangle at each side) removed
 ##Logic: Calls returnRoi to remove 1/7 part of each side
 ## Example call: paddingRemoved = removeBlackPadding(rect)
    
def removeBlackPadding(rect):
    aruco = returnRoi(rect, 1/7, 6/7, 1/7, 6/7, returnRect = True)
    # Return the part with 5/7 x 5/7 of initial dimensions of each part.
    return aruco

 ## Function Name: binaryToDecimal
 ## Input: A list with binary digits of a binary number eg. [1, 0, 1, 1]
 ## Output: Decimal value of corresponding binary number
 ## Logic: Multiplying by 2 ** n from leftmost digit and decrementing n,
 ##        where n is length of list (By General Procedure)
 ## Example call: decimal = binaryToDecimal([1, 0, 1, 1])
    
def binaryToDecimal(binary):
    n = len(binary) - 1
    decimal = 0
    for bit in binary:
        decimal += bit * (2 ** n)
        n -= 1
    return decimal

 ## Function Name: bitwise_not
 ## Input: A list with binary digits of a binary number eg. [1, 1, 0, 1, 0]
 ## Output: A list with binary digits of a binary number, with performing bitwise not on each digit eg. [0, 0, 1, 0, 1]
 ## Logic: Change bits from 1 to 0 and vice-versa.
 ## Example call: bit_not =  bitwise_not([1, 1, 0, 1, 0])
    
def bitwise_not(bits):
    bits_not = []
    for bit in bits:
        bits_not.append(0 if (bit == 1) else 1) # If a bit is 1 then we add 0 and vice versa.
    return bits_not

 ## Function Name: xnor
 ## Input: Two lists of equal length with binary digits
 ## Output: List of xnor of each binary digit
 ## Logic: If both digits at an index are equal, then 1 is placed at the index, else 0
 ## Example call: xnor = xnor([1, 1, 0, 1, 0], [0, 1, 1, 0, 0])
    
def xnor(bits1, bits2):
    bits = []
    for bit1, bit2 in list(zip(bits1, bits2)):   # Iterate through each bit in same index of the two lists
        bits.append(1 if (bit1 == bit2) else 0)  # We add 1 if if both bits are same else 0
    return bits

img = cv2.imread("../Images/Input/arucos-1.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(gray, 150, 210, cv2.THRESH_BINARY)
thresh_inv = 255*(thresh < 128).astype(np.uint8) #If a pixel value in thresh is less than 128 it is converted to black, else to whtie pixel in thresh_inv
#cv2.imwrite("../Images/Output/Detected/arucos-4 thresh_inv.png", thresh_inv)        
rects = getRectangles() # Get rectangles bounded by the contours
printIds(rects) # Print the detected IDs in the image
cv2.imwrite("../Images/Output/Detected/arucos-1 detected.png", img) # Save the output image in Output folder

 
        