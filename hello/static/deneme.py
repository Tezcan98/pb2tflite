import tensorflow as tf
import os 

 
converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_dir = "saved_model", input_shapes={"image_tensor" : [1,300,300,3]})
 
tflite_model = converter.convert()

## TFLite Interpreter to check input shape
interpreter = tf.lite.Interpreter(model_content=tflite_model)
interpreter.resize_tensor_input(0, [1, 300, 300, 3], strict=True)
interpreter.allocate_tensors()
# Get input and output tensors.
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()



if not os.path.exists("enes"):
    os.mkdir("enes")
# Save the model.
f_name= "enes/12345.tflite"
with open(f_name, 'wb') as f:
    f.write(tflite_model) 