# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time
import logging

import numpy as np
import tensorflow as tf

class CNNClassifier:
    def __init__(self, model_file, label_file, input_layer="input", output_layer="final_output", input_height=128, input_width=128, input_mean=127.5, input_std=127.5):
        self._graph = self.load_graph(model_file)
        self._labels = self.load_labels(label_file)
        input_name = "import/" + input_layer
        output_name = "import/" + output_layer
        self._input_operation = self._graph.get_operation_by_name(input_name);
        self._output_operation = self._graph.get_operation_by_name(output_name);
        self._session = tf.Session(graph=self._graph)
        self._graph_norm = tf.Graph()
	with self._graph_norm.as_default():
            image_mat = tf.placeholder(tf.float32, None, name="image_rgb_in")
            float_caster = tf.cast(image_mat, tf.float32)
            dims_expander = tf.expand_dims(float_caster, 0);
            resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
            normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std], name="image_norm_out")
            self._input_operation_norm =  self._graph_norm.get_operation_by_name("image_rgb_in")
            self._output_operation_norm = self._graph_norm.get_operation_by_name("image_norm_out")
	self._sess_norm = tf.Session(graph=self._graph_norm)

    def close(self):
        self._session.close()
	self._sess_norm.close()

    def load_graph(self, model_file):
        graph = tf.Graph()
        graph_def = tf.GraphDef()

        with open(model_file, "rb") as f:
            graph_def.ParseFromString(f.read())
        with graph.as_default():
            tf.import_graph_def(graph_def)

        return graph

    def read_tensor_from_image_file(self, file_name, input_height=299, input_width=299, input_mean=0, input_std=255):
        input_name = "file_reader"
        output_name = "normalized"

        file_reader = tf.read_file(file_name, input_name)

        if file_name.endswith(".png"):
            image_reader = tf.image.decode_png(file_reader, channels = 3,
                                       name='png_reader')
        elif file_name.endswith(".gif"):
            image_reader = tf.squeeze(tf.image.decode_gif(file_reader,
                                                  name='gif_reader'))
        elif file_name.endswith(".bmp"):
            image_reader = tf.image.decode_bmp(file_reader, name='bmp_reader')
        else:
            image_reader = tf.image.decode_jpeg(file_reader, channels = 3,
                                        name='jpeg_reader')

        float_caster = tf.cast(image_reader, tf.float32)
        dims_expander = tf.expand_dims(float_caster, 0);
        resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
        normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
        sess = tf.Session()

        result = sess.run(normalized)
        sess.close()

        return result

    def read_tensor_from_image_mat(self, image_mat, input_height=299, input_width=299, input_mean=0, input_std=255):
        result = self._sess_norm.run(self._output_operation_norm.outputs[0], {self._input_operation_norm.outputs[0]: image_mat})
        return result

    def load_labels(self, label_file):
        label = []
        proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
        for l in proto_as_ascii_lines:
            label.append(l.rstrip())
        return label

    def classify_image(self,
                       image_file_or_mat,
                       input_height=128,
                       input_width=128,
                       input_mean=0,
                       input_std=255):
        s_t = time.time()
	t = None
	if type(image_file_or_mat) == str:
        	t = self.read_tensor_from_image_file(file_name=image_file_or_mat,
                	              input_height=input_height,
                                      input_width=input_width,
                                      input_mean=input_mean,
                                      input_std=input_std)
	else:
 		t = self.read_tensor_from_image_mat(image_file_or_mat,
                                      input_height=input_height,
                                      input_width=input_width,
                                      input_mean=input_mean,
                                      input_std=input_std)

        logging.info( "time.norm: " + str(time.time() - s_t))
        s_t = time.time()

        results = self._session.run(self._output_operation.outputs[0],
                                        {self._input_operation.outputs[0]: t})

        logging.info( "time.cls: " + str(time.time() - s_t))

        results = np.squeeze(results)

        pairs = {}
        for i in results.argsort():
            pairs[self._labels[i]] = results[i]

        return pairs
