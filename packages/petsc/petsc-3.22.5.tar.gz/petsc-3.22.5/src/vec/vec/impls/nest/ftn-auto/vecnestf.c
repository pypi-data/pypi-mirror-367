#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* vecnest.c */
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

#include "petscvec.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecnestgetsubvec_ VECNESTGETSUBVEC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecnestgetsubvec_ vecnestgetsubvec
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecnestsetsubvec_ VECNESTSETSUBVEC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecnestsetsubvec_ vecnestsetsubvec
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecnestsetsubvecs_ VECNESTSETSUBVECS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecnestsetsubvecs_ vecnestsetsubvecs
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecnestgetsize_ VECNESTGETSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecnestgetsize_ vecnestgetsize
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  vecnestgetsubvec_(Vec X,PetscInt *idxm,Vec *sx, int *ierr)
{
CHKFORTRANNULLOBJECT(X);
PetscBool sx_null = !*(void**) sx ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sx);
*ierr = VecNestGetSubVec(
	(Vec)PetscToPointer((X) ),*idxm,sx);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sx_null && !*(void**) sx) * (void **) sx = (void *)-2;
}
PETSC_EXTERN void  vecnestsetsubvec_(Vec X,PetscInt *idxm,Vec sx, int *ierr)
{
CHKFORTRANNULLOBJECT(X);
CHKFORTRANNULLOBJECT(sx);
*ierr = VecNestSetSubVec(
	(Vec)PetscToPointer((X) ),*idxm,
	(Vec)PetscToPointer((sx) ));
}
PETSC_EXTERN void  vecnestsetsubvecs_(Vec X,PetscInt *N,PetscInt idxm[],Vec sx[], int *ierr)
{
CHKFORTRANNULLOBJECT(X);
CHKFORTRANNULLINTEGER(idxm);
PetscBool sx_null = !*(void**) sx ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sx);
*ierr = VecNestSetSubVecs(
	(Vec)PetscToPointer((X) ),*N,idxm,sx);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sx_null && !*(void**) sx) * (void **) sx = (void *)-2;
}
PETSC_EXTERN void  vecnestgetsize_(Vec X,PetscInt *N, int *ierr)
{
CHKFORTRANNULLOBJECT(X);
CHKFORTRANNULLINTEGER(N);
*ierr = VecNestGetSize(
	(Vec)PetscToPointer((X) ),N);
}
#if defined(__cplusplus)
}
#endif
