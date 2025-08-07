#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* plexextrude.c */
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
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexextrude_ DMPLEXEXTRUDE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexextrude_ dmplexextrude
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmplexextrude_(DM dm,PetscInt *layers,PetscReal *thickness,PetscBool *tensor,PetscBool *symmetric,PetscBool *periodic, PetscReal normal[], PetscReal thicknesses[],DM *edm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLREAL(normal);
CHKFORTRANNULLREAL(thicknesses);
PetscBool edm_null = !*(void**) edm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(edm);
*ierr = DMPlexExtrude(
	(DM)PetscToPointer((dm) ),*layers,*thickness,*tensor,*symmetric,*periodic,normal,thicknesses,edm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! edm_null && !*(void**) edm) * (void **) edm = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
