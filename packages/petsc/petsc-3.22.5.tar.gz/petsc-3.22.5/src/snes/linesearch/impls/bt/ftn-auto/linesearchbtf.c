#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* linesearchbt.c */
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

#include "petscsnes.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchbtsetalpha_ SNESLINESEARCHBTSETALPHA
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchbtsetalpha_ sneslinesearchbtsetalpha
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchbtgetalpha_ SNESLINESEARCHBTGETALPHA
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchbtgetalpha_ sneslinesearchbtgetalpha
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  sneslinesearchbtsetalpha_(SNESLineSearch linesearch,PetscReal *alpha, int *ierr)
{
CHKFORTRANNULLOBJECT(linesearch);
*ierr = SNESLineSearchBTSetAlpha(
	(SNESLineSearch)PetscToPointer((linesearch) ),*alpha);
}
PETSC_EXTERN void  sneslinesearchbtgetalpha_(SNESLineSearch linesearch,PetscReal *alpha, int *ierr)
{
CHKFORTRANNULLOBJECT(linesearch);
CHKFORTRANNULLREAL(alpha);
*ierr = SNESLineSearchBTGetAlpha(
	(SNESLineSearch)PetscToPointer((linesearch) ),alpha);
}
#if defined(__cplusplus)
}
#endif
