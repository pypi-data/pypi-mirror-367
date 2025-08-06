#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>

#include <pthread.h>

#include <Python.h>

#include <gst/gst.h>
#include <gst/video/video.h>
#include <gst/video/gstvideofilter.h>

//#define DEBUG_PRINTF 1

#define BEGIN_PYTHON_THREAD PyGILState_STATE _gil_state = PyGILState_Ensure();
#define END_PYTHON_THREAD PyGILState_Release(_gil_state);

static inline void py_maybe_decref(PyObject *v) {
    if (v != NULL && v != Py_None) Py_DECREF(v);
}

static PyObject *pipeline_exception_class = NULL;
static PyObject *nil_tuple = NULL;

static inline GstElement *element_ref_unsink(GstElement *v) {

    return (GstElement *) g_object_ref_sink((GObject *) v);

}

static void *gevent_thread_worker(void *udata) {

    GMainContext *ctx = g_main_context_default();
    if (g_main_context_acquire(ctx)) {
        GMainLoop *loop = g_main_loop_new(ctx, 1);
        g_main_loop_run(loop);
    }
    return NULL;

}

static void start_gevent_thread() {
    pthread_t gevent_thread;
    pthread_create(&gevent_thread, NULL, gevent_thread_worker, NULL);
}

static int py_object_to_g_value(GValue *res, PyObject *inp) {

    if (PyLong_Check(inp)) {
        g_value_init(res, G_TYPE_INT);
        g_value_set_int(res, PyLong_AsLong(inp));
        return 1;
    } else if (PyBytes_Check(inp)) {
        g_value_init(res, G_TYPE_STRING);
        g_value_set_string(res, PyBytes_AsString(inp));
        return 1;
    } else if (PyFloat_Check(inp)) {
        g_value_init(res, G_TYPE_DOUBLE);
        g_value_set_double(res, PyFloat_AsDouble(inp));
        return 1;
    } else {
        PyErr_SetNone(PyExc_TypeError);
        return 0;
    }


}

static PyObject *py_object_from_g_value(const GValue *inp, GType typ) {

    switch(typ) {

        case G_TYPE_INT:
            int v = g_value_get_int(inp);
            return PyLong_FromLong(v);
        case G_TYPE_LONG:
            glong vl = g_value_get_long(inp);
            return PyLong_FromLong(vl);
        case G_TYPE_STRING:
            const gchar *vs = g_value_get_string(inp);
            return PyBytes_FromString(vs);
        case G_TYPE_DOUBLE:
            const double vd = g_value_get_double(inp);
            return PyFloat_FromDouble(vd);
        default:
            PyErr_SetNone(PyExc_TypeError);
            return NULL;

    }

}

static GstCaps *py_unwrap_caps(PyObject *inp) {
    GstCaps *res = PyCapsule_GetPointer(inp, "caps");    
    return res;
}

static void py_caps_unref(PyObject *v) {
    BEGIN_PYTHON_THREAD
    GstCaps *caps = py_unwrap_caps(v);
    END_PYTHON_THREAD
    gst_caps_unref(caps);
}

static PyObject *py_wrap_caps(GstCaps *obj) {

    gst_caps_ref(obj);
    return PyCapsule_New(obj, "caps", py_caps_unref);
    
}

static gint sample_get_int(GstSample *s, const char *k) {

    GstCaps *caps = gst_sample_get_caps(s);
    GstStructure *st = gst_caps_get_structure(caps, 0);
    gint res;
    
    gst_structure_get_int(st, k, &res);

    return res;


}

static size_t sample_get_width(GstSample *s) {

    return sample_get_int(s, "width");

}

static size_t sample_get_height(GstSample *s) {

    return sample_get_int(s, "height");

}

static GstElement *python_gst_object_unwrap(PyObject *inp) {
    return PyCapsule_GetPointer(inp, "gst");
}

static void py_gst_wrapper_unref(PyObject *wrapper) {
    BEGIN_PYTHON_THREAD
    GstElement *ptr = python_gst_object_unwrap(wrapper);
    END_PYTHON_THREAD
    if (ptr != NULL) {
        gst_object_unref(ptr);
    }
}

static PyObject *python_gst_object_wrapper(GstElement *el) {
    return PyCapsule_New(el, "gst", py_gst_wrapper_unref);

}

typedef struct PyPipeline {
    GstPipeline *pipeline;
    PyObject *done_callback;
    PyObject *exc;
} PyPipeline;

static PyPipeline *py_pipeline_unwrap(PyObject *wrapper) {
    return PyCapsule_GetPointer(wrapper, "pipeline");
}

static void py_pipeline_wrapper_unref(PyObject *wrapper) {

    PyPipeline *p = py_pipeline_unwrap(wrapper);
    if (p->pipeline) {
        gst_element_set_state((GstElement *) (p->pipeline), GST_STATE_NULL);
        gst_object_unref(p->pipeline);
    }
    if (p->done_callback) Py_DECREF(p->done_callback);
    if (p->exc && p->exc != Py_None) Py_DECREF(p->exc);
    free(p);

}

static PyObject *py_pipeline_wrap(PyPipeline *p) {
    return PyCapsule_New(p, "pipeline", py_pipeline_wrapper_unref);
}

static PyPipeline *py_pipeline_construct(GstPipeline *gp, PyObject *cb) {

    PyPipeline *res = malloc(sizeof(PyPipeline));
    res->pipeline = gp;
    res->done_callback = cb;
    res->exc = Py_None;
    Py_INCREF(cb);
    return res;

}

static PyObject *make_pipeline(PyObject *self, PyObject *args) {

    const char *pipeline_name;
    PyObject *callback = NULL;
    if (!PyArg_ParseTuple(args, "sO", &pipeline_name, &callback)) return NULL;

    GstPipeline *pipeline = (GstPipeline *) gst_pipeline_new(pipeline_name);
    PyPipeline *pp = py_pipeline_construct(pipeline, callback);


    return py_pipeline_wrap(pp);

}

static PyObject *remove_element(PyObject *self, PyObject *args) {

    PyPipeline *pipeline;
    GstElement *el;

    PyObject *pipeline_wrapper = NULL;
    PyObject *el_wrapper = NULL;

    if (!PyArg_ParseTuple(args, "OO", &pipeline_wrapper, &el_wrapper)) return NULL;

    pipeline = py_pipeline_unwrap(pipeline_wrapper);
    if (pipeline == NULL) return NULL;

    el = python_gst_object_unwrap(el_wrapper);
    if (el == NULL) return NULL;

    if (!gst_bin_remove((GstBin *) (pipeline->pipeline), el)) {

        PyErr_SetString(PyExc_RuntimeError, "failed to remove element");
        return NULL;

    }


    Py_RETURN_NONE;

}

static PyObject *construct_element(PyObject *self, PyObject *args) {

    GstElementFactory *factory;
    GstElement *res;
    PyPipeline *pipeline;
    
    const char *element_name;
    PyObject *pipeline_wrapper = NULL;
    PyObject *items = NULL;
    PyObject *ret = NULL;

    if (!PyArg_ParseTuple(args, "OsO", &pipeline_wrapper, &element_name, &items)) goto end;

    pipeline = py_pipeline_unwrap(pipeline_wrapper);
    if (pipeline == NULL) {
        PyErr_SetString(PyExc_TypeError, "pipeline_unwrap");
        goto end;
    }

    factory = gst_element_factory_find(element_name);
    if (factory == NULL) {
        PyErr_SetString(PyExc_KeyError, element_name);
        goto end;
    }

    res = gst_element_factory_create(factory, NULL);

    Py_ssize_t n_items = PyList_Size(items);
    for (Py_ssize_t i=0; i < n_items; i++) {
        PyObject *item = PyList_GetItem(items, i);
        const char *k;
        PyObject *v;
        if (!PyArg_ParseTuple(item, "sO", &k, &v)) {
            goto end;
        }

        GValue gv = G_VALUE_INIT;
        if (!py_object_to_g_value(&gv, v)) goto end;
        g_object_set_property((GObject *) res, k, &gv);
    }

    if (!gst_bin_add((GstBin *) (pipeline->pipeline), res)) {
        PyErr_SetString(PyExc_RuntimeError, "could not add element to pipeline");
        goto end;
    }

    PyObject *py_el = python_gst_object_wrapper(element_ref_unsink(res));
    gchar *name = gst_element_get_name(res);
    PyObject *py_name = Py_None;
    if (name) {
        py_name = PyBytes_FromString(name);
        g_free(name);
    }
    
    ret = Py_BuildValue("(OO)", py_el, py_name);

end:
    return ret;

}

static PyObject *make_capsfilter(PyObject *self, PyObject *args) {

    const char *type;
    PyObject *params = NULL;
    PyObject *pipeline_wrapper = NULL;
    PyObject *ret = NULL;
    PyPipeline *pipeline;

    if (!PyArg_ParseTuple(args, "OsO", &pipeline_wrapper, &type, &params)) goto end;

    pipeline = py_pipeline_unwrap(pipeline_wrapper);
    if (!pipeline) goto end;

    GstElementFactory *factory = gst_element_factory_find("capsfilter");
    if (factory == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "could not construct capsfilter element");
        goto end;
    }

    GstElement *capsfilter = gst_element_factory_create(factory, NULL);

    GstCaps *caps = gst_caps_new_empty_simple(type);
    Py_ssize_t n_params = PyList_Size(params);
    for (Py_ssize_t i=0; i < n_params; i++) {
        PyObject *param = PyList_GetItem(params, i);
        const char *k;
        PyObject *v;
        if (!PyArg_ParseTuple(param, "sO", &k, &v)) {
            goto end;
        }

        GValue gv = G_VALUE_INIT;
        if (!py_object_to_g_value(&gv, v)) goto end;
        gst_caps_set_value(caps, k, &gv);
    }

    g_object_set((GObject *) capsfilter, "caps", caps, NULL);

    gst_bin_add((GstBin *) (pipeline->pipeline), capsfilter);

    ret = python_gst_object_wrapper(element_ref_unsink(capsfilter));

end:
    return ret;

}

static void link_deferred(GstElement *upstream, GstPad *upstream_pad, GstElement *downstream) {

    GstIterator *downstream_sink_pads = gst_element_iterate_sink_pads(downstream);
    GValue downstream_pad_container = G_VALUE_INIT;
    GstPad *downstream_pad;

    while(gst_iterator_next(downstream_sink_pads, &downstream_pad_container) == GST_ITERATOR_OK) {

        downstream_pad = g_value_get_object(&downstream_pad_container);
        if (gst_pad_can_link(upstream_pad, downstream_pad) && (gst_pad_link(upstream_pad, downstream_pad) == GST_PAD_LINK_OK)) {
            break;
        }
    }

    gst_iterator_free(downstream_sink_pads);

}

static PyObject *link_elements(PyObject *self, PyObject *args) {

    PyObject *py_upstream = NULL;
    PyObject *py_downstream = NULL;

    py_upstream = PyTuple_GetItem(args, 0);
    if (!py_upstream) goto end;
    py_downstream = PyTuple_GetItem(args, 1);
    if (!py_downstream) goto end;

    GstElement *upstream = python_gst_object_unwrap(py_upstream);
    if (!upstream) goto end;
    GstElement *downstream = python_gst_object_unwrap(py_downstream);
    if (!downstream) goto end;

    if (!gst_element_link(upstream, downstream)) {

        g_signal_connect(upstream, "pad-added", G_CALLBACK(link_deferred), downstream);        
    }

end:

    Py_RETURN_NONE;

}

static gboolean bus_watch(GstBus *bus, GstMessage *message, gpointer pipeline_p) {

   
#ifdef DEBUG_PRINTF
    printf("%s\n", gst_message_type_get_name(GST_MESSAGE_TYPE(message)));
#endif

    switch(message->type) {

        case GST_MESSAGE_EOS:
        case GST_MESSAGE_ERROR:
            BEGIN_PYTHON_THREAD
            const GstStructure *data = gst_message_get_structure(message);
            GstObject *src_object = message->src;
            PyObject *name = Py_None;
            if (src_object) {
                name = PyList_New(0);

                GstObject *cur_object = src_object;

                while (cur_object) {
                    gchar *gname = gst_object_get_name(cur_object);
                    if (gname) {
                        PyList_Append(name, PyBytes_FromString(gname));
                        g_free(gname);
                    } else {
                        break;
                    }
                    cur_object = gst_object_get_parent(cur_object);
                }

            }

            PyObject *pipeline_wrapper = (PyObject *) pipeline_p;
            PyPipeline *pipeline = py_pipeline_unwrap(pipeline_wrapper);

            if (message->type == GST_MESSAGE_ERROR && pipeline_exception_class) {
                GError *error;
                gst_message_parse_error(message, &error, NULL);
                pipeline->exc = PyObject_CallFunction(pipeline_exception_class,
                    "ss", error->message, gst_structure_get_string(data, "debug"));
                g_error_free(error);
            }

            if (pipeline->done_callback) {
                PyObject_CallFunction(pipeline->done_callback, "OO", pipeline->exc, name);
            }
            Py_DECREF(pipeline_wrapper);

            if (name != Py_None) Py_DECREF(name);

            END_PYTHON_THREAD
            
            gst_element_set_state((GstElement *) (pipeline->pipeline), GST_STATE_NULL);
            return 0;

        default:
            return 1;
    }

}

static gboolean state_check_timeout(gpointer vp) {

    PyObject *pipeline_wrapper = (PyObject *) vp;
    PyPipeline *pipeline = py_pipeline_unwrap(pipeline_wrapper);
    if (pipeline) {
        GstState cur_state;
        gst_element_get_state(
            (GstElement *) (pipeline->pipeline),
            &cur_state, NULL, 0);
        if (cur_state != GST_STATE_PLAYING && pipeline->done_callback) {
            BEGIN_PYTHON_THREAD

            PyObject *exc = PyObject_CallFunction(PyExc_RuntimeError, "s", "playing timed out");

            PyObject_CallOneArg(pipeline->done_callback, exc);           

            PyObject_CallFunction(pipeline->done_callback, "OO", exc, nil_tuple);

            END_PYTHON_THREAD
        }
    }

    Py_DECREF(pipeline_wrapper);

    return FALSE;

}

static PyObject *run_pipeline(PyObject *self, PyObject *args) {


    PyObject *pipeline_wrapper = PyTuple_GetItem(args, 0);
    if (pipeline_wrapper == NULL) return NULL;
    PyPipeline *pipeline = py_pipeline_unwrap(pipeline_wrapper);
    if (pipeline == NULL) return NULL;
    
    GstBus *bus = gst_pipeline_get_bus(pipeline->pipeline);
    Py_INCREF(pipeline_wrapper);
    gst_bus_add_watch(bus, bus_watch, pipeline_wrapper);

    if (gst_element_set_state((GstElement *) (pipeline->pipeline), GST_STATE_PLAYING) == \
        GST_STATE_CHANGE_FAILURE) {
        PyErr_SetString(PyExc_RuntimeError, "failed to play pipeline");
        return NULL;
    }

    Py_INCREF(pipeline_wrapper);
    g_timeout_add_seconds(2, state_check_timeout, pipeline_wrapper);

    Py_RETURN_NONE;

}

static GstBuffer *py_bytes_to_gst_buffer(PyObject *inp) {
    PyObject *bytes = PyBytes_FromObject(inp);
    char *data = PyBytes_AsString(bytes);
    size_t size = PyBytes_Size(bytes);

    GstBuffer *res = gst_buffer_new_memdup(data, size);

    Py_DECREF(bytes);

    return res;
}

static GstFlowReturn appsrc_iterator_callback(GstElement *appsrc, guint length, PyObject *iterator) {

#ifdef DEBUG_PRINTF
    printf("iterator callback\n");
#endif

    BEGIN_PYTHON_THREAD
    GstFlowReturn ret = GST_FLOW_OK;
    PyObject *next_value = NULL;

    if (!PyIter_Check(iterator)) {
#ifdef DEBUG_PRINTF
        printf("PyIter_Check fail\n");
#endif
        ret = GST_FLOW_ERROR;
        goto end;
    }

#ifdef DEBUG_PRINTF
    PyObject_Print(iterator, stdout, Py_PRINT_RAW);
    printf("\n");
#endif
    
    next_value = PyIter_Next(iterator);
    
    if (next_value == NULL) {
#ifdef DEBUG_PRINTF
        printf("iter end\n");
#endif

        if (PyErr_Occurred()) {
            PyErr_Print();
            ret = GST_FLOW_ERROR;
        } else {
            ret = GST_FLOW_EOS;
        }
        g_signal_emit_by_name(appsrc, "end-of-stream", &ret);
        Py_DECREF(iterator);
        goto end;
    }

    PyObject *py_data = NULL;
    uint64_t timestamp;
    uint64_t duration;
    uint64_t counter;
    if (!PyArg_ParseTuple(next_value, "OKKK", &py_data, &timestamp, &duration, &counter)) {
        ret = GST_FLOW_ERROR;
        goto end;
    }

    if (!PyBytes_Check(py_data)) {
        PyErr_SetNone(PyExc_TypeError);
        ret = GST_FLOW_ERROR;
        goto end;
    }

    GstBuffer *buf = py_bytes_to_gst_buffer(py_data);
    buf->dts = timestamp;
    buf->pts = timestamp;
    buf->duration = duration;
    buf->offset = counter;

#ifdef DEBUG_PRINTF
    printf("push buffer\n");
#endif

    g_signal_emit_by_name(appsrc, "push-buffer", buf, &ret);
    gst_buffer_unref(buf);

end:
    py_maybe_decref(next_value);

#ifdef DEBUG_PRINTF
    printf("ret %d\n", ret);
#endif

    if (PyErr_Occurred()) {
        PyErr_Print();
    }
    END_PYTHON_THREAD
    
    return ret;

}


static PyObject *make_iterator_source(PyObject *self, PyObject *args) {
    PyObject *pipeline_wrapper;
    PyObject *inp;
    PyObject *caps_props;

    if (!PyArg_ParseTuple(args, "OOO", &pipeline_wrapper, &inp, &caps_props)) return NULL;

    inp = PyObject_GetIter(inp);
    if (!inp) return NULL;

    PyPipeline *pipeline = py_pipeline_unwrap(pipeline_wrapper);
    if (!pipeline) return NULL;

    GstElementFactory *factory = gst_element_factory_find("appsrc");
    if (factory == NULL) {
        PyErr_SetString(PyExc_ImportError, "appsrc element cannot be found. something is wrong with your gstreamer installation");
        return NULL;
    }

    GstElement *appsrc = gst_element_factory_create(factory, NULL);
    if (appsrc == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "failed to construct appsrc");
        return NULL;
    }

    if (!gst_bin_add((GstBin *) (pipeline->pipeline), appsrc)) {
        PyErr_SetString(PyExc_RuntimeError, "failed to add appsrc to pipeline");
        gst_object_unref(appsrc);
        return NULL;
    }

    GstCaps *caps = gst_caps_new_simple("video/x-raw",
        "format", G_TYPE_STRING, "RGB",
        NULL);
    if (PyList_Check(caps_props)) {
        for (Py_ssize_t i=0; i < PyList_Size(caps_props); i++) {
            PyObject *row = PyList_GetItem(caps_props, i);
            char *k;
            PyObject *v;
            if (!PyArg_ParseTuple(row, "sO", &k, &v)) return NULL;
            GValue gv = G_VALUE_INIT;
            if (!py_object_to_g_value(&gv, v)) return NULL;
            gst_caps_set_value(caps, k, &gv);
        }
    }
    g_object_set((GObject *) appsrc, 
        "emit-signals", TRUE, 
        "caps", caps,
        NULL);
    gst_caps_unref(caps);

    g_signal_connect(appsrc, "need-data", G_CALLBACK(appsrc_iterator_callback), inp);

    return python_gst_object_wrapper(element_ref_unsink(appsrc));


}

static PyObject *gst_buffer_to_python(GstBuffer *buf) {

    size_t size = gst_buffer_get_size(buf);
    PyObject *py_buf = PyBytes_FromStringAndSize(NULL, size);
    if (!py_buf) return NULL;

    gst_buffer_extract(buf, 0, PyBytes_AsString(py_buf), size);

    return py_buf;
}


static PyObject *make_callback_sink(PyObject *self, PyObject *args) {

    PyObject *pipeline_wrapper = PyTuple_GetItem(args, 0);
    if (!pipeline_wrapper) return NULL;

    PyPipeline *pipeline = py_pipeline_unwrap(pipeline_wrapper);

    GstElementFactory *factory = gst_element_factory_find("appsink");
    if (factory == NULL) {
        PyErr_SetString(PyExc_ImportError, "appsink element cannot be found. something is wrong with your gstreamer installation");
        return NULL;
    }

    GstCaps *video_caps = gst_caps_new_simple("video/x-raw", 
        "format", G_TYPE_STRING, "RGB", NULL);

    GstElement *appsink = gst_element_factory_create(factory, NULL);
    if (appsink == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "failed to construct appsink");
        return NULL;
    }

    if (!gst_bin_add((GstBin *) (pipeline->pipeline), appsink)) {
        PyErr_SetString(PyExc_RuntimeError, "failed to add appsink to pipeline");
        return NULL;
    }

    g_object_set((GObject *) appsink, 
        "max-buffers", 1,
        "caps", video_caps,
        NULL);

    return python_gst_object_wrapper(element_ref_unsink(appsink));

}

static PyObject *appsink_pull_buffer(PyObject *self, PyObject *args) {

    PyObject *element_wrapper;
    guint64 timeout_interval;
    if (!PyArg_ParseTuple(args, "OK", &element_wrapper, &timeout_interval)) return NULL;

    GstElement *element = python_gst_object_unwrap(element_wrapper);

    GstSample *sample = NULL;
    Py_BEGIN_ALLOW_THREADS
    g_signal_emit_by_name(element, "try-pull-sample", timeout_interval, &sample);
    Py_END_ALLOW_THREADS

    if (sample == NULL) {
        gboolean is_eos;
        g_object_get((GObject *) element, "eos", &is_eos, NULL);
        if (is_eos) {
            Py_RETURN_NONE;
        } else {
            Py_RETURN_FALSE;
        }
    }

    GstBuffer *buf = gst_sample_get_buffer(sample);
    if (buf == NULL) {
        gst_sample_unref(sample);
        Py_RETURN_FALSE;
    }
    PyObject *py_buf = gst_buffer_to_python(buf);
    gst_sample_unref(sample);
   
    PyObject *res = Py_BuildValue("(Okk)", 
        py_buf,
        sample_get_width(sample),
        sample_get_height(sample));

    Py_DECREF(py_buf);

    return res;
    
}

// transform filter

G_BEGIN_DECLS

typedef struct _GstPythonFilter GstPythonFilter;
typedef struct _GstPythonFilterClass GstPythonFilterClass;

struct _GstPythonFilter {

    GstBaseTransform base_transform;

    PyObject *callback;
    GstCaps *sink_caps;
    GstCaps *src_caps;

};

struct _GstPythonFilterClass {

    GstBaseTransformClass parent_class;

};

GST_ELEMENT_REGISTER_DECLARE(pythonfilter);

G_END_DECLS

G_DEFINE_TYPE(GstPythonFilter, gst_python_filter, GST_TYPE_BASE_TRANSFORM);

static gboolean py_filter_accept_caps(GstBaseTransform *selfp, GstPadDirection direction, GstCaps *caps) {


    GstPythonFilter *self = (GstPythonFilter *) selfp;

    if (direction == GST_PAD_SRC) {

        return gst_caps_can_intersect(caps, self->sink_caps);

    } else if (direction == GST_PAD_SINK) {
        
        return gst_caps_can_intersect(caps, self->src_caps);

    } else {

        return FALSE;

    }

}

static GstFlowReturn py_filter_transform(GstBaseTransform *base, GstBuffer *buf_in, GstBuffer *buf_out) {


    GstPythonFilter *self = (GstPythonFilter *) base;

    GstPad *src_pad = GST_BASE_TRANSFORM_SRC_PAD(base);
    GstPad *sink_pad = GST_BASE_TRANSFORM_SINK_PAD(base);

    GstCaps *src_caps = gst_pad_get_current_caps(src_pad);
    GstCaps *sink_caps = gst_pad_get_current_caps(sink_pad);
    
    GstFlowReturn ret = GST_FLOW_ERROR;

    BEGIN_PYTHON_THREAD


    PyObject *src_caps_wrapper = py_wrap_caps(src_caps);
    PyObject *sink_caps_wrapper = py_wrap_caps(sink_caps);

    PyObject *py_in = gst_buffer_to_python(buf_in);

    PyObject *cb_res = PyObject_CallFunction(self->callback, "OOO",
        sink_caps_wrapper, src_caps_wrapper, py_in);

    if (cb_res == Py_False) {
        ret = GST_FLOW_EOS;
        goto end;
    }

    if (!cb_res || !PyBytes_Check(cb_res)) {
        ret = GST_FLOW_ERROR;
        goto end;
    }

    const char *res_data = PyBytes_AsString(cb_res);
    size_t res_size = PyBytes_Size(cb_res);
    
    gst_buffer_fill(buf_out, 0, res_data, res_size);
    ret = GST_FLOW_OK;



end:

    END_PYTHON_THREAD
    if (py_in) Py_DECREF(py_in);
    if (cb_res) Py_DECREF(cb_res);
    gst_caps_unref(src_caps);
    gst_caps_unref(sink_caps);
    return ret;
}

static void py_filter_finalize(GObject *gobject) {

    GstPythonFilter *f = (GstPythonFilter *) gobject;
    Py_DECREF(f->callback);
    gst_caps_unref(f->src_caps);
    gst_caps_unref(f->sink_caps);
    G_OBJECT_CLASS(gst_python_filter_parent_class)->finalize(gobject);

}

static void gst_python_filter_init(GstPythonFilter *self) {
    self->callback = NULL;
    self->sink_caps = NULL;
    self->src_caps = NULL;

}

static GstStaticPadTemplate python_src_template = 
    GST_STATIC_PAD_TEMPLATE(
        "src",
        GST_PAD_SRC,
        GST_PAD_ALWAYS,
        GST_STATIC_CAPS_ANY);
static GstStaticPadTemplate python_sink_template = 
    GST_STATIC_PAD_TEMPLATE(
        "sink",
        GST_PAD_SINK,
        GST_PAD_ALWAYS,
        GST_STATIC_CAPS_ANY);

static void gst_python_filter_class_init(GstPythonFilterClass *cls) {

    GObjectClass *gobject_class = (GObjectClass *) cls;
    GstElementClass *gst_element_class = (GstElementClass *) cls;
    GstBaseTransformClass *gst_transform_class = (GstBaseTransformClass *) cls;

    gobject_class->finalize = py_filter_finalize;

    gst_element_class_set_static_metadata(gst_element_class, "Python Filter",
        "Filter", 
        "Runs user-defined python code to transform things",
        "Bob Poekert <candyfloss@hella.cheap>");

    gst_transform_class->accept_caps = py_filter_accept_caps;
    gst_transform_class->transform = py_filter_transform;


    gst_element_class_add_static_pad_template(gst_element_class, &python_sink_template);
    gst_element_class_add_static_pad_template(gst_element_class, &python_src_template);

}

PyObject *make_callback_transform(PyObject *self, PyObject *args) {

    PyObject *pipeline_wrapper = NULL;
    PyObject *inp_caps_wrapper = NULL;
    PyObject *outp_caps_wrapper = NULL;
    PyObject *callback = NULL;
    const char *desired_name;

    if (!PyArg_ParseTuple(args, "OOOOs", 
        &pipeline_wrapper,
        &inp_caps_wrapper,
        &outp_caps_wrapper,
        &callback,
        &desired_name)) return NULL;

    PyPipeline *pipeline = py_pipeline_unwrap(pipeline_wrapper);
    if (!pipeline) return NULL;

    GstCaps *inp_caps = py_unwrap_caps(inp_caps_wrapper);
    if (!inp_caps) return NULL;
    GstCaps *outp_caps = py_unwrap_caps(outp_caps_wrapper);
    if (!outp_caps) return NULL;
    
    GstPythonFilter *el = (GstPythonFilter *) g_object_new(gst_python_filter_get_type(), NULL);
    el->callback = callback;
    gst_caps_ref(inp_caps);
    el->sink_caps = inp_caps;
    gst_caps_ref(outp_caps);
    el->src_caps = outp_caps;

    if (!gst_bin_add((GstBin *) (pipeline->pipeline), (GstElement *) el)) {
        PyErr_SetString(PyExc_RuntimeError, "failed to add filter to pipeline");
        return NULL;
    }
    
    Py_INCREF(callback);
    gst_object_ref(el);
    return python_gst_object_wrapper((GstElement *) el);

}

static PyObject *dot_viz(PyObject *self, PyObject *args) {

    PyObject *inp = PyTuple_GetItem(args, 0);
    if (inp == NULL) return NULL;

    PyPipeline *pipeline = py_pipeline_unwrap(inp);
    gchar *data = gst_debug_bin_to_dot_data((GstBin *) (pipeline->pipeline), 
        GST_DEBUG_GRAPH_SHOW_ALL);

    PyObject *res = PyBytes_FromString(data);
    g_free(data);
    return res;

}

static PyObject *set_pipeline_exception_class(PyObject *self, PyObject *args) {

    PyObject *cls = PyTuple_GetItem(args, 0);
    if (!cls) return NULL;

    pipeline_exception_class = cls;
    
    Py_RETURN_NONE;

}

static PyObject *stop_pipeline(PyObject *self, PyObject *args) {

    PyObject *pipeline_wrapper = PyTuple_GetItem(args, 0);
    if (!pipeline_wrapper) return NULL;
    PyPipeline *pipeline = py_pipeline_unwrap(pipeline_wrapper);
    if (!pipeline) return NULL;

    gst_element_set_state((GstElement *) (pipeline->pipeline), GST_STATE_NULL);

    Py_RETURN_NONE;

}


static PyObject *py_make_caps(PyObject *self, PyObject *args) {

    const char *caps_name;
    PyObject *props_list;

    if (!PyArg_ParseTuple(args, "sO", &caps_name, &props_list)) return NULL;

    GstCaps *res = gst_caps_new_empty_simple(caps_name);
    size_t n_props = PyList_Size(props_list);
    for (size_t i=0; i < n_props; i++) {
        PyObject *pair = PyList_GetItem(props_list, i);

        const char *key;
        PyObject *value;

        if (!PyArg_ParseTuple(pair, "sO", &key, &value)) return NULL;

        GValue gv = G_VALUE_INIT;
        py_object_to_g_value(&gv, value);

        gst_caps_set_value(res, key, &gv);

    }

    return py_wrap_caps(res);

}

PyObject *py_caps_get_prop(PyObject *self, PyObject *args) {

    PyObject *caps_wrapper;
    const char *key;
    PyObject *res = NULL;

    if (!PyArg_ParseTuple(args, "Os", &caps_wrapper, &key)) return NULL;

    GstCaps *caps = py_unwrap_caps(caps_wrapper);
    if (!caps) return NULL;

    size_t n_structures = gst_caps_get_size(caps);
    for (size_t si=0; si < n_structures; si++) {

        GstStructure *st = gst_caps_get_structure(caps, si);
        if (gst_structure_has_field(st, key)) {

            const GValue *value = gst_structure_get_value(st, key);
            res = py_object_from_g_value(value, gst_structure_get_field_type(st, key));
            break;

        }

    }


    return res;


}

static PyObject *py_caps_is_compatible(PyObject *self, PyObject *args) {

    PyObject *py_a;
    PyObject *py_b;

    if (!PyArg_ParseTuple(args, "OO", &py_a, &py_b)) return NULL;

    GstCaps *caps_a = py_unwrap_caps(py_a);
    if (!caps_a) return NULL;

    GstCaps *caps_b = py_unwrap_caps(py_b);
    if (!caps_b) return NULL;

    if (gst_caps_can_intersect(caps_a, caps_b)) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }

}


static PyObject *py_caps_to_list(PyObject *self, PyObject *args) {

    PyObject *caps_wrapper = PyTuple_GetItem(args, 0);
    if (!caps_wrapper) return NULL;

    GstCaps *caps = py_unwrap_caps(caps_wrapper);
    if (!caps) return NULL;

    PyObject *res = PyList_New(1);
    
    char *media_type = NULL;

    size_t n_structures = gst_caps_get_size(caps);
    for (size_t si=0; si < n_structures; si++) {

        const GstStructure *s = gst_caps_get_structure(caps, si);

        media_type = (char *) gst_structure_get_name(s);
    
        size_t n_fields = gst_structure_n_fields(s);

        for (size_t ki=0; ki < n_fields; ki++) {

            const gchar *k = gst_structure_nth_field_name(s, ki);
            const GValue *v = gst_structure_get_value(s, k);
            GType typ = gst_structure_get_field_type(s, k);

            PyObject *pair = PyTuple_New(2);
            PyTuple_SetItem(pair, 0, PyBytes_FromString(k));
            PyTuple_SetItem(pair, 1, py_object_from_g_value(v, typ));

            PyList_Append(res, pair);

        }

    }

    if (media_type) {
        PyList_SetItem(res, 0, PyBytes_FromString(media_type));
    } else {
        PyList_SetItem(res, 0, Py_None);
    }

    return res;

}

static PyObject *py_caps_union(PyObject *self, PyObject *args) {

    PyObject *wrapper_a = NULL;
    PyObject *wrapper_b = NULL;

    if (!PyArg_ParseTuple(args, "OO", &wrapper_a, &wrapper_b)) return NULL;

    GstCaps *caps_a = py_unwrap_caps(wrapper_a);
    if (!caps_a) return NULL;

    GstCaps *caps_b = py_unwrap_caps(wrapper_b);
    if (!caps_b) return NULL;

    GstCaps *caps_res = gst_caps_new_empty();
    gst_caps_append(caps_res, caps_a);
    gst_caps_append(caps_res, caps_b);

    return py_wrap_caps(caps_res);

}

static PyMethodDef py_entrypoint_methods[] = {

    {"make_pipeline", make_pipeline, METH_VARARGS,
        "Construct an empty gstreamer pipeline"},
    {"construct_element", construct_element, METH_VARARGS,
        "Construct an element with a given name and a given set of properties"},
    {"remove_element", remove_element, METH_VARARGS,
        "Remove the given element from the given pipeline"},
    {"link_elements", link_elements, METH_VARARGS,
        "Link two elements together"},
    {"run_pipeline", run_pipeline, METH_VARARGS,
        "Run the given pipeline. Will block until the pipeline finishes (EOS or and error)"},
    {"make_capsfilter", make_capsfilter, METH_VARARGS,
        "Constructs a capsfilter element with the given type and parameters"},
    {"dot_viz", dot_viz, METH_VARARGS,
        "Return a graphviz dot representation of the given pipeline"},
    {"set_exception_class", set_pipeline_exception_class, METH_VARARGS,
        "Sets the class that pipeline exceptions are constructed from"},
    {"stop_pipeline", stop_pipeline, METH_VARARGS,
        "Stop the given pipeline"},

    {"make_caps", py_make_caps, METH_VARARGS, "make caps"},
    {"caps_get_prop", py_caps_get_prop, METH_VARARGS, "get prop from caps"},
    {"caps_is_compatible", py_caps_is_compatible, METH_VARARGS, "are two capses compatible"},
    {"caps_to_list", py_caps_to_list, METH_VARARGS, "list of props of caps"},
    {"caps_union", py_caps_union, METH_VARARGS, "returns the union of caps a and b"},
    
    {"make_iterator_source", make_iterator_source, METH_VARARGS,
        "Construct a source element that consumes frames from a given iterator"},
    {"make_callback_sink", make_callback_sink, METH_VARARGS,
        "Construct a sink element that calls a given callback with new buffers"},
    {"make_callback_transform", make_callback_transform, METH_VARARGS,
        "Construct a transform element that maps the given callback over the pipeline"},
    {"appsink_pull_buffer", appsink_pull_buffer, METH_VARARGS,
        "Pull a buffer from the internal queue of the given appsink element (blocks)"},

    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef py_entrypoint = {
    .m_methods = py_entrypoint_methods,
};

PyMODINIT_FUNC PyInit_c_candyfloss(void) {
    nil_tuple = PyTuple_New(0);
    Py_INCREF(nil_tuple);
    start_gevent_thread();
    gst_init(NULL, NULL);
    return PyModuleDef_Init(&py_entrypoint);
}
