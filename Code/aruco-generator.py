"""
Author: Eswara prasad
Domain: Signal Processing and ML
Sub-domain: Image processing
Functions:convertIdToBits, decimalToBinary, setRoi, bitColor           
Global variables: img, width, height  

"""

import cv2
import numpy as np

 ## Function name: convertIdToBits
 ## Input: Valid ID of ArUco Marker
 ## Output: parity2, data1, parity3, data2, and parity1 bits represented by a list
 ## Logic: First we convert ID to binary.
 ##        Then, we calculate the databits by arranging binary digits in alternating fashion.
 ##        Then, we calculate the parity bits by modified hamming code:
 ##        1) The parity 2 bits are bitwise not of data 1 bits.
 ##        2) The parity 3 bits are the same as data 2 bits.
 ##        3) The parity 1 bit in each row is XOR of parity 2 and parity 3 bits in that row
 ## Example call: bits = convertIdToBits(id)
              
def convertIdToBits(id):
    binary = decimalToBinary(id)
    i = 0
    data1 = binary[0::2]
    data2 = binary[1::2]
    parity1 = []
    parity2 = []
    parity3 = data2
    for d in data1:
        parity2.append(0 if (d==1) else 1)
    for i in range(5):
        parity1.append(0 if(data1[i] == data2[i]) else 1)
    return parity2, data1, parity3, data2, parity1

 ## Function name: decimalToBinary
 ## Input: Decimal number
 ## Output: Binary digits of the decimal number represented by a list
 ## Logic: Append the remainder obtained by dividing decimal number by 2 from left to right till the decimal number is 0.
 ##        Then make it to 10 digits by adding required digits of 0 in the front.
 ##        Finally, reverse the list.
 ## Example call: bunary = decimalToBinary(decimal)
 
def decimalToBinary(decimal):
    binary = []
    if(decimal == 0):
        binary.append(0)
    while(decimal > 0):
        binary.append(decimal % 2)  # Append the remainder obtained by dividing decimal number by 2 from left to right                              
        decimal = decimal//2        # till the decimal number is 0
    while (len(binary) < 10):
        binary.append(0)            # Make it to 10 digits by adding required digits of 0 in the front
    binary.reverse()                # Finally, reverse the list
    return binary

 ## Function name: setRoi
 ## Input: Fractions of distances relative to height and width relative to image and Bit representing 1 or 0.
 ## Output: Prints white or black color in a given grid or cell
 ## Logic: Calculates coordinates of the cell relative to the image and sets the color of the cell to white or black.
 ## Example call: setRoi(2/5. 3/5, 1/5, 2/5, bit = 1)
 
def setRoi(x1, x2, y1, y2, bit):
    x1 = int(x1 * width)
    x2 = int(x2 * width)
    y1 = int(y1 * height)
    y2 = int(y2 * height)
   
    aruco[y1 : y2, x1: x2] = bitColor(bit)

 ## Function name: bitColor
 ## Input: Bit representing 1 or 0.
 ## Output: Returns white color tuple if bit is 1, else black.
 ## Example call: color = bitColor(bit = 0)
 
def bitColor(bit):
    return ((255, 255, 255) if (bit == 1) else (0, 0, 0))
    
width = 400
height = 400
aruco = np.zeros((height, width, 3), np.uint8)  # Creates a black image (numpy array of zeros).

print("Enter -1 to quit")

while(True):                      # Runs an infinit loop until either the ID entered is valid or -1 is pressed.
    inp = input("Enter ID : ")
    try:
        id = int(inp)
    
    except:                       # Try except block to avoid user entering input other than integer.
        print("Enter a valid number")
        continue
        
    if(id >= 0 and id < 1024):    # If the ID is valid, proceed to getting bits of the given ID.
        parity2, data1, parity3, data2, parity1 = convertIdToBits(id)
        bits = parity2 + data1 + parity3 + data2 + parity1  # Joins the parity and data bits in the required fashion. 
            
        for col in range(1, 6):  # Iterate through each 5x5 cells in center in 7x7 grid.
            for row in range(1, 6):
                bit = bits[5*(col-1) + (row-1)] # 5*(col-1) + (row-1) iterates through 0 to 24. Find the corresponding bit in bits list.
                setRoi(col/7, (col + 1)/7, row/7, (row + 1)/7, bit) # Set color of each of 5x5 cells in center represented by bit. 
                # We divide by 7 because setRoi accepts fractions. eg. x1 = 1/7, x2 = 2/7 represents the 2nd column in 7x7 grid.
       
        # Adding White padding to the ArUco marker
        img = cv2.copyMakeBorder(aruco, 30, 30, 30, 30 ,cv2.BORDER_CONSTANT,value = [255, 255, 255])
        
       # If the ID has to be displayed on the generated image (Optional), the following line can be included:
       # cv2.putText(img, "ID: "+ "%d" % id,(180, 20), cv2.FONT_HERSHEY_TRIPLEX, 0.7, (0, 0, 0), 1, cv2.LINE_AA)
        
        # Save the image in the output folder with the name aruco-<id>.png eg. aruco-650.png
        cv2.imwrite("../Images/Output/Generated/aruco-" + "%d" % id + ".png", img)
        print("Aruco marker ID "+ "%d" % id + " generated in output folder")
        break
    
    # -1 is pressed the while loop is terminated and hence the program.
    elif(id == -1):
        break
    
    # Else if the input is a inavlid decimal number for ArUco ID (-1 not inclusive), program prompts to enter a valid ID, till the input is valid OD.
    else:
        print("Enter a valid Aruco ID (0 to 1023)")
     
