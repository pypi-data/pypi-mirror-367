import xcbm

Data_path= str(list(xcbm.__path__)[0])+"/GMTKN55_Dataset"
print(Data_path)

from GMTKN55 import GMTKN55_Benchmark

ff = open('GMTKN55_results.dat','w')

xc_list = ['DSD-BLYP-D3BJ','WB97X-V']

for ii in xc_list:

    calc = GMTKN55_Benchmark(xc_functional_name=ii, basis_set_name='def2-tzvp', subset_list='SLIM05',
                  dataset_path=Data_path)
      
    mae, wtmad_2 = calc.run()
   
    ff.write('XC Functional : '+str(calc.xc_functional)+'  Basis : '+str(calc.basis_set)+\
           '  SET : '+str(calc.gmtkn55_subset)+'\n\n\n')
    ff.write('WTMAD-2 : '+str(wtmad_2)+'\n\n\n')
   
    for key, value in mae.items():
      ff.write(str(key)+'     '+str(value)+'\n')

ff.close()


