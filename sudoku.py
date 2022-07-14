import numpy as np

symbols=[k for k in range(1,10)]
block_ids=list(range(9))

class Sudoku:
    def __init__(self,data_list=None):
        c=np.zeros([9,9],np.int)
        if not (data_list is None):
            for i in range(len(data_list)):
                if data_list[i][0]!='$':
                    offset=0
                    s_current=data_list[i]
                else:
                    offset=int(data_list[i][1])
                    s_current=data_list[i][2:]
                for j in range(len(s_current)):
                    if s_current[j]>'0':
                        c[i,j+offset]=int(s_current[j])
        self.c=c
    def set(self,a):
        if len(a.shape)==1:
            self.c=np.copy(a).reshape(9,9)
        else:
            self.c==np.copy(a)
    def __getitem__(self,i):
        return self.c[i[0],i[1]]
    def __str__(self):
        s=str(self.c)
        return s

if __name__=='__main__':
    from predef import *
    s=Sudoku(sod3)
    print(s)
    print(s[0,1])