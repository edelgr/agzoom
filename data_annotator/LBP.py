import cv2
import numpy as np




def get_pixel(img, center, x, y): 
      
    new_value = 0
      
    try: 
        # If local neighbourhood pixel  
        # value is greater than or equal 
        # to center pixel values then  
        # set it to 1 
        if img[x][y] >= center: 
            new_value = 1
              
    except: 
        # Exception is required when  
        # neighbourhood value of a center 
        # pixel value is null i.e. values 
        # present at boundaries. 
        pass
      
    return new_value 



# Function for calculating LBP 
def lbp_calculated_pixel(img, x, y): 
   
    center = img[x][y] 
   
    val_ar = [] 
      
    # top_left 
    val_ar.append(get_pixel(img, center, x-1, y-1)) 
      
    # top 
    val_ar.append(get_pixel(img, center, x-1, y)) 
      
    # top_right 
    val_ar.append(get_pixel(img, center, x-1, y + 1)) 
      
    # right 
    val_ar.append(get_pixel(img, center, x, y + 1)) 
      
    # bottom_right 
    val_ar.append(get_pixel(img, center, x + 1, y + 1)) 
      
    # bottom 
    val_ar.append(get_pixel(img, center, x + 1, y)) 
      
    # bottom_left 
    val_ar.append(get_pixel(img, center, x + 1, y-1)) 
      
    # left 
    val_ar.append(get_pixel(img, center, x, y-1)) 
       
    # Now, we need to convert binary 
    # values to decimal 
    power_val = [1, 2, 4, 8, 16, 32, 64, 128] 
   
    val = 0
      
    for i in range(len(val_ar)): 
        val += val_ar[i] * power_val[i] 
          
    return val 



def LBPfeature(img_bgr):
 
    height, width, _ = img_bgr.shape 
   
    # We need to convert RGB image  
    # into gray one because gray  
    # image has one channel only. 
    img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY) 
   
   # moments= cv2.moments(img_gray) #momentos ortogonales de la imagen
   # momentos=list(moments.values())
   # min=np.amin(img_gray) #minimo
   # max=np.amax(img_gray) #maximo
   # mean,std=cv2.meanStdDev(img_gray) #media y desviacion estandar

    # Create a numpy array as  
    # the same height and width  
    # of RGB image 

    #granulometric analisys 
    img_lbp = np.zeros((height, width, 7), np.uint8) 
    kernel=np.ones((10,10),np.uint8)
    
    #3 granulometric maps base on morphologycal opening
    gr_mp_op1=cv2.morphologyEx(img_bgr,cv2.MORPH_OPEN,kernel)
    gr_mp_op2=cv2.morphologyEx(gr_mp_op1,cv2.MORPH_OPEN,kernel)
    gr_mp_op3=cv2.morphologyEx(gr_mp_op2,cv2.MORPH_OPEN,kernel)
    
    #3 granulometric maps base on morphologycal closing
    gr_mp_cl1=cv2.morphologyEx(img_bgr,cv2.MORPH_CLOSE,kernel)
    gr_mp_cl2=cv2.morphologyEx(gr_mp_cl1,cv2.MORPH_CLOSE,kernel)
    gr_mp_cl3=cv2.morphologyEx(gr_mp_cl2,cv2.MORPH_CLOSE,kernel)


    for i in range(0, height): 
         for j in range(0, width): 
              img_lbp[i, j,0] = lbp_calculated_pixel(img_gray, i, j) 
              img_lbp[i,j,1]= gr_mp_op1[i,j,0]
              img_lbp[i,j,2]= gr_mp_op2[i,j,0]
              img_lbp[i,j,3]= gr_mp_op3[i,j,0]
              img_lbp[i,j,4]= gr_mp_cl1[i,j,0]
              img_lbp[i,j,5]= gr_mp_cl2[i,j,0]
              img_lbp[i,j,6]= gr_mp_cl3[i,j,0]

    img_lbp=img_lbp.ravel()
   
    features=img_lbp.tolist()
   # features.append(min)
   # features.append(max)
   # features.append(mean)
   # features.append(std)
    #for k in range(0,len(momentos)):
       # features.append(momentos[k])
    samples=np.array(features)
    
    return samples



