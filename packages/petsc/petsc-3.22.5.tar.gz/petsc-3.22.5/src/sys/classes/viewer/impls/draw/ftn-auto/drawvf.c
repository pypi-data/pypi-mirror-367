#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* drawv.c */
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

#include "petscdraw.h"
#include "petscviewer.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerdrawgetdraw_ PETSCVIEWERDRAWGETDRAW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerdrawgetdraw_ petscviewerdrawgetdraw
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerdrawbaseadd_ PETSCVIEWERDRAWBASEADD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerdrawbaseadd_ petscviewerdrawbaseadd
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerdrawbaseset_ PETSCVIEWERDRAWBASESET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerdrawbaseset_ petscviewerdrawbaseset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerdrawgetdrawlg_ PETSCVIEWERDRAWGETDRAWLG
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerdrawgetdrawlg_ petscviewerdrawgetdrawlg
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerdrawgetdrawaxis_ PETSCVIEWERDRAWGETDRAWAXIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerdrawgetdrawaxis_ petscviewerdrawgetdrawaxis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerdrawopen_ PETSCVIEWERDRAWOPEN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerdrawopen_ petscviewerdrawopen
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerdrawclear_ PETSCVIEWERDRAWCLEAR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerdrawclear_ petscviewerdrawclear
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerdrawgetpause_ PETSCVIEWERDRAWGETPAUSE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerdrawgetpause_ petscviewerdrawgetpause
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerdrawsetpause_ PETSCVIEWERDRAWSETPAUSE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerdrawsetpause_ petscviewerdrawsetpause
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerdrawsethold_ PETSCVIEWERDRAWSETHOLD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerdrawsethold_ petscviewerdrawsethold
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerdrawgethold_ PETSCVIEWERDRAWGETHOLD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerdrawgethold_ petscviewerdrawgethold
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerdrawsetbounds_ PETSCVIEWERDRAWSETBOUNDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerdrawsetbounds_ petscviewerdrawsetbounds
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscviewerdrawgetdraw_(PetscViewer viewer,PetscInt *windownumber,PetscDraw *draw, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
PetscBool draw_null = !*(void**) draw ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(draw);
*ierr = PetscViewerDrawGetDraw(PetscPatchDefaultViewers((PetscViewer*)viewer),*windownumber,draw);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! draw_null && !*(void**) draw) * (void **) draw = (void *)-2;
}
PETSC_EXTERN void  petscviewerdrawbaseadd_(PetscViewer viewer,PetscInt *windownumber, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerDrawBaseAdd(PetscPatchDefaultViewers((PetscViewer*)viewer),*windownumber);
}
PETSC_EXTERN void  petscviewerdrawbaseset_(PetscViewer viewer,PetscInt *windownumber, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerDrawBaseSet(PetscPatchDefaultViewers((PetscViewer*)viewer),*windownumber);
}
PETSC_EXTERN void  petscviewerdrawgetdrawlg_(PetscViewer viewer,PetscInt *windownumber,PetscDrawLG *drawlg, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
PetscBool drawlg_null = !*(void**) drawlg ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(drawlg);
*ierr = PetscViewerDrawGetDrawLG(PetscPatchDefaultViewers((PetscViewer*)viewer),*windownumber,drawlg);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! drawlg_null && !*(void**) drawlg) * (void **) drawlg = (void *)-2;
}
PETSC_EXTERN void  petscviewerdrawgetdrawaxis_(PetscViewer viewer,PetscInt *windownumber,PetscDrawAxis *drawaxis, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
PetscBool drawaxis_null = !*(void**) drawaxis ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(drawaxis);
*ierr = PetscViewerDrawGetDrawAxis(PetscPatchDefaultViewers((PetscViewer*)viewer),*windownumber,drawaxis);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! drawaxis_null && !*(void**) drawaxis) * (void **) drawaxis = (void *)-2;
}
PETSC_EXTERN void  petscviewerdrawopen_(MPI_Fint * comm, char display[], char title[],int *x,int *y,int *w,int *h,PetscViewer *viewer, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0, PETSC_FORTRAN_CHARLEN_T cl1)
{
  char *_cltmp0 = PETSC_NULLPTR;
  char *_cltmp1 = PETSC_NULLPTR;
PetscBool viewer_null = !*(void**) viewer ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(viewer);
/* insert Fortran-to-C conversion for display */
  FIXCHAR(display,cl0,_cltmp0);
/* insert Fortran-to-C conversion for title */
  FIXCHAR(title,cl1,_cltmp1);
*ierr = PetscViewerDrawOpen(
	MPI_Comm_f2c(*(comm)),_cltmp0,_cltmp1,*x,*y,*w,*h,viewer);
  FREECHAR(display,_cltmp0);
  FREECHAR(title,_cltmp1);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! viewer_null && !*(void**) viewer) * (void **) viewer = (void *)-2;
}
PETSC_EXTERN void  petscviewerdrawclear_(PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerDrawClear(PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petscviewerdrawgetpause_(PetscViewer viewer,PetscReal *pause, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
CHKFORTRANNULLREAL(pause);
*ierr = PetscViewerDrawGetPause(PetscPatchDefaultViewers((PetscViewer*)viewer),pause);
}
PETSC_EXTERN void  petscviewerdrawsetpause_(PetscViewer viewer,PetscReal *pause, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerDrawSetPause(PetscPatchDefaultViewers((PetscViewer*)viewer),*pause);
}
PETSC_EXTERN void  petscviewerdrawsethold_(PetscViewer viewer,PetscBool *hold, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerDrawSetHold(PetscPatchDefaultViewers((PetscViewer*)viewer),*hold);
}
PETSC_EXTERN void  petscviewerdrawgethold_(PetscViewer viewer,PetscBool *hold, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerDrawGetHold(PetscPatchDefaultViewers((PetscViewer*)viewer),hold);
}
PETSC_EXTERN void  petscviewerdrawsetbounds_(PetscViewer viewer,PetscInt *nbounds, PetscReal *bounds, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
CHKFORTRANNULLREAL(bounds);
*ierr = PetscViewerDrawSetBounds(PetscPatchDefaultViewers((PetscViewer*)viewer),*nbounds,bounds);
}
#if defined(__cplusplus)
}
#endif
