#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* sortd.c */
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
#define petscsortedreal_ PETSCSORTEDREAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsortedreal_ petscsortedreal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsortreal_ PETSCSORTREAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsortreal_ petscsortreal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsortrealwitharrayint_ PETSCSORTREALWITHARRAYINT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsortrealwitharrayint_ petscsortrealwitharrayint
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfindreal_ PETSCFINDREAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfindreal_ petscfindreal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsortremovedupsreal_ PETSCSORTREMOVEDUPSREAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsortremovedupsreal_ petscsortremovedupsreal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsortsplit_ PETSCSORTSPLIT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsortsplit_ petscsortsplit
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsortsplitreal_ PETSCSORTSPLITREAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsortsplitreal_ petscsortsplitreal
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscsortedreal_(PetscCount *n, PetscReal X[],PetscBool *sorted, int *ierr)
{
CHKFORTRANNULLREAL(X);
*ierr = PetscSortedReal(*n,X,sorted);
}
PETSC_EXTERN void  petscsortreal_(PetscCount *n,PetscReal v[], int *ierr)
{
CHKFORTRANNULLREAL(v);
*ierr = PetscSortReal(*n,v);
}
PETSC_EXTERN void  petscsortrealwitharrayint_(PetscCount *n,PetscReal r[],PetscInt Ii[], int *ierr)
{
CHKFORTRANNULLREAL(r);
CHKFORTRANNULLINTEGER(Ii);
*ierr = PetscSortRealWithArrayInt(*n,r,Ii);
}
PETSC_EXTERN void  petscfindreal_(PetscReal *key,PetscCount *n, PetscReal t[],PetscReal *eps,PetscInt *loc, int *ierr)
{
CHKFORTRANNULLREAL(t);
CHKFORTRANNULLINTEGER(loc);
*ierr = PetscFindReal(*key,*n,t,*eps,loc);
}
PETSC_EXTERN void  petscsortremovedupsreal_(PetscInt *n,PetscReal v[], int *ierr)
{
CHKFORTRANNULLINTEGER(n);
CHKFORTRANNULLREAL(v);
*ierr = PetscSortRemoveDupsReal(n,v);
}
PETSC_EXTERN void  petscsortsplit_(PetscInt *ncut,PetscInt *n,PetscScalar a[],PetscInt idx[], int *ierr)
{
CHKFORTRANNULLSCALAR(a);
CHKFORTRANNULLINTEGER(idx);
*ierr = PetscSortSplit(*ncut,*n,a,idx);
}
PETSC_EXTERN void  petscsortsplitreal_(PetscInt *ncut,PetscInt *n,PetscReal a[],PetscInt idx[], int *ierr)
{
CHKFORTRANNULLREAL(a);
CHKFORTRANNULLINTEGER(idx);
*ierr = PetscSortSplitReal(*ncut,*n,a,idx);
}
#if defined(__cplusplus)
}
#endif
