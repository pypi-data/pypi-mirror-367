#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* plog.c */
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
#define petscloggetdefaulthandler_ PETSCLOGGETDEFAULTHANDLER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscloggetdefaulthandler_ petscloggetdefaulthandler
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscloggetstate_ PETSCLOGGETSTATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscloggetstate_ petscloggetstate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscloghandlerstart_ PETSCLOGHANDLERSTART
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscloghandlerstart_ petscloghandlerstart
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscloghandlerstop_ PETSCLOGHANDLERSTOP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscloghandlerstop_ petscloghandlerstop
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogisactive_ PETSCLOGISACTIVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogisactive_ petsclogisactive
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogdefaultbegin_ PETSCLOGDEFAULTBEGIN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogdefaultbegin_ petsclogdefaultbegin
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclognestedbegin_ PETSCLOGNESTEDBEGIN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclognestedbegin_ petsclognestedbegin
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogactions_ PETSCLOGACTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogactions_ petsclogactions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogobjects_ PETSCLOGOBJECTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogobjects_ petsclogobjects
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstageregister_ PETSCLOGSTAGEREGISTER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstageregister_ petsclogstageregister
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstagepush_ PETSCLOGSTAGEPUSH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstagepush_ petsclogstagepush
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstagepop_ PETSCLOGSTAGEPOP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstagepop_ petsclogstagepop
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstagesetactive_ PETSCLOGSTAGESETACTIVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstagesetactive_ petsclogstagesetactive
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstagegetactive_ PETSCLOGSTAGEGETACTIVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstagegetactive_ petsclogstagegetactive
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstagesetvisible_ PETSCLOGSTAGESETVISIBLE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstagesetvisible_ petsclogstagesetvisible
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstagegetvisible_ PETSCLOGSTAGEGETVISIBLE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstagegetvisible_ petsclogstagegetvisible
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstagegetid_ PETSCLOGSTAGEGETID
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstagegetid_ petsclogstagegetid
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogstagegetname_ PETSCLOGSTAGEGETNAME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogstagegetname_ petsclogstagegetname
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogeventregister_ PETSCLOGEVENTREGISTER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogeventregister_ petsclogeventregister
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogeventsetcollective_ PETSCLOGEVENTSETCOLLECTIVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogeventsetcollective_ petsclogeventsetcollective
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogeventincludeclass_ PETSCLOGEVENTINCLUDECLASS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogeventincludeclass_ petsclogeventincludeclass
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogeventexcludeclass_ PETSCLOGEVENTEXCLUDECLASS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogeventexcludeclass_ petsclogeventexcludeclass
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogeventactivate_ PETSCLOGEVENTACTIVATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogeventactivate_ petsclogeventactivate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogeventdeactivate_ PETSCLOGEVENTDEACTIVATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogeventdeactivate_ petsclogeventdeactivate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogeventdeactivatepush_ PETSCLOGEVENTDEACTIVATEPUSH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogeventdeactivatepush_ petsclogeventdeactivatepush
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogeventdeactivatepop_ PETSCLOGEVENTDEACTIVATEPOP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogeventdeactivatepop_ petsclogeventdeactivatepop
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogeventsetactiveall_ PETSCLOGEVENTSETACTIVEALL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogeventsetactiveall_ petsclogeventsetactiveall
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogeventactivateclass_ PETSCLOGEVENTACTIVATECLASS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogeventactivateclass_ petsclogeventactivateclass
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogeventdeactivateclass_ PETSCLOGEVENTDEACTIVATECLASS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogeventdeactivateclass_ petsclogeventdeactivateclass
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogeventsetdof_ PETSCLOGEVENTSETDOF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogeventsetdof_ petsclogeventsetdof
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogeventseterror_ PETSCLOGEVENTSETERROR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogeventseterror_ petsclogeventseterror
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogeventgetid_ PETSCLOGEVENTGETID
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogeventgetid_ petsclogeventgetid
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogeventgetname_ PETSCLOGEVENTGETNAME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogeventgetname_ petsclogeventgetname
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogeventspause_ PETSCLOGEVENTSPAUSE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogeventspause_ petsclogeventspause
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogeventsresume_ PETSCLOGEVENTSRESUME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogeventsresume_ petsclogeventsresume
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogclassgetclassid_ PETSCLOGCLASSGETCLASSID
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogclassgetclassid_ petsclogclassgetclassid
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogdump_ PETSCLOGDUMP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogdump_ petsclogdump
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogmpedump_ PETSCLOGMPEDUMP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogmpedump_ petsclogmpedump
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogview_ PETSCLOGVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogview_ petsclogview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclogsetthreshold_ PETSCLOGSETTHRESHOLD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclogsetthreshold_ petsclogsetthreshold
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscgetflops_ PETSCGETFLOPS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscgetflops_ petscgetflops
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscloggputime_ PETSCLOGGPUTIME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscloggputime_ petscloggputime
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscloggputimebegin_ PETSCLOGGPUTIMEBEGIN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscloggputimebegin_ petscloggputimebegin
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscloggputimeend_ PETSCLOGGPUTIMEEND
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscloggputimeend_ petscloggputimeend
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscclassidregister_ PETSCCLASSIDREGISTER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscclassidregister_ petscclassidregister
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscloggetdefaulthandler_(PetscLogHandler *handler, int *ierr)
{
PetscBool handler_null = !*(void**) handler ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(handler);
*ierr = PetscLogGetDefaultHandler(handler);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! handler_null && !*(void**) handler) * (void **) handler = (void *)-2;
}
PETSC_EXTERN void  petscloggetstate_(PetscLogState *state, int *ierr)
{
PetscBool state_null = !*(void**) state ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(state);
*ierr = PetscLogGetState(state);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! state_null && !*(void**) state) * (void **) state = (void *)-2;
}
PETSC_EXTERN void  petscloghandlerstart_(PetscLogHandler h, int *ierr)
{
CHKFORTRANNULLOBJECT(h);
*ierr = PetscLogHandlerStart(
	(PetscLogHandler)PetscToPointer((h) ));
}
PETSC_EXTERN void  petscloghandlerstop_(PetscLogHandler h, int *ierr)
{
CHKFORTRANNULLOBJECT(h);
*ierr = PetscLogHandlerStop(
	(PetscLogHandler)PetscToPointer((h) ));
}
PETSC_EXTERN void  petsclogisactive_(PetscBool *isActive, int *ierr)
{
*ierr = PetscLogIsActive(isActive);
}
PETSC_EXTERN void  petsclogdefaultbegin_(int *ierr)
{
*ierr = PetscLogDefaultBegin();
}
PETSC_EXTERN void  petsclognestedbegin_(int *ierr)
{
*ierr = PetscLogNestedBegin();
}
PETSC_EXTERN void  petsclogactions_(PetscBool *flag, int *ierr)
{
*ierr = PetscLogActions(*flag);
}
PETSC_EXTERN void  petsclogobjects_(PetscBool *flag, int *ierr)
{
*ierr = PetscLogObjects(*flag);
}
PETSC_EXTERN void  petsclogstageregister_( char sname[],PetscLogStage *stage, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
/* insert Fortran-to-C conversion for sname */
  FIXCHAR(sname,cl0,_cltmp0);
*ierr = PetscLogStageRegister(_cltmp0,stage);
  FREECHAR(sname,_cltmp0);
}
PETSC_EXTERN void  petsclogstagepush_(PetscLogStage *stage, int *ierr)
{
*ierr = PetscLogStagePush(*stage);
}
PETSC_EXTERN void  petsclogstagepop_(int *ierr)
{
*ierr = PetscLogStagePop();
}
PETSC_EXTERN void  petsclogstagesetactive_(PetscLogStage *stage,PetscBool *isActive, int *ierr)
{
*ierr = PetscLogStageSetActive(*stage,*isActive);
}
PETSC_EXTERN void  petsclogstagegetactive_(PetscLogStage *stage,PetscBool *isActive, int *ierr)
{
*ierr = PetscLogStageGetActive(*stage,isActive);
}
PETSC_EXTERN void  petsclogstagesetvisible_(PetscLogStage *stage,PetscBool *isVisible, int *ierr)
{
*ierr = PetscLogStageSetVisible(*stage,*isVisible);
}
PETSC_EXTERN void  petsclogstagegetvisible_(PetscLogStage *stage,PetscBool *isVisible, int *ierr)
{
*ierr = PetscLogStageGetVisible(*stage,isVisible);
}
PETSC_EXTERN void  petsclogstagegetid_( char name[],PetscLogStage *stage, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscLogStageGetId(_cltmp0,stage);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petsclogstagegetname_(PetscLogStage *stage, char *name, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
*ierr = PetscLogStageGetName(*stage,(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for name */
*ierr = PetscStrncpy(name, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, name, cl0);
}
PETSC_EXTERN void  petsclogeventregister_( char name[],PetscClassId *classid,PetscLogEvent *event, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscLogEventRegister(_cltmp0,*classid,event);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petsclogeventsetcollective_(PetscLogEvent *event,PetscBool *collective, int *ierr)
{
*ierr = PetscLogEventSetCollective(*event,*collective);
}
PETSC_EXTERN void  petsclogeventincludeclass_(PetscClassId *classid, int *ierr)
{
*ierr = PetscLogEventIncludeClass(*classid);
}
PETSC_EXTERN void  petsclogeventexcludeclass_(PetscClassId *classid, int *ierr)
{
*ierr = PetscLogEventExcludeClass(*classid);
}
PETSC_EXTERN void  petsclogeventactivate_(PetscLogEvent *event, int *ierr)
{
*ierr = PetscLogEventActivate(*event);
}
PETSC_EXTERN void  petsclogeventdeactivate_(PetscLogEvent *event, int *ierr)
{
*ierr = PetscLogEventDeactivate(*event);
}
PETSC_EXTERN void  petsclogeventdeactivatepush_(PetscLogEvent *event, int *ierr)
{
*ierr = PetscLogEventDeactivatePush(*event);
}
PETSC_EXTERN void  petsclogeventdeactivatepop_(PetscLogEvent *event, int *ierr)
{
*ierr = PetscLogEventDeactivatePop(*event);
}
PETSC_EXTERN void  petsclogeventsetactiveall_(PetscLogEvent *event,PetscBool *isActive, int *ierr)
{
*ierr = PetscLogEventSetActiveAll(*event,*isActive);
}
PETSC_EXTERN void  petsclogeventactivateclass_(PetscClassId *classid, int *ierr)
{
*ierr = PetscLogEventActivateClass(*classid);
}
PETSC_EXTERN void  petsclogeventdeactivateclass_(PetscClassId *classid, int *ierr)
{
*ierr = PetscLogEventDeactivateClass(*classid);
}
PETSC_EXTERN void  petsclogeventsetdof_(PetscLogEvent *event,PetscInt *n,PetscLogDouble *dof, int *ierr)
{
*ierr = PetscLogEventSetDof(*event,*n,*dof);
}
PETSC_EXTERN void  petsclogeventseterror_(PetscLogEvent *event,PetscInt *n,PetscLogDouble *error, int *ierr)
{
*ierr = PetscLogEventSetError(*event,*n,*error);
}
PETSC_EXTERN void  petsclogeventgetid_( char name[],PetscLogEvent *event, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscLogEventGetId(_cltmp0,event);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petsclogeventgetname_(PetscLogEvent *event, char *name, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
*ierr = PetscLogEventGetName(*event,(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for name */
*ierr = PetscStrncpy(name, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, name, cl0);
}
PETSC_EXTERN void  petsclogeventspause_(int *ierr)
{
*ierr = PetscLogEventsPause();
}
PETSC_EXTERN void  petsclogeventsresume_(int *ierr)
{
*ierr = PetscLogEventsResume();
}
PETSC_EXTERN void  petsclogclassgetclassid_( char name[],PetscClassId *classid, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscLogClassGetClassId(_cltmp0,classid);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petsclogdump_( char sname[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
/* insert Fortran-to-C conversion for sname */
  FIXCHAR(sname,cl0,_cltmp0);
*ierr = PetscLogDump(_cltmp0);
  FREECHAR(sname,_cltmp0);
}
PETSC_EXTERN void  petsclogmpedump_( char sname[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
/* insert Fortran-to-C conversion for sname */
  FIXCHAR(sname,cl0,_cltmp0);
*ierr = PetscLogMPEDump(_cltmp0);
  FREECHAR(sname,_cltmp0);
}
PETSC_EXTERN void  petsclogview_(PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscLogView(PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petsclogsetthreshold_(PetscLogDouble *newThresh,PetscLogDouble *oldThresh, int *ierr)
{
*ierr = PetscLogSetThreshold(*newThresh,oldThresh);
}
PETSC_EXTERN void  petscgetflops_(PetscLogDouble *flops, int *ierr)
{
*ierr = PetscGetFlops(flops);
}
PETSC_EXTERN void  petscloggputime_(int *ierr)
{
*ierr = PetscLogGpuTime();
}
PETSC_EXTERN void  petscloggputimebegin_(int *ierr)
{
*ierr = PetscLogGpuTimeBegin();
}
PETSC_EXTERN void  petscloggputimeend_(int *ierr)
{
*ierr = PetscLogGpuTimeEnd();
}
PETSC_EXTERN void  petscclassidregister_( char name[],PetscClassId *oclass, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscClassIdRegister(_cltmp0,oclass);
  FREECHAR(name,_cltmp0);
}
#if defined(__cplusplus)
}
#endif
