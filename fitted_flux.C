
Double_t fitted_F_vs_d(Double_t d)
{
  return fFluxVsD->Eval(d);
}

Double_t fitted_F_vs_a(Double_t a)
{
  return fFluxVsa->Eval(a);
}

Double_t fitted_F_vs_d_without(Double_t d)
{
  return fFluxVsD_without->Eval(d);
}

//Double_t fitted_F_vs_lambda(Double_t lambda)
//{
//  return fFluxVslambda->Eval(lambda);
//}
