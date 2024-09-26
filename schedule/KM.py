import numpy as np

class KM:
    def __init__(self):
        self.matrix = None
        self.max_weight = 0
        self.row, self.col = 0, 0  
        self.size = 0  
        self.lx = None 
        self.ly = None  
        self.match = None   
        self.slack = None  
        self.visx = None    
        self.visy = None    

    # 调整数据
    def pad_matrix(self, min):
        if min:
            max = self.matrix.max() + 1
            self.matrix = max-self.matrix

        if self.row > self.col:  
            self.matrix = np.c_[self.matrix, np.array([[0] * (self.row - self.col)] * self.row)]
        elif self.col > self.row:  
            self.matrix = np.r_[self.matrix, np.array([[0] * self.col] * (self.col - self.row))]

    def reset_slack(self):
        self.slack.fill(self.max_weight + 1)

    def reset_vis(self):
        self.visx.fill(False)
        self.visy.fill(False)

    def find_path(self, x):
        self.visx[x] = True
        for y in range(self.size):
            if self.visy[y]:
                continue
            tmp_delta = self.lx[x] + self.ly[y] - self.matrix[x][y]
            if tmp_delta == 0:
                self.visy[y] = True
                if self.match[y] == -1 or self.find_path(self.match[y]):
                    self.match[y] = x
                    return True
            elif self.slack[y] > tmp_delta:
                self.slack[y] = tmp_delta

        return False

    def km_cal(self):
        for x in range(self.size):
            self.reset_slack()
            while True:
                self.reset_vis()
                if self.find_path(x):
                    break
                else:  # update slack
                    delta = self.slack[~self.visy].min()
                    self.lx[self.visx] -= delta
                    self.ly[self.visy] += delta
                    self.slack[~self.visy] -= delta

    def compute(self, datas, min=False):
        self.matrix = np.array(datas) if not isinstance(datas, np.ndarray) else datas
        self.max_weight = self.matrix.sum()
        self.row, self.col = self.matrix.shape  
        self.size = max(self.row, self.col)
        self.pad_matrix(min)
        self.lx = self.matrix.max(1)
        self.ly = np.array([0] * self.size, dtype=int)
        self.match = np.array([-1] * self.size, dtype=int)
        self.slack = np.array([0] * self.size, dtype=int)
        self.visx = np.array([False] * self.size, dtype=bool)
        self.visy = np.array([False] * self.size, dtype=bool)

        self.km_cal()

        match = [i[0] for i in sorted(enumerate(self.match), key=lambda x: x[1])]
        result = []
        for i in range(self.row):
            result.append((i, match[i] if match[i] < self.col else -1)) 
        return result


# if __name__ == '__main__':
#     a = np.array([[1,2,3,4],[2,3,4,5],[4,5,6,7],[4,5,6,7],[4,5,6,7]])
#     # a = np.array([[84, 65], [3, 34], [63, 18], [35, 12]])
#     print(len(a))
#     a = a.T
#     print(a)
#     print(len(a[0]))
  
#     km = KM()
#     min_ = km.compute(a.copy(), True)
#     print("最小组合:", min_, a[[i[0] for i in min_], [i[1] for i in min_]])
#     max_ = km.compute(a.copy())
#     print("最大组合:", max_, a[[i[0] for i in max_], [i[1] for i in max_]])
#     for i in max_:
#         print(i[1])
