#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* taolinesearch.c */
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

#include "petsctaolinesearch.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taolinesearchviewfromoptions_ TAOLINESEARCHVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taolinesearchviewfromoptions_ taolinesearchviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taolinesearchview_ TAOLINESEARCHVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taolinesearchview_ taolinesearchview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taolinesearchsetup_ TAOLINESEARCHSETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taolinesearchsetup_ taolinesearchsetup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taolinesearchreset_ TAOLINESEARCHRESET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taolinesearchreset_ taolinesearchreset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taolinesearchdestroy_ TAOLINESEARCHDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taolinesearchdestroy_ taolinesearchdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taolinesearchapply_ TAOLINESEARCHAPPLY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taolinesearchapply_ taolinesearchapply
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taolinesearchsettype_ TAOLINESEARCHSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taolinesearchsettype_ taolinesearchsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taolinesearchsetfromoptions_ TAOLINESEARCHSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taolinesearchsetfromoptions_ taolinesearchsetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taolinesearchgettype_ TAOLINESEARCHGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taolinesearchgettype_ taolinesearchgettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taolinesearchgetnumberfunctionevaluations_ TAOLINESEARCHGETNUMBERFUNCTIONEVALUATIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taolinesearchgetnumberfunctionevaluations_ taolinesearchgetnumberfunctionevaluations
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taolinesearchisusingtaoroutines_ TAOLINESEARCHISUSINGTAOROUTINES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taolinesearchisusingtaoroutines_ taolinesearchisusingtaoroutines
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taolinesearchusetaoroutines_ TAOLINESEARCHUSETAOROUTINES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taolinesearchusetaoroutines_ taolinesearchusetaoroutines
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taolinesearchcomputeobjective_ TAOLINESEARCHCOMPUTEOBJECTIVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taolinesearchcomputeobjective_ taolinesearchcomputeobjective
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taolinesearchcomputeobjectiveandgradient_ TAOLINESEARCHCOMPUTEOBJECTIVEANDGRADIENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taolinesearchcomputeobjectiveandgradient_ taolinesearchcomputeobjectiveandgradient
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taolinesearchcomputegradient_ TAOLINESEARCHCOMPUTEGRADIENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taolinesearchcomputegradient_ taolinesearchcomputegradient
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taolinesearchcomputeobjectiveandgts_ TAOLINESEARCHCOMPUTEOBJECTIVEANDGTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taolinesearchcomputeobjectiveandgts_ taolinesearchcomputeobjectiveandgts
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taolinesearchgetsolution_ TAOLINESEARCHGETSOLUTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taolinesearchgetsolution_ taolinesearchgetsolution
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taolinesearchgetstartingvector_ TAOLINESEARCHGETSTARTINGVECTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taolinesearchgetstartingvector_ taolinesearchgetstartingvector
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taolinesearchgetstepdirection_ TAOLINESEARCHGETSTEPDIRECTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taolinesearchgetstepdirection_ taolinesearchgetstepdirection
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taolinesearchgetfullstepobjective_ TAOLINESEARCHGETFULLSTEPOBJECTIVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taolinesearchgetfullstepobjective_ taolinesearchgetfullstepobjective
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taolinesearchsetvariablebounds_ TAOLINESEARCHSETVARIABLEBOUNDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taolinesearchsetvariablebounds_ taolinesearchsetvariablebounds
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taolinesearchsetinitialsteplength_ TAOLINESEARCHSETINITIALSTEPLENGTH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taolinesearchsetinitialsteplength_ taolinesearchsetinitialsteplength
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taolinesearchgetsteplength_ TAOLINESEARCHGETSTEPLENGTH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taolinesearchgetsteplength_ taolinesearchgetsteplength
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taolinesearchappendoptionsprefix_ TAOLINESEARCHAPPENDOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taolinesearchappendoptionsprefix_ taolinesearchappendoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taolinesearchgetoptionsprefix_ TAOLINESEARCHGETOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taolinesearchgetoptionsprefix_ taolinesearchgetoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taolinesearchsetoptionsprefix_ TAOLINESEARCHSETOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taolinesearchsetoptionsprefix_ taolinesearchsetoptionsprefix
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  taolinesearchviewfromoptions_(TaoLineSearch A,PetscObject obj, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = TaoLineSearchViewFromOptions(
	(TaoLineSearch)PetscToPointer((A) ),
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  taolinesearchview_(TaoLineSearch ls,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(ls);
CHKFORTRANNULLOBJECT(viewer);
*ierr = TaoLineSearchView(
	(TaoLineSearch)PetscToPointer((ls) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  taolinesearchsetup_(TaoLineSearch ls, int *ierr)
{
CHKFORTRANNULLOBJECT(ls);
*ierr = TaoLineSearchSetUp(
	(TaoLineSearch)PetscToPointer((ls) ));
}
PETSC_EXTERN void  taolinesearchreset_(TaoLineSearch ls, int *ierr)
{
CHKFORTRANNULLOBJECT(ls);
*ierr = TaoLineSearchReset(
	(TaoLineSearch)PetscToPointer((ls) ));
}
PETSC_EXTERN void  taolinesearchdestroy_(TaoLineSearch *ls, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(ls);
 PetscBool ls_null = !*(void**) ls ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ls);
*ierr = TaoLineSearchDestroy(ls);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ls_null && !*(void**) ls) * (void **) ls = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(ls);
 }
PETSC_EXTERN void  taolinesearchapply_(TaoLineSearch ls,Vec x,PetscReal *f,Vec g,Vec s,PetscReal *steplength,TaoLineSearchConvergedReason *reason, int *ierr)
{
CHKFORTRANNULLOBJECT(ls);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLREAL(f);
CHKFORTRANNULLOBJECT(g);
CHKFORTRANNULLOBJECT(s);
CHKFORTRANNULLREAL(steplength);
*ierr = TaoLineSearchApply(
	(TaoLineSearch)PetscToPointer((ls) ),
	(Vec)PetscToPointer((x) ),f,
	(Vec)PetscToPointer((g) ),
	(Vec)PetscToPointer((s) ),steplength,reason);
}
PETSC_EXTERN void  taolinesearchsettype_(TaoLineSearch ls,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ls);
/* insert Fortran-to-C conversion for type */
  FIXCHAR(type,cl0,_cltmp0);
*ierr = TaoLineSearchSetType(
	(TaoLineSearch)PetscToPointer((ls) ),_cltmp0);
  FREECHAR(type,_cltmp0);
}
PETSC_EXTERN void  taolinesearchsetfromoptions_(TaoLineSearch ls, int *ierr)
{
CHKFORTRANNULLOBJECT(ls);
*ierr = TaoLineSearchSetFromOptions(
	(TaoLineSearch)PetscToPointer((ls) ));
}
PETSC_EXTERN void  taolinesearchgettype_(TaoLineSearch ls,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ls);
*ierr = TaoLineSearchGetType(
	(TaoLineSearch)PetscToPointer((ls) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for type */
*ierr = PetscStrncpy(type, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, type, cl0);
}
PETSC_EXTERN void  taolinesearchgetnumberfunctionevaluations_(TaoLineSearch ls,PetscInt *nfeval,PetscInt *ngeval,PetscInt *nfgeval, int *ierr)
{
CHKFORTRANNULLOBJECT(ls);
CHKFORTRANNULLINTEGER(nfeval);
CHKFORTRANNULLINTEGER(ngeval);
CHKFORTRANNULLINTEGER(nfgeval);
*ierr = TaoLineSearchGetNumberFunctionEvaluations(
	(TaoLineSearch)PetscToPointer((ls) ),nfeval,ngeval,nfgeval);
}
PETSC_EXTERN void  taolinesearchisusingtaoroutines_(TaoLineSearch ls,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(ls);
*ierr = TaoLineSearchIsUsingTaoRoutines(
	(TaoLineSearch)PetscToPointer((ls) ),flg);
}
PETSC_EXTERN void  taolinesearchusetaoroutines_(TaoLineSearch ls,Tao ts, int *ierr)
{
CHKFORTRANNULLOBJECT(ls);
CHKFORTRANNULLOBJECT(ts);
*ierr = TaoLineSearchUseTaoRoutines(
	(TaoLineSearch)PetscToPointer((ls) ),
	(Tao)PetscToPointer((ts) ));
}
PETSC_EXTERN void  taolinesearchcomputeobjective_(TaoLineSearch ls,Vec x,PetscReal *f, int *ierr)
{
CHKFORTRANNULLOBJECT(ls);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLREAL(f);
*ierr = TaoLineSearchComputeObjective(
	(TaoLineSearch)PetscToPointer((ls) ),
	(Vec)PetscToPointer((x) ),f);
}
PETSC_EXTERN void  taolinesearchcomputeobjectiveandgradient_(TaoLineSearch ls,Vec x,PetscReal *f,Vec g, int *ierr)
{
CHKFORTRANNULLOBJECT(ls);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLREAL(f);
CHKFORTRANNULLOBJECT(g);
*ierr = TaoLineSearchComputeObjectiveAndGradient(
	(TaoLineSearch)PetscToPointer((ls) ),
	(Vec)PetscToPointer((x) ),f,
	(Vec)PetscToPointer((g) ));
}
PETSC_EXTERN void  taolinesearchcomputegradient_(TaoLineSearch ls,Vec x,Vec g, int *ierr)
{
CHKFORTRANNULLOBJECT(ls);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(g);
*ierr = TaoLineSearchComputeGradient(
	(TaoLineSearch)PetscToPointer((ls) ),
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((g) ));
}
PETSC_EXTERN void  taolinesearchcomputeobjectiveandgts_(TaoLineSearch ls,Vec x,PetscReal *f,PetscReal *gts, int *ierr)
{
CHKFORTRANNULLOBJECT(ls);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLREAL(f);
CHKFORTRANNULLREAL(gts);
*ierr = TaoLineSearchComputeObjectiveAndGTS(
	(TaoLineSearch)PetscToPointer((ls) ),
	(Vec)PetscToPointer((x) ),f,gts);
}
PETSC_EXTERN void  taolinesearchgetsolution_(TaoLineSearch ls,Vec x,PetscReal *f,Vec g,PetscReal *steplength,TaoLineSearchConvergedReason *reason, int *ierr)
{
CHKFORTRANNULLOBJECT(ls);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLREAL(f);
CHKFORTRANNULLOBJECT(g);
CHKFORTRANNULLREAL(steplength);
*ierr = TaoLineSearchGetSolution(
	(TaoLineSearch)PetscToPointer((ls) ),
	(Vec)PetscToPointer((x) ),f,
	(Vec)PetscToPointer((g) ),steplength,reason);
}
PETSC_EXTERN void  taolinesearchgetstartingvector_(TaoLineSearch ls,Vec *x, int *ierr)
{
CHKFORTRANNULLOBJECT(ls);
PetscBool x_null = !*(void**) x ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(x);
*ierr = TaoLineSearchGetStartingVector(
	(TaoLineSearch)PetscToPointer((ls) ),x);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! x_null && !*(void**) x) * (void **) x = (void *)-2;
}
PETSC_EXTERN void  taolinesearchgetstepdirection_(TaoLineSearch ls,Vec *s, int *ierr)
{
CHKFORTRANNULLOBJECT(ls);
PetscBool s_null = !*(void**) s ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(s);
*ierr = TaoLineSearchGetStepDirection(
	(TaoLineSearch)PetscToPointer((ls) ),s);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! s_null && !*(void**) s) * (void **) s = (void *)-2;
}
PETSC_EXTERN void  taolinesearchgetfullstepobjective_(TaoLineSearch ls,PetscReal *f_fullstep, int *ierr)
{
CHKFORTRANNULLOBJECT(ls);
CHKFORTRANNULLREAL(f_fullstep);
*ierr = TaoLineSearchGetFullStepObjective(
	(TaoLineSearch)PetscToPointer((ls) ),f_fullstep);
}
PETSC_EXTERN void  taolinesearchsetvariablebounds_(TaoLineSearch ls,Vec xl,Vec xu, int *ierr)
{
CHKFORTRANNULLOBJECT(ls);
CHKFORTRANNULLOBJECT(xl);
CHKFORTRANNULLOBJECT(xu);
*ierr = TaoLineSearchSetVariableBounds(
	(TaoLineSearch)PetscToPointer((ls) ),
	(Vec)PetscToPointer((xl) ),
	(Vec)PetscToPointer((xu) ));
}
PETSC_EXTERN void  taolinesearchsetinitialsteplength_(TaoLineSearch ls,PetscReal *s, int *ierr)
{
CHKFORTRANNULLOBJECT(ls);
*ierr = TaoLineSearchSetInitialStepLength(
	(TaoLineSearch)PetscToPointer((ls) ),*s);
}
PETSC_EXTERN void  taolinesearchgetsteplength_(TaoLineSearch ls,PetscReal *s, int *ierr)
{
CHKFORTRANNULLOBJECT(ls);
CHKFORTRANNULLREAL(s);
*ierr = TaoLineSearchGetStepLength(
	(TaoLineSearch)PetscToPointer((ls) ),s);
}
PETSC_EXTERN void  taolinesearchappendoptionsprefix_(TaoLineSearch ls, char p[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ls);
/* insert Fortran-to-C conversion for p */
  FIXCHAR(p,cl0,_cltmp0);
*ierr = TaoLineSearchAppendOptionsPrefix(
	(TaoLineSearch)PetscToPointer((ls) ),_cltmp0);
  FREECHAR(p,_cltmp0);
}
PETSC_EXTERN void  taolinesearchgetoptionsprefix_(TaoLineSearch ls, char *p, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ls);
*ierr = TaoLineSearchGetOptionsPrefix(
	(TaoLineSearch)PetscToPointer((ls) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for p */
*ierr = PetscStrncpy(p, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, p, cl0);
}
PETSC_EXTERN void  taolinesearchsetoptionsprefix_(TaoLineSearch ls, char p[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ls);
/* insert Fortran-to-C conversion for p */
  FIXCHAR(p,cl0,_cltmp0);
*ierr = TaoLineSearchSetOptionsPrefix(
	(TaoLineSearch)PetscToPointer((ls) ),_cltmp0);
  FREECHAR(p,_cltmp0);
}
#if defined(__cplusplus)
}
#endif
