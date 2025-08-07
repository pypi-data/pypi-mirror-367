#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* drect.c */
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
#define petscdrawcoordinatetopixel_ PETSCDRAWCOORDINATETOPIXEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawcoordinatetopixel_ petscdrawcoordinatetopixel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawpixeltocoordinate_ PETSCDRAWPIXELTOCOORDINATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawpixeltocoordinate_ petscdrawpixeltocoordinate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawrectangle_ PETSCDRAWRECTANGLE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawrectangle_ petscdrawrectangle
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscdrawcoordinatetopixel_(PetscDraw draw,PetscReal *x,PetscReal *y,int *i,int *j, int *ierr)
{
CHKFORTRANNULLOBJECT(draw);
*ierr = PetscDrawCoordinateToPixel(
	(PetscDraw)PetscToPointer((draw) ),*x,*y,i,j);
}
PETSC_EXTERN void  petscdrawpixeltocoordinate_(PetscDraw draw,int *i,int *j,PetscReal *x,PetscReal *y, int *ierr)
{
CHKFORTRANNULLOBJECT(draw);
CHKFORTRANNULLREAL(x);
CHKFORTRANNULLREAL(y);
*ierr = PetscDrawPixelToCoordinate(
	(PetscDraw)PetscToPointer((draw) ),*i,*j,x,y);
}
PETSC_EXTERN void  petscdrawrectangle_(PetscDraw draw,PetscReal *xl,PetscReal *yl,PetscReal *xr,PetscReal *yr,int *c1,int *c2,int *c3,int *c4, int *ierr)
{
CHKFORTRANNULLOBJECT(draw);
*ierr = PetscDrawRectangle(
	(PetscDraw)PetscToPointer((draw) ),*xl,*yl,*xr,*yr,*c1,*c2,*c3,*c4);
}
#if defined(__cplusplus)
}
#endif
