#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* galerkin.c */
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
#define pcgalerkinsetrestriction_ PCGALERKINSETRESTRICTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgalerkinsetrestriction_ pcgalerkinsetrestriction
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgalerkinsetinterpolation_ PCGALERKINSETINTERPOLATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgalerkinsetinterpolation_ pcgalerkinsetinterpolation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgalerkingetksp_ PCGALERKINGETKSP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgalerkingetksp_ pcgalerkingetksp
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  pcgalerkinsetrestriction_(PC pc,Mat R, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(R);
*ierr = PCGalerkinSetRestriction(
	(PC)PetscToPointer((pc) ),
	(Mat)PetscToPointer((R) ));
}
PETSC_EXTERN void  pcgalerkinsetinterpolation_(PC pc,Mat P, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(P);
*ierr = PCGalerkinSetInterpolation(
	(PC)PetscToPointer((pc) ),
	(Mat)PetscToPointer((P) ));
}
PETSC_EXTERN void  pcgalerkingetksp_(PC pc,KSP *ksp, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool ksp_null = !*(void**) ksp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ksp);
*ierr = PCGalerkinGetKSP(
	(PC)PetscToPointer((pc) ),ksp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ksp_null && !*(void**) ksp) * (void **) ksp = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
