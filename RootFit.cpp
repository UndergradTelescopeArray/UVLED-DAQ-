#include <fstream>
#include <iostream>
#include <cstring>
#include <string>
#include <vector>

int main() {
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
	ampl.push_back(std::stod(tokBuffer,NULL));
	break;
      case 5:
	dist.push_back(std::stod(tokBuffer,NULL));
	break;
      case 6:
	freq.push_back(std::stod(tokBuffer,NULL));
	break;
      case 9:
	flux.push_back(std::stod(tokBuffer,NULL));
	break;
      case 10:
	fluxErr.push_back(std::stod(tokBuffer,NULL));
	break;
      default:
	break;
      }//End switch
      column++;
      tokBuffer = std::strtok(NULL,",");
    }//End while

    for(int i = 0; i<flux.size(); i++ )
      std::cout << flux[i] << "," << fluxErr[i] << "," << dist[i] << "," << ampl[i] << "," << freq[i] << "\n";
  }
}
