#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* loghandler.c */
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

#include "petscsys.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscloghandlercreate_ PETSCLOGHANDLERCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscloghandlercreate_ petscloghandlercreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscloghandlerdestroy_ PETSCLOGHANDLERDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscloghandlerdestroy_ petscloghandlerdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscloghandlersetstate_ PETSCLOGHANDLERSETSTATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscloghandlersetstate_ petscloghandlersetstate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscloghandlergetstate_ PETSCLOGHANDLERGETSTATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscloghandlergetstate_ petscloghandlergetstate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscloghandlereventbegin_ PETSCLOGHANDLEREVENTBEGIN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscloghandlereventbegin_ petscloghandlereventbegin
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscloghandlereventend_ PETSCLOGHANDLEREVENTEND
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscloghandlereventend_ petscloghandlereventend
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscloghandlereventsync_ PETSCLOGHANDLEREVENTSYNC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscloghandlereventsync_ petscloghandlereventsync
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscloghandlerobjectcreate_ PETSCLOGHANDLEROBJECTCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscloghandlerobjectcreate_ petscloghandlerobjectcreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscloghandlerobjectdestroy_ PETSCLOGHANDLEROBJECTDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscloghandlerobjectdestroy_ petscloghandlerobjectdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscloghandlerstagepush_ PETSCLOGHANDLERSTAGEPUSH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscloghandlerstagepush_ petscloghandlerstagepush
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscloghandlerstagepop_ PETSCLOGHANDLERSTAGEPOP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscloghandlerstagepop_ petscloghandlerstagepop
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscloghandlerview_ PETSCLOGHANDLERVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscloghandlerview_ petscloghandlerview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscloghandlersetlogactions_ PETSCLOGHANDLERSETLOGACTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscloghandlersetlogactions_ petscloghandlersetlogactions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscloghandlersetlogobjects_ PETSCLOGHANDLERSETLOGOBJECTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscloghandlersetlogobjects_ petscloghandlersetlogobjects
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscloghandlergetnumobjects_ PETSCLOGHANDLERGETNUMOBJECTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscloghandlergetnumobjects_ petscloghandlergetnumobjects
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscloghandlereventdeactivatepush_ PETSCLOGHANDLEREVENTDEACTIVATEPUSH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscloghandlereventdeactivatepush_ petscloghandlereventdeactivatepush
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscloghandlereventdeactivatepop_ PETSCLOGHANDLEREVENTDEACTIVATEPOP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscloghandlereventdeactivatepop_ petscloghandlereventdeactivatepop
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscloghandlereventspause_ PETSCLOGHANDLEREVENTSPAUSE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscloghandlereventspause_ petscloghandlereventspause
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscloghandlereventsresume_ PETSCLOGHANDLEREVENTSRESUME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscloghandlereventsresume_ petscloghandlereventsresume
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscloghandlerdump_ PETSCLOGHANDLERDUMP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscloghandlerdump_ petscloghandlerdump
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscloghandlerstagesetvisible_ PETSCLOGHANDLERSTAGESETVISIBLE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscloghandlerstagesetvisible_ petscloghandlerstagesetvisible
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscloghandlerstagegetvisible_ PETSCLOGHANDLERSTAGEGETVISIBLE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscloghandlerstagegetvisible_ petscloghandlerstagegetvisible
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscloghandlercreate_(MPI_Fint * comm,PetscLogHandler *handler, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(handler);
 PetscBool handler_null = !*(void**) handler ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(handler);
*ierr = PetscLogHandlerCreate(
	MPI_Comm_f2c(*(comm)),handler);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! handler_null && !*(void**) handler) * (void **) handler = (void *)-2;
}
PETSC_EXTERN void  petscloghandlerdestroy_(PetscLogHandler *handler, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(handler);
 PetscBool handler_null = !*(void**) handler ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(handler);
*ierr = PetscLogHandlerDestroy(handler);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! handler_null && !*(void**) handler) * (void **) handler = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(handler);
 }
PETSC_EXTERN void  petscloghandlersetstate_(PetscLogHandler h,PetscLogState state, int *ierr)
{
CHKFORTRANNULLOBJECT(h);
CHKFORTRANNULLOBJECT(state);
*ierr = PetscLogHandlerSetState(
	(PetscLogHandler)PetscToPointer((h) ),
	(PetscLogState)PetscToPointer((state) ));
}
PETSC_EXTERN void  petscloghandlergetstate_(PetscLogHandler h,PetscLogState *state, int *ierr)
{
CHKFORTRANNULLOBJECT(h);
PetscBool state_null = !*(void**) state ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(state);
*ierr = PetscLogHandlerGetState(
	(PetscLogHandler)PetscToPointer((h) ),state);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! state_null && !*(void**) state) * (void **) state = (void *)-2;
}
PETSC_EXTERN void  petscloghandlereventbegin_(PetscLogHandler h,PetscLogEvent *e,PetscObject o1,PetscObject o2,PetscObject o3,PetscObject o4, int *ierr)
{
CHKFORTRANNULLOBJECT(h);
CHKFORTRANNULLOBJECT(o1);
CHKFORTRANNULLOBJECT(o2);
CHKFORTRANNULLOBJECT(o3);
CHKFORTRANNULLOBJECT(o4);
*ierr = PetscLogHandlerEventBegin(
	(PetscLogHandler)PetscToPointer((h) ),*e,
	(PetscObject)PetscToPointer((o1) ),
	(PetscObject)PetscToPointer((o2) ),
	(PetscObject)PetscToPointer((o3) ),
	(PetscObject)PetscToPointer((o4) ));
}
PETSC_EXTERN void  petscloghandlereventend_(PetscLogHandler h,PetscLogEvent *e,PetscObject o1,PetscObject o2,PetscObject o3,PetscObject o4, int *ierr)
{
CHKFORTRANNULLOBJECT(h);
CHKFORTRANNULLOBJECT(o1);
CHKFORTRANNULLOBJECT(o2);
CHKFORTRANNULLOBJECT(o3);
CHKFORTRANNULLOBJECT(o4);
*ierr = PetscLogHandlerEventEnd(
	(PetscLogHandler)PetscToPointer((h) ),*e,
	(PetscObject)PetscToPointer((o1) ),
	(PetscObject)PetscToPointer((o2) ),
	(PetscObject)PetscToPointer((o3) ),
	(PetscObject)PetscToPointer((o4) ));
}
PETSC_EXTERN void  petscloghandlereventsync_(PetscLogHandler h,PetscLogEvent *e,MPI_Fint * comm, int *ierr)
{
CHKFORTRANNULLOBJECT(h);
*ierr = PetscLogHandlerEventSync(
	(PetscLogHandler)PetscToPointer((h) ),*e,
	MPI_Comm_f2c(*(comm)));
}
PETSC_EXTERN void  petscloghandlerobjectcreate_(PetscLogHandler h,PetscObject obj, int *ierr)
{
CHKFORTRANNULLOBJECT(h);
CHKFORTRANNULLOBJECT(obj);
*ierr = PetscLogHandlerObjectCreate(
	(PetscLogHandler)PetscToPointer((h) ),
	(PetscObject)PetscToPointer((obj) ));
}
PETSC_EXTERN void  petscloghandlerobjectdestroy_(PetscLogHandler h,PetscObject obj, int *ierr)
{
CHKFORTRANNULLOBJECT(h);
CHKFORTRANNULLOBJECT(obj);
*ierr = PetscLogHandlerObjectDestroy(
	(PetscLogHandler)PetscToPointer((h) ),
	(PetscObject)PetscToPointer((obj) ));
}
PETSC_EXTERN void  petscloghandlerstagepush_(PetscLogHandler h,PetscLogStage *stage, int *ierr)
{
CHKFORTRANNULLOBJECT(h);
*ierr = PetscLogHandlerStagePush(
	(PetscLogHandler)PetscToPointer((h) ),*stage);
}
PETSC_EXTERN void  petscloghandlerstagepop_(PetscLogHandler h,PetscLogStage *stage, int *ierr)
{
CHKFORTRANNULLOBJECT(h);
*ierr = PetscLogHandlerStagePop(
	(PetscLogHandler)PetscToPointer((h) ),*stage);
}
PETSC_EXTERN void  petscloghandlerview_(PetscLogHandler h,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(h);
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscLogHandlerView(
	(PetscLogHandler)PetscToPointer((h) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petscloghandlersetlogactions_(PetscLogHandler handler,PetscBool *flag, int *ierr)
{
CHKFORTRANNULLOBJECT(handler);
*ierr = PetscLogHandlerSetLogActions(
	(PetscLogHandler)PetscToPointer((handler) ),*flag);
}
PETSC_EXTERN void  petscloghandlersetlogobjects_(PetscLogHandler handler,PetscBool *flag, int *ierr)
{
CHKFORTRANNULLOBJECT(handler);
*ierr = PetscLogHandlerSetLogObjects(
	(PetscLogHandler)PetscToPointer((handler) ),*flag);
}
PETSC_EXTERN void  petscloghandlergetnumobjects_(PetscLogHandler handler,PetscInt *num_objects, int *ierr)
{
CHKFORTRANNULLOBJECT(handler);
CHKFORTRANNULLINTEGER(num_objects);
*ierr = PetscLogHandlerGetNumObjects(
	(PetscLogHandler)PetscToPointer((handler) ),num_objects);
}
PETSC_EXTERN void  petscloghandlereventdeactivatepush_(PetscLogHandler handler,PetscLogStage *stage,PetscLogEvent *event, int *ierr)
{
CHKFORTRANNULLOBJECT(handler);
*ierr = PetscLogHandlerEventDeactivatePush(
	(PetscLogHandler)PetscToPointer((handler) ),*stage,*event);
}
PETSC_EXTERN void  petscloghandlereventdeactivatepop_(PetscLogHandler handler,PetscLogStage *stage,PetscLogEvent *event, int *ierr)
{
CHKFORTRANNULLOBJECT(handler);
*ierr = PetscLogHandlerEventDeactivatePop(
	(PetscLogHandler)PetscToPointer((handler) ),*stage,*event);
}
PETSC_EXTERN void  petscloghandlereventspause_(PetscLogHandler handler, int *ierr)
{
CHKFORTRANNULLOBJECT(handler);
*ierr = PetscLogHandlerEventsPause(
	(PetscLogHandler)PetscToPointer((handler) ));
}
PETSC_EXTERN void  petscloghandlereventsresume_(PetscLogHandler handler, int *ierr)
{
CHKFORTRANNULLOBJECT(handler);
*ierr = PetscLogHandlerEventsResume(
	(PetscLogHandler)PetscToPointer((handler) ));
}
PETSC_EXTERN void  petscloghandlerdump_(PetscLogHandler handler, char sname[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(handler);
/* insert Fortran-to-C conversion for sname */
  FIXCHAR(sname,cl0,_cltmp0);
*ierr = PetscLogHandlerDump(
	(PetscLogHandler)PetscToPointer((handler) ),_cltmp0);
  FREECHAR(sname,_cltmp0);
}
PETSC_EXTERN void  petscloghandlerstagesetvisible_(PetscLogHandler handler,PetscLogStage *stage,PetscBool *isVisible, int *ierr)
{
CHKFORTRANNULLOBJECT(handler);
*ierr = PetscLogHandlerStageSetVisible(
	(PetscLogHandler)PetscToPointer((handler) ),*stage,*isVisible);
}
PETSC_EXTERN void  petscloghandlerstagegetvisible_(PetscLogHandler handler,PetscLogStage *stage,PetscBool *isVisible, int *ierr)
{
CHKFORTRANNULLOBJECT(handler);
*ierr = PetscLogHandlerStageGetVisible(
	(PetscLogHandler)PetscToPointer((handler) ),*stage,isVisible);
}
#if defined(__cplusplus)
}
#endif
