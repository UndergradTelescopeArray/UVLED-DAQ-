//datapoints global

Double_t fitting_function(Double_t x, Double_t y, Double_t z,
	Double_t a, Double_t b, Double_t c,
	Double_t d, Double_t e, Double_t f, Double_t g)

{
     return (g*(a*y + b*y*y) + c*y*x + d*y*y*x + e*y*x*x)/((z-f)*(z-f));
}

double a = 0;
double b = 0;
double c = 0;
double d = 0;
double e = 0;
double f = 0; 
double g = 0; 

void FCN(Int_t &npar, Double_t *gin, Double_t &f_fcn, Double_t *par, Int_t iflag)
{

  double chisq = 0;
  double residual = 0;
  double residual_over_error = 0;
  double delta_chisq = 0;
  a = par[0];
  b = par[1];
  c = par[2];
  d = par[3];
  e = par[4];
  f = par[5];
  g = par[6];

  for (Int_t i=0; i< n_data_points_total;i++){
     double flux_expected_by_fit = fitting_function(frequency[i],amplitude[i],uvled_phdiod_distance[i],a,b,c,d,e,f,g);
     residual = (Flux[i] - flux_expected_by_fit);
     residual_over_error=residual/Flux_err[i]; 
     delta_chisq = residual_over_error * residual_over_error;
     chisq += delta_chisq;
     }
   f_fcn = chisq;
}

Double_t fitted_function(Double_t x, Double_t y, Double_t z){
  return fitting_function(x,y,z,a,b,c,d,e,f,g);
}



