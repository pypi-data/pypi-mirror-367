#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* plexreorder.c */
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

#include "petscdmplex.h"
#include "petscmat.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetordering1d_ DMPLEXGETORDERING1D
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetordering1d_ dmplexgetordering1d
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexpermute_ DMPLEXPERMUTE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexpermute_ dmplexpermute
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexreordersetdefault_ DMPLEXREORDERSETDEFAULT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexreordersetdefault_ dmplexreordersetdefault
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexreordergetdefault_ DMPLEXREORDERGETDEFAULT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexreordergetdefault_ dmplexreordergetdefault
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmplexgetordering1d_(DM dm,IS *perm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool perm_null = !*(void**) perm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(perm);
*ierr = DMPlexGetOrdering1D(
	(DM)PetscToPointer((dm) ),perm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! perm_null && !*(void**) perm) * (void **) perm = (void *)-2;
}
PETSC_EXTERN void  dmplexpermute_(DM dm,IS perm,DM *pdm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(perm);
PetscBool pdm_null = !*(void**) pdm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(pdm);
*ierr = DMPlexPermute(
	(DM)PetscToPointer((dm) ),
	(IS)PetscToPointer((perm) ),pdm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! pdm_null && !*(void**) pdm) * (void **) pdm = (void *)-2;
}
PETSC_EXTERN void  dmplexreordersetdefault_(DM dm,DMReorderDefaultFlag *reorder, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexReorderSetDefault(
	(DM)PetscToPointer((dm) ),*reorder);
}
PETSC_EXTERN void  dmplexreordergetdefault_(DM dm,DMReorderDefaultFlag *reorder, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexReorderGetDefault(
	(DM)PetscToPointer((dm) ),reorder);
}
#if defined(__cplusplus)
}
#endif
