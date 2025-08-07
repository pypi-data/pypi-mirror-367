#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* almmutils.c */
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
#define taoalmmgettype_ TAOALMMGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoalmmgettype_ taoalmmgettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taoalmmsettype_ TAOALMMSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoalmmsettype_ taoalmmsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taoalmmgetsubsolver_ TAOALMMGETSUBSOLVER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoalmmgetsubsolver_ taoalmmgetsubsolver
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taoalmmsetsubsolver_ TAOALMMSETSUBSOLVER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoalmmsetsubsolver_ taoalmmsetsubsolver
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taoalmmgetmultipliers_ TAOALMMGETMULTIPLIERS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoalmmgetmultipliers_ taoalmmgetmultipliers
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taoalmmsetmultipliers_ TAOALMMSETMULTIPLIERS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoalmmsetmultipliers_ taoalmmsetmultipliers
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taoalmmgetprimalis_ TAOALMMGETPRIMALIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoalmmgetprimalis_ taoalmmgetprimalis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taoalmmgetdualis_ TAOALMMGETDUALIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taoalmmgetdualis_ taoalmmgetdualis
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  taoalmmgettype_(Tao tao,TaoALMMType *type, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoALMMGetType(
	(Tao)PetscToPointer((tao) ),type);
}
PETSC_EXTERN void  taoalmmsettype_(Tao tao,TaoALMMType *type, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoALMMSetType(
	(Tao)PetscToPointer((tao) ),*type);
}
PETSC_EXTERN void  taoalmmgetsubsolver_(Tao tao,Tao *subsolver, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
PetscBool subsolver_null = !*(void**) subsolver ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(subsolver);
*ierr = TaoALMMGetSubsolver(
	(Tao)PetscToPointer((tao) ),subsolver);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! subsolver_null && !*(void**) subsolver) * (void **) subsolver = (void *)-2;
}
PETSC_EXTERN void  taoalmmsetsubsolver_(Tao tao,Tao subsolver, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLOBJECT(subsolver);
*ierr = TaoALMMSetSubsolver(
	(Tao)PetscToPointer((tao) ),
	(Tao)PetscToPointer((subsolver) ));
}
PETSC_EXTERN void  taoalmmgetmultipliers_(Tao tao,Vec *Y, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
PetscBool Y_null = !*(void**) Y ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(Y);
*ierr = TaoALMMGetMultipliers(
	(Tao)PetscToPointer((tao) ),Y);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! Y_null && !*(void**) Y) * (void **) Y = (void *)-2;
}
PETSC_EXTERN void  taoalmmsetmultipliers_(Tao tao,Vec Y, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
CHKFORTRANNULLOBJECT(Y);
*ierr = TaoALMMSetMultipliers(
	(Tao)PetscToPointer((tao) ),
	(Vec)PetscToPointer((Y) ));
}
PETSC_EXTERN void  taoalmmgetprimalis_(Tao tao,IS *opt_is,IS *slack_is, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
PetscBool opt_is_null = !*(void**) opt_is ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(opt_is);
PetscBool slack_is_null = !*(void**) slack_is ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(slack_is);
*ierr = TaoALMMGetPrimalIS(
	(Tao)PetscToPointer((tao) ),opt_is,slack_is);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! opt_is_null && !*(void**) opt_is) * (void **) opt_is = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! slack_is_null && !*(void**) slack_is) * (void **) slack_is = (void *)-2;
}
PETSC_EXTERN void  taoalmmgetdualis_(Tao tao,IS *eq_is,IS *ineq_is, int *ierr)
{
CHKFORTRANNULLOBJECT(tao);
PetscBool eq_is_null = !*(void**) eq_is ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(eq_is);
PetscBool ineq_is_null = !*(void**) ineq_is ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ineq_is);
*ierr = TaoALMMGetDualIS(
	(Tao)PetscToPointer((tao) ),eq_is,ineq_is);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! eq_is_null && !*(void**) eq_is) * (void **) eq_is = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ineq_is_null && !*(void**) ineq_is) * (void **) ineq_is = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
