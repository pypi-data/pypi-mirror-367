#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* mpisbaij.c */
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
#define matmpisbaijsetpreallocation_ MATMPISBAIJSETPREALLOCATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmpisbaijsetpreallocation_ matmpisbaijsetpreallocation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreatesbaij_ MATCREATESBAIJ
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreatesbaij_ matcreatesbaij
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreatempisbaijwitharrays_ MATCREATEMPISBAIJWITHARRAYS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreatempisbaijwitharrays_ matcreatempisbaijwitharrays
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmpisbaijsetpreallocationcsr_ MATMPISBAIJSETPREALLOCATIONCSR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmpisbaijsetpreallocationcsr_ matmpisbaijsetpreallocationcsr
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matmpisbaijsetpreallocation_(Mat B,PetscInt *bs,PetscInt *d_nz, PetscInt d_nnz[],PetscInt *o_nz, PetscInt o_nnz[], int *ierr)
{
CHKFORTRANNULLOBJECT(B);
CHKFORTRANNULLINTEGER(d_nnz);
CHKFORTRANNULLINTEGER(o_nnz);
*ierr = MatMPISBAIJSetPreallocation(
	(Mat)PetscToPointer((B) ),*bs,*d_nz,d_nnz,*o_nz,o_nnz);
}
PETSC_EXTERN void  matcreatesbaij_(MPI_Fint * comm,PetscInt *bs,PetscInt *m,PetscInt *n,PetscInt *M,PetscInt *N,PetscInt *d_nz, PetscInt d_nnz[],PetscInt *o_nz, PetscInt o_nnz[],Mat *A, int *ierr)
{
CHKFORTRANNULLINTEGER(d_nnz);
CHKFORTRANNULLINTEGER(o_nnz);
PetscBool A_null = !*(void**) A ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(A);
*ierr = MatCreateSBAIJ(
	MPI_Comm_f2c(*(comm)),*bs,*m,*n,*M,*N,*d_nz,d_nnz,*o_nz,o_nnz,A);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! A_null && !*(void**) A) * (void **) A = (void *)-2;
}
PETSC_EXTERN void  matcreatempisbaijwitharrays_(MPI_Fint * comm,PetscInt *bs,PetscInt *m,PetscInt *n,PetscInt *M,PetscInt *N, PetscInt i[], PetscInt j[], PetscScalar a[],Mat *mat, int *ierr)
{
CHKFORTRANNULLINTEGER(i);
CHKFORTRANNULLINTEGER(j);
CHKFORTRANNULLSCALAR(a);
PetscBool mat_null = !*(void**) mat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mat);
*ierr = MatCreateMPISBAIJWithArrays(
	MPI_Comm_f2c(*(comm)),*bs,*m,*n,*M,*N,i,j,a,mat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mat_null && !*(void**) mat) * (void **) mat = (void *)-2;
}
PETSC_EXTERN void  matmpisbaijsetpreallocationcsr_(Mat B,PetscInt *bs, PetscInt i[], PetscInt j[], PetscScalar v[], int *ierr)
{
CHKFORTRANNULLOBJECT(B);
CHKFORTRANNULLINTEGER(i);
CHKFORTRANNULLINTEGER(j);
CHKFORTRANNULLSCALAR(v);
*ierr = MatMPISBAIJSetPreallocationCSR(
	(Mat)PetscToPointer((B) ),*bs,i,j,v);
}
#if defined(__cplusplus)
}
#endif
