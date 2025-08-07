#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* vsection.c */
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

#include "petscsection.h"
#include "petscvec.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsectionvecview_ PETSCSECTIONVECVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsectionvecview_ petscsectionvecview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsectionvecnorm_ PETSCSECTIONVECNORM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsectionvecnorm_ petscsectionvecnorm
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscsectionvecview_(PetscSection s,Vec v,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(s);
CHKFORTRANNULLOBJECT(v);
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscSectionVecView(
	(PetscSection)PetscToPointer((s) ),
	(Vec)PetscToPointer((v) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petscsectionvecnorm_(PetscSection s,PetscSection gs,Vec x,NormType *type,PetscReal val[], int *ierr)
{
CHKFORTRANNULLOBJECT(s);
CHKFORTRANNULLOBJECT(gs);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLREAL(val);
*ierr = PetscSectionVecNorm(
	(PetscSection)PetscToPointer((s) ),
	(PetscSection)PetscToPointer((gs) ),
	(Vec)PetscToPointer((x) ),*type,val);
}
#if defined(__cplusplus)
}
#endif
