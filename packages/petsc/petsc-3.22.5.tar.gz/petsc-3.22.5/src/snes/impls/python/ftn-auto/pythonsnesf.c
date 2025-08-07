#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* pythonsnes.c */
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

#include "petscsnes.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snespythonsettype_ SNESPYTHONSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snespythonsettype_ snespythonsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snespythongettype_ SNESPYTHONGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snespythongettype_ snespythongettype
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  snespythonsettype_(SNES snes, char pyname[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(snes);
/* insert Fortran-to-C conversion for pyname */
  FIXCHAR(pyname,cl0,_cltmp0);
*ierr = SNESPythonSetType(
	(SNES)PetscToPointer((snes) ),_cltmp0);
  FREECHAR(pyname,_cltmp0);
}
PETSC_EXTERN void  snespythongettype_(SNES snes, char *pyname, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESPythonGetType(
	(SNES)PetscToPointer((snes) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for pyname */
*ierr = PetscStrncpy(pyname, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, pyname, cl0);
}
#if defined(__cplusplus)
}
#endif
