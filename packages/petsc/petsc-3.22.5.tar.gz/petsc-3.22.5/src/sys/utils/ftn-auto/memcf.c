#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* memc.c */
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

#include "petscsys.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscmemcmp_ PETSCMEMCMP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscmemcmp_ petscmemcmp
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscprocessplacementview_ PETSCPROCESSPLACEMENTVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscprocessplacementview_ petscprocessplacementview
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscmemcmp_( void*str1, void*str2,size_t *len,PetscBool *e, int *ierr)
{
*ierr = PetscMemcmp(str1,str2,*len,e);
}
PETSC_EXTERN void  petscprocessplacementview_(PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscProcessPlacementView(PetscPatchDefaultViewers((PetscViewer*)viewer));
}
#if defined(__cplusplus)
}
#endif
