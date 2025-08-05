#from pyscf import gto, dft
import numpy as np
import pandas as pd


class GMTKN55:
       """This is a class that gets functional name, basis set and gmtkn55 subsets as arguments and performs the \
       GMTKN55 benchmarking"""

       def __init__(self, xc_functional_name, basis_set_name, subset_list,dataset_path,package='psi4'):
         self.xc_functional  = xc_functional_name
         self.basis_set      = basis_set_name
         self.gmtkn55_subset = subset_list
         self.package        = package
         self.gmtkn55_dataset_path = dataset_path
 
         if isinstance(self.gmtkn55_subset,str):
             if self.gmtkn55_subset.upper() == 'FULL':
                 self.gmtkn55_subset = ['W4-11', 'G21EA', 'G21IP',  'DIPCS10',  'PA26',  'SIE4x4',  'ALKBDE10',  'YBDE18',   \
                                     'AL2X6', 'HEAVYSB11', 'NBPRC', 'ALK8', 'RC21', 'G2RC', 'BH76RC', 'FH51', 'TAUT15',    \
                                     'DC13', 'MB16-43', 'DARC', 'RSE43', 'BSR36', 'CDIE20', 'ISO34', 'ISOL24','C60ISO',    \
                                     'PArel', 'BH76', 'BHPERI', 'BHDIV10', 'INV24', 'BHROT27', 'PX13', 'WCPT18', 'RG18',   \
                                     'ADIM6', 'S22', 'S66', 'HEAVY28', 'WATER27', 'CARBHB12', 'PNICO23', 'HAL59', 'AHB21', \
                                     'CHB6','IL16', 'IDISP', 'ICONF', 'ACONF', 'Amino20x4', 'PCONF21', 'MCONF', 'SCONF',   \
                                     'UPU23', 'BUT14DIOL'] 
         
             elif self.gmtkn55_subset.upper() =='SLIM05':
                self.gmtkn55_dataset_path = dataset_path+'/GMTKN55_SLIM05/'
                self.gmtkn55_subset = ['AHB21', 'ALKBDE10', 'BH76', 'BH76RC', 'BHROT27', 'CHB6', 'DIPCS10', 'G21EA',\
                                       'G21IP', 'G2RC', 'HAL59', 'HEAVY28', 'HEAVYSB11', 'INV24', 'PA26', 'RG18', 'RSE43',\
                                       'SIE4x4', 'TAUT15', 'W4-11', 'WATER27', 'WCPT18']
             
             elif self.gmtkn55_subset.upper() =='SLIM16':
                self.gmtkn55_dataset_path = dataset_path+'/GMTKN55_SLIM16/'
                self.gmtkn55_subset = ['ADIM6','AHB21','AL2X6','ALK8', 'ALKBDE10', 'BH76', 'BH76RC','BHDIV10','BHPERI', 'BHROT27',\
                                       'BUT14DIOL','CARBHB12','DC13', 'DIPCS10', 'G21EA', 'G21IP', 'G2RC', 'HAL59', 'HEAVY28',\
                                       'ICONF','IL16','ISO34','MB16-43', 'PA26', 'PNICO23','PX13','RC21', 'RG18', 'RSE43','S66',\
                                       'SIE4x4', 'TAUT15', 'W4-11', 'WATER27', 'WCPT18','YBDE18']

             elif self.gmtkn55_subset.upper() =='SLIM20':
                self.gmtkn55_dataset_path = dataset_path+'/GMTKN55_SLIM20/'
                self.gmtkn55_subset = ['ACONF','AHB21', 'ALKBDE10','Amino20x4', 'BH76', 'BH76RC','BHDIV10','BHPERI','BSR36',\
                                     'BUT14DIOL','CDIE20','DIPCS10','FH51', 'G21EA', 'G21IP', 'G2RC', 'HAL59', 'HEAVY28', 'ICONF','IL16',\
                                     'INV24','ISO34','MB16-43', 'PA26','PArel', 'PNICO23','PX13', 'RSE43','S22','S66',\
                                       'SIE4x4', 'TAUT15', 'W4-11', 'WATER27', 'WCPT18','YBDE18']



         print(self.package)
         if self.package=='psi4':
             import psi4
             self.psi4 = psi4
         else:
             from pyscf import gto, dft


       def xyz_to_psi4_molecule(self, xyz_file, charge=0, multiplicity=1, units='angstrom'):
         """
         Reads a .xyz file and returns a Psi4 molecule object.
      
         Parameters:
         - xyz_file (str): Path to the .xyz file.
         - charge (int): Total charge of the molecule.
         - multiplicity (int): Spin multiplicity of the molecule.
         - units (str): Units for coordinates ('angstrom' or 'bohr').
      
         Returns:
         - psi4.core.Molecule: Psi4 molecule object.
         """
         with open(xyz_file, 'r') as f:
             lines = f.readlines()
             atom_lines = ''.join(lines[2:])  # skip first two lines
      
         geometry = f"""
         {charge} {multiplicity}
         {atom_lines}
         """
      
       
         mol = self.psi4.geometry(f"""
         units {units}
         {geometry}
         """)
         return mol
      
     
       def compute_psi4_rks_energy(self, geometry, charge, multiplicity, basis, xc_functional, ds_name): 
         print(geometry)  
         psi4_mol = self.xyz_to_psi4_molecule(xyz_file=geometry, charge=charge, multiplicity=multiplicity)
         self.psi4.set_output_file("psi4_output_rks.dat", True)
         self.psi4.set_options({'basis'                : basis,
                           'DFT_SPHERICAL_POINTS' : 110,
                           'DFT_RADIAL_POINTS'    : 210,
                           'MAXITER'              : 500,
                           'SCF_TYPE'             : 'DIRECT',
                           'E_CONVERGENCE'        : 1e-6,
                           'D_CONVERGENCE'        : 1e-4})
         energy,scf_wfn = self.psi4.properties('SCF',dft_functional=xc_functional, molecule=psi4_mol, return_wfn=True, property=['dipole'])
         print(energy)
         return energy

       def compute_psi4_uks_energy(self, geometry, charge, multiplicity, basis, xc_functional, ds_name): 
           print(geometry)         
           psi4_mol = self.xyz_to_psi4_molecule(xyz_file=geometry, charge=charge, multiplicity=multiplicity)
           self.psi4.set_output_file("psi4_output_rks.dat", True)
           self.psi4.set_options({'basis'                : basis,
                             'reference'            : 'uks',
                             'DFT_SPHERICAL_POINTS' : 110,
                             'DFT_RADIAL_POINTS'    : 210,
                             'MAXITER'              : 500,
                             'SCF_TYPE'             : 'DIRECT',
                             'E_CONVERGENCE'        : 1e-6,
                             'D_CONVERGENCE'        : 1e-4})
           energy,scf_wfn = self.psi4.properties('SCF',dft_functional=xc_functional, molecule=psi4_mol, return_wfn=True, property=['dipole']) 
           print(energy)
           return energy 

       def compute_rs_energy(self,geometry,charge,multiplicity,basis,xc_functional, ds_name):
           mol = gto.M(atom=geometry, charge=charge, basis=basis, spin = int((multiplicity-1)))
           print(geometry)
           mol.verbose = 0
           if ds_name in ['HEAVY28','HEAVYSB11']:
              mf = dft.RKS(mol).newton()
           else:
              mf = dft.RKS(mol)
           mf.xc = xc_functional
           energy = mf.kernel()
           print(energy)
           return energy

       def compute_urs_energy(self,geometry,charge,multiplicity,basis,xc_functional, ds_name):
           mol = gto.M(atom=geometry,charge=charge,basis=basis,spin = int((multiplicity-1)))
           print(geometry)
           mol.verbose=0
           if ds_name in ['HEAVY28','HEAVYSB11']:
              mf = dft.UKS(mol).newton()
           else:
              mf = dft.RKS(mol)
           mf.xc = xc_functional
           energy = mf.kernel()
           print(energy)
           return energy

       def compute_mae(self,arr1, arr2):
           """
           Calculate the mean absolute deviation between two arrays.
            
           Args:
               arr1 (array-like): The first array.
               arr2 (array-like): The second array.
            
           Returns:
               float: The mean absolute deviation.
           """
           arr1 = np.array(arr1)
           arr2 = np.array(arr2) 
           if arr1.shape != arr2.shape:
               raise ValueError("Both arrays must have the same shape.")
           abs_diff = np.abs(arr1 - arr2)    
           return np.mean(abs_diff)

       def compute_energy(self,data_set_name):
           input_file = open(self.gmtkn55_dataset_path+'/CHARGE_MULTIPLICITY/'+'CHARGE_MULTIPLICITY_'+data_set_name+'.txt','r')

           lines = input_file.readlines()
           input_struc      = []
           input_charge     = []
           input_mul        = []
           input_geom       = []
           input_basis      = self.basis_set
           input_functional = self.xc_functional

           for line in lines:
               for s in line.strip().split()[0:1]:
                   input_struc.append(s)
    
           for line in lines:
               for s in line.strip().split()[1:2]:
                   input_charge.append(int(s))
    
           for line in lines:
               for s in line.strip().split()[2:3]:
                   input_mul.append(int(s))
  
           for ii in input_struc:
               input_geom.append(self.gmtkn55_dataset_path+'/STRUCTURES/'+data_set_name+'/'+str(ii)+'/struc.xyz')

           input_energy = np.zeros(len(input_struc))
           for index, value in enumerate(input_geom):
               if self.package=='psi4':
                   if input_mul[index] == 1 :
                       input_energy[index] = self.compute_psi4_rks_energy(input_geom[index],input_charge[index], input_mul[index],input_basis, input_functional,data_set_name)
                   elif input_mul[index]>1  :
                       input_energy[index] = self.compute_psi4_uks_energy(input_geom[index],input_charge[index], input_mul[index],input_basis, input_functional,data_set_name)

               else:
                  if input_mul[index] == 1:
                      input_energy[index] = self.compute_rs_energy(input_geom[index],input_charge[index], input_mul[index],input_basis, input_functional,data_set_name) 
                  elif input_mul[index] > 1:
                      input_energy[index] = self.compute_urs_energy(input_geom[index],input_charge[index], input_mul[index], input_basis, input_functional,data_set_name)


           data_frame = pd.DataFrame(index=range(len(input_struc)), columns = ['input__struc','input__charge','input__mul','input__energy'])

           data_frame['input__struc']  = input_struc
           data_frame['input__charge'] = input_charge
           data_frame['input__mul']    = input_mul
           data_frame['input__energy'] = input_energy

           return data_frame

       def compute_predictions(self,file,computed_file):
           ff = open(self.gmtkn55_dataset_path+'/STOCHIOMETRY/'+'STOCHIOMETRY_'+file+'.txt','r')
           lines = ff.readlines()
           df = computed_file
           print(df)
           pred_value = []
           ref_value  = []
           for line in lines[1:]:
                s = line.split()[1:-1]
                ref_value_temp = line.split()[-1]
                nn=int(len(s)/2)
                s_1 = s[:nn]
                print(s_1)
                s_2 = s[nn:]
                print(s_2)
                temp = 0
                for jj in range(len(s_1)):
                    en = df.loc[df['input__struc'] ==str(s_1[jj]),'input__energy'].values[0]
                    en = en * 6.275030E2
                    temp = temp + float(en)*float(s_2[jj])
                pred_value.append(float(temp))
                ref_value.append(float(ref_value_temp))
           pred_value = np.array(pred_value)
           for ii in pred_value:
               print('pred :',pred_value)
           ref_value = np.array(ref_value)
           for ii in ref_value:
               print('ref  :',ref_value)
           return ref_value , pred_value

       def compute_wtmad2(self,mad_dict):
              NIS = {'ACONF': 15.0, 'ADIM6': 6.0, 'AHB21': 21.0, 'AL2X6': 6.0, 'ALK8': 8.0, 'ALKBDE10': 10.0, 'Amino20x4': 80.0,\
                      'BH76RC': 30.0, 'BH76': 76.0, 'BHDIV10': 10.0, 'BHPERI':26.0, 'BHROT27': 27.0, 'BSR36': 36.0, 'BUT14DIOL': 64.0,\
                      'C60ISO': 9.0, 'CARBHB12': 12.0, 'CDIE20': 20.0, 'CHB6': 6.0, 'DARC': 14.0, 'DC13': 13.0, 'DIPCS10': 10.0,\
                      'FH51': 51.0, 'G21EA': 25.0, 'G21IP': 36.0, 'G2RC': 25.0, 'HAL59': 59.0, 'HEAVY28': 29.0, 'HEAVYSB11': 11.0,\
                      'ICONF': 17.0, 'IDISP': 6.0, 'IL16': 16.0, 'INV24': 24.0, 'ISO34': 34.0, 'ISOL24': 24.0, 'MB16-43': 43.0, \
                      'MCONF': 51.0, 'NBPRC': 12.0, 'PA26': 26.0, 'PArel': 20.0, 'PCONF21': 18.0, 'PNICO23': 23.0, 'PX13': 13.0,\
                      'RC21': 21.0, 'RG18': 18.0, 'RSE43': 43.0, 'S22': 22.0, 'S66': 66.0, 'SCONF': 17.0, 'SIE4x4': 16.0,\
                      'TAUT15': 15.0, 'UPU23': 23.0, 'W4-11': 140.0, 'WATER27': 27.0, 'WCPT18': 18.0, 'YBDE18': 18.0}

              AARE ={'ACONF':1.83, 'ADIM6':3.36 , 'AHB21':22.49 , 'AL2X6':35.88 , 'ALK8':62.60 , 'ALKBDE10':100.69 , 'Amino20x4':2.44 ,\
                      'BH76RC':21.39 , 'BH76':18.61 , 'BHDIV10':45.33 , 'BHPERI':20.87 , 'BHROT27':6.27 , 'BSR36':16.20 , 'BUT14DIOL':2.80 ,\
                      'C60ISO':98.25 , 'CARBHB12':6.04 , 'CDIE20':4.06 , 'CHB6':26.79 , 'DARC':32.47 , 'DC13':54.98 ,'DIPCS10':654.26 , \
                      'FH51':31.01 , 'G21EA':33.62 , 'G21IP':257.61 , 'G2RC':51.26 , 'HAL59':4.59 , 'HEAVY28':1.24 , 'HEAVYSB11':58.02 ,\
                      'ICONF':3.27 , 'IDISP':14.22, 'IL16':109.04 , 'INV24':31.85 , 'ISO34':14.57 , 'ISOL24':21.92 , 'MB16-43':414.73 ,\
                      'MCONF':4.97 , 'NBPRC':27.71 , 'PA26':189.05 , 'PArel':4.63 , 'PCONF21':1.62 ,'PNICO23':4.27 , 'PX13':33.36 , 'RC21' :35.70 ,\
                      'RG18':0.58 , 'RSE43':7.60 , 'S22':7.30 , 'S66':5.47 , 'SCONF':4.60 , 'SIE4x4':33.72 , 'TAUT15':3.05 , 'UPU23':5.72,\
                      'W4-11':306.91 , 'WATER27':81.14 , 'WCPT18':34.99 , 'YBDE18':49.28 }
       
              wtmad2 = 0
              tot_den = 0
       
              if len(mad_dict) == 55:
                  for key, value in mad_dict.items():
                       tot_den += NIS[key]
                       wtmad2 += (NIS[key] * 56.84 * mad_dict[key]) / AARE[key]
                  wtmad2 = wtmad2 / tot_den

              else: 
                  for key, value in mad_dict.items():
                       tot_den += NIS[key]
                       wtmad2  += (NIS[key] * 56.84 *  mad_dict[key]) / AARE[key]
                  wtmad2 = wtmad2 / tot_den

              return wtmad2

        

       def run(self):
           mae_dict = {}
           for dsn in self.gmtkn55_subset:
               dsn_energy = self.compute_energy(dsn)
               r_v,p_v = self.compute_predictions(file=dsn,computed_file=dsn_energy)
               temp_mae = self.compute_mae(r_v,p_v)
               mae_dict[dsn] = temp_mae
               print( dsn, " MAD :  ", temp_mae)

           
           calculate_wtmad2 = self.compute_wtmad2(mae_dict)
           print('wtmad2 : ', calculate_wtmad2)
           return mae_dict, calculate_wtmad2



