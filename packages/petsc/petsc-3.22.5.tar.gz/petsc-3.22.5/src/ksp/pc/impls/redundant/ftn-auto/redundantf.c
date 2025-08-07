#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* redundant.c */
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
#define pcredundantsetnumber_ PCREDUNDANTSETNUMBER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcredundantsetnumber_ pcredundantsetnumber
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcredundantsetscatter_ PCREDUNDANTSETSCATTER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcredundantsetscatter_ pcredundantsetscatter
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcredundantgetksp_ PCREDUNDANTGETKSP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcredundantgetksp_ pcredundantgetksp
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcredundantgetoperators_ PCREDUNDANTGETOPERATORS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcredundantgetoperators_ pcredundantgetoperators
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  pcredundantsetnumber_(PC pc,PetscInt *nredundant, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCRedundantSetNumber(
	(PC)PetscToPointer((pc) ),*nredundant);
}
PETSC_EXTERN void  pcredundantsetscatter_(PC pc,VecScatter *in,VecScatter *out, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCRedundantSetScatter(
	(PC)PetscToPointer((pc) ),*in,*out);
}
PETSC_EXTERN void  pcredundantgetksp_(PC pc,KSP *innerksp, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool innerksp_null = !*(void**) innerksp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(innerksp);
*ierr = PCRedundantGetKSP(
	(PC)PetscToPointer((pc) ),innerksp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! innerksp_null && !*(void**) innerksp) * (void **) innerksp = (void *)-2;
}
PETSC_EXTERN void  pcredundantgetoperators_(PC pc,Mat *mat,Mat *pmat, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool mat_null = !*(void**) mat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mat);
PetscBool pmat_null = !*(void**) pmat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(pmat);
*ierr = PCRedundantGetOperators(
	(PC)PetscToPointer((pc) ),mat,pmat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mat_null && !*(void**) mat) * (void **) mat = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! pmat_null && !*(void**) pmat) * (void **) pmat = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
