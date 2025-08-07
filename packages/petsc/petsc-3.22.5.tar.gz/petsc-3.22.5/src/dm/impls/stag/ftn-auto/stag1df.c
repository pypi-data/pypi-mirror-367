#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* stag1d.c */
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
#define dmstagcreate1d_ DMSTAGCREATE1D
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmstagcreate1d_ dmstagcreate1d
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmstagcreate1d_(MPI_Fint * comm,DMBoundaryType *bndx,PetscInt *M,PetscInt *dof0,PetscInt *dof1,DMStagStencilType *stencilType,PetscInt *stencilWidth, PetscInt lx[],DM *dm, int *ierr)
{
CHKFORTRANNULLINTEGER(lx);
PetscBool dm_null = !*(void**) dm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMStagCreate1d(
	MPI_Comm_f2c(*(comm)),*bndx,*M,*dof0,*dof1,*stencilType,*stencilWidth,lx,dm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dm_null && !*(void**) dm) * (void **) dm = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
