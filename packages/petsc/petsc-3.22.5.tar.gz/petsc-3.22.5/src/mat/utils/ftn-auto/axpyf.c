#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* axpy.c */
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
#define mataxpy_ MATAXPY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define mataxpy_ mataxpy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matshift_ MATSHIFT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matshift_ matshift
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matdiagonalset_ MATDIAGONALSET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matdiagonalset_ matdiagonalset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define mataypx_ MATAYPX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define mataypx_ mataypx
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcomputeoperator_ MATCOMPUTEOPERATOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcomputeoperator_ matcomputeoperator
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcomputeoperatortranspose_ MATCOMPUTEOPERATORTRANSPOSE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcomputeoperatortranspose_ matcomputeoperatortranspose
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfilter_ MATFILTER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfilter_ matfilter
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  mataxpy_(Mat Y,PetscScalar *a,Mat X,MatStructure *str, int *ierr)
{
CHKFORTRANNULLOBJECT(Y);
CHKFORTRANNULLOBJECT(X);
*ierr = MatAXPY(
	(Mat)PetscToPointer((Y) ),*a,
	(Mat)PetscToPointer((X) ),*str);
}
PETSC_EXTERN void  matshift_(Mat Y,PetscScalar *a, int *ierr)
{
CHKFORTRANNULLOBJECT(Y);
*ierr = MatShift(
	(Mat)PetscToPointer((Y) ),*a);
}
PETSC_EXTERN void  matdiagonalset_(Mat Y,Vec D,InsertMode *is, int *ierr)
{
CHKFORTRANNULLOBJECT(Y);
CHKFORTRANNULLOBJECT(D);
*ierr = MatDiagonalSet(
	(Mat)PetscToPointer((Y) ),
	(Vec)PetscToPointer((D) ),*is);
}
PETSC_EXTERN void  mataypx_(Mat Y,PetscScalar *a,Mat X,MatStructure *str, int *ierr)
{
CHKFORTRANNULLOBJECT(Y);
CHKFORTRANNULLOBJECT(X);
*ierr = MatAYPX(
	(Mat)PetscToPointer((Y) ),*a,
	(Mat)PetscToPointer((X) ),*str);
}
PETSC_EXTERN void  matcomputeoperator_(Mat inmat,char *mattype,Mat *mat, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(inmat);
PetscBool mat_null = !*(void**) mat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mat);
/* insert Fortran-to-C conversion for mattype */
  FIXCHAR(mattype,cl0,_cltmp0);
*ierr = MatComputeOperator(
	(Mat)PetscToPointer((inmat) ),_cltmp0,mat);
  FREECHAR(mattype,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mat_null && !*(void**) mat) * (void **) mat = (void *)-2;
}
PETSC_EXTERN void  matcomputeoperatortranspose_(Mat inmat,char *mattype,Mat *mat, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(inmat);
PetscBool mat_null = !*(void**) mat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mat);
/* insert Fortran-to-C conversion for mattype */
  FIXCHAR(mattype,cl0,_cltmp0);
*ierr = MatComputeOperatorTranspose(
	(Mat)PetscToPointer((inmat) ),_cltmp0,mat);
  FREECHAR(mattype,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mat_null && !*(void**) mat) * (void **) mat = (void *)-2;
}
PETSC_EXTERN void  matfilter_(Mat A,PetscReal *tol,PetscBool *compress,PetscBool *keep, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatFilter(
	(Mat)PetscToPointer((A) ),*tol,*compress,*keep);
}
#if defined(__cplusplus)
}
#endif
