#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* bars.c */
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
#define petscdrawbarcreate_ PETSCDRAWBARCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawbarcreate_ petscdrawbarcreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawbardestroy_ PETSCDRAWBARDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawbardestroy_ petscdrawbardestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawbardraw_ PETSCDRAWBARDRAW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawbardraw_ petscdrawbardraw
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawbarsave_ PETSCDRAWBARSAVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawbarsave_ petscdrawbarsave
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawbarsetcolor_ PETSCDRAWBARSETCOLOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawbarsetcolor_ petscdrawbarsetcolor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawbarsort_ PETSCDRAWBARSORT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawbarsort_ petscdrawbarsort
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawbarsetlimits_ PETSCDRAWBARSETLIMITS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawbarsetlimits_ petscdrawbarsetlimits
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawbargetaxis_ PETSCDRAWBARGETAXIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawbargetaxis_ petscdrawbargetaxis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawbargetdraw_ PETSCDRAWBARGETDRAW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawbargetdraw_ petscdrawbargetdraw
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawbarsetfromoptions_ PETSCDRAWBARSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawbarsetfromoptions_ petscdrawbarsetfromoptions
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscdrawbarcreate_(PetscDraw draw,PetscDrawBar *bar, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(bar);
 CHKFORTRANNULLOBJECT(draw);
PetscBool bar_null = !*(void**) bar ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(bar);
*ierr = PetscDrawBarCreate(
	(PetscDraw)PetscToPointer((draw) ),bar);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! bar_null && !*(void**) bar) * (void **) bar = (void *)-2;
}
PETSC_EXTERN void  petscdrawbardestroy_(PetscDrawBar *bar, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(bar);
 PetscBool bar_null = !*(void**) bar ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(bar);
*ierr = PetscDrawBarDestroy(bar);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! bar_null && !*(void**) bar) * (void **) bar = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(bar);
 }
PETSC_EXTERN void  petscdrawbardraw_(PetscDrawBar bar, int *ierr)
{
CHKFORTRANNULLOBJECT(bar);
*ierr = PetscDrawBarDraw(
	(PetscDrawBar)PetscToPointer((bar) ));
}
PETSC_EXTERN void  petscdrawbarsave_(PetscDrawBar bar, int *ierr)
{
CHKFORTRANNULLOBJECT(bar);
*ierr = PetscDrawBarSave(
	(PetscDrawBar)PetscToPointer((bar) ));
}
PETSC_EXTERN void  petscdrawbarsetcolor_(PetscDrawBar bar,int *color, int *ierr)
{
CHKFORTRANNULLOBJECT(bar);
*ierr = PetscDrawBarSetColor(
	(PetscDrawBar)PetscToPointer((bar) ),*color);
}
PETSC_EXTERN void  petscdrawbarsort_(PetscDrawBar bar,PetscBool *sort,PetscReal *tolerance, int *ierr)
{
CHKFORTRANNULLOBJECT(bar);
*ierr = PetscDrawBarSort(
	(PetscDrawBar)PetscToPointer((bar) ),*sort,*tolerance);
}
PETSC_EXTERN void  petscdrawbarsetlimits_(PetscDrawBar bar,PetscReal *y_min,PetscReal *y_max, int *ierr)
{
CHKFORTRANNULLOBJECT(bar);
*ierr = PetscDrawBarSetLimits(
	(PetscDrawBar)PetscToPointer((bar) ),*y_min,*y_max);
}
PETSC_EXTERN void  petscdrawbargetaxis_(PetscDrawBar bar,PetscDrawAxis *axis, int *ierr)
{
CHKFORTRANNULLOBJECT(bar);
PetscBool axis_null = !*(void**) axis ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(axis);
*ierr = PetscDrawBarGetAxis(
	(PetscDrawBar)PetscToPointer((bar) ),axis);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! axis_null && !*(void**) axis) * (void **) axis = (void *)-2;
}
PETSC_EXTERN void  petscdrawbargetdraw_(PetscDrawBar bar,PetscDraw *draw, int *ierr)
{
CHKFORTRANNULLOBJECT(bar);
PetscBool draw_null = !*(void**) draw ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(draw);
*ierr = PetscDrawBarGetDraw(
	(PetscDrawBar)PetscToPointer((bar) ),draw);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! draw_null && !*(void**) draw) * (void **) draw = (void *)-2;
}
PETSC_EXTERN void  petscdrawbarsetfromoptions_(PetscDrawBar bar, int *ierr)
{
CHKFORTRANNULLOBJECT(bar);
*ierr = PetscDrawBarSetFromOptions(
	(PetscDrawBar)PetscToPointer((bar) ));
}
#if defined(__cplusplus)
}
#endif
