#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* linesearch.c */
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

#include "petscsnes.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchmonitorcancel_ SNESLINESEARCHMONITORCANCEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchmonitorcancel_ sneslinesearchmonitorcancel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchmonitor_ SNESLINESEARCHMONITOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchmonitor_ sneslinesearchmonitor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchcreate_ SNESLINESEARCHCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchcreate_ sneslinesearchcreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchsetup_ SNESLINESEARCHSETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchsetup_ sneslinesearchsetup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchreset_ SNESLINESEARCHRESET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchreset_ sneslinesearchreset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchprecheck_ SNESLINESEARCHPRECHECK
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchprecheck_ sneslinesearchprecheck
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchpostcheck_ SNESLINESEARCHPOSTCHECK
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchpostcheck_ sneslinesearchpostcheck
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchapply_ SNESLINESEARCHAPPLY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchapply_ sneslinesearchapply
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchdestroy_ SNESLINESEARCHDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchdestroy_ sneslinesearchdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchsetdefaultmonitor_ SNESLINESEARCHSETDEFAULTMONITOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchsetdefaultmonitor_ sneslinesearchsetdefaultmonitor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchgetdefaultmonitor_ SNESLINESEARCHGETDEFAULTMONITOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchgetdefaultmonitor_ sneslinesearchgetdefaultmonitor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchsetfromoptions_ SNESLINESEARCHSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchsetfromoptions_ sneslinesearchsetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchview_ SNESLINESEARCHVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchview_ sneslinesearchview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchgettype_ SNESLINESEARCHGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchgettype_ sneslinesearchgettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchsettype_ SNESLINESEARCHSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchsettype_ sneslinesearchsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchsetsnes_ SNESLINESEARCHSETSNES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchsetsnes_ sneslinesearchsetsnes
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchgetsnes_ SNESLINESEARCHGETSNES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchgetsnes_ sneslinesearchgetsnes
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchgetlambda_ SNESLINESEARCHGETLAMBDA
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchgetlambda_ sneslinesearchgetlambda
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchsetlambda_ SNESLINESEARCHSETLAMBDA
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchsetlambda_ sneslinesearchsetlambda
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchgettolerances_ SNESLINESEARCHGETTOLERANCES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchgettolerances_ sneslinesearchgettolerances
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchsettolerances_ SNESLINESEARCHSETTOLERANCES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchsettolerances_ sneslinesearchsettolerances
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchgetdamping_ SNESLINESEARCHGETDAMPING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchgetdamping_ sneslinesearchgetdamping
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchsetdamping_ SNESLINESEARCHSETDAMPING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchsetdamping_ sneslinesearchsetdamping
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchgetorder_ SNESLINESEARCHGETORDER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchgetorder_ sneslinesearchgetorder
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchsetorder_ SNESLINESEARCHSETORDER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchsetorder_ sneslinesearchsetorder
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchgetnorms_ SNESLINESEARCHGETNORMS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchgetnorms_ sneslinesearchgetnorms
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchsetnorms_ SNESLINESEARCHSETNORMS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchsetnorms_ sneslinesearchsetnorms
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchcomputenorms_ SNESLINESEARCHCOMPUTENORMS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchcomputenorms_ sneslinesearchcomputenorms
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchsetcomputenorms_ SNESLINESEARCHSETCOMPUTENORMS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchsetcomputenorms_ sneslinesearchsetcomputenorms
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchgetvecs_ SNESLINESEARCHGETVECS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchgetvecs_ sneslinesearchgetvecs
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchsetvecs_ SNESLINESEARCHSETVECS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchsetvecs_ sneslinesearchsetvecs
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchappendoptionsprefix_ SNESLINESEARCHAPPENDOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchappendoptionsprefix_ sneslinesearchappendoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchgetoptionsprefix_ SNESLINESEARCHGETOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchgetoptionsprefix_ sneslinesearchgetoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchgetreason_ SNESLINESEARCHGETREASON
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchgetreason_ sneslinesearchgetreason
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define sneslinesearchsetreason_ SNESLINESEARCHSETREASON
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define sneslinesearchsetreason_ sneslinesearchsetreason
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  sneslinesearchmonitorcancel_(SNESLineSearch ls, int *ierr)
{
CHKFORTRANNULLOBJECT(ls);
*ierr = SNESLineSearchMonitorCancel(
	(SNESLineSearch)PetscToPointer((ls) ));
}
PETSC_EXTERN void  sneslinesearchmonitor_(SNESLineSearch ls, int *ierr)
{
CHKFORTRANNULLOBJECT(ls);
*ierr = SNESLineSearchMonitor(
	(SNESLineSearch)PetscToPointer((ls) ));
}
PETSC_EXTERN void  sneslinesearchcreate_(MPI_Fint * comm,SNESLineSearch *outlinesearch, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(outlinesearch);
 PetscBool outlinesearch_null = !*(void**) outlinesearch ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(outlinesearch);
*ierr = SNESLineSearchCreate(
	MPI_Comm_f2c(*(comm)),outlinesearch);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! outlinesearch_null && !*(void**) outlinesearch) * (void **) outlinesearch = (void *)-2;
}
PETSC_EXTERN void  sneslinesearchsetup_(SNESLineSearch linesearch, int *ierr)
{
CHKFORTRANNULLOBJECT(linesearch);
*ierr = SNESLineSearchSetUp(
	(SNESLineSearch)PetscToPointer((linesearch) ));
}
PETSC_EXTERN void  sneslinesearchreset_(SNESLineSearch linesearch, int *ierr)
{
CHKFORTRANNULLOBJECT(linesearch);
*ierr = SNESLineSearchReset(
	(SNESLineSearch)PetscToPointer((linesearch) ));
}
PETSC_EXTERN void  sneslinesearchprecheck_(SNESLineSearch linesearch,Vec X,Vec Y,PetscBool *changed, int *ierr)
{
CHKFORTRANNULLOBJECT(linesearch);
CHKFORTRANNULLOBJECT(X);
CHKFORTRANNULLOBJECT(Y);
*ierr = SNESLineSearchPreCheck(
	(SNESLineSearch)PetscToPointer((linesearch) ),
	(Vec)PetscToPointer((X) ),
	(Vec)PetscToPointer((Y) ),changed);
}
PETSC_EXTERN void  sneslinesearchpostcheck_(SNESLineSearch linesearch,Vec X,Vec Y,Vec W,PetscBool *changed_Y,PetscBool *changed_W, int *ierr)
{
CHKFORTRANNULLOBJECT(linesearch);
CHKFORTRANNULLOBJECT(X);
CHKFORTRANNULLOBJECT(Y);
CHKFORTRANNULLOBJECT(W);
*ierr = SNESLineSearchPostCheck(
	(SNESLineSearch)PetscToPointer((linesearch) ),
	(Vec)PetscToPointer((X) ),
	(Vec)PetscToPointer((Y) ),
	(Vec)PetscToPointer((W) ),changed_Y,changed_W);
}
PETSC_EXTERN void  sneslinesearchapply_(SNESLineSearch linesearch,Vec X,Vec F,PetscReal *fnorm,Vec Y, int *ierr)
{
CHKFORTRANNULLOBJECT(linesearch);
CHKFORTRANNULLOBJECT(X);
CHKFORTRANNULLOBJECT(F);
CHKFORTRANNULLREAL(fnorm);
CHKFORTRANNULLOBJECT(Y);
*ierr = SNESLineSearchApply(
	(SNESLineSearch)PetscToPointer((linesearch) ),
	(Vec)PetscToPointer((X) ),
	(Vec)PetscToPointer((F) ),fnorm,
	(Vec)PetscToPointer((Y) ));
}
PETSC_EXTERN void  sneslinesearchdestroy_(SNESLineSearch *linesearch, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(linesearch);
 PetscBool linesearch_null = !*(void**) linesearch ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(linesearch);
*ierr = SNESLineSearchDestroy(linesearch);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! linesearch_null && !*(void**) linesearch) * (void **) linesearch = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(linesearch);
 }
PETSC_EXTERN void  sneslinesearchsetdefaultmonitor_(SNESLineSearch linesearch,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(linesearch);
CHKFORTRANNULLOBJECT(viewer);
*ierr = SNESLineSearchSetDefaultMonitor(
	(SNESLineSearch)PetscToPointer((linesearch) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  sneslinesearchgetdefaultmonitor_(SNESLineSearch linesearch,PetscViewer *monitor, int *ierr)
{
CHKFORTRANNULLOBJECT(linesearch);
PetscBool monitor_null = !*(void**) monitor ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(monitor);
*ierr = SNESLineSearchGetDefaultMonitor(
	(SNESLineSearch)PetscToPointer((linesearch) ),monitor);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! monitor_null && !*(void**) monitor) * (void **) monitor = (void *)-2;
}
PETSC_EXTERN void  sneslinesearchsetfromoptions_(SNESLineSearch linesearch, int *ierr)
{
CHKFORTRANNULLOBJECT(linesearch);
*ierr = SNESLineSearchSetFromOptions(
	(SNESLineSearch)PetscToPointer((linesearch) ));
}
PETSC_EXTERN void  sneslinesearchview_(SNESLineSearch linesearch,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(linesearch);
CHKFORTRANNULLOBJECT(viewer);
*ierr = SNESLineSearchView(
	(SNESLineSearch)PetscToPointer((linesearch) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  sneslinesearchgettype_(SNESLineSearch linesearch,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(linesearch);
*ierr = SNESLineSearchGetType(
	(SNESLineSearch)PetscToPointer((linesearch) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for type */
*ierr = PetscStrncpy(type, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, type, cl0);
}
PETSC_EXTERN void  sneslinesearchsettype_(SNESLineSearch linesearch,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(linesearch);
/* insert Fortran-to-C conversion for type */
  FIXCHAR(type,cl0,_cltmp0);
*ierr = SNESLineSearchSetType(
	(SNESLineSearch)PetscToPointer((linesearch) ),_cltmp0);
  FREECHAR(type,_cltmp0);
}
PETSC_EXTERN void  sneslinesearchsetsnes_(SNESLineSearch linesearch,SNES snes, int *ierr)
{
CHKFORTRANNULLOBJECT(linesearch);
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESLineSearchSetSNES(
	(SNESLineSearch)PetscToPointer((linesearch) ),
	(SNES)PetscToPointer((snes) ));
}
PETSC_EXTERN void  sneslinesearchgetsnes_(SNESLineSearch linesearch,SNES *snes, int *ierr)
{
CHKFORTRANNULLOBJECT(linesearch);
PetscBool snes_null = !*(void**) snes ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESLineSearchGetSNES(
	(SNESLineSearch)PetscToPointer((linesearch) ),snes);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! snes_null && !*(void**) snes) * (void **) snes = (void *)-2;
}
PETSC_EXTERN void  sneslinesearchgetlambda_(SNESLineSearch linesearch,PetscReal *lambda, int *ierr)
{
CHKFORTRANNULLOBJECT(linesearch);
CHKFORTRANNULLREAL(lambda);
*ierr = SNESLineSearchGetLambda(
	(SNESLineSearch)PetscToPointer((linesearch) ),lambda);
}
PETSC_EXTERN void  sneslinesearchsetlambda_(SNESLineSearch linesearch,PetscReal *lambda, int *ierr)
{
CHKFORTRANNULLOBJECT(linesearch);
*ierr = SNESLineSearchSetLambda(
	(SNESLineSearch)PetscToPointer((linesearch) ),*lambda);
}
PETSC_EXTERN void  sneslinesearchgettolerances_(SNESLineSearch linesearch,PetscReal *steptol,PetscReal *maxstep,PetscReal *rtol,PetscReal *atol,PetscReal *ltol,PetscInt *max_its, int *ierr)
{
CHKFORTRANNULLOBJECT(linesearch);
CHKFORTRANNULLREAL(steptol);
CHKFORTRANNULLREAL(maxstep);
CHKFORTRANNULLREAL(rtol);
CHKFORTRANNULLREAL(atol);
CHKFORTRANNULLREAL(ltol);
CHKFORTRANNULLINTEGER(max_its);
*ierr = SNESLineSearchGetTolerances(
	(SNESLineSearch)PetscToPointer((linesearch) ),steptol,maxstep,rtol,atol,ltol,max_its);
}
PETSC_EXTERN void  sneslinesearchsettolerances_(SNESLineSearch linesearch,PetscReal *steptol,PetscReal *maxstep,PetscReal *rtol,PetscReal *atol,PetscReal *ltol,PetscInt *max_it, int *ierr)
{
CHKFORTRANNULLOBJECT(linesearch);
*ierr = SNESLineSearchSetTolerances(
	(SNESLineSearch)PetscToPointer((linesearch) ),*steptol,*maxstep,*rtol,*atol,*ltol,*max_it);
}
PETSC_EXTERN void  sneslinesearchgetdamping_(SNESLineSearch linesearch,PetscReal *damping, int *ierr)
{
CHKFORTRANNULLOBJECT(linesearch);
CHKFORTRANNULLREAL(damping);
*ierr = SNESLineSearchGetDamping(
	(SNESLineSearch)PetscToPointer((linesearch) ),damping);
}
PETSC_EXTERN void  sneslinesearchsetdamping_(SNESLineSearch linesearch,PetscReal *damping, int *ierr)
{
CHKFORTRANNULLOBJECT(linesearch);
*ierr = SNESLineSearchSetDamping(
	(SNESLineSearch)PetscToPointer((linesearch) ),*damping);
}
PETSC_EXTERN void  sneslinesearchgetorder_(SNESLineSearch linesearch,PetscInt *order, int *ierr)
{
CHKFORTRANNULLOBJECT(linesearch);
CHKFORTRANNULLINTEGER(order);
*ierr = SNESLineSearchGetOrder(
	(SNESLineSearch)PetscToPointer((linesearch) ),order);
}
PETSC_EXTERN void  sneslinesearchsetorder_(SNESLineSearch linesearch,PetscInt *order, int *ierr)
{
CHKFORTRANNULLOBJECT(linesearch);
*ierr = SNESLineSearchSetOrder(
	(SNESLineSearch)PetscToPointer((linesearch) ),*order);
}
PETSC_EXTERN void  sneslinesearchgetnorms_(SNESLineSearch linesearch,PetscReal *xnorm,PetscReal *fnorm,PetscReal *ynorm, int *ierr)
{
CHKFORTRANNULLOBJECT(linesearch);
CHKFORTRANNULLREAL(xnorm);
CHKFORTRANNULLREAL(fnorm);
CHKFORTRANNULLREAL(ynorm);
*ierr = SNESLineSearchGetNorms(
	(SNESLineSearch)PetscToPointer((linesearch) ),xnorm,fnorm,ynorm);
}
PETSC_EXTERN void  sneslinesearchsetnorms_(SNESLineSearch linesearch,PetscReal *xnorm,PetscReal *fnorm,PetscReal *ynorm, int *ierr)
{
CHKFORTRANNULLOBJECT(linesearch);
*ierr = SNESLineSearchSetNorms(
	(SNESLineSearch)PetscToPointer((linesearch) ),*xnorm,*fnorm,*ynorm);
}
PETSC_EXTERN void  sneslinesearchcomputenorms_(SNESLineSearch linesearch, int *ierr)
{
CHKFORTRANNULLOBJECT(linesearch);
*ierr = SNESLineSearchComputeNorms(
	(SNESLineSearch)PetscToPointer((linesearch) ));
}
PETSC_EXTERN void  sneslinesearchsetcomputenorms_(SNESLineSearch linesearch,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(linesearch);
*ierr = SNESLineSearchSetComputeNorms(
	(SNESLineSearch)PetscToPointer((linesearch) ),*flg);
}
PETSC_EXTERN void  sneslinesearchgetvecs_(SNESLineSearch linesearch,Vec *X,Vec *F,Vec *Y,Vec *W,Vec *G, int *ierr)
{
CHKFORTRANNULLOBJECT(linesearch);
PetscBool X_null = !*(void**) X ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(X);
PetscBool F_null = !*(void**) F ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(F);
PetscBool Y_null = !*(void**) Y ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(Y);
PetscBool W_null = !*(void**) W ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(W);
PetscBool G_null = !*(void**) G ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(G);
*ierr = SNESLineSearchGetVecs(
	(SNESLineSearch)PetscToPointer((linesearch) ),X,F,Y,W,G);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! X_null && !*(void**) X) * (void **) X = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! F_null && !*(void**) F) * (void **) F = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! Y_null && !*(void**) Y) * (void **) Y = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! W_null && !*(void**) W) * (void **) W = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! G_null && !*(void**) G) * (void **) G = (void *)-2;
}
PETSC_EXTERN void  sneslinesearchsetvecs_(SNESLineSearch linesearch,Vec X,Vec F,Vec Y,Vec W,Vec G, int *ierr)
{
CHKFORTRANNULLOBJECT(linesearch);
CHKFORTRANNULLOBJECT(X);
CHKFORTRANNULLOBJECT(F);
CHKFORTRANNULLOBJECT(Y);
CHKFORTRANNULLOBJECT(W);
CHKFORTRANNULLOBJECT(G);
*ierr = SNESLineSearchSetVecs(
	(SNESLineSearch)PetscToPointer((linesearch) ),
	(Vec)PetscToPointer((X) ),
	(Vec)PetscToPointer((F) ),
	(Vec)PetscToPointer((Y) ),
	(Vec)PetscToPointer((W) ),
	(Vec)PetscToPointer((G) ));
}
PETSC_EXTERN void  sneslinesearchappendoptionsprefix_(SNESLineSearch linesearch, char prefix[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(linesearch);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = SNESLineSearchAppendOptionsPrefix(
	(SNESLineSearch)PetscToPointer((linesearch) ),_cltmp0);
  FREECHAR(prefix,_cltmp0);
}
PETSC_EXTERN void  sneslinesearchgetoptionsprefix_(SNESLineSearch linesearch, char *prefix, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(linesearch);
*ierr = SNESLineSearchGetOptionsPrefix(
	(SNESLineSearch)PetscToPointer((linesearch) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for prefix */
*ierr = PetscStrncpy(prefix, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, prefix, cl0);
}
PETSC_EXTERN void  sneslinesearchgetreason_(SNESLineSearch linesearch,SNESLineSearchReason *result, int *ierr)
{
CHKFORTRANNULLOBJECT(linesearch);
*ierr = SNESLineSearchGetReason(
	(SNESLineSearch)PetscToPointer((linesearch) ),result);
}
PETSC_EXTERN void  sneslinesearchsetreason_(SNESLineSearch linesearch,SNESLineSearchReason *result, int *ierr)
{
CHKFORTRANNULLOBJECT(linesearch);
*ierr = SNESLineSearchSetReason(
	(SNESLineSearch)PetscToPointer((linesearch) ),*result);
}
#if defined(__cplusplus)
}
#endif
