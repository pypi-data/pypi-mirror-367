#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* state.c */
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
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectstateget_ PETSCOBJECTSTATEGET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectstateget_ petscobjectstateget
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectstateset_ PETSCOBJECTSTATESET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectstateset_ petscobjectstateset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectgetid_ PETSCOBJECTGETID
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectgetid_ petscobjectgetid
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectcompareid_ PETSCOBJECTCOMPAREID
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectcompareid_ petscobjectcompareid
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscobjectstateget_(PetscObject obj,PetscObjectState *state, int *ierr)
{
CHKFORTRANNULLOBJECT(obj);
*ierr = PetscObjectStateGet(
	(PetscObject)PetscToPointer((obj) ),
	(PetscObjectState* )PetscToPointer((state) ));
}
PETSC_EXTERN void  petscobjectstateset_(PetscObject obj,PetscObjectState *state, int *ierr)
{
CHKFORTRANNULLOBJECT(obj);
*ierr = PetscObjectStateSet(
	(PetscObject)PetscToPointer((obj) ),*state);
}
PETSC_EXTERN void  petscobjectgetid_(PetscObject obj,PetscObjectId *id, int *ierr)
{
CHKFORTRANNULLOBJECT(obj);
*ierr = PetscObjectGetId(
	(PetscObject)PetscToPointer((obj) ),
	(PetscObjectId* )PetscToPointer((id) ));
}
PETSC_EXTERN void  petscobjectcompareid_(PetscObject obj,PetscObjectId *id,PetscBool *eq, int *ierr)
{
CHKFORTRANNULLOBJECT(obj);
*ierr = PetscObjectCompareId(
	(PetscObject)PetscToPointer((obj) ),*id,eq);
}
#if defined(__cplusplus)
}
#endif
