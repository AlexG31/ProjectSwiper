g++ -std=c++11 \
    KPD.cc KPD.h\
    abs.c                              gaussian_function.c\
    call_simple_function.c             mean.c\
    call_simple_function_data.c        power.c\
    call_simple_function_emxAPI.c      QRS_detection.c\
    call_simple_function_emxutil.c     rand.c\
    call_simple_function_initialize.c  rdivide.c\
    call_simple_function_terminate.c   rtGetInf.c\
    eml_rand.c                         rtGetNaN.c\
    eml_rand_mcg16807_stateful.c       rt_nonfinite.c\
    eml_rand_mt19937ar_stateful.c      simple_function.c\
    eml_rand_shr3cong_stateful.c       sum.c\
    eml_sort.c                         T_detection.c\
    floor.c\
    kpd_api.cc kpd_api.h \
    -L/usr/lib/python2.7/config-x86_64-linux-gnu -L/usr/lib -lpython2.7 \
    -lpthread -ldl  -lutil -lm  -Xlinker -export-dynamic -Wl,-O1 \
    -o caller 
