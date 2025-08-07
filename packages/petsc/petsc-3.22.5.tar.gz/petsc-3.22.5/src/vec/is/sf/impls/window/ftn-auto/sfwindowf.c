#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* sfwindow.c */
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

#include "petscsf.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfwindowsetflavortype_ PETSCSFWINDOWSETFLAVORTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfwindowsetflavortype_ petscsfwindowsetflavortype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfwindowgetflavortype_ PETSCSFWINDOWGETFLAVORTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfwindowgetflavortype_ petscsfwindowgetflavortype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfwindowsetsynctype_ PETSCSFWINDOWSETSYNCTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfwindowsetsynctype_ petscsfwindowsetsynctype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfwindowgetsynctype_ PETSCSFWINDOWGETSYNCTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfwindowgetsynctype_ petscsfwindowgetsynctype
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscsfwindowsetflavortype_(PetscSF sf,PetscSFWindowFlavorType *flavor, int *ierr)
{
CHKFORTRANNULLOBJECT(sf);
*ierr = PetscSFWindowSetFlavorType(
	(PetscSF)PetscToPointer((sf) ),*flavor);
}
PETSC_EXTERN void  petscsfwindowgetflavortype_(PetscSF sf,PetscSFWindowFlavorType *flavor, int *ierr)
{
CHKFORTRANNULLOBJECT(sf);
*ierr = PetscSFWindowGetFlavorType(
	(PetscSF)PetscToPointer((sf) ),flavor);
}
PETSC_EXTERN void  petscsfwindowsetsynctype_(PetscSF sf,PetscSFWindowSyncType *sync, int *ierr)
{
CHKFORTRANNULLOBJECT(sf);
*ierr = PetscSFWindowSetSyncType(
	(PetscSF)PetscToPointer((sf) ),*sync);
}
PETSC_EXTERN void  petscsfwindowgetsynctype_(PetscSF sf,PetscSFWindowSyncType *sync, int *ierr)
{
CHKFORTRANNULLOBJECT(sf);
*ierr = PetscSFWindowGetSyncType(
	(PetscSF)PetscToPointer((sf) ),sync);
}
#if defined(__cplusplus)
}
#endif
