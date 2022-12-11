import tensorflow as tf
from absl import app,flags,logging
from absl.flags import FLAGS

flags.DEFINE_string('weights','./checkpoints/mobilenet_ssd_char_seg','path to weights file')
flags.DEFINE_string('output','./checkpoints/mobilenet_ssd_char_seg.tflite','path to output')
flags.DEFINE_integer('input_size',416,'path to output')
flags.DEFINE_string('quantize_mode','float32','quantize mode (int8, float16, float32)')
flags.DEFINE_string('dataset', "/Volumes/Elements/data/coco_dataset/coco/5k.txt", 'path to dataset')


def representative_data_gen():
  fimage = open(FLAGS.dataset).read().split()
  for input_value in range(10):
    if os.path.exists(fimage[input_value]):
      original_image=cv2.imread(fimage[input_value])
      original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
      image_data = utils.image_preprocess(np.copy(original_image), [FLAGS.input_size, FLAGS.input_size])
      img_in = image_data[np.newaxis, ...].astype(np.float32)
      print("calibration image {}".format(fimage[input_value]))
      yield [img_in]
    else:
      continue

def save_tflite():
    converter=tf.lite.TFLiteConverter.from_saved_model(flags.weights)
    
    if FLAGS.quantize_mode=='float16':
        #set converter opitmization with default mode
        converter.optimizations=[tf.lite.Optimize.DEFAULT]
        #set supported dtype
        converter.target_spec.supported_types=[tf.compat.v1.lite.constants.FLOAT16]
        #generate tflite
        converter.target_spec.supported_ops=[tf.lite.OpsSet.TFLITE_BUILTINS,tf.lite.OpsSet.SELECT_TF_OPS]
        #allowing custom ops
        converter.allow_custom_ops=True
    elif FLAGS.quantize_mode=='int8': 
        #supported ops to int8 mode
        converter.target_spec.supported_ops=[tf.lite.OpsSet.TFLITE_BUILTINS_INT8,tf.lite.OpsSet.SELECT_TF_OPS]
        converter.optimizations=[tf.lite.Optimize.DEFAULT]
        converter.target_spec.supported_ops=[tf.lite.OpsSet.TFLITE_BUILTINS,tf.lite.OpsSet.SELECT_TF_OPS]
        converter.allow_custom_ops=True
        converter.representative_dataset=representative_data_gen

    tflite_model=converter.convert()
    open(FLAGS.output,'wb').write(tflite_model)

    logging.info('model saved to : {}'.format(FLAGS.output))


def main():
    save_tflite()


if __name__=='__main__':
    try:
        app.run(main)
    except SystemExit:
        pass