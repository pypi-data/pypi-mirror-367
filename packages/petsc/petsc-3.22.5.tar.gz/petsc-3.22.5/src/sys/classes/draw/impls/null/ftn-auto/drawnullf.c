#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* drawnull.c */
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
#define petscdrawopennull_ PETSCDRAWOPENNULL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawopennull_ petscdrawopennull
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdrawisnull_ PETSCDRAWISNULL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdrawisnull_ petscdrawisnull
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscdrawopennull_(MPI_Fint * comm,PetscDraw *win, int *ierr)
{
PetscBool win_null = !*(void**) win ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(win);
*ierr = PetscDrawOpenNull(
	MPI_Comm_f2c(*(comm)),win);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! win_null && !*(void**) win) * (void **) win = (void *)-2;
}
PETSC_EXTERN void  petscdrawisnull_(PetscDraw draw,PetscBool *yes, int *ierr)
{
CHKFORTRANNULLOBJECT(draw);
*ierr = PetscDrawIsNull(
	(PetscDraw)PetscToPointer((draw) ),yes);
}
#if defined(__cplusplus)
}
#endif
