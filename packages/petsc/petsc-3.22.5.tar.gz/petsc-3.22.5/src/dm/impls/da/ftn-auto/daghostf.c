#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* daghost.c */
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

#include "petscdmda.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmdagetghostcorners_ DMDAGETGHOSTCORNERS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmdagetghostcorners_ dmdagetghostcorners
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmdagetghostcorners_(DM da,PetscInt *x,PetscInt *y,PetscInt *z,PetscInt *m,PetscInt *n,PetscInt *p, int *ierr)
{
CHKFORTRANNULLOBJECT(da);
CHKFORTRANNULLINTEGER(x);
CHKFORTRANNULLINTEGER(y);
CHKFORTRANNULLINTEGER(z);
CHKFORTRANNULLINTEGER(m);
CHKFORTRANNULLINTEGER(n);
CHKFORTRANNULLINTEGER(p);
*ierr = DMDAGetGhostCorners(
	(DM)PetscToPointer((da) ),x,y,z,m,n,p);
}
#if defined(__cplusplus)
}
#endif
