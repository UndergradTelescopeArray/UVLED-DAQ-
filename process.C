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

  //Read in Data
  TTree *t = new TTree("t","UVLED Data");
  t->ReadFile("dataset.txt",
	      "year/I:month/I:day/I:fno/I:id/I:lambda/D:I/D:I_stdev/D:a/D:d/D:f/D:Ic/D:Ic_stdev/D:F/D:F_err");  

  //f(x,A,V) = (a*V+b)*(1-exp(-A/c))/((x-d)**2) + e

  //Distance
  TCanvas *c1 = new TCanvas("c1","c1",700,700);
  TProfile *pFluxVsD = new TProfile("pFluxVsD","",1000,0.1,1.0);
  t->Draw("F:d>>pFluxVsD","","prof");
  
  TF1 *fFluxVsD = new TF1("fFluxVsD","[0]/(x-[1])^2+[2]",0.1,1.0);
  fFluxVsD->SetParNames("A_{Scaling}","D_{Min}","C_{Offset}");

  pFluxVsD->Fit(fFluxVsD);
  
  //Distance_Comparison 
  TF1 *fFluxVsD_without = new TF1("fFluxVsD","[0]/(x-[1])^2+[2]",0.1,1.0);
  fFluxVsD->SetParNames("A_{Scaling}","D_{Min}","C_{Offset}");
  fFluxVsD->FixParameter(2,0.0);

  TCanvas *c7 = new TCanvas("c7","c7",700,700);
  t->SetTitle("Offset percent difference vs d");
  t->Draw("100.0*(fitted_F_vs_d(d)-fitted_F_vs_d_without(d))/fitted_F_vs_d(d):d","","prof");

  //Amplitude
  TCanvas *c2 = new TCanvas("c2","c2",700,700);
  TProfile *pFluxVsa = new TProfile("pFluxVsa","",100,0.1,170);
  t->Draw("F:a>>pFluxVsa","","prof");
  
  TF1 *fFluxVsa = new TF1("fFluxVsa","[0]*(1-exp(-x/[1]))/[2]",0.1,170);
  fFluxVsa->SetParNames("A_{Scaling}","amplitude_{Scaling}","distance{}");
  double pars[3]={1,151.932,-0.0200057 };
  fFluxVsa->SetParameters(pars);
  pFluxVsa->Fit(fFluxVsa);

  //Frequency
  TCanvas *c3 = new TCanvas("c3","c3",700,700);
  TProfile *pFluxVslambda = new TProfile("pFluxVslambda","",1000, 0,120000);
  t->Draw("F:lambda>>pFluxVslambda","","prof");
  
  //TF1 *fFluxVslambda = new TF1("fFluxVsa","[0]*x+[1])*[3]",0.1,120);
  //fFluxVslambda->SetParNames("lambda_{scaling}","lambda_{offset}","C_{scaling}"); 
  //pFluxVslambda->Fit(fFluxVslambda);

  //Error of individual parameters
  gROOT->LoadMacro("fitted_flux2.C");

  TCanvas *c4 = new TCanvas("c4","c4",700,700);
  t->SetTitle("Distance Error vs Distance");
  t->Draw("100.0*(F-fitted_F_vs_d(d))/fitted_F_vs_d(d):d","","prof");

  TCanvas *c5 = new TCanvas("c5","c5",700,700);
  t->SetTitle("Amplitude Error vs Amplitude");
  t->Draw("100.0*(F-fitted_F_vs_a(a))/fitted_F_vs_a(a):a","","prof");

  //TCanvas *c6 = new TCanvas("c6","c6",700,700);
  //t->SetTitle("Frequency Error vs Frequency");
  //t->Draw("100.0*(F-fitted_F_vs_lambda(lambda))/fitted_F_vs_lambda(lambda):lambda","","prof");

}





