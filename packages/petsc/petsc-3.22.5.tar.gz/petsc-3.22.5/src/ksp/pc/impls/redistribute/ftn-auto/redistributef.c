#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* redistribute.c */
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

#include "petscksp.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcredistributegetksp_ PCREDISTRIBUTEGETKSP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcredistributegetksp_ pcredistributegetksp
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  pcredistributegetksp_(PC pc,KSP *innerksp, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool innerksp_null = !*(void**) innerksp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(innerksp);
*ierr = PCRedistributeGetKSP(
	(PC)PetscToPointer((pc) ),innerksp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! innerksp_null && !*(void**) innerksp) * (void **) innerksp = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
