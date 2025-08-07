#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* dmlabelephplex.c */
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

#include "petscdmlabelephemeral.h"
#include "petscdmplextransform.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelephemeralgettransform_ DMLABELEPHEMERALGETTRANSFORM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelephemeralgettransform_ dmlabelephemeralgettransform
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelephemeralsettransform_ DMLABELEPHEMERALSETTRANSFORM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelephemeralsettransform_ dmlabelephemeralsettransform
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmlabelephemeralgettransform_(DMLabel label,DMPlexTransform *tr, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
PetscBool tr_null = !*(void**) tr ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(tr);
*ierr = DMLabelEphemeralGetTransform(
	(DMLabel)PetscToPointer((label) ),tr);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! tr_null && !*(void**) tr) * (void **) tr = (void *)-2;
}
PETSC_EXTERN void  dmlabelephemeralsettransform_(DMLabel label,DMPlexTransform tr, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
CHKFORTRANNULLOBJECT(tr);
*ierr = DMLabelEphemeralSetTransform(
	(DMLabel)PetscToPointer((label) ),
	(DMPlexTransform)PetscToPointer((tr) ));
}
#if defined(__cplusplus)
}
#endif
