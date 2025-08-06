import c_candyfloss as cc

class PipelineError(Exception):

    def __init__(self, *messages):
        self.message = ' @ '.join(messages)
        self.stack_info = None

    def add_stack_info(self, v):
        self.stack_info = '\n'.join(traceback.StackSummary(v).format())

    def __str__(self):
        info = self.stack_info or ''
        return '%s %s' % (info, self.message)

    def __repr__(self):
        return 'PipelineError: %s' % str(self)

cc.set_exception_class(PipelineError)


import os
import threading
import queue
from inspect import signature
import traceback
import time
import operator
from functools import reduce

from PIL import Image
import numpy as np

def parse_dict(inp):
    res = []
    for k, v in inp.items():
        if type(v) == str:
            v = v.encode('utf-8')
        res.append((str(k), v))
    return res


class Caps:

    def __init__(self, fmt, **params):
        if fmt is not None:
            self.caps = cc.make_caps(fmt, parse_dict(params))

    @classmethod
    def from_cc(cls, v):
        res = cls(None)
        res.caps = v
        return res

    def __getitem__(self, k):
        res = cc.caps_get_prop(self.caps, k)
        if res is None:
            raise KeyError(k)
        return res

    def is_compatible(self, other_caps):
        return cc.caps_is_compatible(self.caps, other_caps.caps)

    def to_list(self):
        return cc.caps_to_list(self.caps)

    def __iter__(self):
        return iter(self.to_list())

    def __str__(self):
        l = self.to_list()
        return 'Caps(%s, %s)' % (l[0].decode('utf-8'), ', '.join('%s=%r' % (k.decode('utf-8'),v)  for k,v in l[1:]))

    def union(self, other_caps):
        return Caps.from_cc(cc.caps_union(self.caps, other_caps.caps))

    def __or__(self, other):
        return self.union(other)


class ImageExtractor:

    __static_caps__ = Caps('video/x-raw', format='RGB')

    def unpack(data, caps):
        return Image.frombytes('RGB', (caps['width'], caps['height']), data)

    def pack(image, target_caps):
        try:
            if target_caps['format'] != b'RGB':
                raise ValueError
        except KeyError:
            pass
        try:
            if image.width != target_caps['width'] or image.height != target_caps['height']:
                image = image.resize((target_caps['width'], target_caps['height']))
        except KeyError:
            pass
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return image.tobytes()

class AudioExtractor:


    # TODO: handle 24-bit PCM (numpy doesn't have native 24-bit integer types)
    format_dtype = {
        'U8': np.uint8,
        'S16BE': np.dtype('>i2'),
        'S16LE': np.dtype('<i2'),
        'S32BE': np.dtype('>i4'),
        'S32LE': np.dtype('<i4'),
        'F32LE': np.float32,
        'F32BE': np.float32,
        'F64LE': np.float64,
        'F64BE': np.float64
    }

    __static_caps__ = reduce(operator.or_, 
        (Caps('audio/x-raw',format=k) for k in format_dtype.keys()))
    
    def unpack(data, caps):
        return np.frombuffer(data, dtype=self.format_dtype[caps['format']])

    def pack(arr, target_caps):
        return arr.astype(self.format_dtype[target_caps['format']]).tobytes()


def util_fn(f):
    def _res(*args, **kwargs):
        def _r2(pipeline):
            root = PipelineEl(pipeline, None)
            return f(root, *args, **kwargs)
        return _r2
    _res.__name__ = f.__name__
    return _res

class PipelineEl:

    def __init__(self, pipeline, arg):
        self.pipeline = pipeline

        if arg is None:
            self.obj = None
        elif type(arg) == tuple:
            self.set_obj(cc.make_capsfilter(pipeline.pipeline, arg[0], parse_dict(arg[1])), 
                'pipeline:%d' % hash(self))
        elif type(arg) == str:
            self.set_obj(*cc.construct_element(pipeline.pipeline, arg, []))
        elif type(arg) == list:
            self.set_obj(*cc.construct_element(pipeline.pipeline, arg[0], parse_dict(arg[1])))
        else:
            raise TypeError('invalid argument type: %r' % type(arg))

    def set_obj(self, obj, name):
        self.obj = obj
        self.pipeline.stacks[name] = traceback.extract_stack()

    def link(self, other):
        if self.obj is not None:
            cc.link_elements(self.obj, other.obj)

    @staticmethod
    def to_el(upstream, pipeline, v, rec=False):
        if isinstance(v, PipelineEl):
            return v
        else:
            try:
                return PipelineEl(pipeline, v)
            except TypeError as e:
                if callable(v):
                    return v(pipeline)
                else:
                    raise e
                
    def __rshift__(self, other):
        other = self.to_el(self, self.pipeline, other)
        self.link(other)
        return other

    def from_iter(self, inp, **kwargs):
        return IteratorSourceWrapper(self.pipeline, inp, **kwargs)

    def map(self, f, inp_extractor=ImageExtractor, outp_extractor=ImageExtractor):
        return UserCallback(self.pipeline, inp_extractor, outp_extractor, f)

class UserCallback(PipelineEl):

    def __init__(self, pipeline, inp_extractor, outp_extractor, callback):
        self.pipeline = pipeline
        self.callback = callback
        self.inp_extractor = inp_extractor
        self.outp_extractor = outp_extractor
        name = 'udf:%d' % hash(self)
        self.set_obj(cc.make_callback_transform(
            self.pipeline.pipeline, 
            inp_extractor.__static_caps__.caps, outp_extractor.__static_caps__.caps, 
            self._on_callback, name), 
            name)

    def _on_callback(self, inp_caps, outp_caps, data):
        inp_caps = Caps.from_cc(inp_caps)
        outp_caps = Caps.from_cc(outp_caps)
        try:
            inp = self.inp_extractor.unpack(data, inp_caps)
            outp = self.callback(inp)
            res = self.outp_extractor.pack(outp, outp_caps)
        except Exception as e:
            self.pipeline.exc = e
            raise e
        return res 

class IteratorSourceWrapper(PipelineEl):

    def __init__(self, pipeline, inp_iter, 
        framerate=30, extractor=ImageExtractor, returns_timestamp=False):

        self.returns_timestamp = returns_timestamp
        self.inp_iter = inp_iter
        self.extractor = extractor
        self.pipeline = pipeline
        self.nanos_per_frame = int(1000000000 / framerate)

        self.set_obj(cc.make_iterator_source(
            pipeline.pipeline,
            self,
            extractor.__static_caps__.caps),
            'appsrc:%d' % hash(self))


    def __iter__(self):
        total_time = 0
        try:
            for i, obj in enumerate(self.inp_iter):
                caps = Caps.from_cc(cc.get_static_pad_caps(self.obj, 'src'))
                if self.returns_timestamp:
                    ts, duration, obj = obj
                    yield (
                        self.extractor.pack(obj, caps),
                        ts, duration, i)
                    self.total_time += duration
                else:
                    yield (
                        self.extractor.pack(obj, caps),
                        total_time,
                        self.nanos_per_frame,
                        i)
                    total_time += self.nanos_per_frame
        except Exception as e:
            self.pipeline.exc = e

class deftransform:

    def __init__(self, inp_extractor, outp_extractor):
        self.inp_extractor = inp_extractor
        self.outp_extractor = outp_extractor
        self.callback = None

    def __call__(self, callback):
        self.callback = callback
        return self.construct

    def construct(self, pipeline):
        return UserCallback(pipeline, self.inp_extractor, self.outp_extractor, self.callback)

class CallbackSink:

    def __init__(self, pipeline, end_el):
        self.pipeline = pipeline
        self.el = cc.make_callback_sink(pipeline.pipeline)
        cc.link_elements(end_el.obj, self.el)

    def __iter__(self):
        while 1:
            v = cc.appsink_pull_buffer(self.el, 10000000) # 100ms (in nanos)
            if v is False:
                if self.pipeline.is_done:
                    if self.pipeline.exc is not None:
                        raise self.pipeline.exc
                    break
                else:
                    continue
            if v is None:
                break
            buf, w, h = v
            yield Image.frombytes('RGB', (w, h), buf)

import webbrowser, socketserver
def browser_open(data, mime=None):
    class Handler(socketserver.BaseRequestHandler):

        def handle(self):
            self.request.send(b'HTTP/1.1 200 OK\r\n')
            if mime is not None:
                self.request.send(b'Content-Type: %s\r\n' % mime.encode('utf-8'))
            self.request.send(b'\r\n')
            self.request.send(data)

    with socketserver.TCPServer(('127.0.0.1', 0), Handler) as server:
        webbrowser.open('http://127.0.0.1:%d/' % server.server_address[1])
        server.handle_request()

class Pipeline:

    def __init__(self, gen_fn=None, name=None, debug_viz=False):
        if name is None:
            name = str(hash(self))
        self.stacks = {}
        self.error_stack = None
        self.exc = None
        self.run_lock = threading.Lock()
        self.run_lock.acquire(blocking=False)
        self.pipeline = cc.make_pipeline(name, self._on_done)
        self.is_done = False
        self.gen_el = None
        self.debug_viz = debug_viz

        if gen_fn is not None:
            self.gen_el = gen_fn(PipelineEl(self, None))

    def _on_done(self, exc, el_names):
        if not self.is_done:
            if el_names is not None:
                for name in reversed(el_names):
                    try:
                        self.error_stack = self.stacks[name]
                        break
                    except KeyError:
                        pass
            if self.exc is None:
                self.exc = exc
            self.is_done = True
            self.run_lock.release()

    def run_async(self):
        if self.is_done:
            return
        if self.debug_viz:
            import graphviz
            debug_dot = cc.dot_viz(self.pipeline)
            svg = graphviz.pipe('dot', 'svg', debug_dot)
            browser_open(svg, 'image/svg+xml')
        cc.run_pipeline(self.pipeline)

    def run(self):
        self.run_async()
        self.run_lock.acquire()
        self.run_lock.release()
        self._post_run()

    def _post_run(self):
        if self.exc is not None:
            if self.error_stack is not None:
                try:
                    self.exc.add_stack_info(self.error_stack)
                except AttributeError:
                    pass
            raise self.exc

    def close(self):
        cc.stop_pipeline(self.pipeline)
        self._post_run()


    def __enter__(self):
        return PipelineEl(self, None)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            raise exc_val

        self.run()

    def __iter__(self):
        if self.gen_el is None:
            return []

        res = CallbackSink(self, self.gen_el)
        self.run_async()
        for frame in res:
            yield frame
        self._post_run()
