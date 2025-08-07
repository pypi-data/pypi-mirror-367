#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* productutils.c */
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

#include "petsc/private/dmproductimpl.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmproductgetdm_ DMPRODUCTGETDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmproductgetdm_ dmproductgetdm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmproductsetdm_ DMPRODUCTSETDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmproductsetdm_ dmproductsetdm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmproductsetdimensionindex_ DMPRODUCTSETDIMENSIONINDEX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmproductsetdimensionindex_ dmproductsetdimensionindex
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmproductgetdm_(DM dm,PetscInt *slot,DM *subdm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool subdm_null = !*(void**) subdm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(subdm);
*ierr = DMProductGetDM(
	(DM)PetscToPointer((dm) ),*slot,subdm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! subdm_null && !*(void**) subdm) * (void **) subdm = (void *)-2;
}
PETSC_EXTERN void  dmproductsetdm_(DM dm,PetscInt *slot,DM subdm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(subdm);
*ierr = DMProductSetDM(
	(DM)PetscToPointer((dm) ),*slot,
	(DM)PetscToPointer((subdm) ));
}
PETSC_EXTERN void  dmproductsetdimensionindex_(DM dm,PetscInt *slot,PetscInt *idx, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMProductSetDimensionIndex(
	(DM)PetscToPointer((dm) ),*slot,*idx);
}
#if defined(__cplusplus)
}
#endif
