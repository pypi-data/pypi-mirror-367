import math
from abc import ABC, abstractmethod
import random
from functools import partial
from typing import List

import jax
from jax import lax
import jax.numpy as jnp
from numba import jit
from numba.experimental import jitclass

from apollo_toolbox_py.apollo_py.extra_tensorly_backend import Device, DType, Backend, ExtraBackend as T2
import tensorly as tl


class FunctionTensorly(ABC):

    def call(self, x: tl.tensor) -> tl.tensor:
        assert x.shape == (self.input_dim(),)
        out = T2.new_from_heterogeneous_array(self.call_raw(x))
        assert out.shape == (self.output_dim(),)
        return out

    @abstractmethod
    def call_raw(self, x: tl.tensor) -> List[tl.tensor]:
        pass

    @abstractmethod
    def input_dim(self):
        pass

    @abstractmethod
    def output_dim(self):
        pass


class TestFunction(FunctionTensorly):

    def call_raw(self, x: tl.tensor) -> List[tl.tensor]:
        return [tl.sin(x[0]), tl.cos(x[1])]

    def input_dim(self):
        return 2

    def output_dim(self):
        return 2


class BenchmarkFunction(FunctionTensorly):
    def __init__(self, n: int, m: int, num_operations: int):
        self.n = n
        self.m = m
        self.num_operations = num_operations
        self.r = []
        self.s = []
        for i in range(m):
            self.r.append([random.randint(0, n - 1) for _ in range(num_operations + 1)])
            self.s.append([random.randint(0, 1) for _ in range(num_operations)])

    def call_raw(self, x: tl.tensor) -> List[tl.tensor]:
        out = []

        for i in range(self.m):
            rr = self.r[i]
            ss = self.s[i]
            tmp = x[rr[0]]
            for j in range(self.num_operations):
                if ss[j] == 0:
                    tmp = tl.sin(tmp * x[rr[j + 1]])
                elif ss[j] == 1:
                    tmp = tl.cos(tmp * x[rr[j + 1]])
                else:
                    raise ValueError("Operation not supported")
            out.append(tmp)

        return out

    def input_dim(self):
        return self.n

    def output_dim(self):
        return self.m


class BenchmarkFunction2(FunctionTensorly):
    def __init__(self, n: int, m: int, num_operations: int):
        self.n = n
        self.m = m
        self.num_operations = num_operations
        self.r = []
        self.s = []
        for i in range(m):
            self.r.append([random.randint(0, n - 1) for _ in range(num_operations + 1)])
            self.s.append([random.randint(0, 1) for _ in range(num_operations)])

    def call_raw(self, x: tl.tensor) -> List[tl.tensor]:
        out = []

        for i in range(self.m):
            rr = self.r[i]
            ss = self.s[i]
            tmp = x[rr[0]]
            for j in range(self.num_operations):
                if ss[j] == 0:
                    tmp = tl.sin(tl.cos(tmp) + x[rr[j + 1]])
                elif ss[j] == 1:
                    tmp = tl.cos(tl.sin(tmp) + x[rr[j + 1]])
                else:
                    raise ValueError("Operation not supported")
            out.append(tmp)

        return out

    def input_dim(self):
        return self.n

    def output_dim(self):
        return self.m


class BenchmarkFunction2JAX:
    def __init__(self, n: int, m: int, num_operations: int):
        self.n = n
        self.m = m
        self.num_operations = num_operations

        self.r = jnp.array([
            [random.randint(0, n - 1) for _ in range(num_operations + 1)]
            for _ in range(m)
        ], dtype=jnp.int32)
        self.s = jnp.array([
            [random.randint(0, 1) for _ in range(num_operations)]
            for _ in range(m)
        ], dtype=jnp.int32)

    @partial(jax.jit, static_argnums=0)
    def call_raw(self, x: jnp.ndarray) -> jnp.ndarray:
        def compute_one_output(rr_i, ss_i):
            def body_fun(idx, tmp):
                op = ss_i[idx]
                x_val = x[rr_i[idx + 1]]
                tmp = lax.cond(
                    op == 0,
                    lambda t: jnp.sin(jnp.cos(t) + x_val),
                    lambda t: jnp.cos(jnp.sin(t) + x_val),
                    tmp
                )
                return tmp

            tmp0 = x[rr_i[0]]
            return lax.fori_loop(0, self.num_operations, body_fun, tmp0)

        outputs = jax.vmap(compute_one_output, in_axes=(0, 0))(self.r, self.s)
        return outputs

    def input_dim(self):
        return self.n

    def output_dim(self):
        return self.m
