#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* vi.c */
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
#define snesvigetactivesetis_ SNESVIGETACTIVESETIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesvigetactivesetis_ snesvigetactivesetis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesvisetvariablebounds_ SNESVISETVARIABLEBOUNDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesvisetvariablebounds_ snesvisetvariablebounds
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snesvigetvariablebounds_ SNESVIGETVARIABLEBOUNDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snesvigetvariablebounds_ snesvigetvariablebounds
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  snesvigetactivesetis_(SNES snes,Vec X,Vec F,IS *ISact, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLOBJECT(X);
CHKFORTRANNULLOBJECT(F);
PetscBool ISact_null = !*(void**) ISact ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ISact);
*ierr = SNESVIGetActiveSetIS(
	(SNES)PetscToPointer((snes) ),
	(Vec)PetscToPointer((X) ),
	(Vec)PetscToPointer((F) ),ISact);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ISact_null && !*(void**) ISact) * (void **) ISact = (void *)-2;
}
PETSC_EXTERN void  snesvisetvariablebounds_(SNES snes,Vec xl,Vec xu, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLOBJECT(xl);
CHKFORTRANNULLOBJECT(xu);
*ierr = SNESVISetVariableBounds(
	(SNES)PetscToPointer((snes) ),
	(Vec)PetscToPointer((xl) ),
	(Vec)PetscToPointer((xu) ));
}
PETSC_EXTERN void  snesvigetvariablebounds_(SNES snes,Vec *xl,Vec *xu, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
PetscBool xl_null = !*(void**) xl ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(xl);
PetscBool xu_null = !*(void**) xu ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(xu);
*ierr = SNESVIGetVariableBounds(
	(SNES)PetscToPointer((snes) ),xl,xu);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! xl_null && !*(void**) xl) * (void **) xl = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! xu_null && !*(void**) xu) * (void **) xu = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
