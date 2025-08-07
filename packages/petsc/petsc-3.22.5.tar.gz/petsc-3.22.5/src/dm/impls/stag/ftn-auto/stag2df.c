#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* stag2d.c */
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

#include "petscdmstag.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmstagcreate2d_ DMSTAGCREATE2D
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstagcreate2d_ dmstagcreate2d
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmstagcreate2d_(MPI_Fint * comm,DMBoundaryType *bndx,DMBoundaryType *bndy,PetscInt *M,PetscInt *N,PetscInt *m,PetscInt *n,PetscInt *dof0,PetscInt *dof1,PetscInt *dof2,DMStagStencilType *stencilType,PetscInt *stencilWidth, PetscInt lx[], PetscInt ly[],DM *dm, int *ierr)
{
CHKFORTRANNULLINTEGER(lx);
CHKFORTRANNULLINTEGER(ly);
PetscBool dm_null = !*(void**) dm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMStagCreate2d(
	MPI_Comm_f2c(*(comm)),*bndx,*bndy,*M,*N,*m,*n,*dof0,*dof1,*dof2,*stencilType,*stencilWidth,lx,ly,dm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dm_null && !*(void**) dm) * (void **) dm = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
