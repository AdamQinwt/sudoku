import numpy as np
from sudoku import Sudoku
symbols=[k for k in range(1,10)]
block_ids=list(range(9))

class Cell:
    def __init__(self):
        self.row=0
        self.col=0
        self.square=0
        self.v=0
        self.possible={k:True for k in symbols}
    def __str__(self):
        return f'row={self.row}, col={self.col}, square={self.square}, v={self.v}, possible={self.possible}'

class UnitBlock:
    def __init__(self):
        self.cells=[]
        self.ready={k:False for k in symbols}
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

class SudokuSolver:
    def __init__(self,sudoku):
        self.sudoku=sudoku
        self.cells=[Cell() for i in range(81)]
        self.rows=[Row(i) for i in block_ids]
        self.cols=[Column(i) for i in block_ids]
        self.squares=[Square(i) for i in block_ids]
        self.blocks=[self.rows,self.cols,self.squares]
        self.array=np.zeros([81],dtype=np.int)
        self.fill_sequence=[]
        self._add_cell_to_blocks()
    def set(self,idx,x,label='init'):
        self.fill_sequence.append((idx,x,label))
        self.cells[idx].v=x
        self.array[idx]=x
        self.cells[idx].possible=None
        self.rows[self.cells[idx].row].ready[x]=True
        self.cols[self.cells[idx].col].ready[x]=True
        self.squares[self.cells[idx].square].ready[x]=True
        # print(self.cols[0].ready,self.cols[0].cells,idx,x)
        # print(self.cells[idx])
    def update_possible_list(self):
        for b in self.blocks:
            for u in b:
                for cidx in u.cells:
                    if self.cells[cidx].possible:
                        for t in symbols:
                            if u.ready[t]:
                                self.cells[cidx].possible[t]=False
                                # if cidx==0: print(u.cells,t)
    def cell_filler(self):
        # if there is only one possible value, fill it.
        changed=False
        for cidx in range(81):
            if self.cells[cidx].possible is None: continue
            npossible=0
            can_write=0
            for i in symbols:
                if self.cells[cidx].possible[i]:
                    npossible+=1
                    if npossible>1:
                        break
                    else:
                        can_write=i
            if npossible==1:
                # print(self.cells[cidx],can_write)
                self.set(cidx,can_write,'cell')
                changed=True
            elif npossible==0:
                return None
        return changed
    def block_filler(self):
        # if there is only one possible position, fill it.
        changed=False
        for b in self.blocks:
            for u in b:
                for k in symbols:
                    if u.ready[k]: continue
                    npossible=0
                    can_write=None
                    for cidx in u.cells:
                        if self.cells[cidx].possible is None: continue
                        if self.cells[cidx].possible[k]:
                            npossible+=1
                            if npossible>1:
                                break
                            can_write=cidx
                    if npossible==1:
                        self.set(can_write,k,'block')
                        changed=True
                    elif npossible==0:
                        return None
        return changed
    def naive_fill(self):
        # returns:
        # True: Successfully filled all cells
        # False: Some cells remain uncertain
        # None: Conflicts
        changed=True
        while changed:
            self.update_possible_list()
            changed1=self.cell_filler()
            changed2=self.block_filler()
            if changed1 is None or changed2 is None: return None
            changed=changed1|changed2
        return self.check_complete()
    def assume_filler(self,assume_thresh=3,assume_depth=3,*args,**kwargs):
        # try the box with npossible no larger than thresh
        # find a cell with minmum npossible
        min_npossible=9
        min_npossible_idx=-1
        for idx in range(81):
            npossible=0
            if self.cells[idx].possible is None: continue
            for sym in symbols:
                if self.cells[idx].possible[sym]:
                    npossible+=1
                    if npossible>assume_thresh:
                        continue
            if npossible<min_npossible:
                min_npossible=npossible
                min_npossible_idx=idx
        if min_npossible>assume_thresh:
            # print(f'Cannot Use assume_filler @ {min_npossible}>{assume_thresh}')
            return False
        elif min_npossible==0:
            return False
        assume_idx=min_npossible_idx
        assume_list=[sym for sym in symbols if self.cells[assume_idx].possible[sym]]
        print(f'Assuming {assume_list} @ {assume_idx}')
        # print(self)
        for sym in assume_list:
            new_sudoku=self.create_sudoku()
            new_solver=SudokuSolver(new_sudoku)
            new_solver.set(assume_idx,sym,'assume')
            success=new_solver.solve(assume_thresh=assume_thresh,assume_depth=assume_depth-1)
            if success is None:
                pass
                # print(f'Failed at Assuming {sym}@{assume_idx}')
            elif success:
                self.copy_from(new_solver)
                return True
            else:
                pass
                # print(f'Assuming {sym}@{assume_idx} Remains Uncertain!')
                # print(new_solver.fill_sequence)
        return False
    def solve(self,assume_depth=3,*args,**kwargs):
        if self.naive_fill(): return True
        if assume_depth==0: return False
        if self.assume_filler(assume_depth=assume_depth,*args,**kwargs): return True
        return False
    def check_complete(self):
        for c in self.cells:
            if c.v==0: return False
        return True
    def _add_cell_to_blocks(self):
        for i in block_ids:
            for j in self.rows[i].cells:
                self.cells[j].row=i
            for j in self.cols[i].cells:
                self.cells[j].col=i
            for j in self.squares[i].cells:
                self.cells[j].square=i
        for i in block_ids:
            for j in block_ids:
                if self.sudoku[i,j]>0: self.set(i*9+j,self.sudoku[i,j])
        self.fill_sequence=[]
    def __str__(self):
        s=''
        s0=[self.rows[i].toString([self.cells[t] for t in self.rows[i].cells]) for i in block_ids]
        for s00 in s0:
            s+=f'{s00}\n'
        return s
    def create_sudoku(self):
        # creates a new sudoku
        s=Sudoku()
        s.set(self.array)
        return s
    def copy_from(self,s):
        for idx in range(81):
            if self.cells[idx].v==0:
                self.set(idx,s.cells[idx].v,'copy')

if __name__=='__main__':
    from predef import *
    sudoku=Sudoku(sod6)
    solver=SudokuSolver(sudoku)
    # print(solver)
    solver.solve(assume_depth=5)
    print(solver.fill_sequence)
    print(solver)