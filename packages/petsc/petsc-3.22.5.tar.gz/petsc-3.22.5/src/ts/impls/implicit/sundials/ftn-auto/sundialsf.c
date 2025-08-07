#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* sundials.c */
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

#include "petscts.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tssundialsgetiterations_ TSSUNDIALSGETITERATIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tssundialsgetiterations_ tssundialsgetiterations
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tssundialssettype_ TSSUNDIALSSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tssundialssettype_ tssundialssettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tssundialssetmaxord_ TSSUNDIALSSETMAXORD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tssundialssetmaxord_ tssundialssetmaxord
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tssundialssetmaxl_ TSSUNDIALSSETMAXL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tssundialssetmaxl_ tssundialssetmaxl
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tssundialssetlineartolerance_ TSSUNDIALSSETLINEARTOLERANCE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tssundialssetlineartolerance_ tssundialssetlineartolerance
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tssundialssetgramschmidttype_ TSSUNDIALSSETGRAMSCHMIDTTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tssundialssetgramschmidttype_ tssundialssetgramschmidttype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tssundialssettolerance_ TSSUNDIALSSETTOLERANCE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tssundialssettolerance_ tssundialssettolerance
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tssundialsgetpc_ TSSUNDIALSGETPC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tssundialsgetpc_ tssundialsgetpc
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tssundialssetmintimestep_ TSSUNDIALSSETMINTIMESTEP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tssundialssetmintimestep_ tssundialssetmintimestep
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tssundialssetmaxtimestep_ TSSUNDIALSSETMAXTIMESTEP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tssundialssetmaxtimestep_ tssundialssetmaxtimestep
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tssundialsmonitorinternalsteps_ TSSUNDIALSMONITORINTERNALSTEPS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tssundialsmonitorinternalsteps_ tssundialsmonitorinternalsteps
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tssundialssetusedense_ TSSUNDIALSSETUSEDENSE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tssundialssetusedense_ tssundialssetusedense
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  tssundialsgetiterations_(TS ts,int *nonlin,int *lin, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSSundialsGetIterations(
	(TS)PetscToPointer((ts) ),nonlin,lin);
}
PETSC_EXTERN void  tssundialssettype_(TS ts,TSSundialsLmmType *type, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSSundialsSetType(
	(TS)PetscToPointer((ts) ),*type);
}
PETSC_EXTERN void  tssundialssetmaxord_(TS ts,PetscInt *maxord, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSSundialsSetMaxord(
	(TS)PetscToPointer((ts) ),*maxord);
}
PETSC_EXTERN void  tssundialssetmaxl_(TS ts,PetscInt *maxl, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSSundialsSetMaxl(
	(TS)PetscToPointer((ts) ),*maxl);
}
PETSC_EXTERN void  tssundialssetlineartolerance_(TS ts,PetscReal *tol, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSSundialsSetLinearTolerance(
	(TS)PetscToPointer((ts) ),*tol);
}
PETSC_EXTERN void  tssundialssetgramschmidttype_(TS ts,TSSundialsGramSchmidtType *type, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSSundialsSetGramSchmidtType(
	(TS)PetscToPointer((ts) ),*type);
}
PETSC_EXTERN void  tssundialssettolerance_(TS ts,PetscReal *aabs,PetscReal *rel, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSSundialsSetTolerance(
	(TS)PetscToPointer((ts) ),*aabs,*rel);
}
PETSC_EXTERN void  tssundialsgetpc_(TS ts,PC *pc, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
PetscBool pc_null = !*(void**) pc ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(pc);
*ierr = TSSundialsGetPC(
	(TS)PetscToPointer((ts) ),pc);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! pc_null && !*(void**) pc) * (void **) pc = (void *)-2;
}
PETSC_EXTERN void  tssundialssetmintimestep_(TS ts,PetscReal *mindt, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSSundialsSetMinTimeStep(
	(TS)PetscToPointer((ts) ),*mindt);
}
PETSC_EXTERN void  tssundialssetmaxtimestep_(TS ts,PetscReal *maxdt, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSSundialsSetMaxTimeStep(
	(TS)PetscToPointer((ts) ),*maxdt);
}
PETSC_EXTERN void  tssundialsmonitorinternalsteps_(TS ts,PetscBool *ft, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSSundialsMonitorInternalSteps(
	(TS)PetscToPointer((ts) ),*ft);
}
PETSC_EXTERN void  tssundialssetusedense_(TS ts,PetscBool *use_dense, int *ierr)
{
CHKFORTRANNULLOBJECT(ts);
*ierr = TSSundialsSetUseDense(
	(TS)PetscToPointer((ts) ),*use_dense);
}
#if defined(__cplusplus)
}
#endif
