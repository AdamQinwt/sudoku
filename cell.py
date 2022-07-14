import numpy as np

symbols=[k for k in range(1,10)]
block_ids=list(range(9))

class Cell:
    def __init__(self):
        self.row=0
        self.col=0
        self.square=0
        self.v=0
        self.possible={k:True for k in symbols}
    def find_possible(self,blocks):
        if self.v>0:
            self.possible=None
            return False
        # print(self)
        for b in blocks:
            r=b.ready
            for k in symbols:
                if r[k]: self.possible[k]=False
        return self.check_writable()
    def check_writable(self):
        if self.v>0:
            self.possible=None
            return False
        npossible=0
        for i in symbols:
            if self.possible[i]:
                if npossible>0:
                    return False
                npossible=i
        print(self,npossible)
        self.v=npossible
        self.possible=None
        return True
    def __str__(self):
        return f'row={self.row}, col={self.col}, square={self.square}, v={self.v}, possible={self.possible}'
    def fill(self,x,blocks):
        self.v=x
        self.possible=None
        blocks[0][self.row].ready[x]=True
        blocks[1][self.col].ready[x]=True
        blocks[2][self.square].ready[x]=True

class UnitBlock:
    def __init__(self):
        self.cells=[]
        self.ready={k:False for k in symbols}
    def find_ready(self,cells):
        for cell in cells:
            self.ready[cell.v]=True
    def check_writable(self,cells,blocks):
        changed=False
        for k in symbols:
            if self.ready[k]: continue
            npossible=0
            can_write=None
            for c in cells:
                if c.v>0 or c.possible is None: continue
                if c.possible[k]:
                    npossible+=1
                    if npossible>1:
                        can_write=None
                        break
                    can_write=c
            if npossible==1:
                for c in cells:
                    print(c)
                print(can_write,k)
                can_write.fill(k,blocks)
                changed=True
        return changed

    def toString(self,cells):
        s=''
        for c in cells:
            s+=f'{c.v} '
        return s

class Row(UnitBlock):
    def __init__(self,id):
        super(Row,self).__init__()
        start_id=id*9
        self.cells=[i+start_id for i in block_ids]

class Column(UnitBlock):
    def __init__(self,id):
        super(Column,self).__init__()
        start_id=id
        self.cells=[9*i+start_id for i in block_ids]

class Square(UnitBlock):
    def __init__(self,id):
        super(Square,self).__init__()
        if id in [0,1,2]:
            start_id=id*3
        elif id in [3,4,5]:
            start_id=id*3+18
        elif id in [6,7,8]:
            start_id=id*3+36
        self.cells=[
            start_id,
            start_id+1,
            start_id+2,
            start_id+9,
            start_id+10,
            start_id+11,
            start_id+18,
            start_id+19,
            start_id+20,
        ]

class Soduko:
    def __init__(self):
        self.cells=[Cell() for i in range(81)]
        self.rows=[Row(i) for i in block_ids]
        self.cols=[Column(i) for i in block_ids]
        self.squares=[Square(i) for i in block_ids]
        self.blocks=[self.rows,self.cols,self.squares]
        self._add_cell_to_blocks()
    def _init_from_array(self,data_list):
        # initialize the map based on a given 2D array
        for i in block_ids:
            for j in block_ids:
                if data_list[i,j]>0:
                    self.cells[i*9+j].v=data_list[i,j]
    def _init_from_str(self,data_list):
        # initialize the map based on a given 2D array
        for i in range(len(data_list)):
            if data_list[i][0]!='$':
                offset=0
                s_current=data_list[i]
            else:
                offset=int(data_list[i][1])
                s_current=data_list[i][2:]
            for j in range(len(s_current)):
                if s_current[j]>'0':
                    self.cells[i*9+j+offset].v=int(s_current[j])# -int('0')
    def _get_block(self,cell):
        return [self.rows[cell.row],self.cols[cell.col],self.squares[cell.square]]
    def _update_ready(self):
        # iteratively update possible dicts in each cell and ready dicts in each block
        changed=False
        print(self)
        for c in self.cells:
            changed|=c.find_possible(self._get_block(c))
        for b in self.blocks:
            for u in b:
                u.find_ready([self.cells[i] for i in u.cells])
        print(self)
        for b in self.blocks:
            for u in b:
                changed|=u.check_writable([self.cells[i] for i in u.cells],self.blocks)
        for b in self.blocks:
            for u in b:
                u.find_ready([self.cells[i] for i in u.cells])
        return changed
    def _naive_fill(self):
        changed=True
        for b in self.blocks:
            for u in b:
                u.find_ready([self.cells[i] for i in u.cells])
        while changed:
            changed=self._update_ready()
    def _add_cell_to_blocks(self):
        for i in range(81):
            for j in block_ids:
                if i in self.rows[j].cells:
                    self.cells[i].row=j
                    break
            for j in block_ids:
                if i in self.cols[j].cells:
                    self.cells[i].col=j
                    break
            for j in block_ids:
                if i in self.squares[j].cells:
                    self.cells[i].square=j
                    break
    def __str__(self):
        s=''
        s0=[self.rows[i].toString([self.cells[t] for t in self.rows[i].cells]) for i in block_ids]
        for s00 in s0:
            s+=f'{s00}\n'
        return s


if __name__=='__main__':
    s=Soduko()
    from predef import *
    # s._init_from_array(np.array(sod1))
    s._init_from_str(sod3)
    print(s)
    s._naive_fill()
    print(s)