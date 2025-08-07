#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* taosolver_hj.c */
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

#include "petsctao.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taocomputehessian_ TAOCOMPUTEHESSIAN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taocomputehessian_ taocomputehessian
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taocomputejacobian_ TAOCOMPUTEJACOBIAN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taocomputejacobian_ taocomputejacobian
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taocomputeresidualjacobian_ TAOCOMPUTERESIDUALJACOBIAN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taocomputeresidualjacobian_ taocomputeresidualjacobian
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taocomputejacobianstate_ TAOCOMPUTEJACOBIANSTATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taocomputejacobianstate_ taocomputejacobianstate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taocomputejacobiandesign_ TAOCOMPUTEJACOBIANDESIGN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taocomputejacobiandesign_ taocomputejacobiandesign
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taosetstatedesignis_ TAOSETSTATEDESIGNIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taosetstatedesignis_ taosetstatedesignis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taocomputejacobianequality_ TAOCOMPUTEJACOBIANEQUALITY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taocomputejacobianequality_ taocomputejacobianequality
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taocomputejacobianinequality_ TAOCOMPUTEJACOBIANINEQUALITY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taocomputejacobianinequality_ taocomputejacobianinequality
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  taocomputehessian_(Tao tao,Vec X,Mat H,Mat Hpre, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLOBJECT(X);
CHKFORTRANNULLOBJECT(H);
CHKFORTRANNULLOBJECT(Hpre);
*ierr = TaoComputeHessian(
	(Tao)PetscToPointer((tao) ),
	(Vec)PetscToPointer((X) ),
	(Mat)PetscToPointer((H) ),
	(Mat)PetscToPointer((Hpre) ));
}
PETSC_EXTERN void  taocomputejacobian_(Tao tao,Vec X,Mat J,Mat Jpre, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLOBJECT(X);
CHKFORTRANNULLOBJECT(J);
CHKFORTRANNULLOBJECT(Jpre);
*ierr = TaoComputeJacobian(
	(Tao)PetscToPointer((tao) ),
	(Vec)PetscToPointer((X) ),
	(Mat)PetscToPointer((J) ),
	(Mat)PetscToPointer((Jpre) ));
}
PETSC_EXTERN void  taocomputeresidualjacobian_(Tao tao,Vec X,Mat J,Mat Jpre, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLOBJECT(X);
CHKFORTRANNULLOBJECT(J);
CHKFORTRANNULLOBJECT(Jpre);
*ierr = TaoComputeResidualJacobian(
	(Tao)PetscToPointer((tao) ),
	(Vec)PetscToPointer((X) ),
	(Mat)PetscToPointer((J) ),
	(Mat)PetscToPointer((Jpre) ));
}
PETSC_EXTERN void  taocomputejacobianstate_(Tao tao,Vec X,Mat J,Mat Jpre,Mat Jinv, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLOBJECT(X);
CHKFORTRANNULLOBJECT(J);
CHKFORTRANNULLOBJECT(Jpre);
CHKFORTRANNULLOBJECT(Jinv);
*ierr = TaoComputeJacobianState(
	(Tao)PetscToPointer((tao) ),
	(Vec)PetscToPointer((X) ),
	(Mat)PetscToPointer((J) ),
	(Mat)PetscToPointer((Jpre) ),
	(Mat)PetscToPointer((Jinv) ));
}
PETSC_EXTERN void  taocomputejacobiandesign_(Tao tao,Vec X,Mat J, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLOBJECT(X);
CHKFORTRANNULLOBJECT(J);
*ierr = TaoComputeJacobianDesign(
	(Tao)PetscToPointer((tao) ),
	(Vec)PetscToPointer((X) ),
	(Mat)PetscToPointer((J) ));
}
PETSC_EXTERN void  taosetstatedesignis_(Tao tao,IS s_is,IS d_is, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLOBJECT(s_is);
CHKFORTRANNULLOBJECT(d_is);
*ierr = TaoSetStateDesignIS(
	(Tao)PetscToPointer((tao) ),
	(IS)PetscToPointer((s_is) ),
	(IS)PetscToPointer((d_is) ));
}
PETSC_EXTERN void  taocomputejacobianequality_(Tao tao,Vec X,Mat J,Mat Jpre, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLOBJECT(X);
CHKFORTRANNULLOBJECT(J);
CHKFORTRANNULLOBJECT(Jpre);
*ierr = TaoComputeJacobianEquality(
	(Tao)PetscToPointer((tao) ),
	(Vec)PetscToPointer((X) ),
	(Mat)PetscToPointer((J) ),
	(Mat)PetscToPointer((Jpre) ));
}
PETSC_EXTERN void  taocomputejacobianinequality_(Tao tao,Vec X,Mat J,Mat Jpre, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLOBJECT(X);
CHKFORTRANNULLOBJECT(J);
CHKFORTRANNULLOBJECT(Jpre);
*ierr = TaoComputeJacobianInequality(
	(Tao)PetscToPointer((tao) ),
	(Vec)PetscToPointer((X) ),
	(Mat)PetscToPointer((J) ),
	(Mat)PetscToPointer((Jpre) ));
}
#if defined(__cplusplus)
}
#endif
