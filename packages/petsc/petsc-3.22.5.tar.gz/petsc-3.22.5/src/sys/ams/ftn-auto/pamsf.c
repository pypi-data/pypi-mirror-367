#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* pams.c */
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
#define petscobjectsawstakeaccess_ PETSCOBJECTSAWSTAKEACCESS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectsawstakeaccess_ petscobjectsawstakeaccess
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectsawsgrantaccess_ PETSCOBJECTSAWSGRANTACCESS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectsawsgrantaccess_ petscobjectsawsgrantaccess
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsawsblock_ PETSCSAWSBLOCK
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsawsblock_ petscsawsblock
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectsawsblock_ PETSCOBJECTSAWSBLOCK
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectsawsblock_ petscobjectsawsblock
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectsawssetblock_ PETSCOBJECTSAWSSETBLOCK
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectsawssetblock_ petscobjectsawssetblock
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscobjectsawstakeaccess_(PetscObject obj, int *ierr)
{
CHKFORTRANNULLOBJECT(obj);
*ierr = PetscObjectSAWsTakeAccess(
	(PetscObject)PetscToPointer((obj) ));
}
PETSC_EXTERN void  petscobjectsawsgrantaccess_(PetscObject obj, int *ierr)
{
CHKFORTRANNULLOBJECT(obj);
*ierr = PetscObjectSAWsGrantAccess(
	(PetscObject)PetscToPointer((obj) ));
}
PETSC_EXTERN void  petscsawsblock_(int *ierr)
{
*ierr = PetscSAWsBlock();
}
PETSC_EXTERN void  petscobjectsawsblock_(PetscObject obj, int *ierr)
{
CHKFORTRANNULLOBJECT(obj);
*ierr = PetscObjectSAWsBlock(
	(PetscObject)PetscToPointer((obj) ));
}
PETSC_EXTERN void  petscobjectsawssetblock_(PetscObject obj,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(obj);
*ierr = PetscObjectSAWsSetBlock(
	(PetscObject)PetscToPointer((obj) ),*flg);
}
#if defined(__cplusplus)
}
#endif
