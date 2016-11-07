#include "python2.7/Python.h"

#include "kpd_api.h"
#include "KPD.h"

#include <iostream>
#include <cstdlib>
#include <ctime>

using namespace std;

string wavelet_api_file_path = "/home/alex/code/matlab/KPD/wavelet-cpp/";

PyObject* CreateList(const vector<double>& vec_input) {
    // Create Python list according to vector<T> input.
    // Note: caller have to call Py_DECREF() to free the resources on heap.
    if (vec_input.empty())return NULL;
    PyObject* ret = PyList_New(vec_input.size());
    for (int i = 0; i < vec_input.size(); ++i) {
        PyObject* py_value = PyFloat_FromDouble(vec_input[i]);
        PyList_SetItem(ret, i, py_value);
    }
    // debug
    //PyObject_Print(ret, stdout, Py_PRINT_RAW);
    return ret;
}

PyObject* CreateList_int32(const vector<int>& vec_input) {
    // Create Python list according to vector<T> input.
    // Note: caller have to call Py_DECREF() to free the resources on heap.
    if (vec_input.empty())return NULL;
    PyObject* ret = PyList_New(vec_input.size());
    for (int i = 0; i < vec_input.size(); ++i) {
        PyObject* py_value = PyInt_FromLong(vec_input[i]);
        PyList_SetItem(ret, i, py_value);
    }
    // debug
    //PyObject_Print(ret, stdout, Py_PRINT_RAW);
    return ret;
}


PyObject* GetWaveletObject_Simple(const vector<double>& low_dec,
        const vector<double>& high_dec,
        const vector<double>& low_rec,
        const vector<double>& high_rec,
        string wavelet_name = string("my_wt")) {

    // Create pyWavelet object.
    PyObject* pFunc_wavelet = PyImport_ReloadModule(PyString_FromString("pywt.Wavelet"));
    
    if(!pFunc_wavelet || !PyCallable_Check(pFunc_wavelet)) {
        cout << "ERROR: imported pywt.Wavelet not callable" << endl;
    }
    cout << "imported pywt.Wavelet." << endl;

    // Warning: mem leak?
    PyObject* py_filter_banks = PyTuple_New(4);
    PyTuple_SetItem(py_filter_banks, 0, CreateList(low_dec));
    PyTuple_SetItem(py_filter_banks, 1, CreateList(high_dec));
    PyTuple_SetItem(py_filter_banks, 2, CreateList(low_rec));
    PyTuple_SetItem(py_filter_banks, 3, CreateList(high_rec));

    // Wavelet function parameter.
    PyObject* py_wavelet_parameters = PyTuple_New(2);
    PyObject* py_wavelet_name = PyString_FromString(wavelet_name.c_str());
    PyTuple_SetItem(py_wavelet_parameters, 0, py_wavelet_name);
    PyTuple_SetItem(py_wavelet_parameters, 1, py_filter_banks);

    cout << "calcing: wt_obj" << endl;
    PyObject* wt_obj = PyObject_CallObject(pFunc_wavelet, py_wavelet_parameters);

    cout << "returning wt_obj" << endl;
    return wt_obj;
}

PyObject* GetWaveletObject(const vector<double>& low_dec,
        const vector<double>& high_dec,
        const vector<double>& low_rec,
        const vector<double>& high_rec,
        string wavelet_name = string("my_wt")) {

    // Create pyWavelet object.
    PyObject* pFunc_wavelet = PyImport_ReloadModule(PyString_FromString("pywt.Wavelet"));
    
    if(!pFunc_wavelet || !PyCallable_Check(pFunc_wavelet)) {
        cout << "ERROR: imported pywt.Wavelet not callable" << endl;
    }
    cout << "imported pywt.Wavelet." << endl;

    // Warning: mem leak?
    PyObject* py_filter_banks = PyTuple_New(4);
    PyTuple_SetItem(py_filter_banks, 0, CreateList(low_dec));
    PyTuple_SetItem(py_filter_banks, 1, CreateList(high_dec));
    PyTuple_SetItem(py_filter_banks, 2, CreateList(low_rec));
    PyTuple_SetItem(py_filter_banks, 3, CreateList(high_rec));

    // Wavelet function parameter.
    PyObject* py_wavelet_parameters = PyTuple_New(2);
    PyObject* py_wavelet_name = PyString_FromString(wavelet_name.c_str());
    PyTuple_SetItem(py_wavelet_parameters, 0, py_wavelet_name);
    PyTuple_SetItem(py_wavelet_parameters, 1, py_filter_banks);

    cout << "[wt_obj]" << endl;
    //PyObject* wt_obj = PyObject_CallObject(pFunc_wavelet, py_wavelet_parameters);
    PyObject* wt_obj = PyInstance_New(pFunc_wavelet, py_wavelet_parameters, nullptr);

    cout << "returning wt_obj" << endl;
    return wt_obj;
}

PyObject* ArrayToList(PyObject* array_in) {
    // Convert Python numpy.array object to list object.
    // create dict of array_in
    PyObject* locals = PyDict_New();
    PyObject* globals = PyDict_New();
    PyDict_SetItemString(globals, "__builtins__", PyEval_GetBuiltins());

    PyDict_SetItemString(locals, "array_in", array_in);
    PyObject* output = PyRun_String("list(array_in)",
            Py_eval_input,
            globals,
            locals);
    auto* list_obj = PyList_New(2);
    return output;
}

void FormatWavedecOutput(PyObject* dec_result,
        vector<double>* sig_out,
        vector<int>* coef_length_vec) {
    // Reorder dec_result into sig_out & coef_length_vec
    sig_out->clear();
    coef_length_vec->clear();
    int result_size = PyList_Size(dec_result);

    for (int i = 0; i < result_size; ++i) {
        //Py_ssize_t py_ind = PyInt_AsSsize_t(PyInt_FromLong(i));
        PyObject* cur_layer_array = PyList_GetItem(dec_result, i);
        PyObject* cur_layer = ArrayToList(cur_layer_array);

        auto layer_length = PyList_Size(cur_layer);
        coef_length_vec->push_back(layer_length);
        for (int j = 0; j < layer_length; ++j) {
            int val = PyInt_AsLong(PyList_GetItem(cur_layer, j));
            sig_out->push_back(val);
        }
    }
    return;
}

void FormatWaverecOutput(PyObject* rec_result,
        vector<double>* sig_out) {
    // Reorder dec_result into sig_out & coef_length_vec
    sig_out->clear();
    PyObject* py_result_list = ArrayToList(rec_result);
    int result_size = PyList_Size(py_result_list);

    for (int i = 0; i < result_size; ++i) {
        //Py_ssize_t py_ind = PyInt_AsSsize_t(PyInt_FromLong(i));
        auto* py_val = PyList_GetItem(py_result_list, i);
        double val = PyFloat_AsDouble(py_val);
        sig_out->push_back(val);
    }
    return;
}

PyObject* GetCoefList(const vector<double>& C,
        const vector<int>& L) {
    int coef_length = 0;
    for (const auto&val : L) coef_length += val;

    int layer_size = L.size();
    PyObject* py_coef_list = PyList_New(layer_size);

    int cnt = 0;
    for (int i = 0; i < layer_size; ++i) {
        int layer_coef_length = L[i];
        PyObject* py_layer_list = PyList_New(layer_coef_length);
        for (int j = 0; j < layer_coef_length; ++j) {
            double val = C[cnt];
            PyObject* py_value = PyFloat_FromDouble(val);
            PyList_SetItem(py_layer_list, j, py_value);
            ++cnt;
        }
        PyList_SetItem(py_coef_list, i, py_layer_list);
    }
    return py_coef_list;
}

/*
 * Convert Python objects to vector<vector<double>> type.
 */
void FormatDtcwtOutput(PyObject* py_s_rec,
        vector<vector<double>>* s_rec) {

    int result_size = PyList_Size(py_s_rec);
    for (int i = 0; i < result_size; ++i) {
        PyObject* cur_layer_list = PyList_GetItem(py_s_rec, i);

        int layer_length = PyList_Size(cur_layer_list);
        //cout << "layer[" << i << "] length= " << layer_length << endl;
        
        vector<double> layer_double;
        for (int j = 0; j < layer_length; ++j) {

            PyObject* py_value= PyList_GetItem(cur_layer_list, j);
            double val_double = PyFloat_AsDouble(py_value);

            layer_double.push_back(val_double);
        }
        s_rec->push_back(layer_double);
    }
    return;
}

void DTCWT(const vector<double>& sig_in,
        int dwt_level,
        vector<vector<double>>* s_rec) {
    // This function will call python module
    Py_Initialize();

    s_rec->clear();

    PyRun_SimpleString("import sys"); 
    // import module
    string wavelet_api_file_path =
        "/home/alex/LabGit/ProjectSwiper/other_tasks/call_simple_function/";
    string str_module_path =
        "sys.path.append('" + wavelet_api_file_path + "')";
    PyRun_SimpleString(str_module_path.c_str());

    PyObject* pModule = PyImport_ImportModule("wavelet_api");
    
    if (!pModule) {
        PyErr_Print();
        cout << "Import DTCWT module failed!" << endl;
        return ;
    }

    PyObject* pFunc = PyObject_GetAttrString(pModule, "DTCWT_API");

    if(pFunc && PyCallable_Check(pFunc))
    {
        // Default mode for pywt.wavedec
        PyObject* params = PyTuple_New(3);
        PyTuple_SetItem(params, 0, CreateList(sig_in));
        PyTuple_SetItem(params, 1, PyInt_FromLong(dwt_level));

        // Num_Subbands
        vector<int> Num_Subbands;
        for (int i = 1; i <= dwt_level; ++i) Num_Subbands.push_back(i);
        PyTuple_SetItem(params, 2, CreateList_int32(Num_Subbands));

        // Call Python Function.
        PyObject* pValue = PyObject_CallObject(pFunc, params);

        if (!pValue) {
            PyErr_Print();
            return ;
        }
        
        // debug
        int result_size = PyList_Size(pValue);
        //cout << "result_size = " << result_size << endl;

        // Set return values
        FormatDtcwtOutput(pValue, s_rec);
    } else cout << "Error: cannot find function Testing." << endl;
    return;
}

void Testing(vector<double> sig_in, vector<pair<char, int>>* result_out) {
    int sig_len = sig_in.size();
    vector<vector<double>> s_rec;

    DTCWT(sig_in, 9, &s_rec);

    KPD(s_rec, sig_len, 360.0, result_out);
}

// TEST CASES
void TEST1() {
     vector<double> sig_in;
     int n = 10000;
     for (int i = 0; i < n; ++i) sig_in.push_back((5566 % 10000) / 5000.0);
     vector<pair<char, int>> res;
     Testing(sig_in, &res);
     cout << "res size = "
          << res.size() << endl;
}

void GenSignal(int n, vector<double>* sig_out) {
     for (int i = 0; i < n; ++i) sig_out->push_back((rand() % 10000) / 10000.0);
}

int main(int argc, char** argv)
{
    Py_Initialize();
    PySys_SetArgv(argc, argv);

    srand(time(NULL));
    TEST1();

    Py_Finalize();
    return 0;
}

