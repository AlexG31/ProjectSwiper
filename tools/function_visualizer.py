#encoding:utf8
import os
import re


class FunctionVisualizer(object):
    '''This funciton visualizes the heirarchy of a py file.'''
    def __init__(self, fin):
        '''input file object.'''
        self.fin = fin
        # re pattern
        self.function_pattern = re.compile(r'^([ \t]*)def ([_a-zA-Z]+)\(')
        self.class_pattern = re.compile(r'^([ \t]*)class ([a-zA-Z]+)')
        
    def GetFunctionList(self):
        '''
        Return:(default empty list)
            [[function_name, front_tab_count],
             ...,
             []
            ]
        '''
        fin = self.fin
        # Reset file pointer
        fin.seek(0)
        
        result_list = []

        for line in fin:
            res = self.FindObjectName(line)
            if res is not None:
                result_list.append(res)

        return result_list
            
    def FindObjectName(self, line):
        '''Match class and functions.'''
        # Functions
        res = self.function_pattern.match(line)
        if res is not None:
            indent_level = len(res.group(1))
            function_name = res.group(2)
            return (indent_level, function_name)

        res = self.class_pattern.match(line)
        if res is not None:
            indent_level = len(res.group(1))
            function_name = res.group(2)
            return (indent_level, 'class ' + function_name)
        return None

    def Visualize(self):
        '''Visualize.'''
        result_list = self.GetFunctionList()
        for indent_count, name in result_list:
            print ' ' * indent_count,
            print name
        
        return None


def Test1():
    with open("./test.py", "r") as fin:
        fv_obj = FunctionVisualizer(fin)
        fv_obj.Visualize()
if __name__ == '__main__':
    Test1()

