#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* axisc.c */
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
#define petscdrawaxiscreate_ PETSCDRAWAXISCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawaxiscreate_ petscdrawaxiscreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawaxisdestroy_ PETSCDRAWAXISDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawaxisdestroy_ petscdrawaxisdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawaxissetcolors_ PETSCDRAWAXISSETCOLORS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawaxissetcolors_ petscdrawaxissetcolors
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawaxissetlabels_ PETSCDRAWAXISSETLABELS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawaxissetlabels_ petscdrawaxissetlabels
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawaxissetlimits_ PETSCDRAWAXISSETLIMITS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawaxissetlimits_ petscdrawaxissetlimits
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawaxisgetlimits_ PETSCDRAWAXISGETLIMITS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawaxisgetlimits_ petscdrawaxisgetlimits
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawaxissetholdlimits_ PETSCDRAWAXISSETHOLDLIMITS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawaxissetholdlimits_ petscdrawaxissetholdlimits
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawaxisdraw_ PETSCDRAWAXISDRAW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawaxisdraw_ petscdrawaxisdraw
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscdrawaxiscreate_(PetscDraw draw,PetscDrawAxis *axis, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(axis);
 CHKFORTRANNULLOBJECT(draw);
PetscBool axis_null = !*(void**) axis ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(axis);
*ierr = PetscDrawAxisCreate(
	(PetscDraw)PetscToPointer((draw) ),axis);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! axis_null && !*(void**) axis) * (void **) axis = (void *)-2;
}
PETSC_EXTERN void  petscdrawaxisdestroy_(PetscDrawAxis *axis, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(axis);
 PetscBool axis_null = !*(void**) axis ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(axis);
*ierr = PetscDrawAxisDestroy(axis);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! axis_null && !*(void**) axis) * (void **) axis = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(axis);
 }
PETSC_EXTERN void  petscdrawaxissetcolors_(PetscDrawAxis axis,int *ac,int *tc,int *cc, int *ierr)
{
CHKFORTRANNULLOBJECT(axis);
*ierr = PetscDrawAxisSetColors(
	(PetscDrawAxis)PetscToPointer((axis) ),*ac,*tc,*cc);
}
PETSC_EXTERN void  petscdrawaxissetlabels_(PetscDrawAxis axis, char top[], char xlabel[], char ylabel[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0, PETSC_FORTRAN_CHARLEN_T cl1, PETSC_FORTRAN_CHARLEN_T cl2)
{
  char *_cltmp0 = PETSC_NULLPTR;
  char *_cltmp1 = PETSC_NULLPTR;
  char *_cltmp2 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(axis);
/* insert Fortran-to-C conversion for top */
  FIXCHAR(top,cl0,_cltmp0);
/* insert Fortran-to-C conversion for xlabel */
  FIXCHAR(xlabel,cl1,_cltmp1);
/* insert Fortran-to-C conversion for ylabel */
  FIXCHAR(ylabel,cl2,_cltmp2);
*ierr = PetscDrawAxisSetLabels(
	(PetscDrawAxis)PetscToPointer((axis) ),_cltmp0,_cltmp1,_cltmp2);
  FREECHAR(top,_cltmp0);
  FREECHAR(xlabel,_cltmp1);
  FREECHAR(ylabel,_cltmp2);
}
PETSC_EXTERN void  petscdrawaxissetlimits_(PetscDrawAxis axis,PetscReal *xmin,PetscReal *xmax,PetscReal *ymin,PetscReal *ymax, int *ierr)
{
CHKFORTRANNULLOBJECT(axis);
*ierr = PetscDrawAxisSetLimits(
	(PetscDrawAxis)PetscToPointer((axis) ),*xmin,*xmax,*ymin,*ymax);
}
PETSC_EXTERN void  petscdrawaxisgetlimits_(PetscDrawAxis axis,PetscReal *xmin,PetscReal *xmax,PetscReal *ymin,PetscReal *ymax, int *ierr)
{
CHKFORTRANNULLOBJECT(axis);
CHKFORTRANNULLREAL(xmin);
CHKFORTRANNULLREAL(xmax);
CHKFORTRANNULLREAL(ymin);
CHKFORTRANNULLREAL(ymax);
*ierr = PetscDrawAxisGetLimits(
	(PetscDrawAxis)PetscToPointer((axis) ),xmin,xmax,ymin,ymax);
}
PETSC_EXTERN void  petscdrawaxissetholdlimits_(PetscDrawAxis axis,PetscBool *hold, int *ierr)
{
CHKFORTRANNULLOBJECT(axis);
*ierr = PetscDrawAxisSetHoldLimits(
	(PetscDrawAxis)PetscToPointer((axis) ),*hold);
}
PETSC_EXTERN void  petscdrawaxisdraw_(PetscDrawAxis axis, int *ierr)
{
CHKFORTRANNULLOBJECT(axis);
*ierr = PetscDrawAxisDraw(
	(PetscDrawAxis)PetscToPointer((axis) ));
}
#if defined(__cplusplus)
}
#endif
