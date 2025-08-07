#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* fftw.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscmat.h"
#include "petscvec.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreatevecsfftw_ MATCREATEVECSFFTW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreatevecsfftw_ matcreatevecsfftw
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecscatterpetsctofftw_ VECSCATTERPETSCTOFFTW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecscatterpetsctofftw_ vecscatterpetsctofftw
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecscatterfftwtopetsc_ VECSCATTERFFTWTOPETSC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecscatterfftwtopetsc_ vecscatterfftwtopetsc
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matcreatevecsfftw_(Mat A,Vec *x,Vec *y,Vec *z, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool x_null = !*(void**) x ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(x);
PetscBool y_null = !*(void**) y ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(y);
PetscBool z_null = !*(void**) z ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(z);
*ierr = MatCreateVecsFFTW(
	(Mat)PetscToPointer((A) ),x,y,z);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! x_null && !*(void**) x) * (void **) x = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! y_null && !*(void**) y) * (void **) y = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! z_null && !*(void**) z) * (void **) z = (void *)-2;
}
PETSC_EXTERN void  vecscatterpetsctofftw_(Mat A,Vec x,Vec y, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(y);
*ierr = VecScatterPetscToFFTW(
	(Mat)PetscToPointer((A) ),
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((y) ));
}
PETSC_EXTERN void  vecscatterfftwtopetsc_(Mat A,Vec x,Vec y, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(y);
*ierr = VecScatterFFTWToPetsc(
	(Mat)PetscToPointer((A) ),
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((y) ));
}
#if defined(__cplusplus)
}
#endif
