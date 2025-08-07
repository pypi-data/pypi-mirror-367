#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* mpiadj.c */
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
#define matmpiadjcreatenonemptysubcommmat_ MATMPIADJCREATENONEMPTYSUBCOMMMAT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmpiadjcreatenonemptysubcommmat_ matmpiadjcreatenonemptysubcommmat
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmpiadjtoseq_ MATMPIADJTOSEQ
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmpiadjtoseq_ matmpiadjtoseq
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmpiadjtoseqrankzero_ MATMPIADJTOSEQRANKZERO
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmpiadjtoseqrankzero_ matmpiadjtoseqrankzero
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmpiadjsetpreallocation_ MATMPIADJSETPREALLOCATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmpiadjsetpreallocation_ matmpiadjsetpreallocation
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matmpiadjcreatenonemptysubcommmat_(Mat A,Mat *B, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool B_null = !*(void**) B ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(B);
*ierr = MatMPIAdjCreateNonemptySubcommMat(
	(Mat)PetscToPointer((A) ),B);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! B_null && !*(void**) B) * (void **) B = (void *)-2;
}
PETSC_EXTERN void  matmpiadjtoseq_(Mat A,Mat *B, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool B_null = !*(void**) B ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(B);
*ierr = MatMPIAdjToSeq(
	(Mat)PetscToPointer((A) ),B);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! B_null && !*(void**) B) * (void **) B = (void *)-2;
}
PETSC_EXTERN void  matmpiadjtoseqrankzero_(Mat A,Mat *B, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool B_null = !*(void**) B ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(B);
*ierr = MatMPIAdjToSeqRankZero(
	(Mat)PetscToPointer((A) ),B);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! B_null && !*(void**) B) * (void **) B = (void *)-2;
}
PETSC_EXTERN void  matmpiadjsetpreallocation_(Mat B,PetscInt *i,PetscInt *j,PetscInt *values, int *ierr)
{
CHKFORTRANNULLOBJECT(B);
CHKFORTRANNULLINTEGER(i);
CHKFORTRANNULLINTEGER(j);
CHKFORTRANNULLINTEGER(values);
*ierr = MatMPIAdjSetPreallocation(
	(Mat)PetscToPointer((B) ),i,j,values);
}
#if defined(__cplusplus)
}
#endif
