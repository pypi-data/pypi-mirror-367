#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* amsopen.c */
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

#include "petscsys.h"
#include "petscviewersaws.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewersawsopen_ PETSCVIEWERSAWSOPEN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewersawsopen_ petscviewersawsopen
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectviewsaws_ PETSCOBJECTVIEWSAWS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectviewsaws_ petscobjectviewsaws
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscviewersawsopen_(MPI_Fint * comm,PetscViewer *lab, int *ierr)
{
PetscBool lab_null = !*(void**) lab ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(lab);
*ierr = PetscViewerSAWsOpen(
	MPI_Comm_f2c(*(comm)),lab);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! lab_null && !*(void**) lab) * (void **) lab = (void *)-2;
}
PETSC_EXTERN void  petscobjectviewsaws_(PetscObject obj,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(obj);
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscObjectViewSAWs(
	(PetscObject)PetscToPointer((obj) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
#if defined(__cplusplus)
}
#endif
