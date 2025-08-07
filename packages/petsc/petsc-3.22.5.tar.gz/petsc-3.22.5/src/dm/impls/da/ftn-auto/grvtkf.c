#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* grvtk.c */
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
#define dmdavtkwriteall_ DMDAVTKWRITEALL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmdavtkwriteall_ dmdavtkwriteall
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmdavtkwriteall_(PetscObject odm,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(odm);
CHKFORTRANNULLOBJECT(viewer);
*ierr = DMDAVTKWriteAll(
	(PetscObject)PetscToPointer((odm) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
#if defined(__cplusplus)
}
#endif
