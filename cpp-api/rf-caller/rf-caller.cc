#include "python2.7/Python.h"

#include <stdio.h>
#include <cstdio>
#include <string>
#include <iostream>
#include <vector>

using namespace std;

PyObject* CreateList(const vector<double>& vec_input) {
    // Create Python list according to vector<double> input.
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
// Testing API.
bool Testing(const vector<double>& raw_signal, vector<pair<int, string>>* output, const string& project_home_path, const string& model_path) {

    Py_Initialize();
    // Add relative path to sys to import module from current path.
    PyRun_SimpleString("import sys"); 
    
    // import module
    string str_module_path = "sys.path.append('" + project_home_path + "')";
    PyRun_SimpleString(str_module_path.c_str());

    // my own function.
    PyObject* param_list = CreateList(vector<double>(700,2.34));

    PyObject *pModule, *pFunc, *pValue;
    pModule = PyImport_ImportModule("RFclassifier.ClassificationLearner_API");

    pFunc = PyObject_GetAttrString(pModule, "Testing");

    if(pFunc && PyCallable_Check(pFunc))
    {
        //Set model path for python testing function to load.
        PyObject* Py_model_path = PyString_FromString(model_path.c_str());

        PyObject* params = PyTuple_New(2);
        PyTuple_SetItem(params, 0, param_list);
        PyTuple_SetItem(params, 1, Py_model_path);

        PyObject* pValue = PyObject_CallObject(pFunc, params);

        //PyObject_Print(pValue, stdout, Py_PRINT_RAW);
        if (!pValue) {
            Py_Finalize();
            return false;
        }
        
        // debug
        //PyObject_Print(pValue, stdout, Py_PRINT_RAW);
        int result_size = PyList_Size(pValue);
        for (int i = 0; i < result_size; ++i) {
            PyObject* cur_pair = PyList_GetItem(pValue, i);
            PyObject* Py_pos = PyTuple_GetItem(cur_pair, 0);
            PyObject* Py_label = PyTuple_GetItem(cur_pair, 1);
            int pos = PyInt_AsSsize_t(Py_pos);
            char* label = PyString_AsString(Py_label);
            string result_label(label);
            // Write to output.
            output->push_back(make_pair(pos,result_label));
        }
    } else cout << "Error: cannot find function Testing." << endl;

    Py_Finalize();
    return true;
}

int main()
{

    vector<pair<int, string>> output;
    string project_home_path = "/home/alex/LabGit/ProjectSwiper";
    string save_modle_path = "/home/alex/LabGit/ProjectSwiper/result/test-api";

    Testing(vector<double>(1000,9.3), &output, project_home_path, save_modle_path);
    cout << "size : " << output.size() << endl;
    return 0;
}
