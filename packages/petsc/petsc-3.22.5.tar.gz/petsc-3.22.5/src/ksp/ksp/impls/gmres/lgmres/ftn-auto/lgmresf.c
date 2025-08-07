#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* lgmres.c */
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
#define ksplgmressetaugdim_ KSPLGMRESSETAUGDIM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define ksplgmressetaugdim_ ksplgmressetaugdim
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define ksplgmressetconstant_ KSPLGMRESSETCONSTANT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define ksplgmressetconstant_ ksplgmressetconstant
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  ksplgmressetaugdim_(KSP ksp,PetscInt *dim, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
*ierr = KSPLGMRESSetAugDim(
	(KSP)PetscToPointer((ksp) ),*dim);
}
PETSC_EXTERN void  ksplgmressetconstant_(KSP ksp, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
*ierr = KSPLGMRESSetConstant(
	(KSP)PetscToPointer((ksp) ));
}
#if defined(__cplusplus)
}
#endif
