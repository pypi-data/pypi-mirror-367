#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* mpibaij.c */
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
#define matmpibaijsetpreallocation_ MATMPIBAIJSETPREALLOCATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmpibaijsetpreallocation_ matmpibaijsetpreallocation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreatebaij_ MATCREATEBAIJ
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreatebaij_ matcreatebaij
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmpibaijsethashtablefactor_ MATMPIBAIJSETHASHTABLEFACTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmpibaijsethashtablefactor_ matmpibaijsethashtablefactor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreatempibaijwitharrays_ MATCREATEMPIBAIJWITHARRAYS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreatempibaijwitharrays_ matcreatempibaijwitharrays
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matmpibaijsetpreallocation_(Mat B,PetscInt *bs,PetscInt *d_nz, PetscInt d_nnz[],PetscInt *o_nz, PetscInt o_nnz[], int *ierr)
{
CHKFORTRANNULLOBJECT(B);
CHKFORTRANNULLINTEGER(d_nnz);
CHKFORTRANNULLINTEGER(o_nnz);
*ierr = MatMPIBAIJSetPreallocation(
	(Mat)PetscToPointer((B) ),*bs,*d_nz,d_nnz,*o_nz,o_nnz);
}
PETSC_EXTERN void  matcreatebaij_(MPI_Fint * comm,PetscInt *bs,PetscInt *m,PetscInt *n,PetscInt *M,PetscInt *N,PetscInt *d_nz, PetscInt d_nnz[],PetscInt *o_nz, PetscInt o_nnz[],Mat *A, int *ierr)
{
CHKFORTRANNULLINTEGER(d_nnz);
CHKFORTRANNULLINTEGER(o_nnz);
PetscBool A_null = !*(void**) A ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(A);
*ierr = MatCreateBAIJ(
	MPI_Comm_f2c(*(comm)),*bs,*m,*n,*M,*N,*d_nz,d_nnz,*o_nz,o_nnz,A);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! A_null && !*(void**) A) * (void **) A = (void *)-2;
}
PETSC_EXTERN void  matmpibaijsethashtablefactor_(Mat mat,PetscReal *fact, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatMPIBAIJSetHashTableFactor(
	(Mat)PetscToPointer((mat) ),*fact);
}
PETSC_EXTERN void  matcreatempibaijwitharrays_(MPI_Fint * comm,PetscInt *bs,PetscInt *m,PetscInt *n,PetscInt *M,PetscInt *N, PetscInt i[], PetscInt j[], PetscScalar a[],Mat *mat, int *ierr)
{
CHKFORTRANNULLINTEGER(i);
CHKFORTRANNULLINTEGER(j);
CHKFORTRANNULLSCALAR(a);
PetscBool mat_null = !*(void**) mat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mat);
*ierr = MatCreateMPIBAIJWithArrays(
	MPI_Comm_f2c(*(comm)),*bs,*m,*n,*M,*N,i,j,a,mat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mat_null && !*(void**) mat) * (void **) mat = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
