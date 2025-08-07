#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* mg.c */
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
#define pcmggetlevels_ PCMGGETLEVELS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmggetlevels_ pcmggetlevels
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmggetgridcomplexity_ PCMGGETGRIDCOMPLEXITY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmggetgridcomplexity_ pcmggetgridcomplexity
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmgsettype_ PCMGSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmgsettype_ pcmgsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmggettype_ PCMGGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmggettype_ pcmggettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmgsetcycletype_ PCMGSETCYCLETYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmgsetcycletype_ pcmgsetcycletype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmgmultiplicativesetcycles_ PCMGMULTIPLICATIVESETCYCLES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmgmultiplicativesetcycles_ pcmgmultiplicativesetcycles
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmgsetgalerkin_ PCMGSETGALERKIN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmgsetgalerkin_ pcmgsetgalerkin
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmggetgalerkin_ PCMGGETGALERKIN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmggetgalerkin_ pcmggetgalerkin
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmgsetadaptcoarsespacetype_ PCMGSETADAPTCOARSESPACETYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmgsetadaptcoarsespacetype_ pcmgsetadaptcoarsespacetype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmggetadaptcoarsespacetype_ PCMGGETADAPTCOARSESPACETYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmggetadaptcoarsespacetype_ pcmggetadaptcoarsespacetype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmgsetadaptinterpolation_ PCMGSETADAPTINTERPOLATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmgsetadaptinterpolation_ pcmgsetadaptinterpolation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmggetadaptinterpolation_ PCMGGETADAPTINTERPOLATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmggetadaptinterpolation_ pcmggetadaptinterpolation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmgsetadaptcr_ PCMGSETADAPTCR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmgsetadaptcr_ pcmgsetadaptcr
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmggetadaptcr_ PCMGGETADAPTCR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmggetadaptcr_ pcmggetadaptcr
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmgsetnumbersmooth_ PCMGSETNUMBERSMOOTH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmgsetnumbersmooth_ pcmgsetnumbersmooth
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmgsetdistinctsmoothup_ PCMGSETDISTINCTSMOOTHUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmgsetdistinctsmoothup_ pcmgsetdistinctsmoothup
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  pcmggetlevels_(PC pc,PetscInt *levels, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLINTEGER(levels);
*ierr = PCMGGetLevels(
	(PC)PetscToPointer((pc) ),levels);
}
PETSC_EXTERN void  pcmggetgridcomplexity_(PC pc,PetscReal *gc,PetscReal *oc, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLREAL(gc);
CHKFORTRANNULLREAL(oc);
*ierr = PCMGGetGridComplexity(
	(PC)PetscToPointer((pc) ),gc,oc);
}
PETSC_EXTERN void  pcmgsettype_(PC pc,PCMGType *form, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCMGSetType(
	(PC)PetscToPointer((pc) ),*form);
}
PETSC_EXTERN void  pcmggettype_(PC pc,PCMGType *type, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCMGGetType(
	(PC)PetscToPointer((pc) ),type);
}
PETSC_EXTERN void  pcmgsetcycletype_(PC pc,PCMGCycleType *n, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCMGSetCycleType(
	(PC)PetscToPointer((pc) ),*n);
}
PETSC_EXTERN void  pcmgmultiplicativesetcycles_(PC pc,PetscInt *n, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCMGMultiplicativeSetCycles(
	(PC)PetscToPointer((pc) ),*n);
}
PETSC_EXTERN void  pcmgsetgalerkin_(PC pc,PCMGGalerkinType *use, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCMGSetGalerkin(
	(PC)PetscToPointer((pc) ),*use);
}
PETSC_EXTERN void  pcmggetgalerkin_(PC pc,PCMGGalerkinType *galerkin, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCMGGetGalerkin(
	(PC)PetscToPointer((pc) ),galerkin);
}
PETSC_EXTERN void  pcmgsetadaptcoarsespacetype_(PC pc,PCMGCoarseSpaceType *ctype, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCMGSetAdaptCoarseSpaceType(
	(PC)PetscToPointer((pc) ),*ctype);
}
PETSC_EXTERN void  pcmggetadaptcoarsespacetype_(PC pc,PCMGCoarseSpaceType *ctype, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCMGGetAdaptCoarseSpaceType(
	(PC)PetscToPointer((pc) ),ctype);
}
PETSC_EXTERN void  pcmgsetadaptinterpolation_(PC pc,PetscBool *adapt, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCMGSetAdaptInterpolation(
	(PC)PetscToPointer((pc) ),*adapt);
}
PETSC_EXTERN void  pcmggetadaptinterpolation_(PC pc,PetscBool *adapt, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCMGGetAdaptInterpolation(
	(PC)PetscToPointer((pc) ),adapt);
}
PETSC_EXTERN void  pcmgsetadaptcr_(PC pc,PetscBool *cr, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCMGSetAdaptCR(
	(PC)PetscToPointer((pc) ),*cr);
}
PETSC_EXTERN void  pcmggetadaptcr_(PC pc,PetscBool *cr, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCMGGetAdaptCR(
	(PC)PetscToPointer((pc) ),cr);
}
PETSC_EXTERN void  pcmgsetnumbersmooth_(PC pc,PetscInt *n, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCMGSetNumberSmooth(
	(PC)PetscToPointer((pc) ),*n);
}
PETSC_EXTERN void  pcmgsetdistinctsmoothup_(PC pc, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCMGSetDistinctSmoothUp(
	(PC)PetscToPointer((pc) ));
}
#if defined(__cplusplus)
}
#endif
