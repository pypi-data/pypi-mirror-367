#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* dsave.c */
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
#define petscdrawsetsave_ PETSCDRAWSETSAVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawsetsave_ petscdrawsetsave
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawsetsavemovie_ PETSCDRAWSETSAVEMOVIE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawsetsavemovie_ petscdrawsetsavemovie
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawsetsavefinalimage_ PETSCDRAWSETSAVEFINALIMAGE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawsetsavefinalimage_ petscdrawsetsavefinalimage
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawsave_ PETSCDRAWSAVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawsave_ petscdrawsave
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawsavemovie_ PETSCDRAWSAVEMOVIE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawsavemovie_ petscdrawsavemovie
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscdrawsetsave_(PetscDraw draw, char filename[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(draw);
/* insert Fortran-to-C conversion for filename */
  FIXCHAR(filename,cl0,_cltmp0);
*ierr = PetscDrawSetSave(
	(PetscDraw)PetscToPointer((draw) ),_cltmp0);
  FREECHAR(filename,_cltmp0);
}
PETSC_EXTERN void  petscdrawsetsavemovie_(PetscDraw draw, char movieext[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(draw);
/* insert Fortran-to-C conversion for movieext */
  FIXCHAR(movieext,cl0,_cltmp0);
*ierr = PetscDrawSetSaveMovie(
	(PetscDraw)PetscToPointer((draw) ),_cltmp0);
  FREECHAR(movieext,_cltmp0);
}
PETSC_EXTERN void  petscdrawsetsavefinalimage_(PetscDraw draw, char filename[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(draw);
/* insert Fortran-to-C conversion for filename */
  FIXCHAR(filename,cl0,_cltmp0);
*ierr = PetscDrawSetSaveFinalImage(
	(PetscDraw)PetscToPointer((draw) ),_cltmp0);
  FREECHAR(filename,_cltmp0);
}
PETSC_EXTERN void  petscdrawsave_(PetscDraw draw, int *ierr)
{
CHKFORTRANNULLOBJECT(draw);
*ierr = PetscDrawSave(
	(PetscDraw)PetscToPointer((draw) ));
}
PETSC_EXTERN void  petscdrawsavemovie_(PetscDraw draw, int *ierr)
{
CHKFORTRANNULLOBJECT(draw);
*ierr = PetscDrawSaveMovie(
	(PetscDraw)PetscToPointer((draw) ));
}
#if defined(__cplusplus)
}
#endif
