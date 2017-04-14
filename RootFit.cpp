#include <fstream>
#include <iostream>
#include <cstring>
#include <cstdlib>
#include <string>
#include <vector>
#include <cmath>

int fit() {
  std::vector<double> flux, fluxErr, ampl, freq, dist;
  std::ifstream datafile;

  datafile.open("dataset.csv");
  if(datafile.bad()) {
    std::cout << "Error opening file\n";
    return 1;
  }

  char buffer[300];
  datafile.getline(buffer,300);//Remove header
  while(true) {
    datafile.getline(buffer,300);
    if(datafile.fail())
      break;
    char* tokBuffer;
    tokBuffer = std::strtok(buffer,",");//should it be ",\n\r"?
    int column = 0;
    while(tokBuffer != NULL ) {
      switch(column) {
      case 4:
	ampl.push_back(atof(tokBuffer));
	break;
      case 5:
	dist.push_back(atof(tokBuffer));
	break;
      case 6:
	freq.push_back(atof(tokBuffer));
	break;
      case 9:
	flux.push_back(atof(tokBuffer));
	break;
      case 10:
	fluxErr.push_back(atof(tokBuffer));
	break;
      default:
	break;
      }//End switch
      column++;
      tokBuffer = std::strtok(NULL,",");
    }//End while
    
    TCanvas *c1 = new TCanvas("c1","Percent residual vs Distance",200,10,700,500);
    TProfile *resProf = new TProfile("resProf", "Percent residual vs Distance",100,0,2);
    for(int i = 0; i<flux.size(); i++ ) {
      resProf->Fill( dist[i], (gnuFit(dist[i],ampl[i],freq[i])-flux[i])/flux[i] );
    }
    resProf->Draw();
    //std::cout << flux[i] << "," << fluxErr[i] << "," << dist[i] << "," << ampl[i] << "," << freq[i] << "\n";
  }
}

double gnuFit(double x, double amplitude, double frequency) {
  const double a = -0.00134129;
  const double b = 692.699;
  const double c = 160.165;
  const double d = -0.0176522;
  double f = (a*frequency+b)*(1-exp(-amplitude/c))/pow(x-d,2);
  return f;
}
