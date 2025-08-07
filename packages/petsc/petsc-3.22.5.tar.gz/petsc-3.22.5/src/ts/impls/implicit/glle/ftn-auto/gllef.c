#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* glle.c */
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
#define tsgllesettype_ TSGLLESETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsgllesettype_ tsgllesettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsgllegetadapt_ TSGLLEGETADAPT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsgllegetadapt_ tsgllegetadapt
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  tsgllesettype_(TS ts,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ts);
/* insert Fortran-to-C conversion for type */
  FIXCHAR(type,cl0,_cltmp0);
*ierr = TSGLLESetType(
	(TS)PetscToPointer((ts) ),_cltmp0);
  FREECHAR(type,_cltmp0);
}
PETSC_EXTERN void  tsgllegetadapt_(TS ts,TSGLLEAdapt *adapt, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
PetscBool adapt_null = !*(void**) adapt ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(adapt);
*ierr = TSGLLEGetAdapt(
	(TS)PetscToPointer((ts) ),adapt);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! adapt_null && !*(void**) adapt) * (void **) adapt = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
