#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* daview.c */
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

#include "petscdmda.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmdagetinfo_ DMDAGETINFO
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmdagetinfo_ dmdagetinfo
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmdagetlocalinfo_ DMDAGETLOCALINFO
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmdagetlocalinfo_ dmdagetlocalinfo
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmdagetinfo_(DM da,PetscInt *dim,PetscInt *M,PetscInt *N,PetscInt *P,PetscInt *m,PetscInt *n,PetscInt *p,PetscInt *dof,PetscInt *s,DMBoundaryType *bx,DMBoundaryType *by,DMBoundaryType *bz,DMDAStencilType *st, int *ierr)
{
CHKFORTRANNULLOBJECT(da);
CHKFORTRANNULLINTEGER(dim);
CHKFORTRANNULLINTEGER(M);
CHKFORTRANNULLINTEGER(N);
CHKFORTRANNULLINTEGER(P);
CHKFORTRANNULLINTEGER(m);
CHKFORTRANNULLINTEGER(n);
CHKFORTRANNULLINTEGER(p);
CHKFORTRANNULLINTEGER(dof);
CHKFORTRANNULLINTEGER(s);
*ierr = DMDAGetInfo(
	(DM)PetscToPointer((da) ),dim,M,N,P,m,n,p,dof,s,bx,by,bz,st);
}
PETSC_EXTERN void  dmdagetlocalinfo_(DM da,DMDALocalInfo *info, int *ierr)
{
CHKFORTRANNULLOBJECT(da);
*ierr = DMDAGetLocalInfo(
	(DM)PetscToPointer((da) ),info);
}
#if defined(__cplusplus)
}
#endif
