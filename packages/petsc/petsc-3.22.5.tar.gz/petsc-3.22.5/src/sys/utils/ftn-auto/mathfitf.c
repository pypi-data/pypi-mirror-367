#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* mathfit.c */
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

#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclinearregression_ PETSCLINEARREGRESSION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclinearregression_ petsclinearregression
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petsclinearregression_(PetscInt *n, PetscReal x[], PetscReal y[],PetscReal *slope,PetscReal *intercept, int *ierr)
{
CHKFORTRANNULLREAL(x);
CHKFORTRANNULLREAL(y);
CHKFORTRANNULLREAL(slope);
CHKFORTRANNULLREAL(intercept);
*ierr = PetscLinearRegression(*n,x,y,slope,intercept);
}
#if defined(__cplusplus)
}
#endif
