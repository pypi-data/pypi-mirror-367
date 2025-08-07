#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* tsadapt.c */
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
#define tsadaptsettype_ TSADAPTSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadaptsettype_ tsadaptsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadaptgettype_ TSADAPTGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadaptgettype_ tsadaptgettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadaptload_ TSADAPTLOAD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadaptload_ tsadaptload
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadaptreset_ TSADAPTRESET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadaptreset_ tsadaptreset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadaptsetmonitor_ TSADAPTSETMONITOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadaptsetmonitor_ tsadaptsetmonitor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadaptsetalwaysaccept_ TSADAPTSETALWAYSACCEPT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadaptsetalwaysaccept_ tsadaptsetalwaysaccept
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadaptsetsafety_ TSADAPTSETSAFETY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadaptsetsafety_ tsadaptsetsafety
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadaptgetsafety_ TSADAPTGETSAFETY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadaptgetsafety_ tsadaptgetsafety
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadaptsetmaxignore_ TSADAPTSETMAXIGNORE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadaptsetmaxignore_ tsadaptsetmaxignore
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadaptgetmaxignore_ TSADAPTGETMAXIGNORE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadaptgetmaxignore_ tsadaptgetmaxignore
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadaptsetclip_ TSADAPTSETCLIP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadaptsetclip_ tsadaptsetclip
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadaptgetclip_ TSADAPTGETCLIP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadaptgetclip_ tsadaptgetclip
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadaptsetscalesolvefailed_ TSADAPTSETSCALESOLVEFAILED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadaptsetscalesolvefailed_ tsadaptsetscalesolvefailed
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadaptgetscalesolvefailed_ TSADAPTGETSCALESOLVEFAILED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadaptgetscalesolvefailed_ tsadaptgetscalesolvefailed
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadaptsetsteplimits_ TSADAPTSETSTEPLIMITS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadaptsetsteplimits_ tsadaptsetsteplimits
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadaptgetsteplimits_ TSADAPTGETSTEPLIMITS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadaptgetsteplimits_ tsadaptgetsteplimits
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadaptcandidatesclear_ TSADAPTCANDIDATESCLEAR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadaptcandidatesclear_ tsadaptcandidatesclear
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadaptsettimestepincreasedelay_ TSADAPTSETTIMESTEPINCREASEDELAY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadaptsettimestepincreasedelay_ tsadaptsettimestepincreasedelay
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadaptcheckstage_ TSADAPTCHECKSTAGE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadaptcheckstage_ tsadaptcheckstage
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tsadaptcreate_ TSADAPTCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tsadaptcreate_ tsadaptcreate
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  tsadaptsettype_(TSAdapt adapt,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(adapt);
/* insert Fortran-to-C conversion for type */
  FIXCHAR(type,cl0,_cltmp0);
*ierr = TSAdaptSetType(
	(TSAdapt)PetscToPointer((adapt) ),_cltmp0);
  FREECHAR(type,_cltmp0);
}
PETSC_EXTERN void  tsadaptgettype_(TSAdapt adapt,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(adapt);
*ierr = TSAdaptGetType(
	(TSAdapt)PetscToPointer((adapt) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for type */
*ierr = PetscStrncpy(type, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, type, cl0);
}
PETSC_EXTERN void  tsadaptload_(TSAdapt adapt,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(adapt);
CHKFORTRANNULLOBJECT(viewer);
*ierr = TSAdaptLoad(
	(TSAdapt)PetscToPointer((adapt) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  tsadaptreset_(TSAdapt adapt, int *ierr)
{
CHKFORTRANNULLOBJECT(adapt);
*ierr = TSAdaptReset(
	(TSAdapt)PetscToPointer((adapt) ));
}
PETSC_EXTERN void  tsadaptsetmonitor_(TSAdapt adapt,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(adapt);
*ierr = TSAdaptSetMonitor(
	(TSAdapt)PetscToPointer((adapt) ),*flg);
}
PETSC_EXTERN void  tsadaptsetalwaysaccept_(TSAdapt adapt,PetscBool *flag, int *ierr)
{
CHKFORTRANNULLOBJECT(adapt);
*ierr = TSAdaptSetAlwaysAccept(
	(TSAdapt)PetscToPointer((adapt) ),*flag);
}
PETSC_EXTERN void  tsadaptsetsafety_(TSAdapt adapt,PetscReal *safety,PetscReal *reject_safety, int *ierr)
{
CHKFORTRANNULLOBJECT(adapt);
*ierr = TSAdaptSetSafety(
	(TSAdapt)PetscToPointer((adapt) ),*safety,*reject_safety);
}
PETSC_EXTERN void  tsadaptgetsafety_(TSAdapt adapt,PetscReal *safety,PetscReal *reject_safety, int *ierr)
{
CHKFORTRANNULLOBJECT(adapt);
CHKFORTRANNULLREAL(safety);
CHKFORTRANNULLREAL(reject_safety);
*ierr = TSAdaptGetSafety(
	(TSAdapt)PetscToPointer((adapt) ),safety,reject_safety);
}
PETSC_EXTERN void  tsadaptsetmaxignore_(TSAdapt adapt,PetscReal *max_ignore, int *ierr)
{
CHKFORTRANNULLOBJECT(adapt);
*ierr = TSAdaptSetMaxIgnore(
	(TSAdapt)PetscToPointer((adapt) ),*max_ignore);
}
PETSC_EXTERN void  tsadaptgetmaxignore_(TSAdapt adapt,PetscReal *max_ignore, int *ierr)
{
CHKFORTRANNULLOBJECT(adapt);
CHKFORTRANNULLREAL(max_ignore);
*ierr = TSAdaptGetMaxIgnore(
	(TSAdapt)PetscToPointer((adapt) ),max_ignore);
}
PETSC_EXTERN void  tsadaptsetclip_(TSAdapt adapt,PetscReal *low,PetscReal *high, int *ierr)
{
CHKFORTRANNULLOBJECT(adapt);
*ierr = TSAdaptSetClip(
	(TSAdapt)PetscToPointer((adapt) ),*low,*high);
}
PETSC_EXTERN void  tsadaptgetclip_(TSAdapt adapt,PetscReal *low,PetscReal *high, int *ierr)
{
CHKFORTRANNULLOBJECT(adapt);
CHKFORTRANNULLREAL(low);
CHKFORTRANNULLREAL(high);
*ierr = TSAdaptGetClip(
	(TSAdapt)PetscToPointer((adapt) ),low,high);
}
PETSC_EXTERN void  tsadaptsetscalesolvefailed_(TSAdapt adapt,PetscReal *scale, int *ierr)
{
CHKFORTRANNULLOBJECT(adapt);
*ierr = TSAdaptSetScaleSolveFailed(
	(TSAdapt)PetscToPointer((adapt) ),*scale);
}
PETSC_EXTERN void  tsadaptgetscalesolvefailed_(TSAdapt adapt,PetscReal *scale, int *ierr)
{
CHKFORTRANNULLOBJECT(adapt);
CHKFORTRANNULLREAL(scale);
*ierr = TSAdaptGetScaleSolveFailed(
	(TSAdapt)PetscToPointer((adapt) ),scale);
}
PETSC_EXTERN void  tsadaptsetsteplimits_(TSAdapt adapt,PetscReal *hmin,PetscReal *hmax, int *ierr)
{
CHKFORTRANNULLOBJECT(adapt);
*ierr = TSAdaptSetStepLimits(
	(TSAdapt)PetscToPointer((adapt) ),*hmin,*hmax);
}
PETSC_EXTERN void  tsadaptgetsteplimits_(TSAdapt adapt,PetscReal *hmin,PetscReal *hmax, int *ierr)
{
CHKFORTRANNULLOBJECT(adapt);
CHKFORTRANNULLREAL(hmin);
CHKFORTRANNULLREAL(hmax);
*ierr = TSAdaptGetStepLimits(
	(TSAdapt)PetscToPointer((adapt) ),hmin,hmax);
}
PETSC_EXTERN void  tsadaptcandidatesclear_(TSAdapt adapt, int *ierr)
{
CHKFORTRANNULLOBJECT(adapt);
*ierr = TSAdaptCandidatesClear(
	(TSAdapt)PetscToPointer((adapt) ));
}
PETSC_EXTERN void  tsadaptsettimestepincreasedelay_(TSAdapt adapt,PetscInt *cnt, int *ierr)
{
CHKFORTRANNULLOBJECT(adapt);
*ierr = TSAdaptSetTimeStepIncreaseDelay(
	(TSAdapt)PetscToPointer((adapt) ),*cnt);
}
PETSC_EXTERN void  tsadaptcheckstage_(TSAdapt adapt,TS ts,PetscReal *t,Vec Y,PetscBool *accept, int *ierr)
{
CHKFORTRANNULLOBJECT(adapt);
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLOBJECT(Y);
*ierr = TSAdaptCheckStage(
	(TSAdapt)PetscToPointer((adapt) ),
	(TS)PetscToPointer((ts) ),*t,
	(Vec)PetscToPointer((Y) ),accept);
}
PETSC_EXTERN void  tsadaptcreate_(MPI_Fint * comm,TSAdapt *inadapt, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(inadapt);
 PetscBool inadapt_null = !*(void**) inadapt ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(inadapt);
*ierr = TSAdaptCreate(
	MPI_Comm_f2c(*(comm)),inadapt);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! inadapt_null && !*(void**) inadapt) * (void **) inadapt = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
