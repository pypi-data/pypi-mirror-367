from Models.BWM.StandardBWM import StandardBWM
import numpy as np
from Visualizer.graph import credal_ranking, weight_distribution

if __name__ == "__main__":
    a_b =  np.array([
       [ 3, 4, 6, 1, 5, 2, 9, 7],
       [ 1, 2, 8, 4, 5, 3, 9, 6],
       [ 2, 2, 3, 1, 5, 5, 9, 8],
       [ 2, 1, 8, 2, 9, 3, 8, 8],
       [ 2, 4, 9, 1, 4, 3, 5, 5],
       [ 1, 2, 9, 1, 3, 5, 5, 4],
       ])

    a_w =  np.array([
        [ 7, 6, 4, 9, 5, 8, 1, 3],
        [ 9, 8, 2, 5, 4, 5, 1, 3],
        [ 8, 8, 5, 9, 5, 5, 1, 2],
        [ 8, 9, 2, 8, 1, 8, 2, 2],
        [ 8, 6, 1, 9, 6, 7, 4, 4],
        [ 9, 8, 1, 9, 7, 5, 5, 6],
        ])

    dmNo, cNo = a_w.shape
    altNo = 50
    x = np.random.rand(altNo // 2, cNo)
    altMat = np.concatenate([x*1,x])

    opt = {'CriteriaDependence': False, 'Sigma': np.eye(cNo) }

    bwm = StandardBWM( AB=a_b*100, AW=a_w*100, opt=opt, alternatives=altMat)
    bwm.sampling()
    print('Ok')
