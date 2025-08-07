#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* normm.c */
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
#define matnormalgetmat_ MATNORMALGETMAT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matnormalgetmat_ matnormalgetmat
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreatenormal_ MATCREATENORMAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreatenormal_ matcreatenormal
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matnormalgetmat_(Mat A,Mat *M, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool M_null = !*(void**) M ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(M);
*ierr = MatNormalGetMat(
	(Mat)PetscToPointer((A) ),M);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! M_null && !*(void**) M) * (void **) M = (void *)-2;
}
PETSC_EXTERN void  matcreatenormal_(Mat A,Mat *N, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool N_null = !*(void**) N ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(N);
*ierr = MatCreateNormal(
	(Mat)PetscToPointer((A) ),N);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! N_null && !*(void**) N) * (void **) N = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
