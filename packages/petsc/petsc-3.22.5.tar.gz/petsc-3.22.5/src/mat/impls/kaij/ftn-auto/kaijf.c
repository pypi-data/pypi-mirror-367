#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* kaij.c */
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

#include "petscmat.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matkaijgetaij_ MATKAIJGETAIJ
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matkaijgetaij_ matkaijgetaij
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matkaijsetaij_ MATKAIJSETAIJ
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matkaijsetaij_ matkaijsetaij
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matkaijsets_ MATKAIJSETS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matkaijsets_ matkaijsets
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matkaijgetscaledidentity_ MATKAIJGETSCALEDIDENTITY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matkaijgetscaledidentity_ matkaijgetscaledidentity
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matkaijsett_ MATKAIJSETT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matkaijsett_ matkaijsett
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matkaijgetaij_(Mat A,Mat *B, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool B_null = !*(void**) B ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(B);
*ierr = MatKAIJGetAIJ(
	(Mat)PetscToPointer((A) ),B);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! B_null && !*(void**) B) * (void **) B = (void *)-2;
}
PETSC_EXTERN void  matkaijsetaij_(Mat A,Mat B, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(B);
*ierr = MatKAIJSetAIJ(
	(Mat)PetscToPointer((A) ),
	(Mat)PetscToPointer((B) ));
}
PETSC_EXTERN void  matkaijsets_(Mat A,PetscInt *p,PetscInt *q, PetscScalar S[], int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLSCALAR(S);
*ierr = MatKAIJSetS(
	(Mat)PetscToPointer((A) ),*p,*q,S);
}
PETSC_EXTERN void  matkaijgetscaledidentity_(Mat A,PetscBool *identity, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatKAIJGetScaledIdentity(
	(Mat)PetscToPointer((A) ),identity);
}
PETSC_EXTERN void  matkaijsett_(Mat A,PetscInt *p,PetscInt *q, PetscScalar T[], int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLSCALAR(T);
*ierr = MatKAIJSetT(
	(Mat)PetscToPointer((A) ),*p,*q,T);
}
#if defined(__cplusplus)
}
#endif
