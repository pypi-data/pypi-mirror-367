#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* dmgeommodel.c */
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

#include "petscdm.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetsnaptogeommodel_ DMSETSNAPTOGEOMMODEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetsnaptogeommodel_ dmsetsnaptogeommodel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsnaptogeommodel_ DMSNAPTOGEOMMODEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsnaptogeommodel_ dmsnaptogeommodel
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmsetsnaptogeommodel_(DM dm, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMSetSnapToGeomModel(
	(DM)PetscToPointer((dm) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  dmsnaptogeommodel_(DM dm,PetscInt *p,PetscInt *dE, PetscScalar mcoords[],PetscScalar gcoords[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLSCALAR(mcoords);
CHKFORTRANNULLSCALAR(gcoords);
*ierr = DMSnapToGeomModel(
	(DM)PetscToPointer((dm) ),*p,*dE,mcoords,gcoords);
}
#if defined(__cplusplus)
}
#endif
