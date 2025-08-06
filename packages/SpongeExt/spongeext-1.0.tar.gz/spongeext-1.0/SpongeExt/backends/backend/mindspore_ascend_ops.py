# Copyright Dechin CHEN 2025

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from functools import wraps
import mindspore as ms
from mindspore import mint


_MINDSPORE_OPS = {}

def register_op(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    _MINDSPORE_OPS[func.__name__] = wrapper
    return wrapper


@register_op
def Sum(ipt, *args, **kwargs):
    return mint.sum(ipt, *args, **kwargs)


@register_op
def where(ipt, *args, **kwargs):
    return mint.where(ipt, *args, **kwargs)


@register_op
def arange(ipt, *args, **kwargs):
    return mint.arange(ipt, *args, **kwargs)


@register_op
def bernoulli(ipt, *args, **kwargs):
    return mint.bernoulli(ipt, *args, **kwargs)


@register_op
def bincount(ipt, *args, **kwargs):
    return mint.bincount(ipt, *args, **kwargs)


@register_op
def clone(ipt, *args, **kwargs):
    return mint.clone(ipt, *args, **kwargs)


@register_op
def eye(ipt, *args, **kwargs):
    return mint.eye(ipt, *args, **kwargs)


@register_op
def einsum(ipt, *args, **kwargs):
    return mint.einsum(ipt, *args, **kwargs)


@register_op
def empty(ipt, *args, **kwargs):
    return mint.empty(ipt, *args, **kwargs)


@register_op
def empty_like(ipt, *args, **kwargs):
    return mint.empty_like(ipt, *args, **kwargs)


@register_op
def full(ipt, *args, **kwargs):
    return mint.full(ipt, *args, **kwargs)


@register_op
def full_like(ipt, *args, **kwargs):
    return mint.full_like(ipt, *args, **kwargs)


@register_op
def linspace(ipt, *args, **kwargs):
    return mint.linspace(ipt, *args, **kwargs)


@register_op
def ones(ipt, *args, **kwargs):
    return mint.ones(ipt, *args, **kwargs)


@register_op
def ones_like(ipt, *args, **kwargs):
    return mint.ones_like(ipt, *args, **kwargs)


@register_op
def randint(ipt, *args, **kwargs):
    return mint.randint(ipt, *args, **kwargs)


@register_op
def randint_like(ipt, *args, **kwargs):
    return mint.randint_like(ipt, *args, **kwargs)


@register_op
def randn(ipt, *args, **kwargs):
    return mint.randn(ipt, *args, **kwargs)


@register_op
def randn_like(ipt, *args, **kwargs):
    return mint.randn_like(ipt, *args, **kwargs)


@register_op
def randperm(ipt, *args, **kwargs):
    return mint.randperm(ipt, *args, **kwargs)


@register_op
def zeros(ipt, *args, **kwargs):
    return mint.zeros(ipt, *args, **kwargs)


@register_op
def zeros_like(ipt, *args, **kwargs):
    return mint.zeros_like(ipt, *args, **kwargs)


@register_op
def vstack(ipt, *args, **kwargs):
    return mint.stack(ipt, *args, **kwargs, dim=0)


@register_op
def hstack(ipt, *args, **kwargs):
    return mint.stack(ipt, *args, **kwargs, dim=1)


@register_op
def exp(ipt, *args, **kwargs):
    return mint.exp(ipt, *args, **kwargs)


@register_op
def cat(ipt, *args, **kwargs):
    return mint.cat(ipt, *args, **kwargs)


@register_op
def chunk(ipt, *args, **kwargs):
    return mint.chunk(ipt, *args, **kwargs)


@register_op
def concat(ipt, *args, **kwargs):
    return mint.concat(ipt, *args, **kwargs)


@register_op
def count_nonzero(ipt, *args, **kwargs):
    return mint.count_nonzero(ipt, *args, **kwargs)


@register_op
def gather(ipt, *args, **kwargs):
    return mint.gather(ipt, *args, **kwargs)


@register_op
def index_add(ipt, *args, **kwargs):
    return mint.index_add(ipt, *args, **kwargs)


@register_op
def index_select(ipt, *args, **kwargs):
    return mint.index_select(ipt, *args, **kwargs)


@register_op
def masked_select(ipt, *args, **kwargs):
    return mint.masked_select(ipt, *args, **kwargs)


@register_op
def permute(ipt, *args, **kwargs):
    return mint.permute(ipt, *args, **kwargs)


@register_op
def reshape(ipt, *args, **kwargs):
    return mint.reshape(ipt, *args, **kwargs)


@register_op
def scatter(ipt, *args, **kwargs):
    return mint.scatter(ipt, *args, **kwargs)


@register_op
def scatter_add(ipt, *args, **kwargs):
    return mint.scatter_add(ipt, *args, **kwargs)


@register_op
def split(ipt, *args, **kwargs):
    return mint.split(ipt, *args, **kwargs)


@register_op
def narrow(ipt, *args, **kwargs):
    return mint.narrow(ipt, *args, **kwargs)


@register_op
def nonzero(ipt, *args, **kwargs):
    return mint.nonzero(ipt, *args, **kwargs)


@register_op
def tile(ipt, *args, **kwargs):
    return mint.tile(ipt, *args, **kwargs)


@register_op
def tril(ipt, *args, **kwargs):
    return mint.tril(ipt, *args, **kwargs)


@register_op
def select(ipt, *args, **kwargs):
    return mint.select(ipt, *args, **kwargs)


@register_op
def squeeze(ipt, *args, **kwargs):
    return mint.squeeze(ipt, *args, **kwargs)


@register_op
def stack(ipt, *args, **kwargs):
    return mint.stack(ipt, *args, **kwargs)


@register_op
def swapaxes(ipt, *args, **kwargs):
    return mint.swapaxes(ipt, *args, **kwargs)


@register_op
def transpose(ipt, *args, **kwargs):
    return mint.transpose(ipt, *args, **kwargs)


@register_op
def triu(ipt, *args, **kwargs):
    return mint.triu(ipt, *args, **kwargs)


@register_op
def unbind(ipt, *args, **kwargs):
    return mint.unbind(ipt, *args, **kwargs)


@register_op
def unique_consecutive(ipt, *args, **kwargs):
    return mint.unique_consecutive(ipt, *args, **kwargs)


@register_op
def unsqueeze(ipt, *args, **kwargs):
    return mint.unsqueeze(ipt, *args, **kwargs)


@register_op
def multinomial(ipt, *args, **kwargs):
    return mint.multinomial(ipt, *args, **kwargs)


@register_op
def normal(ipt, *args, **kwargs):
    return mint.normal(ipt, *args, **kwargs)


@register_op
def rand_like(ipt, *args, **kwargs):
    return mint.rand_like(ipt, *args, **kwargs)


@register_op
def rand(ipt, *args, **kwargs):
    return mint.rand(ipt, *args, **kwargs)


@register_op
def Abs(ipt, *args, **kwargs):
    return mint.abs(ipt, *args, **kwargs)


@register_op
def add(ipt, *args, **kwargs):
    return mint.add(ipt, *args, **kwargs)


@register_op
def addmv(ipt, *args, **kwargs):
    return mint.addmv(ipt, *args, **kwargs)


@register_op
def acos(ipt, *args, **kwargs):
    return mint.acos(ipt, *args, **kwargs)


@register_op
def acosh(ipt, *args, **kwargs):
    return mint.acosh(ipt, *args, **kwargs)


@register_op
def arccos(ipt, *args, **kwargs):
    return mint.arccos(ipt, *args, **kwargs)


@register_op
def arccosh(ipt, *args, **kwargs):
    return mint.arccosh(ipt, *args, **kwargs)


@register_op
def arcsin(ipt, *args, **kwargs):
    return mint.arcsin(ipt, *args, **kwargs)


@register_op
def arcsinh(ipt, *args, **kwargs):
    return mint.arcsinh(ipt, *args, **kwargs)


@register_op
def arctan(ipt, *args, **kwargs):
    return mint.arctan(ipt, *args, **kwargs)


@register_op
def arctan2(ipt, *args, **kwargs):
    return mint.arctan2(ipt, *args, **kwargs)


@register_op
def arctanh(ipt, *args, **kwargs):
    return mint.arctanh(ipt, *args, **kwargs)


@register_op
def asin(ipt, *args, **kwargs):
    return mint.asin(ipt, *args, **kwargs)


@register_op
def asinh(ipt, *args, **kwargs):
    return mint.asinh(ipt, *args, **kwargs)


@register_op
def atan(ipt, *args, **kwargs):
    return mint.atan(ipt, *args, **kwargs)


@register_op
def atan2(ipt, *args, **kwargs):
    return mint.atan2(ipt, *args, **kwargs)


@register_op
def atanh(ipt, *args, **kwargs):
    return mint.atanh(ipt, *args, **kwargs)


@register_op
def bitwise_and(ipt, *args, **kwargs):
    return mint.bitwise_and(ipt, *args, **kwargs)


@register_op
def bitwise_or(ipt, *args, **kwargs):
    return mint.bitwise_or(ipt, *args, **kwargs)


@register_op
def bitwise_xor(ipt, *args, **kwargs):
    return mint.bitwise_xor(ipt, *args, **kwargs)


@register_op
def ceil(ipt, *args, **kwargs):
    return mint.ceil(ipt, *args, **kwargs)


@register_op
def clamp(ipt, *args, **kwargs):
    return mint.clamp(ipt, *args, **kwargs)


@register_op
def cos(ipt, *args, **kwargs):
    return mint.cos(ipt, *args, **kwargs)


@register_op
def cosh(ipt, *args, **kwargs):
    return mint.cosh(ipt, *args, **kwargs)


@register_op
def cross(ipt, *args, **kwargs):
    return mint.cross(ipt, *args, **kwargs)


@register_op
def diff(ipt, *args, **kwargs):
    return mint.diff(ipt, *args, **kwargs)


@register_op
def div(ipt, *args, **kwargs):
    return mint.div(ipt, *args, **kwargs)


@register_op
def divide(ipt, *args, **kwargs):
    return mint.divide(ipt, *args, **kwargs)


@register_op
def erf(ipt, *args, **kwargs):
    return mint.erf(ipt, *args, **kwargs)


@register_op
def erfc(ipt, *args, **kwargs):
    return mint.erfc(ipt, *args, **kwargs)


@register_op
def erfinv(ipt, *args, **kwargs):
    return mint.erfinv(ipt, *args, **kwargs)


@register_op
def exp(ipt, *args, **kwargs):
    return mint.exp(ipt, *args, **kwargs)


@register_op
def exp2(ipt, *args, **kwargs):
    return mint.exp2(ipt, *args, **kwargs)


@register_op
def expm1(ipt, *args, **kwargs):
    return mint.expm1(ipt, *args, **kwargs)


@register_op
def fix(ipt, *args, **kwargs):
    return mint.fix(ipt, *args, **kwargs)


@register_op
def float_power(ipt, *args, **kwargs):
    return mint.float_power(ipt, *args, **kwargs)


@register_op
def floor(ipt, *args, **kwargs):
    return mint.floor(ipt, *args, **kwargs)


@register_op
def fmod(ipt, *args, **kwargs):
    return mint.fmod(ipt, *args, **kwargs)


@register_op
def frac(ipt, *args, **kwargs):
    return mint.frac(ipt, *args, **kwargs)


@register_op
def lerp(ipt, *args, **kwargs):
    return mint.lerp(ipt, *args, **kwargs)


@register_op
def log(ipt, *args, **kwargs):
    return mint.log(ipt, *args, **kwargs)


@register_op
def log1p(ipt, *args, **kwargs):
    return mint.log1p(ipt, *args, **kwargs)


@register_op
def log2(ipt, *args, **kwargs):
    return mint.log2(ipt, *args, **kwargs)


@register_op
def log10(ipt, *args, **kwargs):
    return mint.log10(ipt, *args, **kwargs)


@register_op
def logaddexp(ipt, *args, **kwargs):
    return mint.logaddexp(ipt, *args, **kwargs)


@register_op
def logaddexp2(ipt, *args, **kwargs):
    return mint.logaddexp2(ipt, *args, **kwargs)


@register_op
def logical_and(ipt, *args, **kwargs):
    return mint.logical_and(ipt, *args, **kwargs)


@register_op
def logical_not(ipt, *args, **kwargs):
    return mint.logical_not(ipt, *args, **kwargs)


@register_op
def logical_or(ipt, *args, **kwargs):
    return mint.logical_or(ipt, *args, **kwargs)


@register_op
def logical_xor(ipt, *args, **kwargs):
    return mint.logical_xor(ipt, *args, **kwargs)


@register_op
def mul(ipt, *args, **kwargs):
    return mint.mul(ipt, *args, **kwargs)


@register_op
def mv(ipt, *args, **kwargs):
    return mint.mv(ipt, *args, **kwargs)


@register_op
def nansum(ipt, *args, **kwargs):
    return mint.nansum(ipt, *args, **kwargs)


@register_op
def nan_to_num(ipt, *args, **kwargs):
    return mint.nan_to_num(ipt, *args, **kwargs)


@register_op
def neg(ipt, *args, **kwargs):
    return mint.neg(ipt, *args, **kwargs)


@register_op
def negative(ipt, *args, **kwargs):
    return mint.negative(ipt, *args, **kwargs)


@register_op
def Pow(ipt, *args, **kwargs):
    return mint.pow(ipt, *args, **kwargs)


@register_op
def polar(ipt, *args, **kwargs):
    return mint.polar(ipt, *args, **kwargs)


@register_op
def ravel(ipt, *args, **kwargs):
    return mint.ravel(ipt, *args, **kwargs)


@register_op
def reciprocal(ipt, *args, **kwargs):
    return mint.reciprocal(ipt, *args, **kwargs)


@register_op
def remainder(ipt, *args, **kwargs):
    return mint.remainder(ipt, *args, **kwargs)


@register_op
def roll(ipt, *args, **kwargs):
    return mint.roll(ipt, *args, **kwargs)


@register_op
def round(ipt, *args, **kwargs):
    return mint.round(ipt, *args, **kwargs)


@register_op
def rsqrt(ipt, *args, **kwargs):
    return mint.rsqrt(ipt, *args, **kwargs)


@register_op
def sigmoid(ipt, *args, **kwargs):
    return mint.sigmoid(ipt, *args, **kwargs)


@register_op
def sign(ipt, *args, **kwargs):
    return mint.sign(ipt, *args, **kwargs)


@register_op
def sin(ipt, *args, **kwargs):
    return mint.sin(ipt, *args, **kwargs)


@register_op
def sinc(ipt, *args, **kwargs):
    return mint.sinc(ipt, *args, **kwargs)


@register_op
def sinh(ipt, *args, **kwargs):
    return mint.sinh(ipt, *args, **kwargs)


@register_op
def softmax(ipt, *args, **kwargs):
    return mint.softmax(ipt, *args, **kwargs)


@register_op
def sqrt(ipt, *args, **kwargs):
    return mint.sqrt(ipt, *args, **kwargs)


@register_op
def square(ipt, *args, **kwargs):
    return mint.square(ipt, *args, **kwargs)


@register_op
def sub(ipt, *args, **kwargs):
    return mint.sub(ipt, *args, **kwargs)


@register_op
def t(ipt, *args, **kwargs):
    return mint.t(ipt, *args, **kwargs)


@register_op
def tan(ipt, *args, **kwargs):
    return mint.tan(ipt, *args, **kwargs)


@register_op
def tanh(ipt, *args, **kwargs):
    return mint.tanh(ipt, *args, **kwargs)


@register_op
def trunc(ipt, *args, **kwargs):
    return mint.trunc(ipt, *args, **kwargs)


@register_op
def xlogy(ipt, *args, **kwargs):
    return mint.xlogy(ipt, *args, **kwargs)


@register_op
def amax(ipt, *args, **kwargs):
    return mint.amax(ipt, *args, **kwargs)


@register_op
def amin(ipt, *args, **kwargs):
    return mint.amin(ipt, *args, **kwargs)


@register_op
def argmax(ipt, *args, **kwargs):
    return mint.argmax(ipt, *args, **kwargs)


@register_op
def argmin(ipt, *args, **kwargs):
    return mint.argmin(ipt, *args, **kwargs)


@register_op
def argsort(ipt, *args, **kwargs):
    return mint.argsort(ipt, *args, **kwargs)


@register_op
def All(ipt, *args, **kwargs):
    return mint.all(ipt, *args, **kwargs)


@register_op
def Any(ipt, *args, **kwargs):
    return mint.any(ipt, *args, **kwargs)


@register_op
def cumprod(ipt, *args, **kwargs):
    return mint.cumprod(ipt, *args, **kwargs)


@register_op
def histc(ipt, *args, **kwargs):
    return mint.histc(ipt, *args, **kwargs)


@register_op
def logsumexp(ipt, *args, **kwargs):
    return mint.logsumexp(ipt, *args, **kwargs)


@register_op
def Max(ipt, *args, **kwargs):
    return mint.max(ipt, *args, **kwargs)


@register_op
def mean(ipt, *args, **kwargs):
    return mint.mean(ipt, *args, **kwargs)


@register_op
def median(ipt, *args, **kwargs):
    return mint.median(ipt, *args, **kwargs)


@register_op
def Min(ipt, *args, **kwargs):
    return mint.min(ipt, *args, **kwargs)


@register_op
def norm(ipt, *args, **kwargs):
    return mint.norm(ipt, *args, **kwargs)


@register_op
def prod(ipt, *args, **kwargs):
    return mint.prod(ipt, *args, **kwargs)


@register_op
def std(ipt, *args, **kwargs):
    return mint.std(ipt, *args, **kwargs)


@register_op
def std_mean(ipt, *args, **kwargs):
    return mint.std_mean(ipt, *args, **kwargs)


@register_op
def unique(ipt, *args, **kwargs):
    return mint.unique(ipt, *args, **kwargs)


@register_op
def var(ipt, *args, **kwargs):
    return mint.var(ipt, *args, **kwargs)


@register_op
def var_mean(ipt, *args, **kwargs):
    return mint.var_mean(ipt, *args, **kwargs)


@register_op
def allclose(ipt, *args, **kwargs):
    return mint.allclose(ipt, *args, **kwargs)


@register_op
def argsort(ipt, *args, **kwargs):
    return mint.argsort(ipt, *args, **kwargs)


@register_op
def eq(ipt, *args, **kwargs):
    return mint.eq(ipt, *args, **kwargs)


@register_op
def equal(ipt, *args, **kwargs):
    return mint.equal(ipt, *args, **kwargs)


@register_op
def greater(ipt, *args, **kwargs):
    return mint.greater(ipt, *args, **kwargs)


@register_op
def greater_equal(ipt, *args, **kwargs):
    return mint.greater_equal(ipt, *args, **kwargs)


@register_op
def gt(ipt, *args, **kwargs):
    return mint.gt(ipt, *args, **kwargs)


@register_op
def isclose(ipt, *args, **kwargs):
    return mint.isclose(ipt, *args, **kwargs)


@register_op
def isfinite(ipt, *args, **kwargs):
    return mint.isfinite(ipt, *args, **kwargs)


@register_op
def isinf(ipt, *args, **kwargs):
    return mint.isinf(ipt, *args, **kwargs)


@register_op
def isneginf(ipt, *args, **kwargs):
    return mint.isneginf(ipt, *args, **kwargs)


@register_op
def le(ipt, *args, **kwargs):
    return mint.le(ipt, *args, **kwargs)


@register_op
def less(ipt, *args, **kwargs):
    return mint.less(ipt, *args, **kwargs)


@register_op
def less_equal(ipt, *args, **kwargs):
    return mint.less_equal(ipt, *args, **kwargs)


@register_op
def lt(ipt, *args, **kwargs):
    return mint.lt(ipt, *args, **kwargs)


@register_op
def maximum(ipt, *args, **kwargs):
    return mint.maximum(ipt, *args, **kwargs)


@register_op
def minimum(ipt, *args, **kwargs):
    return mint.minimum(ipt, *args, **kwargs)


@register_op
def ne(ipt, *args, **kwargs):
    return mint.ne(ipt, *args, **kwargs)


@register_op
def not_equal(ipt, *args, **kwargs):
    return mint.not_equal(ipt, *args, **kwargs)


@register_op
def topk(ipt, *args, **kwargs):
    return mint.topk(ipt, *args, **kwargs)


@register_op
def sort(ipt, *args, **kwargs):
    return mint.sort(ipt, *args, **kwargs)


@register_op
def addbmm(ipt, *args, **kwargs):
    return mint.addbmm(ipt, *args, **kwargs)


@register_op
def addmm(ipt, *args, **kwargs):
    return mint.addmm(ipt, *args, **kwargs)


@register_op
def baddbmm(ipt, *args, **kwargs):
    return mint.baddbmm(ipt, *args, **kwargs)


@register_op
def bmm(ipt, *args, **kwargs):
    return mint.bmm(ipt, *args, **kwargs)


@register_op
def dot(ipt, *args, **kwargs):
    return mint.dot(ipt, *args, **kwargs)


@register_op
def inverse(ipt, *args, **kwargs):
    return mint.inverse(ipt, *args, **kwargs)


@register_op
def matmul(ipt, *args, **kwargs):
    return mint.matmul(ipt, *args, **kwargs)


@register_op
def meshgrid(ipt, *args, **kwargs):
    return mint.meshgrid(ipt, *args, **kwargs)


@register_op
def mm(ipt, *args, **kwargs):
    return mint.mm(ipt, *args, **kwargs)


@register_op
def outer(ipt, *args, **kwargs):
    return mint.outer(ipt, *args, **kwargs)


@register_op
def trace(ipt, *args, **kwargs):
    return mint.trace(ipt, *args, **kwargs)


@register_op
def broadcast_to(ipt, *args, **kwargs):
    return mint.broadcast_to(ipt, *args, **kwargs)


@register_op
def cdist(ipt, *args, **kwargs):
    return mint.cdist(ipt, *args, **kwargs)


@register_op
def cummax(ipt, *args, **kwargs):
    return mint.cummax(ipt, *args, **kwargs)


@register_op
def cummin(ipt, *args, **kwargs):
    return mint.cummin(ipt, *args, **kwargs)


@register_op
def cumsum(ipt, *args, **kwargs):
    return mint.cumsum(ipt, *args, **kwargs)


@register_op
def diag(ipt, *args, **kwargs):
    return mint.diag(ipt, *args, **kwargs)


@register_op
def flatten(ipt, *args, **kwargs):
    return mint.flatten(ipt, *args, **kwargs)


@register_op
def flip(ipt, *args, **kwargs):
    return mint.flip(ipt, *args, **kwargs)


@register_op
def tensor(input, *args, **kwargs):
    return mint.array(input, *args, **kwargs)


@register_op
def to_numpy(input):
    return input.asnumpy()


@register_op
def repeat_interleave(ipt, *args, **kwargs):
    return mint.repeat_interleave(ipt, *args, **kwargs)


@register_op
def searchsorted(ipt, *args, **kwargs):
    return mint.searchsorted(ipt, *args, **kwargs)


@register_op
def tril(ipt, *args, **kwargs):
    return mint.tril(ipt, *args, **kwargs)


@register_op
def triangular_solve(ipt, *args, **kwargs):
    return mint.triangular_solve(ipt, *args, **kwargs)

