from PIL import Image
import numpy as np
import cv2




#Functions
def PreventiveScaling(image,scaling_factor):
    height = int((len(np.array(image))-1)/scaling_factor) * scaling_factor
    width = int((len(np.array(image)[0])-1)/scaling_factor) * scaling_factor
    resized_image = cv2.resize(np.array(image),(width,height))
    return resized_image

def DownScaleImage(image,scaling_factor):
    
    new_width = int(len(image[0]) / scaling_factor)
    new_height = int(len(image) / scaling_factor)

    new_image_size = cv2.resize(image,(new_width,new_height))

    return new_image_size


def RemoveColors(downscaled_image):
    gray_image = cv2.cvtColor(downscaled_image, cv2.COLOR_BGR2GRAY)
    return np.array(gray_image)

def ExtendedDifferenceOfGausians(gray_image):
    sigma1 = 1.4
    sigma2 = 16
    kernel = (7,7)

    t = 0.84

    DifferenceOfGausians = cv2.GaussianBlur(gray_image,kernel,sigma1) - cv2.GaussianBlur(gray_image,kernel,sigma2)  * t 
    
    for y,line in enumerate(DifferenceOfGausians):
        for x,pixel in enumerate(line):
            if pixel > 15:
                DifferenceOfGausians[y][x] = 255
            else:
                DifferenceOfGausians[y][x] = 0

  
    return DifferenceOfGausians
    

def SobelEdge(gausian_blur_image):
    sobel_x = cv2.Sobel(gausian_blur_image, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gausian_blur_image, cv2.CV_64F, 0, 1, ksize=3)
    vectors = np.abs(np.divide(np.arctan2(np.array(sobel_y),np.array(sobel_x)),np.pi))

    return vectors;
        
def ScaleDownProperly(vectors,treshold,scaling_factor):
    
    windows_y = int((len(vectors)-1)/scaling_factor)
    windows_x = int((len(vectors[0])-1)/scaling_factor)
    
    scaled_down_vectors = []

    #window sliding scaling_factor*scaling_factor
    for y in range(0,windows_y):
        pixel_row = []
        for x in range(0,windows_x):
            block = []
            for y_range in range(y*scaling_factor - scaling_factor,scaling_factor*y):
                for x_range in range(x*scaling_factor -scaling_factor,x*scaling_factor):
                        block.append(vectors[y_range][x_range])
    
            shapes =[0,0,0,0,0]
            for pixel in block:
                if pixel > 0 and pixel <= 0.20:   
                    shapes[0]+=1
                elif pixel > 0.20 and pixel <= 0.40:
                    shapes[1]+=1
                elif pixel > 0.40 and pixel <= 0.60:
                    shapes[2]+=1
                elif pixel > 0.60 and pixel <= 0.80:
                    shapes[3]+=1
                elif pixel > 0.80 and pixel <= 1:
                    shapes[4]+=1
            
            max_num = max(shapes)
            if max_num > treshold:
                index = shapes.index(max_num)
                if index == 0:
                    pixel_row.append(0.20)
                elif index == 1:
                    pixel_row.append(0.40)
                elif index == 2:
                    pixel_row.append(0.60)
                elif index == 3:
                    pixel_row.append(0.80)
                elif index == 4:
                    pixel_row.append(1)
            else:
                pixel_row.append(0)

        scaled_down_vectors.append(pixel_row)
    return scaled_down_vectors

def BuildAscii(gray_image,edge_vectors):
    asciiTable = {0:' ',10:' ',20:'.',30:';',40:'c',50:'o',60:'P',70:'O',80:'?',90:'@',100:'■'}

    np_gray_image = np.array(gray_image)
    constant = 100/np.max(np_gray_image)
    image_arr = np.ceil(np_gray_image*constant/10)*10

    converted_arr = []
    for line in image_arr:
        lineAscii = []
        for val in line:
            lineAscii.append(asciiTable[val])
        converted_arr.append(lineAscii)

    edge_table = {0.20:'|',0.40:'/',0.60:'-',0.80:'\\',1:'|'}
    
    for y,line in enumerate(edge_vectors):
        for x,pixel in enumerate(line):
            if pixel != 0:
                converted_arr[y][x] = edge_table[pixel]


    return np.array(converted_arr)


def PrintAsciiArt(ascii_image):
    for line in ascii_image:
        for char in line:
            print(char,end='')
        print('\n')


def WriteFile(ascii_image):
    with open('D:/MyPrograms/AsciiConverter/ascii.txt','w',encoding="utf-8") as ascii_file:
        for line in ascii_image:
            for char in line:
                ascii_file.write(char)
            ascii_file.write('\n')
        ascii_file.close()
        




#MAIN

font_size = 8

while True:
    try:

        imagePath = input("imagePath />")
        image = Image.open(imagePath)
        preventive_resize = PreventiveScaling(image,font_size)
        gray_image = RemoveColors(preventive_resize)
        gausian = ExtendedDifferenceOfGausians(gray_image)
        vectors = SobelEdge(gausian)
        DownScaleImage = DownScaleImage(gray_image, font_size)
        scaled_down_vectors = ScaleDownProperly(vectors,treshold=5,scaling_factor=font_size)
        build_ascii = BuildAscii(DownScaleImage,scaled_down_vectors)
        WriteFile(build_ascii)

        print("Image converted")
   
    except:
        print("invalid image path")
    

