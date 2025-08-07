#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* tr.c */
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
#define snesnewtontrsetnormtype_ SNESNEWTONTRSETNORMTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesnewtontrsetnormtype_ snesnewtontrsetnormtype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesnewtontrsetqntype_ SNESNEWTONTRSETQNTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesnewtontrsetqntype_ snesnewtontrsetqntype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesnewtontrsetfallbacktype_ SNESNEWTONTRSETFALLBACKTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesnewtontrsetfallbacktype_ snesnewtontrsetfallbacktype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snessettrustregiontolerance_ SNESSETTRUSTREGIONTOLERANCE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snessettrustregiontolerance_ snessettrustregiontolerance
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesnewtontrsettolerances_ SNESNEWTONTRSETTOLERANCES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesnewtontrsettolerances_ snesnewtontrsettolerances
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesnewtontrgettolerances_ SNESNEWTONTRGETTOLERANCES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesnewtontrgettolerances_ snesnewtontrgettolerances
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesnewtontrsetupdateparameters_ SNESNEWTONTRSETUPDATEPARAMETERS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesnewtontrsetupdateparameters_ snesnewtontrsetupdateparameters
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesnewtontrgetupdateparameters_ SNESNEWTONTRGETUPDATEPARAMETERS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesnewtontrgetupdateparameters_ snesnewtontrgetupdateparameters
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  snesnewtontrsetnormtype_(SNES snes,NormType *norm, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESNewtonTRSetNormType(
	(SNES)PetscToPointer((snes) ),*norm);
}
PETSC_EXTERN void  snesnewtontrsetqntype_(SNES snes,SNESNewtonTRQNType *use, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESNewtonTRSetQNType(
	(SNES)PetscToPointer((snes) ),*use);
}
PETSC_EXTERN void  snesnewtontrsetfallbacktype_(SNES snes,SNESNewtonTRFallbackType *ftype, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESNewtonTRSetFallbackType(
	(SNES)PetscToPointer((snes) ),*ftype);
}
PETSC_EXTERN void  snessettrustregiontolerance_(SNES snes,PetscReal *tol, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESSetTrustRegionTolerance(
	(SNES)PetscToPointer((snes) ),*tol);
}
PETSC_EXTERN void  snesnewtontrsettolerances_(SNES snes,PetscReal *delta_min,PetscReal *delta_max,PetscReal *delta_0, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESNewtonTRSetTolerances(
	(SNES)PetscToPointer((snes) ),*delta_min,*delta_max,*delta_0);
}
PETSC_EXTERN void  snesnewtontrgettolerances_(SNES snes,PetscReal *delta_min,PetscReal *delta_max,PetscReal *delta_0, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLREAL(delta_min);
CHKFORTRANNULLREAL(delta_max);
CHKFORTRANNULLREAL(delta_0);
*ierr = SNESNewtonTRGetTolerances(
	(SNES)PetscToPointer((snes) ),delta_min,delta_max,delta_0);
}
PETSC_EXTERN void  snesnewtontrsetupdateparameters_(SNES snes,PetscReal *eta1,PetscReal *eta2,PetscReal *eta3,PetscReal *t1,PetscReal *t2, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESNewtonTRSetUpdateParameters(
	(SNES)PetscToPointer((snes) ),*eta1,*eta2,*eta3,*t1,*t2);
}
PETSC_EXTERN void  snesnewtontrgetupdateparameters_(SNES snes,PetscReal *eta1,PetscReal *eta2,PetscReal *eta3,PetscReal *t1,PetscReal *t2, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLREAL(eta1);
CHKFORTRANNULLREAL(eta2);
CHKFORTRANNULLREAL(eta3);
CHKFORTRANNULLREAL(t1);
CHKFORTRANNULLREAL(t2);
*ierr = SNESNewtonTRGetUpdateParameters(
	(SNES)PetscToPointer((snes) ),eta1,eta2,eta3,t1,t2);
}
#if defined(__cplusplus)
}
#endif
