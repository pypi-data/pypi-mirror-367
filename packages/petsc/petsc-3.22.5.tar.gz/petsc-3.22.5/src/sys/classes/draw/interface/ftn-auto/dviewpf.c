#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* dviewp.c */
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
#define petscdrawsetviewport_ PETSCDRAWSETVIEWPORT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawsetviewport_ petscdrawsetviewport
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawgetviewport_ PETSCDRAWGETVIEWPORT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawgetviewport_ petscdrawgetviewport
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawsplitviewport_ PETSCDRAWSPLITVIEWPORT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawsplitviewport_ petscdrawsplitviewport
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscdrawsetviewport_(PetscDraw draw,PetscReal *xl,PetscReal *yl,PetscReal *xr,PetscReal *yr, int *ierr)
{
CHKFORTRANNULLOBJECT(draw);
*ierr = PetscDrawSetViewPort(
	(PetscDraw)PetscToPointer((draw) ),*xl,*yl,*xr,*yr);
}
PETSC_EXTERN void  petscdrawgetviewport_(PetscDraw draw,PetscReal *xl,PetscReal *yl,PetscReal *xr,PetscReal *yr, int *ierr)
{
CHKFORTRANNULLOBJECT(draw);
CHKFORTRANNULLREAL(xl);
CHKFORTRANNULLREAL(yl);
CHKFORTRANNULLREAL(xr);
CHKFORTRANNULLREAL(yr);
*ierr = PetscDrawGetViewPort(
	(PetscDraw)PetscToPointer((draw) ),xl,yl,xr,yr);
}
PETSC_EXTERN void  petscdrawsplitviewport_(PetscDraw draw, int *ierr)
{
CHKFORTRANNULLOBJECT(draw);
*ierr = PetscDrawSplitViewPort(
	(PetscDraw)PetscToPointer((draw) ));
}
#if defined(__cplusplus)
}
#endif
