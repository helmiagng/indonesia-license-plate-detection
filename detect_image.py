from distutils.command import clean
import os
import re
import time
# comment out below line to enable tensorflow outputs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
import tensorflow as tf
physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)
from tensorflow.python.saved_model  import tag_constants
from PIL import Image
import cv2
import numpy as np
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession
import random
import colorsys
import pytesseract

#for extracting license plate number i user pytesseract
#first enter path of tesseract exe 
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def filter_boxes(box_xywh, scores, score_threshold=0.4, input_shape = tf.constant([416,416])):
    scores_max = tf.math.reduce_max(scores, axis=-1)

    mask = scores_max >= score_threshold
    class_boxes = tf.boolean_mask(box_xywh, mask)
    pred_conf = tf.boolean_mask(scores, mask)
    class_boxes = tf.reshape(class_boxes, [tf.shape(scores)[0], -1, tf.shape(class_boxes)[-1]])
    pred_conf = tf.reshape(pred_conf, [tf.shape(scores)[0], -1, tf.shape(pred_conf)[-1]])

    box_xy, box_wh = tf.split(class_boxes, (2, 2), axis=-1)

    input_shape = tf.cast(input_shape, dtype=tf.float32)

    box_yx = box_xy[..., ::-1]
    box_hw = box_wh[..., ::-1]

    box_mins = (box_yx - (box_hw / 2.)) / input_shape
    box_maxes = (box_yx + (box_hw / 2.)) / input_shape
    boxes = tf.concat([
        box_mins[..., 0:1],  # y_min
        box_mins[..., 1:2],  # x_min
        box_maxes[..., 0:1],  # y_max
        box_maxes[..., 1:2]  # x_max
    ], axis=-1)
    # return tf.concat([boxes, pred_conf], axis=-1)
    return (boxes, pred_conf)


def format_boxes(bboxes, image_height, image_width):
    for box in bboxes:
        ymin = int(box[0] * image_height)
        xmin = int(box[1] * image_width)
        ymax = int(box[2] * image_height)
        xmax = int(box[3] * image_width)
        box[0], box[1], box[2], box[3] = xmin, ymin, xmax, ymax
    return bboxes

def run_tflite(weights,input_size,image_file,images_data):
    
    interpreter = tf.lite.Interpreter(model_path=weights)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    interpreter.set_tensor(input_details[0]['index'], images_data)
    interpreter.invoke()
    pred = [interpreter.get_tensor(output_details[i]['index']) for i in range(len(output_details))]
    boxes, pred_conf = filter_boxes(pred[0], pred[1], score_threshold=0.25, input_shape=tf.constant([input_size, input_size]))
    # run non max suppression on detections
    boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
        boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
        scores=tf.reshape(
            pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
        max_output_size_per_class=9,
        max_total_size=9,
        iou_threshold=0.45,
        score_threshold=0.25
    )

    original_h, original_w, _ = image_file.shape
    bboxes = format_boxes(boxes.numpy()[0], original_h, original_w)
            
    # hold all detection data in one variable
    pred_bbox = [bboxes, scores.numpy()[0]*100, classes.numpy()[0], valid_detections.numpy()[0]]

    return pred_bbox

def get_classes(class_file_name):
    names = []
    with open(class_file_name, 'r') as data:
        lines=data.readlines()
        for line in lines:
            names.append(line)
    return names

def draw_bbox_and_ocr(image, bboxes, allowed_classes,plate_text,show_label=True):
    classes = allowed_classes
    num_classes = len(classes)
    image_h, image_w, _ = image.shape
    hsv_tuples = [(1.0 * x / num_classes, 1., 1.) for x in range(num_classes)]
    colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
    colors = list(map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)), colors))

    random.seed(0)
    random.shuffle(colors)
    random.seed(None)

    out_boxes, out_scores, out_classes, num_boxes = bboxes
    for i in range(num_boxes):
        if int(out_classes[i]) < 0 or int(out_classes[i]) > num_classes: continue
        coor = out_boxes[i]
        fontScale = 0.6
        score = out_scores[i]
        class_name = classes[i]
        if class_name not in allowed_classes:
            continue
        else:
            bbox_color = colors[i]
            bbox_thick = int(0.6 * (image_h + image_w) / 600)
            c1, c2 = (coor[0], coor[1]), (coor[2], coor[3])
            cv2.rectangle(image, c1, c2, bbox_color, bbox_thick)
            if show_label:
                bbox_mess = '%s: %.2f' % (class_name, score) + '%'
                t_size = cv2.getTextSize(bbox_mess, 0, fontScale, thickness=bbox_thick // 2)[0]
                c3 = (c1[0] + t_size[0], c1[1] - t_size[1] - 3)
                cv2.rectangle(image, c1, (np.float32(c3[0]), np.float32(c3[1])), bbox_color, -1) #filled

                cv2.putText(image, bbox_mess, (c1[0], np.float32(c1[1] - 2)), cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale, (0, 0, 0), bbox_thick // 2, lineType=cv2.LINE_AA)
                text_pos=(c1[0], np.float32(c1[1] - 30))
                font_text_size=0.9
                font_thickness=int(0.8*(image_h+image_w)/300)
                cv2.putText(image,plate_text,text_pos,cv2.FONT_HERSHEY_SIMPLEX,
                                font_text_size,colors[i],font_thickness,lineType=cv2.LINE_AA)

    return image


def read_license_plate(coord,image,n_count):
    
    
    
    for i in range(len(coord)) :
        xmin, ymin, xmax, ymax = coord[i]
        #only read coordinat that contain character
        if xmin==0 and ymin==0 and xmax==0 and ymax==0:
            continue
        extend_coord=2
        #image preprocessing before doing ocr
        seg_image = image[int(ymin):int(ymax), int(xmin)+extend_coord:int(xmax)+extend_coord]
        gray=cv2.cvtColor(seg_image,cv2.COLOR_BGR2GRAY)
        zoom_rate=4
        gray=cv2.resize(gray,None,fx=zoom_rate,fy=zoom_rate,interpolation=cv2.INTER_CUBIC)
        gray=cv2.GaussianBlur(gray,(1,1),0)
        thresh=cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
        rect_kern = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
        # apply dilation to make regions more clear
        dilation = cv2.dilate(thresh, rect_kern, iterations = 1)
        roi=cv2.bitwise_not(thresh)
        try:
            text = pytesseract.image_to_string(roi, config='-c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ --psm 7 --oem 3')
            # clean tesseract text by removing any unwanted blank spaces
            clean_text = re.sub('[\W_]+', '', text)
            print("license plate:",clean_text)
            
        except:
            continue

    return clean_text


def main():
    start = time.time()
    #input size for license plate detection
    plate_input_size = 416
    #Enter path of image 
    image_path = input("Enter image path input:")
    plate_weights_path='input("Enter weights path input:")
    
    original_image = cv2.imread(image_path)
    original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

    image_data = cv2.resize(original_image, (plate_input_size, plate_input_size))
    image_data = image_data / 255.

    images_data = []
    for i in range(1):
        images_data.append(image_data)
    images_data = np.asarray(images_data).astype(np.float32)
    #running detection plate
    pred_bbox=run_tflite(plate_weights_path,plate_input_size,original_image,images_data)

    #allowed_classes = class_names
    #enter path of classes .txt file 
    classes_path=input("Enter classes path:")
    allowed_classes = get_classes(classes_path)
    #image = draw_bbox(original_image, pred_bbox, allowed_classes=allowed_classes)
    detect_plat_nomor_time=time.time()
    print("The time of execution of plate detection is :",
    (detect_plat_nomor_time-start) * 10**3, "ms")
    boxes,scores,classes,valid_detection = pred_bbox
    sorted_boxes=sorted(boxes,key=lambda x:x[0])
 
    plate_text=read_license_plate(sorted_boxes,original_image,valid_detection)
    image=draw_bbox_and_ocr(original_image,pred_bbox,allowed_classes,plate_text)
    display_image=Image.fromarray(image)
    display_image.show()
    end=time.time()
    print("OCR computing time:",(end-start)*10**3,'ms')
    
        
if __name__ == '__main__':
    main()
