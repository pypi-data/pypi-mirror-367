#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* mpiaij.c */
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
#define matmpiaijgetnumbernonzeros_ MATMPIAIJGETNUMBERNONZEROS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmpiaijgetnumbernonzeros_ matmpiaijgetnumbernonzeros
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmpiaijsetusescalableincreaseoverlap_ MATMPIAIJSETUSESCALABLEINCREASEOVERLAP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmpiaijsetusescalableincreaseoverlap_ matmpiaijsetusescalableincreaseoverlap
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmpiaijsetpreallocationcsr_ MATMPIAIJSETPREALLOCATIONCSR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmpiaijsetpreallocationcsr_ matmpiaijsetpreallocationcsr
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmpiaijsetpreallocation_ MATMPIAIJSETPREALLOCATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmpiaijsetpreallocation_ matmpiaijsetpreallocation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreatempiaijwitharrays_ MATCREATEMPIAIJWITHARRAYS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreatempiaijwitharrays_ matcreatempiaijwitharrays
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matupdatempiaijwitharrays_ MATUPDATEMPIAIJWITHARRAYS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matupdatempiaijwitharrays_ matupdatempiaijwitharrays
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matupdatempiaijwitharray_ MATUPDATEMPIAIJWITHARRAY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matupdatempiaijwitharray_ matupdatempiaijwitharray
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreateaij_ MATCREATEAIJ
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreateaij_ matcreateaij
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreatempiaijsumseqaij_ MATCREATEMPIAIJSUMSEQAIJ
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreatempiaijsumseqaij_ matcreatempiaijsumseqaij
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define mataijgetlocalmat_ MATAIJGETLOCALMAT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define mataijgetlocalmat_ mataijgetlocalmat
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmpiaijgetlocalmat_ MATMPIAIJGETLOCALMAT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmpiaijgetlocalmat_ matmpiaijgetlocalmat
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmpiaijgetlocalmatmerge_ MATMPIAIJGETLOCALMATMERGE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmpiaijgetlocalmatmerge_ matmpiaijgetlocalmatmerge
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreatempiaijwithsplitarrays_ MATCREATEMPIAIJWITHSPLITARRAYS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreatempiaijwithsplitarrays_ matcreatempiaijwithsplitarrays
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matmpiaijgetnumbernonzeros_(Mat A,PetscCount *nz, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatMPIAIJGetNumberNonzeros(
	(Mat)PetscToPointer((A) ),
	(PetscCount* )PetscToPointer((nz) ));
}
PETSC_EXTERN void  matmpiaijsetusescalableincreaseoverlap_(Mat A,PetscBool *sc, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatMPIAIJSetUseScalableIncreaseOverlap(
	(Mat)PetscToPointer((A) ),*sc);
}
PETSC_EXTERN void  matmpiaijsetpreallocationcsr_(Mat B, PetscInt i[], PetscInt j[], PetscScalar v[], int *ierr)
{
CHKFORTRANNULLOBJECT(B);
CHKFORTRANNULLINTEGER(i);
CHKFORTRANNULLINTEGER(j);
CHKFORTRANNULLSCALAR(v);
*ierr = MatMPIAIJSetPreallocationCSR(
	(Mat)PetscToPointer((B) ),i,j,v);
}
PETSC_EXTERN void  matmpiaijsetpreallocation_(Mat B,PetscInt *d_nz, PetscInt d_nnz[],PetscInt *o_nz, PetscInt o_nnz[], int *ierr)
{
CHKFORTRANNULLOBJECT(B);
CHKFORTRANNULLINTEGER(d_nnz);
CHKFORTRANNULLINTEGER(o_nnz);
*ierr = MatMPIAIJSetPreallocation(
	(Mat)PetscToPointer((B) ),*d_nz,d_nnz,*o_nz,o_nnz);
}
PETSC_EXTERN void  matcreatempiaijwitharrays_(MPI_Fint * comm,PetscInt *m,PetscInt *n,PetscInt *M,PetscInt *N, PetscInt i[], PetscInt j[], PetscScalar a[],Mat *mat, int *ierr)
{
CHKFORTRANNULLINTEGER(i);
CHKFORTRANNULLINTEGER(j);
CHKFORTRANNULLSCALAR(a);
PetscBool mat_null = !*(void**) mat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mat);
*ierr = MatCreateMPIAIJWithArrays(
	MPI_Comm_f2c(*(comm)),*m,*n,*M,*N,i,j,a,mat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mat_null && !*(void**) mat) * (void **) mat = (void *)-2;
}
PETSC_EXTERN void  matupdatempiaijwitharrays_(Mat mat,PetscInt *m,PetscInt *n,PetscInt *M,PetscInt *N, PetscInt Ii[], PetscInt J[], PetscScalar v[], int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLINTEGER(Ii);
CHKFORTRANNULLINTEGER(J);
CHKFORTRANNULLSCALAR(v);
*ierr = MatUpdateMPIAIJWithArrays(
	(Mat)PetscToPointer((mat) ),*m,*n,*M,*N,Ii,J,v);
}
PETSC_EXTERN void  matupdatempiaijwitharray_(Mat mat, PetscScalar v[], int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLSCALAR(v);
*ierr = MatUpdateMPIAIJWithArray(
	(Mat)PetscToPointer((mat) ),v);
}
PETSC_EXTERN void  matcreateaij_(MPI_Fint * comm,PetscInt *m,PetscInt *n,PetscInt *M,PetscInt *N,PetscInt *d_nz, PetscInt d_nnz[],PetscInt *o_nz, PetscInt o_nnz[],Mat *A, int *ierr)
{
CHKFORTRANNULLINTEGER(d_nnz);
CHKFORTRANNULLINTEGER(o_nnz);
PetscBool A_null = !*(void**) A ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(A);
*ierr = MatCreateAIJ(
	MPI_Comm_f2c(*(comm)),*m,*n,*M,*N,*d_nz,d_nnz,*o_nz,o_nnz,A);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! A_null && !*(void**) A) * (void **) A = (void *)-2;
}
PETSC_EXTERN void  matcreatempiaijsumseqaij_(MPI_Fint * comm,Mat seqmat,PetscInt *m,PetscInt *n,MatReuse *scall,Mat *mpimat, int *ierr)
{
CHKFORTRANNULLOBJECT(seqmat);
PetscBool mpimat_null = !*(void**) mpimat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mpimat);
*ierr = MatCreateMPIAIJSumSeqAIJ(
	MPI_Comm_f2c(*(comm)),
	(Mat)PetscToPointer((seqmat) ),*m,*n,*scall,mpimat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mpimat_null && !*(void**) mpimat) * (void **) mpimat = (void *)-2;
}
PETSC_EXTERN void  mataijgetlocalmat_(Mat A,Mat *A_loc, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool A_loc_null = !*(void**) A_loc ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(A_loc);
*ierr = MatAIJGetLocalMat(
	(Mat)PetscToPointer((A) ),A_loc);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! A_loc_null && !*(void**) A_loc) * (void **) A_loc = (void *)-2;
}
PETSC_EXTERN void  matmpiaijgetlocalmat_(Mat A,MatReuse *scall,Mat *A_loc, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool A_loc_null = !*(void**) A_loc ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(A_loc);
*ierr = MatMPIAIJGetLocalMat(
	(Mat)PetscToPointer((A) ),*scall,A_loc);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! A_loc_null && !*(void**) A_loc) * (void **) A_loc = (void *)-2;
}
PETSC_EXTERN void  matmpiaijgetlocalmatmerge_(Mat A,MatReuse *scall,IS *glob,Mat *A_loc, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool glob_null = !*(void**) glob ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(glob);
PetscBool A_loc_null = !*(void**) A_loc ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(A_loc);
*ierr = MatMPIAIJGetLocalMatMerge(
	(Mat)PetscToPointer((A) ),*scall,glob,A_loc);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! glob_null && !*(void**) glob) * (void **) glob = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! A_loc_null && !*(void**) A_loc) * (void **) A_loc = (void *)-2;
}
PETSC_EXTERN void  matcreatempiaijwithsplitarrays_(MPI_Fint * comm,PetscInt *m,PetscInt *n,PetscInt *M,PetscInt *N,PetscInt i[],PetscInt j[],PetscScalar a[],PetscInt oi[],PetscInt oj[],PetscScalar oa[],Mat *mat, int *ierr)
{
CHKFORTRANNULLINTEGER(i);
CHKFORTRANNULLINTEGER(j);
CHKFORTRANNULLSCALAR(a);
CHKFORTRANNULLINTEGER(oi);
CHKFORTRANNULLINTEGER(oj);
CHKFORTRANNULLSCALAR(oa);
PetscBool mat_null = !*(void**) mat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mat);
*ierr = MatCreateMPIAIJWithSplitArrays(
	MPI_Comm_f2c(*(comm)),*m,*n,*M,*N,i,j,a,oi,oj,oa,mat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mat_null && !*(void**) mat) * (void **) mat = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
