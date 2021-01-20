from django.shortcuts import render
from django.http import HttpResponse

from django.http import JsonResponse
from .models import Greeting
import tensorflow as tf 
import sys   
from django.views.decorators.csrf import csrf_exempt
import zipfile
import urllib.request 
import requests
import os
# from tusclient import client
    
# Create your views here.
@csrf_exempt
def index(request):
    # return HttpResponse('Hello from Python!')
    return render(request, "index.html")
 
 
@csrf_exempt
def tfconverter(request):
    url= request.POST.get('url','')  
    name= request.POST.get('name','')  
    result = False 
    if url!='':
        
        resp = requests.get(url, allow_redirects=True)
        path= "hello/static/tmp/"
        return_name=""
        label_name=""
        with open(path+name, 'wb') as f:
            f.write(resp.content)  
        
        sub_file_names = extract_zip(path,name) 
        for file_n in sub_file_names:
            print(file_n)
            file_name = file_n.split("/")
            if len(file_name)==2 and file_name[0] == "saved_model" :
                result = converter(name,name,"saved_model")   
            if file_n.split(".")[-1]=="txt":
                result = saveToFolder(file_n,name) 
            if len(file_name)==1 and file_n.split(".")[-1]=="h5":
                print("45")
                result = converter(file_n,name,"h5") 
        
        result = True
    response = {
         "res": result, 
    }
    return JsonResponse(response)
 

def extract_zip(path,name):    
           
    zip = zipfile.ZipFile(path+name)
    zip.extractall(path=path)
    sub_file_names = zip.namelist()
    # os.remove(path+name)
    zip.close()
    print("67")
    return sub_file_names
  
    ## adını al falan 
def saveToFolder(read_name,name):   
    print(name)
    path2read= "hello/static/tmp/"+read_name
    path2write = "hello/static/converted_models/"+name.split(".")[0]+"/label.txt"
    
     
    if not os.path.exists("hello/static/converted_models/"+name.split(".")[0]):
        os.mkdir("hello/static/converted_models/"+name.split(".")[0])

    file = open(path2read,"r") 
    with open(path2write,'wb') as f:
        f.write(file.read().encode()) 
    return True

def converter(model_name,name,model_type):
    
    if model_type == "h5": 
        model = tf.keras.models.load_model("hello/static/tmp/"+model_name)
        tf.saved_model.save(model, 'hello/static/tmp/saved_model')

    model = tf.saved_model.load("hello/static/tmp/saved_model")
    
    model.signatures[tf.saved_model.DEFAULT_SERVING_SIGNATURE_DEF_KEY].inputs[0].set_shape([1, 300, 300, 3])
    # adjusting layers
    tf.saved_model.save(model, "hello/static/saved_model_updated", signatures=model.signatures[tf.saved_model.DEFAULT_SERVING_SIGNATURE_DEF_KEY])
    # Convert
    converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_dir='hello/static/saved_model_updated', signature_keys=['serving_default'])
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS, tf.lite.OpsSet.SELECT_TF_OPS]
    tflite_model = converter.convert()
     
    if not os.path.exists("hello/static/converted_models/"+name.split(".")[0]):
        os.mkdir("hello/static/converted_models/"+name.split(".")[0])
    # Save the model.
    f_name= "hello/static/converted_models/"+name.split(".")[0]+"/model.tflite"
   
    with open(f_name, 'wb') as f:
        f.write(tflite_model) 
    return True


def db(request):

    greeting = Greeting()
    greeting.save()

    # greetings = Greeting.objects.all()

    # return render(request, "db.html", {"greetings": greetings})
