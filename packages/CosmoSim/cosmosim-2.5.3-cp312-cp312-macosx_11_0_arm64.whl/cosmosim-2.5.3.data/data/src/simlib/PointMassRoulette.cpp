/* (C) 2023: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Roulette.h"

/* The following is a default implementation for the point mass lens. 
 * It would be better to make the class abstract and move this definition to the 
 * subclass. */
cv::Point2d PointMassRoulette::getDistortedPos(double r, double theta) const {
    double R = getXiAbs()  ;
    double einsteinR = pmlens->getEinsteinR() ;

    double nu1 = r*cos(theta) ;
    double nu2 = r*sin(theta) ;
    double frac = (einsteinR * einsteinR) / R ;
    double rf = r/R ;

    for (int m=1; m<=nterms; m++){
       double sign = m%2 ? -1 : +1 ;
       double f = sign*pow(rf, m) ;
       nu1 -= frac * f * cos(m*theta) ;
       nu2 += frac * f * sin(m*theta) ;
    }
    // The return value should be normalised coordinates in the source plane.
    // We have calculated the coordinates in the lens plane.
    return cv::Point2d( nu1 / CHI, nu2 / CHI ) ;
}
