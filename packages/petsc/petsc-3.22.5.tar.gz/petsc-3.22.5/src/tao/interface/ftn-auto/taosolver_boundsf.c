#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* taosolver_bounds.c */
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
#define taosetvariablebounds_ TAOSETVARIABLEBOUNDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taosetvariablebounds_ taosetvariablebounds
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taogetvariablebounds_ TAOGETVARIABLEBOUNDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taogetvariablebounds_ taogetvariablebounds
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taocomputevariablebounds_ TAOCOMPUTEVARIABLEBOUNDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taocomputevariablebounds_ taocomputevariablebounds
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taosetinequalitybounds_ TAOSETINEQUALITYBOUNDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taosetinequalitybounds_ taosetinequalitybounds
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taogetinequalitybounds_ TAOGETINEQUALITYBOUNDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taogetinequalitybounds_ taogetinequalitybounds
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taocomputeconstraints_ TAOCOMPUTECONSTRAINTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taocomputeconstraints_ taocomputeconstraints
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taocomputedualvariables_ TAOCOMPUTEDUALVARIABLES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taocomputedualvariables_ taocomputedualvariables
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taogetdualvariables_ TAOGETDUALVARIABLES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taogetdualvariables_ taogetdualvariables
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taocomputeequalityconstraints_ TAOCOMPUTEEQUALITYCONSTRAINTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taocomputeequalityconstraints_ taocomputeequalityconstraints
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taocomputeinequalityconstraints_ TAOCOMPUTEINEQUALITYCONSTRAINTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taocomputeinequalityconstraints_ taocomputeinequalityconstraints
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  taosetvariablebounds_(Tao tao,Vec XL,Vec XU, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLOBJECT(XL);
CHKFORTRANNULLOBJECT(XU);
*ierr = TaoSetVariableBounds(
	(Tao)PetscToPointer((tao) ),
	(Vec)PetscToPointer((XL) ),
	(Vec)PetscToPointer((XU) ));
}
PETSC_EXTERN void  taogetvariablebounds_(Tao tao,Vec *XL,Vec *XU, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
PetscBool XL_null = !*(void**) XL ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(XL);
PetscBool XU_null = !*(void**) XU ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(XU);
*ierr = TaoGetVariableBounds(
	(Tao)PetscToPointer((tao) ),XL,XU);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! XL_null && !*(void**) XL) * (void **) XL = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! XU_null && !*(void**) XU) * (void **) XU = (void *)-2;
}
PETSC_EXTERN void  taocomputevariablebounds_(Tao tao, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoComputeVariableBounds(
	(Tao)PetscToPointer((tao) ));
}
PETSC_EXTERN void  taosetinequalitybounds_(Tao tao,Vec IL,Vec IU, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLOBJECT(IL);
CHKFORTRANNULLOBJECT(IU);
*ierr = TaoSetInequalityBounds(
	(Tao)PetscToPointer((tao) ),
	(Vec)PetscToPointer((IL) ),
	(Vec)PetscToPointer((IU) ));
}
PETSC_EXTERN void  taogetinequalitybounds_(Tao tao,Vec *IL,Vec *IU, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
PetscBool IL_null = !*(void**) IL ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(IL);
PetscBool IU_null = !*(void**) IU ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(IU);
*ierr = TaoGetInequalityBounds(
	(Tao)PetscToPointer((tao) ),IL,IU);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! IL_null && !*(void**) IL) * (void **) IL = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! IU_null && !*(void**) IU) * (void **) IU = (void *)-2;
}
PETSC_EXTERN void  taocomputeconstraints_(Tao tao,Vec X,Vec C, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLOBJECT(X);
CHKFORTRANNULLOBJECT(C);
*ierr = TaoComputeConstraints(
	(Tao)PetscToPointer((tao) ),
	(Vec)PetscToPointer((X) ),
	(Vec)PetscToPointer((C) ));
}
PETSC_EXTERN void  taocomputedualvariables_(Tao tao,Vec DL,Vec DU, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLOBJECT(DL);
CHKFORTRANNULLOBJECT(DU);
*ierr = TaoComputeDualVariables(
	(Tao)PetscToPointer((tao) ),
	(Vec)PetscToPointer((DL) ),
	(Vec)PetscToPointer((DU) ));
}
PETSC_EXTERN void  taogetdualvariables_(Tao tao,Vec *DE,Vec *DI, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
PetscBool DE_null = !*(void**) DE ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(DE);
PetscBool DI_null = !*(void**) DI ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(DI);
*ierr = TaoGetDualVariables(
	(Tao)PetscToPointer((tao) ),DE,DI);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! DE_null && !*(void**) DE) * (void **) DE = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! DI_null && !*(void**) DI) * (void **) DI = (void *)-2;
}
PETSC_EXTERN void  taocomputeequalityconstraints_(Tao tao,Vec X,Vec CE, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLOBJECT(X);
CHKFORTRANNULLOBJECT(CE);
*ierr = TaoComputeEqualityConstraints(
	(Tao)PetscToPointer((tao) ),
	(Vec)PetscToPointer((X) ),
	(Vec)PetscToPointer((CE) ));
}
PETSC_EXTERN void  taocomputeinequalityconstraints_(Tao tao,Vec X,Vec CI, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLOBJECT(X);
CHKFORTRANNULLOBJECT(CI);
*ierr = TaoComputeInequalityConstraints(
	(Tao)PetscToPointer((tao) ),
	(Vec)PetscToPointer((X) ),
	(Vec)PetscToPointer((CI) ));
}
#if defined(__cplusplus)
}
#endif
