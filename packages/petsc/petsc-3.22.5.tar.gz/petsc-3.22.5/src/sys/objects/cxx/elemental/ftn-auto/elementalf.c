#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* elemental.cxx */
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

#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscelementalinitializepackage_ PETSCELEMENTALINITIALIZEPACKAGE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscelementalinitializepackage_ petscelementalinitializepackage
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscelementalinitialized_ PETSCELEMENTALINITIALIZED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscelementalinitialized_ petscelementalinitialized
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscelementalfinalizepackage_ PETSCELEMENTALFINALIZEPACKAGE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscelementalfinalizepackage_ petscelementalfinalizepackage
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscelementalinitializepackage_(int *ierr)
{
*ierr = PetscElementalInitializePackage();
}
PETSC_EXTERN void  petscelementalinitialized_(PetscBool *isInitialized, int *ierr)
{
*ierr = PetscElementalInitialized(isInitialized);
}
PETSC_EXTERN void  petscelementalfinalizepackage_(int *ierr)
{
*ierr = PetscElementalFinalizePackage();
}
#if defined(__cplusplus)
}
#endif
