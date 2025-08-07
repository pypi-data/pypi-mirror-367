#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* convest.c */
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

#include "petscconvest.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscconvestdestroy_ PETSCCONVESTDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscconvestdestroy_ petscconvestdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscconvestsetfromoptions_ PETSCCONVESTSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscconvestsetfromoptions_ petscconvestsetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscconvestview_ PETSCCONVESTVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscconvestview_ petscconvestview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscconvestgetsolver_ PETSCCONVESTGETSOLVER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscconvestgetsolver_ petscconvestgetsolver
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscconvestsetsolver_ PETSCCONVESTSETSOLVER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscconvestsetsolver_ petscconvestsetsolver
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscconvestsetup_ PETSCCONVESTSETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscconvestsetup_ petscconvestsetup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscconvestmonitordefault_ PETSCCONVESTMONITORDEFAULT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscconvestmonitordefault_ petscconvestmonitordefault
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscconvestgetconvrate_ PETSCCONVESTGETCONVRATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscconvestgetconvrate_ petscconvestgetconvrate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscconvestrateview_ PETSCCONVESTRATEVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscconvestrateview_ petscconvestrateview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscconvestcreate_ PETSCCONVESTCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscconvestcreate_ petscconvestcreate
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscconvestdestroy_(PetscConvEst *ce, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(ce);
 PetscBool ce_null = !*(void**) ce ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ce);
*ierr = PetscConvEstDestroy(ce);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ce_null && !*(void**) ce) * (void **) ce = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(ce);
 }
PETSC_EXTERN void  petscconvestsetfromoptions_(PetscConvEst ce, int *ierr)
{
CHKFORTRANNULLOBJECT(ce);
*ierr = PetscConvEstSetFromOptions(
	(PetscConvEst)PetscToPointer((ce) ));
}
PETSC_EXTERN void  petscconvestview_(PetscConvEst ce,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(ce);
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscConvEstView(
	(PetscConvEst)PetscToPointer((ce) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petscconvestgetsolver_(PetscConvEst ce,PetscObject *solver, int *ierr)
{
CHKFORTRANNULLOBJECT(ce);
PetscBool solver_null = !*(void**) solver ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(solver);
*ierr = PetscConvEstGetSolver(
	(PetscConvEst)PetscToPointer((ce) ),solver);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! solver_null && !*(void**) solver) * (void **) solver = (void *)-2;
}
PETSC_EXTERN void  petscconvestsetsolver_(PetscConvEst ce,PetscObject solver, int *ierr)
{
CHKFORTRANNULLOBJECT(ce);
CHKFORTRANNULLOBJECT(solver);
*ierr = PetscConvEstSetSolver(
	(PetscConvEst)PetscToPointer((ce) ),
	(PetscObject)PetscToPointer((solver) ));
}
PETSC_EXTERN void  petscconvestsetup_(PetscConvEst ce, int *ierr)
{
CHKFORTRANNULLOBJECT(ce);
*ierr = PetscConvEstSetUp(
	(PetscConvEst)PetscToPointer((ce) ));
}
PETSC_EXTERN void  petscconvestmonitordefault_(PetscConvEst ce,PetscInt *r, int *ierr)
{
CHKFORTRANNULLOBJECT(ce);
*ierr = PetscConvEstMonitorDefault(
	(PetscConvEst)PetscToPointer((ce) ),*r);
}
PETSC_EXTERN void  petscconvestgetconvrate_(PetscConvEst ce,PetscReal alpha[], int *ierr)
{
CHKFORTRANNULLOBJECT(ce);
CHKFORTRANNULLREAL(alpha);
*ierr = PetscConvEstGetConvRate(
	(PetscConvEst)PetscToPointer((ce) ),alpha);
}
PETSC_EXTERN void  petscconvestrateview_(PetscConvEst ce, PetscReal alpha[],PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(ce);
CHKFORTRANNULLREAL(alpha);
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscConvEstRateView(
	(PetscConvEst)PetscToPointer((ce) ),alpha,PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petscconvestcreate_(MPI_Fint * comm,PetscConvEst *ce, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(ce);
 PetscBool ce_null = !*(void**) ce ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ce);
*ierr = PetscConvEstCreate(
	MPI_Comm_f2c(*(comm)),ce);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ce_null && !*(void**) ce) * (void **) ce = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
