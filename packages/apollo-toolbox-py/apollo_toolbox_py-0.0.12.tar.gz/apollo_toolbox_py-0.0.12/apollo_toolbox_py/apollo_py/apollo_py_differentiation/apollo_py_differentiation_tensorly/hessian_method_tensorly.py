from abc import ABC, abstractmethod
from typing import List
import tensorly as tl

from apollo_toolbox_py.apollo_py.apollo_py_differentiation.apollo_py_differentiation_tensorly.derivative_method_tensorly import \
    DerivativeMethodTensorly
from apollo_toolbox_py.apollo_py.apollo_py_differentiation.apollo_py_differentiation_tensorly.function_tensorly import \
    FunctionTensorly
from apollo_toolbox_py.apollo_py.extra_tensorly_backend import Backend, ExtraBackend as T2


class HessianMethodTensorly(ABC):
    @abstractmethod
    def allowable_backends(self) -> List[Backend]:
        pass

    @abstractmethod
    def default_backend(self) -> Backend:
        pass

    @abstractmethod
    def hessian_raw(self, f: FunctionTensorly, x: tl.tensor) -> tl.tensor:
        pass

    def hessian(self, f: FunctionTensorly, x: tl.tensor) -> tl.tensor:
        assert f.output_dim() == 1
        assert x.shape == (f.input_dim(),)
        h = self.hessian_raw(f, x)
        assert h.shape == (f.input_dim(), f.input_dim()), 'shape is {}'.format(h.shape)
        return h


class HessianMethodElementwiseFD(HessianMethodTensorly):
    def allowable_backends(self) -> List[Backend]:
        return [Backend.Numpy, Backend.PyTorch, Backend.JAX]

    def default_backend(self) -> Backend:
        return Backend.Numpy

    def hessian_raw(self, f: FunctionTensorly, x: tl.tensor) -> tl.tensor:
        out = tl.zeros((f.input_dim(), f.input_dim()), device=getattr(x, 'device', None), dtype=x.dtype)

        epsilon = 0.00001

        for i in range(f.input_dim()):
            e_i = tl.zeros((f.input_dim(),), device=getattr(x, 'device', None), dtype=x.dtype)
            e_i = T2.set_and_return(e_i, i, 1.0)
            for j in range(f.input_dim()):
                if i == j:
                    fp = f.call(x + epsilon * e_i)
                    fn = f.call(x - epsilon * e_i)
                    ff = f.call(x)

                    res = (fp - 2.0 * ff + fn) / (epsilon * epsilon)
                    out = T2.set_and_return(out, (i, j), res)
                else:
                    e_j = tl.zeros((f.input_dim(),), device=getattr(x, 'device', None), dtype=x.dtype)
                    e_j = T2.set_and_return(e_j, j, 1.0)

                    fpp = f.call(x + epsilon * e_i + epsilon * e_j)
                    fpn = f.call(x + epsilon * e_i - epsilon * e_j)
                    fnp = f.call(x - epsilon * e_i + epsilon * e_j)
                    fnn = f.call(x - epsilon * e_i - epsilon * e_j)

                    res = (fpp - fpn - fnp + fnn) / (4.0 * epsilon * epsilon)
                    out = T2.set_and_return(out, (i, j), res)

        return out


class HessianMethodGradientwiseFD(HessianMethodTensorly):
    def __init__(self, gradient_method: DerivativeMethodTensorly):
        self.gradient_method = gradient_method

    def allowable_backends(self) -> List[Backend]:
        return self.gradient_method.allowable_backends()

    def default_backend(self) -> Backend:
        return self.gradient_method.default_backend()

    def hessian_raw(self, f: FunctionTensorly, x: tl.tensor) -> tl.tensor:
        out = tl.zeros((f.input_dim(), f.input_dim()), device=getattr(x, 'device', None), dtype=x.dtype)

        epsilon = 0.00001
        # g0 = self.gradient_method.derivative(f, x)

        for i in range(f.input_dim()):
            e_i = tl.zeros((f.input_dim(),), device=getattr(x, 'device', None), dtype=x.dtype)
            e_i = T2.set_and_return(e_i, i, 1.0)
            ghp = self.gradient_method.derivative(f, x + epsilon * e_i)
            ghn = self.gradient_method.derivative(f, x - epsilon * e_i)
            col = (ghp - ghn) / (2.0*epsilon)
            out = T2.set_and_return(out, (slice(None), i), col)

        return (out + out.T) / 2.0
