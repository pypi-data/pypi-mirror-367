cdef extern from "fast_fourier_model.hpp" nogil:

    void generate_star_model(double xpos, double ypos,
                             double *A, double x_offset, double y_offset,
                             int odim, int osampl,
                             float complex *psfft,
                             float complex *xshiftft, float complex *yshiftft,
                             float complex *convmodelft, float complex *dsmodelft);
