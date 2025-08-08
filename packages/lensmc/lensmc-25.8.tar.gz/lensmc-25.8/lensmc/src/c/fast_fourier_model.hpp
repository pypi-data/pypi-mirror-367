// fast_fourier_model.hpp

#include <cmath>
#include <complex>


typedef std::complex<float> fcomplex;


void generate_galaxy_model(double e1, double e2, double galsize, double xpos, double ypos,
                           int semimajor, double rfiducial,
                           double *A, double x_offset, double y_offset,
                           int odim, int mdim, int osampl,
                           float* rmodelft, float* resampledmodelft, fcomplex *psfft,
                           fcomplex *xshiftft, fcomplex *yshiftft,
                           fcomplex *convmodelft, fcomplex *dsmodelft,
                           int do_hankel_resample);


void generate_star_model(double xpos, double ypos,
                         double *A, double x_offset, double y_offset,
                         int odim, int osampl,
                         fcomplex *psfft,
                         fcomplex *xshiftft, fcomplex *yshiftft,
                         fcomplex *convmodelft, fcomplex *dsmodelft);


void make_circular_galaxy(double n, double a, double rfiducial, int modeldim, int osampl, double *f);
