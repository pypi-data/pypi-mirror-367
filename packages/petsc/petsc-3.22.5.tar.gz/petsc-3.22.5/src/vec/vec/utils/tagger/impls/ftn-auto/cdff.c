#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* cdf.c */
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

#include "petscvec.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vectaggercdfsetmethod_ VECTAGGERCDFSETMETHOD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vectaggercdfsetmethod_ vectaggercdfsetmethod
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vectaggercdfgetmethod_ VECTAGGERCDFGETMETHOD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vectaggercdfgetmethod_ vectaggercdfgetmethod
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vectaggercdfiterativegettolerances_ VECTAGGERCDFITERATIVEGETTOLERANCES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vectaggercdfiterativegettolerances_ vectaggercdfiterativegettolerances
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  vectaggercdfsetmethod_(VecTagger tagger,VecTaggerCDFMethod *method, int *ierr)
{
CHKFORTRANNULLOBJECT(tagger);
*ierr = VecTaggerCDFSetMethod(
	(VecTagger)PetscToPointer((tagger) ),*method);
}
PETSC_EXTERN void  vectaggercdfgetmethod_(VecTagger tagger,VecTaggerCDFMethod *method, int *ierr)
{
CHKFORTRANNULLOBJECT(tagger);
*ierr = VecTaggerCDFGetMethod(
	(VecTagger)PetscToPointer((tagger) ),method);
}
PETSC_EXTERN void  vectaggercdfiterativegettolerances_(VecTagger tagger,PetscInt *maxit,PetscReal *rtol,PetscReal *atol, int *ierr)
{
CHKFORTRANNULLOBJECT(tagger);
CHKFORTRANNULLINTEGER(maxit);
CHKFORTRANNULLREAL(rtol);
CHKFORTRANNULLREAL(atol);
*ierr = VecTaggerCDFIterativeGetTolerances(
	(VecTagger)PetscToPointer((tagger) ),maxit,rtol,atol);
}
#if defined(__cplusplus)
}
#endif
