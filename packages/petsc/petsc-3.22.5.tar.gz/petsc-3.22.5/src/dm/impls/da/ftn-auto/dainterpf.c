#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* dainterp.c */
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
#define dmcreateaggregates_ DMCREATEAGGREGATES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcreateaggregates_ dmcreateaggregates
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmdacreateaggregates_ DMDACREATEAGGREGATES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmdacreateaggregates_ dmdacreateaggregates
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmcreateaggregates_(DM dac,DM daf,Mat *mat, int *ierr)
{
CHKFORTRANNULLOBJECT(dac);
CHKFORTRANNULLOBJECT(daf);
PetscBool mat_null = !*(void**) mat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mat);
*ierr = DMCreateAggregates(
	(DM)PetscToPointer((dac) ),
	(DM)PetscToPointer((daf) ),mat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mat_null && !*(void**) mat) * (void **) mat = (void *)-2;
}
PETSC_EXTERN void  dmdacreateaggregates_(DM dac,DM daf,Mat *rest, int *ierr)
{
CHKFORTRANNULLOBJECT(dac);
CHKFORTRANNULLOBJECT(daf);
PetscBool rest_null = !*(void**) rest ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(rest);
*ierr = DMDACreateAggregates(
	(DM)PetscToPointer((dac) ),
	(DM)PetscToPointer((daf) ),rest);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! rest_null && !*(void**) rest) * (void **) rest = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
