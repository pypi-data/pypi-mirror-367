#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* lmvmpc.c */
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

#include "petscpc.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pclmvmsetupdatevec_ PCLMVMSETUPDATEVEC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pclmvmsetupdatevec_ pclmvmsetupdatevec
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pclmvmsetmatlmvm_ PCLMVMSETMATLMVM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pclmvmsetmatlmvm_ pclmvmsetmatlmvm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pclmvmgetmatlmvm_ PCLMVMGETMATLMVM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pclmvmgetmatlmvm_ pclmvmgetmatlmvm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pclmvmsetis_ PCLMVMSETIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pclmvmsetis_ pclmvmsetis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pclmvmclearis_ PCLMVMCLEARIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pclmvmclearis_ pclmvmclearis
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  pclmvmsetupdatevec_(PC pc,Vec X, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(X);
*ierr = PCLMVMSetUpdateVec(
	(PC)PetscToPointer((pc) ),
	(Vec)PetscToPointer((X) ));
}
PETSC_EXTERN void  pclmvmsetmatlmvm_(PC pc,Mat B, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(B);
*ierr = PCLMVMSetMatLMVM(
	(PC)PetscToPointer((pc) ),
	(Mat)PetscToPointer((B) ));
}
PETSC_EXTERN void  pclmvmgetmatlmvm_(PC pc,Mat *B, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool B_null = !*(void**) B ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(B);
*ierr = PCLMVMGetMatLMVM(
	(PC)PetscToPointer((pc) ),B);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! B_null && !*(void**) B) * (void **) B = (void *)-2;
}
PETSC_EXTERN void  pclmvmsetis_(PC pc,IS inactive, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(inactive);
*ierr = PCLMVMSetIS(
	(PC)PetscToPointer((pc) ),
	(IS)PetscToPointer((inactive) ));
}
PETSC_EXTERN void  pclmvmclearis_(PC pc, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCLMVMClearIS(
	(PC)PetscToPointer((pc) ));
}
#if defined(__cplusplus)
}
#endif
