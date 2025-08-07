#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* pythonksp.c */
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
#define ksppythonsettype_ KSPPYTHONSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define ksppythonsettype_ ksppythonsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define ksppythongettype_ KSPPYTHONGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define ksppythongettype_ ksppythongettype
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  ksppythonsettype_(KSP ksp, char pyname[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ksp);
/* insert Fortran-to-C conversion for pyname */
  FIXCHAR(pyname,cl0,_cltmp0);
*ierr = KSPPythonSetType(
	(KSP)PetscToPointer((ksp) ),_cltmp0);
  FREECHAR(pyname,_cltmp0);
}
PETSC_EXTERN void  ksppythongettype_(KSP ksp, char *pyname, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ksp);
*ierr = KSPPythonGetType(
	(KSP)PetscToPointer((ksp) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for pyname */
*ierr = PetscStrncpy(pyname, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, pyname, cl0);
}
#if defined(__cplusplus)
}
#endif
