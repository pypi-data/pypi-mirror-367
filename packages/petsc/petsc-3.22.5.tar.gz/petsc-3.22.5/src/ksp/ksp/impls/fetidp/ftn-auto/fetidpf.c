#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* fetidp.c */
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

#include <petscksp.h>
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspfetidpsetpressureoperator_ KSPFETIDPSETPRESSUREOPERATOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspfetidpsetpressureoperator_ kspfetidpsetpressureoperator
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspfetidpgetinnerksp_ KSPFETIDPGETINNERKSP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspfetidpgetinnerksp_ kspfetidpgetinnerksp
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspfetidpgetinnerbddc_ KSPFETIDPGETINNERBDDC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspfetidpgetinnerbddc_ kspfetidpgetinnerbddc
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspfetidpsetinnerbddc_ KSPFETIDPSETINNERBDDC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspfetidpsetinnerbddc_ kspfetidpsetinnerbddc
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  kspfetidpsetpressureoperator_(KSP ksp,Mat P, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
CHKFORTRANNULLOBJECT(P);
*ierr = KSPFETIDPSetPressureOperator(
	(KSP)PetscToPointer((ksp) ),
	(Mat)PetscToPointer((P) ));
}
PETSC_EXTERN void  kspfetidpgetinnerksp_(KSP ksp,KSP *innerksp, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
PetscBool innerksp_null = !*(void**) innerksp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(innerksp);
*ierr = KSPFETIDPGetInnerKSP(
	(KSP)PetscToPointer((ksp) ),innerksp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! innerksp_null && !*(void**) innerksp) * (void **) innerksp = (void *)-2;
}
PETSC_EXTERN void  kspfetidpgetinnerbddc_(KSP ksp,PC *pc, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
PetscBool pc_null = !*(void**) pc ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(pc);
*ierr = KSPFETIDPGetInnerBDDC(
	(KSP)PetscToPointer((ksp) ),pc);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! pc_null && !*(void**) pc) * (void **) pc = (void *)-2;
}
PETSC_EXTERN void  kspfetidpsetinnerbddc_(KSP ksp,PC pc, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
CHKFORTRANNULLOBJECT(pc);
*ierr = KSPFETIDPSetInnerBDDC(
	(KSP)PetscToPointer((ksp) ),
	(PC)PetscToPointer((pc) ));
}
#if defined(__cplusplus)
}
#endif
