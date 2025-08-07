#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* traj.c */
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
#define tstrajectoryset_ TSTRAJECTORYSET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tstrajectoryset_ tstrajectoryset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tstrajectorygetnumsteps_ TSTRAJECTORYGETNUMSTEPS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tstrajectorygetnumsteps_ tstrajectorygetnumsteps
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tstrajectoryget_ TSTRAJECTORYGET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tstrajectoryget_ tstrajectoryget
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tstrajectorygetvecs_ TSTRAJECTORYGETVECS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tstrajectorygetvecs_ tstrajectorygetvecs
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tstrajectoryviewfromoptions_ TSTRAJECTORYVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tstrajectoryviewfromoptions_ tstrajectoryviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tstrajectoryview_ TSTRAJECTORYVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tstrajectoryview_ tstrajectoryview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tstrajectorycreate_ TSTRAJECTORYCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tstrajectorycreate_ tstrajectorycreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tstrajectorysettype_ TSTRAJECTORYSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tstrajectorysettype_ tstrajectorysettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tstrajectorygettype_ TSTRAJECTORYGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tstrajectorygettype_ tstrajectorygettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tstrajectoryreset_ TSTRAJECTORYRESET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tstrajectoryreset_ tstrajectoryreset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tstrajectorydestroy_ TSTRAJECTORYDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tstrajectorydestroy_ tstrajectorydestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tstrajectorysetusehistory_ TSTRAJECTORYSETUSEHISTORY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tstrajectorysetusehistory_ tstrajectorysetusehistory
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tstrajectorysetmonitor_ TSTRAJECTORYSETMONITOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tstrajectorysetmonitor_ tstrajectorysetmonitor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tstrajectorysetkeepfiles_ TSTRAJECTORYSETKEEPFILES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tstrajectorysetkeepfiles_ tstrajectorysetkeepfiles
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tstrajectorysetdirname_ TSTRAJECTORYSETDIRNAME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tstrajectorysetdirname_ tstrajectorysetdirname
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tstrajectorysetfiletemplate_ TSTRAJECTORYSETFILETEMPLATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tstrajectorysetfiletemplate_ tstrajectorysetfiletemplate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tstrajectorysetfromoptions_ TSTRAJECTORYSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tstrajectorysetfromoptions_ tstrajectorysetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tstrajectorysetup_ TSTRAJECTORYSETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tstrajectorysetup_ tstrajectorysetup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tstrajectorysetsolutiononly_ TSTRAJECTORYSETSOLUTIONONLY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tstrajectorysetsolutiononly_ tstrajectorysetsolutiononly
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tstrajectorygetsolutiononly_ TSTRAJECTORYGETSOLUTIONONLY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tstrajectorygetsolutiononly_ tstrajectorygetsolutiononly
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tstrajectorygetupdatedhistoryvecs_ TSTRAJECTORYGETUPDATEDHISTORYVECS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tstrajectorygetupdatedhistoryvecs_ tstrajectorygetupdatedhistoryvecs
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define tstrajectoryrestoreupdatedhistoryvecs_ TSTRAJECTORYRESTOREUPDATEDHISTORYVECS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define tstrajectoryrestoreupdatedhistoryvecs_ tstrajectoryrestoreupdatedhistoryvecs
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  tstrajectoryset_(TSTrajectory tj,TS ts,PetscInt *stepnum,PetscReal *time,Vec X, int *ierr)
{
CHKFORTRANNULLOBJECT(tj);
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLOBJECT(X);
*ierr = TSTrajectorySet(
	(TSTrajectory)PetscToPointer((tj) ),
	(TS)PetscToPointer((ts) ),*stepnum,*time,
	(Vec)PetscToPointer((X) ));
}
PETSC_EXTERN void  tstrajectorygetnumsteps_(TSTrajectory tj,PetscInt *steps, int *ierr)
{
CHKFORTRANNULLOBJECT(tj);
CHKFORTRANNULLINTEGER(steps);
*ierr = TSTrajectoryGetNumSteps(
	(TSTrajectory)PetscToPointer((tj) ),steps);
}
PETSC_EXTERN void  tstrajectoryget_(TSTrajectory tj,TS ts,PetscInt *stepnum,PetscReal *time, int *ierr)
{
CHKFORTRANNULLOBJECT(tj);
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLREAL(time);
*ierr = TSTrajectoryGet(
	(TSTrajectory)PetscToPointer((tj) ),
	(TS)PetscToPointer((ts) ),*stepnum,time);
}
PETSC_EXTERN void  tstrajectorygetvecs_(TSTrajectory tj,TS ts,PetscInt *stepnum,PetscReal *time,Vec U,Vec Udot, int *ierr)
{
CHKFORTRANNULLOBJECT(tj);
CHKFORTRANNULLOBJECT(ts);
CHKFORTRANNULLREAL(time);
CHKFORTRANNULLOBJECT(U);
CHKFORTRANNULLOBJECT(Udot);
*ierr = TSTrajectoryGetVecs(
	(TSTrajectory)PetscToPointer((tj) ),
	(TS)PetscToPointer((ts) ),*stepnum,time,
	(Vec)PetscToPointer((U) ),
	(Vec)PetscToPointer((Udot) ));
}
PETSC_EXTERN void  tstrajectoryviewfromoptions_(TSTrajectory A,PetscObject obj, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = TSTrajectoryViewFromOptions(
	(TSTrajectory)PetscToPointer((A) ),
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  tstrajectoryview_(TSTrajectory tj,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(tj);
CHKFORTRANNULLOBJECT(viewer);
*ierr = TSTrajectoryView(
	(TSTrajectory)PetscToPointer((tj) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  tstrajectorycreate_(MPI_Fint * comm,TSTrajectory *tj, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(tj);
 PetscBool tj_null = !*(void**) tj ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(tj);
*ierr = TSTrajectoryCreate(
	MPI_Comm_f2c(*(comm)),tj);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! tj_null && !*(void**) tj) * (void **) tj = (void *)-2;
}
PETSC_EXTERN void  tstrajectorysettype_(TSTrajectory tj,TS ts,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(tj);
CHKFORTRANNULLOBJECT(ts);
/* insert Fortran-to-C conversion for type */
  FIXCHAR(type,cl0,_cltmp0);
*ierr = TSTrajectorySetType(
	(TSTrajectory)PetscToPointer((tj) ),
	(TS)PetscToPointer((ts) ),_cltmp0);
  FREECHAR(type,_cltmp0);
}
PETSC_EXTERN void  tstrajectorygettype_(TSTrajectory tj,TS ts,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(tj);
CHKFORTRANNULLOBJECT(ts);
*ierr = TSTrajectoryGetType(
	(TSTrajectory)PetscToPointer((tj) ),
	(TS)PetscToPointer((ts) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for type */
*ierr = PetscStrncpy(type, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, type, cl0);
}
PETSC_EXTERN void  tstrajectoryreset_(TSTrajectory tj, int *ierr)
{
CHKFORTRANNULLOBJECT(tj);
*ierr = TSTrajectoryReset(
	(TSTrajectory)PetscToPointer((tj) ));
}
PETSC_EXTERN void  tstrajectorydestroy_(TSTrajectory *tj, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(tj);
 PetscBool tj_null = !*(void**) tj ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(tj);
*ierr = TSTrajectoryDestroy(tj);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! tj_null && !*(void**) tj) * (void **) tj = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(tj);
 }
PETSC_EXTERN void  tstrajectorysetusehistory_(TSTrajectory tj,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(tj);
*ierr = TSTrajectorySetUseHistory(
	(TSTrajectory)PetscToPointer((tj) ),*flg);
}
PETSC_EXTERN void  tstrajectorysetmonitor_(TSTrajectory tj,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(tj);
*ierr = TSTrajectorySetMonitor(
	(TSTrajectory)PetscToPointer((tj) ),*flg);
}
PETSC_EXTERN void  tstrajectorysetkeepfiles_(TSTrajectory tj,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(tj);
*ierr = TSTrajectorySetKeepFiles(
	(TSTrajectory)PetscToPointer((tj) ),*flg);
}
PETSC_EXTERN void  tstrajectorysetdirname_(TSTrajectory tj, char dirname[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(tj);
/* insert Fortran-to-C conversion for dirname */
  FIXCHAR(dirname,cl0,_cltmp0);
*ierr = TSTrajectorySetDirname(
	(TSTrajectory)PetscToPointer((tj) ),_cltmp0);
  FREECHAR(dirname,_cltmp0);
}
PETSC_EXTERN void  tstrajectorysetfiletemplate_(TSTrajectory tj, char filetemplate[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(tj);
/* insert Fortran-to-C conversion for filetemplate */
  FIXCHAR(filetemplate,cl0,_cltmp0);
*ierr = TSTrajectorySetFiletemplate(
	(TSTrajectory)PetscToPointer((tj) ),_cltmp0);
  FREECHAR(filetemplate,_cltmp0);
}
PETSC_EXTERN void  tstrajectorysetfromoptions_(TSTrajectory tj,TS ts, int *ierr)
{
CHKFORTRANNULLOBJECT(tj);
CHKFORTRANNULLOBJECT(ts);
*ierr = TSTrajectorySetFromOptions(
	(TSTrajectory)PetscToPointer((tj) ),
	(TS)PetscToPointer((ts) ));
}
PETSC_EXTERN void  tstrajectorysetup_(TSTrajectory tj,TS ts, int *ierr)
{
CHKFORTRANNULLOBJECT(tj);
CHKFORTRANNULLOBJECT(ts);
*ierr = TSTrajectorySetUp(
	(TSTrajectory)PetscToPointer((tj) ),
	(TS)PetscToPointer((ts) ));
}
PETSC_EXTERN void  tstrajectorysetsolutiononly_(TSTrajectory tj,PetscBool *solution_only, int *ierr)
{
CHKFORTRANNULLOBJECT(tj);
*ierr = TSTrajectorySetSolutionOnly(
	(TSTrajectory)PetscToPointer((tj) ),*solution_only);
}
PETSC_EXTERN void  tstrajectorygetsolutiononly_(TSTrajectory tj,PetscBool *solution_only, int *ierr)
{
CHKFORTRANNULLOBJECT(tj);
*ierr = TSTrajectoryGetSolutionOnly(
	(TSTrajectory)PetscToPointer((tj) ),solution_only);
}
PETSC_EXTERN void  tstrajectorygetupdatedhistoryvecs_(TSTrajectory tj,TS ts,PetscReal *time,Vec *U,Vec *Udot, int *ierr)
{
CHKFORTRANNULLOBJECT(tj);
CHKFORTRANNULLOBJECT(ts);
PetscBool U_null = !*(void**) U ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(U);
PetscBool Udot_null = !*(void**) Udot ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(Udot);
*ierr = TSTrajectoryGetUpdatedHistoryVecs(
	(TSTrajectory)PetscToPointer((tj) ),
	(TS)PetscToPointer((ts) ),*time,U,Udot);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! U_null && !*(void**) U) * (void **) U = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! Udot_null && !*(void**) Udot) * (void **) Udot = (void *)-2;
}
PETSC_EXTERN void  tstrajectoryrestoreupdatedhistoryvecs_(TSTrajectory tj,Vec *U,Vec *Udot, int *ierr)
{
CHKFORTRANNULLOBJECT(tj);
PetscBool U_null = !*(void**) U ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(U);
PetscBool Udot_null = !*(void**) Udot ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(Udot);
*ierr = TSTrajectoryRestoreUpdatedHistoryVecs(
	(TSTrajectory)PetscToPointer((tj) ),U,Udot);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! U_null && !*(void**) U) * (void **) U = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! Udot_null && !*(void**) Udot) * (void **) Udot = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
