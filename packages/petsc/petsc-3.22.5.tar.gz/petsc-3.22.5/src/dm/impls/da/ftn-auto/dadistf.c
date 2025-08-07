#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* dadist.c */
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
#define dmdacreatenaturalvector_ DMDACREATENATURALVECTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmdacreatenaturalvector_ dmdacreatenaturalvector
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmdacreatenaturalvector_(DM da,Vec *g, int *ierr)
{
CHKFORTRANNULLOBJECT(da);
PetscBool g_null = !*(void**) g ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(g);
*ierr = DMDACreateNaturalVector(
	(DM)PetscToPointer((da) ),g);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! g_null && !*(void**) g) * (void **) g = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
