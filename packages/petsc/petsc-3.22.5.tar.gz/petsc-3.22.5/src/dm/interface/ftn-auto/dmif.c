#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* dmi.c */
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
#define dmcreatesectionsubdm_ DMCREATESECTIONSUBDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcreatesectionsubdm_ dmcreatesectionsubdm
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmcreatesectionsubdm_(DM dm,PetscInt *numFields, PetscInt fields[], PetscInt numComps[], PetscInt comps[],IS *is,DM *subdm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(fields);
CHKFORTRANNULLINTEGER(numComps);
CHKFORTRANNULLINTEGER(comps);
PetscBool is_null = !*(void**) is ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is);
PetscBool subdm_null = !*(void**) subdm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(subdm);
*ierr = DMCreateSectionSubDM(
	(DM)PetscToPointer((dm) ),*numFields,fields,numComps,comps,is,subdm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is_null && !*(void**) is) * (void **) is = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! subdm_null && !*(void**) subdm) * (void **) subdm = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
