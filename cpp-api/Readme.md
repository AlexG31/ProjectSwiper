# ECG random forest classifier c++ api

## 1. How to compile

First make sure you've installed python2.7.
The use python-config to get nessassery include & link parameters for g++.

For example, in my computer, this works:


```
   g++ rf-caller.cc -L/usr/lib/python2.7/config-x86_64-linux-gnu -L/usr/lib -lpython2.7 -lpthread -ldl  -lutil -lm  -Xlinker -export-dynamic -Wl,-O1 -std=c++11  -o caller && ./caller     
```

## 2. How to use API

Simply call the Testing function, also set the path of the home dir of the python project & path of the trained model.
