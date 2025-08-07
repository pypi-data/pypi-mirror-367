#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* htool.cxx */
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

#include "petscmat.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define mathtoolgetpermutationsource_ MATHTOOLGETPERMUTATIONSOURCE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define mathtoolgetpermutationsource_ mathtoolgetpermutationsource
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define mathtoolgetpermutationtarget_ MATHTOOLGETPERMUTATIONTARGET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define mathtoolgetpermutationtarget_ mathtoolgetpermutationtarget
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define mathtoolusepermutation_ MATHTOOLUSEPERMUTATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define mathtoolusepermutation_ mathtoolusepermutation
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  mathtoolgetpermutationsource_(Mat A,IS *is, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool is_null = !*(void**) is ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is);
*ierr = MatHtoolGetPermutationSource(
	(Mat)PetscToPointer((A) ),is);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is_null && !*(void**) is) * (void **) is = (void *)-2;
}
PETSC_EXTERN void  mathtoolgetpermutationtarget_(Mat A,IS *is, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool is_null = !*(void**) is ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is);
*ierr = MatHtoolGetPermutationTarget(
	(Mat)PetscToPointer((A) ),is);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is_null && !*(void**) is) * (void **) is = (void *)-2;
}
PETSC_EXTERN void  mathtoolusepermutation_(Mat A,PetscBool *use, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatHtoolUsePermutation(
	(Mat)PetscToPointer((A) ),*use);
}
#if defined(__cplusplus)
}
#endif
