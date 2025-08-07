#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* eige.c */
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
#define kspcomputeoperator_ KSPCOMPUTEOPERATOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspcomputeoperator_ kspcomputeoperator
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspcomputeeigenvaluesexplicitly_ KSPCOMPUTEEIGENVALUESEXPLICITLY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspcomputeeigenvaluesexplicitly_ kspcomputeeigenvaluesexplicitly
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  kspcomputeoperator_(KSP ksp,char *mattype,Mat *mat, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ksp);
PetscBool mat_null = !*(void**) mat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mat);
/* insert Fortran-to-C conversion for mattype */
  FIXCHAR(mattype,cl0,_cltmp0);
*ierr = KSPComputeOperator(
	(KSP)PetscToPointer((ksp) ),_cltmp0,mat);
  FREECHAR(mattype,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mat_null && !*(void**) mat) * (void **) mat = (void *)-2;
}
PETSC_EXTERN void  kspcomputeeigenvaluesexplicitly_(KSP ksp,PetscInt *nmax,PetscReal r[],PetscReal c[], int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
CHKFORTRANNULLREAL(r);
CHKFORTRANNULLREAL(c);
*ierr = KSPComputeEigenvaluesExplicitly(
	(KSP)PetscToPointer((ksp) ),*nmax,r,c);
}
#if defined(__cplusplus)
}
#endif
