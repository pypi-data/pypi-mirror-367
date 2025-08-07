#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* draw.c */
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
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawresizewindow_ PETSCDRAWRESIZEWINDOW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawresizewindow_ petscdrawresizewindow
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawgetwindowsize_ PETSCDRAWGETWINDOWSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawgetwindowsize_ petscdrawgetwindowsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawcheckresizedwindow_ PETSCDRAWCHECKRESIZEDWINDOW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawcheckresizedwindow_ petscdrawcheckresizedwindow
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawgettitle_ PETSCDRAWGETTITLE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawgettitle_ petscdrawgettitle
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawsettitle_ PETSCDRAWSETTITLE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawsettitle_ petscdrawsettitle
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawappendtitle_ PETSCDRAWAPPENDTITLE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawappendtitle_ petscdrawappendtitle
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawdestroy_ PETSCDRAWDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawdestroy_ petscdrawdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawgetpopup_ PETSCDRAWGETPOPUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawgetpopup_ petscdrawgetpopup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawsetdisplay_ PETSCDRAWSETDISPLAY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawsetdisplay_ petscdrawsetdisplay
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawsetdoublebuffer_ PETSCDRAWSETDOUBLEBUFFER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawsetdoublebuffer_ petscdrawsetdoublebuffer
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawgetsingleton_ PETSCDRAWGETSINGLETON
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawgetsingleton_ petscdrawgetsingleton
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawrestoresingleton_ PETSCDRAWRESTORESINGLETON
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawrestoresingleton_ petscdrawrestoresingleton
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawsetvisible_ PETSCDRAWSETVISIBLE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawsetvisible_ petscdrawsetvisible
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscdrawresizewindow_(PetscDraw draw,int *w,int *h, int *ierr)
{
CHKFORTRANNULLOBJECT(draw);
*ierr = PetscDrawResizeWindow(
	(PetscDraw)PetscToPointer((draw) ),*w,*h);
}
PETSC_EXTERN void  petscdrawgetwindowsize_(PetscDraw draw,int *w,int *h, int *ierr)
{
CHKFORTRANNULLOBJECT(draw);
*ierr = PetscDrawGetWindowSize(
	(PetscDraw)PetscToPointer((draw) ),w,h);
}
PETSC_EXTERN void  petscdrawcheckresizedwindow_(PetscDraw draw, int *ierr)
{
CHKFORTRANNULLOBJECT(draw);
*ierr = PetscDrawCheckResizedWindow(
	(PetscDraw)PetscToPointer((draw) ));
}
PETSC_EXTERN void  petscdrawgettitle_(PetscDraw draw, char *title, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(draw);
*ierr = PetscDrawGetTitle(
	(PetscDraw)PetscToPointer((draw) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for title */
*ierr = PetscStrncpy(title, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, title, cl0);
}
PETSC_EXTERN void  petscdrawsettitle_(PetscDraw draw, char title[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(draw);
/* insert Fortran-to-C conversion for title */
  FIXCHAR(title,cl0,_cltmp0);
*ierr = PetscDrawSetTitle(
	(PetscDraw)PetscToPointer((draw) ),_cltmp0);
  FREECHAR(title,_cltmp0);
}
PETSC_EXTERN void  petscdrawappendtitle_(PetscDraw draw, char title[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(draw);
/* insert Fortran-to-C conversion for title */
  FIXCHAR(title,cl0,_cltmp0);
*ierr = PetscDrawAppendTitle(
	(PetscDraw)PetscToPointer((draw) ),_cltmp0);
  FREECHAR(title,_cltmp0);
}
PETSC_EXTERN void  petscdrawdestroy_(PetscDraw *draw, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(draw);
 PetscBool draw_null = !*(void**) draw ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(draw);
*ierr = PetscDrawDestroy(draw);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! draw_null && !*(void**) draw) * (void **) draw = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(draw);
 }
PETSC_EXTERN void  petscdrawgetpopup_(PetscDraw draw,PetscDraw *popup, int *ierr)
{
CHKFORTRANNULLOBJECT(draw);
PetscBool popup_null = !*(void**) popup ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(popup);
*ierr = PetscDrawGetPopup(
	(PetscDraw)PetscToPointer((draw) ),popup);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! popup_null && !*(void**) popup) * (void **) popup = (void *)-2;
}
PETSC_EXTERN void  petscdrawsetdisplay_(PetscDraw draw, char display[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(draw);
/* insert Fortran-to-C conversion for display */
  FIXCHAR(display,cl0,_cltmp0);
*ierr = PetscDrawSetDisplay(
	(PetscDraw)PetscToPointer((draw) ),_cltmp0);
  FREECHAR(display,_cltmp0);
}
PETSC_EXTERN void  petscdrawsetdoublebuffer_(PetscDraw draw, int *ierr)
{
CHKFORTRANNULLOBJECT(draw);
*ierr = PetscDrawSetDoubleBuffer(
	(PetscDraw)PetscToPointer((draw) ));
}
PETSC_EXTERN void  petscdrawgetsingleton_(PetscDraw draw,PetscDraw *sdraw, int *ierr)
{
CHKFORTRANNULLOBJECT(draw);
PetscBool sdraw_null = !*(void**) sdraw ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sdraw);
*ierr = PetscDrawGetSingleton(
	(PetscDraw)PetscToPointer((draw) ),sdraw);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sdraw_null && !*(void**) sdraw) * (void **) sdraw = (void *)-2;
}
PETSC_EXTERN void  petscdrawrestoresingleton_(PetscDraw draw,PetscDraw *sdraw, int *ierr)
{
CHKFORTRANNULLOBJECT(draw);
PetscBool sdraw_null = !*(void**) sdraw ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sdraw);
*ierr = PetscDrawRestoreSingleton(
	(PetscDraw)PetscToPointer((draw) ),sdraw);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sdraw_null && !*(void**) sdraw) * (void **) sdraw = (void *)-2;
}
PETSC_EXTERN void  petscdrawsetvisible_(PetscDraw draw,PetscBool *visible, int *ierr)
{
CHKFORTRANNULLOBJECT(draw);
*ierr = PetscDrawSetVisible(
	(PetscDraw)PetscToPointer((draw) ),*visible);
}
#if defined(__cplusplus)
}
#endif
