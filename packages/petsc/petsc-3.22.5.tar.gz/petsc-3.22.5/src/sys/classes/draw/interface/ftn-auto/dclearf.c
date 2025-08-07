#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* dclear.c */
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
#define petscdrawclear_ PETSCDRAWCLEAR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawclear_ petscdrawclear
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawbop_ PETSCDRAWBOP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawbop_ petscdrawbop
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdraweop_ PETSCDRAWEOP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdraweop_ petscdraweop
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscdrawclear_(PetscDraw draw, int *ierr)
{
CHKFORTRANNULLOBJECT(draw);
*ierr = PetscDrawClear(
	(PetscDraw)PetscToPointer((draw) ));
}
PETSC_EXTERN void  petscdrawbop_(PetscDraw draw, int *ierr)
{
CHKFORTRANNULLOBJECT(draw);
*ierr = PetscDrawBOP(
	(PetscDraw)PetscToPointer((draw) ));
}
PETSC_EXTERN void  petscdraweop_(PetscDraw draw, int *ierr)
{
CHKFORTRANNULLOBJECT(draw);
*ierr = PetscDrawEOP(
	(PetscDraw)PetscToPointer((draw) ));
}
#if defined(__cplusplus)
}
#endif
