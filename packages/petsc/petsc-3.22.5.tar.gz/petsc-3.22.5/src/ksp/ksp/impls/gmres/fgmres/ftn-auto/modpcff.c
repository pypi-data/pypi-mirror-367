#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* modpcf.c */
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
#define kspfgmresmodifypcnochange_ KSPFGMRESMODIFYPCNOCHANGE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspfgmresmodifypcnochange_ kspfgmresmodifypcnochange
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspfgmresmodifypcksp_ KSPFGMRESMODIFYPCKSP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspfgmresmodifypcksp_ kspfgmresmodifypcksp
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  kspfgmresmodifypcnochange_(KSP ksp,PetscInt *total_its,PetscInt *loc_its,PetscReal *res_norm,void*ctx, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
*ierr = KSPFGMRESModifyPCNoChange(
	(KSP)PetscToPointer((ksp) ),*total_its,*loc_its,*res_norm,ctx);
}
PETSC_EXTERN void  kspfgmresmodifypcksp_(KSP ksp,PetscInt *total_its,PetscInt *loc_its,PetscReal *res_norm,void*ctx, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
*ierr = KSPFGMRESModifyPCKSP(
	(KSP)PetscToPointer((ksp) ),*total_its,*loc_its,*res_norm,ctx);
}
#if defined(__cplusplus)
}
#endif
