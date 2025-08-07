#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* snesngmres.c */
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
#define snesngmressetrestartfmrise_ SNESNGMRESSETRESTARTFMRISE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesngmressetrestartfmrise_ snesngmressetrestartfmrise
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesngmressetrestarttype_ SNESNGMRESSETRESTARTTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesngmressetrestarttype_ snesngmressetrestarttype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesngmressetselecttype_ SNESNGMRESSETSELECTTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesngmressetselecttype_ snesngmressetselecttype
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  snesngmressetrestartfmrise_(SNES snes,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESNGMRESSetRestartFmRise(
	(SNES)PetscToPointer((snes) ),*flg);
}
PETSC_EXTERN void  snesngmressetrestarttype_(SNES snes,SNESNGMRESRestartType *rtype, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESNGMRESSetRestartType(
	(SNES)PetscToPointer((snes) ),*rtype);
}
PETSC_EXTERN void  snesngmressetselecttype_(SNES snes,SNESNGMRESSelectType *stype, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESNGMRESSetSelectType(
	(SNES)PetscToPointer((snes) ),*stype);
}
#if defined(__cplusplus)
}
#endif
