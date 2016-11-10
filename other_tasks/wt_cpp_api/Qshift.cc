/* Include files */
#include <math.h>
#include <vector>
#include <iostream>
#include <complex>

#include "Qshift.h"

using std::vector;
using std::complex;

using std::cout;
using std::endl;

/* Function Declarations */

#define PI 3.14159265358979323846

typedef complex<double> ComplexDouble;

inline int ToCIndex(int index) {
    return index - 1;
}

inline ComplexDouble GetPower_Negtive_1(double index) {
    // Complex number of form a + bi;
    double a = cos(index * PI);
    double b = sin(index * PI);
    return ComplexDouble(a, b);
}

void Qshift(vector<double>& HL, vector<vector<ComplexDouble>>* ret) {
    
    int L = HL.size();
    vector<ComplexDouble> Coef_HL, H00a, H01a, H10a, H11a, H00b, H01b, H10b, H11b;
    // Init
    H11a = vector<ComplexDouble>(L, ComplexDouble(0, 0));
    H11b = vector<ComplexDouble>(L, ComplexDouble(0, 0));

    for (int ii = L; ii >= 1; --ii) {
        Coef_HL.push_back(ceil(L / 2) + 1 - ii);
    }

    for (int ii = 1; ii <= L; ++ii) {

        H00a.push_back(HL[ToCIndex(L+1-ii)]);
        
        H01a.push_back(
                GetPower_Negtive_1(Coef_HL[ToCIndex(ii)].real()) *
                     HL[ToCIndex(ii)]);
        
        H00b.push_back(HL[ToCIndex(ii)]);
        
        H01b.push_back(
                GetPower_Negtive_1(Coef_HL[ToCIndex(L+1-ii)].real()) *
                    HL[ToCIndex(L+1-ii)]);
        
        H10a.push_back(HL[ToCIndex(ii)]);
        
        H11a[ToCIndex(L+1-ii)]=H01a[ToCIndex(ii)];
        
        H10b.push_back(HL[ToCIndex(L+1-ii)]);
        
        H11b[ToCIndex(L+1-ii)]=H01b[ToCIndex(ii)];
    }
    *ret = vector<vector<ComplexDouble>>{H00a, H01a, H10a, H11a, H00b, H01b, H10b, H11b};
    return;
}


void Test1() {

    //vector<double> HL{1.43,2.2,3,3.4,2.5,3.4,5.2,2.23,4.1,2.4,5.3,6.1};
    vector<double> HL{0.03516384,0,-0.08832942,
        0.23389032,0.76027237,0.58751830,
        0,-0.11430184,0,0};
    vector<vector<ComplexDouble>> ret;
    Qshift(HL, &ret);

    cout << "ret.size = " << ret.size() << endl;
    for (const auto& vec: ret) {
        cout << "vec.size = " << vec.size() << endl;
        for (const auto& val : vec) {
            cout << val << ", ";
        }
        cout << endl;
    }
}

