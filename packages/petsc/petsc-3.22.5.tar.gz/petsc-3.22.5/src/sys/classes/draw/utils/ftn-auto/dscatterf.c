#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* dscatter.c */
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
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawspcreate_ PETSCDRAWSPCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawspcreate_ petscdrawspcreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawspsetdimension_ PETSCDRAWSPSETDIMENSION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawspsetdimension_ petscdrawspsetdimension
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawspgetdimension_ PETSCDRAWSPGETDIMENSION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawspgetdimension_ petscdrawspgetdimension
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawspreset_ PETSCDRAWSPRESET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawspreset_ petscdrawspreset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawspdestroy_ PETSCDRAWSPDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawspdestroy_ petscdrawspdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawspaddpoint_ PETSCDRAWSPADDPOINT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawspaddpoint_ petscdrawspaddpoint
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawspaddpointcolorized_ PETSCDRAWSPADDPOINTCOLORIZED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawspaddpointcolorized_ petscdrawspaddpointcolorized
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawspdraw_ PETSCDRAWSPDRAW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawspdraw_ petscdrawspdraw
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawspsave_ PETSCDRAWSPSAVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawspsave_ petscdrawspsave
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawspsetlimits_ PETSCDRAWSPSETLIMITS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawspsetlimits_ petscdrawspsetlimits
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawspgetaxis_ PETSCDRAWSPGETAXIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawspgetaxis_ petscdrawspgetaxis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawspgetdraw_ PETSCDRAWSPGETDRAW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawspgetdraw_ petscdrawspgetdraw
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscdrawspcreate_(PetscDraw draw,int *dim,PetscDrawSP *drawsp, int *ierr)
{
CHKFORTRANNULLOBJECT(draw);
PetscBool drawsp_null = !*(void**) drawsp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(drawsp);
*ierr = PetscDrawSPCreate(
	(PetscDraw)PetscToPointer((draw) ),*dim,drawsp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! drawsp_null && !*(void**) drawsp) * (void **) drawsp = (void *)-2;
}
PETSC_EXTERN void  petscdrawspsetdimension_(PetscDrawSP sp,int *dim, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
*ierr = PetscDrawSPSetDimension(
	(PetscDrawSP)PetscToPointer((sp) ),*dim);
}
PETSC_EXTERN void  petscdrawspgetdimension_(PetscDrawSP sp,int *dim, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
*ierr = PetscDrawSPGetDimension(
	(PetscDrawSP)PetscToPointer((sp) ),dim);
}
PETSC_EXTERN void  petscdrawspreset_(PetscDrawSP sp, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
*ierr = PetscDrawSPReset(
	(PetscDrawSP)PetscToPointer((sp) ));
}
PETSC_EXTERN void  petscdrawspdestroy_(PetscDrawSP *sp, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(sp);
 PetscBool sp_null = !*(void**) sp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sp);
*ierr = PetscDrawSPDestroy(sp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sp_null && !*(void**) sp) * (void **) sp = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(sp);
 }
PETSC_EXTERN void  petscdrawspaddpoint_(PetscDrawSP sp,PetscReal *x,PetscReal *y, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
CHKFORTRANNULLREAL(x);
CHKFORTRANNULLREAL(y);
*ierr = PetscDrawSPAddPoint(
	(PetscDrawSP)PetscToPointer((sp) ),x,y);
}
PETSC_EXTERN void  petscdrawspaddpointcolorized_(PetscDrawSP sp,PetscReal *x,PetscReal *y,PetscReal *z, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
CHKFORTRANNULLREAL(x);
CHKFORTRANNULLREAL(y);
CHKFORTRANNULLREAL(z);
*ierr = PetscDrawSPAddPointColorized(
	(PetscDrawSP)PetscToPointer((sp) ),x,y,z);
}
PETSC_EXTERN void  petscdrawspdraw_(PetscDrawSP sp,PetscBool *clear, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
*ierr = PetscDrawSPDraw(
	(PetscDrawSP)PetscToPointer((sp) ),*clear);
}
PETSC_EXTERN void  petscdrawspsave_(PetscDrawSP sp, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
*ierr = PetscDrawSPSave(
	(PetscDrawSP)PetscToPointer((sp) ));
}
PETSC_EXTERN void  petscdrawspsetlimits_(PetscDrawSP sp,PetscReal *x_min,PetscReal *x_max,PetscReal *y_min,PetscReal *y_max, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
*ierr = PetscDrawSPSetLimits(
	(PetscDrawSP)PetscToPointer((sp) ),*x_min,*x_max,*y_min,*y_max);
}
PETSC_EXTERN void  petscdrawspgetaxis_(PetscDrawSP sp,PetscDrawAxis *axis, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
PetscBool axis_null = !*(void**) axis ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(axis);
*ierr = PetscDrawSPGetAxis(
	(PetscDrawSP)PetscToPointer((sp) ),axis);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! axis_null && !*(void**) axis) * (void **) axis = (void *)-2;
}
PETSC_EXTERN void  petscdrawspgetdraw_(PetscDrawSP sp,PetscDraw *draw, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
PetscBool draw_null = !*(void**) draw ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(draw);
*ierr = PetscDrawSPGetDraw(
	(PetscDrawSP)PetscToPointer((sp) ),draw);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! draw_null && !*(void**) draw) * (void **) draw = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
