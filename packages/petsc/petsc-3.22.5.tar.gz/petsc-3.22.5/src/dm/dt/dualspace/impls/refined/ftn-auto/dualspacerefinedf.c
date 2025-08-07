#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* dualspacerefined.c */
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

#include "petscfe.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacerefinedsetcellspaces_ PETSCDUALSPACEREFINEDSETCELLSPACES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacerefinedsetcellspaces_ petscdualspacerefinedsetcellspaces
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscdualspacerefinedsetcellspaces_(PetscDualSpace sp, PetscDualSpace cellSpaces[], int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
PetscBool cellSpaces_null = !*(void**) cellSpaces ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(cellSpaces);
*ierr = PetscDualSpaceRefinedSetCellSpaces(
	(PetscDualSpace)PetscToPointer((sp) ),cellSpaces);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! cellSpaces_null && !*(void**) cellSpaces) * (void **) cellSpaces = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
