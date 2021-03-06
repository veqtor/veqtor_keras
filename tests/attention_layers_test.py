import numpy as np
import tensorflow as tf
from tensorflow.keras.utils import custom_object_scope
from tensorflow.python.framework import test_util

from veqtor_keras.layers.attention_layers import LocalizedAttentionLayer1D, LocalizedAttentionLayer2D

def _test_grads(testCase: tf.test.TestCase, func, input):
    _, grads = tf.test.compute_gradient(func, input)
    for grad in grads:
        testCase.assertNotAllClose(grad, np.zeros_like(grad))


to_tensor = tf.convert_to_tensor
normal = np.random.normal


class LocalizedAttentionLayer1DTest(tf.test.TestCase):
    @test_util.use_deterministic_cudnn
    def test_simple(self):
        with custom_object_scope({'LocalizedAttentionLayer1D': LocalizedAttentionLayer1D}):
            t_steps = 12
            bs = 2
            dim = 16
            v_dim = dim * 2
            s = 2

            layer = LocalizedAttentionLayer1D(patch_size=3,
                                              stride=s,
                                              num_heads=4,
                                              dilation=2)

            q = to_tensor(normal(size=(bs, t_steps // s, dim))
                          .astype(np.float32))
            k = to_tensor(normal(size=(bs, t_steps, dim))
                          .astype(np.float32))
            v = to_tensor(normal(size=(bs, t_steps, v_dim))
                          .astype(np.float32))

            @tf.function
            def test_func(q, k, v):
                return layer(q, k, v)

            r = test_func(q, k=k, v=v)

            ex_res_shape = np.zeros((bs, t_steps // s, v_dim))

            self.assertShapeEqual(ex_res_shape, r)

            _test_grads(self, test_func, [q, k, v])


class LocalizedAttentionLayer2DTest(tf.test.TestCase):
    @test_util.use_deterministic_cudnn
    def test_simple(self):
        with custom_object_scope({'LocalizedAttentionLayer2D': LocalizedAttentionLayer2D}):
            in_shape = [4, 4]
            bs = 1
            dim = 4
            v_dim = dim * 2
            s = 2

            layer = LocalizedAttentionLayer2D(patch_size=(3, 3),
                                              strides=(s, s),
                                              num_heads=2,
                                              dilations=(1, 1))

            q = to_tensor(normal(size=(bs, in_shape[0] // s, in_shape[1] // s, dim))
                          .astype(np.float32))
            k = to_tensor(normal(size=(bs, in_shape[0], in_shape[1], dim))
                          .astype(np.float32))
            v = to_tensor(normal(size=(bs, in_shape[0], in_shape[1], v_dim))
                          .astype(np.float32))

            @tf.function
            def test_func(_q, _k, _v):
                return layer(_q, _k, _v)

            r = test_func(q, _k=k, _v=v)

            ex_res_shape = np.zeros((bs, in_shape[0] // s, in_shape[1] // s, v_dim))

            self.assertShapeEqual(ex_res_shape, r)

            _test_grads(self, test_func, [q, k, v])


if __name__ == '__main__':
    tf.test.main()
