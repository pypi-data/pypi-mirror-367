#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* aij.c */
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
#define matseqaijsettotalpreallocation_ MATSEQAIJSETTOTALPREALLOCATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matseqaijsettotalpreallocation_ matseqaijsettotalpreallocation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matseqaijsetcolumnindices_ MATSEQAIJSETCOLUMNINDICES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matseqaijsetcolumnindices_ matseqaijsetcolumnindices
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matstorevalues_ MATSTOREVALUES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matstorevalues_ matstorevalues
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matretrievevalues_ MATRETRIEVEVALUES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matretrievevalues_ matretrievevalues
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreateseqaij_ MATCREATESEQAIJ
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreateseqaij_ matcreateseqaij
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matseqaijsetpreallocation_ MATSEQAIJSETPREALLOCATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matseqaijsetpreallocation_ matseqaijsetpreallocation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matseqaijsetpreallocationcsr_ MATSEQAIJSETPREALLOCATIONCSR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matseqaijsetpreallocationcsr_ matseqaijsetpreallocationcsr
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matseqaijkron_ MATSEQAIJKRON
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matseqaijkron_ matseqaijkron
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matseqaijgetmaxrownonzeros_ MATSEQAIJGETMAXROWNONZEROS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matseqaijgetmaxrownonzeros_ matseqaijgetmaxrownonzeros
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreateseqaijwitharrays_ MATCREATESEQAIJWITHARRAYS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreateseqaijwitharrays_ matcreateseqaijwitharrays
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreateseqaijfromtriple_ MATCREATESEQAIJFROMTRIPLE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreateseqaijfromtriple_ matcreateseqaijfromtriple
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matseqaijsettype_ MATSEQAIJSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matseqaijsettype_ matseqaijsettype
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matseqaijsettotalpreallocation_(Mat A,PetscInt *nztotal, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatSeqAIJSetTotalPreallocation(
	(Mat)PetscToPointer((A) ),*nztotal);
}
PETSC_EXTERN void  matseqaijsetcolumnindices_(Mat mat,PetscInt *indices, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLINTEGER(indices);
*ierr = MatSeqAIJSetColumnIndices(
	(Mat)PetscToPointer((mat) ),indices);
}
PETSC_EXTERN void  matstorevalues_(Mat mat, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatStoreValues(
	(Mat)PetscToPointer((mat) ));
}
PETSC_EXTERN void  matretrievevalues_(Mat mat, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatRetrieveValues(
	(Mat)PetscToPointer((mat) ));
}
PETSC_EXTERN void  matcreateseqaij_(MPI_Fint * comm,PetscInt *m,PetscInt *n,PetscInt *nz, PetscInt nnz[],Mat *A, int *ierr)
{
CHKFORTRANNULLINTEGER(nnz);
PetscBool A_null = !*(void**) A ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(A);
*ierr = MatCreateSeqAIJ(
	MPI_Comm_f2c(*(comm)),*m,*n,*nz,nnz,A);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! A_null && !*(void**) A) * (void **) A = (void *)-2;
}
PETSC_EXTERN void  matseqaijsetpreallocation_(Mat B,PetscInt *nz, PetscInt nnz[], int *ierr)
{
CHKFORTRANNULLOBJECT(B);
CHKFORTRANNULLINTEGER(nnz);
*ierr = MatSeqAIJSetPreallocation(
	(Mat)PetscToPointer((B) ),*nz,nnz);
}
PETSC_EXTERN void  matseqaijsetpreallocationcsr_(Mat B, PetscInt i[], PetscInt j[], PetscScalar v[], int *ierr)
{
CHKFORTRANNULLOBJECT(B);
CHKFORTRANNULLINTEGER(i);
CHKFORTRANNULLINTEGER(j);
CHKFORTRANNULLSCALAR(v);
*ierr = MatSeqAIJSetPreallocationCSR(
	(Mat)PetscToPointer((B) ),i,j,v);
}
PETSC_EXTERN void  matseqaijkron_(Mat A,Mat B,MatReuse *reuse,Mat *C, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(B);
PetscBool C_null = !*(void**) C ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(C);
*ierr = MatSeqAIJKron(
	(Mat)PetscToPointer((A) ),
	(Mat)PetscToPointer((B) ),*reuse,C);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! C_null && !*(void**) C) * (void **) C = (void *)-2;
}
PETSC_EXTERN void  matseqaijgetmaxrownonzeros_(Mat A,PetscInt *nz, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLINTEGER(nz);
*ierr = MatSeqAIJGetMaxRowNonzeros(
	(Mat)PetscToPointer((A) ),nz);
}
PETSC_EXTERN void  matcreateseqaijwitharrays_(MPI_Fint * comm,PetscInt *m,PetscInt *n,PetscInt i[],PetscInt j[],PetscScalar a[],Mat *mat, int *ierr)
{
CHKFORTRANNULLINTEGER(i);
CHKFORTRANNULLINTEGER(j);
CHKFORTRANNULLSCALAR(a);
PetscBool mat_null = !*(void**) mat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mat);
*ierr = MatCreateSeqAIJWithArrays(
	MPI_Comm_f2c(*(comm)),*m,*n,i,j,a,mat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mat_null && !*(void**) mat) * (void **) mat = (void *)-2;
}
PETSC_EXTERN void  matcreateseqaijfromtriple_(MPI_Fint * comm,PetscInt *m,PetscInt *n,PetscInt i[],PetscInt j[],PetscScalar a[],Mat *mat,PetscInt *nz,PetscBool *idx, int *ierr)
{
CHKFORTRANNULLINTEGER(i);
CHKFORTRANNULLINTEGER(j);
CHKFORTRANNULLSCALAR(a);
PetscBool mat_null = !*(void**) mat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mat);
*ierr = MatCreateSeqAIJFromTriple(
	MPI_Comm_f2c(*(comm)),*m,*n,i,j,a,mat,*nz,*idx);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mat_null && !*(void**) mat) * (void **) mat = (void *)-2;
}
PETSC_EXTERN void  matseqaijsettype_(Mat mat,char *matype, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(mat);
/* insert Fortran-to-C conversion for matype */
  FIXCHAR(matype,cl0,_cltmp0);
*ierr = MatSeqAIJSetType(
	(Mat)PetscToPointer((mat) ),_cltmp0);
  FREECHAR(matype,_cltmp0);
}
#if defined(__cplusplus)
}
#endif
