#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* mpidense.c */
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
#define matdensegetlocalmatrix_ MATDENSEGETLOCALMATRIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matdensegetlocalmatrix_ matdensegetlocalmatrix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmpidensesetpreallocation_ MATMPIDENSESETPREALLOCATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmpidensesetpreallocation_ matmpidensesetpreallocation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matdenseplacearray_ MATDENSEPLACEARRAY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matdenseplacearray_ matdenseplacearray
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matdenseresetarray_ MATDENSERESETARRAY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matdenseresetarray_ matdenseresetarray
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matdensereplacearray_ MATDENSEREPLACEARRAY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matdensereplacearray_ matdensereplacearray
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreatedense_ MATCREATEDENSE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreatedense_ matcreatedense
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matdensegetlocalmatrix_(Mat A,Mat *B, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool B_null = !*(void**) B ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(B);
*ierr = MatDenseGetLocalMatrix(
	(Mat)PetscToPointer((A) ),B);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! B_null && !*(void**) B) * (void **) B = (void *)-2;
}
PETSC_EXTERN void  matmpidensesetpreallocation_(Mat B,PetscScalar *data, int *ierr)
{
CHKFORTRANNULLOBJECT(B);
CHKFORTRANNULLSCALAR(data);
*ierr = MatMPIDenseSetPreallocation(
	(Mat)PetscToPointer((B) ),data);
}
PETSC_EXTERN void  matdenseplacearray_(Mat mat, PetscScalar *array, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLSCALAR(array);
*ierr = MatDensePlaceArray(
	(Mat)PetscToPointer((mat) ),array);
}
PETSC_EXTERN void  matdenseresetarray_(Mat mat, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatDenseResetArray(
	(Mat)PetscToPointer((mat) ));
}
PETSC_EXTERN void  matdensereplacearray_(Mat mat, PetscScalar *array, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLSCALAR(array);
*ierr = MatDenseReplaceArray(
	(Mat)PetscToPointer((mat) ),array);
}
PETSC_EXTERN void  matcreatedense_(MPI_Fint * comm,PetscInt *m,PetscInt *n,PetscInt *M,PetscInt *N,PetscScalar *data,Mat *A, int *ierr)
{
CHKFORTRANNULLSCALAR(data);
PetscBool A_null = !*(void**) A ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(A);
*ierr = MatCreateDense(
	MPI_Comm_f2c(*(comm)),*m,*n,*M,*N,data,A);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! A_null && !*(void**) A) * (void **) A = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
