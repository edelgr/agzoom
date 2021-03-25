import cv2
import numpy as np
import os
import clasificator
import trainer
import LBP
import SVM_classificator
import RF_clasificator

#mode=1 entrenar clasificador
#mode=2 clasificar imagen
#mode =3 testear clasificador en lote
#mode =4 testear clasificador por muestra

#clase 2 platano

mode=1
clasif='RF'
#clasif='SVM'
#clasif='MLP'


if (mode==1):
    imagedir='D:/Geo/clasificador/training1/'
    if (clasif=='SVM'):
        trainer.train_svm(imagedir,'D:/Geo/clasificador/crop_classifier/dependence/canna_svm.xml')
    if (clasif=='RF'):
        trainer.train_RF(imagedir,'D:/Geo/clasificador/crop_classifier/dependence/boniato_rf.xml')
    if (clasif=='MLP'):
        trainer.train_mlp(imagedir,'D:/Geo/clasificador/crop_classifier/dependence/canna_mlp.xml')



if (mode==2):
   fname='natural_color.jpg'
   #fname='img_prueba.jpg'
   imagedir= 'D:/Geo/clasificador/'

   if (clasif=='RF'):
      path_rf = 'D:\\Geo\\clasificador\\crop_classifier\\dependence\\canna_rf.xml'
   if (clasif=='SVM'):
       path_rf = 'D:\\Geo\\clasificador\\crop_classifier\\dependence\\canna_svm.xml'
   if (clasif=='MLP'):
       path_rf ='D:/Geo/clasificador/crop_classifier/dependence/platano_mlp.xml'
  
   fpath=os.path.join(imagedir, fname)
   imag=cv2.imread(fpath)
   temp=imag.copy()
  # cv2.namedWindow('Imagen', cv2.WINDOW_NORMAL)
  # cv2.imshow('Imagen', imag) 
   if (clasif=='RF'):
      clasificator.ClasificarRF(temp, path_rf)
   if (clasif=='SVM'):
       clasificator.ClasificarSVM(temp, path_rf)
   if (clasif=='SVM'):
       clasificator.ClasificarMLP(temp, path_rf)
  
   cv2.waitKey(0)


if (mode==3):
  
  # image_dir='D:/Geo/clasificador/training2/'
  # image_dir='D:/Geo/clasificador/20200917/Platano'
   #image_dir='D:/Geo/clasificador/20200917/Malanga'
   #image_dir= 'D:/Geo/clasificador/20200720/Maiz'
   #image_dir='D:/Geo/clasificador/20200720/Frijoles'
   #image_dir='D:/Geo/clasificador/20200720/Canna'
   #image_dir='D:/Geo/clasificador/20200720/Boniato'
   #image_dir='D:/Geo/clasificador/20200720/Arroz'
   
   #image_dir='D:/Geo/clasificador/20200720/Suelo' 
   #image_dir='D:/Geo/clasificador/20200917/Yuca' 
   #image_dir='D:/Geo/clasificador/20200720/Hierba' 
   #image_dir='D:/Geo/clasificador/20200720/Construcciones' 
   #image_dir='D:/Geo/clasificador/20200720/Bosque' 
   #image_dir='D:/Geo/clasificador/20200720/Agua' 
  
   
  
   count=0
 
   if (clasif=='RF'):
      path_rf = 'D:\\Geo\\clasificador\\crop_classifier\\dependence\\canna_rf.xml'
   if (clasif=='SVM'):
       path_rf = 'D:\\Geo\\clasificador\\crop_classifier\\dependence\\canna_svm.xml'
   if (clasif=='MLP'):
       path_rf ='D:/Geo/clasificador/crop_classifier/dependence/platano_mlp.xml'
   
   for fname in os.listdir(image_dir):
     
      #  if not fname.startswith ('image'): continue   #skipped not the target image file
        fpath=os.path.join(image_dir, fname)
        count=count+1
        img=cv2.imread(fpath)
       
        if (clasif=='RF'):
           response=clasificator.Test_RF(img, path_rf)
           print(str(count) + '-' + fname + ' clase: ' + str(response))
        
        if (clasif=='SVM'):
           response=clasificator.Test_SVM(img,path_rf)
           r1=response[1]
           r2=r1[0]
           r3=int(r2[0])
           print(str(count) + '-' + fname + ' clase: ' + str(r3))

        if (clasif=='MLP'):
           response=clasificator.Test_MLP(img, path_rf)
           print(str(count) + '-' + fname + ' clase: ' + str(response))


if (mode==4):
 
 image_dir='D:/Geo/clasificador/training1/1-1.tif'
 sample=cv2.imread(image_dir)
 if (clasif=='RF'):
      path_rf = 'D:\\Geo\\clasificador\\crop_classifier\\dependence\\platano.xml'
      clf=RF_clasificator.RTrees()
 if (clasif=='SVM'):
       path_rf = 'D:\\Geo\\clasificador\\crop_classifier\\dependence\\platano_svm.xml'
       clf = SVM_classificator.SVM()
 
 clf.load(path_rf)
 sample=LBP.LBPfeature(sample)
 
 TestSample=sample.astype(np.float32)
 TestSample=TestSample.reshape(1,-1)
 response=clf.predict(TestSample)
 print (response)
   