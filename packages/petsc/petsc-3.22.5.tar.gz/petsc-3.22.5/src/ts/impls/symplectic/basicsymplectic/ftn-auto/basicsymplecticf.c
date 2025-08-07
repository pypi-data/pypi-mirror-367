#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* basicsymplectic.c */
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
#define tsbasicsymplecticsettype_ TSBASICSYMPLECTICSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsbasicsymplecticsettype_ tsbasicsymplecticsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsbasicsymplecticgettype_ TSBASICSYMPLECTICGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsbasicsymplecticgettype_ tsbasicsymplecticgettype
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  tsbasicsymplecticsettype_(TS ts,char *bsymptype, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ts);
/* insert Fortran-to-C conversion for bsymptype */
  FIXCHAR(bsymptype,cl0,_cltmp0);
*ierr = TSBasicSymplecticSetType(
	(TS)PetscToPointer((ts) ),_cltmp0);
  FREECHAR(bsymptype,_cltmp0);
}
PETSC_EXTERN void  tsbasicsymplecticgettype_(TS ts,char *bsymptype, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ts);
*ierr = TSBasicSymplecticGetType(
	(TS)PetscToPointer((ts) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for bsymptype */
*ierr = PetscStrncpy(bsymptype, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, bsymptype, cl0);
}
#if defined(__cplusplus)
}
#endif
