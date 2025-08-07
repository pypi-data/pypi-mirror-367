#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* submat.c */
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
#define matcreatesubmatrixvirtual_ MATCREATESUBMATRIXVIRTUAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreatesubmatrixvirtual_ matcreatesubmatrixvirtual
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsubmatrixvirtualupdate_ MATSUBMATRIXVIRTUALUPDATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsubmatrixvirtualupdate_ matsubmatrixvirtualupdate
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matcreatesubmatrixvirtual_(Mat A,IS isrow,IS iscol,Mat *newmat, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(isrow);
CHKFORTRANNULLOBJECT(iscol);
PetscBool newmat_null = !*(void**) newmat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(newmat);
*ierr = MatCreateSubMatrixVirtual(
	(Mat)PetscToPointer((A) ),
	(IS)PetscToPointer((isrow) ),
	(IS)PetscToPointer((iscol) ),newmat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! newmat_null && !*(void**) newmat) * (void **) newmat = (void *)-2;
}
PETSC_EXTERN void  matsubmatrixvirtualupdate_(Mat N,Mat A,IS isrow,IS iscol, int *ierr)
{
CHKFORTRANNULLOBJECT(N);
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(isrow);
CHKFORTRANNULLOBJECT(iscol);
*ierr = MatSubMatrixVirtualUpdate(
	(Mat)PetscToPointer((N) ),
	(Mat)PetscToPointer((A) ),
	(IS)PetscToPointer((isrow) ),
	(IS)PetscToPointer((iscol) ));
}
#if defined(__cplusplus)
}
#endif
