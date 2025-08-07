#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* fdmpiaij.c */
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
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfdcoloringsetvalues_ MATFDCOLORINGSETVALUES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfdcoloringsetvalues_ matfdcoloringsetvalues
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matfdcoloringsetvalues_(Mat J,MatFDColoring coloring, PetscScalar y[], int *ierr)
{
CHKFORTRANNULLOBJECT(J);
CHKFORTRANNULLOBJECT(coloring);
CHKFORTRANNULLSCALAR(y);
*ierr = MatFDColoringSetValues(
	(Mat)PetscToPointer((J) ),
	(MatFDColoring)PetscToPointer((coloring) ),y);
}
#if defined(__cplusplus)
}
#endif
