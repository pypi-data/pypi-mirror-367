#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* petsctime.h */
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
#define petsctime_ PETSCTIME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsctime_ petsctime
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsctimesubtract_ PETSCTIMESUBTRACT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsctimesubtract_ petsctimesubtract
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsctimeadd_ PETSCTIMEADD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsctimeadd_ petsctimeadd
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petsctime_(PetscLogDouble *v, int *ierr)
{
*ierr = PetscTime(v);
}
PETSC_EXTERN void  petsctimesubtract_(PetscLogDouble *v, int *ierr)
{
*ierr = PetscTimeSubtract(v);
}
PETSC_EXTERN void  petsctimeadd_(PetscLogDouble *v, int *ierr)
{
*ierr = PetscTimeAdd(v);
}
#if defined(__cplusplus)
}
#endif
