#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* dtext.c */
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
#define petscdrawstring_ PETSCDRAWSTRING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawstring_ petscdrawstring
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawstringvertical_ PETSCDRAWSTRINGVERTICAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawstringvertical_ petscdrawstringvertical
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawstringcentered_ PETSCDRAWSTRINGCENTERED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawstringcentered_ petscdrawstringcentered
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawstringboxed_ PETSCDRAWSTRINGBOXED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawstringboxed_ petscdrawstringboxed
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawstringsetsize_ PETSCDRAWSTRINGSETSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawstringsetsize_ petscdrawstringsetsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawstringgetsize_ PETSCDRAWSTRINGGETSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawstringgetsize_ petscdrawstringgetsize
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscdrawstring_(PetscDraw draw,PetscReal *xl,PetscReal *yl,int *cl, char text[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(draw);
/* insert Fortran-to-C conversion for text */
  FIXCHAR(text,cl0,_cltmp0);
*ierr = PetscDrawString(
	(PetscDraw)PetscToPointer((draw) ),*xl,*yl,*cl,_cltmp0);
  FREECHAR(text,_cltmp0);
}
PETSC_EXTERN void  petscdrawstringvertical_(PetscDraw draw,PetscReal *xl,PetscReal *yl,int *cl, char text[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(draw);
/* insert Fortran-to-C conversion for text */
  FIXCHAR(text,cl0,_cltmp0);
*ierr = PetscDrawStringVertical(
	(PetscDraw)PetscToPointer((draw) ),*xl,*yl,*cl,_cltmp0);
  FREECHAR(text,_cltmp0);
}
PETSC_EXTERN void  petscdrawstringcentered_(PetscDraw draw,PetscReal *xc,PetscReal *yl,int *cl, char text[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(draw);
/* insert Fortran-to-C conversion for text */
  FIXCHAR(text,cl0,_cltmp0);
*ierr = PetscDrawStringCentered(
	(PetscDraw)PetscToPointer((draw) ),*xc,*yl,*cl,_cltmp0);
  FREECHAR(text,_cltmp0);
}
PETSC_EXTERN void  petscdrawstringboxed_(PetscDraw draw,PetscReal *sxl,PetscReal *syl,int *sc,int *bc, char text[],PetscReal *w,PetscReal *h, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(draw);
CHKFORTRANNULLREAL(w);
CHKFORTRANNULLREAL(h);
/* insert Fortran-to-C conversion for text */
  FIXCHAR(text,cl0,_cltmp0);
*ierr = PetscDrawStringBoxed(
	(PetscDraw)PetscToPointer((draw) ),*sxl,*syl,*sc,*bc,_cltmp0,w,h);
  FREECHAR(text,_cltmp0);
}
PETSC_EXTERN void  petscdrawstringsetsize_(PetscDraw draw,PetscReal *width,PetscReal *height, int *ierr)
{
CHKFORTRANNULLOBJECT(draw);
*ierr = PetscDrawStringSetSize(
	(PetscDraw)PetscToPointer((draw) ),*width,*height);
}
PETSC_EXTERN void  petscdrawstringgetsize_(PetscDraw draw,PetscReal *width,PetscReal *height, int *ierr)
{
CHKFORTRANNULLOBJECT(draw);
CHKFORTRANNULLREAL(width);
CHKFORTRANNULLREAL(height);
*ierr = PetscDrawStringGetSize(
	(PetscDraw)PetscToPointer((draw) ),width,height);
}
#if defined(__cplusplus)
}
#endif
