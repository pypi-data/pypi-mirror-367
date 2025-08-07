#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define PY_SSIZE_T_CLEAN
#include <Python.h>

typedef struct {
    FILE* file;
} quickv;

quickv* opendb(const char* filename);
int quickv_set(quickv* db, const char* key, const char* value);
const char* quickv_get(quickv* db, const char* key);
void closedb(quickv* db);

void closedb(quickv* db) {
    fclose(db->file);
    free(db);
}

quickv* opendb(const char* filename) {
    FILE* file = fopen(filename, "r+b");

    if (!file) {
        file = fopen(filename, "wb");
        if (!file) return NULL;

        unsigned char byte = 0xFF;
        fwrite(&byte, 1, 1, file);
        fclose(file);

        file = fopen(filename, "r+b");
        if (!file) return NULL;
    }

    quickv* db = malloc(sizeof(quickv));
    db->file = file;

    return db;
}

int quickv_set(quickv* db, const char* key, const char *value) {
    if (!db || !key || !value) return -1;

    FILE* file = db->file;

    fseek(file, 0, SEEK_SET);

    while (fgetc(file) != 0xFF) {}

    fseek(file, -1, SEEK_CUR);
    long start = ftell(file);
    fseek(file, 0, SEEK_END);
    long end = ftell(file);

    size_t size = (size_t)(end - start);

    unsigned char* buffer = malloc(size);

    fseek(file, start, SEEK_SET);

    fread(buffer, 1, size, file);

    fseek(file, start, SEEK_SET);

    fwrite(key, 1, strlen(key), file);
    char null_byte = '\0';
    fwrite(&null_byte, 1, 1, file);
    uint64_t offset = ftell(file) + size + sizeof(uint64_t);
    fwrite(&offset, 1, sizeof(uint64_t), file);

    fwrite(buffer, 1, size, file);
    free(buffer);

    fwrite(value, 1, strlen(value), file);
    fwrite(&null_byte, 1, 1, file);

    fflush(file);

    return 0;

}

const char* quickv_get(quickv* db, const char* key) {
    if (!db || !key) return NULL;
    FILE* file = db->file;
    fseek(file, 0, SEEK_SET);

    size_t target_len = strlen(key);

    int byte;
    while((byte = fgetc(file)) != EOF) {
        unsigned char c = (unsigned char)byte;
        if (c == 0xFF) return NULL;
        else if (c == 0x00) fseek(file, 8, SEEK_CUR);

        if (c == key[0]) {
            int matched = 1;
            for (size_t i = 1; i < target_len; i++) {
                int next_byte = fgetc(file);
                if ((unsigned char)next_byte != (unsigned char)key[i]) {
                    matched = 0;
                    break;
                }
            }
            if (matched) {
                fseek(file, 1, SEEK_CUR);
                uint64_t offset;
                fread(&offset, sizeof(uint64_t), 1, file);
                fseek(file, (long)offset, SEEK_SET);

                static char buffer[1024];
                size_t i = 0;
                int ch;
                while (i < sizeof(buffer) - 1 && (ch = fgetc(file)) != EOF && ch != '\0') {
                    buffer[i++] = (char)ch;
                }
                buffer[i] = '\0';

                return buffer;
            }
        }


    }
return NULL;
}

/*int main() {
    quickv* db = opendb("");
    //quickv_set(db, "key", "value");
    printf("%s\n", quickv_get(db, "key"));
}*/

typedef struct {
    PyObject_HEAD
    quickv* db;
} PyQuicKVObject;

static void PyQuicKV_dealloc(PyQuicKVObject* self) {
    if (self->db) {
        closedb(self->db);
        self->db = NULL;
    }
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static int PyQuicKV_init(PyQuicKVObject* self, PyObject* args, PyObject* kwds) {
    const char* filename;
    if (!PyArg_ParseTuple(args, "s", &filename))
        return -1;

    self->db = opendb(filename);
    if (!self->db) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to open database");
        return -1;
    }

    return 0;
}

static PyObject* PyQuicKV_set(PyQuicKVObject* self, PyObject* args) {
    const char* key;
    const char* value;
    if (!PyArg_ParseTuple(args, "ss", &key, &value))
        return NULL;

    int res = quickv_set(self->db, key, value);
    if (res != 0) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to set key");
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject* PyQuicKV_get(PyQuicKVObject* self, PyObject* args) {
    const char* key;
    if (!PyArg_ParseTuple(args, "s", &key))
        return NULL;

    const char* value = quickv_get(self->db, key);
    if (!value) {
        Py_RETURN_NONE;
    }

    return Py_BuildValue("s", value);
}

static PyMethodDef PyQuicKV_methods[] = {
    {"set", (PyCFunction)PyQuicKV_set, METH_VARARGS, "Set a key-value pair"},
    {"get", (PyCFunction)PyQuicKV_get, METH_VARARGS, "Get value by key"},
    {NULL, NULL, 0, NULL}
};

static PyTypeObject PyQuicKVType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "quickv.DB",
    .tp_doc = "QuicKV database object",
    .tp_basicsize = sizeof(PyQuicKVObject),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)PyQuicKV_init,
    .tp_dealloc = (destructor)PyQuicKV_dealloc,
    .tp_methods = PyQuicKV_methods,
};

static PyMethodDef quickv_methods[] = {
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef quickvmodule = {
    PyModuleDef_HEAD_INIT,
    "quickv",
    "QuicKV key-value store module",
    -1,
    quickv_methods
};

PyMODINIT_FUNC PyInit_quickv(void) {
    PyObject* m;
    if (PyType_Ready(&PyQuicKVType) < 0)
        return NULL;

    m = PyModule_Create(&quickvmodule);
    if (m == NULL)
        return NULL;

    Py_INCREF(&PyQuicKVType);
    if (PyModule_AddObject(m, "DB", (PyObject*)&PyQuicKVType) < 0) {
        Py_DECREF(&PyQuicKVType);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}
