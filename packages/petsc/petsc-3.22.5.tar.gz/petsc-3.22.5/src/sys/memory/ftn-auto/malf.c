#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* mal.c */
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
#define petscmallocclear_ PETSCMALLOCCLEAR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscmallocclear_ petscmallocclear
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscmallocsetdram_ PETSCMALLOCSETDRAM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscmallocsetdram_ petscmallocsetdram
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscmallocresetdram_ PETSCMALLOCRESETDRAM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscmallocresetdram_ petscmallocresetdram
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscmallocsetcoalesce_ PETSCMALLOCSETCOALESCE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscmallocsetcoalesce_ petscmallocsetcoalesce
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscmallocclear_(int *ierr)
{
*ierr = PetscMallocClear();
}
PETSC_EXTERN void  petscmallocsetdram_(int *ierr)
{
*ierr = PetscMallocSetDRAM();
}
PETSC_EXTERN void  petscmallocresetdram_(int *ierr)
{
*ierr = PetscMallocResetDRAM();
}
PETSC_EXTERN void  petscmallocsetcoalesce_(PetscBool *coalesce, int *ierr)
{
*ierr = PetscMallocSetCoalesce(*coalesce);
}
#if defined(__cplusplus)
}
#endif
