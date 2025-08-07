#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* baij.c */
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
#define matseqbaijsetcolumnindices_ MATSEQBAIJSETCOLUMNINDICES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matseqbaijsetcolumnindices_ matseqbaijsetcolumnindices
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreateseqbaij_ MATCREATESEQBAIJ
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreateseqbaij_ matcreateseqbaij
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matseqbaijsetpreallocation_ MATSEQBAIJSETPREALLOCATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matseqbaijsetpreallocation_ matseqbaijsetpreallocation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreateseqbaijwitharrays_ MATCREATESEQBAIJWITHARRAYS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreateseqbaijwitharrays_ matcreateseqbaijwitharrays
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matseqbaijsetcolumnindices_(Mat mat,PetscInt *indices, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLINTEGER(indices);
*ierr = MatSeqBAIJSetColumnIndices(
	(Mat)PetscToPointer((mat) ),indices);
}
PETSC_EXTERN void  matcreateseqbaij_(MPI_Fint * comm,PetscInt *bs,PetscInt *m,PetscInt *n,PetscInt *nz, PetscInt nnz[],Mat *A, int *ierr)
{
CHKFORTRANNULLINTEGER(nnz);
PetscBool A_null = !*(void**) A ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(A);
*ierr = MatCreateSeqBAIJ(
	MPI_Comm_f2c(*(comm)),*bs,*m,*n,*nz,nnz,A);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! A_null && !*(void**) A) * (void **) A = (void *)-2;
}
PETSC_EXTERN void  matseqbaijsetpreallocation_(Mat B,PetscInt *bs,PetscInt *nz, PetscInt nnz[], int *ierr)
{
CHKFORTRANNULLOBJECT(B);
CHKFORTRANNULLINTEGER(nnz);
*ierr = MatSeqBAIJSetPreallocation(
	(Mat)PetscToPointer((B) ),*bs,*nz,nnz);
}
PETSC_EXTERN void  matcreateseqbaijwitharrays_(MPI_Fint * comm,PetscInt *bs,PetscInt *m,PetscInt *n,PetscInt i[],PetscInt j[],PetscScalar a[],Mat *mat, int *ierr)
{
CHKFORTRANNULLINTEGER(i);
CHKFORTRANNULLINTEGER(j);
CHKFORTRANNULLSCALAR(a);
PetscBool mat_null = !*(void**) mat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mat);
*ierr = MatCreateSeqBAIJWithArrays(
	MPI_Comm_f2c(*(comm)),*bs,*m,*n,i,j,a,mat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mat_null && !*(void**) mat) * (void **) mat = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
