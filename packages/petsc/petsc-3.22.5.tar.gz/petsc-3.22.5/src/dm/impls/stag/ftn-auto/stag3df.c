#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* stag3d.c */
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
#define dmstagcreate3d_ DMSTAGCREATE3D
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstagcreate3d_ dmstagcreate3d
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmstagcreate3d_(MPI_Fint * comm,DMBoundaryType *bndx,DMBoundaryType *bndy,DMBoundaryType *bndz,PetscInt *M,PetscInt *N,PetscInt *P,PetscInt *m,PetscInt *n,PetscInt *p,PetscInt *dof0,PetscInt *dof1,PetscInt *dof2,PetscInt *dof3,DMStagStencilType *stencilType,PetscInt *stencilWidth, PetscInt lx[], PetscInt ly[], PetscInt lz[],DM *dm, int *ierr)
{
CHKFORTRANNULLINTEGER(lx);
CHKFORTRANNULLINTEGER(ly);
CHKFORTRANNULLINTEGER(lz);
PetscBool dm_null = !*(void**) dm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMStagCreate3d(
	MPI_Comm_f2c(*(comm)),*bndx,*bndy,*bndz,*M,*N,*P,*m,*n,*p,*dof0,*dof1,*dof2,*dof3,*stencilType,*stencilWidth,lx,ly,lz,dm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dm_null && !*(void**) dm) * (void **) dm = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
