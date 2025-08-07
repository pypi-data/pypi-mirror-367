#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* matnest.c */
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
#define matnestgetsubmat_ MATNESTGETSUBMAT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matnestgetsubmat_ matnestgetsubmat
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matnestsetsubmat_ MATNESTSETSUBMAT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matnestsetsubmat_ matnestsetsubmat
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matnestgetsize_ MATNESTGETSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matnestgetsize_ matnestgetsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matnestgetiss_ MATNESTGETISS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matnestgetiss_ matnestgetiss
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matnestgetlocaliss_ MATNESTGETLOCALISS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matnestgetlocaliss_ matnestgetlocaliss
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matnestsetvectype_ MATNESTSETVECTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matnestsetvectype_ matnestsetvectype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matnestsetsubmats_ MATNESTSETSUBMATS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matnestsetsubmats_ matnestsetsubmats
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matnestgetsubmat_(Mat A,PetscInt *idxm,PetscInt *jdxm,Mat *sub, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool sub_null = !*(void**) sub ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sub);
*ierr = MatNestGetSubMat(
	(Mat)PetscToPointer((A) ),*idxm,*jdxm,sub);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sub_null && !*(void**) sub) * (void **) sub = (void *)-2;
}
PETSC_EXTERN void  matnestsetsubmat_(Mat A,PetscInt *idxm,PetscInt *jdxm,Mat sub, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(sub);
*ierr = MatNestSetSubMat(
	(Mat)PetscToPointer((A) ),*idxm,*jdxm,
	(Mat)PetscToPointer((sub) ));
}
PETSC_EXTERN void  matnestgetsize_(Mat A,PetscInt *M,PetscInt *N, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLINTEGER(M);
CHKFORTRANNULLINTEGER(N);
*ierr = MatNestGetSize(
	(Mat)PetscToPointer((A) ),M,N);
}
PETSC_EXTERN void  matnestgetiss_(Mat A,IS rows[],IS cols[], int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool rows_null = !*(void**) rows ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(rows);
PetscBool cols_null = !*(void**) cols ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(cols);
*ierr = MatNestGetISs(
	(Mat)PetscToPointer((A) ),rows,cols);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! rows_null && !*(void**) rows) * (void **) rows = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! cols_null && !*(void**) cols) * (void **) cols = (void *)-2;
}
PETSC_EXTERN void  matnestgetlocaliss_(Mat A,IS rows[],IS cols[], int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool rows_null = !*(void**) rows ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(rows);
PetscBool cols_null = !*(void**) cols ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(cols);
*ierr = MatNestGetLocalISs(
	(Mat)PetscToPointer((A) ),rows,cols);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! rows_null && !*(void**) rows) * (void **) rows = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! cols_null && !*(void**) cols) * (void **) cols = (void *)-2;
}
PETSC_EXTERN void  matnestsetvectype_(Mat A,char *vtype, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(A);
/* insert Fortran-to-C conversion for vtype */
  FIXCHAR(vtype,cl0,_cltmp0);
*ierr = MatNestSetVecType(
	(Mat)PetscToPointer((A) ),_cltmp0);
  FREECHAR(vtype,_cltmp0);
}
PETSC_EXTERN void  matnestsetsubmats_(Mat A,PetscInt *nr, IS is_row[],PetscInt *nc, IS is_col[], Mat a[], int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool is_row_null = !*(void**) is_row ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is_row);
PetscBool is_col_null = !*(void**) is_col ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is_col);
PetscBool a_null = !*(void**) a ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(a);
*ierr = MatNestSetSubMats(
	(Mat)PetscToPointer((A) ),*nr,is_row,*nc,is_col,a);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is_row_null && !*(void**) is_row) * (void **) is_row = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is_col_null && !*(void**) is_col) * (void **) is_col = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! a_null && !*(void**) a) * (void **) a = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
