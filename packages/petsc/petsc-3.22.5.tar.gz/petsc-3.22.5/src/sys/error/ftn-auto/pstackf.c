#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* pstack.c */
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
#define petscstacksawsgrantaccess_ PETSCSTACKSAWSGRANTACCESS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscstacksawsgrantaccess_ petscstacksawsgrantaccess
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscstacksawstakeaccess_ PETSCSTACKSAWSTAKEACCESS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscstacksawstakeaccess_ petscstacksawstakeaccess
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscstacksawsgrantaccess_(int *ierr)
{
PetscStackSAWsGrantAccess();
}
PETSC_EXTERN void  petscstacksawstakeaccess_(int *ierr)
{
PetscStackSAWsTakeAccess();
}
#if defined(__cplusplus)
}
#endif
