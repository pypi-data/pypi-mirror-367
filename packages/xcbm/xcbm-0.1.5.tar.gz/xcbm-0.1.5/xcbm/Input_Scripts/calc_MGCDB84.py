import xcbm

Data_path= str(list(xcbm.__path__)[0])+"/MGCDB84_Dataset"
print(Data_path)

from xcbm.MGCDB84 import MGCDB84_Benchmark

calc = MGCDB84_Benchmark(basisset='def2-svp', xcfunctional='B3LYP',\
        dataset_path=Data_path ,\
        dataset_types=['EA13' ,'AE18'])

rmsd,mad  = calc.compute_prediction()

f = open('rmsd_mad.dat','w')

for ii in range(len(rmsd)):
    f.write(str(calc.dataset_types[ii])+"   "+str(rmsd[ii])+"   "+str(mad[ii])+"\n")

f.close()























