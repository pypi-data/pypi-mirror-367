/* fast_fourier_model.cpp

Generate a galaxy profile model generate_galaxy_model() in Fourier space convolved with a PSF and aliasing correctly accounted for. This is used by lensmc for fast shear measurements.

Inputs:
... put here docstrings once finalised.

Algorithm:
1. resample model through shear/stretch/interpolate;
2. apply shift;
3. convolve with PSF and top hat function;
4. alias-downsample.

Copyright 2015 Giuseppe Congedo, Lance Miller

*/


#include <cmath>
#include <complex>
// #include <iostream>

// needed for timing
// #include "omp.h"


typedef std::complex<float> fcomplex;


int hankelresample(float *rmodelft, int mdim, double e1, double e2, double galsize,
                   int semimajor, double rfiducial, int idim,
                   double *A, float *rconvmodelft);


int createshiftft(double xpos, double ypos, int dim,
                  double *A, double x_offset, double y_offset,
                  fcomplex *xshiftft, fcomplex *yshiftft);


int convolve(int dim, fcomplex *convmodelft, float *rconvmodelft, fcomplex *psfft,
             fcomplex *xshiftft, fcomplex *yshiftft);


int convolve2(int dim, fcomplex *convmodelft, fcomplex *psfft,
              fcomplex *xshiftft, fcomplex *yshiftft);


void alias(int dim, int odim, fcomplex *in, fcomplex *out);


void generate_galaxy_model(
                   // parameters for output galaxy model
                   double e1,        // e1
                   double e2,        // e2
                   double galsize,   // scalelength (pixels)
                   double xpos,      // x position shift (pixels)
                   double ypos,      // y position shift (pixels)
                   // galaxy size parameter type (r_a if semimajor is true, r_ab otherwise)
                   int semimajor,
                   // nominal (fiducial) radius of input galaxy
                   double rfiducial,
                   // astrometric distortion matrix for the celestial to pixel transformation
                   double *A,
                   // extra x offset originating in pixel domain
                   double x_offset,
                   // extra y offset originating in pixel domain
                   double y_offset,
                   // 1D dimension of output galaxy image
                   int odim,
                   // 1D dimension of large input circular galaxy image
                   int mdim,
                   // oversampling factor of intermediate resampled image
                   int osampl,
                   // pointer to FFT array of input circular galaxy
                   float* rmodelft,
                   // pointer to FT array of resampled galaxy
                   float* resampledmodelft,
                   // pointer to PSF FT
                   fcomplex *psfft,
                   // pointer to x-shift FT,
                   fcomplex *xshiftft,
                   // pointer to y-shift FT,
                   fcomplex *yshiftft,
                   // pointer to convolved, oversampled model FT
                   fcomplex *convmodelft,
                   // pointer to final downsampled, convolved FT
                   fcomplex *dsmodelft,
                   // Hankel resample?
                   // if not, assume it's been already calculated
                   // useful for multiple exposures fitting
                   int do_hankel_resample
                   )
{
  // function to resample the input galaxy FT to create an output galaxy of specified size and ellipticity

  // to oversampled units
  int idim = odim * osampl;
  double galsize1 = galsize * osampl;
  double rfiducial1 = rfiducial * osampl;
  double xpos1 = xpos * osampl;
  double ypos1 = ypos * osampl;
  double x_offset1 = x_offset * osampl;
  double y_offset1 = y_offset * osampl;

  //double t0, t1;

  //std::cout << "generate_galaxy_model (new) ";

  // resample the Hankel transform
  if (do_hankel_resample)
  {
    //t0=omp_get_wtime();
    hankelresample(rmodelft, mdim, e1, e2, galsize1, semimajor, rfiducial1, idim, A, resampledmodelft);
    //t1 = omp_get_wtime();
    //std::cout << "hankel: " << (t1-t0)*1000000 << "us ";
  }
  // create FT of 1D shifts in x and y
  //t0=omp_get_wtime();
  createshiftft(xpos1, ypos1, idim, A, x_offset1, y_offset1, xshiftft, yshiftft);
  //t1=omp_get_wtime();
  //std::cout << "shiftfft: " << (t1-t0)*1000000 << "us ";
  
  // convolve
  //t0 = omp_get_wtime();
  convolve(idim, convmodelft, resampledmodelft, psfft, xshiftft, yshiftft);
  //t1 = omp_get_wtime();
  //std::cout << "convolve: " << (t1-t0)*1000000 << "us ";
  // call alias function
  //t0 = omp_get_wtime();
  alias(idim, odim, convmodelft, dsmodelft);
  //t1 = omp_get_wtime();
 // std::cout << "alias: " << (t1-t0)*1000000 << "us ";
 // std::cout << "\n";

}


void generate_star_model(
                   // parameters for output star model
                   double xpos,      // x position shift (pixels)
                   double ypos,      // y position shift (pixels)
                   // astrometric distortion matrix for the celestial to pixel transformation
                   double *A,
                   // extra x offset originating in pixel domain
                   double x_offset,
                   // extra y offset originating in pixel domain
                   double y_offset,
                   // 1D dimension of output star image
                   int odim,
                   // oversampling factor of intermediate resampled image
                   int osampl,
                   // pointer to PSF FT
                   fcomplex *psfft,
                   // pointer to x-shift FT,
                   fcomplex *xshiftft,
                   // pointer to y-shift FT,
                   fcomplex *yshiftft,
                   // pointer to convolved, oversampled model FT
                   fcomplex *convmodelft,
                   // pointer to final downsampled, convolved FT
                   fcomplex *dsmodelft
                   )
{
  // function to resample the input galaxy FT to create an output star

  // to oversampled units
  int idim = odim * osampl;
  double xpos1 = xpos * osampl;
  double ypos1 = ypos * osampl;
  double x_offset1 = x_offset * osampl;
  double y_offset1 = y_offset * osampl;

  // create FT of 1D shifts in x and y
  createshiftft(xpos1, ypos1, idim, A, x_offset1, y_offset1, xshiftft, yshiftft);
  // convolve
  convolve2(idim, convmodelft, psfft, xshiftft, yshiftft);
  // call alias function
  alias(idim, odim, convmodelft, dsmodelft);

}


void make_circular_galaxy(double n, double a, double rfiducial, int modeldim, int osampl, double *f)
{
    // make an oversampled galaxy model
    double rmax, xx, yy, r;
    int cen, x, y, p, ox, oy;

    // galaxy parameters
    cen = modeldim / 2;
    rmax = 4.5;

    // oversampling normalisation
    int osampl2 = osampl * osampl;

    // define the dimension of the box where we do the computation of oversampled values, outside it'll be initialised to zero
    // also define the corners of the box
    int idim = 2 * (int) (rfiducial * rmax + 0.5) + 10;
    int c0 = (modeldim - idim) / 2;
    int c1 = c0 + idim;

    // inverse Sersic index
    double in = 1. / n;

    // cast to double outside of the loop
    double dosampl = (double)osampl;

    // main loop
    for (y=0; y<modeldim; y++)
    {
        for (x=0; x<modeldim; x++)
        {
            p = y * modeldim + x;
            f[p] = 0.;
            if (y>c0 && x>c0 && y<c1 && x<c1)
            {
                // make an oversampled distribution
                for (oy=0; oy<osampl; oy++)
                {
                    yy = y + (0.5 + (double)oy) / dosampl - 0.5 - cen;
                    for (ox=0; ox<osampl; ox++)
                    {
                        xx = x + (0.5 + (double)ox) / dosampl - 0.5 - cen;
                        r = std::sqrt(std::pow(yy, 2) + std::pow(xx, 2)) / rfiducial;
                        if (r < rmax)
                        {
                            r = std::pow( r, in );
                            f[p] += std::exp(- a * r) / osampl2;
                        }
                    }
                }
            }
        }
    }

}


// original interpolation
float dinterp(float *array, double r)
{
    // linear interpolation function

    int p = (int)r;
    int p1 = p + 1;
    double dr = r - p;

    double f1 = array[p];
    double f2 = array[p1];

    float val = f1 + dr * (f2 - f1);

    return val;
}


// interpolation which uses more floats in the calculation
// slightly different result, but slightly quicker
float dfinterp(float *array, double r)
{
    // linear interpolation function

    int p = (int)r;
    int p1 = p + 1;
    float dr = r - p;

    float f1 = array[p];
    float f2 = array[p1];

    float val = f1 + dr * (f2 - f1);

    return val;
}


// interpolation taking in a float, and working exclusively with floats
// much quicker but less accurate
float finterp(float *array, float r)
{
    // linear interpolation function

    int p = (int)r;
    int p1 = p + 1;
    float dr = r - p;

    float f1 = array[p];
    float f2 = array[p1];

    float val = f1 + dr * (f2 - f1);

    return val;
}


int hankelresample(float *rmodelft, int mdim, double e1, double e2, double galsize,
                   int semimajor, double rfiducial, int idim,
                   double *A, float *rconvmodelft)
{
    // sample the Hankel transform model in scaled, sheared coordinates to generate FT of elliptical model
    
    // this version has no wrap-around effects included - makes models with high frequency
    // structure but is more correct for band-limited PSFs

    // scale the galaxy size relative to the fiducial size in the circular model
    // and define it as either major axis, or geometric mean
    double rscaled = galsize * (double)mdim / rfiducial / (double)idim;
    double emod2 = e1 * e1 + e2 * e2;
    if (semimajor)
    {
        rscaled /= 1. + std::sqrt(emod2);
    }
    else
    {
        rscaled /= 1. - emod2;
    }

    // scale it by the determinant of the astrometric distortion matrix
    // note |det(A)|: we need to scale both the size and A by the pixel scale
    // to make sure we transform pixels to pixels
    rscaled /= std::abs(A[0] * A[3] - A[1] * A[2]);

    // shear transformation with astrometric distortion
    // in real space: S A
    // in Fourier space: (S A)^(-T) = S^(-T) A^(-T)
    double one_p_e1 = 1. + e1;
    double one_m_e1 = 1. - e1;
    double a = (A[3] * one_p_e1 - A[1] * e2) * rscaled;
    double b = (A[0] * e2 - A[2] * one_p_e1) * rscaled;
    double c = (A[3] * e2 - A[1] * one_m_e1) * rscaled;
    double d = (A[0] * one_m_e1 - A[2] * e2) * rscaled;

    // Nyquist dimensions
    int hdim = 1 + idim / 2;
    int hmdim = 1 + mdim / 2;
    int ihdim = idim * hdim;

    // sample the circular model FT to make the FT of a model with the right ellipticity and size
    int x, y, yy, op;
    double xp, yp;

    // optimised double precision algorithm.

    // allocate storage for the r values
    double *rs = new double[ihdim];

    // calculate r first for all array elements
    for (y=0; y<idim; y++)
    {
        // treat top half of array as having negative frequencies
        yy = y<idim/2 ? y : y-idim;
        for (x=0; x<hdim; x++)
        {
            // output pixel element
            op = y * hdim + x;
            // transformed coordinates
            xp = a * x + b * yy;
            yp = c * x + d * yy;

            rs[op] = xp * xp + yp * yp;
        }
    }

    // now take the sqrt of the whole r array (should allow the compiler to vectorise it)
    for (op=0; op<ihdim; op++){
        rs[op] = std::sqrt(rs[op]);
    }

    // interpolate
    double r;
    int hmdim1 = hmdim - 1;
    for (op=0; op<ihdim; op++){
        r = rs[op];
        // interpolate
        if (r < hmdim1)
        {
            // double precision interpolation - results identical to original code but a wee bit slower
            // rconvmodelft[op] = dinterp(rmodelft, r);

            // hybrid double/float interpolation, speed increase but with a small accuracy cost
            rconvmodelft[op] = dfinterp(rmodelft, r);
        }
        else
        {
            rconvmodelft[op] = 0.;
        }
    }

    //deallocate rs
    delete rs;

    // end of optimised double precision algorithm

// // optimised floating point algorithm (less accurate)
    
//     //allocate storage for the r values
//     float *rs = new float[idim*hdim];
    
//     //calculate r first for all array elements
//     for (y=0; y<idim; y++)
//     {
//         // treat top half of array as having negative frequencies
//         yy = y<idim/2 ? y : y-idim;

//         for (x=0; x<hdim; x++)
//         {
//             // output pixel element
//             op = y * hdim + x;
//             // transformed coordinates
//             xp = a * x + b * yy;
//             yp = c * x + d * yy;

//             rs[op] = (xp*xp + yp*yp);
//         }
//     }
    
//     //now take the sqrt of the whole r array (should allow the compiler to vectorise it)
//     for (op=0;op<idim*hdim;op++){
//         rs[op] = std::sqrt(rs[op]);
//     }
    
//     //now interpolate
//     float r;
//     for (op=0;op<idim*hdim;op++){
//         r=rs[op];  
//         // interpolate
//         if (r < hmdim - 1)
//         {
//             rconvmodelft[op] = finterp(rmodelft, r);
//         }
//         else
//         {
//             rconvmodelft[op] = 0.;
//         }
//     }
    
//     //deallocate rs
//     delete rs;
    
// // end of optimised floating point algorithm

    return 0;
}


int createshiftft(double xpos, double ypos, int dim,
                  double *A, double x_offset, double y_offset,
                  fcomplex *xshiftft, fcomplex *yshiftft)
{
    // apply astrometric distortion
    double det = A[0] * A[3] - A[1] * A[2];
    double xpos1 = (A[3] * xpos - A[1] * ypos) / det;
    double ypos1 = (-A[2] * xpos + A[0] * ypos) / det;

    // apply pixel offset
    xpos1 += x_offset;
    ypos1 += y_offset;

    // set dimensions
    int hdim = dim / 2;
    double dhdim = (double) hdim;

    // loop to create shift
    int p, pp;
    double arg;
    const std::complex<double> i(0.0,1.0);

    // first handle the x-axis up to the Nyquist frequency
    for (p=0; p<hdim; p++)
    {
        arg = xpos1 * M_PI * (double)p / dhdim;
        xshiftft[p] = std::cos(arg) - i * std::sin(arg);
    }

    // now the x-axis Nyquist frequency (this has to be treated as
    // having negative frequency and hence has a sign change on the
    // imaginary part)
    p = hdim;
    arg = xpos1 * M_PI;
    xshiftft[p] = std::cos(arg) + i * std::sin(arg);

    // now treat the y-axis.  split into positive and negative frequency segments
    for (p=0; p<hdim; p++)
    {
        arg = ypos1 * M_PI * (double)p / dhdim;
        yshiftft[p] = std::cos(arg) - i * std::sin(arg);
    }

    for (p=hdim; p<dim; p++)
    {
        pp = p-dim;
        arg = ypos1 * M_PI * (double)pp / dhdim;
        yshiftft[p] = std::cos(arg) - i * std::sin(arg);
    }
    
    return 0;
}


int convolve(int dim, fcomplex *convmodelft, float *rconvmodelft, fcomplex *psfft, fcomplex *xshiftft, fcomplex *yshiftft)
{
    // Fourier domain operations for image-domain convolution
    // multiply all the Fourier transforms together

    int hdim = 1 + dim / 2;

    int x, y, p;
    fcomplex fs;

    for (y=0; y<dim; y++)
    {
        for (x=0; x<hdim; x++)
        {
            p = y * hdim + x;
            fs = psfft[p] * xshiftft[x] * yshiftft[y];
            convmodelft[p] = rconvmodelft[p] * fs;
        }
    }
    
    return 0;
}


int convolve2(int dim, fcomplex *convmodelft, fcomplex *psfft, fcomplex *xshiftft, fcomplex *yshiftft)
{
    // Fourier domain operations for image-domain convolution
    // multiply all the Fourier transforms together
    // this version excludes the resamples model for purpose as it is used for star model making

    int hdim = 1 + dim / 2;

    int x, y, p;

    for (y=0; y<dim; y++)
    {
        for (x=0; x<hdim; x++)
        {
            p = y * hdim + x;
            convmodelft[p] = psfft[p] * xshiftft[x] * yshiftft[y];
        }
    }

    return 0;
}


void alias(int dim, int odim, fcomplex *in, fcomplex *out)
{
    // function to alias large 2D hermitian array into a smaller 2D (non-hermitian) array
    // assumes FFTW convention for hermitian array storage

    // define coordinate in input FT that contains zero frequency component
    int cen = 0;
    // define coordinate in output FT that contains zero frequency component
    int ocen = 0;

    // define a coordinate offset so that values always stay positive
    // but which is a multiple of the output dimension
    // such that the defined zero-frequency component of the input array
    // is mapped onto the defined zero-frequency component of the output array
    int offset = odim * (1 + (dim / odim)) + ocen - cen;

    // initialise output to zero
    int op;
    int odim2 = odim * odim;
    for (op=0; op<odim2; op++)
    {
        out[op] = 0.;
    }

    // define halfwidth of hermitian half arrays along x-axis
    int hdim = 1 + dim / 2;

    // declare variables
    int x, y, yy, ip;
    int *xx;

    // equalise weight of the redundant elements
    int yhdim;
    int hdim1 = hdim - 1;
    for (y=0; y<dim; y++)
    {
        yhdim = y * hdim;
        in[yhdim] *= 0.5;
        in[yhdim + hdim1] *= 0.5;
    }

    //create array to store "(x + offset) % odim" for each x, so we don't have to re-calculate the modulo in the inner loop
    // as modulo is relatively expensive
    xx = new int[hdim];
    // calculate x coordinate in downsampled array
    for (x=0; x<hdim; x++){
        xx[x] = (x + offset) % odim;
    }

    // loop through FT array and alias-downsample
    for (y=0; y<dim; y++)
    {
        // calculate y coordinate in downsampled array
        yy = (y + offset) % odim;

        for (x=0; x<hdim; x++)
        {
            // indices for the input and output arrays
            ip = y * hdim + x;
            op = yy * odim + xx[x];

            out[op] += in[ip];
        }
    }
    
    //deallocate xx
    delete xx;

    // renormalise
    float norm = 1. / std::real(out[0]);
    for (op=0; op<odim2; op++)
    {
        out[op] *= norm;
    }
}
