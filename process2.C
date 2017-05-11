{
  gStyle->SetOptStat(1);
  gStyle->SetOptFit(1);

// Final set of parameters            Asymptotic Standard Error
// =======================            ==========================
// a               = -0.00141287      +/- 1.31e-05     (0.927%)
// b               = 689.025          +/- 2.399        (0.3482%)
// c               = 153.322          +/- 0.8114       (0.5292%)
// d               = -0.0198113       +/- 0.0002735    (1.38%)
// e               = -10.7987         +/- 2.004        (18.56%)

  //(-0.00141287*0+689.025)*(1-exp(-163.83/153.322))/((3.9--0.0198113)**2) + -10.7987
  // 18.64090413068302663702886380962909804373091561755746647

  //Read in Data
  TTree *t = new TTree("t","UVLED Data");
  t->ReadFile("dataset.txt",
	      "year/I:month/I:day/I:fno/I:id/I:wavelength/I:I/D:I_stdev/D:a/D:d/D:frequency/D:Ic/D:Ic_stdev/D:F/D:F_err");  

/*
f(x,A,V) = a00 + (a01*V + a02*V**2 + a10*A + a11*A*V + a12*A*V**2 + a20*A**2 + a21*A**2*V + a22*A**2*V**2)/(x-f)**2;

a00 = 0;
a01 = 0;
a02 = 0;
a10 = 3.71387562498099;
a11 = 3.17186247536114e-06;
a12 = -3.08735059598478e-11;
a20 = -0.0056186989051916;
a21 = -5.82971863993554e-08;
a22 = 0;
f = -0.0178493980840971;

FIT_LIMIT = 1.0e-14
set dummy x, A, V;
fit f(x,A,V) 'dataset.csv' using 6:5:7:10:11 via a10, a11, a12, a20, a21, f

*/

  //TMinuit (Root Fitter) - number of parameters fitting, initialize parameters to starting, 4 step sizes

 
	Int_t n_data_points_total = (Int_t)t->GetEntries();
	Double_t* Flux = new Double_t [n_data_points_total];
	Double_t* Flux_err = new Double_t [n_data_points_total];
	Double_t* uvled_phdiod_distance = new Double_t [n_data_points_total];
	Double_t* frequency = new Double_t [n_data_points_total];
	Double_t* amplitude = new Double_t [n_data_points_total];


        gROOT->LoadMacro("Chi-squared2.C");

	Double_t var_F, var_F_err, var_d, var_frequency, var_amplitude;
	t->SetBranchAddress("F",&var_F);
	t->SetBranchAddress("F_err",&var_F_err);
	t->SetBranchAddress("d",&var_d);
	t->SetBranchAddress("frequency",&var_frequency);
	t->SetBranchAddress("a",&var_amplitude);

	for (Int_t i=0; i<t->GetEntries(); i++)
		{
			t->GetEntry(i);
			Flux[i] = var_F;
	                Flux_err[i] = var_F_err;
                        uvled_phdiod_distance[i] = var_d;
	                frequency[i] = var_frequency;
                        amplitude[i] = var_amplitude;
		}

 
  

  Int_t ierflg = 0; 

  //All Parameters
  TMinuit *minuit = new TMinuit(7);
  minuit->SetFCN(FCN);
  
  enum {param_size = 7}; 
/*f(x,A,V) = (a*A + c*A*V + a12*A*V**2 + b*A**2 + d*A**2*V/(x-f)**2;

a = 3.71387562498099;
b = -0.0056186989051916;
c = 3.17186247536114e-06;
d = -5.82971863993554e-08;
e = -3.08735059598478e-11;
f = -0.0178493980840971;
g = correction

(g*(a*y + b*y*y) + c*y*x + d*y*y*x)/((z-e)*(z-e));

*/

  static Double_t vstart[param_size] = {4  , -0.005 , 0.000003   , -0.00000001 ,  -0.00000000001  , -0.01       , 1};
  static Double_t step[param_size] =   {.1 , 0.0001 , 0.0000001  ,  0.000000001,  -0.000000000001 , 0.001       , 0.1};

  minuit->mnparm(0, "a", vstart[0], step[0], 0,0,ierflg);
  minuit->mnparm(1, "b", vstart[1], step[1], 0,0,ierflg);
  minuit->mnparm(2, "c", vstart[2], step[2], 0,0,ierflg);
  minuit->mnparm(3, "d", vstart[3], step[3], 0,0,ierflg); 
  minuit->mnparm(4, "e", vstart[4], step[4], 0,0,ierflg);
  minuit->mnparm(5, "f", vstart[5], step[5], 0,0,ierflg);
  minuit->mnparm(6, "g", vstart[6], step[6], 0,0,ierflg);


  minuit->SetErrorDef(1.0); 
  minuit->Migrad();
  

  // Print results
  cout << "\n Print results from minuit \n";
  double fParamVal[param_size];
  double fParamErr;

  minuit->GetParameter(0,fParamVal[0],fParamErr);
  cout << "a =" << fParamVal[0] << "\n";
  minuit->GetParameter(1,fParamVal[1],fParamErr);
  cout << "b =" << fParamVal[1] << "\n";
  minuit->GetParameter(2,fParamVal[2],fParamErr);
  cout << "c =" << fParamVal[2] << "\n";
  minuit->GetParameter(3,fParamVal[3],fParamErr);
  cout << "d =" << fParamVal[3] << "\n";
  minuit->GetParameter(4,fParamVal[4],fParamErr);
  cout << "e =" << fParamVal[4] << "\n";
  minuit->GetParameter(5,fParamVal[5],fParamErr);
  cout << "f =" << fParamVal[5] << "\n";
  minuit->GetParameter(6,fParamVal[6],fParamErr);
  cout << "g =" << fParamVal[6] << "\n";

  double in_x = 0;
  double in_y = 163.83;
  double in_z = 3.9; //2.0923 or 3.9
  double value = fitting_function(in_x, in_y, in_z, fParamVal[0], fParamVal[1], fParamVal[2], fParamVal[3], fParamVal[4], fParamVal[5], fParamVal[6]);
  cout << "Fitted Flux Value at " << "amplitude: " << in_y << " distance: " << in_z << " frequency: " << in_x << "\n";  
  cout << "" << value << "\n";

  //double_t residual = (F - fitting_function(frequency, a, d, fParamVal[0], fParamVal[1], fParamVal[2], fParamVal[3], fParamVal[4]));
  //double_t per_residual = (F - fitting_function(frequency, a, d, fParamVal[0], fParamVal[1], fParamVal[2], fParamVal[3], fParamVal[4])) * 100;
  
  

}

