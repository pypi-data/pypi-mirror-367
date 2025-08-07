#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* mkl_pardiso.c */
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
#define matmkl_pardisosetcntl_ MATMKL_PARDISOSETCNTL
#elif defined(FORTRANDOUBLEUNDERSCORE)
#define matmkl_pardisosetcntl_ matmkl_pardisosetcntl__
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE)
#define matmkl_pardisosetcntl_ matmkl_pardisosetcntl
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matmkl_pardisosetcntl_(Mat F,PetscInt *icntl,PetscInt *ival, int *ierr)
{
CHKFORTRANNULLOBJECT(F);
*ierr = MatMkl_PardisoSetCntl(
	(Mat)PetscToPointer((F) ),*icntl,*ival);
}
#if defined(__cplusplus)
}
#endif
