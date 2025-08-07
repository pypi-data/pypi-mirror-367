#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* fas.c */
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

#include "petscsnes.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfascreatecoarsevec_ SNESFASCREATECOARSEVEC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfascreatecoarsevec_ snesfascreatecoarsevec
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesfasrestrict_ SNESFASRESTRICT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesfasrestrict_ snesfasrestrict
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  snesfascreatecoarsevec_(SNES snes,Vec *Xcoarse, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
PetscBool Xcoarse_null = !*(void**) Xcoarse ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(Xcoarse);
*ierr = SNESFASCreateCoarseVec(
	(SNES)PetscToPointer((snes) ),Xcoarse);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! Xcoarse_null && !*(void**) Xcoarse) * (void **) Xcoarse = (void *)-2;
}
PETSC_EXTERN void  snesfasrestrict_(SNES fine,Vec Xfine,Vec Xcoarse, int *ierr)
{
CHKFORTRANNULLOBJECT(fine);
CHKFORTRANNULLOBJECT(Xfine);
CHKFORTRANNULLOBJECT(Xcoarse);
*ierr = SNESFASRestrict(
	(SNES)PetscToPointer((fine) ),
	(Vec)PetscToPointer((Xfine) ),
	(Vec)PetscToPointer((Xcoarse) ));
}
#if defined(__cplusplus)
}
#endif
