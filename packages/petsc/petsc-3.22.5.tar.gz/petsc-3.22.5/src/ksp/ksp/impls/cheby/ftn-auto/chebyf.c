#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* cheby.c */
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
#define kspchebyshevseteigenvalues_ KSPCHEBYSHEVSETEIGENVALUES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspchebyshevseteigenvalues_ kspchebyshevseteigenvalues
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspchebyshevesteigset_ KSPCHEBYSHEVESTEIGSET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspchebyshevesteigset_ kspchebyshevesteigset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspchebyshevesteigsetusenoisy_ KSPCHEBYSHEVESTEIGSETUSENOISY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspchebyshevesteigsetusenoisy_ kspchebyshevesteigsetusenoisy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspchebyshevesteiggetksp_ KSPCHEBYSHEVESTEIGGETKSP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspchebyshevesteiggetksp_ kspchebyshevesteiggetksp
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspchebyshevsetkind_ KSPCHEBYSHEVSETKIND
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspchebyshevsetkind_ kspchebyshevsetkind
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspchebyshevgetkind_ KSPCHEBYSHEVGETKIND
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspchebyshevgetkind_ kspchebyshevgetkind
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  kspchebyshevseteigenvalues_(KSP ksp,PetscReal *emax,PetscReal *emin, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
*ierr = KSPChebyshevSetEigenvalues(
	(KSP)PetscToPointer((ksp) ),*emax,*emin);
}
PETSC_EXTERN void  kspchebyshevesteigset_(KSP ksp,PetscReal *a,PetscReal *b,PetscReal *c,PetscReal *d, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
*ierr = KSPChebyshevEstEigSet(
	(KSP)PetscToPointer((ksp) ),*a,*b,*c,*d);
}
PETSC_EXTERN void  kspchebyshevesteigsetusenoisy_(KSP ksp,PetscBool *use, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
*ierr = KSPChebyshevEstEigSetUseNoisy(
	(KSP)PetscToPointer((ksp) ),*use);
}
PETSC_EXTERN void  kspchebyshevesteiggetksp_(KSP ksp,KSP *kspest, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
PetscBool kspest_null = !*(void**) kspest ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(kspest);
*ierr = KSPChebyshevEstEigGetKSP(
	(KSP)PetscToPointer((ksp) ),kspest);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! kspest_null && !*(void**) kspest) * (void **) kspest = (void *)-2;
}
PETSC_EXTERN void  kspchebyshevsetkind_(KSP ksp,KSPChebyshevKind *kind, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
*ierr = KSPChebyshevSetKind(
	(KSP)PetscToPointer((ksp) ),*kind);
}
PETSC_EXTERN void  kspchebyshevgetkind_(KSP ksp,KSPChebyshevKind *kind, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
*ierr = KSPChebyshevGetKind(
	(KSP)PetscToPointer((ksp) ),kind);
}
#if defined(__cplusplus)
}
#endif
