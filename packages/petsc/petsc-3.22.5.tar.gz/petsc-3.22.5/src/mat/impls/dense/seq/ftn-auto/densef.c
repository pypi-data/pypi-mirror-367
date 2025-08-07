#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* dense.c */
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
#define matdensegetlda_ MATDENSEGETLDA
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matdensegetlda_ matdensegetlda
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matdensesetlda_ MATDENSESETLDA
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matdensesetlda_ matdensesetlda
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreateseqdense_ MATCREATESEQDENSE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreateseqdense_ matcreateseqdense
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matseqdensesetpreallocation_ MATSEQDENSESETPREALLOCATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matseqdensesetpreallocation_ matseqdensesetpreallocation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matdensegetcolumnvec_ MATDENSEGETCOLUMNVEC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matdensegetcolumnvec_ matdensegetcolumnvec
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matdenserestorecolumnvec_ MATDENSERESTORECOLUMNVEC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matdenserestorecolumnvec_ matdenserestorecolumnvec
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matdensegetcolumnvecread_ MATDENSEGETCOLUMNVECREAD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matdensegetcolumnvecread_ matdensegetcolumnvecread
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matdenserestorecolumnvecread_ MATDENSERESTORECOLUMNVECREAD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matdenserestorecolumnvecread_ matdenserestorecolumnvecread
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matdensegetcolumnvecwrite_ MATDENSEGETCOLUMNVECWRITE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matdensegetcolumnvecwrite_ matdensegetcolumnvecwrite
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matdenserestorecolumnvecwrite_ MATDENSERESTORECOLUMNVECWRITE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matdenserestorecolumnvecwrite_ matdenserestorecolumnvecwrite
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matdensegetsubmatrix_ MATDENSEGETSUBMATRIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matdensegetsubmatrix_ matdensegetsubmatrix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matdenserestoresubmatrix_ MATDENSERESTORESUBMATRIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matdenserestoresubmatrix_ matdenserestoresubmatrix
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matdensegetlda_(Mat A,PetscInt *lda, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLINTEGER(lda);
*ierr = MatDenseGetLDA(
	(Mat)PetscToPointer((A) ),lda);
}
PETSC_EXTERN void  matdensesetlda_(Mat A,PetscInt *lda, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatDenseSetLDA(
	(Mat)PetscToPointer((A) ),*lda);
}
PETSC_EXTERN void  matcreateseqdense_(MPI_Fint * comm,PetscInt *m,PetscInt *n,PetscScalar data[],Mat *A, int *ierr)
{
CHKFORTRANNULLSCALAR(data);
PetscBool A_null = !*(void**) A ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(A);
*ierr = MatCreateSeqDense(
	MPI_Comm_f2c(*(comm)),*m,*n,data,A);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! A_null && !*(void**) A) * (void **) A = (void *)-2;
}
PETSC_EXTERN void  matseqdensesetpreallocation_(Mat B,PetscScalar data[], int *ierr)
{
CHKFORTRANNULLOBJECT(B);
CHKFORTRANNULLSCALAR(data);
*ierr = MatSeqDenseSetPreallocation(
	(Mat)PetscToPointer((B) ),data);
}
PETSC_EXTERN void  matdensegetcolumnvec_(Mat A,PetscInt *col,Vec *v, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool v_null = !*(void**) v ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(v);
*ierr = MatDenseGetColumnVec(
	(Mat)PetscToPointer((A) ),*col,v);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! v_null && !*(void**) v) * (void **) v = (void *)-2;
}
PETSC_EXTERN void  matdenserestorecolumnvec_(Mat A,PetscInt *col,Vec *v, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool v_null = !*(void**) v ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(v);
*ierr = MatDenseRestoreColumnVec(
	(Mat)PetscToPointer((A) ),*col,v);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! v_null && !*(void**) v) * (void **) v = (void *)-2;
}
PETSC_EXTERN void  matdensegetcolumnvecread_(Mat A,PetscInt *col,Vec *v, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool v_null = !*(void**) v ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(v);
*ierr = MatDenseGetColumnVecRead(
	(Mat)PetscToPointer((A) ),*col,v);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! v_null && !*(void**) v) * (void **) v = (void *)-2;
}
PETSC_EXTERN void  matdenserestorecolumnvecread_(Mat A,PetscInt *col,Vec *v, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool v_null = !*(void**) v ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(v);
*ierr = MatDenseRestoreColumnVecRead(
	(Mat)PetscToPointer((A) ),*col,v);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! v_null && !*(void**) v) * (void **) v = (void *)-2;
}
PETSC_EXTERN void  matdensegetcolumnvecwrite_(Mat A,PetscInt *col,Vec *v, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool v_null = !*(void**) v ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(v);
*ierr = MatDenseGetColumnVecWrite(
	(Mat)PetscToPointer((A) ),*col,v);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! v_null && !*(void**) v) * (void **) v = (void *)-2;
}
PETSC_EXTERN void  matdenserestorecolumnvecwrite_(Mat A,PetscInt *col,Vec *v, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool v_null = !*(void**) v ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(v);
*ierr = MatDenseRestoreColumnVecWrite(
	(Mat)PetscToPointer((A) ),*col,v);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! v_null && !*(void**) v) * (void **) v = (void *)-2;
}
PETSC_EXTERN void  matdensegetsubmatrix_(Mat A,PetscInt *rbegin,PetscInt *rend,PetscInt *cbegin,PetscInt *cend,Mat *v, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool v_null = !*(void**) v ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(v);
*ierr = MatDenseGetSubMatrix(
	(Mat)PetscToPointer((A) ),*rbegin,*rend,*cbegin,*cend,v);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! v_null && !*(void**) v) * (void **) v = (void *)-2;
}
PETSC_EXTERN void  matdenserestoresubmatrix_(Mat A,Mat *v, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool v_null = !*(void**) v ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(v);
*ierr = MatDenseRestoreSubMatrix(
	(Mat)PetscToPointer((A) ),v);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! v_null && !*(void**) v) * (void **) v = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
