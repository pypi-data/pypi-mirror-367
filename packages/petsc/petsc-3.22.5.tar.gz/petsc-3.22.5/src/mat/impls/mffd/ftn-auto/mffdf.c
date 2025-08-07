#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* mffd.c */
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
#define matmffdsettype_ MATMFFDSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmffdsettype_ matmffdsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmffdsetoptionsprefix_ MATMFFDSETOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmffdsetoptionsprefix_ matmffdsetoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreatemffd_ MATCREATEMFFD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreatemffd_ matcreatemffd
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmffdgeth_ MATMFFDGETH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmffdgeth_ matmffdgeth
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmffdsetperiod_ MATMFFDSETPERIOD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmffdsetperiod_ matmffdsetperiod
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmffdsetfunctionerror_ MATMFFDSETFUNCTIONERROR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmffdsetfunctionerror_ matmffdsetfunctionerror
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmffdsethhistory_ MATMFFDSETHHISTORY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmffdsethhistory_ matmffdsethhistory
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmffdresethhistory_ MATMFFDRESETHHISTORY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmffdresethhistory_ matmffdresethhistory
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmffdsetbase_ MATMFFDSETBASE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmffdsetbase_ matmffdsetbase
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matmffdcheckpositivity_ MATMFFDCHECKPOSITIVITY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matmffdcheckpositivity_ matmffdcheckpositivity
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matmffdsettype_(Mat mat,char *ftype, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(mat);
/* insert Fortran-to-C conversion for ftype */
  FIXCHAR(ftype,cl0,_cltmp0);
*ierr = MatMFFDSetType(
	(Mat)PetscToPointer((mat) ),_cltmp0);
  FREECHAR(ftype,_cltmp0);
}
PETSC_EXTERN void  matmffdsetoptionsprefix_(Mat mat, char prefix[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(mat);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = MatMFFDSetOptionsPrefix(
	(Mat)PetscToPointer((mat) ),_cltmp0);
  FREECHAR(prefix,_cltmp0);
}
PETSC_EXTERN void  matcreatemffd_(MPI_Fint * comm,PetscInt *m,PetscInt *n,PetscInt *M,PetscInt *N,Mat *J, int *ierr)
{
PetscBool J_null = !*(void**) J ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(J);
*ierr = MatCreateMFFD(
	MPI_Comm_f2c(*(comm)),*m,*n,*M,*N,J);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! J_null && !*(void**) J) * (void **) J = (void *)-2;
}
PETSC_EXTERN void  matmffdgeth_(Mat mat,PetscScalar *h, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLSCALAR(h);
*ierr = MatMFFDGetH(
	(Mat)PetscToPointer((mat) ),h);
}
PETSC_EXTERN void  matmffdsetperiod_(Mat mat,PetscInt *period, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatMFFDSetPeriod(
	(Mat)PetscToPointer((mat) ),*period);
}
PETSC_EXTERN void  matmffdsetfunctionerror_(Mat mat,PetscReal *error, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatMFFDSetFunctionError(
	(Mat)PetscToPointer((mat) ),*error);
}
PETSC_EXTERN void  matmffdsethhistory_(Mat J,PetscScalar history[],PetscInt *nhistory, int *ierr)
{
CHKFORTRANNULLOBJECT(J);
CHKFORTRANNULLSCALAR(history);
*ierr = MatMFFDSetHHistory(
	(Mat)PetscToPointer((J) ),history,*nhistory);
}
PETSC_EXTERN void  matmffdresethhistory_(Mat J, int *ierr)
{
CHKFORTRANNULLOBJECT(J);
*ierr = MatMFFDResetHHistory(
	(Mat)PetscToPointer((J) ));
}
PETSC_EXTERN void  matmffdsetbase_(Mat J,Vec U,Vec F, int *ierr)
{
CHKFORTRANNULLOBJECT(J);
CHKFORTRANNULLOBJECT(U);
CHKFORTRANNULLOBJECT(F);
*ierr = MatMFFDSetBase(
	(Mat)PetscToPointer((J) ),
	(Vec)PetscToPointer((U) ),
	(Vec)PetscToPointer((F) ));
}
PETSC_EXTERN void  matmffdcheckpositivity_(void*dummy,Vec U,Vec a,PetscScalar *h, int *ierr)
{
CHKFORTRANNULLOBJECT(U);
CHKFORTRANNULLOBJECT(a);
CHKFORTRANNULLSCALAR(h);
*ierr = MatMFFDCheckPositivity(dummy,
	(Vec)PetscToPointer((U) ),
	(Vec)PetscToPointer((a) ),h);
}
#if defined(__cplusplus)
}
#endif
