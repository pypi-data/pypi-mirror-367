#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* mlocalref.c */
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
#define matcreatelocalref_ MATCREATELOCALREF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreatelocalref_ matcreatelocalref
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matcreatelocalref_(Mat A,IS isrow,IS iscol,Mat *newmat, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(isrow);
CHKFORTRANNULLOBJECT(iscol);
PetscBool newmat_null = !*(void**) newmat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(newmat);
*ierr = MatCreateLocalRef(
	(Mat)PetscToPointer((A) ),
	(IS)PetscToPointer((isrow) ),
	(IS)PetscToPointer((iscol) ),newmat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! newmat_null && !*(void**) newmat) * (void **) newmat = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
