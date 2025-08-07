#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* cgtype.c */
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
#define kspcgsettype_ KSPCGSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspcgsettype_ kspcgsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspcgusesinglereduction_ KSPCGUSESINGLEREDUCTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspcgusesinglereduction_ kspcgusesinglereduction
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspcgsetradius_ KSPCGSETRADIUS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspcgsetradius_ kspcgsetradius
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspcgsetobjectivetarget_ KSPCGSETOBJECTIVETARGET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspcgsetobjectivetarget_ kspcgsetobjectivetarget
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspcggetnormd_ KSPCGGETNORMD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspcggetnormd_ kspcggetnormd
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspcggetobjfcn_ KSPCGGETOBJFCN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspcggetobjfcn_ kspcggetobjfcn
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  kspcgsettype_(KSP ksp,KSPCGType *type, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
*ierr = KSPCGSetType(
	(KSP)PetscToPointer((ksp) ),*type);
}
PETSC_EXTERN void  kspcgusesinglereduction_(KSP ksp,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
*ierr = KSPCGUseSingleReduction(
	(KSP)PetscToPointer((ksp) ),*flg);
}
PETSC_EXTERN void  kspcgsetradius_(KSP ksp,PetscReal *radius, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
*ierr = KSPCGSetRadius(
	(KSP)PetscToPointer((ksp) ),*radius);
}
PETSC_EXTERN void  kspcgsetobjectivetarget_(KSP ksp,PetscReal *obj, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
*ierr = KSPCGSetObjectiveTarget(
	(KSP)PetscToPointer((ksp) ),*obj);
}
PETSC_EXTERN void  kspcggetnormd_(KSP ksp,PetscReal *norm_d, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
CHKFORTRANNULLREAL(norm_d);
*ierr = KSPCGGetNormD(
	(KSP)PetscToPointer((ksp) ),norm_d);
}
PETSC_EXTERN void  kspcggetobjfcn_(KSP ksp,PetscReal *o_fcn, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
CHKFORTRANNULLREAL(o_fcn);
*ierr = KSPCGGetObjFcn(
	(KSP)PetscToPointer((ksp) ),o_fcn);
}
#if defined(__cplusplus)
}
#endif
