#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* sell.c */
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
#define matseqsellsetpreallocation_ MATSEQSELLSETPREALLOCATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matseqsellsetpreallocation_ matseqsellsetpreallocation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matseqsellgetfillratio_ MATSEQSELLGETFILLRATIO
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matseqsellgetfillratio_ matseqsellgetfillratio
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matseqsellgetmaxslicewidth_ MATSEQSELLGETMAXSLICEWIDTH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matseqsellgetmaxslicewidth_ matseqsellgetmaxslicewidth
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matseqsellgetavgslicewidth_ MATSEQSELLGETAVGSLICEWIDTH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matseqsellgetavgslicewidth_ matseqsellgetavgslicewidth
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matseqsellsetsliceheight_ MATSEQSELLSETSLICEHEIGHT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matseqsellsetsliceheight_ matseqsellsetsliceheight
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matseqsellgetvarslicesize_ MATSEQSELLGETVARSLICESIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matseqsellgetvarslicesize_ matseqsellgetvarslicesize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreateseqsell_ MATCREATESEQSELL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreateseqsell_ matcreateseqsell
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matseqsellsetpreallocation_(Mat B,PetscInt *rlenmax, PetscInt rlen[], int *ierr)
{
CHKFORTRANNULLOBJECT(B);
CHKFORTRANNULLINTEGER(rlen);
*ierr = MatSeqSELLSetPreallocation(
	(Mat)PetscToPointer((B) ),*rlenmax,rlen);
}
PETSC_EXTERN void  matseqsellgetfillratio_(Mat A,PetscReal *ratio, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLREAL(ratio);
*ierr = MatSeqSELLGetFillRatio(
	(Mat)PetscToPointer((A) ),ratio);
}
PETSC_EXTERN void  matseqsellgetmaxslicewidth_(Mat A,PetscInt *slicewidth, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLINTEGER(slicewidth);
*ierr = MatSeqSELLGetMaxSliceWidth(
	(Mat)PetscToPointer((A) ),slicewidth);
}
PETSC_EXTERN void  matseqsellgetavgslicewidth_(Mat A,PetscReal *slicewidth, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLREAL(slicewidth);
*ierr = MatSeqSELLGetAvgSliceWidth(
	(Mat)PetscToPointer((A) ),slicewidth);
}
PETSC_EXTERN void  matseqsellsetsliceheight_(Mat A,PetscInt *sliceheight, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatSeqSELLSetSliceHeight(
	(Mat)PetscToPointer((A) ),*sliceheight);
}
PETSC_EXTERN void  matseqsellgetvarslicesize_(Mat A,PetscReal *variance, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLREAL(variance);
*ierr = MatSeqSELLGetVarSliceSize(
	(Mat)PetscToPointer((A) ),variance);
}
PETSC_EXTERN void  matcreateseqsell_(MPI_Fint * comm,PetscInt *m,PetscInt *n,PetscInt *rlenmax, PetscInt rlen[],Mat *A, int *ierr)
{
CHKFORTRANNULLINTEGER(rlen);
PetscBool A_null = !*(void**) A ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(A);
*ierr = MatCreateSeqSELL(
	MPI_Comm_f2c(*(comm)),*m,*n,*rlenmax,rlen,A);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! A_null && !*(void**) A) * (void **) A = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
