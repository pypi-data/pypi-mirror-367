#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* ms.c */
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
#define snesmsgettype_ SNESMSGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesmsgettype_ snesmsgettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesmssettype_ SNESMSSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesmssettype_ snesmssettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesmsgetdamping_ SNESMSGETDAMPING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesmsgetdamping_ snesmsgetdamping
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesmssetdamping_ SNESMSSETDAMPING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesmssetdamping_ snesmssetdamping
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  snesmsgettype_(SNES snes,char *mstype, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESMSGetType(
	(SNES)PetscToPointer((snes) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for mstype */
*ierr = PetscStrncpy(mstype, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, mstype, cl0);
}
PETSC_EXTERN void  snesmssettype_(SNES snes,char *mstype, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(snes);
/* insert Fortran-to-C conversion for mstype */
  FIXCHAR(mstype,cl0,_cltmp0);
*ierr = SNESMSSetType(
	(SNES)PetscToPointer((snes) ),_cltmp0);
  FREECHAR(mstype,_cltmp0);
}
PETSC_EXTERN void  snesmsgetdamping_(SNES snes,PetscReal *damping, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLREAL(damping);
*ierr = SNESMSGetDamping(
	(SNES)PetscToPointer((snes) ),damping);
}
PETSC_EXTERN void  snesmssetdamping_(SNES snes,PetscReal *damping, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESMSSetDamping(
	(SNES)PetscToPointer((snes) ),*damping);
}
#if defined(__cplusplus)
}
#endif
