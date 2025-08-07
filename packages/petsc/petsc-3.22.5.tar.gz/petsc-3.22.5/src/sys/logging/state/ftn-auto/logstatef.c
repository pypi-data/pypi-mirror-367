#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* logstate.c */
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

#include "petsclog.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstatecreate_ PETSCLOGSTATECREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstatecreate_ petsclogstatecreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstatedestroy_ PETSCLOGSTATEDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstatedestroy_ petsclogstatedestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstatestagepush_ PETSCLOGSTATESTAGEPUSH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstatestagepush_ petsclogstatestagepush
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstatestagepop_ PETSCLOGSTATESTAGEPOP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstatestagepop_ petsclogstatestagepop
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstategetcurrentstage_ PETSCLOGSTATEGETCURRENTSTAGE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstategetcurrentstage_ petsclogstategetcurrentstage
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstatestageregister_ PETSCLOGSTATESTAGEREGISTER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstatestageregister_ petsclogstatestageregister
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstateeventregister_ PETSCLOGSTATEEVENTREGISTER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstateeventregister_ petsclogstateeventregister
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstateeventsetcollective_ PETSCLOGSTATEEVENTSETCOLLECTIVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstateeventsetcollective_ petsclogstateeventsetcollective
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstatestagesetactive_ PETSCLOGSTATESTAGESETACTIVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstatestagesetactive_ petsclogstatestagesetactive
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstatestagegetactive_ PETSCLOGSTATESTAGEGETACTIVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstatestagegetactive_ petsclogstatestagegetactive
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstateeventsetactive_ PETSCLOGSTATEEVENTSETACTIVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstateeventsetactive_ petsclogstateeventsetactive
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstateeventsetactiveall_ PETSCLOGSTATEEVENTSETACTIVEALL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstateeventsetactiveall_ petsclogstateeventsetactiveall
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstateclasssetactive_ PETSCLOGSTATECLASSSETACTIVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstateclasssetactive_ petsclogstateclasssetactive
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstateclasssetactiveall_ PETSCLOGSTATECLASSSETACTIVEALL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstateclasssetactiveall_ petsclogstateclasssetactiveall
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstateeventgetactive_ PETSCLOGSTATEEVENTGETACTIVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstateeventgetactive_ petsclogstateeventgetactive
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstategeteventfromname_ PETSCLOGSTATEGETEVENTFROMNAME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstategeteventfromname_ petsclogstategeteventfromname
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstategetstagefromname_ PETSCLOGSTATEGETSTAGEFROMNAME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstategetstagefromname_ petsclogstategetstagefromname
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstategetclassfromname_ PETSCLOGSTATEGETCLASSFROMNAME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstategetclassfromname_ petsclogstategetclassfromname
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstategetclassfromclassid_ PETSCLOGSTATEGETCLASSFROMCLASSID
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstategetclassfromclassid_ petsclogstategetclassfromclassid
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstategetnumevents_ PETSCLOGSTATEGETNUMEVENTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstategetnumevents_ petsclogstategetnumevents
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstategetnumstages_ PETSCLOGSTATEGETNUMSTAGES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstategetnumstages_ petsclogstategetnumstages
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstategetnumclasses_ PETSCLOGSTATEGETNUMCLASSES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstategetnumclasses_ petsclogstategetnumclasses
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstateeventgetinfo_ PETSCLOGSTATEEVENTGETINFO
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstateeventgetinfo_ petsclogstateeventgetinfo
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstatestagegetinfo_ PETSCLOGSTATESTAGEGETINFO
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstatestagegetinfo_ petsclogstatestagegetinfo
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstateclassregister_ PETSCLOGSTATECLASSREGISTER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstateclassregister_ petsclogstateclassregister
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstateclassgetinfo_ PETSCLOGSTATECLASSGETINFO
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstateclassgetinfo_ petsclogstateclassgetinfo
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petsclogstatecreate_(PetscLogState *state, int *ierr)
{
PetscBool state_null = !*(void**) state ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(state);
*ierr = PetscLogStateCreate(state);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! state_null && !*(void**) state) * (void **) state = (void *)-2;
}
PETSC_EXTERN void  petsclogstatedestroy_(PetscLogState *state, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(state);
 PetscBool state_null = !*(void**) state ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(state);
*ierr = PetscLogStateDestroy(state);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! state_null && !*(void**) state) * (void **) state = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(state);
 }
PETSC_EXTERN void  petsclogstatestagepush_(PetscLogState state,PetscLogStage *stage, int *ierr)
{
CHKFORTRANNULLOBJECT(state);
*ierr = PetscLogStateStagePush(
	(PetscLogState)PetscToPointer((state) ),*stage);
}
PETSC_EXTERN void  petsclogstatestagepop_(PetscLogState state, int *ierr)
{
CHKFORTRANNULLOBJECT(state);
*ierr = PetscLogStateStagePop(
	(PetscLogState)PetscToPointer((state) ));
}
PETSC_EXTERN void  petsclogstategetcurrentstage_(PetscLogState state,PetscLogStage *current, int *ierr)
{
CHKFORTRANNULLOBJECT(state);
*ierr = PetscLogStateGetCurrentStage(
	(PetscLogState)PetscToPointer((state) ),current);
}
PETSC_EXTERN void  petsclogstatestageregister_(PetscLogState state, char sname[],PetscLogStage *stage, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(state);
/* insert Fortran-to-C conversion for sname */
  FIXCHAR(sname,cl0,_cltmp0);
*ierr = PetscLogStateStageRegister(
	(PetscLogState)PetscToPointer((state) ),_cltmp0,stage);
  FREECHAR(sname,_cltmp0);
}
PETSC_EXTERN void  petsclogstateeventregister_(PetscLogState state, char sname[],PetscClassId *id,PetscLogEvent *event, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(state);
/* insert Fortran-to-C conversion for sname */
  FIXCHAR(sname,cl0,_cltmp0);
*ierr = PetscLogStateEventRegister(
	(PetscLogState)PetscToPointer((state) ),_cltmp0,*id,event);
  FREECHAR(sname,_cltmp0);
}
PETSC_EXTERN void  petsclogstateeventsetcollective_(PetscLogState state,PetscLogEvent *event,PetscBool *collective, int *ierr)
{
CHKFORTRANNULLOBJECT(state);
*ierr = PetscLogStateEventSetCollective(
	(PetscLogState)PetscToPointer((state) ),*event,*collective);
}
PETSC_EXTERN void  petsclogstatestagesetactive_(PetscLogState state,PetscLogStage *stage,PetscBool *isActive, int *ierr)
{
CHKFORTRANNULLOBJECT(state);
*ierr = PetscLogStateStageSetActive(
	(PetscLogState)PetscToPointer((state) ),*stage,*isActive);
}
PETSC_EXTERN void  petsclogstatestagegetactive_(PetscLogState state,PetscLogStage *stage,PetscBool *isActive, int *ierr)
{
CHKFORTRANNULLOBJECT(state);
*ierr = PetscLogStateStageGetActive(
	(PetscLogState)PetscToPointer((state) ),*stage,isActive);
}
PETSC_EXTERN void  petsclogstateeventsetactive_(PetscLogState state,PetscLogStage *stage,PetscLogEvent *event,PetscBool *isActive, int *ierr)
{
CHKFORTRANNULLOBJECT(state);
*ierr = PetscLogStateEventSetActive(
	(PetscLogState)PetscToPointer((state) ),*stage,*event,*isActive);
}
PETSC_EXTERN void  petsclogstateeventsetactiveall_(PetscLogState state,PetscLogEvent *event,PetscBool *isActive, int *ierr)
{
CHKFORTRANNULLOBJECT(state);
*ierr = PetscLogStateEventSetActiveAll(
	(PetscLogState)PetscToPointer((state) ),*event,*isActive);
}
PETSC_EXTERN void  petsclogstateclasssetactive_(PetscLogState state,PetscLogStage *stage,PetscClassId *classid,PetscBool *isActive, int *ierr)
{
CHKFORTRANNULLOBJECT(state);
*ierr = PetscLogStateClassSetActive(
	(PetscLogState)PetscToPointer((state) ),*stage,*classid,*isActive);
}
PETSC_EXTERN void  petsclogstateclasssetactiveall_(PetscLogState state,PetscClassId *classid,PetscBool *isActive, int *ierr)
{
CHKFORTRANNULLOBJECT(state);
*ierr = PetscLogStateClassSetActiveAll(
	(PetscLogState)PetscToPointer((state) ),*classid,*isActive);
}
PETSC_EXTERN void  petsclogstateeventgetactive_(PetscLogState state,PetscLogStage *stage,PetscLogEvent *event,PetscBool *isActive, int *ierr)
{
CHKFORTRANNULLOBJECT(state);
*ierr = PetscLogStateEventGetActive(
	(PetscLogState)PetscToPointer((state) ),*stage,*event,isActive);
}
PETSC_EXTERN void  petsclogstategeteventfromname_(PetscLogState state, char name[],PetscLogEvent *event, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(state);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscLogStateGetEventFromName(
	(PetscLogState)PetscToPointer((state) ),_cltmp0,event);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petsclogstategetstagefromname_(PetscLogState state, char name[],PetscLogStage *stage, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(state);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscLogStateGetStageFromName(
	(PetscLogState)PetscToPointer((state) ),_cltmp0,stage);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petsclogstategetclassfromname_(PetscLogState state, char name[],PetscLogClass *clss, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(state);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscLogStateGetClassFromName(
	(PetscLogState)PetscToPointer((state) ),_cltmp0,clss);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petsclogstategetclassfromclassid_(PetscLogState state,PetscClassId *classid,PetscLogClass *clss, int *ierr)
{
CHKFORTRANNULLOBJECT(state);
*ierr = PetscLogStateGetClassFromClassId(
	(PetscLogState)PetscToPointer((state) ),*classid,clss);
}
PETSC_EXTERN void  petsclogstategetnumevents_(PetscLogState state,PetscInt *numEvents, int *ierr)
{
CHKFORTRANNULLOBJECT(state);
CHKFORTRANNULLINTEGER(numEvents);
*ierr = PetscLogStateGetNumEvents(
	(PetscLogState)PetscToPointer((state) ),numEvents);
}
PETSC_EXTERN void  petsclogstategetnumstages_(PetscLogState state,PetscInt *numStages, int *ierr)
{
CHKFORTRANNULLOBJECT(state);
CHKFORTRANNULLINTEGER(numStages);
*ierr = PetscLogStateGetNumStages(
	(PetscLogState)PetscToPointer((state) ),numStages);
}
PETSC_EXTERN void  petsclogstategetnumclasses_(PetscLogState state,PetscInt *numClasses, int *ierr)
{
CHKFORTRANNULLOBJECT(state);
CHKFORTRANNULLINTEGER(numClasses);
*ierr = PetscLogStateGetNumClasses(
	(PetscLogState)PetscToPointer((state) ),numClasses);
}
PETSC_EXTERN void  petsclogstateeventgetinfo_(PetscLogState state,PetscLogEvent *event,PetscLogEventInfo *info, int *ierr)
{
CHKFORTRANNULLOBJECT(state);
*ierr = PetscLogStateEventGetInfo(
	(PetscLogState)PetscToPointer((state) ),*event,info);
}
PETSC_EXTERN void  petsclogstatestagegetinfo_(PetscLogState state,PetscLogStage *stage,PetscLogStageInfo *info, int *ierr)
{
CHKFORTRANNULLOBJECT(state);
*ierr = PetscLogStateStageGetInfo(
	(PetscLogState)PetscToPointer((state) ),*stage,
	(PetscLogStageInfo* )PetscToPointer((info) ));
}
PETSC_EXTERN void  petsclogstateclassregister_(PetscLogState state, char name[],PetscClassId *id,PetscLogClass *logclass, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(state);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscLogStateClassRegister(
	(PetscLogState)PetscToPointer((state) ),_cltmp0,*id,logclass);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petsclogstateclassgetinfo_(PetscLogState state,PetscLogClass *clss,PetscLogClassInfo *info, int *ierr)
{
CHKFORTRANNULLOBJECT(state);
*ierr = PetscLogStateClassGetInfo(
	(PetscLogState)PetscToPointer((state) ),*clss,info);
}
#if defined(__cplusplus)
}
#endif
