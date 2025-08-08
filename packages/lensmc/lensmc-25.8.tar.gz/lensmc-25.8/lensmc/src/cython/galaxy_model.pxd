cdef extern from "fast_fourier_model.hpp" nogil:

    void generate_galaxy_model(double e1, double e2, double galsize, double xpos, double ypos,
                               int semimajor, double rfiducial,
                               double *A, double x_offset, double y_offset,
                               int odim, int mdim, int osampl,
                               float* rmodelft, float* resampledmodelft, float complex *psfft,
                               float complex *xshiftft, float complex *yshiftft,
                               float complex *convmodelft, float complex *dsmodelft,
                               int do_hankel_resample);

    void make_circular_galaxy(double n, double a, double rfiducial, int modeldim, int osampl, double *f);
