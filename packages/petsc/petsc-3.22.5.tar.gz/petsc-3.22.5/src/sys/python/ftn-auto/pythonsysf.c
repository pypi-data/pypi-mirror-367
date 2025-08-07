#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* pythonsys.c */
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
#define petscpythonfinalize_ PETSCPYTHONFINALIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscpythonfinalize_ petscpythonfinalize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscpythoninitialize_ PETSCPYTHONINITIALIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscpythoninitialize_ petscpythoninitialize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscpythonmonitorset_ PETSCPYTHONMONITORSET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscpythonmonitorset_ petscpythonmonitorset
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscpythonfinalize_(int *ierr)
{
*ierr = PetscPythonFinalize();
}
PETSC_EXTERN void  petscpythoninitialize_( char pyexe[], char pylib[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0, PETSC_FORTRAN_CHARLEN_T cl1)
{
  char *_cltmp0 = PETSC_NULLPTR;
  char *_cltmp1 = PETSC_NULLPTR;
/* insert Fortran-to-C conversion for pyexe */
  FIXCHAR(pyexe,cl0,_cltmp0);
/* insert Fortran-to-C conversion for pylib */
  FIXCHAR(pylib,cl1,_cltmp1);
*ierr = PetscPythonInitialize(_cltmp0,_cltmp1);
  FREECHAR(pyexe,_cltmp0);
  FREECHAR(pylib,_cltmp1);
}
PETSC_EXTERN void  petscpythonmonitorset_(PetscObject obj, char url[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for url */
  FIXCHAR(url,cl0,_cltmp0);
*ierr = PetscPythonMonitorSet(
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(url,_cltmp0);
}
#if defined(__cplusplus)
}
#endif
