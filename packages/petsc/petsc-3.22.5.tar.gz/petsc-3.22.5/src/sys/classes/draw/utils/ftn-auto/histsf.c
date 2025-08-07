#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* hists.c */
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
#include "petscsys.h"
#include "petscviewer.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawhgcreate_ PETSCDRAWHGCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawhgcreate_ petscdrawhgcreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawhgsetnumberbins_ PETSCDRAWHGSETNUMBERBINS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawhgsetnumberbins_ petscdrawhgsetnumberbins
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawhgreset_ PETSCDRAWHGRESET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawhgreset_ petscdrawhgreset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawhgdestroy_ PETSCDRAWHGDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawhgdestroy_ petscdrawhgdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawhgaddvalue_ PETSCDRAWHGADDVALUE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawhgaddvalue_ petscdrawhgaddvalue
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawhgdraw_ PETSCDRAWHGDRAW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawhgdraw_ petscdrawhgdraw
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawhgsave_ PETSCDRAWHGSAVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawhgsave_ petscdrawhgsave
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawhgview_ PETSCDRAWHGVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawhgview_ petscdrawhgview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawhgsetcolor_ PETSCDRAWHGSETCOLOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawhgsetcolor_ petscdrawhgsetcolor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawhgsetlimits_ PETSCDRAWHGSETLIMITS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawhgsetlimits_ petscdrawhgsetlimits
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawhgcalcstats_ PETSCDRAWHGCALCSTATS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawhgcalcstats_ petscdrawhgcalcstats
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawhgintegerbins_ PETSCDRAWHGINTEGERBINS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawhgintegerbins_ petscdrawhgintegerbins
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawhggetaxis_ PETSCDRAWHGGETAXIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawhggetaxis_ petscdrawhggetaxis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawhggetdraw_ PETSCDRAWHGGETDRAW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawhggetdraw_ petscdrawhggetdraw
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscdrawhgcreate_(PetscDraw draw,int *bins,PetscDrawHG *hist, int *ierr)
{
CHKFORTRANNULLOBJECT(draw);
PetscBool hist_null = !*(void**) hist ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(hist);
*ierr = PetscDrawHGCreate(
	(PetscDraw)PetscToPointer((draw) ),*bins,hist);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! hist_null && !*(void**) hist) * (void **) hist = (void *)-2;
}
PETSC_EXTERN void  petscdrawhgsetnumberbins_(PetscDrawHG hist,int *bins, int *ierr)
{
CHKFORTRANNULLOBJECT(hist);
*ierr = PetscDrawHGSetNumberBins(
	(PetscDrawHG)PetscToPointer((hist) ),*bins);
}
PETSC_EXTERN void  petscdrawhgreset_(PetscDrawHG hist, int *ierr)
{
CHKFORTRANNULLOBJECT(hist);
*ierr = PetscDrawHGReset(
	(PetscDrawHG)PetscToPointer((hist) ));
}
PETSC_EXTERN void  petscdrawhgdestroy_(PetscDrawHG *hist, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(hist);
 PetscBool hist_null = !*(void**) hist ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(hist);
*ierr = PetscDrawHGDestroy(hist);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! hist_null && !*(void**) hist) * (void **) hist = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(hist);
 }
PETSC_EXTERN void  petscdrawhgaddvalue_(PetscDrawHG hist,PetscReal *value, int *ierr)
{
CHKFORTRANNULLOBJECT(hist);
*ierr = PetscDrawHGAddValue(
	(PetscDrawHG)PetscToPointer((hist) ),*value);
}
PETSC_EXTERN void  petscdrawhgdraw_(PetscDrawHG hist, int *ierr)
{
CHKFORTRANNULLOBJECT(hist);
*ierr = PetscDrawHGDraw(
	(PetscDrawHG)PetscToPointer((hist) ));
}
PETSC_EXTERN void  petscdrawhgsave_(PetscDrawHG hg, int *ierr)
{
CHKFORTRANNULLOBJECT(hg);
*ierr = PetscDrawHGSave(
	(PetscDrawHG)PetscToPointer((hg) ));
}
PETSC_EXTERN void  petscdrawhgview_(PetscDrawHG hist,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(hist);
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscDrawHGView(
	(PetscDrawHG)PetscToPointer((hist) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petscdrawhgsetcolor_(PetscDrawHG hist,int *color, int *ierr)
{
CHKFORTRANNULLOBJECT(hist);
*ierr = PetscDrawHGSetColor(
	(PetscDrawHG)PetscToPointer((hist) ),*color);
}
PETSC_EXTERN void  petscdrawhgsetlimits_(PetscDrawHG hist,PetscReal *x_min,PetscReal *x_max,int *y_min,int *y_max, int *ierr)
{
CHKFORTRANNULLOBJECT(hist);
*ierr = PetscDrawHGSetLimits(
	(PetscDrawHG)PetscToPointer((hist) ),*x_min,*x_max,*y_min,*y_max);
}
PETSC_EXTERN void  petscdrawhgcalcstats_(PetscDrawHG hist,PetscBool *calc, int *ierr)
{
CHKFORTRANNULLOBJECT(hist);
*ierr = PetscDrawHGCalcStats(
	(PetscDrawHG)PetscToPointer((hist) ),*calc);
}
PETSC_EXTERN void  petscdrawhgintegerbins_(PetscDrawHG hist,PetscBool *ints, int *ierr)
{
CHKFORTRANNULLOBJECT(hist);
*ierr = PetscDrawHGIntegerBins(
	(PetscDrawHG)PetscToPointer((hist) ),*ints);
}
PETSC_EXTERN void  petscdrawhggetaxis_(PetscDrawHG hist,PetscDrawAxis *axis, int *ierr)
{
CHKFORTRANNULLOBJECT(hist);
PetscBool axis_null = !*(void**) axis ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(axis);
*ierr = PetscDrawHGGetAxis(
	(PetscDrawHG)PetscToPointer((hist) ),axis);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! axis_null && !*(void**) axis) * (void **) axis = (void *)-2;
}
PETSC_EXTERN void  petscdrawhggetdraw_(PetscDrawHG hist,PetscDraw *draw, int *ierr)
{
CHKFORTRANNULLOBJECT(hist);
PetscBool draw_null = !*(void**) draw ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(draw);
*ierr = PetscDrawHGGetDraw(
	(PetscDrawHG)PetscToPointer((hist) ),draw);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! draw_null && !*(void**) draw) * (void **) draw = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
