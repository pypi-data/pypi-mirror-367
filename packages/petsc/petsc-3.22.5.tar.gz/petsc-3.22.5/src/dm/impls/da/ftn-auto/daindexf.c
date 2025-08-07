#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* daindex.c */
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
#define dmdasetaotype_ DMDASETAOTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmdasetaotype_ dmdasetaotype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmdagetao_ DMDAGETAO
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmdagetao_ dmdagetao
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmdasetaotype_(DM da,char *aotype, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(da);
/* insert Fortran-to-C conversion for aotype */
  FIXCHAR(aotype,cl0,_cltmp0);
*ierr = DMDASetAOType(
	(DM)PetscToPointer((da) ),_cltmp0);
  FREECHAR(aotype,_cltmp0);
}
PETSC_EXTERN void  dmdagetao_(DM da,AO *ao, int *ierr)
{
CHKFORTRANNULLOBJECT(da);
PetscBool ao_null = !*(void**) ao ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ao);
*ierr = DMDAGetAO(
	(DM)PetscToPointer((da) ),ao);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ao_null && !*(void**) ao) * (void **) ao = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
