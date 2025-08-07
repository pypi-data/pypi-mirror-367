#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* fp.c */
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
#define petscfptrappush_ PETSCFPTRAPPUSH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfptrappush_ petscfptrappush
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfptrappop_ PETSCFPTRAPPOP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfptrappop_ petscfptrappop
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsetfptrap_ PETSCSETFPTRAP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsetfptrap_ petscsetfptrap
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdetermineinitialfptrap_ PETSCDETERMINEINITIALFPTRAP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdetermineinitialfptrap_ petscdetermineinitialfptrap
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscfptrappush_(PetscFPTrap *trap, int *ierr)
{
*ierr = PetscFPTrapPush(*trap);
}
PETSC_EXTERN void  petscfptrappop_(int *ierr)
{
*ierr = PetscFPTrapPop();
}
PETSC_EXTERN void  petscsetfptrap_(PetscFPTrap *flag, int *ierr)
{
*ierr = PetscSetFPTrap(*flag);
}
PETSC_EXTERN void  petscdetermineinitialfptrap_(int *ierr)
{
*ierr = PetscDetermineInitialFPTrap();
}
#if defined(__cplusplus)
}
#endif
