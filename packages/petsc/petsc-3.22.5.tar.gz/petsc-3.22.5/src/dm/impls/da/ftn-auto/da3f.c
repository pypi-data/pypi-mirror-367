#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* da3.c */
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
#define dmdacreate3d_ DMDACREATE3D
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmdacreate3d_ dmdacreate3d
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmdacreate3d_(MPI_Fint * comm,DMBoundaryType *bx,DMBoundaryType *by,DMBoundaryType *bz,DMDAStencilType *stencil_type,PetscInt *M,PetscInt *N,PetscInt *P,PetscInt *m,PetscInt *n,PetscInt *p,PetscInt *dof,PetscInt *s, PetscInt lx[], PetscInt ly[], PetscInt lz[],DM *da, int *ierr)
{
CHKFORTRANNULLINTEGER(lx);
CHKFORTRANNULLINTEGER(ly);
CHKFORTRANNULLINTEGER(lz);
PetscBool da_null = !*(void**) da ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(da);
*ierr = DMDACreate3d(
	MPI_Comm_f2c(*(comm)),*bx,*by,*bz,*stencil_type,*M,*N,*P,*m,*n,*p,*dof,*s,lx,ly,lz,da);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! da_null && !*(void**) da) * (void **) da = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
