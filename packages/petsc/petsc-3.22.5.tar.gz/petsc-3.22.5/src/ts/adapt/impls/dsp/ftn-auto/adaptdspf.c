#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* adaptdsp.c */
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

#include "petscts.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadaptdspsetfilter_ TSADAPTDSPSETFILTER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadaptdspsetfilter_ tsadaptdspsetfilter
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadaptdspsetpid_ TSADAPTDSPSETPID
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadaptdspsetpid_ tsadaptdspsetpid
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  tsadaptdspsetfilter_(TSAdapt adapt, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(adapt);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = TSAdaptDSPSetFilter(
	(TSAdapt)PetscToPointer((adapt) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  tsadaptdspsetpid_(TSAdapt adapt,PetscReal *kkI,PetscReal *kkP,PetscReal *kkD, int *ierr)
{
CHKFORTRANNULLOBJECT(adapt);
*ierr = TSAdaptDSPSetPID(
	(TSAdapt)PetscToPointer((adapt) ),*kkI,*kkP,*kkD);
}
#if defined(__cplusplus)
}
#endif
