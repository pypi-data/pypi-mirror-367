#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* err.c */
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
#define petscpoperrorhandler_ PETSCPOPERRORHANDLER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscpoperrorhandler_ petscpoperrorhandler
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscintview_ PETSCINTVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscintview_ petscintview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscrealview_ PETSCREALVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscrealview_ petscrealview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscscalarview_ PETSCSCALARVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscscalarview_ petscscalarview
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscpoperrorhandler_(int *ierr)
{
*ierr = PetscPopErrorHandler();
}
PETSC_EXTERN void  petscintview_(PetscInt *N, PetscInt idx[],PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLINTEGER(idx);
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscIntView(*N,idx,PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petscrealview_(PetscInt *N, PetscReal idx[],PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLREAL(idx);
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscRealView(*N,idx,PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petscscalarview_(PetscInt *N, PetscScalar idx[],PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLSCALAR(idx);
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscScalarView(*N,idx,PetscPatchDefaultViewers((PetscViewer*)viewer));
}
#if defined(__cplusplus)
}
#endif
