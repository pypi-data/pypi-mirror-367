#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* version.c */
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
#define petscgetversionnumber_ PETSCGETVERSIONNUMBER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscgetversionnumber_ petscgetversionnumber
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscblassetnumthreads_ PETSCBLASSETNUMTHREADS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscblassetnumthreads_ petscblassetnumthreads
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscblasgetnumthreads_ PETSCBLASGETNUMTHREADS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscblasgetnumthreads_ petscblasgetnumthreads
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscgetversionnumber_(PetscInt *major,PetscInt *minor,PetscInt *subminor,PetscInt *release, int *ierr)
{
CHKFORTRANNULLINTEGER(major);
CHKFORTRANNULLINTEGER(minor);
CHKFORTRANNULLINTEGER(subminor);
CHKFORTRANNULLINTEGER(release);
*ierr = PetscGetVersionNumber(major,minor,subminor,release);
}
PETSC_EXTERN void  petscblassetnumthreads_(PetscInt *nt, int *ierr)
{
*ierr = PetscBLASSetNumThreads(*nt);
}
PETSC_EXTERN void  petscblasgetnumthreads_(PetscInt *nt, int *ierr)
{
CHKFORTRANNULLINTEGER(nt);
*ierr = PetscBLASGetNumThreads(nt);
}
#if defined(__cplusplus)
}
#endif
